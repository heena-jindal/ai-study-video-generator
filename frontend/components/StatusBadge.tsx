import { JobStatus } from "@/lib/api";

const CONFIG: Record<
  JobStatus,
  { label: string; light: string; dark: string }
> = {
  pending: {
    label: "QUEUED",
    light: "bg-[#EDE6D6] text-[#6B5F52]",
    dark: "dark:bg-[#3A322A] dark:text-[#B8AC9A]",
  },
  running: {
    label: "IN PROGRESS",
    light: "bg-tape-mustard text-ink",
    dark: "dark:bg-tapeNight-mustard dark:text-night-bg",
  },
  completed: {
    label: "DONE",
    light: "bg-tape-sage text-cream",
    dark: "dark:bg-tapeNight-sage dark:text-night-ink",
  },
  failed: {
    label: "STUCK",
    light: "bg-tape-rose text-cream",
    dark: "dark:bg-tapeNight-rose dark:text-night-ink",
  },
};

export function StatusBadge({ status }: { status: JobStatus }) {
  const cfg = CONFIG[status];
  return (
    <span
      className={`inline-block rotate-[-1.5deg] rounded-sm px-3 py-1 font-body text-xs font-bold tracking-[0.15em] shadow-tape ${cfg.light} ${cfg.dark}`}
    >
      {cfg.label}
    </span>
  );
}
