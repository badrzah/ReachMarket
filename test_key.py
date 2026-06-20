import urllib.request, urllib.error, json

# Test the exact key the user provided
key = "sk-pro...PXQA"

req = urllib.request.Request(
    "https://api.openai.com/v1/embeddings",
    data=json.dumps({"input":"test","model":"text-embedding-3-small"}).encode(),
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    },
    method="POST"
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    print(f"EMBEDDINGS: OK - vector dim={len(data['data'][0]['embedding'])}")
except urllib.error.HTTPError as e:
    print(f"EMBEDDINGS ERROR {e.code}: {e.read().decode('utf-8')[:300]}")
except Exception as e:
    print(f"ERROR: {e}")

# Also test models list
req2 = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {key}"}
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=10)
    data2 = json.loads(resp2.read())
    print(f"MODELS: OK - {len(data2['data'])} models")
except urllib.error.HTTPError as e:
    print(f"MODELS ERROR {e.code}: {e.read().decode('utf-8')[:200]}")
