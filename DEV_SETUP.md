# 🚀 Development Setup Guide

## Hızlı Başlangıç (Local Development)

### 1️⃣ PostgreSQL Kurulumu

#### macOS (Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15

# Database oluştur
createdb seochecker
createuser seouser
psql -c "ALTER USER seouser WITH PASSWORD 'seopass';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE seochecker TO seouser;"
```

#### Docker ile (Önerilen):
```bash
docker run -d \
  --name seo-postgres \
  -e POSTGRES_USER=seouser \
  -e POSTGRES_PASSWORD=seopass \
  -e POSTGRES_DB=seochecker \
  -p 5432:5432 \
  postgres:15-alpine
```

---

### 2️⃣ Backend Kurulumu

```bash
cd backend

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate  # Windows

# Dependencies yükle
pip install -r requirements.txt

# .env dosyası zaten hazır (API key ile)

# Database tablolarını oluştur
python -c "
from app.database import init_db
import asyncio
asyncio.run(init_db())
"

# Backend'i başlat
uvicorn app.main:app --reload --port 8000
```

**Backend çalışıyor:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

---

### 3️⃣ Frontend Kurulumu

```bash
cd frontend

# Dependencies yükle
npm install

# .env dosyası zaten hazır

# Frontend'i başlat
npm run dev
```

**Frontend çalışıyor:** http://localhost:5173

---

## 🧪 Test Etme

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```

Beklenen response:
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini": "configured"
}
```

### 2. Frontend Test
Tarayıcıda aç: http://localhost:5173
- Dashboard görünmeli
- Sidebar çalışmalı
- Dil değiştirme (🇹🇷/🇬🇧) çalışmalı

### 3. API Test (Postman veya curl)

#### Job Oluştur:
```bash
curl -X POST http://localhost:8000/api/jobs/create \
  -F "file=@test.zip" \
  -F "keywords=test,seo" \
  -F "site_language=tr" \
  -F "site_url=https://example.com"
```

---

## 📁 Test Dosyası Hazırlama

Basit bir test ZIP dosyası oluştur:

```bash
# Test klasörü oluştur
mkdir test_site
cd test_site

# Basit PHP dosyası
cat > index.php << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test Site</title>
</head>
<body>
    <h1>Welcome</h1>
    <p>This is a test page.</p>
</body>
</html>
EOF

# ZIP oluştur
cd ..
zip -r test.zip test_site/
```

---

## 🐛 Troubleshooting

### Backend Hatası: "Connection refused"
```bash
# PostgreSQL çalışıyor mu kontrol et
psql -U seouser -d seochecker -h localhost

# Çalışmıyorsa başlat
brew services start postgresql@15
# veya
docker start seo-postgres
```

### Frontend Hatası: "Module not found"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Gemini API Hatası
```bash
# API key doğru mu kontrol et
cat backend/.env | grep GEMINI_API_KEY

# Test et
curl -X POST http://localhost:8000/api/monitoring/rate-limiter
```

---

## 🔍 Monitoring Endpoints

### Rate Limiter Status:
```bash
curl http://localhost:8000/api/monitoring/rate-limiter
```

### Memory Limits:
```bash
curl http://localhost:8000/api/monitoring/memory-limits
```

### Circuit Breaker (job_id gerekli):
```bash
curl http://localhost:8000/api/monitoring/circuit-breaker/test-job-id
```

---

## 🎯 Geliştirme Workflow

1. **Backend değişiklik:**
   - Dosyayı düzenle
   - Uvicorn otomatik reload yapar
   - http://localhost:8000/docs'ta test et

2. **Frontend değişiklik:**
   - Dosyayı düzenle
   - Vite HMR ile otomatik günceller
   - Tarayıcıda hemen görürsün

3. **Database değişiklik:**
   - Model değiştir (`backend/app/models/`)
   - Alembic migration oluştur (opsiyonel)
   - Veya tabloları yeniden oluştur

---

## 🚀 Production Build Test

### Docker Compose ile:
```bash
# Tüm servisleri başlat
docker-compose up -d

# Logları izle
docker-compose logs -f

# Durdur
docker-compose down
```

**Access:**
- Frontend: http://localhost:80
- Backend: http://localhost:8000

---

## 📊 Database Yönetimi

### Tabloları Görüntüle:
```bash
psql -U seouser -d seochecker -h localhost

\dt  # Tabloları listele
\d jobs  # Job tablosu detayı
SELECT * FROM jobs;  # Job'ları görüntüle
```

### Veritabanını Sıfırla:
```bash
psql -U seouser -d seochecker -h localhost -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Sonra backend'i yeniden başlat (tablolar otomatik oluşur)
```

---

## ✅ Checklist

- [ ] PostgreSQL çalışıyor
- [ ] Backend başladı (http://localhost:8000)
- [ ] Frontend başladı (http://localhost:5173)
- [ ] Health check başarılı
- [ ] Dashboard açılıyor
- [ ] Dil değiştirme çalışıyor
- [ ] API docs erişilebilir

---

## 🆘 Yardım

Sorun yaşarsan:
1. Terminal loglarını kontrol et
2. Browser console'u kontrol et (F12)
3. Database bağlantısını test et
4. API key'in doğru olduğundan emin ol

**Hazırsın! Test etmeye başlayabilirsin! 🎉**

