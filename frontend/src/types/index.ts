/**
 * Domain types for AI Anabasis SEO Spider
 */

export type JobStatus = 
  | 'pending'
  | 'uploading'
  | 'chunking'
  | 'analyzing'
  | 'completed'
  | 'failed'

export type IssueSeverity = 'critical' | 'high' | 'medium' | 'low'

export type IssueStatus = 
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'applied'
  | 'failed'
  | 'superseded'
  | 'conflict'

export type IssueType =
  | 'schema_missing'
  | 'meta_issue'
  | 'title_length'
  | 'h_tag_issue'
  | 'link_naturalness'
  | 'image_alt_missing'
  | 'performance_hint'
  | 'js_error'
  | 'css_suggestion'

export interface Job {
  id: string
  name?: string
  status: JobStatus
  upload_filename: string
  total_files?: number
  file_count?: number
  total_chunks?: number
  chunk_count?: number
  analyzed_chunks?: number
  total_issues?: number
  resolved_issues?: number
  created_at: string
  updated_at?: string
}

export interface FileInfo {
  id: number
  file_path: string
  file_type: string
  line_count: number
  size_bytes: number
  analyzed: boolean
}

export interface Issue {
  id: number
  file_path: string
  line_number: number
  issue_type: IssueType
  action: 'insert_after_line' | 'replace_line' | 'annotate'
  code: string
  reason: string
  severity: IssueSeverity
  confidence: number
  review_required: boolean
  suggested_rewrite?: string
  status: IssueStatus
  conflict_with?: number[]
}

export interface CircuitBreakerStatus {
  job_id: string
  failures: number
  threshold: number
  tripped: boolean
  remaining_attempts: number
}

export interface RateLimiterMetrics {
  max_concurrent: number
  active_requests: number
  queue_size: number
  total_requests: number
  total_wait_time_seconds: number
  average_wait_time_seconds: number
  utilization_percent: number
}

export interface LogEntry {
  timestamp: string
  level: 'info' | 'warning' | 'error' | 'success'
  message: string
}

