# ShrinkRadar email alerts

Stack: Cloudflare Worker + D1 (alerts.shrinkradar.com) + Resend for email. Static site stays on GitHub Pages.

- `worker/`: API (subscribe → double opt-in, confirm, manage, one-click unsubscribe per RFC 8058, admin export/send, 7-day purge of unconfirmed sign-ups). `schema.sql` holds the D1 schema (`plan` free|pro).
- `digest.py`: daily job. It diffs `data/alert_items.json` (written by build_site.py) against `state.json`, matches all/product/brand/category subscriptions, and renders one digest per subscriber. Dry run by default, writing `out/<day>/<id>.html|.txt`. `--send` sends through the worker (idempotent per subscriber per day). The first run only records a baseline.
- Demo: `python3 alerts/digest.py --subs alerts/sample_subs.json --all-as-new --state /tmp/s.json`

## Go-live
1. `npm i -g wrangler && wrangler login`
2. `wrangler d1 create shrinkradar-alerts`, then paste the id into wrangler.toml, then `wrangler d1 execute shrinkradar-alerts --remote --file worker/schema.sql`
3. `wrangler secret put RESEND_API_KEY` and `wrangler secret put ADMIN_TOKEN` (a random 32+ char string)
4. `cd worker && wrangler deploy` (custom domain alerts.shrinkradar.com)
5. Write `alerts_config.json` at the repo root as `{"api":"https://alerts.shrinkradar.com"}`, then run `./publish.sh`. The forms become active.
6. Run daily with `ALERTS_SEND=1 ALERTS_API=https://alerts.shrinkradar.com ALERTS_ADMIN_TOKEN=... ./daily.sh`
