import { defineConfig, type Plugin } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

/**
 * Normalizes KaTeX @font-face declarations to use `font-display: swap` and
 * emit only `.woff2` fonts (eliminating redundant legacy `.woff` and `.ttf` payloads).
 */
function optimizeKatexFonts(): Plugin {
  return {
    name: "optimize-katex-fonts",
    enforce: "pre",
    transform(code, id) {
      if (!id.replace(/\\/g, "/").includes("katex/dist/katex")) {
        return null;
      }
      const optimized = code
        .replace(/font-display:\s*block/g, "font-display:swap")
        .replace(
          /src:url\(([^)]+\.woff2)\)\s*format\("woff2"\)(?:,url\([^)]+\.(?:woff|ttf)\)\s*format\("[^"]+"\))+/g,
          'src:url($1) format("woff2")'
        );
      return { code: optimized, map: null };
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), optimizeKatexFonts()],
  build: {
    outDir: "../../dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules/react/") || id.includes("node_modules/react-dom/")) {
            return "vendor-react";
          }
          if (id.includes("node_modules/react-router")) {
            return "vendor-router";
          }
          if (id.includes("node_modules/katex")) {
            return "vendor-katex";
          }
          return undefined;
        },
      },
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: process.env.VITE_API_GATEWAY_URL || "http://localhost:18080",
        changeOrigin: true
      }
    }
  },
  preview: { port: 4173, strictPort: true },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    clearMocks: true,
    restoreMocks: true
  }
});
