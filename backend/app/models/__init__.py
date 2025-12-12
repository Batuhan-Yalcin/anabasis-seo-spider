from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum, Text, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    CHUNKING = "chunking"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"
    SUPERSEDED = "superseded"  # Deduplication: lower severity issue on same line
    CONFLICT = "conflict"  # Multiple patches target same line


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    upload_filename = Column(String, nullable=False)
    workspace_path = Column(String, nullable=False)
    total_files = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    analyzed_chunks = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    job_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # php, html, js, jsx, tsx, etc.
    line_count = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    analyzed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, index=True)
    file_id = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    context_head = Column(Text)  # Previous 10 lines
    context_tail = Column(Text)  # Next 10 lines
    analyzed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, index=True)
    chunk_id = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    issue_type = Column(String, nullable=False)  # schema_missing, meta_issue, etc.
    action = Column(String, nullable=False)  # insert_after_line, replace_line, annotate
    code = Column(Text, nullable=False)  # The actual code to insert/replace
    reason = Column(Text, nullable=False)
    severity = Column(SQLEnum(IssueSeverity), nullable=False)
    confidence = Column(Float, nullable=False)
    review_required = Column(Boolean, default=False)
    suggested_rewrite = Column(Text)
    status = Column(SQLEnum(IssueStatus), default=IssueStatus.PENDING)
    conflict_with = Column(JSON)  # List of conflicting issue IDs
    backup_path = Column(String)  # Path to backup file before patching
    applied_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PatchHistory(Base):
    __tablename__ = "patch_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, nullable=False)
    job_id = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    backup_path = Column(String, nullable=False)
    original_content = Column(Text, nullable=False)
    patched_content = Column(Text, nullable=False)
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    rollback_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Import SEO models
from app.models.seo_models import (
    SEOAnalysis,
    SEOIssue,
    SEOMetric,
    SEOAnalysisStatus,
    SEOIssueType,
    SEOIssueSeverity
)

