// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: CC-BY-NC-ND-4.0

import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// Local-only web interface for Lumina. The Flask API (server.py)
// runs on 127.0.0.1:5000; we proxy /api so the browser never needs CORS.
export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: false
      }
    }
  }
});
