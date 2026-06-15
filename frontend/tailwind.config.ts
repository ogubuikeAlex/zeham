import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./hooks/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#171717",
        body: "#4d4d4d",
        mute: "#888888",
        hairline: "#ebebeb",
        "hairline-strong": "#a1a1a1",
        canvas: "#ffffff",
        "canvas-soft": "#fafafa",
        "canvas-soft-2": "#f5f5f5",
        link: "#0070f3",
        error: "#ee0000",
        warning: "#f5a623",
        "warning-deep": "#ab570a",
        cyan: "#50e3c2",
        violet: "#7928ca",
        pink: "#ff0080"
      },
      boxShadow: {
        card: "0px 1px 1px #00000005, 0px 2px 2px #0000000a, inset 0 0 0 1px #00000014",
        float: "0px 2px 2px #0000000a, 0px 8px 16px -4px #0000000a, inset 0 0 0 1px #00000014"
      },
      fontFamily: {
        sans: ["Inter", "Geist", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Geist Mono", "ui-monospace", "SFMono-Regular", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
