// API Proxy Worker - forwards all headers including Authorization
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const backendUrl = "https://reachgtm-backend-production.up.railway.app" + url.pathname + url.search;

    // Forward request with ALL original headers preserved
    const backendReq = new Request(backendUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: "follow",
    });

    const response = await fetch(backendReq);

    const corsHeaders = {
      "Access-Control-Allow-Origin": "https://reachgtm-frontend.badrpcc.workers.dev",
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
      "Access-Control-Allow-Headers": "*",
      "Access-Control-Max-Age": "86400",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    const newResponse = new Response(response.body, response);
    for (const [key, value] of Object.entries(corsHeaders)) {
      newResponse.headers.set(key, value);
    }

    return newResponse;
  },
};
