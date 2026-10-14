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
