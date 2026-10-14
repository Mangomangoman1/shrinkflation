# ShrinkRadar worklog

## 2026-10-13
- Baseline: 79 products (Open Food Facts / Open Products Facts sizes, Open Prices USD prices). Published to GitHub Pages (Mangomangoman1/shrinkflation, gh-pages, CNAME shrinkradar.com).
- Big push: expand.py added coffee (regular/ground/instant), cereal, pasta, granola bars, candy, cheese, bread etc. with retry/backoff → 150+ products; re-ran check.py.
- Known cases: data/cases.json, 24 documented before/after cases. Sources fetched & verified: United Steelworkers shrinkflation report PDF (Mar 2024), Philadelphia Inquirer (Mar 2022), Wikipedia Shrinkflation examples list (has primary citations: BBC, Guardian, Grocer, Telegraph…).
- Not usable tonight: Reddit r/shrinkflation (JSON API returns block page without auth); Wayback mining not started. TALLY "Shrinkflation Observatory" excluded: says entries are illustrative composites.
- Features: search (search.json + vanilla JS, SearchAction JSON-LD), /cases/, /brands/, /categories/, RSS /feed.xml, 404.
- SEO: "Did X shrink?" titles/H1/answer box + FAQPage JSON-LD on product and case pages, breadcrumbs, internal links (brand/category/siblings/cases), sitemap, robots, IndexNow key file + indexnow.py (run from publish.sh).

## Next
- Wayback snapshots of manufacturer product pages to date historic sizes; per-UPC OFF revision history (product edit history often shows old quantities).
- Retailer price sources; more household products; Search Console + Bing Webmaster verification.

## 2026-10-13 (late)
- Design language "Net Wt." (DESIGN.md): nutrition-label rules, Size Facts panel, tabular numerals, signal red only for shrinks, light/dark, inline SVG sparklines, product/case cards, radar logo + favicon. Screenshots in design-shots/.

## 2026-10-14
- Post-outage expansion run: products 189 → 289 (OFF search heavily 503-throttled; stopped after retries). Second daily check: 276/289 sizes, 102 prices.
- Cases 24 → 44: +20 from Mouse Print* (Edgar Dworsky) 2025–2026 "Here We Shrink Again" posts, each figure verified in fetched page text. Wayback availability API used to attach archived copies where they exist (few so far).
- Display: label units shown (e.g. "18 oz (510 g)"), metric rounded.

## 2026-10-14 (evening) — cases library push
- data/cases.json: 44 → 573 deduped cases (merge_cases.py merges raw sources; dupes kept as "also_reported").
  - Verbraucherzentrale Hamburg Mogelpackungsliste: 335 (DE), parsed from 48 list pages (mine_vzhh.py), with old/new price.
  - Mouse Print* full archive via WP REST API (~1,100 posts), regex-mined per product section with evidence quote: 91 (US) (mine_mouseprint.py).
  - Manually curated + auto-verified snippets against fetched pages (raw/manual_cases.py): Which? (4 articles), CHOICE (3), CBC (3), foodwatch FR (2): 65.
  - Table parses: Consumer Reports Jan 2011 (10), LendingTree 2024 Wayback-based Walmart study (28): 38.
  - Seed (USW/Casey report, Inquirer, Wikipedia, Mouse Print 2025–26): 44.
- Not usable: Reddit (old.reddit/JSON redirects/blocked), X search (few posts with clear before/after; none accepted), ONS (aggregate only, no product names), ACCC (relies on CHOICE examples, already included).
- Open Food Facts revision mining (mine_off_revs.py) started; results not yet merged (needs manual review: edits can be data corrections).
- Site: filterable /cases/ (country, year, category, text), /countries/*, /years/*, evidence quotes + confidence on case pages, Dataset JSON-LD.
