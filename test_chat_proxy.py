import urllib.request, urllib.error, json

url = "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev/chat"
headers = {
    "Authorization": "Bearer eyJhbG...t0k8",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
body = json.dumps({
    "message": "What is GTM?",
    "session_id": None
}).encode()

req = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"HTTP {resp.status}")
    data = resp.read(1000)
    print(data.decode('utf-8')[:800])
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {body[:300]}")
except Exception as e:
    print(f"ERROR: {e}")
