# Deployment

## Current Status

| Component | Status | URL |
|---|---|---|
| **Frontend** | ✅ Live on Vercel | *your Vercel URL here* |
| **Backend** | ⚠️ Not publicly deployed | runs locally / via Docker |

## Why the backend isn't deployed

The backend was deployed to Render and **did work** — health checks passed, CORS was configured correctly, and jobs started successfully. It reliably failed partway through actual video generation, though, and the cause was confirmed rather than assumed.

### The evidence

Render's logs showed the entire gunicorn process silently restarting mid-job, with no graceful shutdown message of any kind — no `Handling signal: term`, no `Worker exiting`, just a fresh `Starting gunicorn...` boot roughly 6-7 minutes after the previous one started:

```
[13:47:03] Starting gunicorn 22.0.0 ... Booting worker with pid: 7
[13:53:54] Starting gunicorn 22.0.0 ... Booting worker with pid: 8
```

That silence is the signature of a **hard kill** — something outside the application (the OS's out-of-memory killer) terminated the whole container without giving it a chance to log its own death. This happened consistently, on repeated attempts, always roughly mid-render.

### Root cause

Render's free tier provides **512MB RAM**. This pipeline runs Flask + gunicorn + LangGraph + the Groq client + an active Manim rendering subprocess simultaneously — Manim's rendering process alone can spike well past what's left after the rest of the stack's baseline usage. This is a genuine resource ceiling, not a code bug: the same backend runs correctly locally and in local Docker testing, where more memory is available.

Google Cloud's free tier was also attempted and did not respond during setup, for reasons not fully diagnosed before deciding to timebox this and document the constraint rather than continue chasing free-tier limits.

## How to actually deploy it (if you have access to a higher-memory tier)

The backend is fully deploy-ready — `backend/Dockerfile` is complete and tested. To deploy on Render (or any Docker-based host) successfully:

1. Use an instance type with **at least 2GB RAM** (Render's paid "Starter" tier or above)
2. Set the `GROQ_API_KEY` environment variable
3. Deploy `backend/` with Docker as the environment (see main [README](README.md#setup) for the Docker build/run commands)
4. Once live, add the deployed URL to the frontend's `NEXT_PUBLIC_API_URL` environment variable on Vercel, and to the `CORS(origins=[...])` list in `backend/app.py`

## Running the full system yourself (recommended way to evaluate this project)

Since the backend isn't publicly hosted, the most reliable way to see the complete pipeline work is locally:

```bash
# Terminal 1
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # add your GROQ_API_KEY
python app.py

# Terminal 2
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Then open `http://localhost:3000` — the full pipeline runs exactly as demonstrated in the [demo video](README.md#-demo).
