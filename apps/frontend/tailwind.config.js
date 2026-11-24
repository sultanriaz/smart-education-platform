/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem" }]
      },
      colors: {
        bg: "rgb(var(--rgb-bg) / <alpha-value>)",
        background: "rgb(var(--rgb-bg) / <alpha-value>)",
        surface: "rgb(var(--rgb-bg) / <alpha-value>)",
        panel: "rgb(var(--rgb-card) / <alpha-value>)",
        card: "rgb(var(--rgb-card) / <alpha-value>)",
        subtle: "rgb(var(--rgb-subtle) / <alpha-value>)",
        ink: "rgb(var(--rgb-text) / <alpha-value>)",
        text: "rgb(var(--rgb-text) / <alpha-value>)",
        foreground: "rgb(var(--rgb-text) / <alpha-value>)",
        muted: {
          DEFAULT: "rgb(var(--rgb-muted) / <alpha-value>)",
          foreground: "rgb(var(--rgb-muted) / <alpha-value>)"
        },
        line: "rgb(var(--rgb-border) / <alpha-value>)",
        border: "rgb(var(--rgb-border) / <alpha-value>)",
        primary: {
          DEFAULT: "rgb(var(--rgb-primary) / <alpha-value>)",
          hover: "rgb(var(--rgb-primary-hover) / <alpha-value>)",
          fg: "rgb(var(--rgb-primary-fg) / <alpha-value>)",
          soft: "rgb(var(--rgb-primary-soft) / <alpha-value>)",
          ink: "rgb(var(--rgb-primary-ink) / <alpha-value>)",
          50: "rgb(var(--rgb-primary-soft) / <alpha-value>)",
          100: "rgb(var(--rgb-primary-soft) / <alpha-value>)",
          200: "rgb(var(--rgb-border) / <alpha-value>)",
          600: "rgb(var(--rgb-primary) / <alpha-value>)"
        },
        "on-primary": "rgb(var(--rgb-primary-fg) / <alpha-value>)",
        secondary: {
          DEFAULT: "rgb(var(--rgb-secondary) / <alpha-value>)",
          fg: "rgb(var(--rgb-secondary-fg) / <alpha-value>)",
          soft: "rgb(var(--rgb-secondary-soft) / <alpha-value>)",
          ink: "rgb(var(--rgb-secondary-ink) / <alpha-value>)"
        },
        accent: {
          DEFAULT: "rgb(var(--rgb-accent) / <alpha-value>)",
          fg: "rgb(var(--rgb-accent-fg) / <alpha-value>)",
          soft: "rgb(var(--rgb-accent-soft) / <alpha-value>)",
          ink: "rgb(var(--rgb-accent-ink) / <alpha-value>)"
        },
        brand: {
          50: "rgb(var(--rgb-primary-soft) / <alpha-value>)",
          100: "rgb(var(--rgb-primary-soft) / <alpha-value>)",
          200: "rgb(var(--rgb-border) / <alpha-value>)",
          300: "rgb(var(--rgb-primary-ink) / <alpha-value>)",
          400: "rgb(var(--rgb-primary-ink) / <alpha-value>)",
          500: "rgb(var(--rgb-primary) / <alpha-value>)",
          600: "rgb(var(--rgb-primary) / <alpha-value>)",
          700: "rgb(var(--rgb-primary-ink) / <alpha-value>)",
          800: "rgb(var(--rgb-primary-ink) / <alpha-value>)",
          900: "rgb(var(--rgb-primary-ink) / <alpha-value>)"
        },
        success: {
          DEFAULT: "rgb(var(--rgb-success) / <alpha-value>)",
          fg: "rgb(var(--rgb-success-fg) / <alpha-value>)",
          soft: "rgb(var(--rgb-success-soft) / <alpha-value>)",
          ink: "rgb(var(--rgb-success-ink) / <alpha-value>)"
        },
        warning: {
          DEFAULT: "rgb(var(--rgb-warning) / <alpha-value>)",
          fg: "rgb(var(--rgb-warning-fg) / <alpha-value>)",
          soft: "rgb(var(--rgb-warning-soft) / <alpha-value>)",
          ink: "rgb(var(--rgb-warning-ink) / <alpha-value>)"
        },
        danger: {
          DEFAULT: "rgb(var(--rgb-error) / <alpha-value>)",
          fg: "rgb(var(--rgb-error-fg) / <alpha-value>)",
          soft: "rgb(var(--rgb-error-soft) / <alpha-value>)",
          ink: "rgb(var(--rgb-error-ink) / <alpha-value>)"
        },
        overlay: "rgb(var(--rgb-overlay) / <alpha-value>)",
        hero: {
          bg: "rgb(var(--rgb-hero-bg) / <alpha-value>)",
          fg: "rgb(var(--rgb-hero-fg) / <alpha-value>)",
          muted: "rgb(var(--rgb-hero-muted) / <alpha-value>)",
          accent: "rgb(var(--rgb-hero-accent) / <alpha-value>)"
        }
      },
      boxShadow: {
        panel: "var(--shadow-panel)",
        "2xs": "0 1px 3px rgb(var(--rgb-text) / 0.04)",
        xs: "0 2px 6px rgb(var(--rgb-text) / 0.06)",
        sm: "var(--shadow)",
        md: "var(--shadow-panel)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-lg)",
        "2xl": "var(--shadow-lg)"
      }
    }
  },
  plugins: []
};
