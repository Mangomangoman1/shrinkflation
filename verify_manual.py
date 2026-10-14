#!/usr/bin/env python3
"""Verify raw/manual_cases.py entries: snippet must appear in fetched page raw/pages/N.html."""
import re,html,json,sys
sys.path.insert(0,"raw"); from manual_cases import M
def T(f): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",open(f,errors="ignore").read()))).replace("\u00a0"," ")
txt={};out=[];bad=[]
for pg,b,p,cat,bef,aft,u,y,cc,snip in M:
    t=txt.setdefault(pg,T(f"raw/pages/{pg}.html"))
    if snip.lower() not in t.lower(): bad.append((pg,p,snip)); continue
    url=open(f"raw/pages/{pg}.url").read().strip(); i=t.lower().find(snip.lower())
    title=re.search(r"<title>(.*?)</title>",open(f"raw/pages/{pg}.html",errors="ignore").read(),re.S); title=html.unescape(title.group(1).strip()) if title else url
    out.append(dict(product=p,brand=b,category=cat,before=bef,after=aft,unit=u,when=y,country=cc,source_url=url,source=title[:120],
        evidence=t[max(0,i-160):i+len(snip)+120].strip(),evidence_type="consumer-group / news investigation",confidence="high"))
json.dump(out,open("raw/manual_cases.json","w"),indent=1,ensure_ascii=False)
print(len(out),"ok; failed:",bad)
