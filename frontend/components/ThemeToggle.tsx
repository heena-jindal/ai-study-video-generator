"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  // Starts null so we don't render a guess before we've read the real
  // stored/system preference -- avoids a flash of the wrong icon.
  const [isDark, setIsDark] = useState<boolean | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const prefersDark =
      stored === "dark" ||
      (!stored && window.matchMedia("(prefers-color-scheme: dark)").matches);
    setIsDark(prefersDark);
    document.documentElement.classList.toggle("dark", prefersDark);
  }, []);

  function toggle() {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  }

  if (isDark === null) return <div className="h-9 w-9" />; // placeholder, no flash

  return (
    <button
      onClick={toggle}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className="flex h-9 w-9 items-center justify-center rounded-full border border-dashed border-ink/25 text-ink transition-transform hover:-rotate-6 dark:border-night-ink/25 dark:text-night-ink"
    >
      {isDark ? (
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden="true">
          <path
            d="M18 13.5C16.9 15.9 14.4 17.5 11.6 17.3C8 17 5.2 13.9 5.3 10.2C5.4 7.5 7 5.2 9.2 4C7 5 5.5 7.4 5.6 10.1C5.7 13.6 8.6 16.4 12.1 16.4C14.6 16.4 16.8 15 18 13.5Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.6" />
          {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
            <line
              key={deg}
              x1="12"
              y1="3.2"
              x2="12"
              y2="1"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              transform={`rotate(${deg} 12 12)`}
            />
          ))}
        </svg>
      )}
    </button>
  );
}
