/**
 * components/Doodles.tsx
 *
 * Hand-drawn SVG accents. Each path uses slightly irregular curves
 * (not perfect arcs) so they read as sketched, not vector-perfect --
 * that imperfection is what sells the "pencil on paper" feel.
 */

export function TapeStrip({
  color = "tape-mustard",
  rotate = -4,
  className = "",
}: {
  color?: "tape-mustard" | "tape-sage" | "tape-rose" | "tape-slate";
  rotate?: number;
  className?: string;
}) {
  const classes: Record<string, string> = {
    "tape-mustard": "bg-tape-mustard dark:bg-tapeNight-mustard",
    "tape-sage": "bg-tape-sage dark:bg-tapeNight-sage",
    "tape-rose": "bg-tape-rose dark:bg-tapeNight-rose",
    "tape-slate": "bg-tape-slate dark:bg-tapeNight-slate",
  };
  return (
    <div
      className={`absolute h-6 w-20 opacity-80 shadow-tape ${classes[color]} ${className}`}
      style={{
        transform: `rotate(${rotate}deg)`,
        clipPath: "polygon(2% 15%, 98% 0%, 100% 85%, 3% 100%)",
      }}
      aria-hidden="true"
    />
  );
}

export function SketchyUnderline({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 180 14"
      className={`text-tape-mustard dark:text-tapeNight-mustard ${className}`}
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M2 8.5C34 3 71 2 104 6.5C127 9.5 152 5.5 177 8"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function DoodleArrow({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 90 70"
      className={`text-ink dark:text-night-ink ${className}`}
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M6 6C22 22 34 34 46 48C52 55 56 60 60 63"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
      />
      <path
        d="M40 58C46 61 54 63 62 63C64 56 65 49 65 42"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Starburst({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 60 60"
      className={`text-tape-rose dark:text-tapeNight-rose ${className}`}
      fill="none"
      aria-hidden="true"
    >
      {[0, 30, 60, 90, 120, 150].map((deg) => (
        <line
          key={deg}
          x1="30"
          y1="30"
          x2="30"
          y2="4"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          transform={`rotate(${deg} 30 30)`}
        />
      ))}
      {[15, 45, 75, 105, 135, 165].map((deg) => (
        <line
          key={deg}
          x1="30"
          y1="30"
          x2="30"
          y2="12"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          transform={`rotate(${deg} 30 30)`}
        />
      ))}
    </svg>
  );
}

/** Spinning "film reel" doodle used while a job is running -- the
 * signature element: a polaroid that's still developing. */
export function RecordingReel({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 80 80"
      className={`text-ink dark:text-night-ink ${className}`}
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="40"
        cy="40"
        r="30"
        stroke="currentColor"
        strokeWidth="2"
        strokeDasharray="4 5"
      />
      <circle cx="40" cy="40" r="6" className="fill-tape-rose dark:fill-tapeNight-rose" />
      <circle cx="40" cy="16" r="4" stroke="currentColor" strokeWidth="2" />
      <circle cx="60" cy="50" r="4" stroke="currentColor" strokeWidth="2" />
      <circle cx="20" cy="50" r="4" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

export function CheckmarkBadgeDoodle({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 40 40"
      className={`text-tape-sage dark:text-tapeNight-sage ${className}`}
      fill="none"
      aria-hidden="true"
    >
      <circle cx="20" cy="20" r="17" stroke="currentColor" strokeWidth="2.2" />
      <path
        d="M12 20.5L17.5 26L28.5 14"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
