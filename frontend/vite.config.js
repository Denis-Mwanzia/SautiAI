import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync } from 'fs'
import { join } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Plugin to copy _redirects file to dist folder for Netlify
    {
      name: 'copy-redirects',
      closeBundle() {
        try {
          copyFileSync(
            join(__dirname, '_redirects'),
            join(__dirname, 'dist', '_redirects')
          )
        } catch (err) {
          // File might not exist, that's okay
          console.warn('Could not copy _redirects file:', err.message)
        }
      }
    }
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'chart-vendor': ['recharts'],
          'map-vendor': ['leaflet', 'react-leaflet'],
          'ui-vendor': ['lucide-react'],
        }
      }
    },
    chunkSizeWarningLimit: 600,
    sourcemap: false, // Disable source maps in production for security
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  // Use environment variable for API URL in production
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || 'http://localhost:8000'),
  },
})

