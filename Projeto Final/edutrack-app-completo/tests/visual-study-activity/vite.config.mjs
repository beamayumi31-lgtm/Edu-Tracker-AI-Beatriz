import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/postcss';

// Fixture isolada: não inicializa a API, não lê .env e não altera a autenticação do app.
export default defineConfig({
  root: fileURLToPath(new URL('.', import.meta.url)),
  envDir: false,
  plugins: [react()],
  css: { postcss: { plugins: [tailwindcss()] } },
  server: { host: '127.0.0.1', port: 3013, strictPort: true,
    fs: { allow: [fileURLToPath(new URL('../..', import.meta.url))] } },
});
