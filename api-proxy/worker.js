// API Proxy - handles CORS correctly for all origins
addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  // Only handle /api/ routes
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(handleAPI(event.request));
  }
  // Otherwise let other handlers deal with it
});

async function handleAPI(request) {
  const url = new URL(request.url);
  const backendUrl = "https://reachgtm-backend-production.up.railway.app" + url.pathname.replace("/api", "/api") + url.search;
  
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "86400",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  try {
    const backendReq = new Request(backendUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: "follow",
    });
    const response = await fetch(backendReq);
    const newResponse = new Response(response.body, response);
    for (const [key, value] of Object.entries(corsHeaders)) {
      newResponse.headers.set(key, value);
    }
    return newResponse;
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 502,
      headers: { "Content-Type": "application/json", ...corsHeaders },
    });
  }
}
