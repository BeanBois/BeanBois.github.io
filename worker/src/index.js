// What Kai Shun is listening to, for the record on beanbois.github.io.
//   GET /now        {is_playing, title, artist, url, art, duration_ms, progress_ms, bpm, played_at, fetched_at}
//   GET /art?u=…    a Spotify cover image, re-served with CORS so the page can print it as screentone
// Secrets (wrangler secret put): SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN.
// KV (binding MUSIC): the current access token, a rotated refresh token if Spotify sends one, and tempo per track.

const SITES = ["https://beanbois.github.io", "http://localhost:8765", "http://127.0.0.1:8765"];
const FRESH_MS = 15000;     // every visitor polls; Spotify is asked at most once per 15 s per isolate
let last = { at: 0, body: null };

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get("Origin");
    const cors = { "Access-Control-Allow-Origin": SITES.includes(origin) ? origin : SITES[0], "Vary": "Origin" };
    try {
      if (url.pathname === "/now") return json(await now(env, url), cors);
      if (url.pathname === "/art") return art(url);
      return new Response("not found", { status: 404 });
    } catch (e) {
      console.log("error", e.message);
      return json({ is_playing: false, error: "unavailable" }, cors, 503);
    }
  },
};

const json = (body, cors, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { ...cors, "Content-Type": "application/json", "Cache-Control": "no-store" },
});

async function now(env, url) {
  if (last.body && Date.now() - last.at < FRESH_MS) return last.body;
  const h = { Authorization: "Bearer " + (await accessToken(env)) };
  let item = null, playing = false, progress = 0, played_at = null;
  const cur = await fetch("https://api.spotify.com/v1/me/player/currently-playing", { headers: h });
  if (cur.status === 200) {
    const j = await cur.json();
    if (j.item && j.currently_playing_type === "track") { item = j.item; playing = !!j.is_playing; progress = j.progress_ms || 0; }
  }
  if (item && !playing) played_at = Date.now();        // paused: show it as the last thing played
  if (!item) {
    const rec = await fetch("https://api.spotify.com/v1/me/player/recently-played?limit=1", { headers: h });
    if (rec.ok) {
      const x = (await rec.json()).items?.[0];
      if (x) { item = x.track; played_at = Date.parse(x.played_at); progress = 0; }
    }
  }
  let body = { is_playing: false, fetched_at: Date.now() };
  const hidden = (env.HIDE_ARTISTS || "").toLowerCase().split(",").map(s => s.trim()).filter(Boolean);
  if (item && !item.artists.some(a => hidden.includes(a.name.toLowerCase()))) {
    const cover = item.album?.images?.[0]?.url;
    body = {
      is_playing: playing, title: item.name, artist: item.artists.map(a => a.name).join(", "),
      url: item.external_urls?.spotify || null,
      art: cover ? `${url.origin}/art?u=${encodeURIComponent(cover)}` : null,
      duration_ms: item.duration_ms, progress_ms: progress, bpm: await tempo(item.id, env),
      played_at, fetched_at: Date.now(),
    };
  }
  last = { at: Date.now(), body };
  return body;
}

async function accessToken(env) {
  const cached = await env.MUSIC.get("access", "json");
  if (cached && cached.exp > Date.now() + 60000) return cached.token;
  const refresh = (await env.MUSIC.get("refresh")) || env.SPOTIFY_REFRESH_TOKEN;
  const r = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: { Authorization: "Basic " + btoa(`${env.SPOTIFY_CLIENT_ID}:${env.SPOTIFY_CLIENT_SECRET}`), "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "refresh_token", refresh_token: refresh }),
  });
  if (!r.ok) throw new Error(`token refresh failed: ${r.status}`);
  const j = await r.json();
  if (j.refresh_token) await env.MUSIC.put("refresh", j.refresh_token);
  await env.MUSIC.put("access", JSON.stringify({ token: j.access_token, exp: Date.now() + j.expires_in * 1000 }), { expirationTtl: Math.max(60, j.expires_in) });
  return j.access_token;
}

// Spotify closed its tempo data to new apps (Nov 2024); ReccoBeats serves it by Spotify id for most tracks.
// Cached per track for 30 days, including "not found", so each track is looked up once.
async function tempo(id, env) {
  if (!id) return null;
  const hit = await env.MUSIC.get("bpm:" + id);
  if (hit !== null) return hit === "none" ? null : Number(hit);
  let bpm = null;
  try {
    const r = await fetch(`https://api.reccobeats.com/v1/audio-features?ids=${id}`);
    if (r.ok) { const t = (await r.json()).content?.[0]?.tempo; if (t) bpm = Math.round(t); }
  } catch {}
  await env.MUSIC.put("bpm:" + id, bpm ? String(bpm) : "none", { expirationTtl: 30 * 86400 });
  return bpm;
}

async function art(url) {
  const u = url.searchParams.get("u") || "";
  if (!/^https:\/\/i\.scdn\.co\/image\/[a-z0-9]+$/i.test(u)) return new Response("bad image", { status: 400 });
  const r = await fetch(u, { cf: { cacheTtl: 86400, cacheEverything: true } });
  return new Response(r.body, {
    status: r.status,
    headers: { "Content-Type": r.headers.get("Content-Type") || "image/jpeg", "Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=86400" },
  });
}
