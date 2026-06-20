#!/bin/bash
# Check what's in the agent page HTML
echo "=== Agent page HTML (first 2000 chars) ==="
curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/agent' | head -c 2000
echo ""
echo ""
echo "=== Looking for base URL in chunks ==="
HTML=$(curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/agent')
echo "$HTML" | grep -oP 'src="[^"]+\.js"' | sed 's/src="//;s/"//' | while read CHUNK; do
  CONTENT=$(curl -s "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK")
  # Search for 'base' variable assignment
  CLUE=$(echo "$CONTENT" | grep -oP 'base[=:]["'"'"'][^"'"'"']+' | head -3)
  if [ -n "$CLUE" ]; then
    echo ">> $CHUNK : $CLUE"
  fi
  # Search for 'chat' in the content
  CLUE2=$(echo "$CONTENT" | grep -oP 'chat[^,;}\s]{0,30}' | head -3)
  if [ -n "$CLUE2" ]; then
    echo ">> Chat ref in $CHUNK: $CLUE2"
  fi
done
echo "=== Done ==="
