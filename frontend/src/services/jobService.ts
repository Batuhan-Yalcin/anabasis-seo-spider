import { api } from '@/lib/api'
import type { Job, FileInfo, Issue } from '@/types'

/**
 * Job Service - API calls for job management
 */
export const jobService = {
  /**
   * Get all jobs
   */
  async getAllJobs(): Promise<Job[]> {
    const { data } = await api.get<Job[]>('/jobs')
    return data
  },

  /**
   * Create new job with file upload
   */
  async createJob(formData: FormData): Promise<Job> {
    const { data } = await api.post<Job>('/jobs/create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },

  /**
   * Get job details
   */
  async getJob(jobId: string): Promise<Job> {
    const { data } = await api.get<Job>(`/jobs/${jobId}`)
    return data
  },

  /**
   * Extract and inventory files
   */
  async extractJob(jobId: string): Promise<{ total_files: number; extract_dir: string }> {
    const { data } = await api.post(`/jobs/${jobId}/extract`)
    return data
  },

  /**
   * Chunk files
   */
  async chunkJob(jobId: string): Promise<{ total_chunks: number }> {
    const { data } = await api.post(`/jobs/${jobId}/chunk`)
    return data
  },

  /**
   * Get files for job
   */
  async getJobFiles(jobId: string): Promise<FileInfo[]> {
    const { data } = await api.get<FileInfo[]>(`/jobs/${jobId}/files`)
    return data
  },

  /**
   * Get issues for job
   */
  async getJobIssues(jobId: string): Promise<Issue[]> {
    const { data } = await api.get<Issue[]>(`/jobs/${jobId}/issues`)
    return data
  },
}

