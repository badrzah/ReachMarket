import urllib.request, urllib.error, json

url = "https://reachgtm-api-proxy.badrpcc.workers.dev/api/v1/chat/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbG...I9KM",
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
    data = resp.read(2000)
    print(data.decode('utf-8')[:1500])
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}")
    print(e.read().decode('utf-8')[:500])
except Exception as e:
    print(f"ERROR: {e}")
