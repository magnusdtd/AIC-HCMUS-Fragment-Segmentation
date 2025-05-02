import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  build: {
    outDir: '../backend/app/build', // Output to FastAPI's expected directory
    assetsDir: 'static', // Place assets in 'static' folder
  },
})
