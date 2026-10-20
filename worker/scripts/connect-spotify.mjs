// One-time (and every time Spotify's login expires): connect Kai Shun's Spotify account to the worker.
//   npm run connect-spotify
// Asks for the Spotify app's client id and secret, opens Spotify's consent page, catches the redirect on
// 127.0.0.1:8888, and stores the client id, secret and refresh token as worker secrets. Nothing is printed or saved
// to disk: the values go straight into `wrangler secret put` on stdin.
import http from "node:http";
import { spawn, execFile } from "node:child_process";
import { randomBytes } from "node:crypto";

const REDIRECT = "http://127.0.0.1:8888/callback";
const SCOPES = "user-read-currently-playing user-read-recently-played";

function ask(q, hidden = false) {
  return new Promise(resolve => {
    process.stdout.write(q);
    const stdin = process.stdin;
    let out = "";
    if (hidden && stdin.isTTY) stdin.setRawMode(true);
    stdin.resume(); stdin.setEncoding("utf8");
    const onData = ch => {
      for (const c of ch) {
        if (c === "\r" || c === "\n") {
          if (hidden && stdin.isTTY) stdin.setRawMode(false);
          stdin.pause(); stdin.off("data", onData); process.stdout.write("\n"); return resolve(out.trim());
        }
        if (c === "\u0003") process.exit(1);
        if (c === "\u007f") out = out.slice(0, -1); else out += c;
      }
    };
    stdin.on("data", onData);
  });
}

function putSecret(name, value) {
  return new Promise((resolve, reject) => {
    const p = spawn("npx", ["wrangler", "secret", "put", name], { stdio: ["pipe", "ignore", "inherit"] });
    p.stdin.end(value);
    p.on("exit", code => (code === 0 ? resolve() : reject(new Error(`wrangler secret put ${name} failed`))));
  });
}

const id = await ask("Spotify client id: ");
const secret = await ask("Spotify client secret (hidden): ", true);
const state = randomBytes(12).toString("hex");
const auth = `https://accounts.spotify.com/authorize?${new URLSearchParams({ client_id: id, response_type: "code", redirect_uri: REDIRECT, scope: SCOPES, state })}`;

const code = await new Promise((resolve, reject) => {
  const server = http.createServer((req, res) => {
    const u = new URL(req.url, REDIRECT);
    if (u.pathname !== "/callback") return res.writeHead(404).end();
    res.writeHead(200, { "Content-Type": "text/plain" }).end("Done. You can close this tab.");
    server.close();
    if (u.searchParams.get("state") !== state) return reject(new Error("state mismatch"));
    if (u.searchParams.get("error")) return reject(new Error(u.searchParams.get("error")));
    resolve(u.searchParams.get("code"));
  }).listen(8888, "127.0.0.1", () => {
    console.log("Opening Spotify in your browser. Approve, then come back here.");
    execFile("open", [auth]);
  });
});

const r = await fetch("https://accounts.spotify.com/api/token", {
  method: "POST",
  headers: { Authorization: "Basic " + Buffer.from(`${id}:${secret}`).toString("base64"), "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ grant_type: "authorization_code", code, redirect_uri: REDIRECT }),
});
if (!r.ok) { console.error(`Spotify refused the code (${r.status}). Check the client id, secret and redirect URI.`); process.exit(1); }
const { refresh_token } = await r.json();
await putSecret("SPOTIFY_CLIENT_ID", id);
await putSecret("SPOTIFY_CLIENT_SECRET", secret);
await putSecret("SPOTIFY_REFRESH_TOKEN", refresh_token);
console.log("Connected. The worker can now read what you're playing.");
