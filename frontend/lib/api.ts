/**
 * lib/api.ts
 *
 * All backend communication lives here, separate from UI components --
 * so the polling logic, error shapes, and endpoint URLs can change
 * without touching any JSX.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export type JobStatus = "pending" | "running" | "completed" | "failed";

export interface JobStatusResponse {
  job_id: string;
  topic: string;
  status: JobStatus;
  error?: string;
}

export class ApiError extends Error {}

// Shown when the fetch itself fails (network/CORS/unreachable) -- this
// covers the deployed case where the backend isn't publicly hosted
// (see DEPLOYMENT.md). A generic "can't reach the backend" message reads
// as a bug; this one explains the actual, documented reason and points
// people toward proof the pipeline genuinely works.
const BACKEND_UNREACHABLE_MESSAGE =
  "This project's backend isn't running right now — it needs more memory " +
  "than most free hosting tiers provide (see DEPLOYMENT.md for details). " +
  "Check out the demo videos in the README, or clone the repo and run it " +
  "locally to see the full pipeline work end to end.";

export async function startVideoJob(
  topic: string,
  theme: "light" | "dark" = "light",
  instructions: string = ""
): Promise<string> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/generate-video`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, theme, instructions }),
    });
  } catch {
    throw new ApiError(BACKEND_UNREACHABLE_MESSAGE);
  }

  const data = await safeJson(res);

  if (!res.ok) {
    throw new ApiError(data?.error || "Couldn't start the job. Try again.");
  }

  return data.job_id as string;
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/video-status/${jobId}`);
  } catch {
    throw new ApiError(BACKEND_UNREACHABLE_MESSAGE);
  }

  const data = await safeJson(res);

  if (!res.ok) {
    throw new ApiError(data?.error || "Couldn't check job status.");
  }

  return data as JobStatusResponse;
}

export function downloadUrl(jobId: string): string {
  return `${API_BASE}/download-video/${jobId}`;
}

async function safeJson(res: Response): Promise<any> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}
