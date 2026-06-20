#!/bin/bash
# Trace: Check the deployed frontend JS for chat URL
HTML=$(curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/')
echo "=== Check JS chunks for chat URL ==="
echo "$HTML" | grep -oP 'src="/_next/static/chunks/[^"]+\.js"' | sed 's/src="//;s/"//' | while read CHUNK; do
  curl -s "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK" > /tmp/chunk.js
  FOUND=$(grep -o 'reminiscent-moonstone\|reachgtm-chat-proxy\|reachgtm-agents\|reachgtm-api-proxy\|chat/' /tmp/chunk.js | head -3)
  if [ -n "$FOUND" ]; then
    echo ">> $CHUNK : $FOUND"
  fi
done
echo "=== Done ==="
