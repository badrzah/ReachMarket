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
print(f"company_id: {payload['company_id']}")
print(f"user_id: {payload['sub']}")

# Test chat via proxy with company_id and user_id
url = "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev/chat"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
body = json.dumps({
    "message": "What is a GTM strategy?",
    "session_id": None,
    "company_id": payload["company_id"],
    "user_id": payload["sub"]
}).encode()

req = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=60)
    print(f"HTTP {resp.status}")
    data = resp.read(3000)
    print(data.decode('utf-8')[:1500])
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {body[:300]}")
except Exception as e:
    print(f"ERROR: {e}")
