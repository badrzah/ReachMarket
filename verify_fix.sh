#!/bin/bash
# Simple verification: check if fix is deployed
echo "=== Checking deployed frontend ==="
HTML=$(curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/agent')
echo "$HTML" | grep -oP 'src="[^"]+\.js"' | sed 's/src="//;s/"//' | sort -u | while read CHUNK; do
  curl -s "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK" > /tmp/c.js
  if grep -q "base64" /tmp/c.js; then
    echo "base64 found in $CHUNK"
  fi
  if grep -q "reminiscent" /tmp/c.js; then
    echo "reminiscent found in $CHUNK"
  fi
done
echo "=== Done ==="
