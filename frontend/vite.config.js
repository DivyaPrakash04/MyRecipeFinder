import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  preview: {
    host: '0.0.0.0',
    port: process.env.PORT || 8080,
    strictPort: true,
    allowedHosts: 'all'  // Changed: Use 'all' instead of array
  },
  server: {
    host: '0.0.0.0',
    port: process.env.PORT || 5173,
    allowedHosts: 'all'  // Added: Also for server config
  }
})
