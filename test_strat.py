import urllib.request, urllib.error, json

url = "https://reachgtm-backend-production.up.railway.app/api/v1/strategy/"
headers = {
    "Authorization": "Bearer eyJhbG...lZf0",
    "User-Agent": "Mozilla/5.0"
}

req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print(f"HTTP {resp.status}: {resp.read().decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.read().decode('utf-8')[:300]}")
except Exception as e:
    print(f"ERROR: {e}")
