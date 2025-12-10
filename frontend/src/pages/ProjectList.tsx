import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, Clock, CheckCircle, AlertCircle, Upload, Trash2 } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { useTranslation } from '@/lib/i18n'
import { jobService } from '@/services/jobService'
import { useNavigate } from 'react-router-dom'

export function ProjectList() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  // Fetch all jobs
  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobService.getAllJobs(),
    refetchInterval: 5000,
  })
  
  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (data: { file: File; keywords: string; siteUrl: string; language: string }) => {
      const formData = new FormData()
      formData.append('file', data.file)
      formData.append('keywords', data.keywords)
      formData.append('site_url', data.siteUrl)
      formData.append('site_language', data.language)
      
      // 1. Create job (upload file)
      const job = await jobService.createJob(formData)
      
      // 2. Extract archive
      await jobService.extractJob(job.id)
      
      // 3. Chunk files
      await jobService.chunkJob(job.id)
      
      return job
    },
    onSuccess: (job) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      navigate(`/scans/${job.id}`)
    },
  })
  
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // For now, use default values - later we'll add a modal
      uploadMutation.mutate({
        file,
        keywords: 'SEO, optimization',
        siteUrl: 'https://example.com',
        language: 'tr',
      })
    }
  }
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-severity-high" />
      case 'analyzing':
      case 'chunking':
        return <Clock className="h-5 w-5 text-accent-primary animate-pulse" />
      default:
        return <FileText className="h-5 w-5 text-text-tertiary" />
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-text-secondary">{t('common.loading')}</p>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-h1 text-text-primary">{t('nav.projects')}</h1>
          <p className="mt-2 text-text-secondary">
            {t('projects.subtitle')}
          </p>
        </div>
        
        {/* Upload button */}
        <div>
          <input
            ref={(el) => {
              if (el) {
                (window as any).fileInputRef = el
              }
            }}
            type="file"
            accept=".zip,.tar,.tar.gz"
            className="hidden"
            onChange={handleFileUpload}
            disabled={uploadMutation.isPending}
          />
          <Button
            variant="primary"
            size="md"
            onClick={() => {
              const input = (window as any).fileInputRef as HTMLInputElement
              if (input) input.click()
            }}
            disabled={uploadMutation.isPending}
          >
            <Upload className="h-4 w-4 mr-2" />
            {uploadMutation.isPending ? t('common.loading') : t('action.upload')}
          </Button>
        </div>
      </div>
      
      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('projects.totalProjects')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">{jobs.length}</p>
            </div>
            <FileText className="h-8 w-8 text-accent-primary" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('projects.activeScans')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">
                {jobs.filter(j => ['analyzing', 'chunking', 'uploading'].includes(j.status)).length}
              </p>
            </div>
            <Clock className="h-8 w-8 text-accent-secondary" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('projects.completedScans')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">
                {jobs.filter(j => j.status === 'completed').length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-success" />
          </div>
        </Card>
      </div>
      
      {/* Project list */}
      <div className="space-y-4">
        {jobs.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-text-tertiary mx-auto mb-4" />
              <p className="text-text-secondary">{t('projects.noProjects')}</p>
              <p className="text-sm text-text-tertiary mt-2">{t('projects.uploadFirst')}</p>
            </div>
          </Card>
        ) : (
          jobs.map((job, index) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card
                className="cursor-pointer hover:border-accent-primary/50 transition-colors"
                onClick={() => navigate(`/scans/${job.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    {getStatusIcon(job.status)}
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-semibold text-text-primary">
                          {job.name || job.upload_filename}
                        </h3>
                        <Badge variant={
                          job.status === 'completed' ? 'low' :
                          job.status === 'failed' ? 'critical' :
                          'default'
                        }>
                          {t(`status.${job.status}`)}
                        </Badge>
                      </div>
                      
                      <div className="mt-2 flex items-center space-x-6 text-sm text-text-tertiary">
                        <span>
                          {t('common.files')}: {job.file_count || job.total_files || 0}
                        </span>
                        <span>
                          {t('dashboard.issuesFound')}: {job.total_issues || 0}
                        </span>
                        <span>
                          {t('common.created')}: {new Date(job.created_at).toLocaleDateString('tr-TR')}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      // TODO: Implement delete
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-severity-high" />
                  </Button>
                </div>
              </Card>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}
