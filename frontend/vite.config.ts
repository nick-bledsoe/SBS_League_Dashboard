import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  // Vercel's @vercel/static-build namespaces this project's output under /frontend/
  // (since it builds from frontend/package.json in the monorepo) — VERCEL is a env
  // var Vercel injects into its build environment, unset locally, so `npm run dev`
  // and local `npm run build` are unaffected.
  base: process.env.VERCEL ? '/frontend/' : '/',
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
  },
})
