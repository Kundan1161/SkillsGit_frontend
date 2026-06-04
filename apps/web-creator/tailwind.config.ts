import type { Config } from "tailwindcss";

/**
 * Tailwind v4 still respects a config for `content` globs and theme extensions
 * when used via `@tailwindcss/postcss`. The CSS-side tokens live in
 * `packages/ui/src/styles/tokens.css` (imported from `app/layout.tsx`).
 *
 * Mirrors the marketplace config for token consistency across apps.
 */
const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "../../packages/ui/src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        "bg-muted": "var(--color-bg-muted)",
        "bg-raised": "var(--color-bg-raised)",
        border: "var(--color-border)",
        fg: "var(--color-fg)",
        "fg-muted": "var(--color-fg-muted)",
        "fg-subtle": "var(--color-fg-subtle)",
        brand: {
          50:  "var(--color-brand-50)",
          100: "var(--color-brand-100)",
          400: "var(--color-brand-400)",
          500: "var(--color-brand-500)",
          600: "var(--color-brand-600)",
          700: "var(--color-brand-700)",
          900: "var(--color-brand-900)",
          DEFAULT: "var(--color-brand-500)",
        },
        accent: {
          400: "var(--color-accent-400)",
          500: "var(--color-accent-500)",
          DEFAULT: "var(--color-accent-500)",
        },
        success: "var(--color-success)",
        warning: "var(--color-warning)",
        danger: "var(--color-danger)",
        info: "var(--color-info)",
        price: "var(--color-price)",
        rating: "var(--color-rating)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
      },
      fontFamily: {
        sans: ["var(--font-display)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      transitionDuration: {
        DEFAULT: "150ms",
      },
    },
  },
  plugins: [],
};

export default config;
