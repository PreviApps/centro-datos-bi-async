import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react()],
  server: {
    host: '0.0.0.0', // Necesario para Docker
    port: 4008,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '10.10.119.45',
      '10.10.119.97',
      'centro-datos-bi-v2.previsalud.com.co'
    ]
  }
})
