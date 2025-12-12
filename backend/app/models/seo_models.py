from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum, Text, Float, Boolean
from sqlalchemy.sql import func
from app.database import Base
import enum


class SEOAnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    CRAWLING = "crawling"
    ANALYZING = "analyzing"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class SEOIssueType(str, enum.Enum):
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


class SEOIssueSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SEOAnalysis(Base):
    """SEO Spider analiz kayıtları"""
    __tablename__ = "seo_analyses"
    
    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    keywords = Column(JSON, nullable=False)  # List of keywords
    status = Column(SQLEnum(SEOAnalysisStatus), default=SEOAnalysisStatus.PENDING, nullable=False)
    
    # Crawl data
    html_content = Column(Text)
    screenshot_path = Column(String)
    page_title = Column(String)
    meta_description = Column(String)
    word_count = Column(Integer, default=0)
    
    # Analysis results
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    
    # Keyword scores
    keyword_scores = Column(JSON, default=dict)  # {keyword: {presence_score, prominence, recommendation}}
    
    # Overall scores
    overall_score = Column(Float, default=0.0)  # 0-100
    technical_score = Column(Float, default=0.0)
    content_score = Column(Float, default=0.0)
    
    # Report paths
    html_report_path = Column(String)
    pdf_report_path = Column(String)
    
    # Metadata
    analysis_metadata = Column(JSON, default=dict)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))


class SEOIssue(Base):
    """SEO analiz sonucunda bulunan sorunlar"""
    __tablename__ = "seo_issues"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String, nullable=False, index=True)
    
    issue_type = Column(SQLEnum(SEOIssueType), nullable=False)
    severity = Column(SQLEnum(SEOIssueSeverity), nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    
    line = Column(Integer)  # HTML line number if applicable
    element = Column(String)  # HTML element selector
    
    reason = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    example_fix = Column(Text)
    
    # Context
    context_data = Column(JSON)  # Additional context data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SEOMetric(Base):
    """SEO metrikleri ve detaylı analiz verileri"""
    __tablename__ = "seo_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String, nullable=False, index=True)
    
    # Schema analysis
    schemas_found = Column(JSON, default=list)  # List of schema types found
    schemas_missing = Column(JSON, default=list)  # Recommended schemas missing
    
    # Title & Meta
    title_length = Column(Integer)
    title_keyword_match = Column(Boolean, default=False)
    meta_length = Column(Integer)
    meta_keyword_match = Column(Boolean, default=False)
    
    # Headings
    h1_count = Column(Integer, default=0)
    h2_count = Column(Integer, default=0)
    h3_count = Column(Integer, default=0)
    heading_structure_valid = Column(Boolean, default=True)
    
    # Links
    internal_links_count = Column(Integer, default=0)
    external_links_count = Column(Integer, default=0)
    broken_links_count = Column(Integer, default=0)
    nofollow_links_count = Column(Integer, default=0)
    
    # Images
    total_images = Column(Integer, default=0)
    images_without_alt = Column(Integer, default=0)
    
    # Technical
    has_robots_txt = Column(Boolean, default=False)
    has_sitemap = Column(Boolean, default=False)
    page_load_time = Column(Float)  # seconds
    
    # Content
    word_count = Column(Integer, default=0)
    keyword_density = Column(JSON, default=dict)  # {keyword: density}
    
    # Additional data
    metrics_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

