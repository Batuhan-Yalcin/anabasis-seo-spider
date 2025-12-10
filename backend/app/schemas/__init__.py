from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    CHUNKING = "chunking"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"
    SUPERSEDED = "superseded"
    CONFLICT = "conflict"


class IssueType(str, Enum):
    SCHEMA_MISSING = "schema_missing"
    META_ISSUE = "meta_issue"
    TITLE_LENGTH = "title_length"
    H_TAG_ISSUE = "h_tag_issue"
    LINK_NATURALNESS = "link_naturalness"
    IMAGE_ALT_MISSING = "image_alt_missing"
    PERFORMANCE_HINT = "performance_hint"
    JS_ERROR = "js_error"
    CSS_SUGGESTION = "css_suggestion"


class ActionType(str, Enum):
    INSERT_AFTER_LINE = "insert_after_line"
    REPLACE_LINE = "replace_line"
    ANNOTATE = "annotate"


# Gemini Analysis Schemas
class GeminiIssue(BaseModel):
    type: str
    line: int
    action: ActionType
    code: str
    reason: str
    severity: IssueSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    review_required: bool = False
    suggested_rewrite: Optional[str] = None
    
    @field_validator('review_required', mode='before')
    @classmethod
    def auto_mark_low_confidence(cls, v, info):
        """Automatically mark as review_required if confidence < 0.70"""
        confidence = info.data.get('confidence', 1.0)
        if confidence < 0.70:
            return True
        return v


class GeminiResponse(BaseModel):
    file: str
    chunk_start: int
    chunk_end: int
    issues: List[GeminiIssue]


# API Request/Response Schemas
class JobCreate(BaseModel):
    keywords: List[str]
    site_language: str = "tr"
    site_url: str


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    upload_filename: str
    total_files: int
    total_chunks: int
    analyzed_chunks: int
    total_issues: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileResponse(BaseModel):
    id: int
    file_path: str
    file_type: str
    line_count: int
    size_bytes: int
    analyzed: bool
    
    class Config:
        from_attributes = True


class IssueResponse(BaseModel):
    id: int
    file_path: str
    line_number: int
    issue_type: str
    action: str
    code: str
    reason: str
    severity: IssueSeverity
    confidence: float
    review_required: bool
    suggested_rewrite: Optional[str]
    status: IssueStatus
    conflict_with: Optional[List[int]] = None
    
    class Config:
        from_attributes = True


class IssueApproval(BaseModel):
    issue_ids: List[int]
    action: str  # approve, reject, edit
    edited_code: Optional[str] = None


class ChunkData(BaseModel):
    file: str
    chunk_start: int
    chunk_end: int
    content: str
    context_head: Optional[str] = None
    context_tail: Optional[str] = None


class GlobalRules(BaseModel):
    title_min: int = 45
    title_max: int = 60
    meta_min: int = 120
    meta_max: int = 155
    force_schema_types: List[str] = [
        "Product",
        "FAQPage",
        "BreadcrumbList",
        "LocalBusiness",
        "Article",
        "Review",
        "VideoObject",
        "Speakable"
    ]


class GeminiPromptData(BaseModel):
    file: str
    chunk_start: int
    chunk_end: int
    content: str
    context_head: Optional[str] = None
    context_tail: Optional[str] = None
    keywords: List[str]
    site_language: str
    site_url: str
    global_rules: GlobalRules

