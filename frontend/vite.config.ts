import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/merilang/',
  build: {
    outDir: '../docs',
    emptyOutDir: false, // Don't delete existing markdown files in docs
    assetsDir: 'assets',
  }
})
