import urllib.request, urllib.error, json, base64

# Login
req = urllib.request.Request(
    "https://reachgtm-backend-production.up.railway.app/api/v1/auth/login",
    data=json.dumps({"email":"demo2@reachgtm.com","password":"demo1234"}).encode(),
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    method="POST"
)
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())
token = data["access_token"]

# Decode JWT
parts = token.split('.')
payload_b64 = parts[1].replace('-','+').replace('_','/')
pad = 4 - len(payload_b64) % 4
if pad != 4: payload_b64 += '=' * pad
payload = json.loads(base64.b64decode(payload_b64))
print(f"company_id: {payload['company_id']}")
print(f"user_id: {payload['sub']}")

# Test 1: Backend chat via main proxy
print("\n=== Test 1: Backend chat via main proxy ===")
url = "https://reachgtm-api-proxy.badrpcc.workers.dev/api/v1/chat/"
body = json.dumps({"message": "What is GTM?", "session_id": None}).encode()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
req2 = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp2 = urllib.request.urlopen(req2, timeout=30)
    print(f"HTTP {resp2.status}")
    raw = resp2.read(500)
    print(raw.decode('utf-8')[:300])
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Agents service direct
print("\n=== Test 2: Agents service direct ===")
url2 = "https://reachgtm-agents-production.up.railway.app/chat"
body2 = json.dumps({
    "message": "What is GTM?",
    "session_id": None,
    "company_id": payload["company_id"],
    "user_id": payload["sub"]
}).encode()

req3 = urllib.request.Request(url2, data=body2, headers=headers, method="POST")
try:
    resp3 = urllib.request.urlopen(req3, timeout=30)
    print(f"HTTP {resp3.status}")
    raw3 = resp3.read(500)
    print(raw3.decode('utf-8')[:300])
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"ERROR: {e}")
