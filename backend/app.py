"""
app.py
"""

import re
import threading
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from job_service import init_db, create_job, update_job, get_job
from orchestrator import run_pipeline

app = Flask(__name__)

# Allows the Next.js frontend to call this API. Vercel gives every
# deployment of the same project several valid URLs -- a clean production
# domain AND team/project-scoped variants with random hashes (e.g.
# https://ai-study-video-generator-ptdfzp7xm-heena-aim124-5180s-projects.vercel.app)
# -- all pointing at the same live site. Hardcoding just the clean domain
# missed the scoped variant actually being used in the browser, so this
# matches ANY subdomain under the project's Vercel namespace via regex,
# not just one exact string.
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ai-study-video-generator.vercel.app",
    re.compile(r"^https://ai-study-video-generator.*\.vercel\.app$"),
])

init_db()

MAX_INSTRUCTIONS_LENGTH = 500  # keep prompts bounded -- this gets appended to two separate LLM calls per shot


def _run_job_in_background(job_id: str, topic: str, theme: str, instructions: str):
    """
    Runs the full multi-agent pipeline in a background thread so the
    original HTTP request can return immediately with a job_id, instead
    of the client hanging for several minutes waiting for a synchronous
    response (and likely hitting a timeout regardless).
    """
    update_job(job_id, status="running")
    try:
        final_video_path = run_pipeline(topic, theme, instructions)
        update_job(job_id, status="completed", video_path=final_video_path)
    except Exception as e:
        update_job(job_id, status="failed", error=str(e))


@app.route("/generate-video", methods=["POST"])
def generate_video():
    data = request.get_json()

    if not data or "topic" not in data or not data["topic"].strip():
        return jsonify({"error": "Please provide a non-empty 'topic' field"}), 400

    topic = data["topic"].strip()

    theme = data.get("theme", "light")
    if theme not in ("light", "dark"):
        return jsonify({"error": "theme must be 'light' or 'dark'"}), 400

    instructions = (data.get("instructions") or "").strip()
    if len(instructions) > MAX_INSTRUCTIONS_LENGTH:
        return jsonify({
            "error": f"instructions must be under {MAX_INSTRUCTIONS_LENGTH} characters"
        }), 400

    job_id = create_job(topic)

    thread = threading.Thread(
        target=_run_job_in_background,
        args=(job_id, topic, theme, instructions),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id, "status": "pending"}), 202


@app.route("/video-status/<job_id>", methods=["GET"])
def video_status(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    response = {"job_id": job["id"], "topic": job["topic"], "status": job["status"]}
    if job["status"] == "failed":
        response["error"] = job["error"]
    return jsonify(response)


@app.route("/download-video/<job_id>", methods=["GET"])
def download_video(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job["status"] != "completed":
        return jsonify({"error": f"Job is not complete yet (status: {job['status']})"}), 400

    return send_file(job["video_path"], mimetype="video/mp4", as_attachment=True)


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Study-Material-to-Video Agent backend is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True, use_reloader=False)
