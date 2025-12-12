from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SEOAnalysisStatus(str, Enum):
    PENDING = "pending"
    CRAWLING = "crawling"
    ANALYZING = "analyzing"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class SEOIssueType(str, Enum):
    SCHEMA_MISSING = "schema_missing"
    TITLE_ISSUE = "title_issue"
    META_ISSUE = "meta_issue"
    HEADING_ISSUE = "heading_issue"
    BROKEN_LINK = "broken_link"
    NOFOLLOW_ISSUE = "nofollow_issue"
    ANCHOR_SPAM = "anchor_spam"
    SEMANTIC_DENSITY_LOW = "semantic_density_low"
    WORDCOUNT_LOW = "wordcount_low"
    IMAGE_ALT_MISSING = "image_alt_missing"
    ROBOTS_ISSUE = "robots_issue"
    SITEMAP_ISSUE = "sitemap_issue"
    SNIPPET_ISSUE = "snippet_issue"
    TECHNICAL_ERROR = "technical_error"


class SEOIssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Request Schemas
class SEOAnalysisRequest(BaseModel):
    """SEO analizi başlatma isteği"""
    url: str = Field(..., description="Analiz edilecek URL")
    keywords: List[str] = Field(..., min_length=1, description="Anahtar kelimeler")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL http:// veya https:// ile başlamalıdır')
        return v
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if not v:
            raise ValueError('En az bir anahtar kelime gereklidir')
        # Trim and filter empty keywords
        keywords = [k.strip() for k in v if k.strip()]
        if not keywords:
            raise ValueError('Geçerli anahtar kelime bulunamadı')
        return keywords


# Response Schemas
class KeywordScore(BaseModel):
    """Anahtar kelime skoru"""
    presence_score: float = Field(..., ge=0, le=100, description="Varlık skoru (0-100)")
    prominence: float = Field(..., ge=0, le=100, description="Öne çıkma skoru (0-100)")
    recommendation: str = Field(..., description="Öneri")


class SEOIssueResponse(BaseModel):
    """SEO sorunu detayı"""
    id: int
    issue_type: SEOIssueType
    severity: SEOIssueSeverity
    confidence: float
    line: Optional[int] = None
    element: Optional[str] = None
    reason: str
    recommendation: str
    example_fix: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class SEOMetricResponse(BaseModel):
    """SEO metrikleri"""
    schemas_found: List[str]
    schemas_missing: List[str]
    title_length: Optional[int]
    title_keyword_match: bool
    meta_length: Optional[int]
    meta_keyword_match: bool
    h1_count: int
    h2_count: int
    h3_count: int
    heading_structure_valid: bool
    internal_links_count: int
    external_links_count: int
    broken_links_count: int
    nofollow_links_count: int
    total_images: int
    images_without_alt: int
    has_robots_txt: bool
    has_sitemap: bool
    word_count: int
    keyword_density: Dict[str, float]
    
    class Config:
        from_attributes = True


class SEOAnalysisResponse(BaseModel):
    """SEO analizi özet yanıtı"""
    id: str
    url: str
    keywords: List[str]
    status: SEOAnalysisStatus
    
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    word_count: int
    
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    
    keyword_scores: Dict[str, KeywordScore]
    
    overall_score: float
    technical_score: float
    content_score: float
    
    html_report_path: Optional[str] = None
    pdf_report_path: Optional[str] = None
    
    error_message: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SEOAnalysisDetailResponse(SEOAnalysisResponse):
    """Detaylı SEO analizi yanıtı (issues ve metrics dahil)"""
    issues: List[SEOIssueResponse] = []
    metrics: Optional[SEOMetricResponse] = None
    detected_data: Optional[Dict[str, Any]] = None  # Tespit edilen SEO elementleri


# Gemini Analysis Schemas
class GeminiSEOIssue(BaseModel):
    """Gemini'den dönen SEO sorunu"""
    type: SEOIssueType
    line: Optional[int] = None
    reason: str
    recommendation: str
    example_fix: str = ""
    severity: SEOIssueSeverity
    confidence: float = Field(ge=0.0, le=1.0)


class GeminiKeywordScore(BaseModel):
    """Gemini'den dönen anahtar kelime skoru"""
    presence_score: float = Field(ge=0, le=100)
    prominence: float = Field(ge=0, le=100)
    recommendation: str


class GeminiSEOResponse(BaseModel):
    """Gemini SEO analiz yanıtı"""
    issues: List[GeminiSEOIssue]
    keyword_scores: Dict[str, GeminiKeywordScore]


# Internal Service Schemas
class CrawlResult(BaseModel):
    """Playwright crawl sonucu"""
    url: str
    html_content: str
    screenshot_path: Optional[str] = None
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    status_code: int = 200
    load_time: float = 0.0
    error: Optional[str] = None
    visible_h1_count: Optional[int] = None  # Playwright ile sayılan görünür H1 sayısı


class HTMLChunk(BaseModel):
    """HTML chunk for analysis"""
    chunk_id: int
    content: str
    start_pos: int
    end_pos: int
    context: Optional[str] = None


class AnalysisProgress(BaseModel):
    """Analiz ilerleme durumu"""
    analysis_id: str
    status: SEOAnalysisStatus
    progress_percentage: float = Field(ge=0, le=100)
    current_step: str
    message: str

