import urllib.request, urllib.error, json

key = "sk-pro...PXQA"

# Test embedding
print("=== Testing text-embedding-3-small ===")
req = urllib.request.Request(
    "https://api.openai.com/v1/embeddings",
    data=json.dumps({"input":"test","model":"text-embedding-3-small"}).encode(),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    method="POST"
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print("OK - embeddings work!")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"ERROR: {body[:300]}")

# Test chat model
print("\n=== Testing gpt-4o-mini ===")
req2 = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=json.dumps({"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}).encode(),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    method="POST"
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    data2 = json.loads(resp2.read())
    print(f"OK - response: {data2['choices'][0]['message']['content'][:50]}")
except urllib.error.HTTPError as e:
    body2 = e.read().decode('utf-8')
    print(f"ERROR: {body2[:300]}")
