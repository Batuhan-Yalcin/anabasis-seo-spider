from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import uuid
import logging

from app.database import get_db
from app.models import Job, File as FileModel, Chunk, Issue, JobStatus
from app.schemas import JobCreate, JobResponse, FileResponse, IssueResponse
from app.services.file_handler import FileHandler
from app.services.chunker import chunker
from app.services.gemini_client import gemini_client
from app.services.memory_guard import memory_guard
from app.schemas import GeminiPromptData, GlobalRules
from app.config import get_settings

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)
settings = get_settings()

file_handler = FileHandler(settings.UPLOAD_DIR)


@router.get("", response_model=List[JobResponse])
async def get_all_jobs(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all jobs
    """
    result = await db.execute(select(Job).order_by(Job.created_at.desc()))
    jobs = result.scalars().all()
    
    return jobs


@router.post("/create", response_model=JobResponse)
async def create_job(
    file: UploadFile = File(...),
    keywords: str = Form(...),
    site_language: str = Form("tr"),
    site_url: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new analysis job with file upload
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Save uploaded file
        upload_path = await file_handler.save_upload(
            file_content,
            file.filename,
            job_id
        )
        
        # Create job record
        job = Job(
            id=job_id,
            status=JobStatus.UPLOADING,
            upload_filename=file.filename,
            workspace_path=upload_path,
            metadata={
                'keywords': keywords.split(','),
                'site_language': site_language,
                'site_url': site_url
            }
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        logger.info(f"Created job: {job_id}")
        return job
    
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/extract")
async def extract_and_inventory(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Extract uploaded archive and create file inventory
    """
    try:
        # Get job
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update status
        await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=JobStatus.CHUNKING)
        )
        await db.commit()
        
        # Extract archive
        extract_dir = file_handler.extract_archive(job.workspace_path, job_id)
        
        # MEMORY GUARD: Check extracted size
        is_valid, total_size, error_msg = memory_guard.check_directory_size(extract_dir)
        
        if not is_valid:
            # Update job status to failed
            await db.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(status=JobStatus.FAILED, metadata={'error': error_msg})
            )
            await db.commit()
            
            logger.error(f"Job {job_id} aborted: {error_msg}")
            raise HTTPException(status_code=413, detail=error_msg)
        
        logger.info(
            f"Memory guard passed for job {job_id}: "
            f"{memory_guard.format_size(total_size)}"
        )
        
        # Create inventory
        inventory = file_handler.create_inventory(extract_dir)
        
        # Save files to database
        for file_info in inventory:
            file_record = FileModel(
                job_id=job_id,
                file_path=file_info['absolute_path'],  # Use absolute path for reading
                file_type=file_info['file_type'],
                line_count=file_info['line_count'],
                size_bytes=file_info['size_bytes']
            )
            db.add(file_record)
        
        await db.commit()
        
        # Update job
        await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(total_files=len(inventory))
        )
        await db.commit()
        
        logger.info(f"Extracted and inventoried {len(inventory)} files for job {job_id}")
        
        return {
            "job_id": job_id,
            "total_files": len(inventory),
            "extract_dir": extract_dir
        }
    
    except Exception as e:
        logger.error(f"Failed to extract: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/chunk")
async def chunk_files(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Chunk all files in job
    """
    try:
        # Get all files for job
        result = await db.execute(
            select(FileModel).where(FileModel.job_id == job_id)
        )
        files = result.scalars().all()
        
        if not files:
            raise HTTPException(status_code=404, detail="No files found for job")
        
        total_chunks = 0
        
        # Chunk each file
        for file_record in files:
            # Read file content
            with open(file_record.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Create chunks
            chunks = chunker.chunk_file(file_record.file_path, content)
            
            # Save chunks to database
            for chunk_data in chunks:
                chunk = Chunk(
                    job_id=job_id,
                    file_id=file_record.id,
                    file_path=file_record.file_path,
                    start_line=chunk_data['start_line'],
                    end_line=chunk_data['end_line'],
                    content=chunk_data['content'],
                    context_head=chunk_data['context_head'],
                    context_tail=chunk_data['context_tail']
                )
                db.add(chunk)
                total_chunks += 1
        
        await db.commit()
        
        # Update job
        await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(total_chunks=total_chunks, status=JobStatus.ANALYZING)
        )
        await db.commit()
        
        logger.info(f"Created {total_chunks} chunks for job {job_id}")
        
        return {
            "job_id": job_id,
            "total_chunks": total_chunks
        }
    
    except Exception as e:
        logger.error(f"Failed to chunk files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get job details
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.get("/{job_id}/files", response_model=List[FileResponse])
async def get_job_files(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all files for a job
    """
    result = await db.execute(
        select(FileModel).where(FileModel.job_id == job_id)
    )
    files = result.scalars().all()
    
    return files


@router.get("/{job_id}/issues", response_model=List[IssueResponse])
async def get_job_issues(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all issues for a job
    """
    result = await db.execute(
        select(Issue).where(Issue.job_id == job_id)
    )
    issues = result.scalars().all()
    
    return issues

