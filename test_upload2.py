import urllib.request, urllib.error, json

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
print(f"Token OK")

# Create a real minimal PDF file
pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 44>>stream
BT /F1 24 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000356 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
428
%%EOF"""

# Try upload via proxy (what the frontend does)
boundary = "----TestBoundary456"
body = b""
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="doc_type"\r\n\r\n'
body += b"brand_guide\r\n"
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n'
body += b"Content-Type: application/pdf\r\n\r\n"
body += pdf_content
body += b"\r\n"
body += f"--{boundary}--\r\n".encode()

# Try via main proxy
url = "https://reachgtm-api-proxy.badrpcc.workers.dev/api/v1/knowledge/upload"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
    "User-Agent": "Mozilla/5.0"
}

req2 = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    resp2 = urllib.request.urlopen(req2, timeout=60)
    print(f"PROXY: HTTP {resp2.status}: {resp2.read().decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    print(f"PROXY: HTTP ERROR {e.code}: {e.read().decode('utf-8')[:500]}")
except Exception as e:
    print(f"PROXY: ERROR: {e}")

# Try directly on backend
url2 = "https://reachgtm-backend-production.up.railway.app/api/v1/knowledge/upload"
req3 = urllib.request.Request(url2, data=body, headers=headers, method="POST")
try:
    resp3 = urllib.request.urlopen(req3, timeout=60)
    print(f"BACKEND: HTTP {resp3.status}: {resp3.read().decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    err = e.read().decode('utf-8')
    print(f"BACKEND: HTTP ERROR {e.code}: {err[:500]}")
except Exception as e:
    print(f"BACKEND: ERROR: {e}")
