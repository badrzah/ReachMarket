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

# Fetch SSE response
url = "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev/chat"
body = json.dumps({
    "message": "What is GTM?",
    "session_id": None,
    "company_id": payload["company_id"],
    "user_id": payload["sub"]
}).encode()

req2 = urllib.request.Request(url, data=body, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://reachgtm-frontend.badrpcc.workers.dev"
}, method="POST")

try:
    resp2 = urllib.request.urlopen(req2, timeout=60)
    print(f"\nHTTP {resp2.status}")
    raw = resp2.read(5000)
    print(f"Total bytes: {len(raw)}")
    
    # Show raw bytes with special chars visible
    text = raw.decode('utf-8')
    lines = text.split('\n')
    print(f"Total lines: {len(lines)}")
    
    for i, line in enumerate(lines):
        if line.startswith("data: "):
            json_str = line[6:]
            try:
                parsed = json.loads(json_str)
                print(f"Line {i}: OK - event={parsed.get('event','?')} len(msg)={len(parsed.get('message',''))}")
            except json.JSONDecodeError as e:
                print(f"Line {i}: *** JSON ERROR *** {e}")
                print(f"  Raw: {repr(json_str[:200])}")
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"ERROR: {e}")
