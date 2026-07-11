/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1120",
        panel: "#111c33",
        panel2: "#16223f",
        accent: "#38bdf8",
        accent2: "#22d3ee",
        good: "#34d399",
        warn: "#fbbf24",
        bad: "#f87171",
        muted: "#94a3b8",
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      boxShadow: { glow: "0 0 0 1px rgba(56,189,248,.25), 0 8px 30px rgba(2,8,23,.6)" },
    },
  },
  plugins: [],
};
