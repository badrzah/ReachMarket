import urllib.request, urllib.error, json, io, base64

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
print(f"Token: {token[:20]}...")

# Build multipart upload like the browser does
boundary = "----TestBoundary123"
body = b""
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="doc_type"\r\n\r\n'
body += b"brand_guide\r\n"
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n'
body += b"Content-Type: application/pdf\r\n\r\n"
body += b"%PDF-1.4 Minimal test content\n"
body += f"--{boundary}--\r\n".encode()

url = "https://reachgtm-api-proxy.badrpcc.workers.dev/api/v1/knowledge/upload"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
    "User-Agent": "Mozilla/5.0"
}

req2 = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp2 = urllib.request.urlopen(req2, timeout=30)
    print(f"HTTP {resp2.status}: {resp2.read().decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.read().decode('utf-8')[:500]}")
except Exception as e:
    print(f"ERROR: {e}")

# Also try directly on backend (bypass proxy)
print("\n=== Direct backend ===")
url2 = "https://reachgtm-backend-production.up.railway.app/api/v1/knowledge/upload"
headers2 = {
    "Authorization": f"Bearer {token}",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
    "User-Agent": "Mozilla/5.0"
}
body2 = body
req3 = urllib.request.Request(url2, data=body2, headers=headers2, method="POST")
try:
    resp3 = urllib.request.urlopen(req3, timeout=30)
    print(f"HTTP {resp3.status}: {resp3.read().decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {err_body[:500]}")
except Exception as e:
    print(f"ERROR: {e}")
