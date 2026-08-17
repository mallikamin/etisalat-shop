/**
 * Cloudflare Worker entry for goldennummbers.com.
 *
 * Routes:
 *   POST /api/tiktok-event              -> TikTok Events API proxy (CAPI)
 *   GET  /oauth/tiktok/start            -> branded landing page with "Connect" button
 *   GET  /oauth/tiktok/authorize        -> 302 to TikTok consent screen (CSRF state cookie)
 *   GET  /oauth/tiktok/callback         -> exchanges code, displays tokens for admin copy
 *   GET  /oauth/pinterest/start         -> branded landing page with "Connect" button
 *   GET  /oauth/pinterest/authorize     -> 302 to Pinterest consent screen (CSRF state cookie, prompt=consent)
 *   GET  /oauth/pinterest/callback      -> exchanges code via Basic auth, displays tokens
 *   GET  /r                             -> WhatsApp short-link redirect
 *   everything else                     -> served as static assets from ./  (env.ASSETS)
 *
 * Env (set in Cloudflare dashboard -> Settings -> Variables and Secrets):
 *   TIKTOK_EVENTS_API_TOKEN   secret, long-lived token from TikTok Ads Manager
 *   TIKTOK_PIXEL_ID           plaintext, e.g. D7J1GQRC77UDQGOITA8G
 *   TIKTOK_CLIENT_KEY         plaintext, Content Posting API client key
 *   TIKTOK_CLIENT_SECRET      secret, Content Posting API client secret
 *   PINTEREST_CLIENT_ID       plaintext, Pinterest app ID (1568917 for GoldenNumbers Poster)
 *   PINTEREST_CLIENT_SECRET   secret, Pinterest app client secret
 *
 * Why a Worker (not Pages Functions): this project deploys as
 * "Workers with Static Assets" instead of Pages. Same capabilities,
 * different config shape. Functions live in worker.js rather than
 * /functions/*.js.
 */

const TIKTOK_ENDPOINT = "https://business-api.tiktok.com/open_api/v1.3/event/track/";
const ALLOWED_ORIGIN = "https://goldennummbers.com";
const TIKTOK_OAUTH_AUTHORIZE = "https://www.tiktok.com/v2/auth/authorize/";
const TIKTOK_OAUTH_TOKEN     = "https://open.tiktokapis.com/v2/oauth/token/";
const TIKTOK_OAUTH_REDIRECT  = "https://goldennummbers.com/oauth/tiktok/callback";
const TIKTOK_OAUTH_SCOPES    = "user.info.basic,video.publish,video.upload";

const PINTEREST_OAUTH_AUTHORIZE = "https://www.pinterest.com/oauth/";
const PINTEREST_OAUTH_TOKEN     = "https://api.pinterest.com/v5/oauth/token";
const PINTEREST_OAUTH_REDIRECT  = "https://goldennummbers.com/oauth/pinterest/callback";
const PINTEREST_OAUTH_SCOPES    = "boards:read,boards:write,pins:read,pins:write,user_accounts:read";

// /r — short-link redirect for FB direct-CTW ads.
// Generates a unique token, builds the canonical Ref code, redirects to
// wa.me with the prefill text including Ref:. Lets us attribute every
// WhatsApp message back to a specific Rail + creative even though the
// FB ad's prefill text is static.
const WA_NUMBER = "971569028087";
const RAIL_PREFILLS = {
  A: "Hi! I'm interested in a premium Etisalat number from your ad.\n\nName: \nCity: \nBudget (AED): ",
  B: "Hi! I'd like a free golden Etisalat number with the postpaid plan.\n\nName: \nCity: \nBudget (AED): ",
  C: "Hi! I saw your Etisalat numbers offer again — please share available options.\n\nName: \nCity: \nBudget (AED): ",
};
const RAIL_SOURCES = { A: "RETURNING", B: "CTW", C: "RETARGET" };

function genToken() {
  // 7-char uppercase alphanumeric token
  const chars = "ABCDEFGHIJKLMNPQRSTUVWXYZ23456789";
  let t = "T";
  for (let i = 0; i < 6; i++) t += chars[Math.floor(Math.random() * chars.length)];
  return t;
}

function buildRailRef(rail, creative) {
  const cleanCreative = String(creative || "").replace(/[^a-zA-Z0-9]/g, "").slice(0, 8).toUpperCase();
  const campaign = "RAIL" + rail.toUpperCase() + (cleanCreative ? "-" + cleanCreative : "");
  return ["GN1", "PM", "FB", campaign.replace("-", ""), "X", RAIL_SOURCES[rail.toUpperCase()] || "CTW", genToken()].join("-");
}

function handleRailRedirect(request) {
  const url = new URL(request.url);
  const rail = (url.searchParams.get("rail") || "").toUpperCase();
  const creative = url.searchParams.get("c") || "";
  if (!RAIL_PREFILLS[rail]) {
    return new Response("Bad rail. Use ?rail=A|B|C", { status: 400 });
  }
  const ref = buildRailRef(rail, creative);
  const text = RAIL_PREFILLS[rail] + "\n\nRef: " + ref;
  const waUrl = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(text)}`;
  return Response.redirect(waUrl, 302);
}

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

// --- TikTok Content Posting API OAuth ----------------------------------------
//
// Three-step admin flow:
//   1. Admin visits /oauth/tiktok/start (a branded landing page with a
//      "Connect @telecom.store.uae" button).
//   2. Click goes to /oauth/tiktok/authorize, which sets a CSRF `tiktok_oauth_state`
//      cookie and 302s to TikTok's consent screen with our scopes.
//   3. TikTok redirects to /oauth/tiktok/callback?code=...&state=...; we
//      validate state, exchange code for an access_token + refresh_token at
//      /v2/oauth/token/, and display the result on a copyable HTML page so the
//      admin can paste them into the loom-edge tiktok_config.json.
//
// The callback page intentionally returns HTML rather than JSON so it
// renders cleanly in the demo screencast.

function randomState() {
  const buf = new Uint8Array(24);
  crypto.getRandomValues(buf);
  return Array.from(buf).map(b => b.toString(16).padStart(2, "0")).join("");
}

function htmlShell(title, body) {
  return `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title>
<meta name="robots" content="noindex,nofollow">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0D1117;--surface:#161B22;--border:#21262D;--gold:#C9A962;--gold-light:#E8D5A3;--text:#F5F5F0;--muted:rgba(245,245,240,.65);--ok:#3FB950;--err:#F85149}
body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:40px 20px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:48px 40px;max-width:680px;width:100%}
h1{font-family:'Playfair Display',serif;color:var(--gold);font-size:1.9rem;margin-bottom:8px}
h2{font-family:'Playfair Display',serif;color:var(--gold-light);font-size:1.15rem;margin-top:24px;margin-bottom:8px}
p{color:var(--muted);margin-bottom:14px;font-size:.95rem}
.handle{color:var(--gold);font-weight:600}
.btn{display:inline-block;padding:14px 28px;background:var(--gold);color:var(--bg);text-decoration:none;font-weight:600;border-radius:10px;margin-top:8px;border:none;cursor:pointer;font-size:1rem;font-family:inherit}
.btn:hover{opacity:.9}
.box{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:.85rem;word-break:break-all;color:var(--gold-light)}
.row{display:flex;gap:12px;align-items:center;margin-bottom:8px}
.label{min-width:120px;color:var(--muted);font-size:.85rem}
.copy{padding:6px 12px;background:transparent;color:var(--gold);border:1px solid var(--gold);border-radius:6px;cursor:pointer;font-size:.8rem;font-family:inherit}
.copy:hover{background:var(--gold);color:var(--bg)}
.ok{color:var(--ok)}.err{color:var(--err)}
.muted{color:var(--muted);font-size:.85rem}
.bullets li{color:var(--muted);margin-left:24px;margin-bottom:6px;font-size:.92rem}
hr{border:none;border-top:1px solid var(--border);margin:28px 0}
</style></head><body><div class="card">${body}</div>
<script>
function copy(id,btn){const el=document.getElementById(id);navigator.clipboard.writeText(el.textContent.trim()).then(()=>{const t=btn.textContent;btn.textContent="Copied";setTimeout(()=>btn.textContent=t,1200)})}
</script></body></html>`;
}

function pageStart() {
  return htmlShell("Connect TikTok — goldennummbers", `
    <h1>Connect TikTok Posting</h1>
    <p>This authorizes the goldennummbers content scheduler to publish photo posts to <span class="handle">@telecom.store.uae</span> via the TikTok Content Posting API.</p>
    <p>Requested scopes: <code>user.info.basic</code>, <code>video.publish</code>, <code>video.upload</code>. The token is stored only on our scheduler server and is used exclusively to post to the connected profile.</p>
    <a class="btn" href="/oauth/tiktok/authorize">Connect @telecom.store.uae</a>
    <hr>
    <p class="muted">Operated by Probiz, Dubai, UAE. See our <a href="/terms/" style="color:var(--gold)">Terms</a> and <a href="/privacy/" style="color:var(--gold)">Privacy Policy</a>.</p>
  `);
}

function pageStartPinterest() {
  return htmlShell("Connect Pinterest — goldennummbers", `
    <h1>Connect Pinterest Posting</h1>
    <p>This authorizes the goldennummbers content scheduler to publish pins to the Pinterest business account <span class="handle">Telecom Store UAE</span> via the Pinterest API v5.</p>
    <p>Requested scopes: <code>boards:read</code>, <code>boards:write</code>, <code>pins:read</code>, <code>pins:write</code>, <code>user_accounts:read</code>. The token is stored only on our scheduler server and is used exclusively to post to the connected business account. No third-party data is read or written.</p>
    <a class="btn" href="/oauth/pinterest/authorize">Connect Telecom Store UAE</a>
    <hr>
    <p class="muted">Operated by Probiz, Dubai, UAE. See our <a href="/terms/" style="color:var(--gold)">Terms</a> and <a href="/privacy/" style="color:var(--gold)">Privacy Policy</a>.</p>
  `);
}

function handleTikTokOAuthAuthorize(request, env) {
  if (!env.TIKTOK_CLIENT_KEY) {
    return new Response("TIKTOK_CLIENT_KEY env var missing", { status: 500 });
  }
  const state = randomState();
  const params = new URLSearchParams({
    client_key: env.TIKTOK_CLIENT_KEY,
    scope: TIKTOK_OAUTH_SCOPES,
    response_type: "code",
    redirect_uri: TIKTOK_OAUTH_REDIRECT,
    state: state,
  });
  const target = TIKTOK_OAUTH_AUTHORIZE + "?" + params.toString();
  return new Response(null, {
    status: 302,
    headers: {
      Location: target,
      "Set-Cookie": `tiktok_oauth_state=${state}; Path=/oauth/tiktok/; Secure; HttpOnly; SameSite=Lax; Max-Age=600`,
    },
  });
}

async function handleTikTokOAuthCallback(request, env) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code") || "";
  const state = url.searchParams.get("state") || "";
  const error = url.searchParams.get("error") || "";
  const errorDesc = url.searchParams.get("error_description") || "";

  if (error) {
    return new Response(htmlShell("TikTok auth failed", `
      <h1>Authorization failed</h1>
      <p class="err">TikTok returned an error: <code>${error}</code></p>
      <p>${errorDesc}</p>
      <a class="btn" href="/oauth/tiktok/start">Try again</a>
    `), { status: 400, headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  if (!code) {
    return new Response("Missing code parameter", { status: 400 });
  }

  const cookieState = getCookie(request.headers.get("Cookie") || "", "tiktok_oauth_state");
  if (!cookieState || cookieState !== state) {
    return new Response(htmlShell("State mismatch", `
      <h1>State mismatch</h1>
      <p class="err">CSRF protection rejected this callback. Restart the flow.</p>
      <a class="btn" href="/oauth/tiktok/start">Restart</a>
    `), { status: 400, headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  if (!env.TIKTOK_CLIENT_KEY || !env.TIKTOK_CLIENT_SECRET) {
    return new Response("TIKTOK_CLIENT_KEY/SECRET env vars missing", { status: 500 });
  }

  const tokenResp = await fetch(TIKTOK_OAUTH_TOKEN, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "Cache-Control": "no-cache",
    },
    body: new URLSearchParams({
      client_key: env.TIKTOK_CLIENT_KEY,
      client_secret: env.TIKTOK_CLIENT_SECRET,
      code: code,
      grant_type: "authorization_code",
      redirect_uri: TIKTOK_OAUTH_REDIRECT,
    }).toString(),
  });

  const tokenJson = await tokenResp.json().catch(() => ({}));

  if (!tokenResp.ok || tokenJson.error || !tokenJson.access_token) {
    const errStr = JSON.stringify(tokenJson, null, 2);
    return new Response(htmlShell("Token exchange failed", `
      <h1>Token exchange failed</h1>
      <p class="err">TikTok rejected the authorization code.</p>
      <pre class="box">${errStr.replace(/</g, "&lt;")}</pre>
      <a class="btn" href="/oauth/tiktok/start">Try again</a>
    `), { status: 502, headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  const expiresAt = Math.floor(Date.now() / 1000) + (tokenJson.expires_in || 86400);
  const refreshExpiresAt = Math.floor(Date.now() / 1000) + (tokenJson.refresh_expires_in || 31536000);

  const config = {
    open_id: tokenJson.open_id,
    scope: tokenJson.scope,
    access_token: tokenJson.access_token,
    expires_at: expiresAt,
    refresh_token: tokenJson.refresh_token,
    refresh_expires_at: refreshExpiresAt,
    token_type: tokenJson.token_type || "Bearer",
    saved_at: new Date().toISOString(),
  };

  return new Response(htmlShell("TikTok connected", `
    <h1>TikTok connected</h1>
    <p class="ok">Authorization complete for open_id <code>${tokenJson.open_id || "(unknown)"}</code>.</p>
    <p>Copy the JSON below and save it on the scheduler as <code>/opt/meta-poster/tiktok_config.json</code>:</p>
    <div style="position:relative">
      <pre id="cfg" class="box" style="white-space:pre-wrap">${JSON.stringify(config, null, 2)}</pre>
      <button class="copy" style="position:absolute;top:10px;right:10px" onclick="copy('cfg',this)">Copy JSON</button>
    </div>
    <h2>Scopes granted</h2>
    <p class="muted"><code>${tokenJson.scope || "(none)"}</code></p>
    <h2>Next steps</h2>
    <ul class="bullets">
      <li>SCP this JSON to <code>loom-edge:/opt/meta-poster/tiktok_config.json</code></li>
      <li>Run <code>python3 tiktok_poster.py --once</code> to publish a queued card</li>
      <li>Add the cron line for daily posting once the test run succeeds</li>
    </ul>
    <hr>
    <p class="muted">This page is shown only on direct callback and is not indexed.</p>
  `), { status: 200, headers: {
    "Content-Type": "text/html; charset=utf-8",
    "Set-Cookie": "tiktok_oauth_state=; Path=/oauth/tiktok/; Secure; HttpOnly; SameSite=Lax; Max-Age=0",
  }});
}

// --- Pinterest API v5 OAuth --------------------------------------------------
//
// Mirror of the TikTok flow, with three Pinterest-specific differences:
//   1. Authorization URL is https://www.pinterest.com/oauth/ (no /authorize suffix)
//   2. Token endpoint at /v5/oauth/token uses HTTP Basic auth for client creds,
//      NOT body params (TikTok puts client_key + client_secret in the form body).
//   3. We always send prompt=consent so the consent screen re-appears even when
//      the app is already authorized — needed for the Standard-access upgrade
//      demo video where the reviewer must see scopes granted.

function handlePinterestOAuthAuthorize(request, env) {
  if (!env.PINTEREST_CLIENT_ID) {
    return new Response("PINTEREST_CLIENT_ID env var missing", { status: 500 });
  }
  const state = randomState();
  const params = new URLSearchParams({
    client_id: env.PINTEREST_CLIENT_ID,
    scope: PINTEREST_OAUTH_SCOPES,
    response_type: "code",
    redirect_uri: PINTEREST_OAUTH_REDIRECT,
    state: state,
    prompt: "consent",
  });
  const target = PINTEREST_OAUTH_AUTHORIZE + "?" + params.toString();
  return new Response(null, {
    status: 302,
    headers: {
      Location: target,
      "Set-Cookie": `pinterest_oauth_state=${state}; Path=/oauth/pinterest/; Secure; HttpOnly; SameSite=Lax; Max-Age=600`,
    },
  });
}

async function handlePinterestOAuthCallback(request, env) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code") || "";
  const state = url.searchParams.get("state") || "";
  const error = url.searchParams.get("error") || "";
  const errorDesc = url.searchParams.get("error_description") || "";

  if (error) {
    return new Response(htmlShell("Pinterest auth failed", `
      <h1>Authorization failed</h1>
      <p class="err">Pinterest returned an error: <code>${error}</code></p>
      <p>${errorDesc}</p>
      <a class="btn" href="/oauth/pinterest/start">Try again</a>
    `), { status: 400, headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  if (!code) {
    return new Response("Missing code parameter", { status: 400 });
  }

  const cookieState = getCookie(request.headers.get("Cookie") || "", "pinterest_oauth_state");
  if (!cookieState || cookieState !== state) {
    return new Response(htmlShell("State mismatch", `
      <h1>State mismatch</h1>
      <p class="err">CSRF protection rejected this callback. Restart the flow.</p>
      <a class="btn" href="/oauth/pinterest/start">Restart</a>
    `), { status: 400, headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  if (!env.PINTEREST_CLIENT_ID || !env.PINTEREST_CLIENT_SECRET) {
    return new Response("PINTEREST_CLIENT_ID/SECRET env vars missing", { status: 500 });
  }

  const basicAuth = btoa(`${env.PINTEREST_CLIENT_ID}:${env.PINTEREST_CLIENT_SECRET}`);
  const tokenResp = await fetch(PINTEREST_OAUTH_TOKEN, {
    method: "POST",
    headers: {
      "Authorization": `Basic ${basicAuth}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code: code,
      redirect_uri: PINTEREST_OAUTH_REDIRECT,
    }).toString(),
  });

  const tokenJson = await tokenResp.json().catch(() => ({}));

  if (!tokenResp.ok || tokenJson.error || !tokenJson.access_token) {
    const errStr = JSON.stringify(tokenJson, null, 2);
    return new Response(htmlShell("Token exchange failed", `
      <h1>Token exchange failed</h1>
      <p class="err">Pinterest rejected the authorization code.</p>
      <pre class="box">${errStr.replace(/</g, "&lt;")}</pre>
      <a class="btn" href="/oauth/pinterest/start">Try again</a>
    `), { status: 502, headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  const now = Math.floor(Date.now() / 1000);
  const expiresAt        = now + (tokenJson.expires_in || 2592000);
  const refreshExpiresAt = now + (tokenJson.refresh_token_expires_in || 31536000);

  const config = {
    scope: tokenJson.scope,
    access_token: tokenJson.access_token,
    expires_at: expiresAt,
    refresh_token: tokenJson.refresh_token,
    refresh_expires_at: refreshExpiresAt,
    token_type: tokenJson.token_type || "bearer",
    saved_at: new Date().toISOString(),
  };

  return new Response(htmlShell("Pinterest connected", `
    <h1>Pinterest connected</h1>
    <p class="ok">Authorization complete for Telecom Store UAE.</p>
    <p>Copy the JSON below and save it on the scheduler as <code>/opt/meta-poster/pinterest_config.json</code>:</p>
    <div style="position:relative">
      <pre id="cfg" class="box" style="white-space:pre-wrap">${JSON.stringify(config, null, 2)}</pre>
      <button class="copy" style="position:absolute;top:10px;right:10px" onclick="copy('cfg',this)">Copy JSON</button>
    </div>
    <h2>Scopes granted</h2>
    <p class="muted"><code>${tokenJson.scope || "(none)"}</code></p>
    <h2>Next steps</h2>
    <ul class="bullets">
      <li>SCP this JSON to <code>loom-edge:/opt/meta-poster/pinterest_config.json</code></li>
      <li>Run <code>python3 pinterest_poster.py --dry-run</code> to preview a pin payload</li>
      <li>Set <code>PINTEREST_TRIAL_MODE=0</code> on the edge only after Pinterest grants Standard access</li>
    </ul>
    <hr>
    <p class="muted">This page is shown only on direct callback and is not indexed.</p>
  `), { status: 200, headers: {
    "Content-Type": "text/html; charset=utf-8",
    "Set-Cookie": "pinterest_oauth_state=; Path=/oauth/pinterest/; Secure; HttpOnly; SameSite=Lax; Max-Age=0",
  }});
}

// ── MAINTENANCE MODE ───────────────────────────────────────────────────────
// Paused 2026-08-17 on the owner's instruction while the brands are reworked.
// TO BRING THE SITE BACK: set MAINTENANCE = false and push to main — that runs
// .github/workflows/deploy.yml, which deploys this Worker to Cloudflare.
//
// 503 + Retry-After is Google's documented signal for planned downtime: the
// URLs stay indexed and crawling is retried later. A 404/410 would instead
// tell Google the pages are gone. Deliberately NO "x-robots-tag: noindex"
// here — that would de-index the very pages the 503 is protecting. The
// response is uncacheable so the site returns the instant this flips back.
const MAINTENANCE = true;
const MAINTENANCE_RETRY_AFTER = 86400; // seconds (24h)

function maintenanceResponse() {
  const html = [
    '<!doctype html><html lang="en"><head><meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<title>Golden Numbers UAE — back shortly</title>',
    '<style>',
    ':root{color-scheme:light dark}',
    '*{box-sizing:border-box}',
    'body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;',
    'font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;',
    'background:#0d1117;color:#e6edf3}',
    '.card{max-width:520px;text-align:center}',
    'h1{font-size:clamp(22px,4vw,30px);margin:0 0 12px;letter-spacing:-.01em}',
    'p{margin:0 0 20px;color:#9aa7b4}',
    '.wa{display:inline-block;padding:12px 22px;border-radius:999px;background:#25d366;',
    'color:#04150a;font-weight:600;text-decoration:none}',
    '.wa:hover{filter:brightness(1.08)}',
    '.sub{margin-top:26px;font-size:13px;color:#6b7683}',
    '</style></head><body><div class="card">',
    '<h1>We&rsquo;re temporarily offline for updates</h1>',
    '<p>Golden Numbers UAE is being updated and will be back shortly.',
    ' Premium Etisalat numbers are still available &mdash; message us directly.</p>',
    '<a class="wa" href="https://wa.me/971569028087">WhatsApp +971 56 902 8087</a>',
    '<div class="sub">Thank you for your patience.</div>',
    '</div></body></html>',
  ].join("");
  return new Response(html, {
    status: 503,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "retry-after": String(MAINTENANCE_RETRY_AFTER),
      "cache-control": "no-store",
    },
  });
}

export default {
  async fetch(request, env) {
    if (MAINTENANCE) return maintenanceResponse();

    const url = new URL(request.url);

    if (url.pathname === "/api/tiktok-event") {
      return handleTikTokEvent(request, env);
    }

    if (url.pathname === "/r") {
      return handleRailRedirect(request);
    }

    if (url.pathname === "/oauth/tiktok/start") {
      return new Response(pageStart(), { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
    }

    if (url.pathname === "/oauth/tiktok/authorize") {
      return handleTikTokOAuthAuthorize(request, env);
    }

    if (url.pathname === "/oauth/tiktok/callback") {
      return handleTikTokOAuthCallback(request, env);
    }

    if (url.pathname === "/oauth/pinterest/start") {
      return new Response(pageStartPinterest(), { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
    }

    if (url.pathname === "/oauth/pinterest/authorize") {
      return handlePinterestOAuthAuthorize(request, env);
    }

    if (url.pathname === "/oauth/pinterest/callback") {
      return handlePinterestOAuthCallback(request, env);
    }

    // Trustpilot domain verification — serve the token file at a direct 200.
    // Static .html assets get 308-redirected to extensionless by Cloudflare's
    // default html_handling, which breaks Trustpilot's fetch of the exact .html
    // URL; this route returns the token body without a redirect.
    if (url.pathname === "/7cc945c5-a3bb-4ca1-8db4-0e568ddbd4a4.html") {
      return new Response("7cc945c5-a3bb-4ca1-8db4-0e568ddbd4a4", {
        status: 200,
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }

    // Fall through to static assets binding for everything else
    return env.ASSETS.fetch(request);
  },
};
