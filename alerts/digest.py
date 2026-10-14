#!/usr/bin/env python3
"""Daily alert digest: diff data/alert_items.json against alerts/state.json, match subscriptions, render + send.
Default is DRY RUN (writes rendered emails to alerts/out/<day>/). Real sending needs --send plus
env ALERTS_API (worker origin) and ALERTS_ADMIN_TOKEN. Subscriptions come from the worker, or --subs FILE in dry-run."""
import json, os, sys, html, pathlib, datetime, argparse, urllib.request
R=pathlib.Path(__file__).resolve().parent; ROOT=R.parent; E=html.escape
SITE="https://shrinkradar.com"; FREE_MAX_ITEMS=50
ap=argparse.ArgumentParser(); ap.add_argument("--send",action="store_true"); ap.add_argument("--subs"); ap.add_argument("--all-as-new",action="store_true",help="treat every item as new (demo)")
ap.add_argument("--state",default=str(R/"state.json")); a=ap.parse_args()
API=os.environ.get("ALERTS_API","").rstrip("/"); TOKEN=os.environ.get("ALERTS_ADMIN_TOKEN","")
day=datetime.date.today().isoformat()
items=json.load(open(ROOT/"data/alert_items.json"))
st=pathlib.Path(a.state); seen=set(json.load(open(st))) if st.exists() else None
if a.all_as_new: new=items
elif seen is None:   # first run: baseline only, never blast the back catalogue
    json.dump(sorted(i["id"] for i in items),open(st,"w")); print(f"baseline: {len(items)} items marked seen, nothing sent"); sys.exit(0)
else: new=[i for i in items if i["id"] not in seen]
def api(path,body=None):
    r=urllib.request.Request(API+path,data=json.dumps(body).encode() if body is not None else None,headers={"authorization":"Bearer "+TOKEN,"content-type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=30))
if a.subs: rows=json.load(open(a.subs))
elif API and TOKEN: rows=api("/admin/subscriptions")
else: rows=[]; print("no subscriptions source (set ALERTS_API/ALERTS_ADMIN_TOKEN or --subs)")
subs={}
for r in rows: subs.setdefault(r["id"],{"email":r["email"],"token":r["token"],"plan":r.get("plan","free"),"f":set()})["f"].add((r["kind"],r["key"]))
def why(i,f):
    if ("all","all") in f: return "All new findings"
    if i["product"] and ("product",i["product"]) in f: return "Product you follow"
    if ("brand",i["brand"]) in f: return f'Brand: {i["brand_name"]}'
    if ("category",i["category"]) in f: return f'Category: {i["category_name"]}'
def render(s,its):
    man=f'{API or "https://alerts.shrinkradar.com"}/manage?t={s["token"]}'; uns=f'{API or "https://alerts.shrinkradar.com"}/unsubscribe?t={s["token"]}'
    nf=sum(i["type"]=="finding" for i,_ in its); nc=len(its)-nf
    subj=f'ShrinkRadar: {len(its)} new shrink{"s" if len(its)!=1 else ""}'+(f' — {its[0][0]["title"]}' if len(its)==1 else '')
    F="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif"
    rows="".join(f'<tr><td style="padding:12px 0;border-bottom:1px solid #d8d4ca;{F}"><div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#595650">{"Daily check" if i["type"]=="finding" else "Documented case"} · {E(w)}</div>'
                 f'<a href="{E(i["url"])}" style="color:#111;font-size:17px;font-weight:700;text-decoration-color:#c8102e">{E(i["title"])}</a>'
                 f'<div style="font-size:15px;margin-top:2px"><span style="background:#fbe9eb;color:#c8102e;font-weight:900;padding:0 5px">{E(i["text"])}</span></div></td></tr>' for i,w in its)
    h=(f'<!doctype html><html><body style="margin:0;background:#f7f5ef;color:#111;{F}"><table role="presentation" width="100%" style="background:#f7f5ef"><tr><td align="center" style="padding:24px 12px">'
       f'<table role="presentation" width="100%" style="max-width:600px;background:#fff;border:2px solid #111"><tr><td style="padding:16px 20px;border-bottom:8px solid #111"><span style="font-size:26px;font-weight:900;letter-spacing:-.03em">Shrink<span style="color:#c8102e">Radar</span></span>'
       f'<div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#595650">Net Wt. alert · {day}</div></td></tr>'
       f'<tr><td style="padding:16px 20px 4px"><div style="font-size:30px;font-weight:900;letter-spacing:-.02em;line-height:1.1">{len(its)} new shrink{"s" if len(its)!=1 else ""}</div>'
       f'<div style="font-size:14px;color:#595650;margin-top:4px;border-bottom:4px solid #111;padding-bottom:10px">{nf} from daily checks · {nc} documented cases matching what you follow</div></td></tr>'
       f'<tr><td style="padding:0 20px"><table role="presentation" width="100%">{rows}</table></td></tr>'
       f'<tr><td style="padding:16px 20px;font-size:12px;color:#595650;border-top:8px solid #111">You get this because you follow these on ShrinkRadar ({E(s["plan"])} plan). '
       f'<a href="{E(man)}" style="color:#111">Manage alerts</a> · <a href="{E(uns)}" style="color:#111">Unsubscribe</a><br>Data: Open Food Facts, Open Prices (ODbL) and cited sources. No tracking pixels.</td></tr></table></td></tr></table></body></html>')
    t=f"ShrinkRadar — {len(its)} new shrinks ({day})\n\n"+"\n".join(f'- {i["title"]}: {i["text"]}\n  {i["url"]}' for i,_ in its)+f"\n\nManage: {man}\nUnsubscribe: {uns}\n"
    return subj,h,t,uns
out=R/"out"/day; n=0
for sid,s in subs.items():
    its=[(i,w) for i in new if (w:=why(i,s["f"]))]
    if not its: continue
    its.sort(key=lambda x:(x[0]["type"]!="finding",x[0]["title"]))
    if s["plan"]!="pro": its=its[:FREE_MAX_ITEMS]   # pro hook: unlimited / instant later
    subj,h,t,uns=render(s,its); n+=1
    if a.send and API and TOKEN:
        print(sid,api("/admin/send",{"subscriber_id":sid,"day":day,"to":s["email"],"subject":subj,"html":h,"text":t,"unsub":uns,"item_ids":[i["id"] for i,_ in its]}))
    else:
        out.mkdir(parents=True,exist_ok=True); (out/f"{sid}.html").write_text(h); (out/f"{sid}.txt").write_text(f"To: {s['email']}\nSubject: {subj}\n\n{t}")
if not a.all_as_new and (a.send or not subs): json.dump(sorted(i["id"] for i in items),open(st,"w"))
print(f"{len(new)} new items, {len(subs)} subscribers, {n} digests {'sent' if a.send else 'rendered to '+str(out)}")
