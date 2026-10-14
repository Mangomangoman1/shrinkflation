#!/usr/bin/env bash
# NOT RUN. Creates public repo Mangomangoman1/shrinkflation, pushes, serves site/ via GitHub Pages (Actions-free: gh-pages branch).
set -euo pipefail; cd "$(dirname "$0")"; REPO=Mangomangoman1/shrinkflation
python3 build_site.py
[ -d .git ] || { git init -b main; printf 'baseline.log\n__pycache__/\n' > .gitignore; }
git add -A && git commit -m "Update $(date +%F)" || true
gh repo view "$REPO" >/dev/null 2>&1 || gh repo create "$REPO" --public --source=. --remote=origin --push
git push origin main
git subtree split --prefix site -b gh-pages-tmp && git push -f origin gh-pages-tmp:gh-pages && git branch -D gh-pages-tmp
gh api -X POST "repos/$REPO/pages" -f "source[branch]=gh-pages" -f "source[path]=/" 2>/dev/null || echo "Pages already enabled"
echo "Published: https://shrinkradar.com/"; python3 indexnow.py || echo "IndexNow submit failed (non-fatal)"
