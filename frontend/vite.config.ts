import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'node'
  },
  server: {
    proxy: {
      '/projects': { target: 'http://localhost:8000', changeOrigin: true },
      '/materials': { target: 'http://localhost:8000', changeOrigin: true },
      '/nodes': { target: 'http://localhost:8000', changeOrigin: true },
      '/relations': { target: 'http://localhost:8000', changeOrigin: true },
      '/score': { target: 'http://localhost:8000', changeOrigin: true },
      '/socket': { target: 'ws://localhost:8000', ws: true }
    }
  }
})
