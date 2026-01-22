import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
  ],
  server: {
    open: true,
    proxy: {
      '/api/trends': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api\/trends/, ''), // Backend expects /api/trends
      },
    },
  },
})
