import re,html,json,glob
U={"gram":"g","g":"g","ml":"ml","milliliter":"ml","liter":"l","stuks":"pieces","repen":"bars","wasbeurten":"loads","rollen":"rolls","zakjes":"bags","kauwgoms":"pieces","tabletten":"tablets","doekjes":"wipes","vellen":"sheets","capsules":"capsules","kg":"kg","cl":"cl"}
out=[]
for f in ["raw/pages/17.html","raw/pages/18.html","raw/pages/28.html"]+[f"raw/pages/{i}.html" for i in (29,30,31)]:
    try: t=html.unescape(open(f).read())
    except: continue
    url=open(f.replace(".html",".url")).read().strip()
    for m in re.finditer(r'"title":"([^"]{2,80})","subtitle":"[^"]*","text":"(.*?)"(?:,"|\})',t):
        title,txt=m.group(1),re.sub(r"\s+"," ",re.sub(r"<[^>]+>|\\n|\|"," ",m.group(2)))
        q=re.search(r"Inhoud: van (\d+(?:[.,]\d+)?) ?([a-zA-Z]+)? naar (\d+(?:[.,]\d+)?) ?([a-zA-Z]+)",txt)
        if not q: continue
        a,ua,b,ub=q.groups(); ua=ua or ub
        if U.get(ua.lower(),ua)!=U.get(ub.lower(),ub): continue
        A,B=float(a.replace(",",".")),float(b.replace(",","."))
        if not B<A: continue
        pm=re.search(r"Prijs: (?:van )?(€[\d,]+)(?: naar (€[\d,]+))?",txt)
        yr=re.search(r"/(20\d\d)/",url).group(1)
        out.append(dict(product=title,brand=title.split(" ")[0],before=A,after=B,unit=U.get(ub.lower(),ub),when=yr,country="NL",
            old_price=pm.group(1) if pm else "",new_price=(pm.group(2) or pm.group(1)) if pm else "",
            source_url=url,source=f"Consumentenbond — Krimpflatie ({yr})",evidence=txt[:300].strip(),evidence_type="consumer association investigation (manufacturer response)",confidence="high"))
d={}
for c in out: d.setdefault((c["product"].lower(),c["before"],c["after"]),c)
json.dump(list(d.values()),open("raw/cb_cases.json","w"),indent=1,ensure_ascii=False); print(len(d))
