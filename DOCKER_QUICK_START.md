# 🐳 Docker Quick Start Guide

## 🚀 Hızlı Başlangıç

### 1. Docker ile Başlatma (Önerilen)

```bash
# Tüm servisleri build et ve başlat
docker compose up --build -d

# Logları izle
docker compose logs -f

# Sadece backend loglarını izle
docker compose logs -f backend

# Servisleri durdur
docker compose down

# Servisleri durdur ve volume'ları temizle
docker compose down -v
```

### 2. Servisler

Sistem başlatıldığında şu servisler çalışacak:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Nginx**: http://localhost:8080
- **PostgreSQL**: localhost:5433

### 3. İlk Kurulum

```bash
# 1. Repoyu klonla veya indir
cd "/Users/test/Desktop/Seo Checker"

# 2. Docker Compose ile başlat
docker compose up -d

# 3. Database migration'ları çalıştır (ilk kurulumda)
docker compose exec backend alembic upgrade head

# 4. Tarayıcıda aç
open http://localhost:5173
```

### 4. Geliştirme Modu

```bash
# Backend'i development mode'da başlat (hot reload)
docker compose up backend

# Frontend'i development mode'da başlat
docker compose up frontend

# Tüm servisleri interaktif modda başlat
docker compose up
```

### 5. Yardımcı Komutlar

```bash
# Çalışan container'ları listele
docker compose ps

# Backend container'ına gir
docker compose exec backend bash

# Database'e bağlan
docker compose exec postgres psql -U postgres -d postgres

# Backend loglarını izle
docker compose logs -f backend

# Tüm servisleri yeniden başlat
docker compose restart

# Sadece backend'i yeniden başlat
docker compose restart backend

# Volume'ları listele
docker volume ls

# Kullanılmayan image'ları temizle
docker image prune -a
```

### 6. Sorun Giderme

#### Port zaten kullanılıyor
```bash
# Çalışan container'ları kontrol et
docker ps

# Port kullanan process'i bul (macOS/Linux)
lsof -i :8000
lsof -i :5173

# Container'ı durdur
docker compose down
```

#### Database bağlantı hatası
```bash
# PostgreSQL'in çalıştığını kontrol et
docker compose ps postgres

# Database loglarını kontrol et
docker compose logs postgres

# Database'i yeniden başlat
docker compose restart postgres
```

#### Playwright hatası
```bash
# Backend container'ını yeniden build et
docker compose build backend --no-cache

# Container'a gir ve Playwright'i kontrol et
docker compose exec backend playwright --version
```

#### WeasyPrint PDF hatası
```bash
# Backend loglarını kontrol et
docker compose logs backend | grep -i weasyprint

# Container'a gir ve test et
docker compose exec backend python -c "from weasyprint import HTML; print('OK')"
```

### 7. Production Deployment

```bash
# Production build
docker compose -f docker-compose.yml build

# Production'da başlat
docker compose -f docker-compose.yml up -d

# Environment değişkenlerini ayarla
# .env dosyası oluştur:
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:your_password@postgres:5432/postgres
GEMINI_API_KEY=your_gemini_api_key
ENVIRONMENT=production
DEBUG=False
EOF

# Güvenlik için şifreleri değiştir
docker compose down
# docker-compose.yml'de şifreleri güncelle
docker compose up -d
```

### 8. Backup ve Restore

```bash
# Database backup
docker compose exec postgres pg_dump -U postgres postgres > backup.sql

# Database restore
docker compose exec -T postgres psql -U postgres postgres < backup.sql

# Volume backup
docker run --rm \
  -v seochecker_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

### 9. Monitoring

```bash
# Resource kullanımını izle
docker stats

# Disk kullanımını kontrol et
docker system df

# Container health check
docker compose ps
```

### 10. Temizlik

```bash
# Tüm container'ları durdur ve sil
docker compose down

# Volume'ları da sil (DİKKAT: Tüm data silinir!)
docker compose down -v

# Kullanılmayan image'ları sil
docker image prune -a

# Tüm Docker verilerini temizle (DİKKAT!)
docker system prune -a --volumes
```

## 📋 Environment Variables

Backend için gerekli environment değişkenleri:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/postgres

# Gemini AI
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# App Config
ENVIRONMENT=production
DEBUG=False

# Playwright (otomatik ayarlanır)
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

## 🔧 Docker Compose Servisleri

### Backend
- **Image**: Python 3.11-slim
- **Port**: 8000
- **Volumes**: 
  - `./backend:/app` (kod)
  - `workspace_data:/app/workspace`
  - `backup_data:/app/backups`
  - `reports_data:/app/workspace/reports`
  - `screenshots_data:/app/workspace/screenshots`
- **Dependencies**: Playwright, WeasyPrint, FastAPI

### Frontend
- **Image**: Node 18-alpine
- **Port**: 5173
- **Volumes**: `./frontend:/app`
- **Tech**: React + Vite + TypeScript

### PostgreSQL
- **Image**: PostgreSQL 15-alpine
- **Port**: 5433 (host) → 5432 (container)
- **Volume**: `postgres_data:/var/lib/postgresql/data`
- **Health Check**: Aktif

### Nginx
- **Image**: Nginx alpine
- **Port**: 8080
- **Config**: `./nginx/nginx.conf`

## 🎯 SEO Spider Özellikleri

Docker container'ında çalışan özellikler:

✅ **Playwright Crawler** - Chromium ile JavaScript render
✅ **Gemini AI** - SEO analizi
✅ **WeasyPrint** - PDF rapor oluşturma
✅ **PostgreSQL** - Veri saklama
✅ **Hot Reload** - Development modu
✅ **Volume Persistence** - Veri kalıcılığı

## 📞 Yardım

Sorun yaşarsanız:

```bash
# Tüm logları kontrol et
docker compose logs

# Belirli bir servisin loglarını kontrol et
docker compose logs backend
docker compose logs frontend
docker compose logs postgres

# Container durumunu kontrol et
docker compose ps

# Container'a gir ve debug yap
docker compose exec backend bash
```

---

**Not**: İlk build işlemi 5-10 dakika sürebilir (Playwright Chromium indirme dahil).

