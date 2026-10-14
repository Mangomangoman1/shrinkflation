#!/usr/bin/env python3
"""Build ShrinkRadar static site into site/ from products.json, data/snapshots.json, data/cases.json."""
import json, pathlib, html, re, shutil, datetime
from email.utils import format_datetime
R=pathlib.Path(__file__).parent; OUT=R/"site"; E=html.escape
SITE="https://shrinkradar.com"; NAME="ShrinkRadar"; TODAY=datetime.date.today().isoformat()
INDEXNOW_KEY=(R/"indexnow_key.txt").read_text().strip() if (R/"indexnow_key.txt").exists() else None
CSS="""body{margin:0;font:1rem/1.6 system-ui,sans-serif;color:#1a1a1a;background:#fbfaf7}a{color:#b3261e}
.w{max-width:52rem;margin:0 auto;padding:0 1rem}header{background:#fff;border-bottom:3px double #1a1a1a;padding:1rem 0}
.brand{font:700 1.8rem Georgia,serif;color:inherit;text-decoration:none}.brand i{color:#b3261e;font-style:normal}
nav a{margin-right:1rem;font-weight:600;display:inline-block}table{width:100%;border-collapse:collapse;background:#fff}
th,td{text-align:left;padding:.45rem;border-bottom:1px solid #ddd;vertical-align:top}th{font-size:.8rem;text-transform:uppercase;color:#666}
.m{color:#666;font-size:.85rem}.na{color:#999}.down{color:#b3261e;font-weight:700}.ans{background:#fff;border-left:4px solid #b3261e;padding:.8rem 1rem;margin:1rem 0}
#q{width:100%;font-size:1.05rem;padding:.6rem;border:1px solid #888;margin:.5rem 0}#res li{margin:.2rem 0}
.chips a{display:inline-block;margin:.2rem .4rem .2rem 0;padding:.15rem .5rem;border:1px solid #ccc;border-radius:3px;text-decoration:none;background:#fff}
footer{border-top:1px solid #ccc;margin-top:3rem;padding:1rem 0;color:#666;font-size:.85rem}"""
SEARCH_JS="""(async()=>{const q=document.getElementById('q'),r=document.getElementById('res');const d=await (await fetch('/search.json')).json();
const go=()=>{const t=q.value.toLowerCase().trim();r.innerHTML='';if(t.length<2)return;d.filter(x=>x.t.toLowerCase().includes(t)).slice(0,40).forEach(x=>{const li=document.createElement('li');const a=document.createElement('a');a.href=x.u;a.textContent=x.t;li.append(a,' ',Object.assign(document.createElement('span'),{className:'m',textContent:x.k}));r.append(li)})};
q.addEventListener('input',go);const p=new URLSearchParams(location.search).get('q');if(p){q.value=p;go()}})();"""
PAGES=[]
def slug(x): return re.sub(r"[^a-z0-9]+","-",x.lower().replace("&","and")).strip("-")
def fmt(v,u): return f"{v:g} {u}"
def page(path,title,desc,body,ld=None,js=None):
    ld_s="".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in (ld or []))
    p=OUT/path; p.parent.mkdir(parents=True,exist_ok=True); url=SITE+"/"+path.replace("index.html","")
    p.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">'
      f'<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:url" content="{url}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">'
      f'<link rel="alternate" type="application/rss+xml" title="{NAME} findings" href="/feed.xml"><link rel="stylesheet" href="/style.css">{ld_s}</head><body>'
      f'<header><div class="w"><a class="brand" href="/">Shrink<i>Radar</i></a><p class="m">Did it shrink? Tracking package sizes and unit prices of everyday groceries and household goods.</p>'
      f'<nav><a href="/">Findings</a><a href="/cases/">Known cases</a><a href="/products/">Products</a><a href="/brands/">Brands</a><a href="/categories/">Categories</a><a href="/search.html">Search</a><a href="/about.html">About</a></nav></div></header>'
      f'<main class="w">{body}</main><footer class="w">Data: Open Food Facts, Open Products Facts, Open Prices (ODbL); documented cases cite their sources. <a href="/feed.xml">RSS</a> · Updated {TODAY}.</footer>'
      +(f'<script>{js}</script>' if js else "")+'</body></html>')
    PAGES.append(path)
def unitp(s): return s["price"]/s["size"]*100 if s.get("price") and s.get("size") else None
def crumbs(*items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,**({"item":SITE+u} if u else {})} for i,(n,u) in enumerate(items)]}
def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); (OUT/"style.css").write_text(CSS)
    prods=json.load(open(R/"products.json")); snaps=json.load(open(R/"data/snapshots.json"))
    cases=json.load(open(R/"data/cases.json")) if (R/"data/cases.json").exists() else []
    by={}
    for s in sorted(snaps,key=lambda s:s["date"]): by.setdefault(s["code"],[]).append(s)
    for p in prods:
        p["title"]=(p["name"] if p["brand"].lower() in p["name"].lower() else f'{p["brand"]} {p["name"]}').strip()
        p["slug"]=slug(p["title"])[:60]+"-"+p["code"][-6:]; p["bslug"]=slug(p["brand"] or "unbranded"); p["cslug"]=slug(p["category"])
    for c in cases:
        c["slug"]=slug(c["product"]+"-"+c["when"]); c["bslug"]=slug(c["brand"]); c["cslug"]=slug(c["category"]); c["pct"]=(1-c["after"]/c["before"])*100
    findings=[]
    for p in prods:
        ok=[s for s in by.get(p["code"],[]) if s.get("size")]
        for a,b in zip(ok,ok[1:]):
            if a["unit"]==b["unit"] and b["size"]<a["size"]:
                findings.append((b["date"],p,f'Size dropped {fmt(a["size"],a["unit"])} → {fmt(b["size"],b["unit"])} ({(1-b["size"]/a["size"])*100:.1f}% less)'))
            ua,ub=unitp(a),unitp(b)
            if ua and ub and ub>ua*1.001 and a["unit"]==b["unit"]:
                findings.append((b["date"],p,f'Unit price up ${ua:.2f} → ${ub:.2f} per 100 {b["unit"]}'))
    findings.sort(key=lambda f:f[0],reverse=True)
    fset={id(f[1]) for f in findings}
    def plink(p): return f'<a href="/products/{p["slug"]}.html">{E(p["title"])}</a>'
    # product pages
    for p in prods:
        h=by.get(p["code"],[]); last=h[-1] if h else {}; ok=[s for s in h if s.get("size")]
        rel_cases=[c for c in cases if c["bslug"]==p["bslug"]]
        shrank=[f for f in findings if f[1] is p]
        if shrank: ans=f'<b>Yes — we detected a change.</b> {E(shrank[0][2])} (checked {shrank[0][0]}).'
        elif len(ok)>1: ans=f'<b>Not since we started tracking.</b> Size has stayed {fmt(ok[-1]["size"],ok[-1]["unit"])} across {len(ok)} checks since {ok[0]["date"]}.'
        elif ok: ans=f'<b>No change detected yet.</b> Our baseline on {ok[0]["date"]} recorded {fmt(ok[0]["size"],ok[0]["unit"])}. We re-check daily and will flag any shrink.'
        else: ans='<b>Not enough data yet.</b> The open product database has no net quantity on file for this item.'
        tr="".join('<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(s["date"],
            fmt(s["size"],s["unit"]) if s.get("size") else '<span class=na>not available</span>',
            f'${s["price"]:.2f} <span class=m>(reported {s.get("price_date")})</span>' if s.get("price") else '<span class=na>no price data</span>',
            f'${unitp(s):.2f}/100 {s["unit"]}' if unitp(s) else "—") for s in reversed(h))
        src=" · ".join(f'<a href="{E(u)}" rel="nofollow">{n}</a>' for n,u in [("size source",last.get("source_url")),("price source",last.get("price_source"))] if u)
        sib=[q for q in prods if q["cslug"]==p["cslug"] and q is not p][:8]
        ld=[{"@context":"https://schema.org","@type":"Product","name":p["title"],"brand":{"@type":"Brand","name":p["brand"]},"gtin13":p["code"].lstrip("0").zfill(13),"category":p["category"],
             **({"size":fmt(last["size"],last["unit"])} if last.get("size") else {}),
             **({"offers":{"@type":"Offer","price":last["price"],"priceCurrency":"USD"}} if last.get("price") else {})},
            crumbs(("Products","/products/"),(p["category"],f'/categories/{p["cslug"]}.html'),(p["title"],None)),
            {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f'Did {p["title"]} shrink?',"acceptedAnswer":{"@type":"Answer","text":re.sub("<[^>]+>","",ans)}}]}]
        size_txt=f' Current size: {fmt(last["size"],last["unit"])}.' if last.get("size") else ""
        page(f'products/{p["slug"]}.html',f'Did {p["title"]} shrink? Size & price history | {NAME}',
             f'Has {p["title"]} gotten smaller? Daily-tracked package size, price and unit price history.{size_txt}',
             f'<p class="m"><a href="/categories/{p["cslug"]}.html">{E(p["category"])}</a> · <a href="/brands/{p["bslug"]}.html">{E(p["brand"] or "Unbranded")}</a> · UPC {p["code"]}</p>'
             f'<h1>Did {E(p["title"])} shrink?</h1><div class="ans">{ans}</div><p>Package label: {E(last.get("quantity_label") or "n/a")} · {src}</p>'
             f'<h2>Size &amp; price history</h2><table><tr><th>Checked</th><th>Size</th><th>Price</th><th>Unit price</th></tr>{tr}</table>'
             +(f'<h2>Documented {E(p["brand"])} shrinkflation</h2><ul>'+"".join(f'<li><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a>: {fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])} ({c["when"]})</li>' for c in rel_cases)+'</ul>' if rel_cases else "")
             +(f'<h2>More {E(p["category"])}</h2><p class="chips">'+"".join(plink(q) for q in sib)+'</p>' if sib else ""),ld)
    # case pages
    for c in cases:
        prs=[p for p in prods if p["bslug"]==c["bslug"]][:8]
        desc=f'Yes: {c["product"]} shrank from {fmt(c["before"],c["unit"])} to {fmt(c["after"],c["unit"])} ({c["pct"]:.1f}% less) around {c["when"]}. Sourced.'
        page(f'cases/{c["slug"]}.html',f'Did {c["product"]} shrink? {fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])} | {NAME}',desc,
             f'<p class="m"><a href="/cases/">Known cases</a> · <a href="/categories/{c["cslug"]}.html">{E(c["category"])}</a> · <a href="/brands/{c["bslug"]}.html">{E(c["brand"])}</a></p>'
             f'<h1>Did {E(c["product"])} shrink?</h1><div class="ans"><b>Yes.</b> It went from <b>{fmt(c["before"],c["unit"])}</b> to <b>{fmt(c["after"],c["unit"])}</b>, <span class="down">{c["pct"]:.1f}% less</span>, around {E(c["when"])}. '
             f'If the price stayed the same, that is a {(c["before"]/c["after"]-1)*100:.1f}% hidden price increase per unit.</div>'
             f'<p>Source: <a href="{E(c["source_url"])}">{E(c["source"])}</a>. {E(c["verified"])}.</p>'
             +(f'<h2>{E(c["brand"])} products we track</h2><p class="chips">'+"".join(plink(p) for p in prs)+'</p>' if prs else ""),
             [crumbs(("Known cases","/cases/"),(c["product"],None)),
              {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f'Did {c["product"]} shrink?',"acceptedAnswer":{"@type":"Answer","text":desc}}]}])
    crow="".join(f'<tr><td><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a><br><span class="m">{E(c["brand"])}</span></td><td>{fmt(c["before"],c["unit"])}</td><td>{fmt(c["after"],c["unit"])}</td><td class="down">−{c["pct"]:.1f}%</td><td>{E(c["when"])}</td><td><a href="{E(c["source_url"])}">source</a></td></tr>' for c in sorted(cases,key=lambda c:-c["pct"]))
    page("cases/index.html",f'Known shrinkflation cases: {len(cases)} documented examples | {NAME}',f'{len(cases)} documented shrinkflation cases with before and after sizes, dates and sources: Doritos, Gatorade, Charmin, Oreo, Cocoa Puffs and more.',
         f'<h1>Known shrinkflation cases</h1><p>Each case is a reported before/after size change, linked to the source we checked. Sorted by how much was cut.</p><table><tr><th>Product</th><th>Before</th><th>After</th><th>Cut</th><th>When</th><th>Source</th></tr>{crow}</table>',
         [crumbs(("Known cases",None)),{"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f'{SITE}/cases/{c["slug"]}.html',"name":c["product"]} for i,c in enumerate(cases)]}])
    # group pages
    def groups(kind,key,label):
        g={}
        for p in prods: g.setdefault(p[key],{"name":p["brand" if kind=="brands" else "category"] or "Unbranded","p":[],"c":[]})["p"].append(p)
        for c in cases: g.setdefault(c[key],{"name":c["brand" if kind=="brands" else "category"],"p":[],"c":[]})["c"].append(c)
        for k,v in g.items():
            body=f'<h1>Did {E(v["name"])} products shrink?</h1>'
            if v["c"]: body+='<h2>Documented cases</h2><ul>'+"".join(f'<li><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a>: {fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])} ({c["when"]})</li>' for c in v["c"])+'</ul>'
            if v["p"]: body+=f'<h2>Tracked daily ({len(v["p"])})</h2><ul>'+"".join(f'<li>{plink(p)}</li>' for p in v["p"])+'</ul>'
            page(f'{kind}/{k}.html',f'{v["name"]} shrinkflation: did {v["name"]} products get smaller? | {NAME}',
                 f'{len(v["c"])} documented cases and {len(v["p"])} {v["name"]} products tracked daily for size and unit-price changes.',body,[crumbs((label,f"/{kind}/"),(v["name"],None))])
        page(f'{kind}/index.html',f'Shrinkflation by {label.lower()[:-1] if label.endswith("s") else label} | {NAME}',f'Browse shrinkflation tracking by {label.lower()}.',
             f'<h1>{label}</h1><p class="chips">'+"".join(f'<a href="/{kind}/{k}.html">{E(v["name"])} ({len(v["p"])+len(v["c"])})</a>' for k,v in sorted(g.items(),key=lambda kv:kv[1]["name"].lower()))+'</p>',[crumbs((label,None))])
    groups("brands","bslug","Brands"); groups("categories","cslug","Categories")
    rows="".join(f'<tr><td>{plink(p)}</td><td><a href="/categories/{p["cslug"]}.html">{E(p["category"])}</a></td><td>{(lambda l: fmt(l["size"],l["unit"]) if l.get("size") else "—")((by.get(p["code"]) or [{}])[-1])}</td></tr>' for p in sorted(prods,key=lambda p:p["title"].lower()))
    page("products/index.html",f'All {len(prods)} tracked products | {NAME}',f'{len(prods)} everyday products checked daily for package-size cuts and unit-price increases.',
         f'<h1>Tracked products ({len(prods)})</h1><table><tr><th>Product</th><th>Category</th><th>Latest size</th></tr>{rows}</table>',[crumbs(("Products",None))])
    feed="".join(f'<li><b>{d}</b> — {plink(p)}: {E(t)}</li>' for d,p,t in findings[:100]) or '<p>No changes detected in our daily checks yet — baselines are in place, and anything that shrinks will show up here first.</p>'
    top="".join(f'<li><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a> <span class="down">−{c["pct"]:.1f}%</span></li>' for c in sorted(cases,key=lambda c:-c["pct"])[:8])
    page("index.html",f'{NAME}: did it shrink? Shrinkflation tracker for groceries & household goods',f'Daily tracking of package sizes and unit prices for {len(prods)} products, plus {len(cases)} documented shrinkflation cases with sources.',
         f'<form action="/search.html"><input id="q0" name="q" placeholder="Did it shrink? Search a product or brand…" style="width:100%;font-size:1.05rem;padding:.6rem;margin-top:1rem"></form>'
         f'<h1>Latest findings from daily checks</h1><ul>{feed}</ul><h2>Biggest documented shrinks</h2><ul>{top}</ul><p><a href="/cases/">All {len(cases)} known cases →</a></p>',
         [{"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE+"/","potentialAction":{"@type":"SearchAction","target":SITE+"/search.html?q={search_term_string}","query-input":"required name=search_term_string"}},
          {"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE+"/"}])
    idx=[{"t":p["title"],"u":f'/products/{p["slug"]}.html',"k":p["category"]} for p in prods]+[{"t":c["product"]+" (documented case)","u":f'/cases/{c["slug"]}.html',"k":c["category"]} for c in cases]
    (OUT/"search.json").write_text(json.dumps(idx,ensure_ascii=False))
    page("search.html",f'Search: did my product shrink? | {NAME}','Search tracked products and documented shrinkflation cases.',
         '<h1>Search</h1><label for="q" class="m">Product, brand or category</label><input id="q" autofocus placeholder="e.g. Doritos, cereal, Charmin"><ul id="res"></ul><noscript>Search needs JavaScript; browse <a href="/products/">products</a> or <a href="/cases/">cases</a>.</noscript>',js=SEARCH_JS)
    page("about.html",f'About & methodology | {NAME}','How ShrinkRadar tracks shrinkflation: sources, method and corrections.',
         '<h1>About ShrinkRadar</h1><p>ShrinkRadar answers one question: <i>did it shrink?</i> We check a fixed list of everyday products daily. Net quantity comes from Open Food Facts / Open Products Facts; prices come from the crowdsourced Open Prices database (most recent US price). We only publish values we actually fetched — missing data is shown as missing, never estimated.</p>'
         '<p>A <b>finding</b> is logged when a newer check shows a smaller net quantity in the same unit, or a higher price per 100 g/ml.</p><p><b>Known cases</b> are historical before/after changes reported by news outlets, advocacy reports and reference works; each links to the source we checked.</p>'
         '<p>Spotted a shrink? Corrections and tips are welcome.</p>',[{"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE+"/"}])
    # RSS: findings + cases
    items=[(d,f'{p["title"]}: {t}',f'{SITE}/products/{p["slug"]}.html') for d,p,t in findings[:50]]+[(TODAY if not findings else findings[-1][0],f'Known case: {c["product"]} {fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])}',f'{SITE}/cases/{c["slug"]}.html') for c in cases]
    rss="".join(f'<item><title>{E(t)}</title><link>{u}</link><guid>{u}</guid><pubDate>{format_datetime(datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc))}</pubDate></item>' for d,t,u in items)
    (OUT/"feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE}/</link><description>Shrinkflation findings and documented cases</description>{rss}</channel></rss>')
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+
        "".join(f'<url><loc>{SITE}/{p.replace("index.html","")}</loc><lastmod>{TODAY}</lastmod></url>' for p in PAGES)+"</urlset>")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"); (OUT/".nojekyll").write_text(""); (OUT/"CNAME").write_text("shrinkradar.com\n")
    if INDEXNOW_KEY: (OUT/f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    (OUT/"404.html").write_text('<!doctype html><meta charset=utf-8><title>Not found</title><p>Page not found. <a href="/">ShrinkRadar home</a> · <a href="/search.html">Search</a></p>')
    print(len(PAGES),"pages,",len(findings),"findings,",len(cases),"cases")
if __name__=="__main__": main()
