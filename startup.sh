#!/bin/bash
set -e

# Copy patched files into the container at startup
echo "🔧 Applying MiroFish startup patches..."

# 1. Patch vite.config.js - allow all hosts
if [ -f /app/frontend/vite.config.js ]; then
  echo '{"allowedHosts_patch"}' > /tmp/vite_patch.json
  cat > /app/frontend/vite.config.js << 'VITE_CONFIG'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    open: true,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
VITE_CONFIG
  echo "  ✅ vite.config.js patched (allowedHosts: true)"
fi

# 2. Patch backend/api/index.js - fix LLM client with fallback reasoning
API_FILE="/app/backend/api/index.py"
if [ -f "$API_FILE" ]; then
  # Patch the JSON schema to allow reasoning field in response
  if grep -q 'response_format' "$API_FILE" 2>/dev/null; then
    sed -i "s/\"response_format\": {\"type\": \"json_object\"}/\"response_format\": {\"type\": \"json_object\"}, \"max_tokens\": 4096/g" "$API_FILE"
    echo "  ✅ api/index.py patched (max_tokens added)"
  fi
fi

# 3. Patch llm_client.py - add reasoning fallback
LLM_FILE="/app/backend/llm/llm_client.py"
if [ -f "$LLM_FILE" ]; then
  # Check if already patched
  if ! grep -q '# PATCH: reasoning fallback' "$LLM_FILE" 2>/dev/null; then
    # Find the line that extracts message content and add reasoning fallback after it
    sed -i "s/message\.get('content', '')/message.get('content', '') or message.get('reasoning', '')  # PATCH: reasoning fallback/g" "$LLM_FILE"
    sed -i "s/choices\[0\]\['message'\]\['content'\]/choices[0]['message'].get('content') or choices[0]['message'].get('reasoning', '')  # PATCH: reasoning fallback/g" "$LLM_FILE"
    echo "  ✅ llm_client.py patched (reasoning fallback)"
  fi
fi

echo "🔧 Startup patches applied. Starting original entrypoint..."

# Execute the original entrypoint or CMD
exec "$@"
