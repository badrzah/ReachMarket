import urllib.request, urllib.error, json

key = "sk-pro...PXQA"

req = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {key}"}
)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print(f"OpenAI API OK - {len(data['data'])} models available")
except urllib.error.HTTPError as e:
    print(f"OpenAI ERROR {e.code}: {e.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"ERROR: {e}")
