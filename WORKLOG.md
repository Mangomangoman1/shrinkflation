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

## 2026-10-15 — data-expansion routine
- products 289 → 340 (+51 net; dropped junk/misclassified creamer-drink rows from OPF/OFF pulls). Household/beauty via Open Products Facts + Open Beauty Facts (OFF search was 503 early in run, later recovered for coffee/cereal): Toilet Paper 3→8, Laundry Detergent 4→13, Dish Soap 3→6, Facial Tissues 0→1, Toothpaste/Shampoo/Deodorant/Mouthwash new categories; +4 US breakfast cereals + Folgers Classic Roast. Paper Towels stayed 4 (OPF brand searches lacked product_quantity). Snapshots for all new codes today (52/52 size ok on first batch; 5 OFF adds also snapped).
- cases 671 → 687 (+16 after merge_cases dedupe):
  - Mouse Print* Fall 2025 Part 2 (was missing from prior mine): Ziploc 280→270 bags; Bounty Mega 180→164 sheets; Viva Triple 133→121 sheets; Cascade Platinum Plus 52→47 pods; SeaPak Popcorn Shrimp 16→14 oz; Little Debbie cupcakes 8→6.
  - CBC Halloween 2025: Mars 65-bar fun size 782→672 g; Hershey’s 50 mini bars 513→481 g (CA).
  - Guardian / Which? UK Easter 2026: Maltesers XL 231→194 g; Cadbury Twirl XL 241→218 g; Cadbury Mini Eggs family 270→256 g; Galaxy XL egg 252→210 g; M&M’s Crispy egg 192→156 g; Cadbury Mini Eggs Easter egg 193.5→181 g; Toblerone Edgy Egg 298→256 g; Cadbury Dairy Milk & White Shell 372→360 g.
- OFF revision flags (6): all rejected (Roncadin data correction; Coke SKU/market mix; Nature Valley 1.5→1.49 labeling noise; Campbell’s 10.75↔10.5 contested/no clear secondary; Nixe net vs drained; Jaouda no secondary). Notes in raw/off_rev_review_2026-10-15.json; off_rev_final.json still [].
- Tried: Wayback CDX (Folgers homepage history OK; charmin sheets empty; availability API 429 after a few calls — mining not productive yet). X posts: vague rants only (Degree 2.7→2.6 uncorroborated) — 0 accepted. Mouse Print WP REST: no newer “Here We Shrink” posts after Spring 2026 Part 2. Reddit still unusable.
- Tiny fix: check.py HOST map now includes Open Beauty Facts (`obf`).
- Site rebuilt (1744 pages, 687 cases). Publish + IndexNow via publish.sh.

## 2026-10-15 — SEO and growth routine
- Head tags on every page: og:image (+ width, height, alt), twitter:card `summary_large_image`, twitter:title, twitter:description, twitter:image, theme-color #111. The share image is `/og.png` (1200×630, drawn with Pillow at build time), because X, Facebook and LinkedIn don't render SVG og:images. `/og.svg` ships alongside as the vector source.
- Brand and category pages (597 brands + 71 categories, all 668 with FAQPage): there is now a Size Facts answer box for "Did {name} products shrink?". It shows the verdict, number of cases, biggest and median cut, years, countries and how many products we track daily. 438 pages say Yes. The rest say "Not in our case library yet. We track N … daily". Cases are sorted by biggest cut. Pages with cases get a prose line linking to /worst/ and /calculator/. Meta descriptions now lead with the answer.
- Country pages (13): FAQPage "Has shrinkflation hit {country}?". The answer gives the case count and the biggest cut. They also link to /worst/ and the how-to guide.
- New /guides/: a hub (guide cards, brands with ≥5 cases, categories by case count, ItemList JSON-LD), /guides/what-is-shrinkflation.html (Article + FAQPage, live figures: median cut, biggest case, priced cases) and /guides/how-to-spot-shrinkflation.html (5-step checklist, Article + FAQPage + HowTo). Guides are in the nav (after Categories), search.json (k="Guide"), the homepage and About.
- /llms.txt: what the site is, key URLs, feed, sitemap and search.json, plus a citation note. robots.txt unchanged (Allow all + Sitemap; AI crawlers not blocked).
- Build: 1742 pages. Internal link check: 0 broken. Published (gh-pages 17c5248). IndexNow 200 (1742 URLs). Live 200: /guides/, both guides, /og.png, /og.svg, /llms.txt. The Cadbury brand page is live with FAQPage and twitter:card.
- Data follow-up noticed: some case categories are wrong, e.g. "Cadbury Dairy Milk Freddo multipack" is in Juice & Drinks and "Cadbury Brunch bars" is in Dairy ("Milk" keyword). These need CATFIX entries in merge_cases.py and a sweep of the "Milk"/"Drink" keyword matches.

## 2026-10-15 — structured-data notification fixes
- Expanded /cases/ Dataset description to satisfy Google's 50–5,000-character requirement.
- Replaced tracking-page Product JSON-LD with WebPage metadata. Open Prices snapshots are historical observations, not current offers; no prices, reviews or ratings invented. Product names, brand, category, identifiers, size and price history remain visible unchanged.
- Added validate_structured_data.py: parsed 3,801 JSON-LD blocks across all 1,744 HTML files (1,742 generated sitemap pages plus existing files); checked the Dataset and all 340 tracking pages. All passed. HTML comparison confirmed that only JSON-LD changed on the 341 affected pages.
- Local rebuild preserved the existing og.png because its hardcoded Liberation Sans font is unavailable in this environment.
- Published source commit 9d39eff and gh-pages commit 83b0158. GitHub Pages deployment 38809814870 succeeded. Live /cases/ and Google's affected bettergoods tortilla-chip URL both returned HTTP 200 and matched the corrected generated files exactly; Dataset description is 128 characters.
- After Samuel signed in, verified both Search Console reports (one affected item each) and submitted Validate Fix for both. Both now show Validation Started, October 15, 2026. Final Google pass/recrawl remains pending.

## 2026-10-15 — features & quality: Submit a sighting + category fixes
- **Feature: /submit/** — static “Submit a sighting” form (client-side only). Fields: product*, brand, category, country, when, old/new size+unit*, optional prices + currency, store, evidence URL, notes, optional email. On submit: validates required fields, opens a prefilled GitHub issue (`Sighting: {product} ({old} → {new})` + markdown table body) on Mangomangoman1/shrinkflation; copy-to-clipboard fallback if the pop-up is blocked. FAQ + WebPage/WebApplication/FAQPage JSON-LD. Explains we verify before adding; no guarantee of inclusion. Linked from nav (after Calculator), homepage, About, /cases/, /worst/, search.json, sitemap, llms.txt. Form CSS + mobile (<600px) rules for full-width fields/button.
- **Data quality:** root cause of Cadbury/etc. mis-cats was `cola` matching inside `chocolate` (Juice & Drinks before Chocolate & Candy), plus Dairy `brunch`/`milk` catching Cadbury Brunch and Dairy Milk candy. Fixes in merge_cases.py: `\bcola\b`, tightened `milk`/`brunch` lookarounds, and **ALWAYS_FIX** product-substring map that always wins (not only when category==Other). Re-ran merge_cases.py (687 cases unchanged count).
  - **39 recategorized** from the known false-positive set: 35 → Chocolate & Candy (incl. Cadbury Dairy Milk Freddo multipack, all other Cadbury candy/eggs, KitKat, Toblerone, Hershey’s, M&M’s, Maltesers, Twix, Mars fun size, Little Debbie Chocolate Cupcakes, Moser Roth, HEJ bar, Milkybar…), 1 → Cookies (McVitie’s Digestives Dark Chocolate), 1 → Ice Cream (Mövenpick Eis Vanilla Chocolate), 2 → Frozen (Danerolles Chocolate Croissants / Pains au Chocolat). Cadbury Brunch bars → Chocolate & Candy. Juice & Drinks now 32; Chocolate & Candy 115. Remaining Juice false positives: 0 in the chocolate/candy sweep.
- Build: 1745 pages (build_site.py). Internal link check: 0 broken (46k+ hrefs).
- Published: source `530f522`, gh-pages `a090ac7`. IndexNow 200 (1745 URLs). Live QA: /submit/ 200 with form + window.open; Freddo and Cadbury Brunch case pages show chocolate-and-candy. Pages deploy 38826629260 succeeded.

### Samuel-only asks
- Google Search Console: verify shrinkradar.com (DNS TXT is best; an HTML file or meta tag works too, send me the token and I'll ship it) and submit /sitemap.xml. Without this we get no feedback on indexing or queries.
- Bing Webmaster Tools: verify the site (it can import from GSC) and submit the sitemap. IndexNow already pings Bing.
- Social accounts (X etc.) if you want distribution. I won't create accounts.

### Legitimate distribution ideas (not done; no outreach without approval)
- Wikipedia "Shrinkflation": only an external link, and only if it meets WP:EL, e.g. as a sourced dataset. Never self-cite into article text.
- Consumer journalists and consumer-desk tipsheets (Mouse Print*, Which?, CBC Marketplace, local TV consumer reporters) once a daily-check finding or a strong dataset angle exists, e.g. "the worst hidden per-unit price hikes".
- Show HN when alerts are live and the daily checks have logged real findings.
- Non-spam listings: data portals (Kaggle/data.world dataset of the case library under CC BY), Open Food Facts community/reuse pages, personal-finance and frugal-living resource lists that take submissions.

## 2026-10-16 — data-expansion (morning)
- **Products:** 340 → 385 (+45 net). Focus: US coffee (Dunkin', Peet's, Community, more Starbucks/Folgers), breakfast cereals (Lucky Charms, Frosted Flakes 21.7 oz, Raisin Bran, Cocoa Puffs, Special K Cinnamon & Pecan, Frosted Flakes w/ marshmallows), household (Bounty Select-A-Size, Kirkland towels, Charmin Ultra Soft/Strong, Cottonelle, Angel Soft mega rolls, Kleenex AU/EU packs with qty, Puffs Plus Lotion, Glad sandwich bags). Categories after: Breakfast Cereals 20, Ground Coffees 15, Coffees 12, Toilet Paper 24 (was 8, mostly US Charmin/Cottonelle/Angel Soft), Paper Towels 7, Facial Tissues 6, Food Storage Bags 2.
- **Snapshots:** 1158 → 1203. Targeted check.py for 45 new codes: 19 with numeric size, 26 size_missing (typical OPF paper/TP without product_quantity). Latest unique: missing size ~39 (was ~13), missing USD price ~269 (was ~233) — rise is mostly new paper SKUs without Open Prices/OFF quantity.
- **Cases:** 687 → 691 (+4 verified):
  - Atkins Protein Bars 5 → 4 bars (US, Mouse Print* Winter 2026 Part 1)
  - Finish Ultimate Dishwashing Pods 76 → 62 pods (US, same)
  - Cadbury hollow hunting eggs carton 22 → 20 eggs (AU, CHOICE Mar 2026)
  - Cadbury boxed hollow Easter eggs 18 → 15 eggs (AU, CHOICE Mar 2026)
- **Sources tried:** Mouse Print WP REST (newest shrink post still Spring 2026 Part 2; Sept 2026 is skimpflation/protein — not size shrink). Winter 2026 posts re-fetched; miner had missed Atkins/Finish (no “from X to Y” pattern for pack-count). CHOICE Easter 2026 media release. LendingTree 2024 tables already fully covered. CBC Halloween 2025 Mars/Hershey already in library (Hershey 100-pack 3.8% lacked exact grams — skipped). Guardian/Which Easter 2026 Galaxy/M&M/Maltesers already present. OFF world/us search API 503 most of the run; used product-by-barcode + fr mirror when available + OPF cgi/API. Reddit not re-tried (known block). Wayback not hammered (prior 429). X not used (no clear before→after + corroboration). OFF revision flags: left off_rev_final.json empty.
- **Rejected / not logged:** Mary's Gone Crackers (Mouse Print “>25%” without oz; company also launched 7 oz family size — ambiguous). Krusteaz “>20%” without oz. Scotts Turf Builder coverage change without clear single bag weight pair. Aldi hot cross buns “20g lighter” without prior weight. Cap'n Crunch OFF entries exist but product_quantity null. Dunkin junk (donuts, iced drinks, tea) filtered out.
- **Build:** 1799 pages, 691 cases, 385 products. New case pages + Charmin/Angel Soft/Frosted Flakes product pages present.
- **Publish:** source `3c1c742`, gh-pages `4ce880f`. IndexNow 200 (1799 URLs). Live smoke (after Pages built): /, Atkins/Finish/Cadbury case pages, Frosted Flakes + Charmin product pages → 200. Source tip later `10d194e` (WORKLOG SHA note only).

## 2026-10-16 — SEO and growth routine
- **Year list pages** `/shrinkflation-{2020…2026}/`, one for every year with ≥40 sourced cases: 2026 has 83, 2025 has 85, 2024 146, 2023 134, 2022 101, 2021 49, 2020 42. Each page has a Size Facts box (cases, countries, brands, median and biggest cut, priced cases that got pricier per unit), an intro naming the main source domains, the top 15 cuts, the biggest hidden price hikes (when ≥3 priced cases), chips by country (linking `/cases/?country=&year=`), category and brand (≥2 cases), the full list with source links, and an FAQ. The current year adds "Is shrinkflation still happening in 2026?". JSON-LD on each: BreadcrumbList, Article, ItemList (every case) and FAQPage. The old `/years/2020…2026.html` pages are now redirect stubs (canonical + 0-second meta refresh) and are no longer in the sitemap; `/years/` links to the new pages and the years before 2020 are unchanged. Linked from the nav ("2026 list", computed from the latest qualifying year), the home page, `/cases/` (year chips), the guides hub (cards and ItemList), search.json (k=List), llms.txt and the README.
- **Open data** `/data/`: `cases.csv` (300 KB) and `cases.json` (600 KB, `{meta, cases}`), 691 rows and 29 fields, released under CC BY 4.0. They include the numeric size cut, the same-price unit rise, raw and parsed prices, and the real per-unit change, plus retailer, maker, date reported, source, source URL, also-reported, archive, evidence type and confidence. Source quotes are left out (they belong to the publishers); daily ODbL snapshots are not part of the release. The `/data/` page has the field table, coverage caveats (agency-driven, not a sample), a citation line and a corrections path. The Dataset JSON-LD on `/cases/` and `/data/` now carries `distribution` (CSV + JSON DataDownload), temporal and spatial coverage, keywords and variableMeasured. The CSV is served as `text/csv`. Nav now has "Open data". Linked from the home page, `/cases/`, the guides hub, llms.txt, search.json and the README.
- **Titles**: `page()` accepts candidate titles and picks the first one of 60 characters or less. A plain-string title over 60 drops " | ShrinkRadar". Brand pages now read "Did {brand} shrink? N shrinkflation cases" and category pages "{cat} shrinkflation: N documented cases". The home page is "ShrinkRadar: shrinkflation tracker & 691 sourced cases", and guide titles are shortened. Duplicate product titles (Heinz Ketchup ×5, Red Bull, Cheerios…) now carry the size or UPC, and duplicate case titles carry country and year. Indexable titles over 60 characters: 1568 → ~209 (the rest are long product names). Duplicate titles: 9 → 0. Duplicate meta descriptions: 2 → 0.
- **Data/display fixes**: brands that had been cut short now come out right (`Gut` → Gut & Günstig ×4; `La` → La Trappe and La Vache qui rit; `costcotuna` → Kirkland). The old `/brands/gut|la|costcotuna.html` are noindex "moved" stubs. Non-Latin brand names used to collide on `/brands/.html` (السبع and سيدي علي); they now get stable `b-<hash>` slugs. 7 UK Guardian/Which? Easter cases with numeric GBP prices now show their prices and real per-unit change, so 391 → 398 cases are priced.
- **Repo**: wrote README.md (what the site is, key pages, open data and licence, how to report, how it's built). Set the GitHub description, homepage https://shrinkradar.com and topics (shrinkflation, open-data, dataset, consumer-protection, groceries, prices, open-food-facts, static-site) with `gh repo edit`. Added `check_links.py` (internal href/src check; exits 1 on any broken link).
- **Not done / noted**: no retailer pages, because the store-brand pages (Aldi 11, Kirkland 5, Great Value 4, Rewe 5, Woolworths 5…) already exist as brand pages and retailer pages would be near-duplicates. Page weight is OK: there are no content images and the largest page is /cases/ at 230 KB raw (gzip on Pages). One OPF product has a junk long name ("Echo Clean • 🇨🇦VIP Products…") and needs a name override.
- **Build**: 1801 pages, 691 cases, 385 products. validate_structured_data.py PASS (1813 HTML files, 3987 JSON-LD blocks, 2 Dataset, 385 tracking pages). check_links.py: 57,807 internal links, 0 broken.
- **Publish**: source `a0e2f95`, gh-pages `2fcc8ab`. IndexNow 200 (1801 URLs). Pages run 38955551063 succeeded. Live 200: /, /shrinkflation-2026/, -2025/, -2024/, -2020/, /data/, /data/cases.csv (691 rows), /data/cases.json (691), /years/2026.html (stub), /years/2019.html, /guides/, /cases/ (distribution present), the new brand pages, the moved stubs, llms.txt and sitemap.xml. Screenshots: design-shots/year2026-desktop.png, year2026-mobile.png, data-desktop.png.
- No Google results yet for `site:shrinkradar.com` (web search). The two GSC Validate Fix runs are still pending.

### Samuel-only asks (current)
- ~~Google Search Console verification + sitemap~~: done 2026-10-14.
- Bing Webmaster Tools: verify the site (it can import from GSC) and submit the sitemap. IndexNow already pings Bing. Still open.
- Social accounts (X etc.), if you want distribution. I won't create accounts. Still open.

## 2026-10-16 — features & quality: barcode lookup + name cleanup
- **Feature: /barcode/** — type (or, where the browser supports BarcodeDetector, scan with the camera) a UPC-A, EAN-13 or EAN-8. Client-side only. For the 385 products we track it shows our own verdict ("No change so far" / "Baseline only" / "Yes, it shrank" / "Unknown") with the size-history link, from a new `/barcodes.json` index (88 KB; also carries brand → documented-case counts). For anything else it asks Open Food Facts, then Open Products Facts, then Open Beauty Facts for the current net quantity, and Open Prices for the 6 most recent shelf prices (date, store, city, currency). It links the brand's case page when the brand has documented cases (e.g. Nutella → Ferrero, 1 case), and offers: calculator prefilled with the current size, a prefilled sighting, "Ask us to track it" (prefilled GitHub issue) and the open-database entry. Check-digit warning for mistyped codes. `?code=` deep links. FAQ (incl. privacy: camera stays on-device, only the number goes to OFF/Open Prices) + WebApplication/FAQPage/Breadcrumb JSON-LD. CORS verified for OFF, OPF and Open Prices.
- Wired in: nav ("Barcode" after Calculator), homepage links row, search page hint, search now offers "Look up barcode …" when the query is 8–14 digits, calculator note, the UPC on every product page links to its lookup, search.json (Tool), llms.txt.
- **Submit form** now accepts prefill params (`product, brand, new_size, new_unit, notes, country`), used by the barcode page.
- **Data quality:** Echo Clean junk name/brand fixed ("Echo Clean Baby Sensitive Sulphate-Free 2X Concentrated Laundry Detergent"); old product URL is a canonical + refresh stub, old brand slug added to the retired-brand stubs; validate_structured_data.py skips redirect stubs. 67 all-caps product names/brands title-cased (Charmin, Angel Soft, Cottonelle, Kirkland, Nescafé, Coca-Cola Services SA/NV…); every product URL unchanged (verified by diffing the products/ listing).
- QA: build 1802 pages; check_links.py 60,027 internal links, 0 broken; validate_structured_data.py PASS (1816 HTML, 3990 JSON-LD blocks, 385 tracking pages). Headless-Chrome DOM tests locally and on live for a tracked product (PopCorners, Cheerios), an untracked food (Nutella 3017620422003, OFF + 6 FR prices + Ferrero link), a non-food (Echo Clean via OPF), and the search digits shortcut. Screenshots: design-shots/barcode-desktop.png, barcode-mobile.png.
- Note: the build still reports 0 daily size findings (only 3–4 checks per product so far), so no "Yes, it shrank" verdicts exist yet.
- **Publish:** source `700c38a`, gh-pages `0f68110`. Pages run 38983650502 succeeded. IndexNow 200 (1802 URLs). Live 200: /barcode/, /barcodes.json, /search.html, /submit/, both Echo Clean URLs.
