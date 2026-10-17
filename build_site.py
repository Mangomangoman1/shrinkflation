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
.calc label{display:block;font-weight:700;font-size:.875rem;margin-top:var(--s2)}.calc input,.calc select,.calc textarea{display:block;width:100%;margin-top:.2rem;font:700 1.15rem var(--f);padding:.55rem .6rem;border:2px solid var(--ink);border-radius:0;background:var(--paper);color:var(--ink)}.calc textarea{font-weight:400;line-height:1.45;resize:vertical;min-height:6rem}
.submit-actions{grid-column:1/-1;margin-top:var(--s2)}.submit-actions button,.label button,#copy{font:900 .95rem var(--f);text-transform:uppercase;letter-spacing:.04em;padding:.7rem 1.1rem;border:2px solid var(--ink);background:var(--ink);color:var(--paper);border-radius:0;cursor:pointer}.submit-actions button:hover,.label button:hover,#copy:hover{background:var(--sig);border-color:var(--sig)}
#md{width:100%;font:400 .875rem ui-monospace,monospace;padding:.6rem;border:2px solid var(--ink);background:var(--paper);color:var(--ink);border-radius:0;resize:vertical}
.st{min-height:1.2em;margin:var(--s2) 0;font-weight:700}
.label .big.no{color:var(--ok)}.label .big.yes{color:var(--sig)}[hidden]{display:none!important}
footer{border-top:8px solid var(--ink);background:var(--panel);padding:var(--s4) 0;font-size:.875rem;color:var(--muted)}
footer a{color:var(--ink)}
@media(max-width:600px){.tag{display:none}.hide-s{display:none}td,th{padding:.45rem .3rem}.calc{grid-template-columns:1fr;gap:var(--s2)}.calc fieldset{padding:var(--s2)}.calc input,.calc select,.calc textarea{font-size:1rem;padding:.65rem .6rem}.submit-actions button{width:100%}.alert .row{flex-direction:column;align-items:stretch}.alert input[type=email],.alert button{width:100%;flex:none}}
"""
LOGO='<svg viewBox="0 0 32 32" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 28A24 24 0 0 1 28 4"/><path d="M10 28A18 18 0 0 1 28 10"/><path d="M16 28A12 12 0 0 1 28 16"/></g><circle cx="24" cy="21" r="3.2" fill="#c8102e"/></svg>'
FAV='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#111"/><g fill="none" stroke="#fff" stroke-width="2.5"><path d="M4 28A24 24 0 0 1 28 4"/><path d="M10 28A18 18 0 0 1 28 10"/><path d="M16 28A12 12 0 0 1 28 16"/></g><circle cx="24" cy="21" r="3.2" fill="#ff5a5f"/></svg>'
OG=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#111"/><rect y="610" width="1200" height="20" fill="#ff5a5f"/>'
    '<g fill="none" stroke="#fff" stroke-width="22" transform="translate(860 150) scale(10)"><path d="M4 28A24 24 0 0 1 28 4" stroke-width="2.5"/><path d="M10 28A18 18 0 0 1 28 10" stroke-width="2.5"/><path d="M16 28A12 12 0 0 1 28 16" stroke-width="2.5"/></g><circle cx="1100" cy="360" r="32" fill="#ff5a5f"/>'
    '<text x="80" y="300" fill="#fff" font-family="Helvetica Neue,Helvetica,Arial,sans-serif" font-weight="900" font-size="120" letter-spacing="-4">Shrink<tspan fill="#ff5a5f">Radar</tspan></text>'
    '<text x="84" y="390" fill="#f2f0ea" font-family="Helvetica Neue,Helvetica,Arial,sans-serif" font-weight="700" font-size="56">Did it shrink?</text>'
    '<text x="84" y="520" fill="#a9a59c" font-family="Helvetica Neue,Helvetica,Arial,sans-serif" font-weight="700" font-size="30" letter-spacing="3">NET WT. WATCH · SOURCED SHRINKFLATION CASES</text></svg>')
def og_png(path):
    """Raster twin of OG (X/Facebook/LinkedIn ignore SVG og:image). Needs Pillow; skipped if missing."""
    try: from PIL import Image,ImageDraw,ImageFont
    except ImportError: return False
    F=lambda n,sz: ImageFont.truetype(f"/usr/share/fonts/truetype/liberation/LiberationSans-{n}.ttf",sz)
    im=Image.new("RGB",(1200,630),"#111"); d=ImageDraw.Draw(im); d.rectangle([0,610,1200,630],fill="#ff5a5f")
    for r in (240,180,120): d.arc([1180-2*r,520-2*r,1180,520],180,270,fill="#fff",width=24)
    d.ellipse([1068,328,1132,392],fill="#ff5a5f")
    f=F("Bold",124); d.text((80,190),"Shrink",font=f,fill="#fff"); d.text((80+d.textlength("Shrink",font=f),190),"Radar",font=f,fill="#ff5a5f")
    d.text((84,340),"Did it shrink?",font=F("Bold",58),fill="#f2f0ea"); d.text((84,490),"NET WT. WATCH · SOURCED SHRINKFLATION CASES",font=F("Bold",30),fill="#a9a59c")
    im.save(path,optimize=True); return True
OGIMG="/og.png"
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
const go=()=>{const t=q.value.toLowerCase().trim();r.innerHTML='';if(t.length<2)return;const dg=t.replace(/[\\s-]/g,'');if(/^\\d{8,14}$/.test(dg)){const li=document.createElement('li'),a=document.createElement('a');a.href='/barcode/?code='+dg;a.textContent='Look up barcode '+dg;li.append(a,' ',Object.assign(document.createElement('span'),{className:'m',textContent:'Barcode'}));r.append(li)}d.filter(x=>x.t.toLowerCase().includes(t)).slice(0,40).forEach(x=>{const li=document.createElement('li');const a=document.createElement('a');a.href=x.u;a.textContent=x.t;li.append(a,' ',Object.assign(document.createElement('span'),{className:'m',textContent:x.k}));r.append(li)})};
q.addEventListener('input',go);const p=new URLSearchParams(location.search).get('q');if(p){q.value=p;go()}})();"""
PAGES=[]
SLUGS=set()
COUNTRY={'US':'United States','UK':'United Kingdom','DE':'Germany','FR':'France','CA':'Canada','AU':'Australia','EU':'Europe','NL':'Netherlands','ES':'Spain','AT':'Austria','IT':'Italy','BR':'Brazil','IN':'India','NZ':'New Zealand'}
FLAG={'US':'🇺🇸','UK':'🇬🇧','DE':'🇩🇪','FR':'🇫🇷','CA':'🇨🇦','AU':'🇦🇺','EU':'🇪🇺','NL':'🇳🇱','ES':'🇪🇸','AT':'🇦🇹','IT':'🇮🇹','BR':'🇧🇷','IN':'🇮🇳'}
NAV=[('/', 'Findings'), ('/cases/', 'Known cases'), ('/worst/', 'Worst offenders'), ('/calculator/', 'Calculator'), ('/barcode/', 'Barcode'), ('/submit/', 'Submit'), ('/products/', 'Products'), ('/brands/', 'Brands'), ('/categories/', 'Categories'), ('/guides/', 'Guides'), ('/countries/', 'Countries'), ('/search.html', 'Search'), ('/alerts/', 'Alerts'), ('/about.html', 'About')]
def slug(x): return re.sub(r"[^a-z0-9]+","-",x.lower().replace("&","and")).strip("-")
def bslug(x):
    """Brand slug; non-Latin names (empty ASCII slug) get a stable hash slug instead of colliding on ''."""
    import hashlib
    return slug(x) or "b-"+hashlib.md5(x.encode()).hexdigest()[:8]
def fmt(v,u): return f"{round(v,1) if v>=10 else round(v,2):g} {u}"
def disp(s):
    q=(s.get("quantity_label") or "").strip()
    if q and re.search(r"\d",q) and len(q)<=28: return q
    return fmt(s["size"],s["unit"])
TITLE_MAX=60
def fit(*cands):
    """First candidate title that fits in TITLE_MAX chars, else the last (shortest) one."""
    return next((t for t in cands if len(t)<=TITLE_MAX),min(cands,key=len))
def page(path,title,desc,body,ld=None,js=None):
    if isinstance(title,(list,tuple)): title=fit(*title)
    sfx=f" | {NAME}"
    if len(title)>TITLE_MAX and title.endswith(sfx): title=title[:-len(sfx)]
    if CUR_ALERT: body+=alert_box(CUR_ALERT); CUR_ALERT.clear(); js=(js or '')+ALERT_JS
    ld_s="".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in (ld or []))
    p=OUT/path; p.parent.mkdir(parents=True,exist_ok=True); url=SITE+"/"+path.replace("index.html","")
    p.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">'
      f'<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:url" content="{url}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">'
      f'<meta property="og:image" content="{SITE}{OGIMG}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="ShrinkRadar: did it shrink?">'
      f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{SITE}{OGIMG}"><meta name="theme-color" content="#111">'
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
    for pre,b in BRANDFIX:
        if pr.lower().startswith(pre.lower()) or c.get("brand")==pre: c["brand"]=b; break
    c["unit"]=UNITFIX.get(c["unit"],c["unit"])
    sym={"GBP":"£","EUR":"€","USD":"$"}.get(c.get("currency"))
    if sym and not c.get("old_price") and c.get("before_price") and c.get("after_price"):
        c["old_price"],c["new_price"]=f'{sym}{c["before_price"]:.2f}',f'{sym}{c["after_price"]:.2f}'
# product-prefix (or raw brand) -> real brand, for multi-word brands the miners cut short
BRANDFIX=[("Gut & Günstig","Gut & Günstig"),("La Trappe","La Trappe"),("La Vache Qui Rit","La Vache qui rit"),("costcotuna","Kirkland")]
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
SUBMIT_JS="""(()=>{const $=id=>document.getElementById(id),f=$('sight'),st=$('st'),md=$('md'),fb=$('fallback');
const val=id=>($(id).value||'').trim();
const req=['product','old_size','old_unit','new_size','new_unit'];
const build=()=>{
  const product=val('product'),brand=val('brand'),cat=val('category'),country=val('country');
  const when=val('when'),os=val('old_size'),ou=val('old_unit'),ns=val('new_size'),nu=val('new_unit');
  const op=val('old_price'),np=val('new_price'),cur=val('currency'),store=val('store');
  const src=val('source'),notes=val('notes'),email=val('email');
  const title=`Sighting: ${product} (${os} ${ou} → ${ns} ${nu})`;
  const lines=[
    '## Sighting report',
    '',
    `| Field | Value |`,
    `| --- | --- |`,
    `| Product | ${product} |`,
    `| Brand | ${brand||'—'} |`,
    `| Category | ${cat||'—'} |`,
    `| Country | ${country||'—'} |`,
    `| When (approx) | ${when||'—'} |`,
    `| Old size | ${os} ${ou} |`,
    `| New size | ${ns} ${nu} |`,
    `| Old price | ${op?((cur?cur+' ':'')+op):'—'} |`,
    `| New price | ${np?((cur?cur+' ':'')+np):'—'} |`,
    `| Store / where seen | ${store||'—'} |`,
    `| Evidence URL | ${src||'—'} |`,
    `| Reporter email | ${email||'(not given)'} |`,
    '',
    '### Notes',
    notes||'_(none)_',
    '',
    '---',
    '_Submitted via [ShrinkRadar /submit/](https://shrinkradar.com/submit/). Verify before adding to the case library._'
  ];
  return {title,body:lines.join('\\n')};
};
const PQ=new URLSearchParams(location.search);['product','brand','new_size','new_unit','notes','country'].forEach(k=>{const v=PQ.get(k);if(v&&$(k)){if($(k).tagName==='SELECT'&&![...$(k).options].some(o=>o.value===v))return;$(k).value=v}});
f.addEventListener('submit',e=>{
  e.preventDefault();
  for(const id of req){if(!val(id)){st.textContent='Please fill in the required fields (product, old size, new size).';$(id).focus();return}}
  const os=parseFloat(val('old_size').replace(',','.')),ns=parseFloat(val('new_size').replace(',','.'));
  if(!(os>0&&ns>0)){st.textContent='Sizes must be positive numbers.';return}
  const {title,body}=build();
  const url='https://github.com/Mangomangoman1/shrinkflation/issues/new?title='+encodeURIComponent(title)+'&body='+encodeURIComponent(body);
  const w=window.open(url,'_blank','noopener');
  md.value=body; fb.hidden=false;
  st.textContent=w?'Opened a prefilled GitHub issue in a new tab. If nothing opened, copy the markdown below and paste it into a new issue.':'Pop-up blocked. Copy the markdown below and paste it into a new GitHub issue.';
});
$('copy').addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(md.value);$('copy').textContent='Copied';setTimeout(()=>$('copy').textContent='Copy markdown',1500)}
  catch(_){md.select();document.execCommand('copy');$('copy').textContent='Copied'}
});
})();"""
BARCODE_JS="""(()=>{const $=i=>document.getElementById(i),inp=$('code'),out=$('bres'),st=$('bst'),P=new URLSearchParams(location.search);let IDX=null;
const el=(t,a={},...k)=>{const e=document.createElement(t);for(const x in a){if(x==='class')e.className=a[x];else if(x==='text')e.textContent=a[x];else e.setAttribute(x,a[x])}k.forEach(c=>c!=null&&e.append(c));return e};
const row=(l,v,cls)=>el('div',{class:'row'},el('span',{text:l}),el('b',{text:v,class:cls||''}));
const slug=s=>s.toLowerCase().replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');
const okGTIN=c=>{if(!/^\\d{8}$|^\\d{12,14}$/.test(c))return false;let s=0;const d=c.split('').reverse().map(Number);for(let i=1;i<d.length;i++)s+=d[i]*(i%2?3:1);return (10-s%10)%10===d[0]};
const norm=v=>String(v||'').replace(/\\D/g,'');
const getJ=async u=>{try{const r=await fetch(u);return r.ok?await r.json():null}catch(_){return null}};
async function off(c){for(const h of ['world.openfoodfacts.org','world.openproductsfacts.org','world.openbeautyfacts.org']){const j=await getJ(`https://${h}/api/v2/product/${c}.json?fields=product_name,brands,quantity,product_quantity,product_quantity_unit`);if(j&&j.status===1&&j.product)return [j.product,h]}return [null,null]}
async function look(raw){let c=norm(raw);out.innerHTML='';if(c.length<8){st.textContent='Enter the 8 to 14 digits under the barcode.';return}
const q=c.length===12?'0'+c:c;history.replaceState(null,'','?code='+c);st.textContent='Looking up '+c+'…';
if(!IDX)IDX=await getJ('/barcodes.json')||{p:{},b:{}};const key=c.replace(/^0+/,''),mine=IDX.p[key];
const [[p,host],pr]=await Promise.all([off(q),getJ(`https://prices.openfoodfacts.org/api/v1/prices?product_code=${q}&order_by=-date&size=6`)]);
st.textContent=okGTIN(c)?'':'Heads up: '+c+' fails the barcode check digit, so it may be mistyped.';
const name=(mine&&mine[0])||(p&&p.product_name)||'',brands=(p&&p.brands)||'',qty=((p&&p.quantity)||(mine&&mine[2])||'').replace(/\\s+[e℮]$/,'');
const box=el('section',{class:'label','aria-label':'Barcode result'},el('div',{class:'hd',text:'Size Facts'}));
box.append(el('div',{class:'row bar'},el('span',{class:'upc',text:'Barcode '+c})));
if(name)box.append(el('div',{class:'big',style:'font-size:1.4rem',text:(brands&&!mine&&!name.toLowerCase().includes(brands.split(',')[0].toLowerCase())?brands.split(',')[0].trim()+' ':'')+name}));
box.append(row('Net quantity on the pack',qty||'not on file'));
if(mine){box.append(row('Did it shrink?',mine[3],mine[3].startsWith('Yes')?'yes':'no'));box.append(el('p',{text:mine[4]}));box.append(el('p',{},el('a',{href:mine[1]},el('b',{text:'Full size and price history →'}))))}
else box.append(el('p',{text:name?'ShrinkRadar does not check this product daily yet, so we have no size history for it. The size above is what the open database lists today.':'This barcode is not in Open Food Facts, Open Products Facts or Open Beauty Facts, and we do not track it.'}));
const items=(pr&&pr.items)||[];
if(items.length){box.append(el('div',{class:'row bar'},el('span',{class:'ml',text:'Recent shelf prices (Open Prices)'})));
items.forEach(i=>{const loc=i.location?[i.location.osm_name,i.location.osm_address_city,i.location.osm_address_country_code].filter(Boolean).join(', '):'';box.append(row(i.date+(loc?' · '+loc:''),(i.price!=null?Number(i.price).toFixed(2):'?')+' '+(i.currency||'')))});
box.append(el('p',{class:'m',text:'Open Prices records the price, not the pack size, so a jump may also be a different pack.'}))}
const bl=brands.split(',').map(b=>b.trim()).filter(Boolean),hit=bl.map(b=>[b,IDX.b[slug(b)]]).find(x=>x[1]);
if(hit)box.append(el('p',{},el('a',{href:'/brands/'+slug(hit[0])+'.html'},el('b',{text:`${hit[1][0]}: ${hit[1][1]} documented shrinkflation case${hit[1][1]>1?'s':''} →`}))));
out.append(box);
const acts=el('p',{class:'m'});const sz=p&&p.product_quantity?Math.round(p.product_quantity*100)/100:'',un=p&&p.product_quantity_unit||'';
acts.append(el('a',{href:'/calculator/?'+new URLSearchParams(sz?{a:sz,u:un}:{})},'Compare it with the old size in the calculator'),' · ',
el('a',{href:'/submit/?'+new URLSearchParams({product:name||('Barcode '+c),brand:bl[0]||'',new_size:sz,new_unit:un,notes:'Barcode '+c})},'Seen it shrink? Submit a sighting'));
if(!mine&&name)acts.append(' · ',el('a',{href:'https://github.com/Mangomangoman1/shrinkflation/issues/new?'+new URLSearchParams({title:`Track product: ${name} (${c})`,body:`Please add barcode ${c} (${name}${brands?', '+brands:''}) to the daily size checks.\\n\\n_Requested from https://shrinkradar.com/barcode/?code=${c}_`}),rel:'noopener',target:'_blank'},'Ask us to track it'));
if(host)acts.append(' · ',el('a',{href:`https://${host}/product/${q}`,rel:'nofollow noopener',target:'_blank'},'Open database entry'));
out.append(acts)}
$('bform').addEventListener('submit',e=>{e.preventDefault();look(inp.value)});
document.querySelectorAll('[data-code]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();inp.value=a.dataset.code;look(a.dataset.code)}));
if('BarcodeDetector' in window&&navigator.mediaDevices){const sb=$('scan'),v=$('cam');sb.hidden=false;let stream=null;
const stop=()=>{if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}v.hidden=true;sb.textContent='Scan with camera'};
sb.addEventListener('click',async()=>{if(stream){stop();return}try{const det=new BarcodeDetector({formats:['ean_13','ean_8','upc_a','upc_e']});
stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'}});v.srcObject=stream;v.hidden=false;await v.play();sb.textContent='Stop camera';st.textContent='Point the camera at the barcode.';
const tick=async()=>{if(!stream)return;try{const r=await det.detect(v);if(r.length){const c=r[0].rawValue;stop();inp.value=c;look(c);return}}catch(_){}requestAnimationFrame(tick)};tick()}
catch(_){stop();st.textContent='Camera not available. Type the digits instead.'}})}
const c0=P.get('code');if(c0){inp.value=c0;look(c0)}})();"""
GUIDE_PUB="2026-10-15"
def guides(cases,prods,bg,cg,med,yl=()):
    """Evergreen guides under /guides/. Returns [(url,title,desc)]."""
    n=len(cases); np_=len(prods); w=max(cases,key=lambda c:c["pct"]); pr=[c for c in cases if c["real"] is not None]; up=sum(1 for c in pr if c["real"]>0.05)
    mcut=med([c["pct"] for c in cases]); nct=len({c["country"] for c in cases})
    art=lambda t,d,u: {"@context":"https://schema.org","@type":"Article","headline":t,"description":d,"url":SITE+u,"mainEntityOfPage":SITE+u,"datePublished":GUIDE_PUB,"dateModified":TODAY,"image":SITE+OGIMG,
                       "author":{"@type":"Organization","name":NAME,"url":SITE+"/"},"publisher":{"@type":"Organization","name":NAME,"url":SITE+"/","logo":{"@type":"ImageObject","url":SITE+"/favicon.svg"}}}
    faq=lambda qa: {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub("<[^>]+>","",a)}} for q,a in qa]}
    faq_h=lambda qa: '<h2 id="faq">FAQ</h2>'+"".join(f'<h3>{E(q)}</h3><p>{a}</p>' for q,a in qa)
    meta=f'<p class="m">By {NAME} · Updated {TODAY} · Figures from our live case library</p>'
    out=[]
    # what is
    u="/guides/what-is-shrinkflation.html"; t="What is shrinkflation? Definition and real examples"
    d=f"Shrinkflation is when a pack gets smaller but the price stays the same or rises. Plain definition, how it differs from inflation and skimpflation, and {n} sourced examples."
    qa=[("What is shrinkflation?","Shrinkflation is when a product’s package gets smaller (less weight, volume or count) while its price stays the same or goes up. You pay the same or more for less, so the price per unit rises."),
        ("Is shrinkflation illegal?","Usually not, as long as the label states the correct net quantity. Some countries go further: France has required supermarkets to flag shrunken packs since July 2024, and consumer agencies in Germany, the UK and Australia publish lists of cases."),
        ("How much does shrinkflation raise prices?",f"Cutting a pack by a fraction x at the same price raises the unit price by x ÷ (1 − x). The median cut across our {n} documented cases is {mcut:.1f}%, which is a {mcut/(100-mcut)*100:.1f}% hidden rise per unit if the price did not change."),
        ("What is the difference between shrinkflation and skimpflation?","Shrinkflation gives you less of the same product. Skimpflation gives you the same amount of a cheaper product, such as a recipe with cheaper ingredients, or a thinner service. Both raise the real price without a higher sticker price.")]
    body=(f'<p class="crumbs"><a href="/guides/">Guides</a> / What is shrinkflation</p><article class="prose"><h1>What is shrinkflation?</h1>{meta}'
      f'<section class="label" aria-label="Definition"><div class="hd">Shrink Facts</div><div class="row bar"><span>Pack size</span><b class="yes">Smaller</b></div><div class="row"><span>Shelf price</span><b>Same or higher</b></div><div class="row bar"><span>Price per unit</span><b class="yes">Up</b></div>'
      f'<p><b>Shrinkflation</b> is a price rise hidden in the package: less product for the same money, or more money.</p></section>'
      f'<p>A box of cereal goes from 18 oz to 15.4 oz. The shelf price stays at $4.99. Nothing on the front of the box says it changed, and the box itself may be the same height. But you now pay 16.9% more per ounce. That is shrinkflation.</p>'
      f'<p>The one number that tells the truth is the <b>net quantity</b> on the label (“Net Wt.”, “Inhalt”, sheet or pod count). If it went down and the price did not, the price per unit went up.</p>'
      f'<h2>Shrinkflation, inflation and skimpflation</h2><ul><li><b>Inflation</b>: the sticker price goes up. You see it.</li><li><b>Shrinkflation</b>: the sticker price stays, the pack gets smaller. You have to read the label to see it.</li>'
      f'<li><b>Skimpflation</b>: price and size stay, quality drops (cheaper ingredients, fewer features). It is the hardest to measure, and we do not track it.</li></ul>'
      f'<p>Official inflation figures generally do count shrinkflation, because statistics agencies measure price per unit. A single shopper buying the same box every week usually does not notice it.</p>'
      f'<h2>How common is it?</h2><p>Our library holds <a href="/cases/">{n} documented cases</a> from {nct} countries. The median cut is {mcut:.1f}%. The largest is {E(w["product"])}: {fmt(w["before"],w["unit"])} → {fmt(w["after"],w["unit"])} (<a href="/cases/{w["slug"]}.html">−{w["pct"]:.1f}%</a>). '
      f'Where the source also recorded the shelf price before and after ({len(pr)} cases), {up} got more expensive per unit. The <a href="/worst/">worst offenders</a> page ranks them.</p>'
      f'<h2>How ShrinkRadar documents it</h2><ul><li><b>Daily checks.</b> We record the net quantity and the most recent price of <a href="/products/">{np_} everyday products</a> every day from Open Food Facts, Open Products Facts and Open Prices. Any drop is logged as a finding on the homepage.</li>'
      f'<li><b>Sourced cases.</b> Historical before/after cuts come from consumer agencies (e.g. Verbraucherzentrale Hamburg, Consumentenbond, Which?, CHOICE), the Mouse Print* archive, and news investigations. Each case links the source and quotes what it says. If we cannot verify a case, we leave it out.</li>'
      f'<li><b>No estimates.</b> Missing data is shown as missing.</li></ul>'
      f'<p>Browse by <a href="/brands/">brand</a> or <a href="/categories/">category</a>, or run your own numbers in the <a href="/calculator/">shrinkflation calculator</a>. Next: <a href="/guides/how-to-spot-shrinkflation.html">how to spot shrinkflation in the store</a>.</p>'
      f'{faq_h(qa)}</article>')
    page(u[1:],f"{t} | {NAME}",d,body,[crumbs(("Guides","/guides/"),("What is shrinkflation",None)),art(t,d,u),faq(qa)]); out.append((u,"What is shrinkflation?",d))
    # how to spot
    u="/guides/how-to-spot-shrinkflation.html"; t="How to spot shrinkflation: a 5-step grocery checklist"
    d="Practical checklist to catch shrinkflation: read the net weight, compare unit prices on shelf tags, check pack sizes, use the calculator, and search known cases."
    qa=[("How can I tell if a product shrank?","Compare the net quantity on the label (weight, volume or count) with an older pack, a photo, or a documented case. The package itself is not reliable: boxes often keep their height and get thinner, or gain a deeper dent in the bottom."),
        ("What is unit price and where do I find it?","Unit price is the price per ounce, 100 g, sheet or load. In most US, UK, EU and Australian supermarkets it is printed in small type on the shelf tag. It is the only fair way to compare packs of different size."),
        ("Is the bigger pack always cheaper per unit?","No. Larger or ‘family’ packs are sometimes more expensive per unit than the regular size, especially after a shrink. Check the unit price on the tag every time."),
        ("How do I report shrinkflation?","Keep the old and new packs or photos showing the net quantity and the price. Consumer agencies such as Verbraucherzentrale (Germany), Which? (UK) and CHOICE (Australia) collect reports; in the US, Mouse Print* covers cases.")]
    steps=[("Read the net quantity, not the box",'Look for “Net Wt.”, “Net contents”, the sheet, roll, pod or load count. Ignore the box size, the “family size” badge and the picture. Packs shrink by getting thinner, adding a deeper punt in the bottom of a jar, or more air in a bag.'),
           ("Compare the unit price on the shelf tag","The small print on the shelf tag gives the price per oz, 100 g, sheet or load. Note it for the things you buy every week. If it jumps while the shelf price stays the same, the pack shrank."),
           ("Check the other sizes of the same brand","Line up the sizes side by side. A shrink often shows when the “regular” pack is now close to the smaller size, or when the multipack costs more per unit than singles."),
           ("Do the math",f'Put the old and new size and price into the <a href="/calculator/">shrinkflation calculator</a>. It gives the real change per unit and the fair price for the new pack. A 10% smaller pack at the same price is an 11.1% price rise.'),
           ("Look it up",f'<a href="/search.html">Search ShrinkRadar</a> for the brand or product. We track {np_} products daily and have {n} <a href="/cases/">documented cases</a>, each with a source. The <a href="/worst/">worst offenders</a> list shows the brands caught most often.')]
    body=(f'<p class="crumbs"><a href="/guides/">Guides</a> / How to spot shrinkflation</p><article class="prose"><h1>How to spot shrinkflation</h1>{meta}'
      f'<p>Shrinkflation is designed to be missed: the price stays, the pack looks the same, only the small number on the label changes. Five habits catch almost all of it.</p>'
      '<section class="label" aria-label="Checklist"><div class="hd">Shrink Check</div>'+"".join(f'<div class="row{" bar" if i==len(steps) else ""}"><span>{i}. {E(h)}</span><b>✓</b></div>' for i,(h,_) in enumerate(steps,1))+'<p>Net quantity and unit price are the two numbers that matter.</p></section>'
      +"".join(f'<h2>{i}. {E(h)}</h2><p>{b}</p>' for i,(h,b) in enumerate(steps,1))
      +f'<h2>Where it happens most</h2><p>Categories with the most documented cases in our library: '+", ".join(f'<a href="/categories/{slug(k)}.html">{E(k)}</a> ({len(v)})' for k,v in sorted(cg.items(),key=lambda kv:-len(kv[1]))[:6])+'.</p>'
      f'<p>Background: <a href="/guides/what-is-shrinkflation.html">what shrinkflation is</a>.</p>{faq_h(qa)}</article>')
    page(u[1:],f"{t} | {NAME}",d,body,[crumbs(("Guides","/guides/"),("How to spot shrinkflation",None)),art(t,d,u),faq(qa),
        {"@context":"https://schema.org","@type":"HowTo","name":"How to spot shrinkflation","step":[{"@type":"HowToStep","position":i,"name":h,"text":re.sub("<[^>]+>","",b)} for i,(h,b) in enumerate(steps,1)]}]); out.append((u,"How to spot shrinkflation",d))
    # hub
    tb=sorted([(k,v) for k,v in bg.items() if len(v)>=5],key=lambda kv:(-len(kv[1]),kv[1][0]["brand"]))
    body=(f'<h1>Shrinkflation guides</h1><p class="prose">Plain explanations of shrinkflation, built on our library of {n} documented cases and daily checks of {np_} products.</p><ul class="grid">'
      +"".join(f'<li class="card"><span class="ml">Guide</span><h3><a href="{u_}">{E(t_)}</a></h3><span class="m">{E(d_)}</span></li>' for u_,t_,d_ in out)
      +'<li class="card"><span class="ml">Tool</span><h3><a href="/calculator/">Shrinkflation calculator</a></h3><span class="m">Old and new size and price in, real price change per unit out.</span></li>'
      +'<li class="card"><span class="ml">Data</span><h3><a href="/worst/">Worst offenders</a></h3><span class="m">Biggest cuts, hidden per-unit price hikes and repeat brands.</span></li>'
      +"".join(f'<li class="card"><span class="ml">List</span><h3><a href="{u_}">{E(t_)}</a></h3><span class="m">{E(d_)}</span></li>' for u_,t_,d_ in yl)
      +f'<li class="card"><span class="ml">Open data</span><h3><a href="/data/">Download the case library</a></h3><span class="m">All {n} cases as CSV or JSON, CC BY 4.0, with sources.</span></li></ul>'
      +'<h2>Brands caught most often</h2><ul class="chips">'+"".join(f'<li><a href="/brands/{k}.html">{E(v[0]["brand"])} <span class="m">{len(v)}</span></a></li>' for k,v in tb)+'</ul>'
      +'<h2>Categories by documented cases</h2><ul class="chips">'+"".join(f'<li><a href="/categories/{slug(k)}.html">{E(k)} <span class="m">{len(v)}</span></a></li>' for k,v in sorted(cg.items(),key=lambda kv:-len(kv[1])))+'</ul>')
    page("guides/index.html",f"Shrinkflation guides: what it is and how to spot it | {NAME}",f"Shrinkflation guides from {NAME}: what shrinkflation is, how to spot it in the store, and the brands and categories with the most of the {n} documented cases.",body,
         [crumbs(("Guides",None)),{"@context":"https://schema.org","@type":"ItemList","name":"Shrinkflation guides","itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+u_,"name":t_} for i,(u_,t_,_) in enumerate(list(out)+list(yl))]}])
    return out
DATA_FIELDS=[("id","Stable case id; also the case page slug"),("url","Case page on shrinkradar.com (quotes the source)"),("product","Product name as reported"),("brand","Brand or store brand"),
  ("category","ShrinkRadar category"),("country","ISO-style country code (UK for the United Kingdom, EU for EU-wide)"),("country_name","Country name"),("when","When the change happened or was reported, as given by the source"),
  ("year","Four-digit year parsed from 'when' (n/d if none)"),("size_before","Net quantity before"),("size_after","Net quantity after"),("unit","Unit of both sizes (g, ml, oz, sheets, pieces…)"),
  ("size_cut_pct","Size cut in % = (1 − after ÷ before) × 100"),("unit_price_rise_same_price_pct","Hidden unit-price rise if the shelf price stayed the same = (before ÷ after − 1) × 100"),
  ("old_price","Shelf price before, as recorded by the source (with currency symbol), if any"),("new_price","Shelf price after, as recorded by the source, if any"),
  ("currency","Currency symbol of the two prices (€, £, $), if both parse"),("old_price_value","Old price as a number"),("new_price_value","New price as a number"),
  ("real_unit_price_change_pct","Change in price per unit combining size and shelf price, if both prices are known and in the same currency"),
  ("retailer","Store where the source bought or saw the pack, if recorded"),("maker","Manufacturer, if recorded"),("date_reported","Date the source published or logged the case, as written by the source"),
  ("source","Name of the source we fetched"),("source_url","Link to that source"),("also_reported","Other sources reporting the same change (space-separated URLs)"),
  ("archive_url","Archived copy of the source, if any"),("evidence_type","Kind of evidence behind the source"),("confidence","high or medium")]
DATA_PUB="2026-10-16"
def dataset_ld(cases,url):
    yrs=sorted(c["year"] for c in cases if c["year"]!="n/d")
    return {"@context":"https://schema.org","@type":"Dataset","name":"ShrinkRadar documented shrinkflation cases",
      "description":f"{len(cases)} documented shrinkflation cases comparing before-and-after package sizes, with dates, countries, prices where recorded, and links to the consumer-agency, consumer-advocate or news sources that reported them. Free to reuse under CC BY 4.0.",
      "url":url,"license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":True,"creator":{"@type":"Organization","name":NAME,"url":SITE+"/"},
      "keywords":["shrinkflation","package size","unit price","consumer prices","groceries"],"temporalCoverage":f"{yrs[0]}/{yrs[-1]}","dateModified":TODAY,
      "spatialCoverage":sorted({COUNTRY.get(c["country"],c["country"]) for c in cases}),
      "variableMeasured":["size_before","size_after","size_cut_pct","old_price","new_price","real_unit_price_change_pct"],
      "distribution":[{"@type":"DataDownload","encodingFormat":"text/csv","contentUrl":SITE+"/data/cases.csv"},{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":SITE+"/data/cases.json"}]}
def open_data(cases):
    """/data/: the case library as CSV + JSON under CC BY 4.0, plus a field/licence/citation page."""
    import csv,io
    rows=[]; num=lambda x: int(x) if float(x).is_integer() else x
    for c in sorted(cases,key=lambda c:c["slug"]):
        a,b=money(c.get("old_price")),money(c.get("new_price")); okp=bool(a and b and a[1]==b[1])
        rows.append({"id":c["slug"],"url":f'{SITE}/cases/{c["slug"]}.html',"product":c["product"],"brand":c["brand"],"category":c["category"],"country":c["country"],
          "country_name":COUNTRY.get(c["country"],c["country"]),"when":c["when"],"year":c["year"],"size_before":num(c["before"]),"size_after":num(c["after"]),"unit":c["unit"],
          "size_cut_pct":round(c["pct"],2),"unit_price_rise_same_price_pct":round((c["before"]/c["after"]-1)*100,2),
          "old_price":c.get("old_price") or "","new_price":c.get("new_price") or "","currency":a[1] if okp else "","old_price_value":a[0] if okp else "","new_price_value":b[0] if okp else "","real_unit_price_change_pct":"" if c["real"] is None else round(c["real"],2),
          "retailer":c.get("retailer") or "","maker":c.get("maker") or "","date_reported":c.get("date_reported") or "","source":c["source"],"source_url":c["source_url"],
          "also_reported":" ".join(a["url"] for a in c.get("also_reported") or []),"archive_url":c.get("archive_url") or "","evidence_type":c.get("evidence_type") or "","confidence":c.get("confidence") or ""})
    d=OUT/"data"; d.mkdir(exist_ok=True)
    buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=[k for k,_ in DATA_FIELDS],lineterminator="\n"); w.writeheader(); w.writerows(rows)
    (d/"cases.csv").write_text(buf.getvalue(),encoding="utf-8")
    meta={"name":"ShrinkRadar documented shrinkflation cases","url":SITE+"/data/","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
          "attribution":"ShrinkRadar (shrinkradar.com)","updated":TODAY,"count":len(rows),"fields":dict(DATA_FIELDS)}
    (d/"cases.json").write_text(json.dumps({"meta":meta,"cases":rows},ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    kb=lambda f:f'{(d/f).stat().st_size/1024:.0f} KB'
    nc=len({c["country"] for c in cases}); npr=sum(1 for c in cases if c["real"] is not None)
    cite=f'ShrinkRadar ({TODAY[:4]}). Documented shrinkflation cases [Data set]. {SITE}/data/. CC BY 4.0. Retrieved {TODAY}.'
    body=(f'<p class="crumbs"><a href="/cases/">Known cases</a> / Open data</p><h1>Open data: shrinkflation cases</h1>'
      f'<p class="prose">Our whole case library as one file: <b>{len(rows)}</b> documented before/after package-size cuts from {nc} countries, {npr} with shelf prices before and after. Free to use, share and adapt under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Please credit ShrinkRadar and link this page.</p>'
      f'<section class="label" aria-label="Downloads"><div class="hd">Data Facts</div><div class="row bar"><span>Cases</span><b>{len(rows)}</b></div>'
      f'<div class="row"><span><a href="/data/cases.csv">cases.csv</a></span><b>{kb("cases.csv")}</b></div><div class="row"><span><a href="/data/cases.json">cases.json</a></span><b>{kb("cases.json")}</b></div>'
      f'<div class="row"><span>Fields</span><b>{len(DATA_FIELDS)}</b></div><div class="row"><span>Licence</span><b>CC BY 4.0</b></div><div class="row bar"><span>Updated</span><b>{TODAY}</b></div>'
      f'<p>Stable URLs: <code>{SITE}/data/cases.csv</code> and <code>{SITE}/data/cases.json</code>. Rebuilt whenever the library changes; case ids do not change.</p></section>'
      '<h2>Fields</h2><div class="tw"><table><thead><tr><th>Field</th><th>Meaning</th></tr></thead><tbody>'+"".join(f'<tr><td><code>{k}</code></td><td>{E(v)}</td></tr>' for k,v in DATA_FIELDS)+'</tbody></table></div>'
      '<div class="prose"><h2>What is in it, and what is not</h2><ul><li>Every row is a size cut that a consumer agency, consumer advocate or news investigation reported, and that we checked against the fetched source. Each row links that source. Cases we could not verify are not included.</li>'
      '<li>Sizes and prices are as the source gave them. We do not estimate or fill gaps; empty fields mean the source did not say.</li>'
      '<li>Quotes from sources are not in the files (they belong to their publishers); each case page shows the quote.</li>'
      '<li>Coverage follows the sources: Germany (Verbraucherzentrale Hamburg) and the Netherlands (Consumentenbond) are strongly represented, the US mostly through Mouse Print*. It is a record of reported cases, not a random sample, so do not read country or brand counts as rates.</li>'
      '<li>Daily product snapshots (sizes and prices of the products we track) derive from Open Food Facts, Open Products Facts and Open Prices under the ODbL and are not part of this download.</li></ul>'
      f'<h2>How to cite</h2><blockquote class="q">{E(cite)}</blockquote><p>When you quote a single case, link its case page or the original source in the <code>source_url</code> column.</p>'
      '<h2>Corrections</h2><p>Found an error or a missing case? <a href="/submit/">Submit a sighting</a> or open an issue on <a href="https://github.com/Mangomangoman1/shrinkflation/issues">GitHub</a>.</p>'
      '<p>Browse the same data as a table in <a href="/cases/">known cases</a>, ranked in <a href="/worst/">worst offenders</a>, or by year: '+", ".join(f'<a href="/shrinkflation-{y}/">{y}</a>' for y in LAND_YEARS)+'.</p></div>')
    page("data/index.html",[f'Shrinkflation open data: {len(rows)} cases (CSV, JSON) | {NAME}',f'Shrinkflation open data: {len(rows)} cases (CSV, JSON)'],
         f'Download {len(rows)} documented shrinkflation cases as CSV or JSON: before/after sizes, prices, dates, countries and sources. Free under CC BY 4.0.',body,
         [crumbs(("Known cases","/cases/"),("Open data",None)),dataset_ld(cases,SITE+"/data/")])
LAND_YEARS=[]
LAND_PUB="2026-10-16"
def year_landings(cases,ccard,med):
    """/shrinkflation-{year}/ list pages for every year with >=40 sourced cases. Returns [(url,title,desc)]."""
    g={}
    for c in cases: g.setdefault(c["year"],[]).append(c)
    out=[]; cur=TODAY[:4]
    for y in LAND_YEARS:
        v=sorted(g[y],key=lambda c:(-c["pct"],c["product"])); n=len(v); u=f"/shrinkflation-{y}/"
        cty={}; cat={}; br={}
        for c in v: cty.setdefault(c["country"],[]).append(c); cat.setdefault(c["category"],[]).append(c); br.setdefault(c["bslug"],[]).append(c)
        w=v[0]; mc=med([c["pct"] for c in v]); pr=[c for c in v if c["real"] is not None]; up=sorted([c for c in pr if c["real"]>0.05],key=lambda c:-c["real"])
        cty_s=sorted(cty.items(),key=lambda kv:-len(kv[1])); rep=sorted([(k,x) for k,x in br.items() if len(x)>=2],key=lambda kv:(-len(kv[1]),kv[1][0]["brand"]))
        sd={}
        for c in v: d_=re.sub(r"^https?://(www\.)?([^/]+).*",r"\2",c["source_url"]); sd[d_]=sd.get(d_,0)+1
        srcs=[k for k,_ in sorted(sd.items(),key=lambda kv:(-kv[1],kv[0]))]
        t=f"Shrinkflation {y}: {n} documented examples"; dsc=f"List of {n} shrinkflation examples from {y}: products that got smaller, with before/after sizes and sources. Biggest: {w['product']} (−{w['pct']:.0f}%)."
        top5=", ".join(f'{c["product"]} ({fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])})' for c in v[:5])
        qa=[(f"What are examples of shrinkflation in {y}?",f"The biggest documented cuts in {y} were: {top5}. ShrinkRadar lists {n} sourced cases from {y}."),
            (f"Which countries had the most shrinkflation cases in {y}?","In our library: "+", ".join(f'{COUNTRY.get(k,k)} {len(x)}' for k,x in cty_s)+". These counts follow where consumer agencies and reporters published lists, so they are not rates."),
            (f"How much smaller did products get in {y}?",f"The median documented cut in {y} was {mc:.1f}%, which is a {mc/(100-mc)*100:.1f}% hidden price rise per unit if the shelf price stayed the same. The biggest was {w['product']}, {fmt(w['before'],w['unit'])} → {fmt(w['after'],w['unit'])} (−{w['pct']:.1f}%).")]
        if y==cur: qa.insert(0,(f"Is shrinkflation still happening in {y}?",f"Yes. ShrinkRadar has {n} documented shrinkflation cases dated {y} so far, from {len(cty)} countries, and the list grows as consumer agencies and reporters publish new ones."))
        if pr: qa.append((f"Did prices per unit go up in {y}?",f"Where the source also recorded the shelf price before and after ({len(pr)} of the {n} cases from {y}), {len(up)} got more expensive per unit."))
        row=lambda c,extra="": (f'<tr><td><a href="/cases/{c["slug"]}.html">{E(c["product"])}</a><br><span class="m">{E(c["brand"])} · {FLAG.get(c["country"],"")} {c["country"]}</span></td>'
                                 f'<td class="n">{fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])}</td><td class="n yes"><b>−{c["pct"]:.1f}%</b></td>{extra}</tr>')
        dom=lambda c: re.sub(r"^https?://(www\.)?([^/]+).*",r"\2",c["source_url"])
        body=(f'<p class="crumbs"><a href="/cases/">Known cases</a> / <a href="/years/">Years</a> / {y}</p><h1>Shrinkflation {y}: {n} documented examples</h1>'
          f'<p class="m">By {NAME} · Updated {TODAY} · Every case links its source</p>'
          f'<section class="label" aria-label="Size facts"><div class="hd">Size Facts {y}</div><div class="row bar"><span>Did packs shrink in {y}?</span><b class="yes">Yes</b></div>'
          f'<div class="row"><span>Documented cases</span><b>{n}</b></div><div class="row"><span>Countries</span><b>{" ".join(FLAG.get(k,k) for k,_ in cty_s)}</b></div>'
          f'<div class="row"><span>Brands</span><b>{len(br)}</b></div><div class="row"><span>Median cut</span><b>−{mc:.1f}%</b></div>'
          f'<div class="row bar"><span>Biggest cut</span><b class="yes">−{w["pct"]:.1f}%</b></div>'
          +(f'<div class="row bar"><span>Pricier per unit (of {len(pr)} priced)</span><b class="yes">{len(up)}</b></div>' if pr else "")
          +f'<p>Biggest: <a href="/cases/{w["slug"]}.html">{E(w["product"])}</a>, {fmt(w["before"],w["unit"])} → {fmt(w["after"],w["unit"])}.</p></section>'
          f'<p class="prose">These are the products that got smaller in {y} according to the consumer agencies, consumer advocates and reporters we track. Main sources: {E(", ".join(srcs[:8]))}{f" and {len(srcs)-8} more" if len(srcs)>8 else ""}. '
          f'We fetched each source and checked the before and after sizes. The year is when the source dates the change; some lists are published a few months after the pack changed.</p>'
          f'<h2>Biggest cuts in {y}</h2><div class="tw"><table><thead><tr><th>Product</th><th class="n">Size</th><th class="n">Cut</th></tr></thead><tbody>{"".join(row(c) for c in v[:15])}</tbody></table></div>'
          +(f'<h2>Biggest hidden price hikes in {y}</h2><p class="prose m">Real change in price per unit, from the shelf prices the source recorded before and after.</p><div class="tw"><table><thead><tr><th>Product</th><th class="n">Size</th><th class="n">Cut</th><th class="n">Price · per unit</th></tr></thead><tbody>'
            +"".join(row(c,f'<td class="n"><span class="m">{E(c["old_price"])} → {E(c["new_price"])}</span><br><b class="yes">+{c["real"]:.1f}%</b></td>') for c in up[:10])+'</tbody></table></div>' if len(up)>=3 else "")
          +f'<h2>By country</h2><ul class="chips">'+"".join(f'<li><a href="/cases/?country={k}&amp;year={y}">{FLAG.get(k,"")} {E(COUNTRY.get(k,k))} <span class="m">{len(x)}</span></a></li>' for k,x in cty_s)+'</ul>'
          +f'<h2>By category</h2><ul class="chips">'+"".join(f'<li><a href="/categories/{slug(k)}.html">{E(k)} <span class="m">{len(x)}</span></a></li>' for k,x in sorted(cat.items(),key=lambda kv:(-len(kv[1]),kv[0])))+'</ul>'
          +(f'<h2>Brands caught more than once in {y}</h2><ul class="chips">'+"".join(f'<li><a href="/brands/{k}.html">{E(x[0]["brand"])} <span class="m">{len(x)}</span></a></li>' for k,x in rep)+'</ul>' if rep else "")
          +f'<h2>All {n} shrinkflation cases from {y}</h2><div class="tw"><table><thead><tr><th>Product</th><th class="n">Size</th><th class="n">Cut</th><th class="n hide-s">Source</th></tr></thead><tbody>'
          +"".join(row(c,f'<td class="n hide-s"><a href="{E(c["source_url"])}" rel="nofollow">{E(dom(c))}</a></td>') for c in v)+'</tbody></table></div>'
          +f'<p class="m">Download every case as <a href="/data/">CSV or JSON</a> (CC BY 4.0). Check any pack with the <a href="/calculator/">shrinkflation calculator</a>. Spotted one we missed? <a href="/submit/">Submit a sighting</a>.</p>'
          +'<p class="chips">'+"".join(f'<a href="/shrinkflation-{o}/">Shrinkflation {o}</a>' for o in LAND_YEARS if o!=y)+'<a href="/years/">Older years</a></p>'
          +'<div class="prose"><h2 id="faq">FAQ</h2>'+"".join(f'<h3>{E(q)}</h3><p>{E(a)}</p>' for q,a in qa)+'</div>')
        ld=[crumbs(("Known cases","/cases/"),("Years","/years/"),(f"Shrinkflation {y}",None)),
            {"@context":"https://schema.org","@type":"Article","headline":t,"description":dsc,"url":SITE+u,"mainEntityOfPage":SITE+u,"datePublished":LAND_PUB,"dateModified":TODAY,"image":SITE+OGIMG,
             "author":{"@type":"Organization","name":NAME,"url":SITE+"/"},"publisher":{"@type":"Organization","name":NAME,"url":SITE+"/","logo":{"@type":"ImageObject","url":SITE+"/favicon.svg"}}},
            {"@context":"https://schema.org","@type":"ItemList","name":f"Shrinkflation examples {y}","numberOfItems":n,"itemListOrder":"https://schema.org/ItemListOrderDescending",
             "itemListElement":[{"@type":"ListItem","position":i+1,"url":f'{SITE}/cases/{c["slug"]}.html',"name":c["product"]} for i,c in enumerate(v)]},
            {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa]}]
        page(f"shrinkflation-{y}/index.html",[f"{t} | {NAME}",t,f"Shrinkflation {y}: {n} examples"],dsc,body,ld); out.append((u,f"Shrinkflation {y}: list of {n} examples",dsc))
    return out
def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); (OUT/"style.css").write_text(CSS)
    prods=json.load(open(R/"products.json")); snaps=json.load(open(R/"data/snapshots.json"))
    cases=json.load(open(R/"data/cases.json")) if (R/"data/cases.json").exists() else []
    by={}
    for s in sorted(snaps,key=lambda s:s["date"]): by.setdefault(s["code"],[]).append(s)
    for p in prods:
        p["title"]=(p["name"] if p["brand"].lower() in p["name"].lower() else f'{p["brand"]} {p["name"]}').strip()
        p["slug"]=slug(p["title"])[:60]+"-"+p["code"][-6:]; p["bslug"]=bslug(p["brand"] or "unbranded"); p["cslug"]=slug(p["category"])
    for c in cases:
        fix_case(c)
        c["when"]=str(c.get("when") or "n/d"); c["country"]=c.get("country") or "US"; c["year"]=(re.findall(r"(?:19|20)\d\d",c["when"]) or ["n/d"])[-1]
        base=slug(c["product"]+"-"+c["country"]+"-"+c["when"])[:80]; c["slug"]=base; k=2
        while c["slug"] in SLUGS: c["slug"]=f"{base}-{k}"; k+=1
        SLUGS.add(c["slug"]); c["bslug"]=bslug(c["brand"]); c["cslug"]=slug(c["category"]); c["pct"]=(1-c["after"]/c["before"])*100; c["real"]=real_change(c)
    yc={}
    for c in cases: yc[c["year"]]=yc.get(c["year"],0)+1
    LAND_YEARS[:]=sorted([y for y,n in yc.items() if y!="n/d" and n>=40],reverse=True)
    if LAND_YEARS: NAV.insert(3,(f'/shrinkflation-{LAND_YEARS[0]}/',f'{LAND_YEARS[0]} list'))
    NAV.insert(NAV.index(('/countries/','Countries'))+1,('/data/','Open data'))
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
    tcount={}
    for p in prods: tcount[p["title"]]=tcount.get(p["title"],0)+1
    for p in prods:
        l=next((s for s in reversed(by.get(p["code"],[])) if s.get("size")),None)
        p["ttl"]=p["title"] if tcount[p["title"]]==1 else (f'{p["title"]} {disp(l)}' if l else f'{p["title"]} (UPC {p["code"]})')
    tcount={}
    for p in prods: tcount[p["ttl"]]=tcount.get(p["ttl"],0)+1
    for p in prods:
        if tcount[p["ttl"]]>1: p["ttl"]=f'{p["ttl"]} (UPC {p["code"]})'
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
        # These pages report observations, not current offers or product reviews.
        # Keep product facts in the visible page without claiming Product eligibility.
        ld=[{"@context":"https://schema.org","@type":"WebPage",
             "name":f'Did {p["title"]} shrink? Size & price history',
             "url":f'{SITE}/products/{p["slug"]}.html',
             "identifier":p["code"],
             "description":f'Package size and observed price history for {p["title"]}. Brand: {p["brand"] or "Unbranded"}. Category: {p["category"]}.'},
            crumbs(("Products","/products/"),(p["category"],f'/categories/{p["cslug"]}.html'),(p["title"],None)),
            {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f'Did {p["title"]} shrink?',"acceptedAnswer":{"@type":"Answer","text":f"{verdict}. "+re.sub("<[^>]+>","",ans)}}]}]
        size_txt=f' Current size: {fmt(L["size"],L["unit"])}.' if L else ""
        CUR_ALERT[:]=[('product',p['code'],p['title']),('brand',p['bslug'],p['brand'] or 'Unbranded'),('category',p['cslug'],p['category'])]
        page(f'products/{p["slug"]}.html',[f'Did {p["ttl"]} shrink? Size & price history | {NAME}',f'Did {p["ttl"]} shrink? Size history | {NAME}',f'Did {p["ttl"]} shrink? | {NAME}',f'Did {p["ttl"]} shrink?'],
             f'Has {p["ttl"]} gotten smaller? Daily-tracked package size, price and unit price history.{size_txt}',
             f'<p class="crumbs"><a href="/categories/{p["cslug"]}.html">{E(p["category"])}</a> / <a href="/brands/{p["bslug"]}.html">{E(p["brand"] or "Unbranded")}</a> / <a class="upc" href="/barcode/?code={p["code"]}" title="Barcode lookup">UPC {p["code"]}</a></p>'
             f'<h1>Did {E(p["title"])} shrink?</h1>{label}'
             f'<h2>Size history</h2>{spark([s["size"] for s in ok])}<div class="tw"><table><thead><tr><th>Checked</th><th class="n">Net wt.</th><th class="n">Price</th><th class="n hide-s">Unit price</th></tr></thead><tbody>{tr}</tbody></table></div><p class="m">{src}</p>'
             +(f'<h2>Documented {E(p["brand"])} shrinks</h2><ul class="grid">'+"".join(ccard(c) for c in rel_cases)+'</ul>' if rel_cases else "")
             +(f'<h2>More {E(p["category"])}</h2><ul class="grid">'+"".join(pcard(q) for q in sib)+'</ul>' if sib else ""),ld)
    ccount={}
    for c in cases: k=(c["product"],c["before"],c["after"],c["unit"]); ccount[k]=ccount.get(k,0)+1
    for c in cases:
        prs=[p for p in prods if p["bslug"]==c["bslug"]][:6]
        ba=f'{fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])}'
        qual=f' ({c["country"]} {c["when"]})' if ccount[(c["product"],c["before"],c["after"],c["unit"])]>1 else ""
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
        CUR_ALERT[:]=[('brand',c['bslug'],c['brand']),('category',slug(c['category']),c['category'])]
        page(f'cases/{c["slug"]}.html',[f'Did {c["product"]} shrink? {ba}{qual} | {NAME}',f'Did {c["product"]} shrink? {ba}{qual}',f'{c["product"]}: {ba}{qual}'],desc,
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
         f'<h1>Known shrinkflation cases</h1><p class="prose">{len(cases)} documented before/after size cuts from consumer agencies, consumer advocates, news investigations and retailer-page archives. Every case links to the source we fetched. Spotted one we missed? <a href="/submit/">Submit a sighting</a>. Download them all as <a href="/data/">CSV or JSON</a> (CC BY 4.0).</p>'
         f'<p class="chips">'+"".join(f'<a href="/shrinkflation-{y}/">Shrinkflation {y}</a>' for y in LAND_YEARS)+'</p>'
         f'<p class="chips">'+"".join(f'<a href="/countries/{k.lower()}.html">{FLAG.get(k,"")} {E(COUNTRY.get(k,k))}</a>' for k in ctry)+'</p>'
         f'<div class="flt"><select aria-label="Country">{opt(ctry,"All countries")}</select><select aria-label="Year">{opt(yrs,"All years")}</select><select aria-label="Category">{opt(cats_c,"All categories")}</select><input type="search" placeholder="Filter by product or brand" aria-label="Filter"></div>'
         f'<p class="m"><b id="n">{len(cases)}</b> cases shown</p><div class="tw"><table id="ct"><thead><tr><th>Product</th><th class="n">Before</th><th class="n">After</th><th class="n">Cut</th><th class="n hide-s">Year</th></tr></thead><tbody>{trs}</tbody></table></div>',
         [crumbs(("Known cases",None)),dataset_ld(cases,SITE+"/cases/")],js=FJS)
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
         f'<p class="m">Check any pack yourself with the <a href="/calculator/">shrinkflation calculator</a>. Spotted one we missed? <a href="/submit/">Submit a sighting</a>.</p>',
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
         '<p class="m">Nothing you type leaves your browser. The link in the address bar updates as you type, so you can share a result. Every <a href="/cases/">documented case</a> has a “check the math” link that fills this in, and the <a href="/barcode/">barcode lookup</a> fills in the current size.</p>'
         '<div class="prose"><h2>How it works</h2>'+"".join(f'<h3>{E(q)}</h3><p>{E(a)}</p>' for q,a in calc_faq)+'<p>See the <a href="/worst/">worst offenders</a> for the biggest real price hikes we have on record.</p></div>',
         [crumbs(("Calculator",None)),{"@context":"https://schema.org","@type":"WebApplication","name":"Shrinkflation calculator","url":SITE+"/calculator/","applicationCategory":"UtilitiesApplication","operatingSystem":"Any","offers":{"@type":"Offer","price":0,"priceCurrency":"USD"}},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in calc_faq]}],js=CALC_JS)
    # ---- Barcode lookup ----
    bidx={"p":{},"b":{}}
    for p in prods:
        h=by.get(p["code"],[]); ok=[s for s in h if s.get("size")]
        sf=[f for f in findings if f[1] is p and f[2].startswith("Size dropped")]
        if sf: v,a=f"Yes, it shrank",f"{sf[0][2]} (checked {sf[0][0]})."
        elif len(ok)>1: v,a="No change so far",f'Size has stayed {fmt(ok[-1]["size"],ok[-1]["unit"])} across {len(ok)} checks since {ok[0]["date"]}.'
        elif ok: v,a="Baseline only",f'First recorded {ok[0]["date"]}. We re-check daily and flag any shrink.'
        else: v,a="Unknown","The open database has no net quantity on file for this item, so we cannot tell yet."
        bidx["p"][p["code"].lstrip("0")]=[p["title"],f'/products/{p["slug"]}.html',disp(ok[-1]) if ok else "",v,a]
    for c in cases:
        e=bidx["b"].setdefault(c["bslug"],[c["brand"],0]); e[1]+=1
    (OUT/"barcodes.json").write_text(json.dumps(bidx,ensure_ascii=False,separators=(",",":")))
    ex=[p for p in prods if any(f[1] is p and f[2].startswith("Size dropped") for f in findings)][:2]+[p for p in prods if p["category"] in ("Breakfast Cereals","Toilet Paper")][:2]
    bc_faq=[("Which barcodes work?","The 12-digit UPC on US and Canadian packs, the 13-digit EAN used in Europe, Australia and most other countries, and the short 8-digit EAN-8. Type the digits printed under the bars; spaces and dashes are ignored."),
            ("Where does the answer come from?",f"If we check the product daily (we track {len(prods)} items), you get our own size history and a yes or no on whether it shrank. For anything else we show what Open Food Facts, Open Products Facts or Open Beauty Facts list as the net quantity today, recent shelf prices from Open Prices, and how many documented shrinkflation cases we hold for the brand."),
            ("Why does it say we have no size history?","Because we only have a history for products we check every day. The open databases store the current pack size, not how it changed. Use the link to ask us to track it, and we will start recording it daily."),
            ("Is the scan private?","The camera picture is read on your device and never uploaded. To look the barcode up, your browser asks the Open Food Facts and Open Prices services for that one number. ShrinkRadar itself stores nothing and uses no trackers."),
            ("The size on the pack is different from what you show. What now?","Then the pack may have changed. That is exactly what we want to hear about: submit a sighting with the old and new size, and a photo or listing link if you have one.")]
    page("barcode/index.html",[f"Barcode lookup: did this product shrink? | {NAME}","Barcode lookup: did this product shrink?"],
         f"Type or scan a UPC or EAN barcode to see the product's pack size, its size history if we track it, recent shelf prices and the brand's shrinkflation record.",
         '<h1>Barcode lookup</h1><p class="prose">Have the pack in your hand? Type the numbers under the barcode, or scan it with your phone camera, to see whether it shrank. You get our size history for the products we check daily, and the current net quantity, recent prices and brand record for nearly everything else.</p>'
         '<form id="bform" class="calc" onsubmit="return false"><fieldset><legend class="ml">Barcode (UPC or EAN)</legend><label>Digits under the bars<input id="code" inputmode="numeric" autocomplete="off" pattern="[0-9 -]*" placeholder="e.g. 0810607024244"></label>'
         '<div class="submit-actions"><button type="submit">Look up</button> <button type="button" id="scan" hidden>Scan with camera</button></div></fieldset></form>'
         '<video id="cam" playsinline muted hidden style="width:100%;max-width:480px;border:2px solid var(--ink);margin-top:var(--s2)"></video>'
         '<p class="st" id="bst" role="status" aria-live="polite"></p><div id="bres" aria-live="polite"></div>'
         '<noscript><p class="empty">The lookup needs JavaScript. You can still <a href="/search.html">search by name</a> or browse <a href="/products/">tracked products</a>.</p></noscript>'
         +'<p class="m">Try one: '+" · ".join([f'<a href="/barcode/?code={p["code"]}" data-code="{p["code"]}">{E(p["title"])}</a>' for p in ex]+['<a href="/barcode/?code=3017620422003" data-code="3017620422003">Nutella jar (not tracked daily)</a>'])+'</p>'+
         '<p class="m">Camera scanning works in browsers that support barcode detection (Chrome on Android, for example). Elsewhere, type the digits.</p>'
         '<div class="prose"><h2>FAQ</h2>'+"".join(f'<h3>{E(q)}</h3><p>{E(a)}</p>' for q,a in bc_faq)+'<p>No barcode handy? <a href="/search.html">Search by name</a>, or browse the <a href="/cases/">documented cases</a>.</p></div>',
         [crumbs(("Barcode lookup",None)),{"@context":"https://schema.org","@type":"WebApplication","name":"ShrinkRadar barcode lookup","url":SITE+"/barcode/","applicationCategory":"UtilitiesApplication","operatingSystem":"Any","offers":{"@type":"Offer","price":0,"priceCurrency":"USD"},"description":"Look up a UPC or EAN barcode to see pack size, size history and shrinkflation record."},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in bc_faq]}],js=BARCODE_JS)
    # ---- Submit a sighting ----
    cats_opts=sorted({c["category"] for c in cases}|{p["category"] for p in prods})
    cat_sel="".join(f'<option value="{E(c)}">{E(c)}</option>' for c in cats_opts)
    ctry_sel="".join(f'<option value="{k}">{E(v)}</option>' for k,v in sorted(COUNTRY.items(),key=lambda kv:kv[1]))
    unit_opts="".join(f'<option value="{u}">{u}</option>' for u in ["g","oz","ml","fl oz","l","kg","lb","sheets","rolls","pieces","bars","loads","count","sq ft"])
    submit_faq=[("What happens after I submit?","Your browser opens a prefilled GitHub issue on the ShrinkRadar repository. We read those issues and verify each report against a primary source (a package photo, a retailer listing, a consumer-agency post or a news article) before anything is added to the case library. There is no guarantee of inclusion."),
                ("Do I need a GitHub account?","Yes, to open an issue on GitHub. If you do not have one, use the copy-to-clipboard button on this page and email the markdown to the maintainer, or open an account free at github.com."),
                ("What makes a strong sighting?","A clear product name, the old and new net size (from the package), roughly when and where you saw it, and a photo or a link to a listing that shows the net weight. Shelf price before and after helps us compute the real unit-price change."),
                ("Will you publish my email?","No. The optional email field is only so we can ask a follow-up question about the sighting. It is not shown on the public site.")]
    page("submit/index.html",f'Submit a shrinkflation sighting | {NAME}',
         'Report a shrinkflation sighting: product, old and new size, store and evidence. Opens a prefilled GitHub issue. We verify before adding to the case library.',
         '<h1>Submit a sighting</h1><p class="prose">Spotted a smaller pack? Fill this in. It opens a <b>prefilled GitHub issue</b> on our public repository. We verify every report against a source before it joins the <a href="/cases/">case library</a> — inclusion is not guaranteed.</p>'
         '<form class="calc submit" id="sight">'
         '<fieldset><legend class="ml">Product</legend>'
         '<label>Product name *<input id="product" name="product" required autocomplete="off" placeholder="e.g. Cadbury Dairy Milk Freddo multipack"></label>'
         '<label>Brand<input id="brand" name="brand" autocomplete="organization" placeholder="e.g. Cadbury"></label>'
         f'<label>Category<select id="category" name="category"><option value="">— select —</option>{cat_sel}</select></label>'
         f'<label>Country<select id="country" name="country"><option value="">— select —</option>{ctry_sel}</select></label>'
         '<label>Year / approx date<input id="when" name="when" placeholder="e.g. 2026-03 or Spring 2026"></label></fieldset>'
         '<fieldset><legend class="ml">Size change</legend>'
         f'<label>Old size *<input id="old_size" name="old_size" inputmode="decimal" required placeholder="e.g. 18"></label>'
         f'<label>Old unit *<select id="old_unit" name="old_unit" required><option value="">—</option>{unit_opts}</select></label>'
         f'<label>New size *<input id="new_size" name="new_size" inputmode="decimal" required placeholder="e.g. 15.4"></label>'
         f'<label>New unit *<select id="new_unit" name="new_unit" required><option value="">—</option>{unit_opts}</select></label></fieldset>'
         '<fieldset><legend class="ml">Price (optional)</legend>'
         '<label>Old price<input id="old_price" name="old_price" inputmode="decimal" placeholder="e.g. 4.99"></label>'
         '<label>New price<input id="new_price" name="new_price" inputmode="decimal" placeholder="e.g. 4.99"></label>'
         '<label>Currency<select id="currency" name="currency"><option value="">—</option><option value="$">$</option><option value="€">€</option><option value="£">£</option><option value="A$">A$</option><option value="C$">C$</option></select></label></fieldset>'
         '<fieldset><legend class="ml">Evidence</legend>'
         '<label>Store / where seen<input id="store" name="store" placeholder="e.g. Tesco, Walmart aisle 4"></label>'
         '<label>Source or evidence URL<input id="source" name="source" type="url" inputmode="url" placeholder="https://…"></label>'
         '<label>Notes<textarea id="notes" name="notes" rows="4" placeholder="What changed on the pack? Any photo description?"></textarea></label>'
         '<label>Your email (optional)<input id="email" name="email" type="email" autocomplete="email" placeholder="only for a follow-up question"></label></fieldset>'
         '<div class="submit-actions"><button type="submit">Open GitHub issue</button>'
         '<p class="m">Required fields marked *. Nothing is sent to our servers — the form only builds a GitHub issue URL in your browser.</p></div></form>'
         '<p class="st" id="st" role="status" aria-live="polite"></p>'
         '<section id="fallback" class="label" hidden><div class="hd">Copy if GitHub did not open</div>'
         '<p class="m">Paste this into a <a href="https://github.com/Mangomangoman1/shrinkflation/issues/new" rel="noopener" target="_blank">new GitHub issue</a>.</p>'
         '<textarea id="md" rows="12" readonly></textarea>'
         '<p><button type="button" id="copy">Copy markdown</button></p></section>'
         '<noscript><p class="empty">This form needs JavaScript to build the GitHub issue link. You can still <a href="https://github.com/Mangomangoman1/shrinkflation/issues/new">open a blank issue</a> and describe the sighting.</p></noscript>'
         '<div class="prose"><h2>FAQ</h2>'+"".join(f'<h3>{E(q)}</h3><p>{a}</p>' for q,a in submit_faq)
         +'<p>Prefer to run the numbers first? Use the <a href="/calculator/">shrinkflation calculator</a>. Browse existing reports in <a href="/cases/">known cases</a>.</p></div>',
         [crumbs(("Submit a sighting",None)),
          {"@context":"https://schema.org","@type":"WebPage","name":"Submit a shrinkflation sighting","url":SITE+"/submit/","description":"Report a shrinkflation sighting to ShrinkRadar. Opens a prefilled GitHub issue; reports are verified before inclusion."},
          {"@context":"https://schema.org","@type":"WebApplication","name":"ShrinkRadar sighting form","url":SITE+"/submit/","applicationCategory":"UtilitiesApplication","operatingSystem":"Any","offers":{"@type":"Offer","price":0,"priceCurrency":"USD"}},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in submit_faq]}],js=SUBMIT_JS)
    for kind,key,lab,namef in [("countries","country","Countries",lambda v:COUNTRY.get(v,v)),("years","year","Years",str)]:
        g={}
        for c in cases: g.setdefault(c[key],[]).append(c)
        for k,v in g.items():
            nm=namef(k)
            if kind=="years" and k in LAND_YEARS:
                # superseded by /shrinkflation-{year}/: redirect stub (canonical + instant refresh), kept out of the sitemap
                (OUT/f"years/{k}.html").parent.mkdir(parents=True,exist_ok=True)
                (OUT/f"years/{k}.html").write_text(f'<!doctype html><meta charset=utf-8><title>Shrinkflation {k}</title><link rel=canonical href="{SITE}/shrinkflation-{k}/"><meta http-equiv=refresh content="0; url=/shrinkflation-{k}/"><p><a href="/shrinkflation-{k}/">Shrinkflation {k}: documented examples</a>')
                continue
            page(f'{kind}/{str(k).lower()}.html',f'Shrinkflation in {nm}: {len(v)} documented cases | {NAME}',f'{len(v)} documented shrinkflation cases {"in "+nm if kind=="countries" else "from "+nm}, with before/after sizes and sources.',
                 f'<p class="crumbs"><a href="/cases/">Known cases</a> / <a href="/{kind}/">{lab}</a></p><h1>Shrinkflation in {E(nm)}</h1><p>{"Has shrinkflation hit "+E(nm)+"? Yes: " if kind=="countries" else ""}{len(v)} documented cases, biggest cuts first. See also the <a href="/worst/">worst offenders</a> and <a href="/guides/how-to-spot-shrinkflation.html">how to spot shrinkflation</a>.</p><ul class="grid">'+"".join(ccard(c) for c in sorted(v,key=lambda c:-c["pct"]))+'</ul>',
                 [crumbs(("Known cases","/cases/"),(nm,None))]+([{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f"Has shrinkflation hit {nm}?","acceptedAnswer":{"@type":"Answer","text":f'Yes. ShrinkRadar has {len(v)} documented, sourced shrinkflation cases in {nm}. The biggest: {max(v,key=lambda c:c["pct"])["product"]}, {fmt(max(v,key=lambda c:c["pct"])["before"],max(v,key=lambda c:c["pct"])["unit"])} → {fmt(max(v,key=lambda c:c["pct"])["after"],max(v,key=lambda c:c["pct"])["unit"])} (−{max(v,key=lambda c:c["pct"])["pct"]:.1f}%).'}}]}] if kind=="countries" else []))
        page(f'{kind}/index.html',f'Shrinkflation by {lab.lower()} | {NAME}',f'Documented shrinkflation cases by {lab.lower()[:-1]}.',
             f'<h1>Cases by {lab.lower()[:-1] if lab!="Countries" else "country"}</h1><ul class="chips">'+"".join(f'<li><a href="{f"/shrinkflation-{k}/" if kind=="years" and k in LAND_YEARS else f"/{kind}/{str(k).lower()}.html"}">{E(namef(k))} <span class="m">{len(v)}</span></a></li>' for k,v in sorted(g.items(),reverse=(kind=="years")))+'</ul>',[crumbs((lab,None))])
    def groups(kind,key,label):
        g={}
        for p in prods: g.setdefault(p[key],{"name":p["brand" if kind=="brands" else "category"] or "Unbranded","p":[],"c":[]})["p"].append(p)
        for c in cases: g.setdefault(c[key],{"name":c["brand" if kind=="brands" else "category"],"p":[],"c":[]})["c"].append(c)
        for k,v in g.items():
            nm=v["name"]; q=f"Did {nm} products shrink?"; np_,nc=len(v["p"]),len(v["c"])
            if nc:
                w=max(v["c"],key=lambda c:c["pct"]); verdict,cls="Yes","yes"
                ans=f'{nc} documented case{"s"*(nc!=1)}. Biggest cut: {w["product"]}, {fmt(w["before"],w["unit"])} → {fmt(w["after"],w["unit"])} (−{w["pct"]:.1f}%). See cases below.'
            elif np_: verdict,cls,ans="Not in our case library yet","",f'Not in our case library yet. We track {np_} {nm} product{"s"*(np_!=1)} daily and flag any size cut.'
            else: verdict,cls,ans="Unknown","","No data on file yet."
            yrs_=sorted({c["year"] for c in v["c"] if c["year"]!="n/d"}); cty=sorted({c["country"] for c in v["c"]})
            label_=(f'<section class="label" aria-label="Size facts"><div class="hd">Size Facts</div><div class="row bar"><span>{E(q)}</span><b class="{cls}">{E(verdict) if nc else ("No case yet" if np_ else "Unknown")}</b></div>'
                    f'<div class="row"><span>Documented cases</span><b>{nc}</b></div>'
                    +(f'<div class="row"><span>Biggest cut</span><b class="yes">−{w["pct"]:.1f}%</b></div><div class="row"><span>Median cut</span><b>−{med([c["pct"] for c in v["c"]]):.1f}%</b></div>' if nc else "")
                    +(f'<div class="row"><span>Years</span><b>{yrs_[0]}{"–"+yrs_[-1] if len(yrs_)>1 else ""}</b></div>' if yrs_ else "")
                    +(f'<div class="row"><span>Countries</span><b>{" ".join(FLAG.get(c,c) for c in cty)}</b></div>' if cty else "")
                    +f'<div class="row bar"><span>Tracked daily</span><b>{np_}</b></div><p>{E(ans)}</p></section>')
            body=f'<p class="crumbs"><a href="/{kind}/">{label}</a></p><h1>Did {E(nm)} products shrink?</h1>{label_}'
            if nc: body+=f'<p class="prose m">Each case links to its source. Compare with the <a href="/worst/">worst offenders</a>, or check any pack with the <a href="/calculator/">shrinkflation calculator</a>.</p>'
            if v["c"]: body+=f'<h2>Documented cases ({len(v["c"])})</h2><ul class="grid">'+"".join(ccard(c) for c in sorted(v["c"],key=lambda c:-c["pct"]))+'</ul>'
            if v["p"]: body+=f'<h2>Tracked daily ({len(v["p"])})</h2><ul class="grid">'+"".join(pcard(p) for p in v["p"])+'</ul>'
            CUR_ALERT[:]=[('brand' if kind=='brands' else 'category',k,v['name'])]
            ttl=([f'Did {nm} shrink? {nc} documented shrinkflation case{"s"*(nc!=1)} | {NAME}',f'Did {nm} shrink? {nc} shrinkflation case{"s"*(nc!=1)} | {NAME}',f'{nm} shrinkflation: {nc} case{"s"*(nc!=1)} | {NAME}',f'{nm} shrinkflation: {nc} case{"s"*(nc!=1)}'] if kind=="brands" else
                 [f'{nm} shrinkflation: {nc} documented case{"s"*(nc!=1)} | {NAME}',f'{nm} shrinkflation: {nc} case{"s"*(nc!=1)} | {NAME}',f'{nm} shrinkflation: {nc} cases']) if nc else [f'Did {nm} products shrink? Tracked daily | {NAME}',f'Did {nm} products shrink? | {NAME}',f'Did {nm} shrink?']
            page(f'{kind}/{k}.html',ttl,
                 (f'Yes: {nc} documented {nm} shrinkflation case{"s"*(nc!=1)}, biggest −{w["pct"]:.0f}% ({w["product"]}). ' if nc else f'Did {nm} products shrink? ')+f'{np_} {nm} products tracked daily for size and unit-price changes.',body,
                 [crumbs((label,f"/{kind}/"),(nm,None)),{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":(f"Yes. {ans}" if nc else ans)}}]}])
        page(f'{kind}/index.html',f'Shrinkflation by {label.lower()} | {NAME}',f'Browse shrinkflation tracking by {label.lower()}.',
             f'<h1>{label}</h1><ul class="chips">'+"".join(f'<li><a href="/{kind}/{k}.html">{E(v["name"])} <span class="m">{len(v["p"])+len(v["c"])}</span></a></li>' for k,v in sorted(g.items(),key=lambda kv:kv[1]["name"].lower()))+'</ul>',[crumbs((label,None))])
    groups("brands","bslug","Brands"); groups("categories","cslug","Categories")
    cats={}
    for p in sorted(prods,key=lambda p:p["title"].lower()): cats.setdefault(p["category"],[]).append(p)
    page("products/index.html",f'All {len(prods)} tracked products | {NAME}',f'{len(prods)} everyday products checked daily for package-size cuts and unit-price increases.',
         f'<h1>Tracked products ({len(prods)})</h1>'+"".join(f'<h2 id="{slug(k)}">{E(k)}</h2><ul class="grid">'+"".join(pcard(p) for p in v)+'</ul>' for k,v in sorted(cats.items())),[crumbs(("Products",None))])
    feed="".join(f'<li><span class="ml">{d}</span>{plink(p)} — {E(t)}</li>' for d,p,t in findings[:100]) or f'<div class="empty"><b>No shrinks detected in our daily checks yet.</b> Baselines are in place for {len(prods)} products; anything that gets smaller shows up here first.</div>'
    page("index.html",f'{NAME}: shrinkflation tracker & {len(cases)} sourced cases',f'Daily tracking of package sizes and unit prices for {len(prods)} products, plus {len(cases)} documented shrinkflation cases with sources.',
         f'<h1>Did it shrink?</h1><p class="prose">We check the net weight of {len(prods)} everyday products every day and keep a sourced record of {len(cases)} known shrinkflation cases.</p>'
         f'<form class="search" action="/search.html" role="search"><label class="ml" for="q0">Search a product or brand</label><input id="q0" name="q" placeholder="Doritos, cereal, Charmin…"></form>'
         f'<h2>Latest from daily checks</h2><ul class="feed">{feed}</ul><h2>Biggest documented shrinks</h2><ul class="grid">{"".join(ccard(c) for c in sorted(cases,key=lambda c:-c["pct"])[:6])}</ul><p><a href="/cases/"><b>All {len(cases)} known cases →</b></a> · <a href="/worst/"><b>Worst offenders →</b></a> · <a href="/calculator/"><b>Shrinkflation calculator →</b></a> · <a href="/barcode/"><b>Barcode lookup →</b></a> · <a href="/submit/"><b>Submit a sighting →</b></a></p><p class="m">'+(f'This year so far: <a href="/shrinkflation-{LAND_YEARS[0]}/"><b>shrinkflation {LAND_YEARS[0]}, {yc[LAND_YEARS[0]]} examples</b></a>. ' if LAND_YEARS else '')+f'Researchers and journalists: <a href="/data/">download the case library</a> (CSV/JSON, CC BY 4.0). New to this? Read <a href="/guides/what-is-shrinkflation.html">what shrinkflation is</a> and <a href="/guides/how-to-spot-shrinkflation.html">how to spot it in the store</a>.</p>'
         f'<h2>Recently checked</h2><ul class="grid">{"".join(pcard(p) for p in prods[:6])}</ul>',
         [{"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE+"/","potentialAction":{"@type":"SearchAction","target":SITE+"/search.html?q={search_term_string}","query-input":"required name=search_term_string"}},
          {"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE+"/","logo":SITE+"/favicon.svg"}])
    YL=year_landings(cases,ccard,med); open_data(cases)
    GUIDES=guides(cases,prods,bg,cg,med,YL)
    idx=[{"t":"Barcode lookup: scan or type a UPC/EAN","u":"/barcode/","k":"Tool"},{"t":"Submit a shrinkflation sighting","u":"/submit/","k":"Tool"},{"t":"Shrinkflation calculator","u":"/calculator/","k":"Tool"},{"t":"Worst shrinkflation offenders","u":"/worst/","k":"Tool"}]+[{"t":t,"u":u,"k":"Guide"} for u,t,_ in GUIDES]+[{"t":t,"u":u,"k":"List"} for u,t,_ in YL]+[{"t":"Open data: download shrinkflation cases (CSV, JSON)","u":"/data/","k":"Data"}]+[{"t":p["title"],"u":f'/products/{p["slug"]}.html',"k":p["category"]} for p in prods]+[{"t":c["product"]+" (documented case)","u":f'/cases/{c["slug"]}.html',"k":c["category"]} for c in cases]
    AI=[{"id":f'f:{p["code"]}:{d}:{t[:4]}',"type":"finding","date":d,"title":p["title"],"text":t,"url":f'{SITE}/products/{p["slug"]}.html',"product":p["code"],"brand":p["bslug"],"category":p["cslug"],"brand_name":p["brand"],"category_name":p["category"]} for d,p,t in findings]
    AI+=[{"id":"c:"+c["slug"],"type":"case","date":c["when"],"title":c["product"],"text":f'{fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])} ({c["pct"]:.0f}% less) · {COUNTRY.get(c["country"],c["country"])}, {c["when"]}',"url":f'{SITE}/cases/{c["slug"]}.html',"product":None,"brand":c["bslug"],"category":slug(c["category"]),"brand_name":c["brand"],"category_name":c["category"]} for c in cases]
    (R/"data/alert_items.json").write_text(json.dumps(AI,ensure_ascii=False,indent=0))
    (OUT/"search.json").write_text(json.dumps(idx,ensure_ascii=False))
    page("search.html",f'Search: did my product shrink? | {NAME}','Search tracked products and documented shrinkflation cases.',
         '<h1>Search</h1><label for="q" class="ml">Product, brand or category</label><input id="q" autofocus placeholder="e.g. Doritos, cereal, Charmin"><p class="m">Got the pack in hand? Use the <a href="/barcode/">barcode lookup</a> to type or scan its UPC.</p><ul id="res"></ul><noscript>Search needs JavaScript; browse <a href="/products/">products</a> or <a href="/cases/">cases</a>.</noscript>',js=SEARCH_JS)
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
         '<h2 id="privacy">Privacy &amp; email alerts</h2><p>No ads, cookies or analytics trackers. Email alerts (when live) store only your address, what you follow and the confirmation time. Double opt-in, one-click unsubscribe, never shared or sold. <a href="/alerts/#privacy">Details</a>.</p><p>New to the topic? Start with <a href="/guides/what-is-shrinkflation.html">what shrinkflation is and how we document it</a>.</p><p>Spotted a shrink? <a href="/submit/"><b>Submit a sighting</b></a> — it opens a prefilled GitHub issue. We verify before adding to the case library.</p></div>',[{"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE+"/"}])
    # RSS: findings + cases
    items=[(d,f'{p["title"]}: {t}',f'{SITE}/products/{p["slug"]}.html') for d,p,t in findings[:50]]+[(TODAY if not findings else findings[-1][0],f'Known case: {c["product"]} {fmt(c["before"],c["unit"])} → {fmt(c["after"],c["unit"])}',f'{SITE}/cases/{c["slug"]}.html') for c in cases]
    rss="".join(f'<item><title>{E(t)}</title><link>{u}</link><guid>{u}</guid><pubDate>{format_datetime(datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc))}</pubDate></item>' for d,t,u in items)
    (OUT/"feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE}/</link><description>Shrinkflation findings and documented cases</description>{rss}</channel></rss>')
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+
        "".join(f'<url><loc>{SITE}/{p.replace("index.html","")}</loc><lastmod>{TODAY}</lastmod></url>' for p in PAGES)+"</urlset>")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"); (OUT/".nojekyll").write_text(""); (OUT/"favicon.svg").write_text(FAV); (OUT/"og.svg").write_text(OG); og_png(OUT/"og.png") or None; (OUT/"CNAME").write_text("shrinkradar.com\n")
    # retired brand slugs from earlier mis-detected brands: noindex stubs pointing at the real brands
    for old,targets in {"dr":["Dr. Oetker","Dr. Hauschka"],"gut":["Gut & Günstig"],"la":["La Trappe","La Vache qui rit"],"costcotuna":["Kirkland"],"echo-clean-vip-products-mission-bc":["Echo Clean"]}.items():
        if not (OUT/f"brands/{old}.html").exists():
            (OUT/f"brands/{old}.html").write_text('<!doctype html><meta charset=utf-8><meta name=robots content=noindex><meta name=viewport content="width=device-width,initial-scale=1"><link rel=stylesheet href=/style.css><title>Moved</title><main class=w><h1>This brand page moved</h1><ul>'+"".join(f'<li><a href="/brands/{slug(t)}.html">{E(t)}</a></li>' for t in targets)+'</ul>')
    # renamed product pages (junk names fixed): redirect stubs to the new slug, kept out of the sitemap
    for oldp,code in {"echo-clean-vip-products-mission-bc-baby-sensitive-sulphate-f-602567":"0063827602567"}.items():
        np_=next((q for q in prods if q["code"]==code),None)
        if np_ and not (OUT/f"products/{oldp}.html").exists():
            u=f'/products/{np_["slug"]}.html'
            (OUT/f"products/{oldp}.html").write_text(f'<!doctype html><meta charset=utf-8><title>Moved</title><link rel=canonical href="{SITE}{u}"><meta http-equiv=refresh content="0;url={u}"><a href="{u}">{E(np_["title"])}</a>')
    (OUT/"llms.txt").write_text(f"""# {NAME}

> {NAME} ({SITE}) answers "did it shrink?" for groceries and household goods. It checks the net quantity of {len(prods)} everyday products daily (Open Food Facts, Open Products Facts, Open Prices; ODbL) and keeps a library of {len(cases)} documented shrinkflation cases. Every case cites the consumer agency, advocate or news source it came from; missing data is shown as missing, never estimated.

## Key pages
- [Home: latest findings]({SITE}/)
- [Known cases: all {len(cases)} documented before/after size cuts, filterable]({SITE}/cases/)
- [Worst offenders: biggest cuts, hidden per-unit price hikes, repeat brands]({SITE}/worst/)
- [Shrinkflation calculator: real price change per unit]({SITE}/calculator/)
- [Barcode lookup: type or scan a UPC/EAN to check pack size and history]({SITE}/barcode/)
- [Submit a sighting: report shrinkflation via GitHub issue]({SITE}/submit/)
- [Guides: what shrinkflation is, how to spot it]({SITE}/guides/)
"""+"".join(f"- [{t}]({SITE}{u})\n" for u,t,_ in YL)+f"""- [Open data: all {len(cases)} cases as CSV/JSON, CC BY 4.0]({SITE}/data/)
- [Brands]({SITE}/brands/) · [Categories]({SITE}/categories/) · [Countries]({SITE}/countries/) · [Products tracked daily]({SITE}/products/)
- [Methodology and sources]({SITE}/about.html)

## Machine-readable
- [RSS feed]({SITE}/feed.xml)
- [Sitemap]({SITE}/sitemap.xml)
- [Search index (JSON)]({SITE}/search.json)
- [Case library CSV]({SITE}/data/cases.csv) · [Case library JSON]({SITE}/data/cases.json) (CC BY 4.0)

Please cite ShrinkRadar and link the case page (which links the original source) when quoting figures.
""")
    if INDEXNOW_KEY: (OUT/f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    (OUT/"404.html").write_text('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><link rel=stylesheet href=/style.css><title>Not found</title><main class=w><h1>Not found</h1><p>Page not found. <a href="/">ShrinkRadar home</a> · <a href="/search.html">Search</a></p>')
    print(len(PAGES),"pages,",len(findings),"findings,",len(cases),"cases")
if __name__=="__main__": main()
