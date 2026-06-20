import urllib.request, urllib.error, json, base64

# 1. Login to get JWT
print("=== STEP 1: Login ===")
req = urllib.request.Request(
    "https://reachgtm-backend-production.up.railway.app/api/v1/auth/login",
    data=json.dumps({"email":"demo2@reachgtm.com","password":"demo1234"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())
token = data["access_token"]
print(f"Token: {token[:30]}...")

# Decode JWT
parts = token.split('.')
payload_b64 = parts[1].replace('-','+').replace('_','/')
pad = 4 - len(payload_b64) % 4
if pad != 4: payload_b64 += '=' * pad
payload = json.loads(base64.b64decode(payload_b64))
print(f"company_id: {payload['company_id']}")
print(f"user_id: {payload['sub']}")

# 2. Test CORS preflight
print("\n=== STEP 2: CORS preflight ===")
req2 = urllib.request.Request(
    "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev/chat",
    method="OPTIONS",
    headers={
        "Origin": "https://reachgtm-frontend.badrpcc.workers.dev",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type, authorization"
    }
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    print(f"HTTP {resp2.status}")
    print(f"ACA-Origin: {resp2.headers.get('Access-Control-Allow-Origin')}")
    print(f"ACA-Credentials: {resp2.headers.get('Access-Control-Allow-Credentials')}")
except Exception as e:
    print(f"FAILED: {e}")

# 3. Test full chat
print("\n=== STEP 3: Chat request ===")
req3 = urllib.request.Request(
    "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev/chat",
    data=json.dumps({
        "message": "What is a GTM strategy?",
        "session_id": None,
        "company_id": payload["company_id"],
        "user_id": payload["sub"]
    }).encode(),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://reachgtm-frontend.badrpcc.workers.dev",
        "User-Agent": "Mozilla/5.0"
    },
    method="POST"
)
try:
    resp3 = urllib.request.urlopen(req3, timeout=60)
    print(f"HTTP {resp3.status}")
    data3 = resp3.read(500)
    print(f"Response: {data3.decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {body[:300]}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n=== Full trace complete ===")
