import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  preview: {
    host: '0.0.0.0',
    port: process.env.PORT || 8080,
    strictPort: true,
    // Allow Railway domains
    allowedHosts: [
      'myrecipefinder.up.railway.app',
      'myrecipefinder-frontend-production.up.railway.app',
      '.railway.app'  // This allows all railway.app subdomains
    ]
  },
  server: {
    host: '0.0.0.0',
    port: process.env.PORT || 5173
  }
})
