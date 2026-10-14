# ShrinkRadar design language — "Net Wt."

ShrinkRadar should read like the most honest part of any package: the **Nutrition Facts / Net Wt. panel**.
Black hairlines and heavy bars, bold sans labels, tabular numbers, everything aligned on one column.
The "radar" part is a single signal colour that only appears when something got smaller.

## Principles
1. **The number is the hero.** Sizes, deltas and unit prices are always big, bold, tabular (`font-variant-numeric: tabular-nums`) and right-aligned in tables.
2. **Signal, not decoration.** Red (`--sig`) is reserved for shrinks/increases. Everything else is ink on paper. If red is on screen, it means something.
3. **Label rules carry structure.** Hierarchy comes from rule weight (8px bar → 4px bar → 1px hairline), as on a nutrition label, not from boxes, shadows or colour fills.
4. **Answer first.** Every page opens with the answer ("Yes — 9.75 → 9.25 oz") before history and context.
5. **Fast & plain.** System fonts only, one CSS file (< 8 KB), no JS except the 1 KB search; inline SVG for sparklines; no web fonts, no images required.
6. **Accessible.** All text ≥ 4.5:1 contrast in both themes; focus rings visible; red is always paired with a sign (−/+) or text, never colour alone.

## Type
- Family: system sans stack (`"Helvetica Neue", Helvetica, Arial, system-ui, sans-serif`) for UI & numbers; Georgia-free. Monospace (`ui-monospace`) only for UPCs.
- Scale (1.25 ratio, rem): `.75` micro labels (uppercase, +.08em tracking) · `.875` meta · `1` body (line-height 1.55) · `1.25` h3 · `1.563` h2 · `clamp(1.75, 5vw, 2.44)` h1 · `clamp(2.4, 9vw, 3.8)` hero number.
- Weights: 400 body, 700 labels, 900 headings & hero numbers (tight `-0.02em`).

## Palette
| token | light | dark | use |
|---|---|---|---|
| `--paper` | `#f7f5ef` (kraft-white) | `#121212` | page |
| `--panel` | `#ffffff` | `#1c1c1c` | label panels |
| `--ink` | `#111111` | `#f2f0ea` | text, rules |
| `--muted` | `#595650` | `#a9a59c` | meta (≥ 4.5:1) |
| `--hair` | `#d8d4ca` | `#353330` | hairlines in tables |
| `--sig` | `#c8102e` | `#ff5a5f` | shrink / increase |
| `--sig-bg` | `#fbe9eb` | `#3a1518` | badge fill |
| `--ok` | `#1d6b3a` | `#5fd38a` | "no change" text |
Dark mode via `prefers-color-scheme`.

## Spacing
4px base: `--s1 .25rem`, `--s2 .5rem`, `--s3 1rem`, `--s4 1.5rem`, `--s5 2.5rem`. Content column max 44rem; tables/grids may go to 60rem. Mobile padding 1rem.

## Motif
- **Label panel** (`.label`): 2px ink border, inner 8px top bar ("Net Wt." header), then rows separated by 1px hairlines and 4px section bars. Used for the answer box on product/case pages.
- **Radar mark**: the logo is "Shrink**Radar**" in 900 weight with a small inline SVG — three concentric arcs with a red blip — that doubles as favicon.
- **Micro-labels**: uppercase .75rem 700 tracked labels ("NET WT.", "UNIT PRICE", "SOURCE") above every number.

## Components
- **Nav**: logo row + one horizontal scrolling row of links (no hamburger) under an 8px bar; current page underlined 3px.
- **Search**: full-width input with 2px ink border, no radius, big type; results as a hairline list.
- **Size-change badge** (`.badge`): `9.75 → 9.25 oz` in tabular bold, followed by `−5.1%` on `--sig-bg` with `--sig` text. Neutral variant (`.badge.flat`) for "no change".
- **Product card** (`.card`): panel with 4px top bar, micro-label category, product name (700), latest NET WT. big number, sparkline right-aligned.
- **Case card** (`.card.case`): same frame, red top bar, badge, "when" + source domain.
- **History table**: hairline rows, header micro-labels with 4px rule beneath, numbers right-aligned tabular; first (latest) row bold.
- **Sparkline**: inline SVG 120×28 (product cards) / 100%×64 (product page), 2px ink polyline, red dot on any drop, last point dot; flat line + "1 check" label when one data point.
- **Footer**: 8px bar, small meta, sources, RSS.
