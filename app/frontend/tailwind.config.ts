import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        track: {
          950: "#050816",
          900: "#0b1022",
          800: "#131a33",
          700: "#1d2643",
        },
        signal: {
          cyan: "#4ad6ff",
          lime: "#c3ff5d",
          amber: "#ffbf69",
          red: "#ff6b6b",
        },
      },
      boxShadow: {
        panel: "0 20px 80px rgba(0, 0, 0, 0.35)",
      },
    },
  },
  plugins: [],
};

export default config;

