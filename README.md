# 🎬 Study-Material-to-Video Agent

<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="status">
  <img src="https://img.shields.io/badge/python-3.12-blue" alt="python">
  <img src="https://img.shields.io/badge/next.js-14-black" alt="nextjs">
  <img src="https://img.shields.io/badge/LLM-Groq-orange" alt="groq">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="license">
</p>

<p align="center">
  <b>An agentic AI system that turns a topic into a complete, narrated explainer video — no scripting, recording, or editing required.</b>
</p>

<p align="center">
  Give it <code>"Two Sum using a hash map"</code>. Get back a planned, narrated, animated video.
</p>

---

### 📊 Project Highlights

| 🤖 AI Agents | 🔊 TTS | 🎨 Visuals | 🎬 Assembly |
|---|---|---|---|
| 4 specialized agents | Piper TTS | Manim | FFmpeg |

## 📺 Demo

<details> <summary>☀️ Watch Light Mode</summary>

<br>

https://github.com/heena-jindal/ai-study-video-generator/raw/refs/heads/main/light-theme-demo.mp4

</details>

<details> <summary>🌙 Watch Dark Mode</summary>

<br>

https://github.com/heena-jindal/ai-study-video-generator/raw/refs/heads/main/dark-theme-demo.mp4

</details>



> **🌐 [Live frontend](#)** — *[ Vercel URL](https://ai-study-video-generator.vercel.app/)* — the UI is deployed and browsable; see [Deployment Status](DEPLOYMENT.md) for why video generation isn't live on it.

---

## 📑 Contents

* [🎬 Demo](#-demo)
* [⚠️ Deployment Status](#️-deployment-status)
* [🧠 How It Works](#-how-it-works)
* [✨ Features](#-features)
* [🛠️ Tech Stack](#️-tech-stack)
* [🚀 Setup](#-setup)
* [📡 API](#-api)
* [🏗️ Design Decisions](#️-design-decisions)
* [🐞 Known Limitations](#-known-limitations)
* [🗺️ Roadmap](#️-roadmap)


## ⚠️ Deployment Status

| Component | Status |
|---|---|
| Frontend (Vercel) | ✅ Deployed and live |
| Backend (video pipeline) | ⚠️ Not currently deployed publicly — runs fully locally / via Docker |

The backend needs more memory than most free hosting tiers provide. Full details, evidence, and how to run it yourself → **[DEPLOYMENT.md](DEPLOYMENT.md)**

---


## 🧠 How It Works

This is a genuine **multi-agent pipeline** — four specialist agents chained in a fixed sequence, each handling a fundamentally different kind of work, orchestrated with LangGraph.

```mermaid
flowchart TD
    A["📝 Topic\n(+ optional theme & instructions)"] --> B["🧭 Planner Agent\nGroq LLM"]
    B -->|"shot list + one\nconsistent example dataset"| C{"For each shot"}
    C --> D["🔊 Narration Agent\nPiper TTS"]
    D -->|"real measured\naudio duration"| E["🎨 Visual Agent\nGroq LLM → Manim"]
    E -->|"rendered clip"| F["🔗 Combine\naudio + video"]
    F -->|"more shots?"| C
    F -->|"all shots done"| G["🎞️ Assembler\nffmpeg concat"]
    G --> H["✅ Final Video"]

    style B fill:#C9A961,color:#211C17
    style D fill:#7C9473,color:#211C17
    style E fill:#B5654A,color:#F1E9DC
    style G fill:#6B8CAE,color:#211C17
```

| Agent | Job | Tech |
|---|---|---|
| **Planner** | Breaks the topic into 3-6 shots with a real pedagogical arc (hook → definition → example → recap). Commits to **one concrete example dataset** up front that every shot must reuse — this is the fix that stopped shots from drifting into unrelated examples or even different topics. | Groq (`openai/gpt-oss-120b`) |
| **Narration** | Synthesizes real speech per shot and measures the *actual* audio duration — used to pace the Visual Agent, not the Planner's word-count guess. | [Piper TTS](https://github.com/OHF-Voice/piper1-gpl) — fully local, zero-cost |
| **Visual** | Generates Manim scene code per shot and renders it, retrying with the real error fed back to the LLM on failure. | Groq LLM → [Manim Community](https://www.manim.community/) |
| **Assembler** | Combines each shot's audio+video, then concatenates every shot into the final file. | Direct `ffmpeg` calls |

### Why narration runs *before* visuals
The Visual Agent paces its Manim animation against Piper's **actual measured** duration, not the Planner's rough word-count estimate — so the video never runs noticeably short or long against the spoken narration.

### The async job flow

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as Next.js Frontend
    participant B as Flask Backend
    participant P as Pipeline (background thread)

    U->>F: Enter topic, pick theme, submit
    F->>B: POST /generate-video
    B->>P: start job in background thread
    B-->>F: 202 { job_id, status: "pending" }
    loop every 5s
        F->>B: GET /video-status/:job_id
        B-->>F: { status: "running" }
    end
    P-->>B: pipeline finishes, updates SQLite
    F->>B: GET /video-status/:job_id
    B-->>F: { status: "completed" }
    U->>F: Click download
    F->>B: GET /download-video/:job_id
    B-->>U: video/mp4
```

A full render takes several minutes, so the backend returns a `job_id` immediately instead of holding the HTTP connection open — the frontend polls for status rather than waiting on one long request.

---

## 🛠️ Tech Stack

| Area | Technologies |
|---|---|
| 🧠 AI Orchestration | LangGraph, LLM Agents |
| ✍️ Content Generation | LLM-based Planning & Narration |
| 🔊 Text-to-Speech | Piper TTS |
| 🎨 Visual Generation | Manim |
| 🎬 Video Processing | FFmpeg |
| ⚙️ Backend | Python, Flask |
| 🗄️ Database | SQLite |
| 🧪 Testing | Pytest |
| 🐳 Deployment | Docker, Gunicorn |
| 🌐 Frontend | HTML, CSS, JavaScript |

## ✨ Key Features

- 🤖 **Multi-Agent AI Pipeline** — Specialized agents handle planning, narration, visual generation, and video assembly.
- 🧠 **LLM-Based Lesson Planning** — Converts a learning topic into structured educational scenes with consistent examples.
- 🔊 **AI-Powered Narration** — Generates narration and converts it into speech using Piper TTS.
- 🎨 **Programmatic Visual Generation** — Generates Manim animations to visually explain concepts.
- ⏱️ **Audio-Aware Animation** — Uses the actual generated narration duration to synchronize visual scenes.
- 🔄 **Automatic Render Retry** — Failed Manim renders are regenerated using the encountered rendering error.
- 🎬 **Automated Video Assembly** — Combines generated visuals and narration into a final educational video using FFmpeg.
- ⚙️ **Asynchronous Job Processing** — Handles long-running video generation without blocking the API request.
- 🗄️ **Persistent Job Tracking** — Stores generation status and job information using SQLite.
- 🧪 **Tested Pipeline Components** — Includes tests for core generation and processing services.

---

## 🧩 Engineering Challenges & Solutions

| Challenge | Solution |
|---|---|
| ⏱️ Narration and animation durations could drift apart | Generated narration first and passed the **actual audio duration** to the Visual Agent for synchronization. |
| 📊 Inconsistent examples across generated scenes | The Planner Agent creates and commits to a consistent example dataset before downstream generation. |
| 🎨 Manim code can fail during rendering | Added an automatic retry mechanism that feeds the rendering error back to the Visual Agent for regeneration. |
| 🎬 Video processing complexity | Used direct **FFmpeg** commands for reliable video/audio concatenation. |
| ⚙️ Long-running generation requests | Implemented asynchronous job processing so video generation doesn't block the API request. |
| 💾 Tracking long-running jobs | Added SQLite-based persistent job status and metadata. |
| 🐳 Limited deployment resources | Documented the memory constraints encountered during Manim rendering and provided a Docker-based deployment setup. |


## 🚀 Setup

### Backend
```bash
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # add your GROQ_API_KEY
python app.py
```
Requires `ffmpeg` and Manim's system dependencies (Cairo, Pango) on PATH. On Windows, make sure your virtual environment is active in *every* terminal — Manim and ffmpeg both need to resolve from inside it.

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Open `http://localhost:3000`. Start the backend first.

### Or run the whole backend via Docker (recommended — matches the deploy environment exactly)
```bash
cd backend
docker build -t study-video-agent .
docker run -p 5000:5000 --env-file .env study-video-agent
```

---

## 📡 API Endpoints

| Endpoint                   | Method | Purpose                                               |
| -------------------------- | ------ | ----------------------------------------------------- |
| `/generate-video`          | `POST` | Starts a video generation job and returns a `job_id`. |
| `/video-status/<job_id>`   | `GET`  | Tracks the current generation status.                 |
| `/download-video/<job_id>` | `GET`  | Downloads the generated `.mp4` after completion.      |

### Example Workflow

```text
POST /generate-video
        ↓
     job_id
        ↓
GET /video-status/<job_id>
        ↓
pending → running → completed
        ↓
GET /download-video/<job_id>
        ↓
     🎬 video.mp4
```

## 🏗️ Design Decisions

- **ffmpeg over MoviePy** for final assembly — MoviePy silently dropped audio during multi-clip concatenation and crashed reading frames near a video's end during development. Direct `ffmpeg` subprocess calls replaced it entirely.
- **SQLite over an in-memory dict** for job tracking — a production WSGI server can run multiple worker processes with separate memory; SQLite is a shared file every worker can read.
- **Sequential pipeline over dynamic agent routing** — every request needs the same fixed Plan → Narrate+Visualize → Assemble sequence, so there's no LLM decision about *which* agent to call next. A simpler, equally legitimate multi-agent pattern for a workflow that doesn't vary.
- **One gunicorn worker, deliberately** — background threads + SQLite status tracking only stay correct with a single process; more workers would split job state across processes that can't see each other's in-flight threads.

---

## 🐞 Known Limitations

This was a first project building a code-generating multi-agent pipeline, and testing surfaced real, worth-documenting failure modes rather than hiding them:

- **Occasional visual rendering issues** — since the retry loop only verifies a Manim render *succeeds*, not that it *looks* correct, some shots have shipped with overlapping text (when a value updates multiple times in one shot), near-invisible low-contrast text, content clipped outside the frame, or disproportionately sized highlight boxes. Each was found, root-caused, and addressed with more explicit rendering rules as testing uncovered it — several are meaningfully improved from earlier versions, but a fully code-generating visual pipeline can't yet guarantee every render is visually perfect the way a schema check guarantees valid JSON. This is an open problem for this class of system generally.
- **No production-grade job recovery** — if the process running a job's background thread crashes mid-render, that job is permanently stuck at `running`. A real task queue (Celery/RQ) would fix this; threading + SQLite was a deliberate, documented tradeoff for this project's scope.
- **Text-only input** — PDF/document upload is planned but not built.
- **Backend not publicly deployed** — see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 🗺️ Roadmap

- [ ] PDF/document upload as an alternative to a typed topic
- [ ] Further harden the Visual Agent prompt against remaining overlap/positioning edge cases
- [ ] Production job queue (Celery/RQ) for crash recovery
- [ ] Backend deployment on a tier with sufficient memory

---

## 📄 License

MIT
