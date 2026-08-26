# Study-Material-to-Video Agent

An agentic AI system that turns a topic into a complete explainer video — narration, synchronized visuals, and structure — with minimal human editing required.

Given a topic like *"Two Sum using a hash map"*, the system plans a coherent shot-by-shot teaching sequence, generates real narration audio, generates and renders animated visuals for each shot, and assembles everything into one final video — no manual scripting, recording, or editing.

## Demo

https://github.com/user-attachments/assets/PLACEHOLDER — *(replace with a link/GIF of your best render once you upload one to the repo)*

## Architecture

This is a **true multi-agent pipeline** built with LangGraph — not a single agent with tools, but four specialist agents chained in a fixed sequence, each handling a fundamentally different kind of work:

```
Topic ─▶ Planner ─▶ [Narration ─▶ Visual ─▶ Combine] × N shots ─▶ Assembler ─▶ Final Video
```

| Agent | Responsibility | Tech |
|---|---|---|
| **Planner** | Breaks the topic into 3-6 shots with a clear pedagogical arc (hook → definition → example → recap). Commits to ONE concrete example dataset that every shot must reuse, to keep the video internally consistent. | Groq (`openai/gpt-oss-120b`), structured JSON output |
| **Narration** | Synthesizes real speech per shot and measures its *actual* duration — used to pace the visuals, not the Planner's word-count estimate. | [Piper TTS](https://github.com/OHF-Voice/piper1-gpl) — fully local, no API key, zero cost |
| **Visual** | Generates Manim scene code per shot and actually renders it, with a retry loop that feeds the real render error back to the LLM on failure. | Groq LLM → [Manim Community](https://www.manim.community/) |
| **Assembler** | Combines each shot's audio+video, then concatenates all shots into the final file. | Direct `ffmpeg` calls (see [Design Decisions](#design-decisions)) |

The **frontend** (Next.js) submits a topic to an async job API and polls for status — a full render takes several minutes, so the backend returns a `job_id` immediately rather than holding the HTTP request open.

## Features

- **Light/dark theme** — both for the website itself and independently for the *generated video's* visual style (background/text colors)
- **Optional custom instructions** — steer tone, emphasis, or visual style per video (e.g. *"keep it beginner-friendly"*, *"focus more on time complexity"*) without changing code
- **Consistent example data** — the Planner commits to one concrete dataset (e.g. a specific array) up front, and every shot is required to reuse it, preventing shots from drifting into unrelated examples or topics
- Async job queue with status polling (`pending` → `running` → `completed`/`failed`)

## Tech Stack

**Backend**: Flask, LangGraph, Groq, Manim, Piper TTS, ffmpeg, SQLite (job tracking)
**Frontend**: Next.js, TypeScript, Tailwind CSS

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or omit the flag outside a managed environment
cp .env.example .env   # add your GROQ_API_KEY
python app.py
```

Requires `ffmpeg` and Manim's system dependencies (Cairo, Pango) available on PATH. On Windows, make sure your virtual environment is activated in *every* terminal you use — both `manim` and `ffmpeg` must resolve from inside the venv, not just be installed globally.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # points at your backend, defaults to localhost:5000
npm run dev
```

Open `http://localhost:3000`. The backend must be running first.

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/generate-video` | POST | Start a job. Body: `{ topic, theme, instructions? }`. Returns `{ job_id, status }` immediately (202). |
| `/video-status/<job_id>` | GET | Poll job status: `pending` / `running` / `completed` / `failed` (+ `error` if failed). |
| `/download-video/<job_id>` | GET | Download the finished `.mp4` once `status` is `completed`. |

## Design Decisions

- **ffmpeg over MoviePy for final assembly** — MoviePy produced two separate, hard-to-debug reliability issues during development (audio silently dropping during concatenation of later clips; frame-read crashes near a video's end). Direct `ffmpeg` subprocess calls replaced it entirely — more predictable, and one fewer dependency.
- **SQLite over an in-memory dict for job tracking** — a production WSGI server can run multiple worker processes with separate memory; an in-memory dict wouldn't be visible across them. SQLite is a shared file on disk, readable from any worker.
- **Sequential pipeline over dynamic agent routing** — every request needs the same fixed sequence (Plan → Narrate+Visualize each shot → Assemble), so there's no decision for an LLM to make about *which* agent to call next. This is a legitimate, simpler alternative to dynamic tool-routing agents, appropriate when the workflow itself doesn't vary.
- **Narration before Visual, per shot** — the Visual Agent paces its animation against the *actual measured* audio duration from Piper, not the Planner's ~150wpm estimate, so visuals don't run short or long against the narration.

## Known Limitations

This was my first project building a multi-agent, code-generating pipeline, and testing surfaced real failure modes worth documenting honestly rather than hiding:

**Occasional visual rendering issues.** Because the Visual Agent asks an LLM to generate Manim code and the retry loop only verifies that the code *renders without crashing* — not that the result *looks* correct — some shots have shipped with:
- Text elements overlapping when a value updates multiple times within one shot (e.g. a growing hash map or list) — largely fixed by explicit prompt rules requiring `Transform`/`FadeOut`-before-`FadeIn` discipline, but not eliminated in every case
- Occasional near-invisible text where the generated color was too close to the background color
- Occasional content positioned partially outside the visible frame
- Occasional disproportionately sized highlight/bounding elements

Each of these was found, root-caused, and addressed with more explicit rendering constraints in the Visual Agent's prompt as testing uncovered them — several are meaningfully improved from earlier versions — but a fully code-generating visual pipeline can't yet guarantee every render is visually perfect the way a schema check can guarantee valid JSON. This is an open problem for this class of system generally, not a fixed bug: "renders successfully" and "looks correct" are different, harder-to-verify properties.

**No production-grade job recovery.** If the worker process running a job's background thread crashes or restarts mid-render, that job is permanently stuck at `running` — there's no automatic recovery. A production system would use a real task queue (Celery, RQ) with proper worker restart handling. For this project's scope, threading + SQLite status tracking was a deliberate, documented tradeoff, not an oversight.

**Text-only input.** The system currently only accepts a topic string. PDF/document upload (extracting and summarizing real source material instead of having the Planner invent an example) is planned but not yet built.

**Groq's daily token limits** are easy to hit during active development/testing (each full pipeline run costs one Planner call + one Visual call per shot, with up to 3 retries each on render failure).

## Roadmap

- [ ] PDF/document upload as an alternative to a typed topic
- [ ] Further harden Visual Agent prompt against remaining overlap/positioning edge cases
- [ ] Production job queue (Celery/RQ) for crash recovery
- [ ] Deploy: backend on Render (Docker), frontend on Vercel

## License

MIT (or your preferred license)
