import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config.js";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    strictPort: true,
  },
  preview: {
    port: 3000,
    strictPort: true,
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./vitest.setup.ts",
  },
});
