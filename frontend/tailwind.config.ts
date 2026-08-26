import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: "#FDFBF7",
        paper: "#FFFEF9",
        ink: "#3D3229",
        "ink-soft": "#6B5F52",
        tape: {
          mustard: "#C9A961",
          sage: "#7C9473",
          rose: "#B5654A",
          slate: "#6B8CAE",
        },
        // Dark mode -- "journal by lamplight," not an inverted palette.
        // Warm charcoal leather instead of pure black, chalk-cream ink,
        // tape colors desaturated so they don't glow against the dark.
        night: {
          bg: "#211C17",
          paper: "#2B241E",
          ink: "#F1E9DC",
          "ink-soft": "#B8AC9A",
        },
        tapeNight: {
          mustard: "#B08D4F",
          sage: "#6C8563",
          rose: "#A15A42",
          slate: "#5E7C99",
        },
      },
      fontFamily: {
        hand: ["var(--font-caveat)", "cursive"],
        body: ["var(--font-karla)", "sans-serif"],
        type: ["var(--font-special-elite)", "monospace"],
      },
      boxShadow: {
        polaroid: "0 4px 6px rgba(61, 50, 41, 0.08), 0 10px 20px rgba(61, 50, 41, 0.1)",
        tape: "0 2px 4px rgba(61, 50, 41, 0.15)",
      },
    },
  },
  plugins: [],
};
export default config;
