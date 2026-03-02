import react from "@vitejs/plugin-react";
import { resolve } from "path";
import { defineConfig } from "vitest/config";

const frontendDir = __dirname;
const projectRoot = resolve(frontendDir, "../..");

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": frontendDir,
    },
  },
  server: {
    fs: {
      allow: [projectRoot],
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    include: [resolve(projectRoot, "tests/frontend/**/*.test.{ts,tsx}")],
  },
});
