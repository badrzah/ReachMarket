#!/bin/bash
# Check deployed frontend - new build may have different chunk names
echo "=== Frontend HTML ==="
HTML=$(curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/')
echo "$HTML" | grep -oP 'src="[^"]+\.js"' | sed 's/src="//;s/"//' > /tmp/chunks.txt
cat /tmp/chunks.txt
echo ""
echo "=== Searching ALL chunks for URLs ==="
cat /tmp/chunks.txt | while read CHUNK; do
  CONTENT=$(curl -s "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK")
  MATCH=$(echo "$CONTENT" | grep -oE '(reminiscent-moonstone|reachgtm-chat-proxy|reachgtm-agents-production|reachgtm-api-proxy|chat/[^"'"'"']+)' | head -3)
  if [ -n "$MATCH" ]; then
    echo "FOUND in $CHUNK:"
    echo "  $MATCH"
  fi
done
echo "=== Searching for base URL pattern ==="
cat /tmp/chunks.txt | while read CHUNK; do
  CONTENT=$(curl -s "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK")
  MATCH=$(echo "$CONTENT" | grep -oE 'https?://reachgtm[^"'"'"']+' | head -5)
  if [ -n "$MATCH" ]; then
    echo "URLs in $CHUNK:"
    echo "  $MATCH"
  fi
done
echo "=== Done ==="
