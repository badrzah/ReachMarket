#!/bin/bash
# Check deployed frontend JS for the chat URL
HTML=$(curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/')
echo "$HTML" | grep -oP 'src="[^"]+\.js"' | while read -r line; do
  CHUNK=$(echo "$line" | sed 's/src="//;s/"//')
  URL="https://reachgtm-frontend.badrpcc.workers.dev$CHUNK"
  CONTENT=$(curl -s "$URL")
  echo "--- Checking $CHUNK ---"
  echo "$CONTENT" | grep -o 'reachgtm-[a-z0-9.-]*\.[a-z]*' | head -3
  echo "$CONTENT" | grep -o '[a-z0-9.-]*\.railway\.app' | head -3
  echo "$CONTENT" | grep -o '[a-z0-9.-]*\.workers\.dev' | head -3
done
