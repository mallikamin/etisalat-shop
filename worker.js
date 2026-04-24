/**
 * Cloudflare Worker entry for goldennummbers.com.
 *
 * Routes:
 *   POST /api/tiktok-event   -> TikTok Events API proxy (CAPI)
 *   everything else          -> served as static assets from ./  (env.ASSETS)
 *
 * Env (set in Cloudflare dashboard -> Settings -> Variables and Secrets):
 *   TIKTOK_EVENTS_API_TOKEN   secret, long-lived token from TikTok Ads Manager
 *   TIKTOK_PIXEL_ID           plaintext, e.g. D7J1GQRC77UDQGOITA8G
 *
 * Why a Worker (not Pages Functions): this project deploys as
 * "Workers with Static Assets" instead of Pages. Same capabilities,
 * different config shape. Functions live in worker.js rather than
 * /functions/*.js.
 */

const TIKTOK_ENDPOINT = "https://business-api.tiktok.com/open_api/v1.3/event/track/";
const ALLOWED_ORIGIN = "https://goldennummbers.com";

async function sha256Hex(input) {
  if (!input) return "";
  const buf = new TextEncoder().encode(String(input).trim().toLowerCase());
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function getCookie(cookieHeader, name) {
  if (!cookieHeader) return "";
  const m = cookieHeader.match(new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()[\]\\/+^])/g, "\\$1") + "=([^;]*)"));
  return m ? decodeURIComponent(m[1]) : "";
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
  };
}

async function handleTikTokEvent(request, env) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: { ...corsHeaders(), "Access-Control-Max-Age": "86400" } });
  }
  if (request.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "POST only" }), { status: 405, headers: corsHeaders() });
  }

  const token = env.TIKTOK_EVENTS_API_TOKEN;
  const pixelId = env.TIKTOK_PIXEL_ID || "D7J1GQRC77UDQGOITA8G";
  if (!token) {
    return new Response(JSON.stringify({ ok: false, error: "TIKTOK_EVENTS_API_TOKEN env var missing" }), { status: 500, headers: corsHeaders() });
  }

  let body;
  try { body = await request.json(); } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: "invalid JSON body" }), { status: 400, headers: corsHeaders() });
  }

  const event = body.event;
  const event_id = body.event_id || ("e_" + Date.now() + "_" + Math.random().toString(36).slice(2, 10));
  if (!event) {
    return new Response(JSON.stringify({ ok: false, error: "event field required" }), { status: 400, headers: corsHeaders() });
  }

  const userIn = body.user || {};
  const cookieHeader = request.headers.get("Cookie") || "";
  const userHashed = {};
  if (userIn.email)       userHashed.email = await sha256Hex(userIn.email);
  if (userIn.phone)       userHashed.phone = await sha256Hex(userIn.phone);
  if (userIn.external_id) userHashed.external_id = await sha256Hex(userIn.external_id);

  const ip = request.headers.get("CF-Connecting-IP") || request.headers.get("X-Real-IP") || "";
  const ua = request.headers.get("User-Agent") || "";
  const ttclid = userIn.ttclid || getCookie(cookieHeader, "ttclid") || "";
  const ttp = userIn.ttp || getCookie(cookieHeader, "_ttp") || "";
  if (ip)     userHashed.ip = ip;
  if (ua)     userHashed.user_agent = ua;
  if (ttclid) userHashed.ttclid = ttclid;
  if (ttp)    userHashed.ttp = ttp;

  const payload = {
    event_source: "web",
    event_source_id: pixelId,
    data: [{
      event: event,
      event_time: Math.floor(Date.now() / 1000),
      event_id: event_id,
      user: userHashed,
      page: {
        url: body.page_url || "",
        referrer: body.page_referrer || "",
      },
      properties: body.properties || {},
    }],
  };

  try {
    const tiktokResp = await fetch(TIKTOK_ENDPOINT, {
      method: "POST",
      headers: { "Access-Token": token, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const tiktokJson = await tiktokResp.json().catch(() => ({}));
    const ok = tiktokResp.ok && tiktokJson.code === 0;
    return new Response(JSON.stringify({ ok, event_id, tiktok: tiktokJson }), { status: ok ? 200 : 502, headers: corsHeaders() });
  } catch (err) {
    return new Response(JSON.stringify({ ok: false, error: String(err) }), { status: 502, headers: corsHeaders() });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/tiktok-event") {
      return handleTikTokEvent(request, env);
    }

    // Fall through to static assets binding for everything else
    return env.ASSETS.fetch(request);
  },
};
