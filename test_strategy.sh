#!/bin/bash
set -e

# Login
echo "--- Logging in ---"
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@reachgtm.com","password":"demo1234"}' > /tmp/login_resp.json

TOKEN_EXTRACT=$(grep -o '"access_token":"[^"]*"' /tmp/login_resp.json | cut -d'"' -f4)
echo "Token acquired (len=${#TOKEN_EXTRACT})"

# Generate strategy
echo ""
echo "--- Generating Strategy ---"
curl -s -X POST http://localhost:8000/api/v1/strategy/generate \
  -H "Authorization: Bearer ${TOKEN_EXTRACT}" \
  -H "Content-Type: application/json" \
  -d '{"company_profile":{"name":"TestCo","industry":"SaaS","stage":"seed","description":"A test company","website":null,"founded_year":null},"additional_context":null}'

echo ""
echo ""
echo "--- Done ---"
