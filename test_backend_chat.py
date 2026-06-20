import urllib.request, urllib.error, json

url = "https://reachgtm-backend-production.up.railway.app/api/v1/chat/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbG...uybA",
    "User-Agent": "Mozilla/5.0"
}
body = json.dumps({
    "message": "What is a GTM strategy?",
    "session_id": None
}).encode()

req = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"HTTP {resp.status}")
    data = resp.read(200)
    print(repr(data.decode('utf-8')[:200]))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {body[:300]}")
except Exception as e:
    print(f"ERROR: {e}")
