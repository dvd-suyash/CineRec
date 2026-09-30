<div align="center">
  <img src="apps/web/public/arachne.webm" width="200" alt="CineRec Orb" />
  <h1>🎬 CineRec</h1>
  <p><strong>An intelligent, AI-driven cinematic exploration and recommendation engine.</strong></p>
  
  [![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=for-the-badge&logo=postgresql)](https://postgresql.org/)
  [![Redis](https://img.shields.io/badge/Redis-Celery-DC382D?style=for-the-badge&logo=redis)](https://redis.io/)
  [![Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google)](https://deepmind.google/technologies/gemini/)
</div>

<br />

CineRec is a brutalist-inspired, AI-native platform that redefines how you discover movies. Powered by Google's Gemini AI, real-time TMDB data, and a conversational interface named **Arachne**, CineRec acts as your personal cinema curator. It builds a persistent "Taste Profile" based on your interactions and seamlessly streams recommendations instantly.

---

## ✨ Key Features

- 🔮 **The Orb (Arachne):** A fully voice-driven and text conversational agent that talks to you, learns your preferences, and recommends movies natively without breaking the immersive experience.
- 🧬 **Cinematic DNA & Memory:** The backend utilizes `pgvector` and Gemini embeddings to deeply understand the *vibe* of what you watch, saving your core memories to construct an evolving taste profile.
- 🍿 **Instant Streaming:** Integrated with the Vidhive API, you can seamlessly stream any recommended movie or TV show directly inside the app with a single click.
- 🖼️ **Infinite Canvas:** A beautiful, drag-and-drop, brutalist spatial canvas where your recommendations float in an interactive space.
- ⚡ **Background Workers:** Heavy AI processing, TMDB synchronizations, and embedding generations are handled asynchronously by Celery workers to keep the API lightning fast.

---

## 🛠️ Tech Stack

**Frontend (The Canvas & Orb)**
* **Next.js 14** (App Router)
* **React & Framer Motion** (For the spatial, fluid animations)
* **Tailwind CSS** (Brutalist styling)
* **Next-Auth** (Google OAuth integration)

**Backend (The Brain)**
* **FastAPI** (High-performance async Python backend)
* **SQLAlchemy 2.0 & asyncpg** (Asynchronous database communication)
* **Celery & Redis** (Distributed task queue for AI processing)
* **Google Gemini Pro** (LLM for conversational recommendations & vector embeddings)
* **TMDB API** (Canonical source of truth for movie metadata)

**Database (The Memory)**
* **PostgreSQL** with `pgvector` extension for storing and searching semantic embeddings.

---

## 🚀 Local Development

Getting the entire stack running locally is incredibly simple. You must have [Docker](https://www.docker.com/) and [Make](https://www.gnu.org/software/make/) installed.

### 1. Clone & Configure
```bash
git clone https://github.com/dvd-suyash/CineRec.git
cd CineRec
```

Create a `.env` file in the root directory (and an identical one in `apps/web/.env.local`). You will need:
```env
# API Keys
TMDB_API_KEY=your_tmdb_jwt_token
GEMINI_API_KEY=your_google_gemini_key

# Database
DATABASE_URL=postgresql+asyncpg://cinerec:cinerec@localhost:5432/cinerec
REDIS_URL=redis://localhost:6379/0

# Auth
SECRET_KEY=super_secret_development_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
NEXTAUTH_URL=http://localhost:3000
```

### 2. Start the Databases
Spin up the local PostgreSQL (with pgvector) and Redis instances:
```bash
make up
```

### 3. Run the Backend API & Workers
In a new terminal:
```bash
make dev-api
```
*(Optionally, start the celery worker locally via `make dev-worker`)*

### 4. Run the Frontend
In another terminal:
```bash
make dev-web
```
Visit `http://localhost:3000` to interact with Arachne!

---

## ☁️ Production Deployment

CineRec is architected as Infrastructure-as-Code (IaC) and is fully ready for 1-click cloud deployments.

### Backend (Render)
1. Go to [Render](https://render.com) and click **New > Blueprint**.
2. Connect this repository.
3. Render will read the `render.yaml` file and automatically provision your Managed PostgreSQL, Private Redis, FastAPI Web Service, and Celery Worker.
4. Input your `TMDB` and `Gemini` API keys when prompted.

### Frontend (Vercel)
1. Go to [Vercel](https://vercel.com) and import this repository.
2. Set the Root Directory to `apps/web`.
3. Add `NEXT_PUBLIC_API_URL` pointing to your new Render web service URL.
4. Deploy!

---

<p align="center">
  <i>"I do not just watch. I observe. What shall we weave today?" — Arachne</i>
</p>
