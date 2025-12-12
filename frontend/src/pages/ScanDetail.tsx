import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, FileText, AlertCircle, CheckCircle, Play, XCircle, Download } from 'lucide-react'
// @ts-ignore - jsPDF types
import jsPDF from 'jspdf'
// @ts-ignore - autoTable types
import autoTable from 'jspdf-autotable'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { useTranslation } from '@/lib/i18n'
import { jobService } from '@/services/jobService'
import { analysisService } from '@/services/analysisService'
import { Issue } from '@/types'

export function ScanDetail() {
  const { t } = useTranslation()
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  console.log('[ScanDetail] jobId:', jobId)
  
  // Fetch job details
  const { data: job, isLoading: jobLoading, error: jobError } = useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => {
      console.log('[ScanDetail] Fetching job:', jobId)
      try {
        const result = await jobService.getJob(jobId!)
        console.log('[ScanDetail] Job data:', result)
        return result
      } catch (err) {
        console.error('[ScanDetail] Error fetching job:', err)
        throw err
      }
    },
    enabled: !!jobId,
    refetchInterval: 5000,
    retry: 1,
  })
  
  console.log('[ScanDetail] job:', job, 'loading:', jobLoading, 'error:', jobError)
  
  // Fetch job issues
  const { data: issues = [] } = useQuery({
    queryKey: ['job-issues', jobId],
    queryFn: () => jobService.getJobIssues(jobId!),
    enabled: !!jobId,
    refetchInterval: 5000,
  })
  
  // Start analysis mutation
  const startAnalysisMutation = useMutation({
    mutationFn: () => analysisService.analyzeJob(jobId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', jobId] })
      queryClient.invalidateQueries({ queryKey: ['job-issues', jobId] })
    },
  })
  
  // Approve issue mutation
  const approveIssueMutation = useMutation({
    mutationFn: (issueId: number) => 
      analysisService.approveIssue(jobId!, issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-issues', jobId] })
    },
  })
  
  // Reject issue mutation
  const rejectIssueMutation = useMutation({
    mutationFn: (issueId: number) => 
      analysisService.rejectIssue(jobId!, issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-issues', jobId] })
    },
  })
  
  // Show loading state
  if (jobLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">{t('common.loading')}</p>
        </div>
      </div>
    )
  }
  
  // Show error if job not found
  if (!job) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-severity-critical mx-auto mb-4" />
          <p className="text-text-primary text-lg mb-2">Job bulunamadı</p>
          <p className="text-text-secondary mb-4">Job ID: {jobId}</p>
          <Button variant="primary" onClick={() => navigate('/projects')}>
            Projelere Dön
          </Button>
        </div>
      </div>
    )
  }
  
  const criticalIssues = issues.filter(i => i.severity === 'critical')
  const highIssues = issues.filter(i => i.severity === 'high')
  const mediumIssues = issues.filter(i => i.severity === 'medium')
  const lowIssues = issues.filter(i => i.severity === 'low')
  const approvedIssues = issues.filter(i => i.status === 'approved')
  
  // PDF Export Function
  const exportToPDF = () => {
    const doc = new jsPDF('p', 'mm', 'a4')
    
    // Header with gradient-like effect
    doc.setFillColor(59, 130, 246)
    doc.rect(0, 0, 210, 40, 'F')
    
    // Title
    doc.setTextColor(255, 255, 255)
    doc.setFontSize(24)
    doc.setFont('helvetica', 'bold')
    doc.text('SEO Analiz Raporu', 14, 20)
    
    // Job Info
    doc.setFontSize(11)
    doc.setFont('helvetica', 'normal')
    doc.text(`Dosya: ${job?.upload_filename || 'N/A'}`, 14, 30)
    doc.text(`Tarih: ${new Date().toLocaleDateString('tr-TR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })}`, 14, 36)
    
    // Summary Box
    doc.setFillColor(248, 250, 252)
    doc.rect(0, 45, 210, 25, 'F')
    
    doc.setTextColor(30, 41, 59)
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.text('OZET', 14, 52)
    
    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.text(`Toplam Sorun: ${issues.length}`, 14, 58)
    
    // Severity counts with colors
    doc.setTextColor(220, 38, 38)
    doc.text(`Kritik: ${criticalIssues.length}`, 60, 58)
    doc.setTextColor(234, 88, 12)
    doc.text(`Yuksek: ${highIssues.length}`, 90, 58)
    doc.setTextColor(234, 179, 8)
    doc.text(`Orta: ${mediumIssues.length}`, 120, 58)
    doc.setTextColor(156, 163, 175)
    doc.text(`Dusuk: ${lowIssues.length}`, 145, 58)
    
    // Status counts
    doc.setTextColor(34, 197, 94)
    doc.text(`Onaylanan: ${approvedIssues.length}`, 14, 64)
    doc.setTextColor(100, 116, 139)
    doc.text(`Bekleyen: ${issues.filter(i => i.status === 'pending').length}`, 55, 64)
    doc.setTextColor(239, 68, 68)
    doc.text(`Reddedilen: ${issues.filter(i => i.status === 'rejected').length}`, 95, 64)
    
    // Issues - Detailed List (not table)
    let yPos = 80
    
    issues.forEach((issue: Issue) => {
      // Check if we need a new page
      if (yPos > 270) {
        doc.addPage()
        yPos = 20
      }
      
      // Issue Box
      doc.setFillColor(249, 250, 251)
      doc.rect(10, yPos - 5, 190, 35, 'F')
      doc.setDrawColor(229, 231, 235)
      doc.rect(10, yPos - 5, 190, 35, 'S')
      
      // Priority Badge
      const severityColors: Record<string, [number, number, number]> = {
        critical: [220, 38, 38],
        high: [234, 88, 12],
        medium: [234, 179, 8],
        low: [156, 163, 175]
      }
      const color = severityColors[issue.severity] || [156, 163, 175]
      doc.setFillColor(color[0], color[1], color[2])
      doc.roundedRect(12, yPos - 3, 20, 6, 1, 1, 'F')
      doc.setTextColor(255, 255, 255)
      doc.setFontSize(7)
      const severityText = issue.severity === 'critical' ? 'KRITIK' : 
                          issue.severity === 'high' ? 'YUKSEK' : 
                          issue.severity === 'medium' ? 'ORTA' : 'DUSUK'
      doc.text(severityText, 22, yPos + 1, { align: 'center' })
      
      // Issue Type
      doc.setTextColor(100, 116, 139)
      doc.setFontSize(7)
      doc.text(issue.issue_type.toUpperCase(), 35, yPos + 1)
      
      // File Path & Line
      doc.setTextColor(71, 85, 105)
      doc.setFontSize(7)
      const filePath = issue.file_path.split('/').slice(-2).join('/')
      doc.text(`${filePath} (L${issue.line_number})`, 12, yPos + 7)
      
      // Status Badge
      const statusText = issue.status === 'approved' ? 'ONAYLANDI' : 
                        issue.status === 'rejected' ? 'REDDEDILDI' : 'BEKLEMEDE'
      const statusColor = issue.status === 'approved' ? [34, 197, 94] : 
                         issue.status === 'rejected' ? [239, 68, 68] : [100, 116, 139]
      doc.setFillColor(statusColor[0], statusColor[1], statusColor[2])
      doc.roundedRect(175, yPos - 3, 23, 6, 1, 1, 'F')
      doc.setTextColor(255, 255, 255)
      doc.setFontSize(6)
      doc.text(statusText, 186.5, yPos + 1, { align: 'center' })
      
      // Reason (wrapped text) - Manual wrapping to avoid Turkish character issues
      doc.setTextColor(30, 41, 59)
      doc.setFontSize(8)
      doc.setFont('helvetica', 'normal')
      
      // Manual text wrapping function for better Turkish support
      const wrapText = (text: string, maxWidth: number) => {
        const words = text.split(' ')
        const lines: string[] = []
        let currentLine = ''
        
        words.forEach(word => {
          const testLine = currentLine ? `${currentLine} ${word}` : word
          const textWidth = doc.getTextWidth(testLine)
          
          if (textWidth > maxWidth && currentLine) {
            lines.push(currentLine)
            currentLine = word
          } else {
            currentLine = testLine
          }
        })
        
        if (currentLine) lines.push(currentLine)
        return lines
      }
      
      const reasonLines = wrapText(issue.reason, 175).slice(0, 3)
      reasonLines.forEach((line: string, idx: number) => {
        doc.text(line, 12, yPos + 13 + (idx * 4))
      })
      
      // Suggested Code (if exists and short)
      if (issue.code && issue.code.length < 100) {
        doc.setFillColor(241, 245, 249)
        doc.rect(12, yPos + 22, 176, 6, 'F')
        doc.setTextColor(71, 85, 105)
        doc.setFontSize(6)
        doc.setFont('courier', 'normal')
        doc.text(issue.code.substring(0, 80), 13, yPos + 26)
        doc.setFont('helvetica', 'normal')
      }
      
      yPos += 40
    })
    
    // Footer on last page
    const pageCount = doc.getNumberOfPages()
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i)
      doc.setFontSize(8)
      doc.setTextColor(156, 163, 175)
      doc.text(`Sayfa ${i} / ${pageCount}`, 105, 290, { align: 'center' })
      doc.text('AI Anabasis SEO Spider', 14, 290)
    }
    
    // Save PDF
    const filename = `seo-analiz-${job?.upload_filename?.replace('.zip', '') || 'rapor'}-${new Date().toISOString().split('T')[0]}.pdf`
    doc.save(filename)
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/projects')}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          
          <div>
            <h1 className="text-h1 text-text-primary">
              {job.name || job.upload_filename}
            </h1>
            <p className="mt-2 text-text-secondary">
              {t('scans.subtitle')}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Badge variant={
            job.status === 'completed' ? 'low' :
            job.status === 'failed' ? 'critical' :
            'default'
          }>
            {t(`status.${job.status}`)}
          </Badge>
          
          <div className="flex items-center gap-2">
            {issues.length > 0 && (
              <Button
                variant="ghost"
                size="md"
                onClick={exportToPDF}
                className="flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                PDF İndir
              </Button>
            )}
            
            {(job.total_chunks && job.total_chunks > 0) && 
             (job.analyzed_chunks || 0) < (job.total_chunks || 0) && (
              <Button
                variant="primary"
                size="md"
                onClick={() => startAnalysisMutation.mutate()}
                disabled={startAnalysisMutation.isPending || (job.status === 'analyzing' && (job.analyzed_chunks || 0) > 0)}
              >
                <Play className="h-4 w-4 mr-2" />
                {job.status === 'analyzing' && (job.analyzed_chunks || 0) > 0 ? t('scans.analyzing') : t('scans.startAnalysis')}
              </Button>
            )}
          </div>
        </div>
      </div>
      
      {/* Real-time Analysis Progress & Stats Combined */}
      {job.status === 'analyzing' ? (
        <div className="grid gap-4 md:grid-cols-2">
          {/* Progress Card */}
          <Card className="bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 border-accent-primary/30">
            <CardContent className="py-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-text-primary">
                  🔍 Analiz Devam Ediyor
                </h3>
                <span className="text-2xl font-bold text-accent-primary">
                  {Math.round(((job.analyzed_chunks || 0) / (job.total_chunks || 1)) * 100)}%
                </span>
              </div>
              
              <div className="w-full bg-bg-secondary rounded-full h-2 overflow-hidden mb-2">
                <motion.div
                  className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                  initial={{ width: 0 }}
                  animate={{ 
                    width: `${((job.analyzed_chunks || 0) / (job.total_chunks || 1)) * 100}%` 
                  }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              
              <p className="text-xs text-text-secondary">
                {job.analyzed_chunks || 0} / {job.total_chunks || 0} chunk analiz edildi
              </p>
            </CardContent>
          </Card>
          
          {/* Live Stats Card */}
          <Card>
            <CardContent className="py-4">
              <h3 className="text-sm font-semibold text-text-primary mb-3">
                📊 Canlı İstatistikler
              </h3>
              <div className="grid grid-cols-6 gap-3">
                <div className="text-center">
                  <p className="text-xl font-bold text-accent-primary">
                    {issues.length}
                  </p>
                  <p className="text-xs text-text-secondary">Toplam</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-severity-critical">
                    {criticalIssues.length}
                  </p>
                  <p className="text-xs text-text-secondary">Kritik</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-severity-high">
                    {highIssues.length}
                  </p>
                  <p className="text-xs text-text-secondary">Yüksek</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-severity-medium">
                    {mediumIssues.length}
                  </p>
                  <p className="text-xs text-text-secondary">Orta</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-severity-low">
                    {lowIssues.length}
                  </p>
                  <p className="text-xs text-text-secondary">Düşük</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-success">
                    {approvedIssues.length}
                  </p>
                  <p className="text-xs text-text-secondary">Onaylı</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Stats - Normal View */
        <div className="grid gap-4 md:grid-cols-7">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">Toplam Sorun</p>
              <p className="mt-2 text-3xl font-bold text-accent-primary">
                {issues.length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-accent-primary" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('severity.critical')}</p>
              <p className="mt-2 text-3xl font-bold text-severity-critical">
                {criticalIssues.length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-severity-critical" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('severity.high')}</p>
              <p className="mt-2 text-3xl font-bold text-severity-high">
                {highIssues.length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-severity-high" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('severity.medium')}</p>
              <p className="mt-2 text-3xl font-bold text-severity-medium">
                {mediumIssues.length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-severity-medium" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('severity.low')}</p>
              <p className="mt-2 text-3xl font-bold text-severity-low">
                {lowIssues.length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-severity-low" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('scans.approved')}</p>
              <p className="mt-2 text-3xl font-bold text-success">
                {approvedIssues.length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-success" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('common.files')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">
                {job.file_count || job.total_files || 0}
              </p>
            </div>
            <FileText className="h-8 w-8 text-accent-primary" />
          </div>
        </Card>
      </div>
      )}
      
      {/* Issues list */}
      <Card>
        <CardHeader>
          <CardTitle>{t('scans.issuesList')} ({issues.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {issues.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="h-12 w-12 text-success mx-auto mb-4" />
              <p className="text-text-secondary">{t('message.noIssues')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {issues.map((issue: Issue, index: number) => (
                <motion.div
                  key={issue.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className="rounded-lg border border-glass-border bg-background-tertiary hover:border-accent-primary/30 transition-all overflow-hidden"
                >
                  {/* Header - Fixed Height */}
                  <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-glass-border bg-background-secondary/50">
                    <div className="flex items-center gap-2 flex-wrap min-w-0 flex-1">
                      <Badge variant={
                        issue.severity === 'critical' ? 'critical' :
                        issue.severity === 'high' ? 'high' :
                        issue.severity === 'medium' ? 'medium' :
                        'low'
                      } className="flex-shrink-0">
                        {t(`severity.${issue.severity}`)}
                      </Badge>
                      
                      <Badge variant="default" className="text-xs flex-shrink-0">
                        {t(`issue.${issue.issue_type}`)}
                      </Badge>
                      
                      <span className="text-xs text-text-tertiary flex-shrink-0">
                        L{issue.line_number}
                      </span>
                      
                      <span className="text-xs text-text-tertiary flex-shrink-0">
                        {(issue.confidence * 100).toFixed(0)}%
                      </span>
                      
                      <div className="flex items-center gap-1 min-w-0 flex-1">
                        <FileText className="h-3 w-3 text-text-tertiary flex-shrink-0" />
                        <span className="text-xs text-text-secondary font-mono truncate">
                          .../{issue.file_path.split('/').slice(-2).join('/')}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex-shrink-0">
                      {issue.status === 'pending' ? (
                        <div className="flex gap-2">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => approveIssueMutation.mutate(issue.id)}
                            disabled={approveIssueMutation.isPending}
                            className="text-xs px-3 py-1 h-7"
                          >
                            <CheckCircle className="h-3 w-3" />
                          </Button>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => rejectIssueMutation.mutate(issue.id)}
                            disabled={rejectIssueMutation.isPending}
                            className="text-xs px-3 py-1 h-7"
                          >
                            <XCircle className="h-3 w-3" />
                          </Button>
                        </div>
                      ) : (
                        <Badge variant={
                          issue.status === 'approved' ? 'low' :
                          issue.status === 'applied' ? 'low' :
                          'critical'
                        } className="text-xs">
                          {t(`status.${issue.status}`)}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {/* Content - Full Display */}
                  <div className="px-4 py-3 space-y-3">
                    {/* Full Reason - No Truncation */}
                    <div className="text-sm text-text-primary leading-relaxed">
                      {issue.reason}
                    </div>
                    
                    {/* Code Block - Always Visible if Present */}
                    {issue.code && issue.code.trim().length > 0 && (
                      <div className="rounded border border-glass-border bg-background-primary overflow-hidden">
                        <div className="px-3 py-2 bg-background-secondary/50 border-b border-glass-border flex items-center justify-between">
                          <span className="text-xs font-medium text-text-primary">Önerilen Kod</span>
                          <span className="text-xs text-text-tertiary">{issue.code.length} karakter</span>
                        </div>
                        <div className="max-h-64 overflow-y-auto">
                          <pre className="p-3 text-xs">
                            <code className="text-text-primary font-mono leading-relaxed whitespace-pre-wrap break-words">
                              {issue.code}
                            </code>
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
