#!/bin/bash
# Check if the JS content actually changed (compare sizes, check for patterns)
echo "=== File sizes ==="
HTML=$(curl -s 'https://reachgtm-frontend.badrpcc.workers.dev/')
echo "$HTML" | grep -oP 'src="[^"]+\.js"' | sed 's/src="//;s/"//' | while read CHUNK; do
  SIZE=$(curl -s -o /dev/null -w '%{size_download}' "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK")
  echo "$CHUNK: $SIZE bytes"
done

echo ""
echo "=== Looking for 'reminiscent' or 'moonstone' in chunks ==="
echo "$HTML" | grep -oP 'src="[^"]+\.js"' | sed 's/src="//;s/"//' | while read CHUNK; do
  CONTENT=$(curl -s "https://reachgtm-frontend.badrpcc.workers.dev$CHUNK")
  if echo "$CONTENT" | grep -q "reminiscent"; then
    echo ">> FOUND 'reminiscent' in $CHUNK"
  fi
  if echo "$CONTENT" | grep -q "moonstone"; then
    echo ">> FOUND 'moonstone' in $CHUNK"
  fi
  if echo "$CONTENT" | grep -q "reminiscent-moonstone"; then
    echo ">> FOUND 'reminiscent-moonstone' in $CHUNK"
  fi
  # Check for the proxy URL as string parts
  if echo "$CONTENT" | grep -q "reachgtm-chat"; then
    echo ">> FOUND 'reachgtm-chat' in $CHUNK"
  fi
  # Check for atob or JWT decode
  if echo "$CONTENT" | grep -q "atob"; then
    echo ">> Found atob in $CHUNK"
  fi
  if echo "$CONTENT" | grep -q "getJwtPayload\\|jwtPayload"; then
    echo ">> Found jwtPayload in $CHUNK"
  fi
done
echo "=== Done ==="
