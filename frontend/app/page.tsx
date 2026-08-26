"use client";

import { useState } from "react";
import { useVideoJob } from "@/lib/useVideoJob";
import { StatusBadge } from "@/components/StatusBadge";
import { ThemeToggle } from "@/components/ThemeToggle";
import {
  TapeStrip,
  SketchyUnderline,
  DoodleArrow,
  Starburst,
  RecordingReel,
  CheckmarkBadgeDoodle,
} from "@/components/Doodles";

export default function Home() {
  const [topicInput, setTopicInput] = useState("");
  const [videoTheme, setVideoTheme] = useState<"light" | "dark">("light");
  const [instructionsInput, setInstructionsInput] = useState("");
  const { status, topic, errorMessage, submit, reset, downloadHref } =
    useVideoJob();

  const isBusy = status === "pending" || status === "running";
  const showForm = status === "idle";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = topicInput.trim();
    if (!trimmed) return;
    submit(trimmed, videoTheme, instructionsInput.trim());
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="relative w-full max-w-md rotate-[-0.6deg] rounded-md bg-paper p-7 shadow-polaroid dark:bg-night-paper">
        <TapeStrip color="tape-mustard" rotate={-7} className="-left-4 -top-4" />
        <TapeStrip color="tape-sage" rotate={6} className="-right-5 -top-3" />

        <div className="absolute -top-3 right-6">
          <ThemeToggle />
        </div>

        {/* Header */}
        <header className="mb-6 text-center">
          <h1 className="font-hand text-4xl font-bold leading-none text-ink dark:text-night-ink">
            study &rarr; video
          </h1>
          <SketchyUnderline className="mx-auto mt-1 h-3 w-40" />
          <p className="mt-3 font-type text-[11px] leading-relaxed text-ink-soft dark:text-night-ink-soft">
            give it a topic, get back a narrated explainer
          </p>
        </header>

        {/* Idle: the form */}
        {showForm && (
          <form onSubmit={handleSubmit} className="relative">
            <label
              htmlFor="topic"
              className="mb-1 block font-hand text-xl text-ink dark:text-night-ink"
            >
              today&apos;s topic is...
            </label>
            <input
              id="topic"
              type="text"
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              placeholder="e.g. binary search"
              className="w-full rounded border-2 border-dashed border-ink/30 bg-cream px-4 py-3 font-body text-ink placeholder:text-ink-soft/60 focus:border-tape-slate focus:outline-none focus:ring-2 focus:ring-tape-slate/30 dark:border-night-ink/25 dark:bg-night-bg dark:text-night-ink dark:placeholder:text-night-ink-soft/50"
            />

            <DoodleArrow className="pointer-events-none absolute -right-2 top-11 h-14 w-14 rotate-[-15deg]" />

            {/* Video theme picker -- this is the actual look of the
                rendered Manim scenes, separate from the site's own
                light/dark toggle above. */}
            <fieldset className="mt-5">
              <legend className="mb-1.5 font-hand text-lg text-ink dark:text-night-ink">
                the video itself should look...
              </legend>
              <div className="flex gap-2">
                {(["light", "dark"] as const).map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setVideoTheme(option)}
                    className={`flex-1 rounded-sm border-2 py-2 font-body text-sm capitalize transition-colors ${
                      videoTheme === option
                        ? "border-tape-slate bg-tape-slate/15 font-bold text-ink dark:border-tapeNight-slate dark:bg-tapeNight-slate/20 dark:text-night-ink"
                        : "border-ink/15 text-ink-soft dark:border-night-ink/15 dark:text-night-ink-soft"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </fieldset>

            <fieldset className="mt-5">
              <legend className="mb-1.5 font-hand text-lg text-ink dark:text-night-ink">
                anything specific? <span className="font-type text-[10px] normal-case text-ink-soft dark:text-night-ink-soft">(optional)</span>
              </legend>
              <textarea
                value={instructionsInput}
                onChange={(e) => setInstructionsInput(e.target.value)}
                maxLength={500}
                rows={3}
                placeholder="e.g. keep it beginner-friendly, focus more on time complexity, avoid highlight boxes..."
                className="w-full resize-none rounded border-2 border-dashed border-ink/20 bg-cream/60 px-3 py-2 font-body text-sm text-ink placeholder:text-ink-soft/50 focus:border-tape-slate focus:outline-none focus:ring-2 focus:ring-tape-slate/30 dark:border-night-ink/20 dark:bg-night-bg/40 dark:text-night-ink dark:placeholder:text-night-ink-soft/40"
              />
              <p className="mt-1 text-right font-type text-[9px] text-ink-soft/70 dark:text-night-ink-soft/60">
                {instructionsInput.length}/500 -- leave blank and it&apos;ll use its own judgment
              </p>
            </fieldset>

            <button
              type="submit"
              disabled={!topicInput.trim()}
              className="group relative mt-5 w-full rounded-sm bg-ink py-3 font-hand text-xl text-cream shadow-tape transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-night-ink dark:text-night-bg"
            >
              make the video
              <Starburst className="absolute -right-3 -top-3 h-8 w-8 opacity-0 transition-opacity group-hover:opacity-100" />
            </button>
          </form>
        )}

        {/* Pending / running / completed / failed: the developing polaroid */}
        {!showForm && (
          <div className="animate-pop-in">
            <div className="mb-4 flex items-center justify-between">
              <StatusBadge status={status as any} />
              <span className="font-type text-[10px] text-ink-soft dark:text-night-ink-soft">
                #{topic.replace(/\s+/g, "-").toLowerCase()}
              </span>
            </div>

            <div className="flex aspect-square w-full flex-col items-center justify-center rounded border border-ink/10 bg-cream/70 dark:border-night-ink/10 dark:bg-night-bg/60">
              {isBusy && (
                <>
                  <RecordingReel className="h-20 w-20 animate-spin-slow" />
                  <p className="mt-4 px-6 text-center font-hand text-lg text-ink-soft dark:text-night-ink-soft">
                    still sketching out &ldquo;{topic}&rdquo;... this takes a
                    few minutes
                  </p>
                </>
              )}

              {status === "completed" && (
                <>
                  <CheckmarkBadgeDoodle className="h-16 w-16" />
                  <p className="mt-4 px-6 text-center font-hand text-lg text-ink dark:text-night-ink">
                    &ldquo;{topic}&rdquo; is ready to watch
                  </p>
                </>
              )}

              {status === "failed" && (
                <>
                  <p className="font-hand text-5xl text-tape-rose dark:text-tapeNight-rose">
                    &times;
                  </p>
                  <p className="mt-3 px-6 text-center font-type text-xs leading-relaxed text-ink-soft dark:text-night-ink-soft">
                    {errorMessage || "Something broke while making this one."}
                  </p>
                </>
              )}
            </div>

            {status === "completed" && downloadHref && (
              <a
                href={downloadHref}
                className="mt-5 block w-full rounded-sm bg-tape-sage py-3 text-center font-hand text-xl text-cream shadow-tape transition-transform hover:-translate-y-0.5 dark:bg-tapeNight-sage dark:text-night-ink"
              >
                download the video
              </a>
            )}

            {(status === "completed" || status === "failed") && (
              <button
                onClick={() => {
                  reset();
                  setTopicInput("");
                }}
                className="mt-3 w-full py-2 text-center font-type text-[11px] text-ink-soft underline decoration-dotted underline-offset-4 hover:text-ink dark:text-night-ink-soft dark:hover:text-night-ink"
              >
                start another one
              </button>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
