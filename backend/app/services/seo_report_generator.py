"""
SEO Report Generator
Generates HTML and PDF reports for SEO analysis
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Template
import subprocess

from app.schemas.seo_schemas import (
    SEOIssueResponse,
    SEOMetricResponse,
    KeywordScore,
    SEOIssueSeverity
)

logger = logging.getLogger(__name__)


class SEOReportGenerator:
    """Generate SEO analysis reports in HTML and PDF formats"""
    
    def __init__(self, reports_dir: str = "workspace/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(
        self,
        analysis_id: str,
        url: str,
        keywords: List[str],
        issues: List[SEOIssueResponse],
        metrics: Optional[SEOMetricResponse],
        keyword_scores: Dict[str, KeywordScore],
        overall_score: float,
        technical_score: float,
        content_score: float,
        page_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        detected_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate HTML report
        
        Returns:
            Path to generated HTML file
        """
        
        # Group issues by severity
        issues_by_severity = {
            'critical': [i for i in issues if i.severity == SEOIssueSeverity.CRITICAL],
            'high': [i for i in issues if i.severity == SEOIssueSeverity.HIGH],
            'medium': [i for i in issues if i.severity == SEOIssueSeverity.MEDIUM],
            'low': [i for i in issues if i.severity == SEOIssueSeverity.LOW],
        }
        
        # Prepare context
        context = {
            'analysis_id': analysis_id,
            'url': url,
            'keywords': keywords,
            'page_title': page_title or 'N/A',
            'meta_description': meta_description or 'N/A',
            'overall_score': overall_score,
            'technical_score': technical_score,
            'content_score': content_score,
            'total_issues': len(issues),
            'critical_count': len(issues_by_severity['critical']),
            'high_count': len(issues_by_severity['high']),
            'medium_count': len(issues_by_severity['medium']),
            'low_count': len(issues_by_severity['low']),
            'issues_by_severity': issues_by_severity,
            'metrics': metrics,
            'keyword_scores': keyword_scores,
            'detected_data': detected_data or {},
            'generated_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'score_color': self._get_score_color(overall_score),
            'score_label': self._get_score_label(overall_score)
        }
        
        # Render HTML
        html_content = self._render_html_template(context)
        
        # Save HTML file
        html_path = self.reports_dir / f"{analysis_id}.html"
        html_path.write_text(html_content, encoding='utf-8')
        
        logger.info(f"HTML report generated: {html_path}")
        return str(html_path)
    
    def generate_pdf_report(self, html_path: str, analysis_id: str) -> str:
        """
        Generate PDF from HTML report using WeasyPrint
        
        Returns:
            Path to generated PDF file
        """
        
        pdf_path = self.reports_dir / f"{analysis_id}.pdf"
        
        try:
            # Try using WeasyPrint
            from weasyprint import HTML
            # Read HTML content first, then convert to PDF
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Use base_url to resolve relative URIs
            base_url = str(Path(html_path).parent.absolute())
            # Create HTML document with proper base_url
            html_doc = HTML(string=html_content, base_url=f"file://{base_url}/")
            # Write PDF - use path as string
            html_doc.write_pdf(str(pdf_path))
            logger.info(f"PDF report generated with WeasyPrint: {pdf_path}")
            
        except (ImportError, Exception) as e:
            logger.warning(f"WeasyPrint PDF generation failed: {str(e)}, falling back to HTML only")
            # Return HTML path as fallback - PDF is optional
            return html_path
        
        return str(pdf_path)
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 80:
            return '#10b981'  # green
        elif score >= 60:
            return '#f59e0b'  # orange
        elif score >= 40:
            return '#ef4444'  # red
        else:
            return '#991b1b'  # dark red
    
    def _get_score_label(self, score: float) -> str:
        """Get label based on score"""
        if score >= 80:
            return 'Mükemmel'
        elif score >= 60:
            return 'İyi'
        elif score >= 40:
            return 'Orta'
        else:
            return 'Zayıf'
    
    def _render_html_template(self, context: Dict[str, Any]) -> str:
        """Render HTML template"""
        
        template_str = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Analiz Raporu - {{ url }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .header {
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .logo {
            font-size: 28px;
            font-weight: 700;
            color: #3b82f6;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #6b7280;
            font-size: 14px;
        }
        
        .meta-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f3f4f6;
            border-radius: 8px;
        }
        
        .meta-item {
            display: flex;
            flex-direction: column;
        }
        
        .meta-label {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        
        .meta-value {
            font-size: 14px;
            color: #1f2937;
            font-weight: 500;
        }
        
        .scores {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .score-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
        }
        
        .score-card.overall {
            background: linear-gradient(135deg, {{ score_color }} 0%, {{ score_color }}dd 100%);
        }
        
        .score-card.technical {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }
        
        .score-card.content {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        }
        
        .score-value {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .score-label {
            font-size: 14px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section-title {
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }
        
        .issue-summary {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .issue-count {
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .issue-count.critical {
            background: #fee2e2;
            border-left: 4px solid #dc2626;
        }
        
        .issue-count.high {
            background: #fed7aa;
            border-left: 4px solid #ea580c;
        }
        
        .issue-count.medium {
            background: #fef3c7;
            border-left: 4px solid #eab308;
        }
        
        .issue-count.low {
            background: #e5e7eb;
            border-left: 4px solid #6b7280;
        }
        
        .issue-count-number {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .issue-count-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #4b5563;
        }
        
        .issue-item {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }
        
        .issue-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .severity-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .severity-badge.critical {
            background: #dc2626;
            color: white;
        }
        
        .severity-badge.high {
            background: #ea580c;
            color: white;
        }
        
        .severity-badge.medium {
            background: #eab308;
            color: white;
        }
        
        .severity-badge.low {
            background: #6b7280;
            color: white;
        }
        
        .issue-type {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
        }
        
        .issue-reason {
            font-size: 14px;
            color: #1f2937;
            margin-bottom: 10px;
            font-weight: 500;
        }
        
        .issue-recommendation {
            font-size: 13px;
            color: #4b5563;
            margin-bottom: 10px;
            padding: 10px;
            background: white;
            border-radius: 6px;
        }
        
        .issue-fix {
            font-size: 12px;
            background: #1f2937;
            color: #10b981;
            padding: 12px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        
        .keyword-scores {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .keyword-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
        }
        
        .keyword-name {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 15px;
        }
        
        .keyword-metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .keyword-metric-label {
            font-size: 13px;
            color: #6b7280;
        }
        
        .keyword-metric-value {
            font-size: 13px;
            font-weight: 600;
            color: #1f2937;
        }
        
        .keyword-recommendation {
            font-size: 12px;
            color: #4b5563;
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 6px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .metric-item {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #3b82f6;
        }
        
        .metric-label {
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
        }
        
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🔍 AI Anabasis SEO Spider</div>
            <div class="subtitle">Profesyonel SEO Analiz Raporu</div>
        </div>
        
        <div class="meta-info">
            <div class="meta-item">
                <div class="meta-label">Analiz Edilen URL</div>
                <div class="meta-value">{{ url }}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Anahtar Kelimeler</div>
                <div class="meta-value">{{ keywords|join(', ') }}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Rapor Tarihi</div>
                <div class="meta-value">{{ generated_at }}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Analiz ID</div>
                <div class="meta-value">{{ analysis_id[:8] }}</div>
            </div>
        </div>
        
        <div class="scores">
            <div class="score-card overall">
                <div class="score-value">{{ overall_score|int }}</div>
                <div class="score-label">Genel Skor - {{ score_label }}</div>
            </div>
            <div class="score-card technical">
                <div class="score-value">{{ technical_score|int }}</div>
                <div class="score-label">Teknik SEO</div>
            </div>
            <div class="score-card content">
                <div class="score-value">{{ content_score|int }}</div>
                <div class="score-label">İçerik Kalitesi</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📊 Sorun Özeti</div>
            <div class="issue-summary">
                <div class="issue-count critical">
                    <div class="issue-count-number">{{ critical_count }}</div>
                    <div class="issue-count-label">Kritik</div>
                </div>
                <div class="issue-count high">
                    <div class="issue-count-number">{{ high_count }}</div>
                    <div class="issue-count-label">Yüksek</div>
                </div>
                <div class="issue-count medium">
                    <div class="issue-count-number">{{ medium_count }}</div>
                    <div class="issue-count-label">Orta</div>
                </div>
                <div class="issue-count low">
                    <div class="issue-count-number">{{ low_count }}</div>
                    <div class="issue-count-label">Düşük</div>
                </div>
            </div>
        </div>
        
        {% if keyword_scores %}
        <div class="section">
            <div class="section-title">🎯 Anahtar Kelime Performansı</div>
            <div class="keyword-scores">
                {% for keyword, score in keyword_scores.items() %}
                <div class="keyword-card">
                    <div class="keyword-name">{{ keyword }}</div>
                    <div class="keyword-metric">
                        <span class="keyword-metric-label">Varlık Skoru:</span>
                        <span class="keyword-metric-value">{{ score.presence_score|int }}/100</span>
                    </div>
                    <div class="keyword-metric">
                        <span class="keyword-metric-label">Öne Çıkma:</span>
                        <span class="keyword-metric-value">{{ score.prominence|int }}/100</span>
                    </div>
                    <div class="keyword-recommendation">
                        💡 {{ score.recommendation }}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if metrics %}
        <div class="section">
            <div class="section-title">📈 Teknik Metrikler</div>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">Kelime Sayısı</div>
                    <div class="metric-value">{{ metrics.word_count }}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">H1 Sayısı</div>
                    <div class="metric-value">{{ metrics.h1_count }}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">İç Link</div>
                    <div class="metric-value">{{ metrics.internal_links_count }}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Dış Link</div>
                    <div class="metric-value">{{ metrics.external_links_count }}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Toplam Görsel</div>
                    <div class="metric-value">{{ metrics.total_images }}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">ALT Eksik Görsel</div>
                    <div class="metric-value">{{ metrics.images_without_alt }}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Bulunan Schema</div>
                    <div class="metric-value">{{ metrics.schemas_found|length }}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Kırık Link</div>
                    <div class="metric-value">{{ metrics.broken_links_count }}</div>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% if detected_data %}
        <div class="section">
            <div class="section-title">🔎 Tespit Edilen SEO Elementleri</div>
            <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin-top: 15px;">
                
                {% if detected_data.h1_texts %}
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #1f2937; margin-bottom: 10px; font-size: 16px;">📌 Sitenizdeki H1 Etiketleri ({{ detected_data.h1_texts|length }} adet):</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #4b5563;">
                        {% for h1_text in detected_data.h1_texts %}
                        <li style="margin-bottom: 5px;">"{{ h1_text }}"</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #1f2937; margin-bottom: 10px; font-size: 16px;">📄 Sitenizin Title Etiketi:</h4>
                    <div style="background: white; padding: 12px; border-radius: 6px; border-left: 4px solid #3b82f6; color: #1f2937; font-weight: 500;">
                        {{ detected_data.title or 'Bulunamadı' }}
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #1f2937; margin-bottom: 10px; font-size: 16px;">📝 Sitenizin Meta Description:</h4>
                    <div style="background: white; padding: 12px; border-radius: 6px; border-left: 4px solid #10b981; color: #1f2937;">
                        {{ detected_data.meta_description or 'Bulunamadı' }}
                    </div>
                </div>
                
                {% if detected_data.schemas %}
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #1f2937; margin-bottom: 10px; font-size: 16px;">🏷️ Sitenizde Tespit Edilen Schema Türleri:</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        {% for schema in detected_data.schemas %}
                        <span style="background: #3b82f6; color: white; padding: 6px 12px; border-radius: 4px; font-size: 14px; font-weight: 500;">{{ schema }}</span>
                        {% endfor %}
                    </div>
                    {% if detected_data.schemas|length == 0 %}
                    <div style="color: #ef4444; font-style: italic;">Hiç schema bulunamadı</div>
                    {% endif %}
                </div>
                {% endif %}
                
                {% if detected_data.anchor_texts %}
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #1f2937; margin-bottom: 10px; font-size: 16px;">🔗 Sitenizdeki İç Link Anchor Text'leri (İlk 15):</h4>
                    <div style="background: white; padding: 12px; border-radius: 6px; max-height: 200px; overflow-y: auto;">
                        <ul style="margin: 0; padding-left: 20px; color: #4b5563; columns: 2; column-gap: 20px;">
                            {% for anchor in detected_data.anchor_texts[:15] %}
                            <li style="margin-bottom: 5px; break-inside: avoid;">
                                "{{ anchor.text }}" → <span style="color: #6b7280; font-size: 12px;">{{ anchor.href[:50] }}{% if anchor.href|length > 50 %}...{% endif %}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endif %}
                
                {% if detected_data.external_links %}
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #1f2937; margin-bottom: 10px; font-size: 16px;">🌐 Sitenizdeki Dış Linkler (Backlinks - İlk 10):</h4>
                    <div style="background: white; padding: 12px; border-radius: 6px; max-height: 200px; overflow-y: auto;">
                        <ul style="margin: 0; padding-left: 20px; color: #4b5563;">
                            {% for link in detected_data.external_links[:10] %}
                            <li style="margin-bottom: 5px;">
                                <a href="{{ link }}" target="_blank" style="color: #3b82f6; text-decoration: none;">{{ link }}</a>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endif %}
                
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <div class="section-title">🔍 Detaylı Sorunlar ve Öneriler</div>
            
            {% for severity, severity_issues in issues_by_severity.items() %}
                {% if severity_issues %}
                <h3 style="margin-top: 30px; margin-bottom: 15px; color: #1f2937; text-transform: capitalize;">
                    {{ severity|replace('critical', 'Kritik')|replace('high', 'Yüksek')|replace('medium', 'Orta')|replace('low', 'Düşük') }} Öncelikli Sorunlar
                </h3>
                
                {% for issue in severity_issues %}
                <div class="issue-item">
                    <div class="issue-header">
                        <span class="severity-badge {{ severity }}">{{ severity|upper }}</span>
                        <span class="issue-type">{{ issue.issue_type.value }}</span>
                    </div>
                    <div class="issue-reason">{{ issue.reason }}</div>
                    <div class="issue-recommendation">
                        <strong>💡 Öneri:</strong> {{ issue.recommendation }}
                    </div>
                    {% if issue.example_fix %}
                    <div class="issue-fix">{{ issue.example_fix }}</div>
                    {% endif %}
                </div>
                {% endfor %}
                {% endif %}
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>Bu rapor AI Anabasis SEO Spider tarafından otomatik olarak oluşturulmuştur.</p>
            <p>© 2024 AI Anabasis - Tüm hakları saklıdır.</p>
        </div>
    </div>
</body>
</html>"""
        
        template = Template(template_str)
        return template.render(**context)

