import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Download,
  Loader2,
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  FileText,
  Target,
  BarChart3
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { seoService } from '../services/seoService'
import type { SEOAnalysisDetail, AnalysisProgress } from '../types/seo'

export default function SEOAnalysisDetail() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const navigate = useNavigate()

  const [analysis, setAnalysis] = useState<SEOAnalysisDetail | null>(null)
  const [progress, setProgress] = useState<AnalysisProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!analysisId) return

    const loadAnalysis = async () => {
      try {
        // Start polling
        const result = await seoService.pollUntilComplete(
          analysisId,
          (prog) => {
            setProgress(prog)
            setLoading(prog.status !== 'completed' && prog.status !== 'failed')
          }
        )
        
        setAnalysis(result)
        setLoading(false)
      } catch (err: any) {
        console.error('Analysis error:', err)
        setError(err.message || 'Analiz yüklenemedi')
        setLoading(false)
      }
    }

    loadAnalysis()
  }, [analysisId])

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Mükemmel'
    if (score >= 60) return 'İyi'
    if (score >= 40) return 'Orta'
    return 'Zayıf'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-gray-100 text-gray-800 border-gray-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'Kritik'
      case 'high':
        return 'Yüksek'
      case 'medium':
        return 'Orta'
      case 'low':
        return 'Düşük'
      default:
        return severity
    }
  }

  const getIssueTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      schema_missing: 'Schema Eksik',
      title_issue: 'Title Sorunu',
      meta_issue: 'Meta Description Sorunu',
      heading_issue: 'Heading Sorunu',
      broken_link: 'Kırık Link',
      nofollow_issue: 'Nofollow Sorunu',
      anchor_spam: 'Anchor Spam',
      semantic_density_low: 'Düşük Keyword Yoğunluğu',
      wordcount_low: 'Düşük Kelime Sayısı',
      image_alt_missing: 'Eksik ALT Etiketi',
      robots_issue: 'Robots.txt Sorunu',
      sitemap_issue: 'Sitemap Sorunu',
      snippet_issue: 'Snippet Sorunu',
      technical_error: 'Teknik Hata'
    }
    return labels[type] || type
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
        <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-semibold text-gray-900">
            {progress?.message || 'Analiz yapılıyor...'}
          </h2>
          <p className="text-gray-600">{progress?.current_step}</p>
          {progress && (
            <div className="w-64 h-2 bg-gray-200 rounded-full overflow-hidden mt-4">
              <div
                className="h-full bg-blue-600 transition-all duration-500"
                style={{ width: `${progress.progress_percentage}%` }}
              />
            </div>
          )}
          <p className="text-sm text-gray-500 mt-2">
            {progress?.progress_percentage || 0}% tamamlandı
          </p>
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <AlertCircle className="w-16 h-16 text-red-600" />
        <h2 className="text-2xl font-semibold text-gray-900">Analiz Yüklenemedi</h2>
        <p className="text-gray-600">{error || 'Bilinmeyen bir hata oluştu'}</p>
        <Button onClick={() => navigate('/seo-spider')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Geri Dön
        </Button>
      </div>
    )
  }

  const issuesBySeverity = {
    critical: analysis.issues.filter(i => i.severity === 'critical'),
    high: analysis.issues.filter(i => i.severity === 'high'),
    medium: analysis.issues.filter(i => i.severity === 'medium'),
    low: analysis.issues.filter(i => i.severity === 'low')
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="secondary"
              onClick={() => navigate('/seo-spider')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Geri
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SEO Analiz Raporu</h1>
              <p className="text-base text-gray-600 mt-2 font-medium">{analysis.url}</p>
            </div>
          </div>
          <div className="flex gap-2">
            {analysis.pdf_report_path && (
              <Button variant="primary">
                <Download className="w-4 h-4 mr-2" />
                PDF İndir
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-8 text-white">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold">Genel Skor</h3>
            <BarChart3 className="w-8 h-8 opacity-80" />
          </div>
          <div className="text-6xl font-black mb-2">
            {Math.round(analysis.overall_score)}
          </div>
          <p className="text-blue-100 text-base font-semibold">{getScoreLabel(analysis.overall_score)}</p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-8 text-white">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold">Teknik SEO</h3>
            <FileText className="w-8 h-8 opacity-80" />
          </div>
          <div className="text-6xl font-black mb-2">
            {Math.round(analysis.technical_score)}
          </div>
          <p className="text-purple-100 text-base font-semibold">{getScoreLabel(analysis.technical_score)}</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-8 text-white">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold">İçerik Kalitesi</h3>
            <TrendingUp className="w-8 h-8 opacity-80" />
          </div>
          <div className="text-6xl font-black mb-2">
            {Math.round(analysis.content_score)}
          </div>
          <p className="text-green-100 text-base font-semibold">{getScoreLabel(analysis.content_score)}</p>
        </div>
      </div>

      {/* Issue Summary */}
      <Card className="p-8 bg-white shadow-sm">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
          <AlertCircle className="w-7 h-7 text-blue-600" />
          Sorun Özeti
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="p-6 bg-red-50 border-l-4 border-red-600 rounded-lg hover:shadow-md transition-shadow">
            <div className="text-5xl font-black text-red-600 mb-2">{analysis.critical_issues}</div>
            <div className="text-base font-bold text-red-800">Kritik</div>
          </div>
          <div className="p-6 bg-orange-50 border-l-4 border-orange-600 rounded-lg hover:shadow-md transition-shadow">
            <div className="text-5xl font-black text-orange-600 mb-2">{analysis.high_issues}</div>
            <div className="text-base font-bold text-orange-800">Yüksek</div>
          </div>
          <div className="p-6 bg-yellow-50 border-l-4 border-yellow-600 rounded-lg hover:shadow-md transition-shadow">
            <div className="text-5xl font-black text-yellow-600 mb-2">{analysis.medium_issues}</div>
            <div className="text-base font-bold text-yellow-800">Orta</div>
          </div>
          <div className="p-6 bg-gray-100 border-l-4 border-gray-600 rounded-lg hover:shadow-md transition-shadow">
            <div className="text-5xl font-black text-gray-700 mb-2">{analysis.low_issues}</div>
            <div className="text-base font-bold text-gray-800">Düşük</div>
          </div>
        </div>
      </Card>

      {/* Keyword Scores */}
      {Object.keys(analysis.keyword_scores).length > 0 && (
        <Card className="p-8 bg-white shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-7 h-7 text-blue-600" />
            Anahtar Kelime Performansı
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(analysis.keyword_scores).map(([keyword, score]) => (
              <div key={keyword} className="p-6 bg-gradient-to-br from-white to-gray-50 rounded-xl border-2 border-gray-200 shadow-sm hover:shadow-lg transition-all">
                <h3 className="font-black text-xl text-gray-900 mb-5 flex items-center gap-2">
                  <span className="text-2xl">🎯</span> {keyword}
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-bold text-gray-700">Varlık Skoru</span>
                      <span className="font-black text-xl text-blue-600">
                        {Math.round(score.presence_score)}
                      </span>
                    </div>
                    <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 shadow-sm"
                        style={{ width: `${score.presence_score}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-bold text-gray-700">Öne Çıkma</span>
                      <span className="font-black text-xl text-purple-600">
                        {Math.round(score.prominence)}
                      </span>
                    </div>
                    <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-500 shadow-sm"
                        style={{ width: `${score.prominence}%` }}
                      />
                    </div>
                  </div>
                  <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-l-4 border-blue-600">
                    <p className="text-sm text-gray-900 font-semibold leading-relaxed">
                      💡 {score.recommendation}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Detected Data */}
      {analysis.detected_data && (
        <Card className="p-8 bg-white shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <span className="text-3xl">🔎</span>
            Tespit Edilen SEO Elementleri
          </h2>
          <div className="bg-gray-50 rounded-xl p-6 space-y-6">
            
            {analysis.detected_data.h1_texts && analysis.detected_data.h1_texts.length > 0 && (
              <div>
                <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">📌</span>
                  Sitenizdeki H1 Etiketleri ({analysis.detected_data.h1_texts.length} adet):
                </h4>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  {analysis.detected_data.h1_texts.map((h1, idx) => (
                    <li key={idx} className="text-gray-700 font-medium">
                      "{h1}"
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div>
              <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">📄</span>
                Sitenizin Title Etiketi:
              </h4>
              <div className="bg-white p-4 rounded-lg border-l-4 border-blue-600 shadow-sm">
                <p className="text-gray-900 font-semibold">
                  {analysis.detected_data.title || 'Bulunamadı'}
                </p>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">📝</span>
                Sitenizin Meta Description:
              </h4>
              <div className="bg-white p-4 rounded-lg border-l-4 border-green-600 shadow-sm">
                <p className="text-gray-700">
                  {analysis.detected_data.meta_description || 'Bulunamadı'}
                </p>
              </div>
            </div>
            
            {analysis.detected_data.schemas && (
              <div>
                <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">🏷️</span>
                  Sitenizde Tespit Edilen Schema Türleri:
                </h4>
                {analysis.detected_data.schemas.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {analysis.detected_data.schemas.map((schema, idx) => (
                      <span
                        key={idx}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold text-sm shadow-sm"
                      >
                        {schema}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-red-600 italic">Hiç schema bulunamadı</p>
                )}
              </div>
            )}
            
            {analysis.detected_data.anchor_texts && analysis.detected_data.anchor_texts.length > 0 && (
              <div>
                <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">🔗</span>
                  Sitenizdeki İç Link Anchor Text'leri (İlk 15):
                </h4>
                <div className="bg-white p-4 rounded-lg max-h-64 overflow-y-auto shadow-sm">
                  <ul className="list-disc list-inside space-y-2 columns-2 gap-4">
                    {analysis.detected_data.anchor_texts.slice(0, 15).map((anchor, idx) => (
                      <li key={idx} className="text-gray-700 break-inside-avoid">
                        "{anchor.text}" →{' '}
                        <span className="text-gray-500 text-xs">
                          {anchor.href.length > 50 ? anchor.href.substring(0, 50) + '...' : anchor.href}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
            
            {analysis.detected_data.external_links && analysis.detected_data.external_links.length > 0 && (
              <div>
                <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">🌐</span>
                  Sitenizdeki Dış Linkler (Backlinks - İlk 10):
                </h4>
                <div className="bg-white p-4 rounded-lg max-h-64 overflow-y-auto shadow-sm">
                  <ul className="list-disc list-inside space-y-2">
                    {analysis.detected_data.external_links.slice(0, 10).map((link, idx) => (
                      <li key={idx} className="text-gray-700">
                        <a
                          href={link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 underline"
                        >
                          {link}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
            
          </div>
        </Card>
      )}

      {/* Metrics */}
      {analysis.metrics && (
        <Card className="p-8 bg-white shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Teknik Metrikler</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="p-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-md text-white">
              <div className="text-sm font-bold opacity-90 mb-2">Kelime Sayısı</div>
              <div className="text-4xl font-black">
                {analysis.metrics.word_count}
              </div>
            </div>
            <div className="p-6 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-md text-white">
              <div className="text-sm font-bold opacity-90 mb-2">H1 Sayısı</div>
              <div className="text-4xl font-black">
                {analysis.metrics.h1_count}
              </div>
            </div>
            <div className="p-6 bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-md text-white">
              <div className="text-sm font-bold opacity-90 mb-2">İç Link</div>
              <div className="text-4xl font-black">
                {analysis.metrics.internal_links_count}
              </div>
            </div>
            <div className="p-6 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-md text-white">
              <div className="text-sm font-bold opacity-90 mb-2">Toplam Görsel</div>
              <div className="text-4xl font-black">
                {analysis.metrics.total_images}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Issues */}
      <Card className="p-8 bg-white shadow-sm">
        <h2 className="text-2xl font-bold text-gray-900 mb-8">
          🔍 Detaylı Sorunlar ve Öneriler
        </h2>

        {(['critical', 'high', 'medium', 'low'] as const).map((severity) => {
          const issues = issuesBySeverity[severity]
          if (issues.length === 0) return null

          return (
            <div key={severity} className="mb-10 last:mb-0">
              <h3 className="text-xl font-black text-gray-900 mb-5 capitalize">
                {getSeverityLabel(severity)} Öncelikli Sorunlar ({issues.length})
              </h3>
              <div className="space-y-5">
                {issues.map((issue) => (
                  <div
                    key={issue.id}
                    className="p-6 bg-gradient-to-br from-white to-gray-50 border-2 border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all"
                  >
                    <div className="flex items-start gap-3 mb-4">
                      <Badge className={`${getSeverityColor(issue.severity)} font-bold px-3 py-1`}>
                        {getSeverityLabel(issue.severity)}
                      </Badge>
                      <span className="text-sm text-gray-700 font-bold uppercase bg-gray-100 px-3 py-1 rounded">
                        {getIssueTypeLabel(issue.issue_type)}
                      </span>
                      <span className="text-sm text-gray-600 ml-auto font-semibold">
                        Güven: {Math.round(issue.confidence * 100)}%
                      </span>
                    </div>
                    <p className="text-lg font-bold text-gray-900 mb-4 leading-relaxed">
                      {issue.reason}
                    </p>
                    <div className="p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-l-4 border-blue-600 mb-4">
                      <p className="text-base text-gray-900 font-semibold leading-relaxed">
                        <strong className="text-blue-700">💡 Öneri:</strong>{' '}
                        {issue.recommendation}
                      </p>
                    </div>
                    {issue.example_fix && (
                      <div className="p-5 bg-gray-900 rounded-xl text-sm text-green-400 font-mono overflow-x-auto border-2 border-gray-700 shadow-inner">
                        <div className="text-xs text-gray-400 mb-3 font-bold">📝 Örnek Düzeltme:</div>
                        <div className="text-green-300">{issue.example_fix}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )
        })}

        {analysis.total_issues === 0 && (
          <div className="text-center py-12">
            <CheckCircle2 className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Harika! Hiç sorun bulunamadı
            </h3>
            <p className="text-gray-600">
              Sayfanız SEO açısından mükemmel durumda görünüyor.
            </p>
          </div>
        )}
      </Card>
    </div>
  )
}

