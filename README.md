# AI Anabasis SEO Spider

Enterprise-grade AI-powered website intelligence platform for automated SEO analysis and patching.

## 🚀 Features

- **AI-Powered Analysis:** Gemini 2.5 Flash integration for intelligent code analysis
- **Semantic Chunking:** Smart code segmentation with overlap for context preservation
- **Automatic Patching:** Safe, sandboxed patch application with validation
- **Production Safeguards:**
  - Memory guard (500MB limit)
  - Rate limiter (3 concurrent Gemini requests)
  - Circuit breaker (5 failure threshold)
  - DB transaction safety
  - Automatic rollback on validation failure
- **Multi-language Support:** Turkish (default) and English
- **Real-time Monitoring:** Live activity feed, rate limiter metrics, circuit breaker status
- **Monaco Editor:** Professional diff viewer for code changes

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **Framework:** FastAPI (async)
- **Database:** PostgreSQL with asyncpg
- **AI:** Google Gemini 2.5 Flash
- **Validation:** PHP lint, DOM integrity, React build checks
- **Safety:** Sandboxed patching, automatic backups, rollback support

### Frontend (React + TypeScript)
- **Framework:** React 18 + Vite
- **Language:** TypeScript
- **Styling:** TailwindCSS + Glassmorphism
- **State:** Zustand
- **API:** Axios + React Query
- **Editor:** Monaco Editor

## 📦 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Gemini API Key

### Setup

1. **Clone repository:**
```bash
git clone <repository-url>
cd "Seo Checker"
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Start with Docker Compose:**
```bash
docker-compose up -d
```

4. **Access the application:**
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

### API Endpoints

#### Jobs
- `POST /api/jobs/create` - Create new job with file upload
- `GET /api/jobs/{job_id}` - Get job details
- `POST /api/jobs/{job_id}/extract` - Extract and inventory files
- `POST /api/jobs/{job_id}/chunk` - Chunk files
- `GET /api/jobs/{job_id}/files` - Get job files
- `GET /api/jobs/{job_id}/issues` - Get job issues

#### Analysis
- `POST /api/analysis/{job_id}/analyze` - Start full automatic analysis
- `POST /api/analysis/{job_id}/analyze-batch` - Analyze next batch

#### Patches
- `POST /api/patches/approve` - Approve and apply patches
- `POST /api/patches/reject` - Reject issues
- `POST /api/patches/rollback/{issue_id}` - Rollback patch

#### Monitoring
- `GET /api/monitoring/rate-limiter` - Rate limiter metrics
- `GET /api/monitoring/circuit-breaker/{job_id}` - Circuit breaker status
- `GET /api/monitoring/memory-limits` - Memory limits

### Workflow

1. **Upload:** User uploads ZIP/TAR file
2. **Extract:** System extracts and checks size (500MB limit)
3. **Chunk:** Files split into 180-line chunks with 20-line overlap
4. **Analyze:** Gemini analyzes each chunk (max 3 concurrent)
5. **Deduplicate:** Issues deduplicated by severity
6. **Review:** User reviews issues in UI
7. **Patch:** Approved patches applied in sandbox
8. **Validate:** PHP lint, DOM integrity, build checks
9. **Apply:** Original files replaced if validation passes
10. **Rollback:** Automatic rollback on failure

## 🎨 Design System

### Colors
- **Background:** Dark blue (#0A0E1A, #131825, #1C2333)
- **Accent:** Electric blue (#00D9FF) + Purple (#8B5CF6)
- **Severity:** Critical (red), High (amber), Medium (purple), Low (green)

### Typography
- **UI:** Inter
- **Code:** JetBrains Mono
- **Display:** Clash Display

## 🔒 Security

- Sandboxed patch application
- Automatic backups before changes
- Validation before applying patches
- Circuit breaker for cascading failures
- Memory limits to prevent exhaustion
- Rate limiting for API calls

## 🌍 i18n Support

Default language: Turkish (tr)
Supported languages: Turkish, English

Change language via UI language switcher in top bar.

## 📊 Monitoring

Access monitoring dashboard at `/monitoring` for:
- Rate limiter metrics
- Circuit breaker status
- Memory usage
- Active requests
- System health

## 🤝 Contributing

This is a proprietary enterprise application.

## 📄 License

Proprietary - AI Anabasis

## 🆘 Support

For support, contact: support@anabasis.ai

---

**AI Anabasis SEO Spider** - Deep crawl. Smart fix. Ship faster.

