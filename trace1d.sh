#!/bin/bash
# Search for various URL patterns in chunks
echo "=== Looking for any chat-related URLs ==="
HTML=$(curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/')
echo "$HTML" | grep -oP 'src="[^"]+\.js"' | sed 's/src="//;s/"//' | while read CHUNK; do
  CONTENT=$(curl -s "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK")
  # Search for any .workers.dev or .railway.app domains
  echo "$CONTENT" | grep -oE '[a-zA-Z0-9.-]+\.workers\.dev' | sort -u | while read DOMAIN; do
    echo ">> $CHUNK : $DOMAIN"
  done
  echo "$CONTENT" | grep -oE '[a-zA-Z0-9.-]+\.railway\.app' | sort -u | while read DOMAIN; do
    echo ">> $CHUNK : $DOMAIN"
  done
done
echo "=== Done ==="
