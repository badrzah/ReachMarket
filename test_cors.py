import os
os.environ["OPENAI_API_KEY"] = "test"
os.environ["DATABASE_URL"] = "postgresql://postgres:***@localhost:5432/test"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["JWT_SECRET"] = "test-secret"

import sys
sys.path.insert(0, r"C:\Users\Admin\ReachMarket")
from backend.app.main import app
from starlette.testclient import TestClient

client = TestClient(app)

# Test OPTIONS preflight
resp = client.options('/api/v1/auth/login', headers={
    'origin': 'https://reachgtm-frontend.badrpcc.workers.dev',
    'access-control-request-method': 'POST'
})
print(f"Status: {resp.status_code}")
has_cors = False
for k, v in resp.headers.items():
    if 'access-control' in k.lower():
        print(f"  {k}: {v}")
        has_cors = True
if not has_cors:
    print("  NO CORS HEADERS!")
print(f"Body: {resp.text[:100]}")
