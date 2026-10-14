// ShrinkRadar alerts API — Cloudflare Worker + D1 + Resend.
const KINDS = new Set(["all", "product", "brand", "category"]);
const EMAIL_RE = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/;
const cors = (env) => ({ "access-control-allow-origin": env.SITE, "access-control-allow-methods": "GET,POST,OPTIONS", "access-control-allow-headers": "content-type" });
const json = (env, o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json", ...cors(env) } });
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const tok = () => [...crypto.getRandomValues(new Uint8Array(24))].map((b) => b.toString(16).padStart(2, "0")).join("");
const page = (env, title, body) => new Response(
  `<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><meta name=robots content=noindex><link rel=stylesheet href="${env.SITE}/style.css"><title>${esc(title)} | ShrinkRadar</title>` +
  `<header><div class=w><div class=top><a class=brand href="${env.SITE}/">Shrink<b>Radar</b></a></div></div></header><main class=w><div class=prose>${body}</div></main>`,
  { headers: { "content-type": "text/html; charset=utf-8" } });

async function sendEmail(env, to, subject, html, text, unsubUrl) {
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST", headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ from: env.FROM, to: [to], subject, html, text,
      headers: unsubUrl ? { "List-Unsubscribe": `<${unsubUrl}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" } : {} }) });
  if (!r.ok) throw new Error("send failed " + r.status);
  return (await r.json()).id;
}
function parseScopes(arr, max) {
  const out = [];
  for (const s of (Array.isArray(arr) ? arr : []).slice(0, max)) {
    const i = String(s).indexOf(":"); const kind = String(s).slice(0, i), key = String(s).slice(i + 1).slice(0, 80);
    if (KINDS.has(kind) && /^[A-Za-z0-9-]+$/.test(key)) out.push({ kind, key });
  }
  return out;
}

async function subscribe(req, env) {
  const b = await req.json().catch(() => ({}));
  if (b.hp) return json(env, { ok: true });                      // honeypot
  const email = String(b.email || "").trim().toLowerCase();
  if (!EMAIL_RE.test(email)) return json(env, { error: "invalid email" }, 400);
  const scopes = parseScopes(b.scopes, +env.FREE_MAX_SUBS);
  if (!scopes.length) return json(env, { error: "no scopes" }, 400);
  let s = await env.DB.prepare("SELECT * FROM subscribers WHERE email=?").bind(email).first();
  if (!s) { await env.DB.prepare("INSERT INTO subscribers(email,token,source) VALUES(?,?,?)").bind(email, tok(), String(b.source || "").slice(0, 200)).run();
            s = await env.DB.prepare("SELECT * FROM subscribers WHERE email=?").bind(email).first(); }
  const ins = env.DB.prepare("INSERT OR IGNORE INTO subscriptions(subscriber_id,kind,key) VALUES(?,?,?)");
  await env.DB.batch(scopes.map((x) => ins.bind(s.id, x.kind, x.key)));
  if (s.status !== "active") {
    // don't re-send confirmation more than once per 10 min (abuse guard)
    if (!s.last_sent_at || Date.now() - Date.parse(s.last_sent_at + "Z") > 6e5) {
      const url = `${new URL(req.url).origin}/confirm?t=${s.token}`;
      await sendEmail(env, email, "Confirm your ShrinkRadar alerts",
        `<p>Confirm you want ShrinkRadar shrinkflation alerts:</p><p><a href="${url}"><b>Confirm subscription</b></a></p><p>If you didn't ask for this, ignore this email; nothing more will be sent.</p>`,
        `Confirm your ShrinkRadar alerts: ${url}\nIf you didn't ask for this, ignore this email.`);
      await env.DB.prepare("UPDATE subscribers SET status='pending',last_sent_at=datetime('now') WHERE id=?").bind(s.id).run();
    }
  }
  return json(env, { ok: true, pending: s.status !== "active" });
}

async function manage(req, env, url) {
  const t = url.searchParams.get("t") || ""; const s = await env.DB.prepare("SELECT * FROM subscribers WHERE token=?").bind(t).first();
  if (!s) return page(env, "Link expired", "<h1>Link not valid</h1>");
  if (req.method === "POST") {
    const f = await req.formData();
    if (f.get("action") === "delete") { await env.DB.prepare("DELETE FROM subscribers WHERE id=?").bind(s.id).run(); return page(env, "Deleted", "<h1>All data deleted</h1>"); }
    const keep = new Set(f.getAll("keep")); const rows = (await env.DB.prepare("SELECT kind,key FROM subscriptions WHERE subscriber_id=?").bind(s.id).all()).results;
    const del = env.DB.prepare("DELETE FROM subscriptions WHERE subscriber_id=? AND kind=? AND key=?");
    const ops = rows.filter((r) => !keep.has(r.kind + ":" + r.key)).map((r) => del.bind(s.id, r.kind, r.key));
    if (ops.length) await env.DB.batch(ops);
  }
  const rows = (await env.DB.prepare("SELECT kind,key FROM subscriptions WHERE subscriber_id=? ORDER BY kind,key").bind(s.id).all()).results;
  const li = rows.map((r) => `<label class=ck><input type=checkbox name=keep value="${esc(r.kind + ":" + r.key)}" checked> ${esc(r.kind)}: ${esc(r.key)}</label>`).join("") || "<p>You follow nothing.</p>";
  return page(env, "Manage alerts", `<h1>Your alerts</h1><p class=m>${esc(s.email)} · ${esc(s.status)} · plan ${esc(s.plan)}</p><form method=post>${li}<p><button>Save</button> <button name=action value=delete>Delete all my data</button></p></form><p><a href="${env.SITE}/alerts/">Add more</a> · <a href="/unsubscribe?t=${esc(t)}">Unsubscribe from everything</a></p>`);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { headers: cors(env) });
    if (url.pathname === "/subscribe" && req.method === "POST") return subscribe(req, env);
    if (url.pathname === "/confirm") {
      const r = await env.DB.prepare("UPDATE subscribers SET status='active',confirmed_at=datetime('now') WHERE token=? AND status!='unsubscribed'").bind(url.searchParams.get("t") || "").run();
      return page(env, "Confirmed", r.meta.changes ? `<h1>You're subscribed</h1><p>Digests arrive at most once a day. <a href="/manage?t=${esc(url.searchParams.get("t"))}">Manage alerts</a></p>` : "<h1>Link not valid</h1>");
    }
    if (url.pathname === "/manage") return manage(req, env, url);
    if (url.pathname === "/unsubscribe") {   // GET shows page, POST = RFC 8058 one-click
      const t = url.searchParams.get("t") || "";
      if (req.method === "POST") { await env.DB.prepare("UPDATE subscribers SET status='unsubscribed' WHERE token=?").bind(t).run();
        await env.DB.prepare("DELETE FROM subscriptions WHERE subscriber_id=(SELECT id FROM subscribers WHERE token=?)").bind(t).run();
        return page(env, "Unsubscribed", "<h1>Unsubscribed</h1><p>You won't get more alerts.</p>"); }
      return page(env, "Unsubscribe", `<h1>Unsubscribe?</h1><form method=post><button>Unsubscribe from all ShrinkRadar alerts</button></form>`);
    }
    // ---- admin API for the daily job (Bearer ADMIN_TOKEN) ----
    if (url.pathname.startsWith("/admin/")) {
      if (req.headers.get("authorization") !== `Bearer ${env.ADMIN_TOKEN}`) return new Response("forbidden", { status: 403 });
      if (url.pathname === "/admin/subscriptions") {
        const r = (await env.DB.prepare("SELECT s.id,s.email,s.token,s.plan,x.kind,x.key FROM subscribers s JOIN subscriptions x ON x.subscriber_id=s.id WHERE s.status='active'").all()).results;
        return json(env, r);
      }
      if (url.pathname === "/admin/send" && req.method === "POST") {   // {subscriber_id, day, to, subject, html, text, unsub, item_ids}
        const m = await req.json();
        const dup = await env.DB.prepare("SELECT 1 FROM sends WHERE subscriber_id=? AND day=?").bind(m.subscriber_id, m.day).first();
        if (dup) return json(env, { skipped: "already sent" });
        const id = await sendEmail(env, m.to, m.subject, m.html, m.text, m.unsub);
        await env.DB.prepare("INSERT INTO sends VALUES(?,?,?,?)").bind(m.subscriber_id, m.day, JSON.stringify(m.item_ids || []), id).run();
        await env.DB.prepare("UPDATE subscribers SET last_sent_at=datetime('now') WHERE id=?").bind(m.subscriber_id).run();
        return json(env, { ok: true, id });
      }
    }
    return new Response("not found", { status: 404 });
  },
  // cron: delete unconfirmed sign-ups older than 7 days
  async scheduled(_e, env) { await env.DB.prepare("DELETE FROM subscribers WHERE status='pending' AND created_at<datetime('now','-7 days')").run(); },
};
