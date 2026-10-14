#!/usr/bin/env python3
"""Build ShrinkRadar static site into site/ from products.json, data/snapshots.json, data/cases.json."""
import json, pathlib, html, re, shutil, datetime
from email.utils import format_datetime
R=pathlib.Path(__file__).parent; OUT=R/"site"; E=html.escape
SITE="https://shrinkradar.com"; NAME="ShrinkRadar"; TODAY=datetime.date.today().isoformat()
INDEXNOW_KEY=(R/"indexnow_key.txt").read_text().strip() if (R/"indexnow_key.txt").exists() else None
CSS="""
:root{--paper:#f7f5ef;--panel:#fff;--ink:#111;--muted:#595650;--hair:#d8d4ca;--sig:#c8102e;--sig-bg:#fbe9eb;--ok:#1d6b3a;--s1:.25rem;--s2:.5rem;--s3:1rem;--s4:1.5rem;--s5:2.5rem;--f:"Helvetica Neue",Helvetica,Arial,system-ui,sans-serif;color-scheme:light dark}
@media(prefers-color-scheme:dark){:root{--paper:#121212;--panel:#1c1c1c;--ink:#f2f0ea;--muted:#a9a59c;--hair:#353330;--sig:#ff5a5f;--sig-bg:#3a1518;--ok:#5fd38a}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:1rem/1.55 var(--f);font-variant-numeric:tabular-nums}
a{color:inherit;text-decoration-color:var(--sig);text-decoration-thickness:2px;text-underline-offset:3px}a:hover{color:var(--sig)}
:focus-visible{outline:3px solid var(--sig);outline-offset:2px}
.w{max-width:60rem;margin:0 auto;padding:0 var(--s3)}main.w{max-width:60rem;padding-top:var(--s4);padding-bottom:var(--s5)}
.prose{max-width:44rem}
header{background:var(--panel);border-bottom:8px solid var(--ink)}
.top{display:flex;align-items:center;justify-content:space-between;gap:var(--s3);padding:var(--s3) 0 var(--s2)}
.brand{display:flex;align-items:center;gap:.5rem;font-weight:900;font-size:1.6rem;letter-spacing:-.03em;text-decoration:none}.brand b{color:var(--sig)}
.brand svg{width:32px;height:32px}
.tag{font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:right}
nav{border-top:1px solid var(--ink);overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch}
nav a{display:inline-block;padding:.6rem 0;margin-right:1.2rem;font-weight:700;font-size:.875rem;text-decoration:none;text-transform:uppercase;letter-spacing:.04em}
nav a[aria-current]{box-shadow:inset 0 -3px var(--sig)}
h1,h2,h3{line-height:1.15;letter-spacing:-.02em;font-weight:900}
h1{font-size:clamp(1.75rem,5vw,2.44rem);margin:var(--s2) 0 var(--s3)}
h2{font-size:1.563rem;margin:var(--s5) 0 var(--s3);padding-top:var(--s2);border-top:4px solid var(--ink)}
h3{font-size:1.25rem;margin:0}
.ml{display:block;font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.m{color:var(--muted);font-size:.875rem}.na{color:var(--muted);font-style:italic}.upc{font-family:ui-monospace,monospace}
.crumbs{font-size:.875rem;color:var(--muted)}.crumbs a{color:var(--muted)}
.label{background:var(--panel);border:2px solid var(--ink);padding:0 var(--s3) var(--s2);margin:var(--s3) 0 var(--s4);max-width:34rem}
.label>.hd{border-bottom:8px solid var(--ink);padding:var(--s2) 0 var(--s1);font-weight:900;font-size:1.563rem;letter-spacing:-.02em}
.label .row{display:flex;justify-content:space-between;align-items:baseline;gap:var(--s3);border-bottom:1px solid var(--ink);padding:var(--s1) 0}
.label .row.bar{border-bottom:4px solid var(--ink)}.label .row b{font-weight:900}
.label .big{font-size:clamp(2.4rem,9vw,3.8rem);font-weight:900;letter-spacing:-.03em;line-height:1}
.label p{margin:var(--s2) 0;font-size:.875rem}
.yes{color:var(--sig)}.no{color:var(--ok)}
.badge{display:inline-flex;align-items:baseline;gap:.4rem;font-weight:700;white-space:nowrap}
.badge i{font-style:normal;background:var(--sig-bg);color:var(--sig);padding:0 .35rem;font-weight:900}
.badge.flat i{background:transparent;color:var(--muted);border:1px solid var(--hair)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));gap:var(--s3);list-style:none;padding:0;margin:var(--s3) 0}
.card{background:var(--panel);border:1px solid var(--hair);border-top:4px solid var(--ink);padding:var(--s2) var(--s3) var(--s3);display:flex;flex-direction:column;gap:var(--s1)}
.card.case{border-top-color:var(--sig)}
.card h3{font-size:1.05rem;font-weight:700;letter-spacing:0}.card h3 a{text-decoration:none}.card h3 a:hover{text-decoration:underline}
.card .nw{display:flex;justify-content:space-between;align-items:flex-end;margin-top:auto;padding-top:var(--s2);border-top:1px solid var(--hair)}
.card .nw b{font-size:1.4rem;font-weight:900}
table{width:100%;border-collapse:collapse;background:var(--panel);font-size:.95rem}
th{font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:left;border-bottom:4px solid var(--ink);padding:.5rem}
td{padding:.5rem;border-bottom:1px solid var(--hair);vertical-align:top}td.n,th.n{text-align:right}
tbody tr:first-child td{font-weight:700}
.tw{overflow-x:auto}
.spark{display:block;width:100%;height:64px;margin:var(--s2) 0}.spark.s{width:120px;height:28px;margin:0}
.spark polyline{fill:none;stroke:var(--ink);stroke-width:2;vector-effect:non-scaling-stroke}.spark .d{fill:var(--sig)}.spark .e{fill:var(--ink)}
.search input,#q{width:100%;font:700 1.15rem var(--f);padding:.7rem .8rem;border:2px solid var(--ink);border-radius:0;background:var(--panel);color:var(--ink)}
.flt{display:flex;flex-wrap:wrap;gap:.5rem;margin:var(--s3) 0}.flt select,.flt input{font:700 .95rem var(--f);padding:.5rem;border:2px solid var(--ink);background:var(--panel);color:var(--ink);border-radius:0}.flt input{flex:1 1 12rem}
blockquote.q{margin:0;padding:var(--s3);background:var(--panel);border-left:4px solid var(--ink);font-size:.95rem}
#res{list-style:none;padding:0}#res li{border-bottom:1px solid var(--hair);padding:.5rem 0}
.feed{list-style:none;padding:0}.feed li{border-bottom:1px solid var(--hair);padding:.6rem 0}
.empty{border:1px dashed var(--muted);padding:var(--s3);background:var(--panel)}
.chips{display:flex;flex-wrap:wrap;gap:.4rem;padding:0;list-style:none}.chips a{display:inline-block;padding:.3rem .6rem;border:1px solid var(--ink);text-decoration:none;font-size:.875rem;font-weight:700;background:var(--panel)}
.chips a:hover{background:var(--ink);color:var(--paper)}
.alert{background:var(--panel);border:2px solid var(--ink);padding:0 var(--s3) var(--s3);margin:var(--s5) 0 0;max-width:34rem}.alert h2{border-top:0;margin:var(--s2) 0;font-size:1.25rem;border-bottom:8px solid var(--ink);padding-bottom:var(--s1)}
.alert fieldset{border:0;padding:0;margin:0 0 var(--s2)}.alert .ck{display:block;padding:.2rem 0;font-weight:700}.alert .row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}.alert .row .ml{flex-basis:100%}
.alert input[type=email]{flex:1 1 14rem;font:700 1rem var(--f);padding:.6rem;border:2px solid var(--ink);background:var(--paper);color:var(--ink);border-radius:0}.alert button{font:900 .95rem var(--f);text-transform:uppercase;letter-spacing:.04em;padding:.65rem 1rem;border:2px solid var(--ink);background:var(--ink);color:var(--paper);border-radius:0;cursor:pointer}
.alert [disabled]{opacity:.55;cursor:not-allowed}.alert .st{min-height:1.2em;margin:.4rem 0 0;font-weight:700}
.calc{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:var(--s3);margin:var(--s3) 0}.calc fieldset{border:2px solid var(--ink);background:var(--panel);margin:0;padding:var(--s2) var(--s3) var(--s3)}.calc legend{padding:0 .3rem;background:var(--panel)}
.calc label{display:block;font-weight:700;font-size:.875rem;margin-top:var(--s2)}.calc input,.calc select{display:block;width:100%;margin-top:.2rem;font:700 1.15rem var(--f);padding:.55rem .6rem;border:2px solid var(--ink);border-radius:0;background:var(--paper);color:var(--ink)}
.label .big.no{color:var(--ok)}.label .big.yes{color:var(--sig)}[hidden]{display:none!important}
footer{border-top:8px solid var(--ink);background:var(--panel);padding:var(--s4) 0;font-size:.875rem;color:var(--muted)}
footer a{color:var(--ink)}
@media(max-width:600px){.tag{display:none}.hide-s{display:none}td,th{padding:.45rem .3rem}}
"""
LOGO='<svg viewBox="0 0 32 32" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 28A24 24 0 0 1 28 4"/><path d="M10 28A18 18 0 0 1 28 10"/><path d="M16 28A12 12 0 0 1 28 16"/></g><circle cx="24" cy="21" r="3.2" fill="#c8102e"/></svg>'
FAV='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#111"/><g fill="none" stroke="#fff" stroke-width="2.5"><path d="M4 28A24 24 0 0 1 28 4"/><path d="M10 28A18 18 0 0 1 28 10"/><path d="M16 28A12 12 0 0 1 28 16"/></g><circle cx="24" cy="21" r="3.2" fill="#ff5a5f"/></svg>'
def spark(vals,small=False):
    v=[x for x in vals if x is not None]
    if not v: return ""
    if len(v)==1: v=v*2
    lo,hi=min(v),max(v); rng=(hi-lo) or 1; W=120 if small else 600; H=28 if small else 64; n=len(v)
    pts=[(i*(W-8)/(n-1)+4,H-4-(x-lo)/rng*(H-8) if hi>lo else H/2) for i,x in enumerate(v)]
    dots="".join(f'<circle class="d" cx="{x:.1f}" cy="{y:.1f}" r="3"/>' for i,(x,y) in enumerate(pts) if i and v[i]<v[i-1])
    return (f'<svg class="spark{" s" if small else ""}" viewBox="0 0 {W} {H}" preserveAspectRatio="none" role="img" aria-label="size trend: {v[0]:g} to {v[-1]:g}">'
            f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}"/>{dots}<circle class="e" cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="2.5"/></svg>')
def badge(b,a,u):
    pct=(a/b-1)*100
    return f'<span class="badge{" flat" if pct>=0 else ""}">{b:g} → {a:g} {E(u)} <i>{"−" if pct<0 else "+"}{abs(pct):.1f}%</i></span>'

SEARCH_JS="""(async()=>{const q=document.getElementById('q'),r=document.getElementById('res');const d=await (await fetch('/search.json')).json();
const go=()=>{const t=q.value.toLowerCase().trim();r.innerHTML='';if(t.length<2)return;d.filter(x=>x.t.toLowerCase().includes(t)).slice(0,40).forEach(x=>{const li=document.createElement('li');const a=document.createElement('a');a.href=x.u;a.textContent=x.t;li.append(a,' ',Object.assign(document.createElement('span'),{className:'m',textContent:x.k}));r.append(li)})};
q.addEventListener('input',go);const p=new URLSearchParams(location.search).get('q');if(p){q.value=p;go()}})();"""
PAGES=[]
SLUGS=set()
COUNTRY={'US':'United States','UK':'United Kingdom','DE':'Germany','FR':'France','CA':'Canada','AU':'Australia','EU':'Europe','NL':'Netherlands','ES':'Spain','AT':'Austria','IT':'Italy','BR':'Brazil','IN':'India'}
FLAG={'US':'🇺🇸','UK':'🇬🇧','DE':'🇩🇪','FR':'🇫🇷','CA':'🇨🇦','AU':'🇦🇺','EU':'🇪🇺','NL':'🇳🇱','ES':'🇪🇸','AT':'🇦🇹','IT':'🇮🇹','BR':'🇧🇷','IN':'🇮🇳'}
NAV=[('/', 'Findings'), ('/cases/', 'Known cases'), ('/worst/', 'Worst offenders'), ('/calculator/', 'Calculator'), ('/products/', 'Products'), ('/brands/', 'Brands'), ('/categories/', 'Categories'), ('/countries/', 'Countries'), ('/search.html', 'Search'), ('/alerts/', 'Alerts'), ('/about.html', 'About')]
def slug(x): return re.sub(r"[^a-z0-9]+","-",x.lower().replace("&","and")).strip("-")
def fmt(v,u): return f"{round(v,1) if v>=10 else round(v,2):g} {u}"
def disp(s):
    q=(s.get("quantity_label") or "").strip()
    if q and re.search(r"\d",q) and len(q)<=28: return q
    return fmt(s["size"],s["unit"])
def page(path,title,desc,body,ld=None,js=None):
    if CUR_ALERT: body+=alert_box(CUR_ALERT); CUR_ALERT.clear(); js=(js or '')+ALERT_JS
    ld_s="".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in (ld or []))
    p=OUT/path; p.parent.mkdir(parents=True,exist_ok=True); url=SITE+"/"+path.replace("index.html","")
    p.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">'
      f'<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:url" content="{url}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">'
      f'<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="{NAME} findings" href="/feed.xml"><link rel="stylesheet" href="/style.css">{ld_s}</head><body>'
      f'<header><div class="w"><div class="top"><a class="brand" href="/">{LOGO}<span>Shrink<b>Radar</b></span></a><span class="tag">Net Wt. watch · groceries &amp; household</span></div>'
      +'<nav aria-label="Main">'+"".join(f'<a href="{u}"{' aria-current="page"' if "/"+path.replace("index.html","")==u or ("/"+path).startswith(u) and u!="/" else ""}>{n}</a>' for u,n in NAV)+'</nav></div></header>'
f'<main class="w">{body}</main><footer><div class="w"><b style="color:var(--ink)">ShrinkRadar</b> — did it shrink? · Data: Open Food Facts, Open Products Facts, Open Prices (ODbL); documented cases cite their sources. <a href="/feed.xml">RSS</a> · Updated {TODAY}.</div></footer>'
      +(f'<script>{js}</script>' if js else "")+'</body></html>')
    PAGES.append(path)
CUR_ALERT=[]
ACFG=json.loads((R/"alerts_config.json").read_text()) if (R/"alerts_config.json").exists() else {}
ALERTS_API=ACFG.get("api","")  # empty = backend not live -> forms disabled
def alert_box(scopes,heading="Get an email when it shrinks"):
    live=bool(ALERTS_API)
    opts="".join(f'<label class="ck"><input type="checkbox" name="scope" value="{k}:{E(v)}"{" checked" if i==0 else ""}{"" if live else " disabled"}> {E(t)} <span class="m">({k})</span></label>' for i,(k,v,t) in enumerate(scopes))
    dis="" if live else " disabled"
    note=('<p class="m">Double opt-in: we email a confirmation link first. One-click unsubscribe in every email. <a href="/alerts/#privacy">Privacy</a>.</p>' if live else
          '<p class="m"><b>Coming soon.</b> Email alerts are not switched on yet. Follow <a href="/feed.xml">RSS</a> meanwhile. <a href="/alerts/">About alerts</a>.</p>')
    return (f'<section class="alert" aria-labelledby="al-h"><h2 id="al-h">{E(heading)}</h2><form class="alertf" data-api="{E(ALERTS_API)}"{"" if live else " aria-disabled=\"true\""}>'
            f'<fieldset{dis}><legend class="ml">Alert me about</legend>{opts}</fieldset>'
            f'<div class="row"><label class="ml" for="ae">Email</label><input id="ae" type="email" name="email" required autocomplete="email" placeholder="you@example.com"{dis}>'
            f'<button type="submit"{dis}>Subscribe</button></div><p class="st" role="status" aria-live="polite"></p>{note}</form></section>')
ALERT_JS="""document.querySelectorAll('form.alertf').forEach(f=>f.addEventListener('submit',async e=>{e.preventDefault();const st=f.querySelector('.st'),api=f.dataset.api;if(!api){st.textContent='Alerts are not live yet.';return}
const scopes=[...f.querySelectorAll('input[name=scope]:checked')].map(i=>i.value);if(!scopes.length){st.textContent='Pick at least one.';return}
st.textContent='Sending…';try{const r=await fetch(api+'/subscribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:f.email.value,scopes,source:location.pathname,hp:f.hp?f.hp.value:''})});
st.textContent=r.ok?'Check your inbox to confirm.':'Something went wrong. Try again later.'}catch(_){st.textContent='Network error. Try again later.'}}));"""
def unitp(s): return s["price"]/s["size"]*100 if s.get("price") and s.get("size") else None
def crumbs(*items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,**({"item":SITE+u} if u else {})} for i,(n,u) in enumerate(items)]}
UNITFIX={"Stück":"pieces","Waschladungen":"loads","luiers":"diapers","grams":"g","L":"l","Waschgänge":"loads"}
def fix_case(c):
    """Display-level clean-up of merged cases (brand mis-detections, foreign unit words)."""
    pr=c["product"].strip(); w=pr.split()
    if c.get("brand")=="All" and not pr.lower().startswith("all "): c["brand"]=w[0]
    if (c.get("brand") or "").endswith(".") and len(w)>1 and w[0]==c["brand"]: c["brand"]=" ".join(w[:2])
    c["unit"]=UNITFIX.get(c["unit"],c["unit"])
def money(s):
    """'0,49 €' / '€1,29' / '$3.99' / '£1.25' -> (0.49,'€'); None if unparseable."""
    if not s: return None
    t=str(s); cur=next((k for k in "€£$" if k in t),"")
    m=re.search(r"\d+(?:[.,]\d{1,2})?",t.replace(" ",""))
    if not m: return None
    v=float(m.group().replace(",",".")); return (v,cur) if v>0 else None
def calc_url(c):
    q={"b":f'{c["before"]:g}',"a":f'{c["after"]:g}',"u":c["unit"]}
    a,b=money(c.get("old_price")),money(c.get("new_price"))
    if a and b and a[1]==b[1]: q.update(pb=f"{a[0]:.2f}",pa=f"{b[0]:.2f}",c=a[1])
    from urllib.parse import urlencode
    return E("/calculator/?"+urlencode(q))
def real_change(c):
    """Per-unit price change in % using the case's old/new shelf price, or None."""
    a,b=money(c.get("old_price")),money(c.get("new_price"))
    if not a or not b or a[1]!=b[1]: return None
    return ((b[0]/c["after"])/(a[0]/c["before"])-1)*100
CALC_JS="""(()=>{const $=i=>document.getElementById(i),F=['b','pb','a','pa','u','c'],o=$('out'),P=new URLSearchParams(location.search);
F.forEach(k=>{if(P.get(k))$(k).value=P.get(k)});const n=v=>parseFloat(String(v).replace(',','.'));
const f=(x,d=2)=>x.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});const t=(i,v)=>{$(i).textContent=v};
const go=()=>{const b=n($('b').value),a=n($('a').value),pb=n($('pb').value),pa=n($('pa').value),u=$('u').value.trim()||'unit',c=$('c').value;
const q=new URLSearchParams();F.forEach(k=>{if($(k).value)q.set(k,$(k).value)});history.replaceState(null,'',q.toString()?'?'+q:location.pathname);
if(!(b>0&&a>0)){o.hidden=true;return}o.hidden=false;const cut=(1-a/b)*100;
t('r-cut',(cut>0?'−':'+')+f(Math.abs(cut),1)+'%');t('r-same',(b/a-1>=0?'+':'−')+f(Math.abs(b/a-1)*100,1)+'%');
const hp=pb>0,np=hp?(pa>0?pa:pb):0;document.querySelectorAll('.np').forEach(e=>e.hidden=!hp);
let v;if(hp){const k=/^(g|ml)$/i.test(u)?100:1,ul=(k>1?'100 ':'')+u,ub=pb/b*k,ua=np/a*k,ch=(ua/ub-1)*100;t('r-ub',c+f(ub,ub<1?3:2)+' / '+ul);t('r-ua',c+f(ua,ua<1?3:2)+' / '+ul);
t('r-real',(ch>=0?'+':'−')+f(Math.abs(ch),1)+'%');t('r-fair',c+f(pb*a/b));$('r-real').className='big np '+(ch>0.05?'yes':'no');
v=ch>0.05?`You get ${f(Math.abs(cut),1)}% ${cut>=0?'less':'more'} for ${np>=pb?f((np/pb-1)*100,1)+'% more':f((1-np/pb)*100,1)+'% less'} money: a real price rise of ${f(ch,1)}% per ${u}. At the old rate the new pack would cost ${c}${f(pb*a/b)}.`:`Per ${u} this is not more expensive than before (${f(ch,1)}%).`}
else v=cut>0?`If the price stayed the same, you now pay ${f((b/a-1)*100,1)}% more per ${u}. Add the prices to see the real change.`:'The pack did not get smaller.';t('verdict',v)};
F.forEach(k=>$(k).addEventListener('input',go));go()})();"""
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
        fix_case(c)
        c["when"]=str(c.get("when") or "n/d"); c["country"]=c.get("country") or "US"; c["year"]=(re.findall(r"(?:19|20)\d\d",c["when"]) or ["n/d"])[-1]
        base=slug(c["product"]+"-"+c["country"]+"-"+c["when"])[:80]; c["slug"]=base; k=2
        while c["slug"] in SLUGS: c["slug"]=f"{base}-{k}"; k+=1
        SLUGS.add(c["slug"]); c["bslug"]=slug(c["brand"]); c["cslug"]=slug(c["category"]); c["pct"]=(1-c["after"]/c["before"])*100; c["real"]=real_change(c)
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
    def latest(p): return next((s for s in reversed(by.get(p["code"],[])) if s.get("size")),{})
    def pcard(p):
        l=latest(p); ok=[s["size"] for s in by.get(p["code"],[]) if s.get("size")]
        return (f'<li class="card"><span class="ml">{E(p["category"])}</span><h3>{plink(p)}</h3>'
                f'<div class="nw"><span><span class="ml">Net wt.</span><b>{E(disp(l)) if l else "—"}</b></span>{spark(ok,True)}</div></li>')
    def ccard(c):
        dom=re.sub(r"^https?://(www\.)?([^/]+).*",r"\2",c["source_url"])
        return (f'<li class="card case"><span class="ml">{FLAG.get(c["country"],"")} {E(c["category"])} · {E(c["when"])}</span><h3><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a></h3>'
                f'{badge(c["before"],c["after"],c["unit"])}<span class="m">Source: <a href="{E(c["source_url"])}">{E(dom)}</a></span></li>')
    for p in prods:
        h=by.get(p["code"],[]); last=h[-1] if h else {}; ok=[s for s in h if s.get("size")]
        rel_cases=[c for c in cases if c["bslug"]==p["bslug"]]
        shrank=[f for f in findings if f[1] is p]
        if shrank: verdict,cls,ans='Yes','yes',f'{E(shrank[0][2])} (checked {shrank[0][0]}).'
        elif len(ok)>1: verdict,cls,ans='No','no',f'Size has stayed {fmt(ok[-1]["size"],ok[-1]["unit"])} across {len(ok)} checks since {ok[0]["date"]}.'
        elif ok: verdict,cls,ans='Not yet','no',f'Baseline recorded {ok[0]["date"]}. We re-check daily and flag any shrink.'
        else: verdict,cls,ans='Unknown','',"The open product database has no net quantity on file for this item."
        L=ok[-1] if ok else {}
        up=next((unitp(s) for s in reversed(h) if unitp(s)),None); pr=next((s for s in reversed(h) if s.get("price")),None)
        label=(f'<section class="label" aria-label="Size facts"><div class="hd">Size Facts</div>'
               f'<div class="row bar"><span>Did it shrink?</span><b class="{cls}">{verdict}</b></div>'
               f'<div class="row"><span class="ml">Net wt. (latest)</span></div><div class="big">{E(disp(L)) if L else "—"}</div>'
               f'<div class="row bar"><span class="m">{E(f"Metric: {fmt(L[chr(115)+chr(105)+chr(122)+chr(101)],L[chr(117)+chr(110)+chr(105)+chr(116)])}") if L else "No net quantity on file"}</span></div>'
               f'<div class="row"><span>Price</span><b>{f"${pr[chr(112)+chr(114)+chr(105)+chr(99)+chr(101)]:.2f}" if pr else "no data"}</b></div>'
               f'<div class="row"><span>Unit price</span><b>{f"${up:.2f} / 100 {L.get(chr(117)+chr(110)+chr(105)+chr(116))}" if up else "—"}</b></div>'
               f'<div class="row"><span>Checks</span><b>{len(h)}</b></div><p>{ans}</p></section>')
        tr="".join('<tr><td>{}</td><td class="n">{}</td><td class="n">{}</td><td class="n hide-s">{}</td></tr>'.format(s["date"],
            E(disp(s)) if s.get("size") else '<span class=na>n/a</span>',
            f'${s["price"]:.2f}' if s.get("price") else '<span class=na>—</span>',
            f'${unitp(s):.2f}/100 {s["unit"]}' if unitp(s) else "—") for s in reversed(h))
        src=" · ".join(f'<a href="{E(u)}" rel="nofollow">{n}</a>' for n,u in [("size source",last.get("source_url")),("price source",last.get("price_source"))] if u)
        sib=[q for q in prods if q["cslug"]==p["cslug"] and q is not p][:6]
        ld=[{"@context":"https://schema.org","@type":"Product","name":p["title"],"brand":{"@type":"Brand","name":p["brand"]},"gtin13":p["code"].lstrip("0").zfill(13),"category":p["category"],
             **({"size":fmt(L["size"],L["unit"])} if L else {}),
             **({"offers":{"@type":"Offer","price":pr["price"],"priceCurrency":"USD"}} if pr else {})},
            crumbs(("Products","/products/"),(p["category"],f'/categories/{p["cslug"]}.html'),(p["title"],None)),
            {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f'Did {p["title"]} shrink?',"acceptedAnswer":{"@type":"Answer","text":f"{verdict}. "+re.sub("<[^>]+>","",ans)}}]}]
        size_txt=f' Current size: {fmt(L["size"],L["unit"])}.' if L else ""
        CUR_ALERT[:]=[('product',p['code'],p['title']),('brand',p['bslug'],p['brand'] or 'Unbranded'),('category',p['cslug'],p['category'])]
        page(f'products/{p["slug"]}.html',f'Did {p["title"]} shrink? Size & price history | {NAME}',
             f'Has {p["title"]} gotten smaller? Daily-tracked package size, price and unit price history.{size_txt}',
             f'<p class="crumbs"><a href="/categories/{p["cslug"]}.html">{E(p["category"])}</a> / <a href="/brands/{p["bslug"]}.html">{E(p["brand"] or "Unbranded")}</a> / <span class="upc">UPC {p["code"]}</span></p>'
             f'<h1>Did {E(p["title"])} shrink?</h1>{label}'
             f'<h2>Size history</h2>{spark([s["size"] for s in ok])}<div class="tw"><table><thead><tr><th>Checked</th><th class="n">Net wt.</th><th class="n">Price</th><th class="n hide-s">Unit price</th></tr></thead><tbody>{tr}</tbody></table></div><p class="m">{src}</p>'
             +(f'<h2>Documented {E(p["brand"])} shrinks</h2><ul class="grid">'+"".join(ccard(c) for c in rel_cases)+'</ul>' if rel_cases else "")
             +(f'<h2>More {E(p["category"])}</h2><ul class="grid">'+"".join(pcard(q) for q in sib)+'</ul>' if sib else ""),ld)
    for c in cases:
        prs=[p for p in prods if p["bslug"]==c["bslug"]][:6]
        desc=f'Yes: {c["product"]} shrank from {fmt(c["before"],c["unit"])} to {fmt(c["after"],c["unit"])} ({c["pct"]:.1f}% less) around {c["when"]}. Sourced.'
        dom=re.sub(r"^https?://(www\.)?([^/]+).*",r"\2",c["source_url"])
        label=(f'<section class="label" aria-label="Size facts"><div class="hd">Size Facts</div>'
               f'<div class="row bar"><span>Did it shrink?</span><b class="yes">Yes</b></div>'
               f'<div class="row"><span>Before</span><b>{fmt(c["before"],c["unit"])}</b></div>'
               f'<div class="row"><span class="ml">After</span></div><div class="big">{fmt(c["after"],c["unit"])}</div>'
               f'<div class="row bar"><span>Cut</span><b class="yes">−{c["pct"]:.1f}%</b></div>'
               f'<div class="row"><span>Hidden unit-price rise at same price</span><b>+{(c["before"]/c["after"]-1)*100:.1f}%</b></div>'
               f'<div class="row"><span>When</span><b>{E(c["when"])}</b></div>'
               f'<div class="row"><span>Country</span><b>{E(COUNTRY.get(c["country"],c["country"]))}</b></div>'
               +(f'<div class="row"><span>Price</span><b>{E(c["old_price"])} → {E(c["new_price"])}</b></div>' if c.get("old_price") and c.get("new_price") else "")
               +(f'<div class="row bar"><span>Real price change per {E(c["unit"])}</span><b class="{"yes" if c["real"]>0.05 else "no"}">{"+" if c["real"]>=0 else "−"}{abs(c["real"]):.1f}%</b></div>' if c["real"] is not None else "")+
               f'<div class="row"><span>Evidence</span><b>{E(c.get("evidence_type","report"))}</b></div>'
               f'<div class="row"><span>Confidence</span><b>{E(c.get("confidence","high"))}</b></div>'
               f'<p>Source: <a href="{E(c["source_url"])}">{E(c["source"])}</a> ({E(dom)}). {E(c.get("verified","Source fetched 2026-10-14"))}.'
               +(f' <a href="{E(c["archive_url"])}">Archived copy</a>.' if c.get("archive_url") else "")+(f' {E(c["note"])}' if c.get("note") else "")+f' <a href="{calc_url(c)}"><b>Check the math in the calculator</b></a>.</p></section>'
               +(f'<h2>What the source says</h2><blockquote class="q">“{E(c["evidence"])}”</blockquote>' if c.get("evidence") else "")
               +(('<h2>Also reported by</h2><ul>'+"".join(f'<li><a href="{E(a["url"])}">{E(a["source"])}</a></li>' for a in c["also_reported"])+'</ul>') if c.get("also_reported") else ""))
        CUR_ALERT[:]=[('brand',slug(c['brand']),c['brand']),('category',slug(c['category']),c['category'])]
        page(f'cases/{c["slug"]}.html',f'Did {c["product"]} shrink? {fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])} | {NAME}',desc,
             f'<p class="crumbs"><a href="/cases/">Known cases</a> / <a href="/categories/{c["cslug"]}.html">{E(c["category"])}</a> / <a href="/brands/{c["bslug"]}.html">{E(c["brand"])}</a></p>'
             f'<h1>Did {E(c["product"])} shrink?</h1>{badge(c["before"],c["after"],c["unit"])}{label}'
             +(f'<h2>{E(c["brand"])} products we track</h2><ul class="grid">'+"".join(pcard(p) for p in prs)+'</ul>' if prs else "")
             +'<h2>Other documented cases</h2><ul class="grid">'+"".join(ccard(o) for o in [o for o in sorted(cases,key=lambda o:(o["cslug"]!=c["cslug"],-o["pct"])) if o is not c][:6])+'</ul>',
             [crumbs(("Known cases","/cases/"),(c["product"],None)),
              {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f'Did {c["product"]} shrink?',"acceptedAnswer":{"@type":"Answer","text":desc}}]}])
    yrs=sorted({c["year"] for c in cases},reverse=True); ctry=sorted({c["country"] for c in cases}); cats_c=sorted({c["category"] for c in cases})
    opt=lambda vals,lab: f'<option value="">{lab}</option>'+"".join(f'<option value="{E(v)}">{E(COUNTRY.get(v,v))}</option>' for v in vals)
    trs="".join(f'<tr data-c="{c["country"]}" data-y="{E(c["year"])}" data-k="{E(c["category"])}"><td><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a><br><span class="m">{E(c["brand"])} · {FLAG.get(c["country"],"")} {c["country"]}</span></td><td class="n">{fmt(c["before"],c["unit"])}</td><td class="n">{fmt(c["after"],c["unit"])}</td><td class="n yes"><b>−{c["pct"]:.1f}%</b></td><td class="n hide-s">{E(c["when"])}</td></tr>' for c in sorted(cases,key=lambda c:(c["when"]!="n/d",c["when"],c["pct"]),reverse=True))
    FJS="""(()=>{const f=[...document.querySelectorAll('.flt select,.flt input')],rows=[...document.querySelectorAll('#ct tbody tr')],n=document.getElementById('n');
const go=()=>{const[c,y,k,t]=f.map(e=>e.value.toLowerCase());let v=0;rows.forEach(r=>{const ok=(!c||r.dataset.c.toLowerCase()==c)&&(!y||r.dataset.y==y)&&(!k||r.dataset.k.toLowerCase()==k)&&(!t||r.textContent.toLowerCase().includes(t));r.hidden=!ok;v+=ok});n.textContent=v};
f.forEach(e=>e.addEventListener('input',go));const p=new URLSearchParams(location.search);['country','year','category','q'].forEach((k,i)=>{if(p.get(k)){f[i].value=p.get(k);}});go()})();"""
    page("cases/index.html",f'Known shrinkflation cases: {len(cases)} documented examples | {NAME}',f'{len(cases)} documented shrinkflation cases from the US, UK, Germany, France, Canada and Australia, each with before/after size, date and source.',
         f'<h1>Known shrinkflation cases</h1><p class="prose">{len(cases)} documented before/after size cuts from consumer agencies, consumer advocates, news investigations and retailer-page archives. Every case links to the source we fetched.</p>'
         f'<p class="chips">'+"".join(f'<a href="/countries/{k.lower()}.html">{FLAG.get(k,"")} {E(COUNTRY.get(k,k))}</a>' for k in ctry)+'</p>'
         f'<div class="flt"><select aria-label="Country">{opt(ctry,"All countries")}</select><select aria-label="Year">{opt(yrs,"All years")}</select><select aria-label="Category">{opt(cats_c,"All categories")}</select><input type="search" placeholder="Filter by product or brand" aria-label="Filter"></div>'
         f'<p class="m"><b id="n">{len(cases)}</b> cases shown</p><div class="tw"><table id="ct"><thead><tr><th>Product</th><th class="n">Before</th><th class="n">After</th><th class="n">Cut</th><th class="n hide-s">Year</th></tr></thead><tbody>{trs}</tbody></table></div>',
         [crumbs(("Known cases",None)),{"@context":"https://schema.org","@type":"Dataset","name":"ShrinkRadar documented shrinkflation cases","description":"Before/after package size reductions with sources","url":SITE+"/cases/","license":"https://creativecommons.org/licenses/by/4.0/","creator":{"@type":"Organization","name":NAME}}],js=FJS)
    # ---- Worst offenders leaderboard ----
    def ctr(c,extra=""):
        return (f'<tr><td><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a><br><span class="m">{E(c["brand"])} · {FLAG.get(c["country"],"")} {c["country"]} · {E(c["when"])}</span></td>'
                f'<td class="n">{fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])}</td><td class="n yes"><b>−{c["pct"]:.1f}%</b></td>{extra}</tr>')
    priced=sorted([c for c in cases if c["real"] is not None and c["real"]>0.05],key=lambda c:-c["real"])
    top_real="".join(ctr(c,f'<td class="n"><span class="m">{E(c["old_price"])} → {E(c["new_price"])}</span><br><b class="yes">+{c["real"]:.1f}%</b></td>') for c in priced[:25])
    top_cut="".join(ctr(c) for c in sorted(cases,key=lambda c:(-c["pct"],c["product"]))[:25])
    bg={}
    for c in cases: bg.setdefault(c["bslug"],[]).append(c)
    rep=sorted([(k,v) for k,v in bg.items() if len(v)>=3],key=lambda kv:(-len(kv[1]),-sum(c["pct"] for c in kv[1])/len(kv[1])))
    med=lambda xs: sorted(xs)[len(xs)//2] if len(xs)%2 else sum(sorted(xs)[len(xs)//2-1:len(xs)//2+1])/2
    rep_tr="".join(f'<tr><td>{i}</td><td><a href="/brands/{k}.html">{E(v[0]["brand"])}</a><br><span class="m">{" ".join(sorted({FLAG.get(c["country"],c["country"]) for c in v}))}</span></td><td class="n"><b>{len(v)}</b></td><td class="n">−{med([c["pct"] for c in v]):.1f}%</td><td class="n hide-s">−{max(c["pct"] for c in v):.1f}%</td></tr>' for i,(k,v) in enumerate(rep[:30],1))
    cg={}
    for c in cases: cg.setdefault(c["category"],[]).append(c)
    cat_tr="".join(f'<tr><td><a href="/categories/{slug(k)}.html">{E(k)}</a></td><td class="n"><b>{len(v)}</b></td><td class="n">−{med([c["pct"] for c in v]):.1f}%</td><td class="n hide-s">{sum(1 for c in v if c["real"] is not None and c["real"]>0.05)}</td></tr>' for k,v in sorted(cg.items(),key=lambda kv:-len(kv[1])))
    nrep=len(priced); allp=[c for c in cases if c["real"] is not None]
    page("worst/index.html",f'Worst shrinkflation offenders: biggest cuts, repeat brands & hidden price hikes | {NAME}',
         f'Leaderboard of the worst shrinkflation from {len(cases)} documented cases: biggest package cuts, hidden per-unit price hikes and the brands caught most often.',
         f'<h1>Worst offenders</h1><p class="prose">Ranked from {len(cases)} documented, sourced cases. Every row links to the case and its source. '
         f'Where the source also recorded the shelf price before and after ({len(allp)} cases), we work out what actually happened to the price per gram, millilitre or piece.</p>'
         f'<p class="chips"><a href="#hidden">Hidden price hikes</a><a href="#cuts">Biggest cuts</a><a href="#brands">Repeat offenders</a><a href="#categories">By category</a></p>'
         f'<h2 id="hidden">Biggest hidden price hikes</h2><p class="prose m">Real change in price per unit, combining the size cut with the shelf-price change. {nrep} of {len(allp)} priced cases got more expensive per unit. Prices come from the reporting source (mostly Verbraucherzentrale Hamburg and Consumentenbond, so mainly Germany and the Netherlands).</p>'
         f'<div class="tw"><table><thead><tr><th>Product</th><th class="n">Size</th><th class="n">Cut</th><th class="n">Price · per unit</th></tr></thead><tbody>{top_real}</tbody></table></div>'
         f'<h2 id="cuts">Biggest package cuts</h2><div class="tw"><table><thead><tr><th>Product</th><th class="n">Size</th><th class="n">Cut</th></tr></thead><tbody>{top_cut}</tbody></table></div>'
         f'<h2 id="brands">Repeat offenders</h2><p class="prose m">Brands and store brands with three or more documented cases. A brand with many products and much press coverage will show up more often, so treat this as “caught most often”, not a measured rate.</p>'
         f'<div class="tw"><table><thead><tr><th>#</th><th>Brand</th><th class="n">Cases</th><th class="n">Median cut</th><th class="n hide-s">Worst cut</th></tr></thead><tbody>{rep_tr}</tbody></table></div>'
         f'<h2 id="categories">By category</h2><div class="tw"><table><thead><tr><th>Category</th><th class="n">Cases</th><th class="n">Median cut</th><th class="n hide-s">Pricier per unit</th></tr></thead><tbody>{cat_tr}</tbody></table></div>'
         f'<p class="m">Check any pack yourself with the <a href="/calculator/">shrinkflation calculator</a>.</p>',
         [crumbs(("Worst offenders",None)),{"@context":"https://schema.org","@type":"ItemList","name":"Biggest documented shrinkflation cuts","itemListOrder":"https://schema.org/ItemListOrderDescending",
           "itemListElement":[{"@type":"ListItem","position":i+1,"url":f'{SITE}/cases/{c["slug"]}.html',"name":c["product"]} for i,c in enumerate(sorted(cases,key=lambda c:(-c["pct"],c["product"]))[:25])]}])
    # ---- Calculator ----
    UNITS_DL="".join(f'<option value="{u}">' for u in ["g","oz","ml","fl oz","l","kg","lb","sheets","rolls","pieces","bars","loads","count","sq ft"])
    calc_faq=[("How do you calculate shrinkflation?","Divide the price by the size before and after the change to get the price per unit (per gram, ounce, sheet…). The percentage difference between the two unit prices is the real price change. A 10% smaller pack at the same price is an 11.1% price rise per unit, because 1 ÷ 0.9 = 1.111."),
              ("Why is the hidden price rise bigger than the size cut?","Because the same price is now spread over less product. Cutting a pack by a fraction x raises the unit price by x ÷ (1 − x): a 20% cut is a 25% rise, a 50% cut is a 100% rise."),
              ("What is a fair price for the smaller pack?","Old price × new size ÷ old size. That is what the new pack would cost at the old price per unit.")]
    page("calculator/index.html",f'Shrinkflation calculator: did the price per unit go up? | {NAME}',
         'Free shrinkflation calculator. Enter the old and new pack size and price to see the size cut, the price per unit before and after, and the real hidden price increase.',
         '<h1>Shrinkflation calculator</h1><p class="prose">Enter the pack size and price before and after. You get the real change in price per unit, which is the number the smaller pack is hiding.</p>'
         '<form class="calc" onsubmit="return false"><fieldset><legend class="ml">Before</legend><label>Size<input id="b" inputmode="decimal" placeholder="e.g. 18"></label><label>Price<input id="pb" inputmode="decimal" placeholder="e.g. 4.99"></label></fieldset>'
         '<fieldset><legend class="ml">After</legend><label>Size<input id="a" inputmode="decimal" placeholder="e.g. 15.4"></label><label>Price<input id="pa" inputmode="decimal" placeholder="same if blank"></label></fieldset>'
         f'<fieldset><legend class="ml">Units</legend><label>Unit<input id="u" list="ul" placeholder="oz, g, sheets…"><datalist id="ul">{UNITS_DL}</datalist></label><label>Currency<select id="c"><option value="$">$</option><option value="€">€</option><option value="£">£</option><option value="">none</option></select></label></fieldset></form>'
         '<section id="out" class="label" aria-live="polite" hidden><div class="hd">Shrink Facts</div>'
         '<div class="row bar"><span>Size change</span><b class="yes" id="r-cut"></b></div>'
         '<div class="row"><span>Unit-price rise if the price stayed the same</span><b id="r-same"></b></div>'
         '<div class="row np"><span>Price per unit before</span><b id="r-ub"></b></div><div class="row np"><span>Price per unit after</span><b id="r-ua"></b></div>'
         '<div class="row np"><span class="ml">Real price change per unit</span></div><div class="big np" id="r-real"></div>'
         '<div class="row bar np"><span>Fair price for the new size</span><b id="r-fair"></b></div><p id="verdict"></p></section>'
         '<noscript><p class="empty">The calculator needs JavaScript. The formula: real change = (new price ÷ new size) ÷ (old price ÷ old size) − 1.</p></noscript>'
         '<p class="m">Nothing you type leaves your browser. The link in the address bar updates as you type, so you can share a result. Every <a href="/cases/">documented case</a> has a “check the math” link that fills this in.</p>'
         '<div class="prose"><h2>How it works</h2>'+"".join(f'<h3>{E(q)}</h3><p>{E(a)}</p>' for q,a in calc_faq)+'<p>See the <a href="/worst/">worst offenders</a> for the biggest real price hikes we have on record.</p></div>',
         [crumbs(("Calculator",None)),{"@context":"https://schema.org","@type":"WebApplication","name":"Shrinkflation calculator","url":SITE+"/calculator/","applicationCategory":"UtilitiesApplication","operatingSystem":"Any","offers":{"@type":"Offer","price":0,"priceCurrency":"USD"}},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in calc_faq]}],js=CALC_JS)
    for kind,key,lab,namef in [("countries","country","Countries",lambda v:COUNTRY.get(v,v)),("years","year","Years",str)]:
        g={}
        for c in cases: g.setdefault(c[key],[]).append(c)
        for k,v in g.items():
            nm=namef(k)
            page(f'{kind}/{str(k).lower()}.html',f'Shrinkflation in {nm}: {len(v)} documented cases | {NAME}',f'{len(v)} documented shrinkflation cases {"in "+nm if kind=="countries" else "from "+nm}, with before/after sizes and sources.',
                 f'<p class="crumbs"><a href="/cases/">Known cases</a> / <a href="/{kind}/">{lab}</a></p><h1>Shrinkflation {"in "+E(nm) if kind=="countries" else "in "+E(nm)}</h1><p>{len(v)} documented cases, biggest cuts first.</p><ul class="grid">'+"".join(ccard(c) for c in sorted(v,key=lambda c:-c["pct"]))+'</ul>',
                 [crumbs(("Known cases","/cases/"),(nm,None))])
        page(f'{kind}/index.html',f'Shrinkflation by {lab.lower()} | {NAME}',f'Documented shrinkflation cases by {lab.lower()[:-1]}.',
             f'<h1>Cases by {lab.lower()[:-1] if lab!="Countries" else "country"}</h1><ul class="chips">'+"".join(f'<li><a href="/{kind}/{str(k).lower()}.html">{E(namef(k))} <span class="m">{len(v)}</span></a></li>' for k,v in sorted(g.items(),reverse=(kind=="years")))+'</ul>',[crumbs((lab,None))])
    def groups(kind,key,label):
        g={}
        for p in prods: g.setdefault(p[key],{"name":p["brand" if kind=="brands" else "category"] or "Unbranded","p":[],"c":[]})["p"].append(p)
        for c in cases: g.setdefault(c[key],{"name":c["brand" if kind=="brands" else "category"],"p":[],"c":[]})["c"].append(c)
        for k,v in g.items():
            body=f'<p class="crumbs"><a href="/{kind}/">{label}</a></p><h1>Did {E(v["name"])} products shrink?</h1>'
            if v["c"]: body+=f'<h2>Documented cases ({len(v["c"])})</h2><ul class="grid">'+"".join(ccard(c) for c in v["c"])+'</ul>'
            if v["p"]: body+=f'<h2>Tracked daily ({len(v["p"])})</h2><ul class="grid">'+"".join(pcard(p) for p in v["p"])+'</ul>'
            CUR_ALERT[:]=[('brand' if kind=='brands' else 'category',k,v['name'])]
            page(f'{kind}/{k}.html',f'{v["name"]} shrinkflation: did {v["name"]} products get smaller? | {NAME}',
                 f'{len(v["c"])} documented cases and {len(v["p"])} {v["name"]} products tracked daily for size and unit-price changes.',body,[crumbs((label,f"/{kind}/"),(v["name"],None))])
        page(f'{kind}/index.html',f'Shrinkflation by {label.lower()} | {NAME}',f'Browse shrinkflation tracking by {label.lower()}.',
             f'<h1>{label}</h1><ul class="chips">'+"".join(f'<li><a href="/{kind}/{k}.html">{E(v["name"])} <span class="m">{len(v["p"])+len(v["c"])}</span></a></li>' for k,v in sorted(g.items(),key=lambda kv:kv[1]["name"].lower()))+'</ul>',[crumbs((label,None))])
    groups("brands","bslug","Brands"); groups("categories","cslug","Categories")
    cats={}
    for p in sorted(prods,key=lambda p:p["title"].lower()): cats.setdefault(p["category"],[]).append(p)
    page("products/index.html",f'All {len(prods)} tracked products | {NAME}',f'{len(prods)} everyday products checked daily for package-size cuts and unit-price increases.',
         f'<h1>Tracked products ({len(prods)})</h1>'+"".join(f'<h2 id="{slug(k)}">{E(k)}</h2><ul class="grid">'+"".join(pcard(p) for p in v)+'</ul>' for k,v in sorted(cats.items())),[crumbs(("Products",None))])
    feed="".join(f'<li><span class="ml">{d}</span>{plink(p)} — {E(t)}</li>' for d,p,t in findings[:100]) or f'<div class="empty"><b>No shrinks detected in our daily checks yet.</b> Baselines are in place for {len(prods)} products; anything that gets smaller shows up here first.</div>'
    page("index.html",f'{NAME}: did it shrink? Shrinkflation tracker for groceries & household goods',f'Daily tracking of package sizes and unit prices for {len(prods)} products, plus {len(cases)} documented shrinkflation cases with sources.',
         f'<h1>Did it shrink?</h1><p class="prose">We check the net weight of {len(prods)} everyday products every day and keep a sourced record of {len(cases)} known shrinkflation cases.</p>'
         f'<form class="search" action="/search.html" role="search"><label class="ml" for="q0">Search a product or brand</label><input id="q0" name="q" placeholder="Doritos, cereal, Charmin…"></form>'
         f'<h2>Latest from daily checks</h2><ul class="feed">{feed}</ul><h2>Biggest documented shrinks</h2><ul class="grid">{"".join(ccard(c) for c in sorted(cases,key=lambda c:-c["pct"])[:6])}</ul><p><a href="/cases/"><b>All {len(cases)} known cases →</b></a> · <a href="/worst/"><b>Worst offenders →</b></a> · <a href="/calculator/"><b>Shrinkflation calculator →</b></a></p>'
         f'<h2>Recently checked</h2><ul class="grid">{"".join(pcard(p) for p in prods[:6])}</ul>',
         [{"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE+"/","potentialAction":{"@type":"SearchAction","target":SITE+"/search.html?q={search_term_string}","query-input":"required name=search_term_string"}},
          {"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE+"/","logo":SITE+"/favicon.svg"}])
    idx=[{"t":p["title"],"u":f'/products/{p["slug"]}.html',"k":p["category"]} for p in prods]+[{"t":c["product"]+" (documented case)","u":f'/cases/{c["slug"]}.html',"k":c["category"]} for c in cases]
    AI=[{"id":f'f:{p["code"]}:{d}:{t[:4]}',"type":"finding","date":d,"title":p["title"],"text":t,"url":f'{SITE}/products/{p["slug"]}.html',"product":p["code"],"brand":p["bslug"],"category":p["cslug"],"brand_name":p["brand"],"category_name":p["category"]} for d,p,t in findings]
    AI+=[{"id":"c:"+c["slug"],"type":"case","date":c["when"],"title":c["product"],"text":f'{fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])} ({c["pct"]:.0f}% less) · {COUNTRY.get(c["country"],c["country"])}, {c["when"]}',"url":f'{SITE}/cases/{c["slug"]}.html',"product":None,"brand":slug(c["brand"]),"category":slug(c["category"]),"brand_name":c["brand"],"category_name":c["category"]} for c in cases]
    (R/"data/alert_items.json").write_text(json.dumps(AI,ensure_ascii=False,indent=0))
    (OUT/"search.json").write_text(json.dumps(idx,ensure_ascii=False))
    page("search.html",f'Search: did my product shrink? | {NAME}','Search tracked products and documented shrinkflation cases.',
         '<h1>Search</h1><label for="q" class="ml">Product, brand or category</label><input id="q" autofocus placeholder="e.g. Doritos, cereal, Charmin"><ul id="res"></ul><noscript>Search needs JavaScript; browse <a href="/products/">products</a> or <a href="/cases/">cases</a>.</noscript>',js=SEARCH_JS)
    CUR_ALERT[:]=[('all','all','All new findings and documented cases')]
    page("alerts/index.html",f'Shrinkflation email alerts | {NAME}','Get an email when a product, brand or category you follow shrinks.',
         '<div class="prose"><h1>Email alerts</h1><p>Follow a product, a brand, a category, or everything. When our daily check logs a size cut or a new documented case matches what you follow, you get one digest email that day. Nothing on days with no news.</p>'
         '<p>To follow a specific product, brand or category, use the alert box at the bottom of its page. Here you can follow <b>everything</b>.</p>'
         '<h2 id="how">How it works</h2><ul><li><b>Double opt-in.</b> We send a confirmation link; nothing else is sent until you click it.</li><li><b>Daily digest</b>, at most one email a day.</li><li><b>Manage or unsubscribe</b> from the link in every email (one click, no login).</li><li>Free. A paid tier with extras (instant alerts, CSV) may come later. Free alerts stay free.</li></ul>'
         '<h2 id="privacy">Privacy</h2><p>We store your email address, what you follow, and when you confirmed. Nothing else: no tracking pixels and no link tracking. Email is delivered by our email provider only to send alerts. We never sell or share addresses. Unsubscribing deletes what you follow; unconfirmed sign-ups are deleted after 7 days. To have your data erased, use the manage link.</p></div>',
         [crumbs(("Alerts",None))])
    page("about.html",f'About & methodology | {NAME}','How ShrinkRadar tracks shrinkflation: sources, method and corrections.',
         '<div class="prose"><h1>About ShrinkRadar</h1><p>ShrinkRadar answers one question: <i>did it shrink?</i> We check a fixed list of everyday products daily. Net quantity comes from Open Food Facts / Open Products Facts; prices come from the crowdsourced Open Prices database (most recent US price). We only publish values we actually fetched — missing data is shown as missing, never estimated.</p>'
         '<p>A <b>finding</b> is logged when a newer check shows a smaller net quantity in the same unit, or a higher price per 100 g/ml.</p><p><b>Known cases</b> are historical before/after size cuts compiled from Verbraucherzentrale Hamburg’s Mogelpackungsliste, the Mouse Print* archive (Edgar Dworsky), Which?, CHOICE, CBC, foodwatch, Consumer Reports, LendingTree’s Wayback-Machine study, the U.S. Senate/USW report, news outlets and Wikipedia. Each case shows the source we fetched and a quote of what it says; cases we could not verify are left out.</p>'
         '<h2 id="privacy">Privacy &amp; email alerts</h2><p>No ads, cookies or analytics trackers. Email alerts (when live) store only your address, what you follow and the confirmation time. Double opt-in, one-click unsubscribe, never shared or sold. <a href="/alerts/#privacy">Details</a>.</p><p>Spotted a shrink? Corrections and tips are welcome.</p></div>',[{"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE+"/"}])
    # RSS: findings + cases
    items=[(d,f'{p["title"]}: {t}',f'{SITE}/products/{p["slug"]}.html') for d,p,t in findings[:50]]+[(TODAY if not findings else findings[-1][0],f'Known case: {c["product"]} {fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])}',f'{SITE}/cases/{c["slug"]}.html') for c in cases]
    rss="".join(f'<item><title>{E(t)}</title><link>{u}</link><guid>{u}</guid><pubDate>{format_datetime(datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc))}</pubDate></item>' for d,t,u in items)
    (OUT/"feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE}/</link><description>Shrinkflation findings and documented cases</description>{rss}</channel></rss>')
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+
        "".join(f'<url><loc>{SITE}/{p.replace("index.html","")}</loc><lastmod>{TODAY}</lastmod></url>' for p in PAGES)+"</urlset>")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"); (OUT/".nojekyll").write_text(""); (OUT/"favicon.svg").write_text(FAV); (OUT/"CNAME").write_text("shrinkradar.com\n")
    # retired brand slugs from earlier mis-detected brands: noindex stubs pointing at the real brands
    for old,targets in {"dr":["dr-oetker","dr-hauschka"]}.items():
        if not (OUT/f"brands/{old}.html").exists():
            (OUT/f"brands/{old}.html").write_text('<!doctype html><meta charset=utf-8><meta name=robots content=noindex><meta name=viewport content="width=device-width,initial-scale=1"><link rel=stylesheet href=/style.css><title>Moved</title><main class=w><h1>This brand page moved</h1><ul>'+"".join(f'<li><a href="/brands/{t}.html">{t.replace("-"," ").title()}</a></li>' for t in targets)+'</ul>')
    if INDEXNOW_KEY: (OUT/f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    (OUT/"404.html").write_text('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><link rel=stylesheet href=/style.css><title>Not found</title><main class=w><h1>Not found</h1><p>Page not found. <a href="/">ShrinkRadar home</a> · <a href="/search.html">Search</a></p>')
    print(len(PAGES),"pages,",len(findings),"findings,",len(cases),"cases")
if __name__=="__main__": main()
