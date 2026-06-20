import urllib.request, urllib.error, json

# Double-check the exact key - test against multiple endpoints
key = "sk-pro...PXQA"

# Test 1: models list (simplest endpoint)
print("=== Test 1: Models list ===")
req = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {key}"}
)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print(f"OK - {len(data['data'])} models")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"ERROR {e.code}: {body[:300]}")

# Test 2: Check if key format is correct
print(f"\n=== Key format check ===")
print(f"Starts with 'sk-proj-': {key.startswith('sk-proj-')}")
print(f"Length: {len(key)}")
print(f"Contains two parts separated by 'Blbk': {'Blbk' in key}")
parts = key.split('Blbk') if 'Blbk' in key else [key]
if len(parts) == 2:
    print(f"Secret part length: {len(parts[1])}")
else:
    print(f"Parts: {len(parts)}")

# Test 3: Check if maybe the instructors gave us a read-only or restricted key
print(f"\n=== Checking key permissions ===")
req2 = urllib.request.Request(
    "https://api.openai.com/v1/models?limit=1",
    headers={"Authorization": f"Bearer {key}"}
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=10)
    print(f"Basic access: OK")
except Exception as e:
    print(f"Basic access failed: {e}")
