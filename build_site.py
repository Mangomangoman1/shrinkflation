#!/usr/bin/env python3
"""Build static site to site/ from products.json + data/snapshots.json."""
import json, pathlib, html, re, shutil, datetime
R=pathlib.Path(__file__).parent; OUT=R/"site"; E=html.escape
SITE="https://shrinkradar.com"
NAME="ShrinkRadar"
CSS="""body{margin:0;font:1rem/1.6 system-ui,sans-serif;color:#1a1a1a;background:#fbfaf7}a{color:#b3261e}
.w{max-width:48rem;margin:0 auto;padding:0 1rem}header{background:#fff;border-bottom:3px double #1a1a1a;padding:1rem 0}
header b{font:700 1.8rem Georgia,serif}nav a{margin-right:1rem;font-weight:600}table{width:100%;border-collapse:collapse;background:#fff}
th,td{text-align:left;padding:.45rem;border-bottom:1px solid #ddd}.m{color:#666;font-size:.85rem}.na{color:#999}
footer{border-top:1px solid #ccc;margin-top:3rem;padding:1rem 0;color:#666;font-size:.85rem}"""
def slug(x): return re.sub(r"[^a-z0-9]+","-",x.lower()).strip("-")
def page(path,title,desc,body,ld=None):
    ld_s="".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (ld or []))
    p=OUT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{SITE}/{path}">'
      f'<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><link rel="stylesheet" href="/style.css">{ld_s}</head><body>'
      f'<header><div class="w"><a href="/" style="text-decoration:none;color:inherit"><b>{NAME}</b></a><p class="m">Tracking package sizes and unit prices of everyday products.</p>'
      f'<nav><a href="/">Findings</a><a href="/products/">Products</a><a href="/about.html">About</a></nav></div></header><main class="w">{body}</main>'
      f'<footer class="w">Data: Open Food Facts, Open Products Facts, Open Prices (ODbL). Built {datetime.date.today()}.</footer></body></html>')
    PAGES.append(path)
def unitp(s):
    return s["price"]/s["size"]*100 if s.get("price") and s.get("size") else None
PAGES=[]
def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); (OUT/"style.css").write_text(CSS)
    prods=json.load(open(R/"products.json")); snaps=json.load(open(R/"data/snapshots.json"))
    by={}; [by.setdefault(s["code"],[]).append(s) for s in sorted(snaps,key=lambda s:s["date"])]
    findings=[]; rows=[]
    for p in prods:
        h=by.get(p["code"],[]); p["slug"]=slug(f'{p["brand"]} {p["name"]}')[:60]+"-"+p["code"][-6:]
        ok=[s for s in h if s.get("size")]
        for a,b in zip(ok,ok[1:]):
            if a["unit"]==b["unit"] and b["size"]<a["size"]:
                findings.append((b["date"],p,f'Size dropped {a["size"]:g}{a["unit"]} → {b["size"]:g}{b["unit"]} ({(1-b["size"]/a["size"])*100:.1f}% less)'))
            ua,ub=unitp(a),unitp(b)
            if ua and ub and ub>ua*1.001 and a["unit"]==b["unit"]:
                findings.append((b["date"],p,f'Unit price up ${ua:.2f} → ${ub:.2f} per 100{b["unit"]}'))
        last=h[-1] if h else {}
        tr="".join(f'<tr><td>{s["date"]}</td><td>{f"{s[chr(115)+chr(105)+chr(122)+chr(101)]:g} {s[chr(117)+chr(110)+chr(105)+chr(116)]}" if s.get("size") else "<span class=na>not available</span>"}</td>'
           f'<td>{f"${s[chr(112)+chr(114)+chr(105)+chr(99)+chr(101)]:.2f} <span class=m>({s.get(chr(112)+chr(114)+chr(105)+chr(99)+chr(101)+chr(95)+chr(100)+chr(97)+chr(116)+chr(101))})</span>" if s.get("price") else "<span class=na>no price data</span>"}</td>'
           f'<td>{f"${unitp(s):.2f}/100{s[chr(117)+chr(110)+chr(105)+chr(116)]}" if unitp(s) else "—"}</td></tr>' for s in reversed(h))
        title=f'{p["brand"]} {p["name"]}'.strip()
        ld=[{"@context":"https://schema.org","@type":"Product","name":title,"brand":{"@type":"Brand","name":p["brand"]},"gtin":p["code"].lstrip("0").zfill(13),"category":p["category"],
             **({"size":f'{last["size"]:g} {last["unit"]}'} if last.get("size") else {}),
             **({"offers":{"@type":"Offer","price":last["price"],"priceCurrency":"USD"}} if last.get("price") else {})},
            {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Products","item":SITE+"/products/"},{"@type":"ListItem","position":2,"name":title}]}]
        src=" · ".join(f'<a href="{E(u)}">{"size source" if i==0 else "price source"}</a>' for i,u in enumerate([last.get("source_url"),last.get("price_source")]) if u)
        page(f'products/{p["slug"]}.html',f'{title} size & price history | {NAME}',f'Package size, price and unit price history for {title}.',
             f'<p class="m">{E(p["category"])} · UPC {p["code"]}</p><h1>{E(title)}</h1><p>Label: {E(last.get("quantity_label") or "n/a")} · {src}</p>'
             f'<table><tr><th>Checked</th><th>Size</th><th>Price</th><th>Unit price</th></tr>{tr}</table>',ld)
        rows.append(f'<tr><td><a href="/products/{p["slug"]}.html">{E(title)}</a></td><td>{E(p["category"])}</td><td>{f"{last[chr(115)+chr(105)+chr(122)+chr(101)]:g} {last[chr(117)+chr(110)+chr(105)+chr(116)]}" if last.get("size") else "—"}</td></tr>')
    page("products/index.html",f"All tracked products | {NAME}",f"{len(prods)} products tracked for shrinkflation.",
         f'<h1>Tracked products ({len(prods)})</h1><table><tr><th>Product</th><th>Category</th><th>Latest size</th></tr>{"".join(rows)}</table>')
    findings.sort(key=lambda f:f[0],reverse=True)
    feed="".join(f'<li><b>{d}</b> — <a href="/products/{p["slug"]}.html">{E(p["brand"]+" "+p["name"])}</a>: {E(t)}</li>' for d,p,t in findings) or \
         '<p>No changes detected yet. Baseline snapshots were taken; findings appear here when a later check shows a smaller package or higher unit price.</p>'
    page("index.html",f"{NAME}: shrinkflation findings",f"Size drops and unit-price rises in everyday groceries and household goods.",
         f'<h1>Latest findings</h1><ul>{feed}</ul>',[{"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE+"/"}])
    page("about.html",f"About | {NAME}","How we track shrinkflation.",
         '<h1>About</h1><p>We check a fixed list of common products daily. Package size comes from Open Food Facts / Open Products Facts; prices come from the crowdsourced Open Prices database (most recent USD receipt/price tag). We only publish values we fetched; missing values are shown as missing.</p>'
         '<p>A <b>finding</b> is logged when a newer snapshot shows a smaller net quantity, or a higher price per 100 g/ml.</p>',
         [{"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE+"/"}])
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+
        "".join(f'<url><loc>{SITE}/{p.replace("index.html","")}</loc><lastmod>{datetime.date.today()}</lastmod></url>' for p in PAGES)+"</urlset>")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"); (OUT/".nojekyll").write_text(""); (OUT/"CNAME").write_text("shrinkradar.com\n")
    print(len(PAGES),"pages,",len(findings),"findings")
if __name__=="__main__": main()
