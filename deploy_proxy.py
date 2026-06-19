import subprocess, os

# Cloudflare credentials from environment
token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")

if not token or not account_id:
    print("Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID env vars")
    exit(1)

env = os.environ.copy()
proxy_dir = r"C:\Users\Admin\ReachMarket\api-proxy"

result = subprocess.run(
    'npx.cmd --yes wrangler deploy worker.js --name reachgtm-api-proxy --compatibility-date 2026-06-16 --compatibility-flag nodejs_compat',
    cwd=proxy_dir, env=env, capture_output=True, text=True, timeout=60, shell=True
)
print(result.stdout)
for line in result.stdout.split('\n'):
    if 'workers.dev' in line:
        print(f"✅ {line.strip()}")
