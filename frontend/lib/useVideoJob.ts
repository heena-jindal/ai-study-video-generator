/**
 * lib/useVideoJob.ts
 *
 * Encapsulates the full job lifecycle: submit -> poll -> resolve.
 * Keeping this out of the page component makes the polling interval
 * easy to reason about and guarantees cleanup on unmount.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, JobStatus, downloadUrl, getJobStatus, startVideoJob } from "./api";

const POLL_INTERVAL_MS = 5000;

interface VideoJobState {
  status: JobStatus | "idle";
  jobId: string | null;
  topic: string;
  errorMessage: string | null;
}

export function useVideoJob() {
  const [state, setState] = useState<VideoJobState>({
    status: "idle",
    jobId: null,
    topic: "",
    errorMessage: null,
  });

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => clearPolling, [clearPolling]);

  const submit = useCallback(
    async (topic: string, theme: "light" | "dark" = "light", instructions: string = "") => {
      clearPolling();
      setState({ status: "pending", jobId: null, topic, errorMessage: null });

      try {
        const jobId = await startVideoJob(topic, theme, instructions);
        setState((s) => ({ ...s, jobId, status: "pending" }));

        intervalRef.current = setInterval(async () => {
          try {
            const result = await getJobStatus(jobId);
            setState((s) => ({
              ...s,
              status: result.status,
              errorMessage: result.error || null,
            }));
            if (result.status === "completed" || result.status === "failed") {
              clearPolling();
            }
          } catch (err) {
            clearPolling();
            setState((s) => ({
              ...s,
              status: "failed",
              errorMessage:
                err instanceof ApiError ? err.message : "Lost track of the job.",
            }));
          }
        }, POLL_INTERVAL_MS);
      } catch (err) {
        setState((s) => ({
          ...s,
          status: "failed",
          errorMessage:
            err instanceof ApiError ? err.message : "Couldn't start the job.",
        }));
      }
    },
    [clearPolling]
  );

  const reset = useCallback(() => {
    clearPolling();
    setState({ status: "idle", jobId: null, topic: "", errorMessage: null });
  }, [clearPolling]);

  return {
    ...state,
    submit,
    reset,
    downloadHref: state.jobId ? downloadUrl(state.jobId) : null,
  };
}
