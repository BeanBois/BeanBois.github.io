// What Kai Shun is listening to, for the record on beanbois.github.io.
//   GET /now        {is_playing, title, artist, url, art, duration_ms, progress_ms, bpm, played_at, fetched_at}
//   GET /art?u=…    a Spotify cover image, re-served with CORS so the page can print it as screentone
// Secrets (wrangler secret put): SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN.
// KV (binding MUSIC): the current access token, a rotated refresh token if Spotify sends one, and tempo per track.
import MANUAL from "./bpm.json";

const SITES = ["https://beanbois.github.io", "http://localhost:8765", "http://127.0.0.1:8765"];
const FRESH_MS = 4000;      // every visitor polls; Spotify is asked at most once per 4 s per isolate
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
      duration_ms: item.duration_ms, progress_ms: progress, ...(await tempo(item, env)),
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

// The tempo bank. Spotify closed its tempo data to new apps (Nov 2024), so a track's BPM comes from the most
// trusted source that knows it; the first hit wins. Exact-id sources rank above anything matched by search.
//   1 manual      bpm.json in this repo: Kai Shun's own count, always wins
//   2 reccobeats  audio features looked up by Spotify id
//   3 deezer      the same recording, matched by ISRC
//   4 deezer      a search, kept only if title, artist and length (±3 s) all agree
// Results are cached in KV with their source: hits for 90 days, misses for a day so a new source gets a retry.
const TIERS = [
  ["reccobeats", async item => {
    const r = await fetch(`https://api.reccobeats.com/v1/audio-features?ids=${item.id}`);
    return r.ok ? (await r.json()).content?.[0]?.tempo : null;
  }],
  ["deezer-isrc", async item => {
    const isrc = item.external_ids?.isrc;
    if (!isrc) return null;
    const r = await fetch(`https://api.deezer.com/track/isrc:${isrc}`);
    return r.ok ? (await r.json()).bpm : null;
  }],
  ["deezer-search", async item => {
    const norm = s => (s || "").toLowerCase().replace(/\(.*?\)|\[.*?\]|-.*remaster.*$/g, "").replace(/[^a-z0-9]+/g, " ").trim();
    const artist = item.artists[0]?.name;
    const r = await fetch(`https://api.deezer.com/search?q=${encodeURIComponent(`${artist} ${item.name}`)}&limit=5`);
    if (!r.ok) return null;
    const hit = ((await r.json()).data || []).find(h => norm(h.title) === norm(item.name) && norm(h.artist?.name) === norm(artist)
      && Math.abs(h.duration * 1000 - item.duration_ms) <= 3000);
    if (!hit) return null;
    const d = await fetch(`https://api.deezer.com/track/${hit.id}`);
    return d.ok ? (await d.json()).bpm : null;
  }],
];

async function tempo(item, env) {
  if (!item.id) return { bpm: null, bpm_source: null };
  if (MANUAL[item.id]?.bpm) return { bpm: MANUAL[item.id].bpm, bpm_source: "manual" };
  const hit = await env.MUSIC.get("tempo:" + item.id, "json");
  if (hit) return { bpm: hit.bpm, bpm_source: hit.source };
  for (const [source, look] of TIERS) {
    let bpm = null;
    try { bpm = await look(item); } catch {}
    if (bpm > 30 && bpm < 300) {
      bpm = Math.round(bpm);
      await env.MUSIC.put("tempo:" + item.id, JSON.stringify({ bpm, source }), { expirationTtl: 90 * 86400 });
      return { bpm, bpm_source: source };
    }
  }
  await env.MUSIC.put("tempo:" + item.id, JSON.stringify({ bpm: null, source: null }), { expirationTtl: 86400 });
  return { bpm: null, bpm_source: null };
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
