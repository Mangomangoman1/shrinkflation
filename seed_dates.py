#!/usr/bin/env python3
"""One-off backfill (2026-10-17) from git history:
- data/case_added.json: case signature -> date the case first appeared in data/cases.json
- data/product_added.json: product code -> date it first appeared in products.json
- data/lastmod.json: site path -> [normalized content hash, date of last real change]
build_site.py keeps all three up to date afterwards (new entries get the build date)."""
import json, subprocess, hashlib, re, pathlib
R=pathlib.Path(__file__).parent
def git(*a): return subprocess.run(["git",*a],cwd=R,capture_output=True,check=True).stdout
def commits(path): return [l.split() for l in git("log","--reverse","--format=%H %ad","--date=short","--",path).decode().splitlines()]
def case_sig(c): return f'{c["source_url"]}|{float(c["before"]):g}|{float(c["after"]):g}|{c["unit"]}'
added={}
for h,d in commits("data/cases.json"):
    for c in json.loads(git("show",f"{h}:data/cases.json")): added.setdefault(case_sig(c),d)
cur=json.load(open(R/"data/cases.json")); ca={case_sig(c):added.get(case_sig(c)) for c in cur}
print("cases",len(ca),"undated",sum(1 for v in ca.values() if not v))
(R/"data/case_added.json").write_text(json.dumps(dict(sorted(ca.items())),indent=0,ensure_ascii=False))
pa={}
for h,d in commits("products.json"):
    for p in json.loads(git("show",f"{h}:products.json")): pa.setdefault(p["code"],d)
(R/"data/product_added.json").write_text(json.dumps(dict(sorted(pa.items())),indent=0))
print("products",len(pa))
# page lastmod from committed site/ snapshots
import importlib.util
spec=importlib.util.spec_from_file_location("b",R/"build_site.py"); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
lm={}; cache={}
for h,d in commits("site/"):
    tree=git("ls-tree","-r",h,"site/").decode().splitlines()
    for line in tree:
        meta,path=line.split("\t",1)
        if not path.endswith(".html"): continue
        blob=meta.split()[2]; p=path[5:]
        if blob not in cache: cache[blob]=b.norm_hash(git("cat-file","-p",blob).decode("utf-8","replace"))
        hv=cache[blob]
        if p not in lm or lm[p][0]!=hv: lm[p]=[hv,d]
(R/"data/lastmod.json").write_text(json.dumps(dict(sorted(lm.items())),indent=0))
from collections import Counter; print("pages",len(lm),Counter(v[1] for v in lm.values()))
