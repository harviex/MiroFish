#!/bin/bash
# MiroFish 启动补丁：持久化前端和后端修改到容器内

set -e

echo "[Patch] Applying MiroFish customizations..."

# Backend: 替换 llm_client.py（支持限流重试）
if [ -f /app/patches/llm_client.py ]; then
    cp /app/patches/llm_client.py /app/backend/app/utils/llm_client.py
    echo "[Patch] ✓ llm_client.py patched"
fi

# Frontend: 替换 api/index.js（使用相对路径）
if [ -f /app/patches/api-index.js ]; then
    cp /app/patches/api-index.js /app/frontend/src/api/index.js
    echo "[Patch] ✓ api/index.js patched"
fi

# Frontend: 替换 vite.config.js（allowedHosts + proxy）
if [ -f /app/patches/vite-patch.js ]; then
    cp /app/patches/vite-patch.js /app/frontend/vite.config.js
    echo "[Patch] ✓ vite.config.js patched"
fi

echo "[Patch] Done. Starting MiroFish..."
exec docker-entrypoint.sh "$@"
