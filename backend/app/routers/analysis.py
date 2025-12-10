from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging

from app.database import get_db
from app.models import Job, Chunk, Issue, JobStatus, IssueStatus
from app.services.gemini_client import gemini_client
from app.services.deduplicator import deduplicator
from app.services.rate_limiter import rate_limiter
from app.schemas import GeminiPromptData, GlobalRules
from app.config import get_settings

router = APIRouter(prefix="/analysis", tags=["analysis"])
logger = logging.getLogger(__name__)
settings = get_settings()


async def analyze_chunk_task(
    chunk_id: int,
    job_id: str,
    keywords: list,
    site_language: str,
    site_url: str,
    db: AsyncSession
):
    """
    Background task to analyze a single chunk
    """
    try:
        # Get chunk
        result = await db.execute(select(Chunk).where(Chunk.id == chunk_id))
        chunk = result.scalar_one_or_none()
        
        if not chunk:
            logger.error(f"Chunk {chunk_id} not found")
            return
        
        # Build prompt data
        prompt_data = GeminiPromptData(
            file=chunk.file_path,
            chunk_start=chunk.start_line,
            chunk_end=chunk.end_line,
            content=chunk.content,
            context_head=chunk.context_head,
            context_tail=chunk.context_tail,
            keywords=keywords,
            site_language=site_language,
            site_url=site_url,
            global_rules=GlobalRules()
        )
        
        # Analyze with Gemini (with rate limiting)
        logger.info(f"Analyzing chunk {chunk_id} for job {job_id}")
        
        # Use rate limiter to control concurrent requests
        async with rate_limiter:
            response = await gemini_client.analyze_chunk(prompt_data)
        
        # Save issues to database (will deduplicate later)
        for issue_data in response.issues:
            issue = Issue(
                job_id=job_id,
                chunk_id=chunk_id,
                file_path=response.file,
                line_number=issue_data.line,
                issue_type=issue_data.type,
                action=issue_data.action.value,
                code=issue_data.code,
                reason=issue_data.reason,
                severity=issue_data.severity,
                confidence=issue_data.confidence,
                review_required=issue_data.review_required,
                suggested_rewrite=issue_data.suggested_rewrite,
                status=IssueStatus.PENDING
            )
            db.add(issue)
        
        # Mark chunk as analyzed
        await db.execute(
            update(Chunk)
            .where(Chunk.id == chunk_id)
            .values(analyzed=True)
        )
        
        await db.commit()
        
        # Update job progress
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if job:
            # Atomic increment of analyzed_chunks
            result = await db.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(analyzed_chunks=Job.analyzed_chunks + 1)
                .returning(Job.analyzed_chunks, Job.total_chunks)
            )
            await db.commit()
            
            row = result.first()
            if row:
                analyzed, total = row
                logger.info(f"Job {job_id} progress: {analyzed}/{total} chunks analyzed")
                
                # Check if all chunks are completed
                if analyzed >= total:
                    await db.execute(
                        update(Job)
                        .where(Job.id == job_id)
                        .values(status=JobStatus.COMPLETED)
                    )
                    await db.commit()
                    logger.info(f"Job {job_id} completed! All {analyzed} chunks analyzed.")
        
        logger.info(f"Completed analysis of chunk {chunk_id}: {len(response.issues)} issues found")
    
    except Exception as e:
        logger.error(f"Failed to analyze chunk {chunk_id}: {e}")


@router.post("/{job_id}/analyze")
async def start_analysis(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start FULL AUTOMATIC analysis of ALL chunks for a job
    
    No user confirmation needed between batches
    """
    try:
        # Get job
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get metadata
        keywords = job.job_metadata.get('keywords', []) if job.job_metadata else []
        site_language = job.job_metadata.get('site_language', 'tr') if job.job_metadata else 'tr'
        site_url = job.job_metadata.get('site_url', '') if job.job_metadata else ''
        
        # Get all chunks
        result = await db.execute(
            select(Chunk).where(
                Chunk.job_id == job_id,
                Chunk.analyzed == False
            )
        )
        chunks = result.scalars().all()
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks to analyze")
        
        # Queue ALL chunks for automatic analysis
        # Process in batches of 5 for rate limiting
        for i, chunk in enumerate(chunks):
            background_tasks.add_task(
                analyze_chunk_task,
                chunk.id,
                job_id,
                keywords,
                site_language,
                site_url,
                db
            )
        
        logger.info(f"Started FULL AUTOMATIC analysis for job {job_id}: {len(chunks)} chunks")
        
        return {
            "job_id": job_id,
            "total_chunks": len(chunks),
            "status": "full_automatic_analysis_started",
            "message": "All chunks will be analyzed automatically"
        }
    
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/analyze-batch")
async def analyze_batch(
    job_id: str,
    batch_size: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze next batch of chunks (for progressive analysis)
    """
    try:
        # Get job metadata
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        keywords = job.metadata.get('keywords', [])
        site_language = job.metadata.get('site_language', 'tr')
        site_url = job.metadata.get('site_url', '')
        
        # Get unanalyzed chunks
        result = await db.execute(
            select(Chunk)
            .where(Chunk.job_id == job_id, Chunk.analyzed == False)
            .limit(batch_size)
        )
        chunks = result.scalars().all()
        
        if not chunks:
            return {
                "job_id": job_id,
                "status": "completed",
                "message": "All chunks analyzed"
            }
        
        # Analyze chunks
        total_issues = 0
        for chunk in chunks:
            await analyze_chunk_task(
                chunk.id,
                job_id,
                keywords,
                site_language,
                site_url,
                db
            )
            total_issues += 1
        
        return {
            "job_id": job_id,
            "analyzed": len(chunks),
            "status": "batch_completed"
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

