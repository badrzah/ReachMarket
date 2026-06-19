import subprocess, os

token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")

if not token or not account_id:
    print("Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID env vars")
    exit(1)

env = os.environ.copy()
frontend = r"C:\Users\Admin\ReachMarket\frontend"
result = subprocess.run('npx.cmd --yes wrangler deployments list --name reachgtm-frontend', cwd=frontend, env=env, capture_output=True, text=True, timeout=30, shell=True)
print(result.stdout[:800])
