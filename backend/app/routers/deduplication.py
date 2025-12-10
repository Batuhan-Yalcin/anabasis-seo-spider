from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging

from app.database import get_db
from app.models import Issue, IssueStatus
from app.services.deduplicator import deduplicator

router = APIRouter(prefix="/deduplication", tags=["deduplication"])
logger = logging.getLogger(__name__)


@router.post("/{job_id}/deduplicate")
async def deduplicate_job_issues(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Deduplicate issues for a job
    
    Rules:
    - Same line, multiple issues → Keep highest severity
    - Same line, conflicting patches → Mark as conflict
    """
    try:
        # Get all pending issues for job
        result = await db.execute(
            select(Issue).where(
                Issue.job_id == job_id,
                Issue.status == IssueStatus.PENDING
            )
        )
        issues = result.scalars().all()
        
        if not issues:
            return {
                "job_id": job_id,
                "message": "No issues to deduplicate"
            }
        
        # Convert to dict for deduplicator
        issues_dict = [
            {
                'id': issue.id,
                'file_path': issue.file_path,
                'line_number': issue.line_number,
                'action': issue.action,
                'code': issue.code,
                'severity': issue.severity,
                'status': issue.status
            }
            for issue in issues
        ]
        
        # Deduplicate
        deduplicated = deduplicator.deduplicate_issues(issues_dict)
        
        # Update database
        superseded_count = 0
        conflict_count = 0
        
        for issue_data in deduplicated:
            if issue_data['status'] == 'superseded':
                await db.execute(
                    update(Issue)
                    .where(Issue.id == issue_data['id'])
                    .values(status=IssueStatus.SUPERSEDED)
                )
                superseded_count += 1
            
            elif issue_data['status'] == 'conflict':
                await db.execute(
                    update(Issue)
                    .where(Issue.id == issue_data['id'])
                    .values(
                        status=IssueStatus.CONFLICT,
                        conflict_with=issue_data.get('conflict_with', [])
                    )
                )
                conflict_count += 1
        
        await db.commit()
        
        # Get conflict summary
        conflict_summary = deduplicator.get_conflict_summary(deduplicated)
        
        logger.info(
            f"Deduplication complete for job {job_id}: "
            f"{superseded_count} superseded, {conflict_count} conflicts"
        )
        
        return {
            "job_id": job_id,
            "total_issues": len(issues),
            "superseded": superseded_count,
            "conflicts": conflict_count,
            "conflict_summary": conflict_summary
        }
    
    except Exception as e:
        logger.error(f"Failed to deduplicate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/conflicts")
async def get_conflicts(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all conflicts for a job
    """
    try:
        result = await db.execute(
            select(Issue).where(
                Issue.job_id == job_id,
                Issue.status == IssueStatus.CONFLICT
            )
        )
        conflicts = result.scalars().all()
        
        return {
            "job_id": job_id,
            "total_conflicts": len(conflicts),
            "conflicts": [
                {
                    "id": issue.id,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "action": issue.action,
                    "code": issue.code,
                    "severity": issue.severity.value,
                    "confidence": issue.confidence,
                    "conflict_with": issue.conflict_with
                }
                for issue in conflicts
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to get conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

