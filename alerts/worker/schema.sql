-- ShrinkRadar alerts (Cloudflare D1 / SQLite)
CREATE TABLE IF NOT EXISTS subscribers(
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  token TEXT NOT NULL UNIQUE,            -- secret for confirm/manage/unsubscribe links
  status TEXT NOT NULL DEFAULT 'pending',-- pending | active | unsubscribed
  plan TEXT NOT NULL DEFAULT 'free',     -- free | pro (future paid tier)
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  confirmed_at TEXT, last_sent_at TEXT, source TEXT
);
CREATE TABLE IF NOT EXISTS subscriptions(
  subscriber_id INTEGER NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK(kind IN ('all','product','brand','category')),
  key TEXT NOT NULL,                     -- product UPC / brand slug / category slug / 'all'
  label TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY(subscriber_id,kind,key)
);
CREATE TABLE IF NOT EXISTS sends(        -- idempotency log for daily digests
  subscriber_id INTEGER NOT NULL, day TEXT NOT NULL, item_ids TEXT, provider_id TEXT,
  PRIMARY KEY(subscriber_id,day)
);
CREATE INDEX IF NOT EXISTS sub_kind_key ON subscriptions(kind,key);
