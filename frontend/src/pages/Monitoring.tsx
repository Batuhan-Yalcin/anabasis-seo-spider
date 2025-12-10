import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Activity, Zap, AlertTriangle, Database } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { useTranslation } from '@/lib/i18n'
import { api } from '@/lib/api'

interface MonitoringData {
  rate_limiter: {
    max_concurrent: number
    active_requests: number
    queue_size: number
    total_requests: number
    average_wait_time_seconds: number
    utilization_percent: number
  }
  circuit_breakers: Array<{
    job_id: string
    failures: number
    threshold: number
    tripped: boolean
    remaining_attempts: number
  }>
  memory_limits: {
    max_extracted_size_mb: number
    current_jobs: Array<{
      job_id: string
      extracted_size_mb: number
      percentage_of_limit: number
    }>
  }
}

export function Monitoring() {
  const { t } = useTranslation()
  
  // Fetch monitoring data
  const { data, isLoading } = useQuery({
    queryKey: ['monitoring'],
    queryFn: async () => {
      const { data } = await api.get<MonitoringData>('/monitoring/health')
      return data
    },
    refetchInterval: 3000, // Refresh every 3 seconds
  })
  
  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-text-secondary">{t('common.loading')}</p>
      </div>
    )
  }
  
  const rateLimiter = data.rate_limiter
  const circuitBreakers = data.circuit_breakers
  const memoryLimits = data.memory_limits
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-h1 text-text-primary">{t('nav.monitoring')}</h1>
        <p className="mt-2 text-text-secondary">
          {t('monitoring.subtitle')}
        </p>
      </div>
      
      {/* Rate Limiter Stats */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Zap className="h-5 w-5 mr-2 text-accent-primary" />
              {t('monitoring.rateLimiter')}
            </CardTitle>
            <Badge variant={
              rateLimiter.utilization_percent > 80 ? 'high' :
              rateLimiter.utilization_percent > 50 ? 'medium' :
              'low'
            }>
              {rateLimiter.utilization_percent.toFixed(0)}% {t('monitoring.utilization')}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-3">
            <div>
              <p className="text-sm text-text-secondary">{t('monitoring.activeRequests')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">
                {rateLimiter.active_requests} / {rateLimiter.max_concurrent}
              </p>
            </div>
            
            <div>
              <p className="text-sm text-text-secondary">{t('monitoring.queueSize')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">
                {rateLimiter.queue_size}
              </p>
            </div>
            
            <div>
              <p className="text-sm text-text-secondary">{t('monitoring.avgWaitTime')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">
                {rateLimiter.average_wait_time_seconds.toFixed(2)}s
              </p>
            </div>
          </div>
          
          <div className="mt-4">
            <p className="text-sm text-text-tertiary">
              {t('monitoring.totalRequests')}: {rateLimiter.total_requests}
            </p>
          </div>
        </CardContent>
      </Card>
      
      {/* Circuit Breakers */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-severity-high" />
            {t('monitoring.circuitBreakers')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {circuitBreakers.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-success mx-auto mb-4" />
              <p className="text-text-secondary">{t('monitoring.allHealthy')}</p>
            </div>
          ) : (
            <div className="space-y-4">
              {circuitBreakers.map((cb, index) => (
                <motion.div
                  key={cb.job_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="rounded-lg border border-glass-border bg-background-tertiary p-4"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-text-primary">
                        Job: {cb.job_id.substring(0, 8)}...
                      </p>
                      <p className="text-sm text-text-tertiary mt-1">
                        {t('monitoring.failures')}: {cb.failures} / {cb.threshold}
                      </p>
                      <p className="text-sm text-text-tertiary">
                        {t('monitoring.remainingAttempts')}: {cb.remaining_attempts}
                      </p>
                    </div>
                    
                    <Badge variant={cb.tripped ? 'critical' : 'medium'}>
                      {cb.tripped ? t('monitoring.tripped') : t('monitoring.active')}
                    </Badge>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Memory Limits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="h-5 w-5 mr-2 text-accent-secondary" />
            {t('monitoring.memoryLimits')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <p className="text-sm text-text-secondary">
              {t('monitoring.maxExtractedSize')}: {memoryLimits.max_extracted_size_mb} MB
            </p>
          </div>
          
          {memoryLimits.current_jobs.length === 0 ? (
            <div className="text-center py-8">
              <Database className="h-12 w-12 text-text-tertiary mx-auto mb-4" />
              <p className="text-text-secondary">{t('monitoring.noActiveJobs')}</p>
            </div>
          ) : (
            <div className="space-y-4">
              {memoryLimits.current_jobs.map((job, index) => (
                <motion.div
                  key={job.job_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="rounded-lg border border-glass-border bg-background-tertiary p-4"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-text-primary">
                      Job: {job.job_id.substring(0, 8)}...
                    </p>
                    <Badge variant={
                      job.percentage_of_limit > 80 ? 'critical' :
                      job.percentage_of_limit > 50 ? 'high' :
                      'low'
                    }>
                      {job.percentage_of_limit.toFixed(0)}%
                    </Badge>
                  </div>
                  
                  <div className="relative h-2 overflow-hidden rounded-full bg-background-primary">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${job.percentage_of_limit}%` }}
                      transition={{ duration: 0.5 }}
                      className={`h-full ${
                        job.percentage_of_limit > 80
                          ? 'bg-severity-critical'
                          : job.percentage_of_limit > 50
                          ? 'bg-severity-high'
                          : 'bg-gradient-to-r from-accent-primary to-accent-secondary'
                      }`}
                    />
                  </div>
                  
                  <p className="mt-2 text-xs text-text-tertiary">
                    {job.extracted_size_mb.toFixed(2)} MB / {memoryLimits.max_extracted_size_mb} MB
                  </p>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
