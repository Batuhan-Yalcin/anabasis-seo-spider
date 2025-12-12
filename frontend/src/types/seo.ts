/**
 * SEO Spider Types
 */

export type SEOAnalysisStatus =
  | 'pending'
  | 'crawling'
  | 'analyzing'
  | 'generating_report'
  | 'completed'
  | 'failed'

export type SEOIssueType =
  | 'schema_missing'
  | 'title_issue'
  | 'meta_issue'
  | 'heading_issue'
  | 'broken_link'
  | 'nofollow_issue'
  | 'anchor_spam'
  | 'semantic_density_low'
  | 'wordcount_low'
  | 'image_alt_missing'
  | 'robots_issue'
  | 'sitemap_issue'
  | 'snippet_issue'
  | 'technical_error'

export type SEOIssueSeverity = 'critical' | 'high' | 'medium' | 'low'

export interface KeywordScore {
  presence_score: number // 0-100
  prominence: number // 0-100
  recommendation: string
}

export interface SEOIssue {
  id: number
  issue_type: SEOIssueType
  severity: SEOIssueSeverity
  confidence: number
  line?: number
  element?: string
  reason: string
  recommendation: string
  example_fix?: string
  context_data?: Record<string, any>
}

export interface SEOMetric {
  schemas_found: string[]
  schemas_missing: string[]
  title_length?: number
  title_keyword_match: boolean
  meta_length?: number
  meta_keyword_match: boolean
  h1_count: number
  h2_count: number
  h3_count: number
  heading_structure_valid: boolean
  internal_links_count: number
  external_links_count: number
  broken_links_count: number
  nofollow_links_count: number
  total_images: number
  images_without_alt: number
  has_robots_txt: boolean
  has_sitemap: boolean
  word_count: number
  keyword_density: Record<string, number>
}

export interface SEOAnalysis {
  id: string
  url: string
  keywords: string[]
  status: SEOAnalysisStatus
  page_title?: string
  meta_description?: string
  word_count: number
  total_issues: number
  critical_issues: number
  high_issues: number
  medium_issues: number
  low_issues: number
  keyword_scores: Record<string, KeywordScore>
  overall_score: number
  technical_score: number
  content_score: number
  html_report_path?: string
  pdf_report_path?: string
  error_message?: string
  created_at: string
  updated_at?: string
  completed_at?: string
}

export interface DetectedData {
  h1_texts?: string[]
  title?: string
  meta_description?: string
  schemas?: string[]
  anchor_texts?: Array<{ text: string; href: string }>
  external_links?: string[]
}

export interface SEOAnalysisDetail extends SEOAnalysis {
  issues: SEOIssue[]
  metrics?: SEOMetric
  detected_data?: DetectedData
}

export interface SEOAnalysisRequest {
  url: string
  keywords: string[]
}

export interface AnalysisProgress {
  analysis_id: string
  status: SEOAnalysisStatus
  progress_percentage: number
  current_step: string
  message: string
}

