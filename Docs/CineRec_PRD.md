# Product Requirements Document (PRD): CineRec (The Weaver)

**Document Version:** 2.0 (Comprehensive Specification)
**Status:** In Active Development (Implementation Phase)
**Last Updated:** October 2026

---

## 1. Executive Summary
**CineRec (The Weaver)** is a highly immersive, AI-native cinematic exploration and recommendation engine. Deviating from traditional, grid-based catalogs, CineRec acts as an intelligent curator—dubbed "Arachne" or "The Orb"—that determines a user's deeply specific cinematic preferences, psychological inclinations, and aesthetic "vibes" through fluid, natural language conversation.

The product relies heavily on cutting-edge 3D-spatial frontend rendering and a robust, multi-tiered LLM backend to make movie discovery feel like an interactive narrative experience rather than a database query.

---

## 2. Problem Statement & Market Opportunity
**The Problem:**
Current recommendation engines (Netflix, Letterboxd, IMDb) rely on static collaborative filtering, rigid genres, or basic metadata (e.g., "Action movies from 2010"). Users frequently seek films based on abstract feelings, atmospheric aesthetics, or highly specific narrative tropes (e.g., "I want a neon-noir detective film with a slow-burn pacing and atmospheric dread"). Traditional engines cannot process these semantic, vibe-based requests.

**The Solution:**
An architecture that leverages Large Language Models (LLMs) to interpret abstract user prompts, cross-reference them against rich cinematic metadata via Vector databases, and present the results in an immersive, highly interactive visual canvas.

---

## 3. Target Audience & Personas
*   **The Vibe-Seeker (Primary):** Wants a specific aesthetic or emotional experience for movie night but lacks the exact vocabulary or movie titles to find it manually. Values the conversational AI interface.
*   **The Auteur / Cinephile (Secondary):** Cares deeply about directorial style, cinematography, and niche subgenres. Uses the platform to maintain a sophisticated Watchlist and Viewing History.
*   **The Aesthetic Explorer (Tertiary):** Drawn to the platform for its UI/UX—specifically the 3D Infinite Canvas and narrative-driven dashboard that acts as a "mirror" to their cinematic soul.

---

## 4. Technical Architecture & Tech Stack (Comprehensive)

The system utilizes a decoupled Modular Monolith architecture, separating a high-performance React frontend from a Python-based data and AI processing backend.

### 4.1 Frontend (Client Application)
*   **Framework:** Next.js 14 (App Router)
*   **UI Library:** React 18
*   **Styling:** TailwindCSS (utilizing complex arbitrary variants like `perspective-[1500px]` for 3D staging).
*   **Animation & Motion:** 
    *   **GSAP (GreenSock):** Utilized for high-performance, hardware-accelerated matrix transforms (e.g., the 60fps 3D Infinite Canvas).
    *   **Framer Motion:** Utilized for layout transitions, micro-interactions, and the sliding prompt timeline.
*   **Authentication:** NextAuth.js (handling session JWTs and secure cookie management).
*   **Deployment:** Vercel (Edge network, Serverless functions).

### 4.2 Backend (API Core)
*   **Framework:** FastAPI (Python 3.11+) - chosen for async performance and automatic OpenAPI documentation.
*   **ORM / Database Toolkit:** SQLAlchemy 2.0 (Core & ORM) with Alembic for database schema migrations.
*   **Data Validation:** Pydantic (strict schema enforcement between frontend payloads and database models).
*   **Deployment:** Render Blueprint (`render.yaml`) orchestrating Dockerized web services.

### 4.3 Data Layer
*   **Primary Database:** PostgreSQL (Neon / Supabase / Render Postgres).
*   **Vector Engine:** `pgvector` extension configured for nearest-neighbor semantic search (storing embeddings of movie synopses and user vibes).
*   **Caching/State:** In-memory session tracking for active AI conversations.

### 4.4 External Integrations & Pipelines
*   **LLM Pipeline (Fallback Architecture):**
    *   *Tier 1:* **Groq** (Llama-3 / Mixtral) - Ultra-low latency inference for real-time conversational responses.
    *   *Tier 2:* **OpenRouter** - Routing layer for access to diverse models (Claude, etc.).
    *   *Tier 3:* **Google Gemini** - Fallback multimodal capabilities and heavy reasoning.
*   **Cinematic Data:** **TMDB API (v3/v4)** - Source of truth for movie metadata, posters, backdrops, and cast information.

---

## 5. Functional Requirements (Current State)

### 5.1 The Conversational Engine (The Orb)
*   **Interactive Chat:** Users converse with "The Orb". The AI processes abstract prompts and returns curated movie objects mapped to TMDB IDs.
*   **Dynamic Prompt Timeline:** A ChatGPT-style right-aligned timeline panel. 
    *   *Hover State:* Expands to reveal truncated prompt history.
    *   *Click State:* Jumps the conversation context back to that specific historical prompt.

### 5.2 The Infinite Canvas (Visual Engine)
The background of the application is a perpetually moving grid of movie posters, strictly isolated by form factor for performance:
*   **Desktop Engine:** Uses raw GSAP Math to create a 3D cylindrical projection. Posters are rotated along a Y-axis using `rotationY: angleRad`, pushed back in Z-space, and rendered within a parent container possessing `[perspective: 1500px]`.
*   **Mobile Engine:** Bypasses the 3D cylinder to prevent vertical screen tearing. Uses a mathematically precise 2D flat tiling grid that wraps edge-to-edge seamlessly based on the mobile viewport dimensions.

### 5.3 User Dashboard & The Weaver Profile
*   **Narrative Profile:** Analyzes the user's viewing history to generate a psychological breakdown (e.g., *"Arachne has observed your choices. You lean heavily into atmospheric dread..."*).
*   **Watchlist Subsystem:** Users can add recommended films to a dedicated Watchlist. The system seamlessly intercepts the TMDB ID, performs a `GET` sync to the local backend, generates an internal UUID, and associates it with the User's Watchlist table.
*   **Viewing History:** Hovering over Watchlist cards reveals "Watch Movie" and "Watched" actions. Marking a movie as "Watched" fires an API sequence that drops the movie from the Watchlist and creates a `ViewingHistory` record marked as `COMPLETED`.
*   **Real-Time Statistics:** The dashboard aggregates real database records (using `func.count()`) to display accurate, dynamic stats (e.g., Total Films Watched, Watchlist Size).

---

## 6. Non-Functional Requirements (NFRs)

*   **Performance (Rendering):** The Infinite Canvas must maintain a strict 60fps. Culling logic (`if finalZ > -100 { display: none }`) is required to prevent rendering DOM nodes on the back half of the 3D cylinder.
*   **Performance (Network):** LLM API calls must resolve within 3 seconds. The Fallback Architecture ensures rate-limit errors from one provider silently failover to the next without user disruption.
*   **Data Integrity & Sync:** A movie cannot be added to a user's relational Watchlist using a raw TMDB integer. The system must enforce the TMDB -> UUID mapping pipeline to ensure database referential integrity.
*   **SSR Compatibility:** CSS `perspective` and window size calculations must gracefully handle Next.js Server-Side Rendering (SSR) to prevent hydration mismatch errors (e.g., using `typeof window !== 'undefined'`).

---

## 7. Data Models & Schemas

1.  **User Model:** UUID, Email, OAuth Tokens, Created/Updated Timestamps.
2.  **Movie Model:** Internal UUID, TMDB ID (Unique Integer), Title, Poster Path, Backdrop Path, Overview, Release Date.
3.  **Watchlist Model:** Many-to-Many join table linking `User UUID` and `Movie UUID`.
4.  **ViewingHistory Model:** Links `User UUID` and `Movie UUID` with metadata (`status: COMPLETED`, `watched_at`).
5.  **ChatSession Model:** Tracks `session_id`, linking an array of user/AI interaction logs for historical context jumping.

---

## 8. Future Roadmap (Next Phases)

*   **Phase 3 (Social):** Implement "Weaver Sync," allowing two users to cross-reference their profiles to find a mathematically perfect compromise movie for a shared movie night.
*   **Phase 4 (Semantic Search):** Fully activate the `pgvector` database to allow users to search via vector proximity rather than relying entirely on the LLM's internal memory (RAG architecture).
*   **Phase 5 (Analytics UI):** Introduce interactive Radar charts on the Dashboard mapping the user's taste across variables like *Pacing, Brightness, Tension, Surrealism, and Gore*.
