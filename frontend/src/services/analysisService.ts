import { api } from '@/lib/api'

/**
 * Analysis Service - API calls for Gemini analysis
 */
export const analysisService = {
  /**
   * Start full automatic analysis for a job
   */
  async analyzeJob(jobId: string): Promise<{ total_chunks: number; status: string }> {
    const { data } = await api.post(`/analysis/${jobId}/analyze`)
    return data
  },

  /**
   * Start full automatic analysis (alias)
   */
  async startAnalysis(jobId: string): Promise<{ total_chunks: number; status: string }> {
    const { data } = await api.post(`/analysis/${jobId}/analyze`)
    return data
  },

  /**
   * Analyze next batch of chunks
   */
  async analyzeBatch(jobId: string, batchSize: number = 5): Promise<{ analyzed: number; status: string }> {
    const { data } = await api.post(`/analysis/${jobId}/analyze-batch`, null, {
      params: { batch_size: batchSize },
    })
    return data
  },
  
  /**
   * Approve an issue
   */
  async approveIssue(jobId: string, issueId: number): Promise<{ status: string }> {
    const { data } = await api.post(`/patches/${jobId}/issues/${issueId}/approve`)
    return data
  },
  
  /**
   * Reject an issue
   */
  async rejectIssue(jobId: string, issueId: number): Promise<{ status: string }> {
    const { data } = await api.post(`/patches/${jobId}/issues/${issueId}/reject`)
    return data
  },
}

