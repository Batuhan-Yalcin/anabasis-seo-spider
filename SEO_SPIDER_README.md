# 🔍 AI Anabasis SEO Spider

Profesyonel, AI destekli tek sayfa SEO analiz modülü.

## ✨ Özellikler

### 🎯 Gerçek Veri ve API Entegrasyonu
- ✅ **PostgreSQL Database** - Tüm veriler database'e kaydedilir
- ✅ **Playwright Crawler** - JavaScript render desteği ile gerçek web tarama
- ✅ **Gemini AI** - Gerçek yapay zeka analizi (fake veri yok!)
- ✅ **Real-time Progress** - Canlı analiz takibi

### 📊 Anahtar Kelime Skoru Hesaplama
Anahtar kelime performansı şu kriterlere göre hesaplanır:

1. **Title Analizi** (Ağırlık: %25)
   - Anahtar kelimenin title'da varlığı
   - Title'daki pozisyon (başta ise bonus)
   - Title uzunluğu (50-60 karakter ideal)

2. **Meta Description** (Ağırlık: %15)
   - Anahtar kelimenin meta description'da varlığı
   - Meta uzunluğu (150-160 karakter ideal)

3. **H1-H2-H3 Hiyerarşisi** (Ağırlık: %25)
   - H1'de anahtar kelime kullanımı
   - H2-H3'te doğal dağılım
   - Heading yapısının geçerliliği

4. **Keyword Density** (Ağırlık: %15)
   - İdeal yoğunluk: %1-3
   - Aşırı kullanım (spam) tespiti
   - Semantic doğallık kontrolü

5. **Schema Uyumluluğu** (Ağırlık: %10)
   - Gerekli schema türlerinin varlığı
   - Schema içinde anahtar kelime kullanımı

6. **İçerik Kalitesi** (Ağırlık: %10)
   - Kelime sayısı (min 300 kelime)
   - İçerik derinliği
   - Anahtar kelimenin bağlamsal kullanımı

**Sonuç:**
- `presence_score`: 0-100 (Anahtar kelimenin sayfada ne kadar var olduğu)
- `prominence`: 0-100 (Anahtar kelimenin ne kadar öne çıktığı)

### 🔍 Analiz Edilen SEO Faktörleri

#### Teknik SEO
- ✅ Schema.org yapılandırılmış veri
- ✅ Title etiketi optimizasyonu
- ✅ Meta description kontrolü
- ✅ Heading yapısı (H1-H2-H3)
- ✅ Robots.txt analizi
- ✅ Sitemap.xml kontrolü
- ✅ Kırık link tespiti

#### İçerik Analizi
- ✅ Kelime sayısı
- ✅ Anahtar kelime yoğunluğu
- ✅ Semantic density
- ✅ Google snippet uyumluluğu
- ✅ İç/dış link analizi
- ✅ Anchor text doğallığı

#### Görsel Optimizasyonu
- ✅ ALT etiket kontrolü
- ✅ Eksik ALT tespiti
- ✅ Görsel sayısı

### 📄 Raporlama
- ✅ HTML rapor (tarayıcıda görüntüleme)
- ✅ PDF rapor (indirilebilir)
- ✅ Detaylı sorun listesi
- ✅ Öncelik bazlı sıralama
- ✅ Kod örnekleri ve düzeltme önerileri

## 🚀 Kurulum

### 1. Backend Kurulumu

```bash
cd backend

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Playwright tarayıcılarını yükle
playwright install chromium

# .env dosyası oluştur
cp .env.example .env
```

`.env` dosyasını düzenle:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/seo_checker
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=development
DEBUG=True
```

```bash
# Database migration
alembic upgrade head

# Sunucuyu başlat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Kurulumu

```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Development sunucusunu başlat
npm run dev
```

Frontend: http://localhost:5173
Backend API: http://localhost:8000

## 📖 Kullanım

### 1. SEO Spider Sayfasına Git
- Sidebar'dan "SEO Spider" menüsüne tıkla

### 2. Analiz Başlat
- **URL**: Analiz edilecek sayfanın tam URL'si
  - Örnek: `https://example.com/urun-sayfasi`
- **Anahtar Kelimeler**: Virgülle ayırarak gir
  - Örnek: `seo analizi, arama motoru optimizasyonu, seo araçları`

### 3. Analiz Takibi
- Real-time progress bar ile analiz durumunu izle
- Aşamalar:
  1. **Crawling**: Sayfa taranıyor
  2. **Analyzing**: AI analizi yapılıyor
  3. **Generating Report**: Rapor oluşturuluyor
  4. **Completed**: Tamamlandı!

### 4. Sonuçları İncele
- **Genel Skor**: 0-100 arası genel SEO skoru
- **Teknik SEO Skoru**: Teknik faktörler
- **İçerik Skoru**: İçerik kalitesi
- **Anahtar Kelime Performansı**: Her kelime için detaylı analiz
- **Sorun Listesi**: Öncelik sırasına göre sorunlar
- **Teknik Metrikler**: Sayfa metrikleri

### 5. Rapor İndir
- PDF formatında detaylı rapor indir
- Müşteriye sunulabilir profesyonel format

## 🏗️ Mimari

### Backend Stack
```
FastAPI (Python)
├── Playwright (Web Crawling)
├── Gemini AI (SEO Analysis)
├── SQLAlchemy (ORM)
├── PostgreSQL (Database)
├── Jinja2 (HTML Templates)
└── WeasyPrint (PDF Generation)
```

### Frontend Stack
```
React + TypeScript
├── Vite (Build Tool)
├── TailwindCSS (Styling)
├── React Router (Routing)
├── Axios (API Client)
└── Lucide Icons
```

### Database Schema

**seo_analyses**
- id, url, keywords, status
- html_content, screenshot_path
- page_title, meta_description
- word_count, scores
- report paths

**seo_issues**
- id, analysis_id
- issue_type, severity, confidence
- reason, recommendation, example_fix

**seo_metrics**
- id, analysis_id
- schemas, headings, links, images
- technical metrics

## 🔧 API Endpoints

### SEO Spider API

```http
POST /api/seo/analyze
Content-Type: application/json

{
  "url": "https://example.com",
  "keywords": ["keyword1", "keyword2"]
}

Response: {
  "id": "uuid",
  "status": "pending",
  ...
}
```

```http
GET /api/seo/analyze/{analysis_id}
Response: Detaylı analiz sonucu
```

```http
GET /api/seo/analyze/{analysis_id}/progress
Response: Real-time progress
```

```http
GET /api/seo/analyses?skip=0&limit=20
Response: Analiz listesi
```

```http
DELETE /api/seo/analyze/{analysis_id}
Response: Success message
```

## 🎨 Frontend Sayfaları

### SEOSpider.tsx
- Ana analiz başlatma sayfası
- URL ve keyword input
- Özellik açıklamaları

### SEOAnalysisDetail.tsx
- Analiz sonuçları sayfası
- Real-time progress tracking
- Skor kartları
- Keyword performans kartları
- Sorun listesi (severity bazlı)
- Teknik metrikler

## 🔐 Güvenlik

- ✅ Input validation (Pydantic)
- ✅ SQL injection koruması (SQLAlchemy ORM)
- ✅ XSS koruması (React)
- ✅ CORS yapılandırması
- ✅ Rate limiting (opsiyonel)

## 📊 Performans

- **Crawl Süresi**: ~5-10 saniye
- **AI Analiz**: ~10-20 saniye (chunk sayısına göre)
- **Rapor Oluşturma**: ~2-5 saniye
- **Toplam**: ~20-35 saniye

## 🐛 Hata Ayıklama

### Backend Logları
```bash
# Terminal'de backend loglarını izle
tail -f backend/logs/app.log
```

### Frontend Console
```javascript
// Browser console'da
localStorage.getItem('debug') // Debug mode kontrolü
```

### Database Kontrolü
```sql
-- Aktif analizler
SELECT * FROM seo_analyses WHERE status != 'completed';

-- Son analizler
SELECT id, url, status, overall_score, created_at 
FROM seo_analyses 
ORDER BY created_at DESC 
LIMIT 10;
```

## 📝 Notlar

1. **Gemini API Key**: Mutlaka geçerli bir Gemini API key gerekli
2. **Playwright**: İlk kurulumda chromium indirilmeli
3. **Database**: PostgreSQL çalışır durumda olmalı
4. **WeasyPrint**: PDF için sistem bağımlılıkları gerekebilir

## 🎯 Gelecek Özellikler

- [ ] Toplu URL analizi
- [ ] Zamanlanmış analizler
- [ ] E-posta raporlama
- [ ] Rekabet analizi
- [ ] Backlink analizi (dış API ile)
- [ ] Performans metrikleri (Core Web Vitals)

## 📞 Destek

Herhangi bir sorun için:
- GitHub Issues
- Email: support@aianabasis.com

---

**AI Anabasis SEO Spider** - Profesyonel SEO analizi artık çok kolay! 🚀

