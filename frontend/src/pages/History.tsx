import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { History as HistoryIcon, RotateCcw, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { useTranslation } from '@/lib/i18n'
import { api } from '@/lib/api'

interface PatchHistory {
  id: number
  job_id: string
  issue_id: number
  file_path: string
  line_number: number
  action: string
  original_content: string
  patched_content: string
  success: boolean
  error_message?: string
  applied_at: string
  rolled_back: boolean
}

export function History() {
  const { t } = useTranslation()
  
  // Fetch patch history
  const { data: history = [], isLoading } = useQuery({
    queryKey: ['patch-history'],
    queryFn: async () => {
      const { data } = await api.get<PatchHistory[]>('/patches/history')
      return data
    },
    refetchInterval: 10000,
  })
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-text-secondary">{t('common.loading')}</p>
      </div>
    )
  }
  
  const successfulPatches = history.filter(h => h.success && !h.rolled_back)
  const failedPatches = history.filter(h => !h.success)
  const rolledBackPatches = history.filter(h => h.rolled_back)
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-h1 text-text-primary">{t('nav.history')}</h1>
        <p className="mt-2 text-text-secondary">
          {t('history.subtitle')}
        </p>
      </div>
      
      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('history.successfulPatches')}</p>
              <p className="mt-2 text-3xl font-bold text-success">
                {successfulPatches.length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-success" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('history.failedPatches')}</p>
              <p className="mt-2 text-3xl font-bold text-severity-high">
                {failedPatches.length}
              </p>
            </div>
            <XCircle className="h-8 w-8 text-severity-high" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-secondary">{t('history.rolledBack')}</p>
              <p className="mt-2 text-3xl font-bold text-text-primary">
                {rolledBackPatches.length}
              </p>
            </div>
            <RotateCcw className="h-8 w-8 text-accent-primary" />
          </div>
        </Card>
      </div>
      
      {/* History list */}
      <Card>
        <CardHeader>
          <CardTitle>{t('history.patchHistory')} ({history.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <div className="text-center py-12">
              <HistoryIcon className="h-12 w-12 text-text-tertiary mx-auto mb-4" />
              <p className="text-text-secondary">{t('history.noHistory')}</p>
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((patch, index) => (
                <motion.div
                  key={patch.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className="rounded-lg border border-glass-border bg-background-tertiary p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <Badge variant={
                          patch.success && !patch.rolled_back ? 'low' :
                          patch.rolled_back ? 'medium' :
                          'critical'
                        }>
                          {patch.rolled_back ? t('history.rolledBack') :
                           patch.success ? t('common.success') :
                           t('common.error')}
                        </Badge>
                        
                        <span className="text-sm text-text-tertiary">
                          {t('common.line')} {patch.line_number}
                        </span>
                        
                        <span className="text-sm text-text-tertiary">
                          {new Date(patch.applied_at).toLocaleString('tr-TR')}
                        </span>
                      </div>
                      
                      <p className="text-sm text-text-secondary mb-2">
                        {patch.file_path}
                      </p>
                      
                      <p className="text-sm text-text-primary mb-3">
                        {t('common.action')}: {patch.action}
                      </p>
                      
                      {patch.error_message && (
                        <div className="bg-severity-critical/10 border border-severity-critical/30 rounded p-3 mb-3">
                          <p className="text-sm text-severity-critical">
                            {patch.error_message}
                          </p>
                        </div>
                      )}
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-text-tertiary mb-2">{t('history.original')}</p>
                          <pre className="bg-background-primary rounded p-3 text-xs overflow-x-auto max-h-32">
                            <code>{patch.original_content}</code>
                          </pre>
                        </div>
                        
                        <div>
                          <p className="text-xs text-text-tertiary mb-2">{t('history.patched')}</p>
                          <pre className="bg-background-primary rounded p-3 text-xs overflow-x-auto max-h-32">
                            <code>{patch.patched_content}</code>
                          </pre>
                        </div>
                      </div>
                    </div>
                    
                    {patch.success && !patch.rolled_back && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          // TODO: Implement rollback
                        }}
                        className="ml-4"
                      >
                        <RotateCcw className="h-4 w-4 mr-1" />
                        {t('action.rollback')}
                      </Button>
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
