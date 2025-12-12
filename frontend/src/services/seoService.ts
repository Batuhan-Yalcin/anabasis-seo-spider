/**
 * SEO Spider API Service
 */
import { api } from '../lib/api'
import type {
  SEOAnalysis,
  SEOAnalysisDetail,
  SEOAnalysisRequest,
  AnalysisProgress
} from '../types/seo'

export const seoService = {
  /**
   * Start a new SEO analysis
   */
  async startAnalysis(request: SEOAnalysisRequest): Promise<SEOAnalysis> {
    const response = await api.post<SEOAnalysis>('/seo/analyze', request)
    return response.data
  },

  /**
   * Get analysis by ID
   */
  async getAnalysis(analysisId: string): Promise<SEOAnalysisDetail> {
    const response = await api.get<SEOAnalysisDetail>(`/seo/analyze/${analysisId}`, {
      timeout: 300000 // 5 minutes
    })
    return response.data
  },

  /**
   * Get analysis progress
   */
  async getProgress(analysisId: string): Promise<AnalysisProgress> {
    const response = await api.get<AnalysisProgress>(`/seo/analyze/${analysisId}/progress`)
    return response.data
  },

  /**
   * List all analyses
   */
  async listAnalyses(skip = 0, limit = 20): Promise<SEOAnalysis[]> {
    const response = await api.get<SEOAnalysis[]>('/seo/analyses', {
      params: { skip, limit }
    })
    return response.data
  },

  /**
   * Delete an analysis
   */
  async deleteAnalysis(analysisId: string): Promise<void> {
    await api.delete(`/seo/analyze/${analysisId}`)
  },

  /**
   * Poll for analysis completion
   */
  async pollUntilComplete(
    analysisId: string,
    onProgress?: (progress: AnalysisProgress) => void,
    intervalMs = 3000, // 3 seconds
    maxAttempts = 200 // 10 minutes max (200 * 3s = 600s)
  ): Promise<SEOAnalysisDetail> {
    let attempts = 0

    while (attempts < maxAttempts) {
      const progress = await this.getProgress(analysisId)
      
      if (onProgress) {
        onProgress(progress)
      }

      if (progress.status === 'completed') {
        return await this.getAnalysis(analysisId)
      }

      if (progress.status === 'failed') {
        const detail = await this.getAnalysis(analysisId)
        throw new Error(detail.error_message || 'Analysis failed')
      }

      await new Promise(resolve => setTimeout(resolve, intervalMs))
      attempts++
    }

    throw new Error('Analysis timeout')
  }
}

