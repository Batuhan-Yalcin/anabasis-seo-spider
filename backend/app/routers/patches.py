from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import logging
from datetime import datetime

from app.database import get_db
from app.models import Issue, IssueStatus, PatchHistory
from app.schemas import IssueApproval
from app.services.patch_engine import patch_engine
from app.services.patch_sandbox import patch_sandbox
from app.services.validator import validator
from app.services.circuit_breaker import circuit_breaker

router = APIRouter(prefix="/patches", tags=["patches"])
logger = logging.getLogger(__name__)


@router.get("/history", response_model=List[dict])
async def get_patch_history(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all patch history
    """
    result = await db.execute(
        select(PatchHistory).order_by(PatchHistory.created_at.desc())
    )
    history = result.scalars().all()
    
    return [
        {
            "id": h.id,
            "job_id": h.job_id,
            "issue_id": h.issue_id,
            "file_path": h.file_path,
            "line_number": h.line_number,
            "action": h.action,
            "original_content": h.original_content,
            "patched_content": h.patched_content,
            "success": h.success,
            "error_message": h.error_message,
            "applied_at": h.applied_at.isoformat(),
            "rolled_back": h.rolled_back,
        }
        for h in history
    ]


@router.post("/{job_id}/issues/{issue_id}/approve")
async def approve_single_issue(
    job_id: str,
    issue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a single issue
    """
    try:
        # Update issue status
        await db.execute(
            update(Issue)
            .where(Issue.id == issue_id)
            .values(status=IssueStatus.APPROVED)
        )
        await db.commit()
        
        logger.info(f"Approved issue {issue_id} for job {job_id}")
        return {"status": "approved", "issue_id": issue_id}
    
    except Exception as e:
        logger.error(f"Failed to approve issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/issues/{issue_id}/reject")
async def reject_single_issue(
    job_id: str,
    issue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a single issue
    """
    try:
        # Update issue status
        await db.execute(
            update(Issue)
            .where(Issue.id == issue_id)
            .values(status=IssueStatus.REJECTED)
        )
        await db.commit()
        
        logger.info(f"Rejected issue {issue_id} for job {job_id}")
        return {"status": "rejected", "issue_id": issue_id}
    
    except Exception as e:
        logger.error(f"Failed to reject issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def approve_issues(
    approval: IssueApproval,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve and apply patches for selected issues
    
    Safeguards:
    - Patches applied in sandbox (temp copy)
    - DB operations wrapped in transaction
    - Circuit breaker stops after 5 failures
    """
    try:
        results = []
        job_id = None
        
        for issue_id in approval.issue_ids:
            # Get issue
            result = await db.execute(select(Issue).where(Issue.id == issue_id))
            issue = result.scalar_one_or_none()
            
            if not issue:
                results.append({
                    "issue_id": issue_id,
                    "status": "not_found"
                })
                continue
            
            # Track job_id for circuit breaker
            if job_id is None:
                job_id = issue.job_id
            
            # CIRCUIT BREAKER: Check if tripped
            if circuit_breaker.is_tripped(issue.job_id):
                results.append({
                    "issue_id": issue_id,
                    "status": "circuit_breaker_tripped",
                    "message": f"Circuit breaker tripped for job {issue.job_id}. Too many failures."
                })
                continue
            
            # CIRCUIT BREAKER: Check if too many failures
            if circuit_breaker.is_tripped(issue.job_id):
                logger.error(
                    f"Circuit breaker tripped for job {issue.job_id}. "
                    f"Stopping further patches."
                )
                results.append({
                    "issue_id": issue_id,
                    "status": "circuit_breaker_tripped",
                    "message": "Too many failures, auto-stopped"
                })
                continue
            
            # Use edited code if provided
            code_to_apply = approval.edited_code if approval.edited_code else issue.code
            
            # SANDBOX: Apply patch to temp copy first
            def apply_patch_wrapper(temp_path, *args, **kwargs):
                return patch_engine.apply_patch(
                    file_path=temp_path,
                    line_number=issue.line_number,
                    action=issue.action,
                    code=code_to_apply,
                    file_type=None
                )
            
            def validate_wrapper(temp_path):
                file_type = temp_path.split('.')[-1]
                return patch_engine.validate_patch(temp_path, f'.{file_type}')
            
            success, temp_path, error = patch_sandbox.apply_and_validate(
                original_path=issue.file_path,
                patch_func=apply_patch_wrapper,
                validate_func=validate_wrapper
            )
            
            if success:
                # DB TRANSACTION: Wrap all updates atomically
                try:
                    # Create backup
                    backup_path = patch_engine.create_backup(issue.file_path)
                    
                    # Read contents for history
                    with open(issue.file_path, 'r') as f:
                        patched_content = f.read()
                    
                    with open(backup_path, 'r') as f:
                        original_content = f.read()
                    
                    # Atomic transaction: issue + history + status
                    async with db.begin():
                        # Update issue
                        await db.execute(
                            update(Issue)
                            .where(Issue.id == issue_id)
                            .values(
                                status=IssueStatus.APPLIED,
                                backup_path=backup_path,
                                applied_at=datetime.utcnow()
                            )
                        )
                        
                        # Create patch history
                        history = PatchHistory(
                            issue_id=issue_id,
                            job_id=issue.job_id,
                            file_path=issue.file_path,
                            backup_path=backup_path,
                            original_content=original_content,
                            patched_content=patched_content,
                            success=True,
                            rollback_available=True
                        )
                        db.add(history)
                    
                    # Circuit breaker: record success
                    circuit_breaker.record_success(issue.job_id)
                    
                    # Cleanup temp file
                    patch_sandbox.cleanup_temp(temp_path)
                    
                    results.append({
                        "issue_id": issue_id,
                        "status": "applied",
                        "backup_path": backup_path
                    })
                
                except Exception as e:
                    logger.error(f"Transaction failed for issue {issue_id}: {e}")
                    
                    # Circuit breaker: record failure
                    circuit_breaker.record_failure(issue.job_id)
                    
                    results.append({
                        "issue_id": issue_id,
                        "status": "transaction_failed",
                        "error": str(e)
                    })
            
            else:
                # Patch failed in sandbox
                logger.error(f"Patch failed for issue {issue_id}: {error}")
                
                # Circuit breaker: record failure
                should_stop = circuit_breaker.record_failure(issue.job_id)
                
                # DB transaction: update issue status
                async with db.begin():
                    await db.execute(
                        update(Issue)
                        .where(Issue.id == issue_id)
                        .values(status=IssueStatus.FAILED)
                    )
                
                # Cleanup temp file
                patch_sandbox.cleanup_temp(temp_path)
                
                results.append({
                    "issue_id": issue_id,
                    "status": "failed",
                    "error": error,
                    "circuit_breaker_status": circuit_breaker.get_status(issue.job_id)
                })
                
                if should_stop:
                    logger.error(f"Stopping further patches for job {issue.job_id}")
                    break
        
        await db.commit()
        
        logger.info(f"Processed {len(approval.issue_ids)} patch approvals")
        
        return {
            "total": len(approval.issue_ids),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Failed to approve patches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject")
async def reject_issues(
    issue_ids: List[int],
    db: AsyncSession = Depends(get_db)
):
    """
    Reject selected issues
    """
    try:
        for issue_id in issue_ids:
            await db.execute(
                update(Issue)
                .where(Issue.id == issue_id)
                .values(status=IssueStatus.REJECTED)
            )
        
        await db.commit()
        
        logger.info(f"Rejected {len(issue_ids)} issues")
        
        return {
            "rejected": len(issue_ids)
        }
    
    except Exception as e:
        logger.error(f"Failed to reject issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback/{issue_id}")
async def rollback_patch(
    issue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Rollback a previously applied patch
    """
    try:
        # Get patch history
        result = await db.execute(
            select(PatchHistory)
            .where(PatchHistory.issue_id == issue_id)
            .order_by(PatchHistory.created_at.desc())
        )
        history = result.scalar_one_or_none()
        
        if not history:
            raise HTTPException(status_code=404, detail="Patch history not found")
        
        if not history.rollback_available:
            raise HTTPException(status_code=400, detail="Rollback not available")
        
        # Perform rollback
        success = patch_engine.rollback(history.file_path, history.backup_path)
        
        if success:
            # Update issue status
            await db.execute(
                update(Issue)
                .where(Issue.id == issue_id)
                .values(status=IssueStatus.PENDING)
            )
            
            # Mark history as rolled back
            await db.execute(
                update(PatchHistory)
                .where(PatchHistory.id == history.id)
                .values(rollback_available=False)
            )
            
            await db.commit()
            
            logger.info(f"Rolled back patch for issue {issue_id}")
            
            return {
                "issue_id": issue_id,
                "status": "rolled_back"
            }
        else:
            raise HTTPException(status_code=500, detail="Rollback failed")
    
    except Exception as e:
        logger.error(f"Failed to rollback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

