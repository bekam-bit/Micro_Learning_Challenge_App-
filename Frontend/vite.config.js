import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const defaultBackendUrl = '/api'

  return {
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        '/api': {
          target: 'https://learning-challenge.onrender.com',
          changeOrigin: true,
          secure: true,
        },
      },
    },
    define: {
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(
        env.VITE_API_BASE_URL || defaultBackendUrl,
      ),
      'import.meta.env.BACKEND_BASE_URL': JSON.stringify(
        env.BACKEND_BASE_URL || env.VITE_API_BASE_URL || defaultBackendUrl,
      ),
    },
  }
})



