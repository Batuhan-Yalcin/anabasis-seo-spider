"""
SEO Spider API Router
Endpoints for SEO analysis
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.seo_models import SEOAnalysis, SEOIssue, SEOMetric, SEOAnalysisStatus
from app.schemas.seo_schemas import (
    SEOAnalysisRequest,
    SEOAnalysisResponse,
    SEOAnalysisDetailResponse,
    SEOIssueResponse,
    SEOMetricResponse,
    KeywordScore,
    AnalysisProgress
)
from app.services.seo_crawler import SEOCrawler, HTMLAnalyzer
from app.services.seo_analyzer import SEOAnalyzer
from app.services.seo_report_generator import SEOReportGenerator
from app.services.gemini_client import GeminiClient
from app.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/seo", tags=["SEO Spider"])


# Dependency for services
def get_gemini_client():
    return GeminiClient()


def get_seo_analyzer(gemini: GeminiClient = Depends(get_gemini_client)):
    return SEOAnalyzer(gemini)


def get_report_generator():
    return SEOReportGenerator()


@router.post("/analyze", response_model=SEOAnalysisResponse)
async def start_seo_analysis(
    request: SEOAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new SEO analysis
    
    This endpoint initiates the analysis and returns immediately.
    The analysis runs in the background.
    """
    
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Create analysis record
    analysis = SEOAnalysis(
        id=analysis_id,
        url=request.url,
        keywords=request.keywords,
        status=SEOAnalysisStatus.PENDING,
        keyword_scores={}
    )
    
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    # Start analysis in background
    background_tasks.add_task(
        run_seo_analysis,
        analysis_id=analysis_id,
        url=request.url,
        keywords=request.keywords
    )
    
    logger.info(f"Started SEO analysis {analysis_id} for {request.url}")
    
    return SEOAnalysisResponse(
        id=analysis.id,
        url=analysis.url,
        keywords=analysis.keywords,
        status=analysis.status,
        word_count=0,
        total_issues=0,
        critical_issues=0,
        high_issues=0,
        medium_issues=0,
        low_issues=0,
        keyword_scores={},
        overall_score=0.0,
        technical_score=0.0,
        content_score=0.0,
        created_at=analysis.created_at
    )


@router.get("/analyze/{analysis_id}", response_model=SEOAnalysisDetailResponse)
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get SEO analysis results with details"""
    
    # Get analysis
    result = await db.execute(select(SEOAnalysis).where(SEOAnalysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get issues
    issues_result = await db.execute(select(SEOIssue).where(SEOIssue.analysis_id == analysis_id))
    issues = issues_result.scalars().all()
    
    # Get metrics
    metrics_result = await db.execute(select(SEOMetric).where(SEOMetric.analysis_id == analysis_id))
    metrics = metrics_result.scalar_one_or_none()
    
    # Convert keyword_scores to KeywordScore objects
    keyword_scores = {}
    if analysis.keyword_scores:
        for kw, score_data in analysis.keyword_scores.items():
            keyword_scores[kw] = KeywordScore(**score_data)
    
    # Get detected data from metadata
    detected_data = None
    if analysis.analysis_metadata and 'detected_data' in analysis.analysis_metadata:
        detected_data = analysis.analysis_metadata['detected_data']
    
    return SEOAnalysisDetailResponse(
        id=analysis.id,
        url=analysis.url,
        keywords=analysis.keywords,
        status=analysis.status,
        page_title=analysis.page_title,
        meta_description=analysis.meta_description,
        word_count=analysis.word_count,
        total_issues=analysis.total_issues,
        critical_issues=analysis.critical_issues,
        high_issues=analysis.high_issues,
        medium_issues=analysis.medium_issues,
        low_issues=analysis.low_issues,
        keyword_scores=keyword_scores,
        overall_score=analysis.overall_score,
        technical_score=analysis.technical_score,
        content_score=analysis.content_score,
        html_report_path=analysis.html_report_path,
        pdf_report_path=analysis.pdf_report_path,
        error_message=analysis.error_message,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        completed_at=analysis.completed_at,
        issues=[SEOIssueResponse.model_validate(issue) for issue in issues],
        metrics=SEOMetricResponse.model_validate(metrics) if metrics else None,
        detected_data=detected_data
    )


@router.get("/analyze/{analysis_id}/progress", response_model=AnalysisProgress)
async def get_analysis_progress(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get analysis progress status"""
    
    result = await db.execute(select(SEOAnalysis).where(SEOAnalysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Calculate progress percentage
    progress_map = {
        SEOAnalysisStatus.PENDING: 0,
        SEOAnalysisStatus.CRAWLING: 25,
        SEOAnalysisStatus.ANALYZING: 50,
        SEOAnalysisStatus.GENERATING_REPORT: 75,
        SEOAnalysisStatus.COMPLETED: 100,
        SEOAnalysisStatus.FAILED: 0
    }
    
    status_messages = {
        SEOAnalysisStatus.PENDING: "Analiz başlatılıyor...",
        SEOAnalysisStatus.CRAWLING: "Sayfa taranıyor...",
        SEOAnalysisStatus.ANALYZING: "SEO analizi yapılıyor...",
        SEOAnalysisStatus.GENERATING_REPORT: "Rapor oluşturuluyor...",
        SEOAnalysisStatus.COMPLETED: "Analiz tamamlandı!",
        SEOAnalysisStatus.FAILED: "Analiz başarısız oldu."
    }
    
    return AnalysisProgress(
        analysis_id=analysis.id,
        status=analysis.status,
        progress_percentage=progress_map.get(analysis.status, 0),
        current_step=analysis.status.value,
        message=status_messages.get(analysis.status, "İşleniyor...")
    )


@router.get("/analyses", response_model=List[SEOAnalysisResponse])
async def list_analyses(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List all SEO analyses"""
    
    result = await db.execute(
        select(SEOAnalysis)
        .order_by(desc(SEOAnalysis.created_at))
        .offset(skip)
        .limit(limit)
    )
    analyses = result.scalars().all()
    
    results = []
    for analysis in analyses:
        keyword_scores = {}
        if analysis.keyword_scores:
            for kw, score_data in analysis.keyword_scores.items():
                keyword_scores[kw] = KeywordScore(**score_data)
        
        results.append(SEOAnalysisResponse(
            id=analysis.id,
            url=analysis.url,
            keywords=analysis.keywords,
            status=analysis.status,
            page_title=analysis.page_title,
            meta_description=analysis.meta_description,
            word_count=analysis.word_count,
            total_issues=analysis.total_issues,
            critical_issues=analysis.critical_issues,
            high_issues=analysis.high_issues,
            medium_issues=analysis.medium_issues,
            low_issues=analysis.low_issues,
            keyword_scores=keyword_scores,
            overall_score=analysis.overall_score,
            technical_score=analysis.technical_score,
            content_score=analysis.content_score,
            html_report_path=analysis.html_report_path,
            pdf_report_path=analysis.pdf_report_path,
            error_message=analysis.error_message,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
            completed_at=analysis.completed_at
        ))
    
    return results


@router.delete("/analyze/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an SEO analysis"""
    
    result = await db.execute(select(SEOAnalysis).where(SEOAnalysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Delete related records
    issues_result = await db.execute(select(SEOIssue).where(SEOIssue.analysis_id == analysis_id))
    issues = issues_result.scalars().all()
    for issue in issues:
        await db.delete(issue)
    
    metrics_result = await db.execute(select(SEOMetric).where(SEOMetric.analysis_id == analysis_id))
    metrics = metrics_result.scalar_one_or_none()
    if metrics:
        await db.delete(metrics)
    
    await db.delete(analysis)
    await db.commit()
    
    return {"message": "Analysis deleted successfully"}


# Background task function
async def run_seo_analysis(analysis_id: str, url: str, keywords: List[str]):
    """
    Run complete SEO analysis pipeline
    
    This function runs in the background and updates the database
    """
    
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(SEOAnalysis).where(SEOAnalysis.id == analysis_id))
            analysis = result.scalar_one_or_none()
            if not analysis:
                logger.error(f"Analysis {analysis_id} not found")
                return
            
            # Step 1: Crawl
            logger.info(f"[{analysis_id}] Starting crawl...")
            analysis.status = SEOAnalysisStatus.CRAWLING
            await db.commit()
            
            async with SEOCrawler() as crawler:
                crawl_result = await crawler.crawl(url, analysis_id)
                
                if crawl_result.error:
                    raise Exception(f"Crawl error: {crawl_result.error}")
                
                # Update analysis with crawl data
                analysis.html_content = crawl_result.html_content
                analysis.screenshot_path = crawl_result.screenshot_path
                analysis.page_title = crawl_result.page_title
                analysis.meta_description = crawl_result.meta_description
                await db.commit()
                
                # Extract metrics using HTMLAnalyzer
                html_analyzer = HTMLAnalyzer(crawl_result.html_content, url)
                
                schemas = html_analyzer.extract_schemas()
                # Use Playwright's visible H1 count if available (more accurate)
                headings = html_analyzer.analyze_headings(visible_h1_count=crawl_result.visible_h1_count)
                links = html_analyzer.analyze_links()
                images = html_analyzer.analyze_images()
                word_count = html_analyzer.calculate_word_count()
                keyword_density = html_analyzer.calculate_keyword_density(keywords)
                
                # Check robots.txt and sitemap
                robots_data = await crawler.check_robots_txt(url)
                sitemap_data = await crawler.check_sitemap(url)
                
                # Check broken links (check internal links only, max 20)
                all_links_to_check = links['internal_links'][:20]
                broken_links_result = await crawler.check_broken_links(all_links_to_check, max_checks=20)
                broken_links_count = broken_links_result['broken_count']
                
                # Create metrics record
                recommended_schemas = ["Organization", "WebSite", "WebPage", "BreadcrumbList"]
                missing_schemas = [s for s in recommended_schemas if s not in schemas]
                
                metrics = SEOMetric(
                    analysis_id=analysis_id,
                    schemas_found=schemas,
                    schemas_missing=missing_schemas,
                    title_length=len(crawl_result.page_title) if crawl_result.page_title else 0,
                    title_keyword_match=any(kw.lower() in (crawl_result.page_title or "").lower() for kw in keywords),
                    meta_length=len(crawl_result.meta_description) if crawl_result.meta_description else 0,
                    meta_keyword_match=any(kw.lower() in (crawl_result.meta_description or "").lower() for kw in keywords),
                    h1_count=headings['h1_count'],
                    h2_count=headings['h2_count'],
                    h3_count=headings['h3_count'],
                    heading_structure_valid=not headings['has_multiple_h1'] and not headings['has_no_h1'],
                    internal_links_count=links['internal_count'],
                    external_links_count=links['external_count'],
                    broken_links_count=broken_links_count,
                    nofollow_links_count=links['nofollow_count'],
                    total_images=images['total_images'],
                    images_without_alt=images['images_without_alt'],
                    has_robots_txt=robots_data.get('exists', False),
                    has_sitemap=sitemap_data.get('exists', False),
                    page_load_time=crawl_result.load_time,
                    word_count=word_count,
                    keyword_density=keyword_density
                )
                
                db.add(metrics)
                analysis.word_count = word_count
                await db.commit()
            
            # Step 2: Analyze with Gemini
            logger.info(f"[{analysis_id}] Starting AI analysis...")
            analysis.status = SEOAnalysisStatus.ANALYZING
            await db.commit()
            
            gemini_client = GeminiClient()
            analyzer = SEOAnalyzer(gemini_client)
            
            # Get anchor texts for natural anchor text analysis
            anchor_texts = links.get('anchor_texts', [])
            
            # Prepare real data from HTMLAnalyzer to prevent false positives
            real_data = {
                'h1_count': headings['h1_count'],
                'h1_texts': headings.get('h1_texts', []),
                'h2_count': headings['h2_count'],
                'h3_count': headings['h3_count'],
                'schemas': schemas,
                'title': crawl_result.page_title,
                'meta_description': crawl_result.meta_description,
                'word_count': word_count,
                'has_multiple_h1': headings.get('has_multiple_h1', False),
                'has_no_h1': headings.get('has_no_h1', False)
            }
            
            analysis_result = await analyzer.analyze_html(
                analysis.html_content,
                url,
                keywords,
                anchor_texts=anchor_texts,
                real_data=real_data
            )
            
            # Save issues
            severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            
            for gemini_issue in analysis_result.issues:
                issue = SEOIssue(
                    analysis_id=analysis_id,
                    issue_type=gemini_issue.type,
                    severity=gemini_issue.severity,
                    confidence=gemini_issue.confidence,
                    line=gemini_issue.line,
                    reason=gemini_issue.reason,
                    recommendation=gemini_issue.recommendation,
                    example_fix=gemini_issue.example_fix
                )
                db.add(issue)
                severity_counts[gemini_issue.severity.value] += 1
            
            # Calculate scores
            scores = analyzer.calculate_overall_score(
                analysis_result.issues,
                analysis_result.keyword_scores
            )
            
            # Update analysis with results
            analysis.total_issues = len(analysis_result.issues)
            analysis.critical_issues = severity_counts['critical']
            analysis.high_issues = severity_counts['high']
            analysis.medium_issues = severity_counts['medium']
            analysis.low_issues = severity_counts['low']
            analysis.overall_score = scores['overall_score']
            analysis.technical_score = scores['technical_score']
            analysis.content_score = scores['content_score']
            
            # Convert keyword scores to dict
            keyword_scores_dict = {}
            for kw, score in analysis_result.keyword_scores.items():
                keyword_scores_dict[kw] = {
                    'presence_score': score.presence_score,
                    'prominence': score.prominence,
                    'recommendation': score.recommendation
                }
            analysis.keyword_scores = keyword_scores_dict
            
            await db.commit()
            
            # Step 3: Generate reports
            logger.info(f"[{analysis_id}] Generating reports...")
            analysis.status = SEOAnalysisStatus.GENERATING_REPORT
            await db.commit()
            
            report_gen = SEOReportGenerator()
            
            # Get issues and metrics for report
            issues_result = await db.execute(select(SEOIssue).where(SEOIssue.analysis_id == analysis_id))
            issues = issues_result.scalars().all()
            metrics_result = await db.execute(select(SEOMetric).where(SEOMetric.analysis_id == analysis_id))
            metrics = metrics_result.scalar_one_or_none()
            
            # Prepare detected data for report
            detected_data = {
                'h1_texts': headings.get('h1_texts', []),
                'title': crawl_result.page_title,
                'meta_description': crawl_result.meta_description,
                'schemas': schemas,
                'anchor_texts': links.get('anchor_texts', [])[:15],  # First 15 anchor texts
                'external_links': links.get('external_links', [])[:10]  # First 10 external links
            }
            
            # Generate HTML report
            html_path = report_gen.generate_html_report(
                analysis_id=analysis_id,
                url=url,
                keywords=keywords,
                issues=[SEOIssueResponse.model_validate(i) for i in issues],
                metrics=SEOMetricResponse.model_validate(metrics) if metrics else None,
                keyword_scores={k: KeywordScore(**v) for k, v in keyword_scores_dict.items()},
                overall_score=analysis.overall_score,
                technical_score=analysis.technical_score,
                content_score=analysis.content_score,
                page_title=analysis.page_title,
                meta_description=analysis.meta_description,
                detected_data=detected_data
            )
            
            # Generate PDF report
            pdf_path = report_gen.generate_pdf_report(html_path, analysis_id)
            
            analysis.html_report_path = html_path
            analysis.pdf_report_path = pdf_path
            
            # Save detected data to analysis metadata
            analysis.analysis_metadata = {
                'detected_data': detected_data
            }
            
            # Complete
            analysis.status = SEOAnalysisStatus.COMPLETED
            analysis.completed_at = datetime.now()
            await db.commit()
            
            logger.info(f"[{analysis_id}] Analysis completed successfully!")
        
        except Exception as e:
            logger.error(f"[{analysis_id}] Analysis failed: {str(e)}", exc_info=True)
            
            result = await db.execute(select(SEOAnalysis).where(SEOAnalysis.id == analysis_id))
            analysis = result.scalar_one_or_none()
            if analysis:
                analysis.status = SEOAnalysisStatus.FAILED
                analysis.error_message = str(e)
                await db.commit()

