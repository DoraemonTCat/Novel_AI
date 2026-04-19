# 📖 Novel AI — AI-Powered Novel Writing Platform

<p align="center">
  <strong>แพลตฟอร์มแต่งนิยายด้วย AI อัจฉริยะ • รองรับภาษาไทยและอังกฤษ</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Llama_3_8B-0467DF?style=for-the-badge&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Dual AI Engine** | Google Gemini 2.5 Flash (cloud) + Ollama Llama 3 8B (local) |
| 📝 **Multi-Chapter Generation** | สร้างนิยายหลายตอนอัตโนมัติ พร้อม outline |
| 🌐 **Bilingual Support** | ภาษาไทย + English + Mixed |
| 📖 **Genre System** | 12 แนวนิยาย (Romance, Fantasy, Mystery, Sci-Fi, BL/GL, etc.) |
| ✍️ **Writing Styles** | Classic, Contemporary, Poetic, Dark Humor, Sweet |
| 🔐 **Google OAuth 2.0** | Login ด้วย Google + JWT (access 15min + refresh 7 days) |
| 🛡️ **Rate Limiting** | SlowAPI + Redis per-user / per-IP protection |
| 📊 **Real-time Progress** | WebSocket สำหรับดูสถานะการสร้างแบบ real-time |
| 📥 **Export** | PDF (ฟอนต์ไทย), EPUB, Markdown, TXT |
| 🎨 **Cover Generation** | Stable Diffusion WebUI (optional) |
| 👤 **Character Manager** | สร้างและจัดการตัวละคร (Story Bible) |
| 🌍 **World Building** | ตั้งค่าโลก, ระบบเวทมนตร์, timeline |
| 🌙 **Dark/Light Theme** | สลับธีมได้ |
| 🔄 **Version History** | บันทึกประวัติแก้ไขทุกตอน |

## 🏗️ Architecture

```
┌─────────┐     ┌──────────┐     ┌───────────┐
│ Frontend │────▶│ Backend  │────▶│PostgreSQL │
│ React    │     │ FastAPI  │     │           │
│ Nginx    │     │          │────▶│  Redis    │
│ :3000    │     │  :8000   │     │           │
└─────────┘     └───┬──────┘     └───────────┘
                    │
               ┌────┴─────┐     ┌───────────┐
               │  Celery   │────▶│ ChromaDB  │
               │  Worker   │     │ (RAG)     │
               └────┬──────┘     └───────────┘
                    │
          ┌─────────┴──────────┐
          │                    │
     ┌────┴────┐        ┌─────┴─────┐
     │ Gemini  │        │  Ollama   │
     │ API     │        │ (Llama 3) │
     └─────────┘        └───────────┘
```

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop/) installed
- [Google Cloud Console](https://console.cloud.google.com/) project with OAuth 2.0 credentials
- [Gemini API Key](https://aistudio.google.com/apikey)

### 1. Clone & Configure

```bash
git clone <repo-url>
cd Novel_AI
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret

# Optional - change in production
JWT_SECRET_KEY=generate-a-random-64-char-string
POSTGRES_PASSWORD=change-me
```

### 2. Start Services

**Windows (PowerShell):**
```powershell
# Core services only (uses Gemini API)
.\start.ps1

# With local Ollama (requires NVIDIA GPU)
.\start.ps1 -WithOllama

# With Stable Diffusion cover generation
.\start.ps1 -WithSD

# Everything
.\start.ps1 -WithOllama -WithSD
```

**Cross-platform:**
```bash
# Core services
docker compose up -d --build

# With Ollama
docker compose --profile with-ollama up -d --build
docker compose exec ollama ollama pull llama3:8b

# With Stable Diffusion
docker compose --profile with-sd up -d --build
```

### 3. Access the App

| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:3000 |
| 📡 Backend API | http://localhost:8000 |
| 📚 API Docs (Swagger) | http://localhost:8000/docs |
| 🔍 API Docs (ReDoc) | http://localhost:8000/redoc |
| ❤️ Health Check | http://localhost:8000/health |

## 🛠️ Tech Stack

### Frontend
- **React 19** + Vite 8
- **CSS Modules** (component-scoped styles)
- **Zustand** (state management)
- **React Query** (server state)
- **Framer Motion** (animations)
- **React Router 7** (routing)
- **i18next** (Thai/English i18n)
- **Lucide React** (icons)

### Backend
- **FastAPI** + Uvicorn
- **SQLAlchemy 2.0** (async ORM)
- **PostgreSQL 16**
- **Redis 7** (broker + cache + rate limiting)
- **Celery 5** (async task queue)
- **ChromaDB** (vector store for RAG)
- **LlamaIndex** (RAG framework)
- **WeasyPrint** (PDF with Thai fonts)
- **ebooklib** (EPUB export)
- **SlowAPI** (rate limiting)
- **python-jose** (JWT)

### AI Providers
- **Google Gemini 2.5 Flash** — Cloud API, fast, high quality
- **Ollama + Llama 3 8B** — Local, free, GPU-accelerated

### Infrastructure
- **Docker Compose** — 6 core + 2 optional services
- **Nginx** — Frontend reverse proxy + SPA routing

## 📁 Project Structure

```
Novel_AI/
├── docker-compose.yml      # All services
├── .env.example            # Environment template
├── start.ps1               # Windows start script
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI entry point
│       ├── config.py            # Pydantic settings
│       ├── database.py          # Async SQLAlchemy
│       ├── api/                 # API routes
│       │   ├── auth.py          # Google OAuth + JWT
│       │   ├── novels.py        # Novel CRUD
│       │   ├── chapters.py      # Chapter CRUD
│       │   ├── characters.py    # Character CRUD
│       │   ├── generation.py    # AI generation triggers
│       │   ├── websocket.py     # Real-time progress
│       │   ├── export.py        # PDF/EPUB/MD/TXT
│       │   └── world.py         # World Building
│       ├── models/              # SQLAlchemy ORM models
│       ├── schemas/             # Pydantic schemas
│       ├── services/            # Business logic
│       │   ├── auth_service.py
│       │   ├── prompt_templates.py
│       │   └── ai_providers/    # Gemini + Ollama
│       ├── tasks/               # Celery tasks
│       └── middleware/          # Auth + Rate Limit
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css            # Global design system
        ├── components/
        │   ├── Auth/            # Login + OAuth callback
        │   ├── Dashboard/       # Stats + Novel gallery
        │   ├── Layout/          # Sidebar + Header
        │   ├── NovelCreation/   # 5-step wizard
        │   ├── NovelDetail/     # Reader + chapters
        │   └── Settings/        # User preferences
        ├── stores/              # Zustand state
        ├── services/            # API client
        └── i18n/                # Thai + English
```

## 🔧 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Go to **APIs & Services** → **Credentials**
4. Create **OAuth 2.0 Client ID** (Web Application)
5. Add **Authorized redirect URI**: `http://localhost:8000/api/auth/google/callback`
6. Copy **Client ID** and **Client Secret** to your `.env`

## 📝 API Highlights

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/google/login` | Get Google OAuth URL |
| GET | `/api/auth/google/callback` | OAuth callback |
| POST | `/api/auth/refresh` | Refresh JWT token |
| GET | `/api/auth/me` | Current user |
| GET | `/api/novels/` | List novels |
| POST | `/api/novels/` | Create novel |
| POST | `/api/generation/start` | Start AI generation |
| GET | `/api/generation/status/{id}` | Check progress |
| WS | `/ws/generation/{task_id}` | Real-time progress |
| POST | `/api/export/` | Export novel |

## 🛑 Stopping

```bash
docker compose down

# Remove volumes (data will be lost)
docker compose down -v
```

## 📋 License

MIT

---

<p align="center">
  Built with ❤️ using Gemini 2.5 Flash + FastAPI + React
</p>
