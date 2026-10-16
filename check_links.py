#!/usr/bin/env python3
"""Internal link check for site/: every root-relative href/src must resolve to a built file."""
import pathlib,re,sys,urllib.parse
R=pathlib.Path(__file__).parent/"site"; bad=[]; n=0
def ok(u):
    u=urllib.parse.unquote(u.split("#")[0].split("?")[0])
    if not u or u=="/": return (R/"index.html").exists()
    p=R/u.lstrip("/")
    return p.is_file() or (p/"index.html").is_file()
for f in R.rglob("*.html"):
    for u in re.findall(r'(?:href|src)="?(/[^"\s>]*)',f.read_text()):
        if u.startswith("//"): continue
        n+=1
        if not ok(u): bad.append((str(f.relative_to(R)),u))
print(f"{n} internal links, {len(bad)} broken")
for b in bad[:30]: print(*b)
sys.exit(1 if bad else 0)
