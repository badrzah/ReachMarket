import { defineRailway, project, service, postgres, redis } from "railway/iac";

export default defineRailway(() => {
  const db = postgres("Postgres");
  const cache = redis("Redis");

  const backend = service("reachgtm-backend", {
    source: {
      repo: "badrzah/ReachMarket",
      branch: "cloudflare-deploy",
    },
    build: {
      dockerfile: "backend/Dockerfile",
      context: ".",
    },
    env: {
      ENVIRONMENT: "production",
      DATABASE_URL: db.url,
      REDIS_URL: cache.url,
      JWT_ALGORITHM: "HS256",
      ACCESS_TOKEN_EXPIRE_MINUTES: "15",
      REFRESH_TOKEN_EXPIRE_DAYS: "30",
    },
  });

  const agents = service("reachgtm-agents", {
    source: {
      repo: "badrzah/ReachMarket",
      branch: "cloudflare-deploy",
    },
    build: {
      dockerfile: "agents/Dockerfile",
      context: ".",
    },
    env: {
      ENVIRONMENT: "production",
      DATABASE_URL: db.url,
      REDIS_URL: cache.url,
      JWT_ALGORITHM: "HS256",
      ACCESS_TOKEN_EXPIRE_MINUTES: "15",
      REFRESH_TOKEN_EXPIRE_DAYS: "30",
    },
  });

  return project("empathetic-mercy", {
    resources: [db, cache, backend, agents],
  });
});
