import { motion } from 'framer-motion'
import { Activity, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { useTranslation } from '@/lib/i18n'
import { useQuery } from '@tanstack/react-query'
import { jobService } from '@/services/jobService'
import { Job } from '@/types'

export function Dashboard() {
  const { t } = useTranslation()
  
  // Fetch all jobs from API
  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobService.getAllJobs(),
    refetchInterval: 5000, // Refresh every 5 seconds
  })
  
  // Calculate stats from real data
  const activeScans = jobs.filter(j => 
    ['uploading', 'chunking', 'analyzing'].includes(j.status)
  ).length
  
  const totalFiles = jobs.reduce((sum, job) => sum + (job.file_count || 0), 0)
  
  const issuesFound = jobs.reduce((sum, job) => 
    sum + (job.total_issues || 0), 0
  )
  
  const issuesFixed = jobs.reduce((sum, job) => 
    sum + (job.resolved_issues || 0), 0
  )
  
  const statsConfig = [
    {
      key: 'dashboard.activeScans',
      value: activeScans.toString(),
      icon: Activity,
      color: 'text-accent-primary',
      bgColor: 'bg-accent-primary/10',
    },
    {
      key: 'dashboard.totalFiles',
      value: totalFiles.toString(),
      icon: FileText,
      color: 'text-accent-secondary',
      bgColor: 'bg-accent-secondary/10',
    },
    {
      key: 'dashboard.issuesFound',
      value: issuesFound.toString(),
      icon: AlertCircle,
      color: 'text-severity-high',
      bgColor: 'bg-severity-high/10',
    },
    {
      key: 'dashboard.issuesFixed',
      value: issuesFixed.toString(),
      icon: CheckCircle,
      color: 'text-success',
      bgColor: 'bg-success/10',
    },
  ] as const
  
  // Get recent scans (last 5 jobs)
  const recentScans = jobs
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
    .map(job => ({
      id: job.id,
      project: job.name || `Job ${job.id}`,
      file: `${job.file_count || 0} ${t('common.files')}`,
      status: job.status,
      progress: calculateProgress(job),
    }))
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-text-secondary">{t('common.loading')}</p>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-h1 text-text-primary">{t('dashboard.title')}</h1>
        <p className="mt-2 text-text-secondary">
          {t('dashboard.subtitle')}
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {statsConfig.map((stat, index) => (
          <motion.div
            key={stat.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-secondary">{t(stat.key as any)}</p>
                  <p className="mt-2 text-3xl font-bold text-text-primary">
                    {stat.value}
                  </p>
                </div>
                <div className={`rounded-lg p-3 ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Recent scans */}
      <Card>
        <CardHeader>
          <CardTitle>{t('dashboard.recentScans')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentScans.map((scan) => (
              <div
                key={scan.id}
                className="rounded-lg border border-glass-border bg-background-tertiary p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="font-medium text-text-primary">
                      {scan.project} - {scan.file}
                    </p>
                  </div>
                  <Badge
                    variant={
                      scan.status === 'analyzing'
                        ? 'default'
                        : scan.status === 'completed'
                        ? 'low'
                        : 'default'
                    }
                  >
                    {t(`status.${scan.status}` as any)}
                  </Badge>
                </div>
                <div className="relative h-2 overflow-hidden rounded-full bg-background-primary">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${scan.progress}%` }}
                    transition={{ duration: 1 }}
                    className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                  />
                </div>
                <p className="mt-1 text-xs text-text-tertiary">{scan.progress}%</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Live activity feed */}
      <Card>
        <CardHeader>
          <CardTitle>{t('dashboard.liveActivity')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentScans.length === 0 ? (
              <p className="text-sm text-text-tertiary text-center py-8">
                {t('dashboard.noActivity')}
              </p>
            ) : (
              recentScans.map((scan, index) => (
                <motion.div
                  key={scan.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-3"
                >
                  <div
                    className={`mt-0.5 h-2 w-2 rounded-full ${
                      scan.status === 'completed'
                        ? 'bg-success'
                        : scan.status === 'failed'
                        ? 'bg-severity-high'
                        : 'bg-accent-primary'
                    }`}
                  />
                  <div className="flex-1">
                    <p className="text-sm text-text-primary">
                      {scan.project} - {t(`status.${scan.status}`)}
                    </p>
                    <p className="text-xs text-text-tertiary">
                      {formatRelativeTime(new Date())}
                    </p>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Helper functions
function calculateProgress(job: Job): number {
  if (job.status === 'completed') return 100
  if (job.status === 'failed') return 0
  if (job.status === 'pending') return 0
  
  // For analyzing/chunking, estimate based on chunks
  const totalChunks = job.chunk_count || 0
  const analyzedChunks = job.analyzed_chunks || 0
  
  if (totalChunks === 0) return 10
  return Math.round((analyzedChunks / totalChunks) * 100)
}

function formatRelativeTime(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)
  
  if (diffSec < 60) return `${diffSec}s önce`
  if (diffMin < 60) return `${diffMin}m önce`
  if (diffHour < 24) return `${diffHour}h önce`
  return `${diffDay}d önce`
}

