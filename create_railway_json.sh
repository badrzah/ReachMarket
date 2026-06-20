#!/bin/bash
# Create railway.json to configure build properly
cat > /c/Users/Admin/ReachMarket/railway.json << 'RAILWAYEOF'
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements.txt",
    "watchPatterns": ["backend/**"]
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
RAILWAYEOF

echo "Created railway.json"
cat /c/Users/Admin/ReachMarket/railway.json
