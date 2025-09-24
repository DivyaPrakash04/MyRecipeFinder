import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  preview: {
    host: '0.0.0.0',
    port: process.env.PORT || 4173,  // Changed: Use Vite's default preview port
    strictPort: true,
    allowedHosts: 'all'
  },
  server: {
    host: '0.0.0.0',
    port: 5173,  // Changed: Keep dev server port static
    allowedHosts: 'all'
  }
})
