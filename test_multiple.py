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

# Test with user's exact question
questions = [
    "What's the best GTM motion for a B2B SaaS startup?",
    "What is a GTM strategy?",
    "Hello",
]

for q in questions:
    print(f"\n=== QUESTION: {q} ===")
    url = "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev/chat"
    body = json.dumps({
        "message": q,
        "session_id": None,
        "company_id": payload["company_id"],
        "user_id": payload["sub"]
    }).encode()
    
    req2 = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }, method="POST")
    
    try:
        resp2 = urllib.request.urlopen(req2, timeout=60)
        raw = resp2.read(5000)
        text = raw.decode('utf-8')
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith("data: "):
                json_str = line[6:]
                try:
                    parsed = json.loads(json_str)
                    status = "OK"
                except json.JSONDecodeError as e:
                    status = f"PARSE ERROR: {e}"
                print(f"  Line {i}: {status}")
    except Exception as e:
        print(f"  FAILED: {e}")
