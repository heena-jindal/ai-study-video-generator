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
    throw new ApiError(
      "Can't reach the backend right now. Make sure it's running and try again."
    );
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
    throw new ApiError("Lost connection to the backend while checking status.");
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
