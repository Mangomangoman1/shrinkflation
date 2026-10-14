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

## 2026-10-13 — case library 573 → 671
- New: Consumentenbond NL (mine_cb.py, 56), Guardian UK, Brut AU, OCU ES, ORF/AK AT, Altroconsumo/La Stampa IT, Procon Niterói BR, NPR 2022 (US/UK/IN), CNN Tostitos. All snippets verified against fetched pages (verify_manual.py, 110 ok).
- OFF revisions: 3 flags reviewed (Roncadin/Costco pizza relabel, generic Coca-Cola code, Nature Valley per-bar vs box) — all data corrections, 0 accepted. Miner still running (~90/289 products).
- "Other" category: 0 (regex + CATFIX overrides for NL/IT/ES names). Added NL/ES/AT/IT/BR/IN to country maps.
- Not done: Wayback mining. Inaccessible: Korea KCA (IP block/queue; Yonhap/Donga fetch failed), RadarSuper 429, CB 2022/2023 404, Reddit, G1 category-only.
- Published, IndexNow 200 (1635 URLs).

## 2026-10-14 — email alerts (built, not live)
- Stack: Cloudflare Worker + D1 + Resend (alerts/). Double opt-in, manage, RFC 8058 one-click unsubscribe, free/pro plan column, idempotent daily sends.
- The site has alert boxes on product, case, brand and category pages, plus /alerts/ (follow everything) and a privacy section on About. They stay disabled ("Coming soon") until alerts_config.json sets the API.
- daily.sh runs alerts/digest.py, a dry run by default. Baseline: 671 items. Sample email: design-shots/alert-email.png.
- Fix: Cocoa Puffs and Reese's Puffs were categorised as Tissues; they are now Breakfast Cereals.

## 2026-10-14 (features run) — worst offenders + shrinkflation calculator
- New /worst/ leaderboard: biggest hidden per-unit price hikes (391 cases with before/after shelf prices; top is Lebensbaum Tomaten-Gewürzsalz, 150 g → 80 g and 2,99 € → 3,99 €, +150% per gram), biggest package cuts, repeat-offender brands (≥3 cases; Aldi 11, Ostmann 9, Charmin 9), and categories by median cut. ItemList JSON-LD.
- New /calculator/: before/after size and price → size cut, unit price per 100 g/ml (or per unit), real price change, fair price for the new pack. Shareable URL params, runs fully in the browser, FAQ + WebApplication JSON-LD. Every case page has a "Check the math" link that prefills it.
- Case pages: new "Real price change per <unit>" row when the source recorded both prices.
- Nav: Worst offenders and Calculator added; homepage links to both.
- QA fixes: brand mis-detection ("Dr." → Dr. Oetker / Dr. Hauschka; "All" matched "All in 1" on Spee, Garnier, Sun); foreign unit words normalised (Stück → pieces, Waschladungen → loads, luiers → diapers, grams → g). Old /brands/dr.html kept as a noindex stub. Internal link check: 0 broken across 1,640 pages. Screenshots: design-shots/calc-*.png, worst-*.png.
