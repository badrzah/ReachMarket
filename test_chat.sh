#!/bin/bash
# Login and get token
RESP=$(curl -s "https://reachgtm-backend-production.up.railway.app/api/v1/auth/login" -X POST -H "Content-Type: application/json" -d '{"email":"demo2@reachgtm.com","password":"demo1234"}')
TOKEN=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token length: ${#TOKEN}"

# Test chat via backend
echo "---"
curl -s --max-time 30 \
  "https://reachgtm-backend-production.up.railway.app/api/v1/chat/" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"What is a GTM strategy?","session_id":null}' 2>&1 | head -10
echo ""
echo "EXIT: $?"
