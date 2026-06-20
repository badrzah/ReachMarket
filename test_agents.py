import urllib.request, urllib.error, json

url = "https://reachgtm-agents-production.up.railway.app/chat"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbG...lZf0",
    "User-Agent": "Mozilla/5.0"
}
body = json.dumps({
    "message": "What is a GTM strategy?",
    "session_id": None,
    "company_id": "00000000-0000-0000-0000-000000000001",
    "user_id": "00000000-0000-0000-0000-000000000002"
}).encode()

req = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"HTTP {resp.status}")
    data = resp.read(2000)
    print(data.decode('utf-8')[:1000])
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {body[:500]}")
except Exception as e:
    print(f"ERROR: {e}")
