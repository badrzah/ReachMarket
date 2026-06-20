import urllib.request, urllib.error, json, base64

# Login
req = urllib.request.Request(
    "https://reachgtm-backend-production.up.railway.app/api/v1/auth/login",
    data=json.dumps({"email":"demo2@reachgtm.com","password":"demo1234"}).encode(),
    headers={"Content-Type": "application/json"},
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

# Get RAW chat response (not decoded)
print("=== RAW response (first 3000 bytes) ===")
req2 = urllib.request.Request(
    "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev/chat",
    data=json.dumps({
        "message": "What is GTM?",
        "session_id": None,
        "company_id": payload["company_id"],
        "user_id": payload["sub"]
    }).encode(),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://reachgtm-frontend.badrpcc.workers.dev",
    },
    method="POST"
)
resp2 = urllib.request.urlopen(req2, timeout=60)
raw = resp2.read(3000)
print(repr(raw[:1500]))
