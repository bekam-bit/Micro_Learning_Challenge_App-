import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react(), tailwindcss()],
    define: {
      // Support both variable names for flexibility
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(
        env.VITE_API_BASE_URL || 'https://learning-challenge.onrender.com',
      ),
      'import.meta.env.BACKEND_BASE_URL': JSON.stringify(
        env.BACKEND_BASE_URL || env.VITE_API_BASE_URL || 'https://learning-challenge.onrender.com',
      ),
    },
  }
})



