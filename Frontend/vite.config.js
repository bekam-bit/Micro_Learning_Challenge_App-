import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const defaultBackendUrl = 'http://127.0.0.1:8000'

  return {
    plugins: [react(), tailwindcss()],
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



