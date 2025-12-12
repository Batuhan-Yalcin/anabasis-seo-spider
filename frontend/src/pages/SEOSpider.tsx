import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, TrendingUp, AlertCircle, Loader2 } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { seoService } from '../services/seoService'
import type { SEOAnalysis } from '../types/seo'

export default function SEOSpider() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [keywords, setKeywords] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    // Validation
    if (!url.trim()) {
      setError('Lütfen bir URL girin')
      return
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setError('URL http:// veya https:// ile başlamalıdır')
      return
    }

    const keywordList = keywords
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0)

    if (keywordList.length === 0) {
      setError('En az bir anahtar kelime girin')
      return
    }

    setError(null)
    setIsAnalyzing(true)

    try {
      const analysis = await seoService.startAnalysis({
        url: url.trim(),
        keywords: keywordList
      })

      // Navigate to analysis detail page
      navigate(`/seo-spider/${analysis.id}`)
    } catch (err: any) {
      console.error('Analysis error:', err)
      setError(err.response?.data?.detail || 'Analiz başlatılamadı')
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
            AI Anabasis SEO Spider
          </h1>
          <p className="text-gray-600 mt-2">
            Profesyonel tek sayfa SEO analizi - Gemini AI destekli
          </p>
        </div>
      </div>

      {/* Main Analysis Form */}
      <Card className="p-8">
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              Yeni SEO Analizi Başlat
            </h2>
            <p className="text-base text-gray-700 leading-relaxed font-medium">
              Analiz edilecek sayfanın URL'sini ve hedef anahtar kelimeleri girin.
              Sistem sayfayı tarayacak, teknik SEO sorunlarını tespit edecek ve
              anahtar kelimeleriniz için optimizasyon önerileri sunacak.
            </p>
          </div>

          {/* URL Input */}
          <div>
            <label className="block text-sm font-bold text-gray-900 mb-2">
              Analiz Edilecek URL *
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/sayfa"
              className="w-full px-4 py-3 text-base text-gray-900 bg-white border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all placeholder:text-gray-400"
              disabled={isAnalyzing}
            />
            <p className="text-sm text-gray-600 mt-2 font-medium">
              💡 Tam URL girin (http:// veya https:// ile başlamalı)
            </p>
          </div>

          {/* Keywords Input */}
          <div>
            <label className="block text-sm font-bold text-gray-900 mb-2">
              Anahtar Kelimeler *
            </label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="seo analizi, arama motoru optimizasyonu, seo araçları"
              className="w-full px-4 py-3 text-base text-gray-900 bg-white border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all placeholder:text-gray-400"
              disabled={isAnalyzing}
            />
            <p className="text-sm text-gray-600 mt-2 font-medium">
              💡 Virgülle ayırarak birden fazla anahtar kelime girebilirsiniz
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-900">Hata</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full py-4 text-base font-semibold"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                Analiz Başlatılıyor...
              </>
            ) : (
              <>
                <Search className="w-5 h-5 mr-2" />
                SEO Analizi Başlat
              </>
            )}
          </Button>
        </div>
      </Card>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 border-l-4 border-blue-500 bg-blue-50">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <Search className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1 text-base">
                Playwright Crawler
              </h3>
              <p className="text-sm text-gray-700 font-medium">
                JavaScript render desteği ile tam sayfa tarama
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6 border-l-4 border-purple-500 bg-purple-50">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1 text-base">
                Gemini AI Analiz
              </h3>
              <p className="text-sm text-gray-700 font-medium">
                Yapay zeka destekli derin SEO analizi
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6 border-l-4 border-green-500 bg-green-50">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1 text-base">
                Detaylı Rapor
              </h3>
              <p className="text-sm text-gray-700 font-medium">
                HTML ve PDF formatında indirilebilir raporlar
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Features List */}
      <Card className="p-6 bg-gradient-to-br from-gray-50 to-blue-50">
        <h3 className="text-xl font-bold text-gray-900 mb-6">
          📋 Analiz Edilen SEO Faktörleri
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            'Schema.org yapılandırılmış veri analizi',
            'Title ve Meta description optimizasyonu',
            'Heading yapısı (H1-H2-H3) kontrolü',
            'İç ve dış link analizi',
            'Görsel ALT etiket kontrolü',
            'Anahtar kelime yoğunluğu analizi',
            'Kelime sayısı ve içerik kalitesi',
            'Google snippet uyumluluğu',
            'Robots.txt ve sitemap kontrolü',
            'Teknik SEO hata tespiti',
            'Anahtar kelime öne çıkma skoru',
            'Mobil uyumluluk ve performans'
          ].map((feature, index) => (
            <div key={index} className="flex items-center gap-3 p-2 bg-white rounded-lg">
              <div className="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0" />
              <span className="text-sm text-gray-900 font-medium">{feature}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

