import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  preview: {
    host: '0.0.0.0',
    port: process.env.PORT || 4173,  // Changed: Use Vite's default preview port
    strictPort: true,
    allowedHosts: ['myrecipefinder-frontend-production.up.railway.app', 'myrecipefinder.up.railway.app', 'myrecipefinder-prod.up.railway.app']
  },
  server: {
    host: '0.0.0.0',
    port: 5173,  // Changed: Keep dev server port static
    allowedHosts: ['myrecipefinder-frontend-production.up.railway.app', 'myrecipefinder.up.railway.app', 'myrecipefinder-prod.up.railway.app']
  }
})
