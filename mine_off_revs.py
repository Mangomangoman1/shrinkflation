#!/usr/bin/env python3
"""Sample Open Food Facts edit history per tracked barcode; flag net-quantity decreases that persist to the current record."""
import json,re,time,urllib.request,datetime
UA={"User-Agent":"ShrinkRadar/0.3 (https://shrinkradar.com)"}
def get(u):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception: time.sleep(4*(i+1))
def q(s):
    if not s: return None
    m=re.search(r"(\d+(?:[.,]\d+)?)\s*(fl\.? ?oz|oz|g|kg|ml|l|lb)\b",s,re.I)
    if not m: return None
    v=float(m.group(1).replace(",",".")); u=m.group(2).lower().replace(".","").replace(" ","")
    return v,u
out=[];P=[p for p in json.load(open("products.json")) if p["db"]=="off"]
for p in P:
    cur=get(f'https://world.openfoodfacts.org/api/v2/product/{p["code"]}.json?fields=rev,quantity')
    if not cur or "product" not in cur: continue
    R=cur["product"].get("rev") or 0; cq=q(cur["product"].get("quantity"))
    if not cq or R<3: continue
    revs=sorted(set([max(1,int(R*k/6)) for k in range(6)]))
    hist=[]
    for r in revs:
        d=get(f'https://world.openfoodfacts.org/api/v0/product/{p["code"]}.json?rev={r}')
        pr=(d or {}).get("product") or {}
        qq=q(pr.get("quantity"))
        if qq: hist.append((r,qq,pr.get("last_modified_t"),pr.get("quantity")))
        time.sleep(0.4)
    hist.append((R,cq,None,cur["product"].get("quantity")))
    for (r1,q1,t1,s1) in hist:
        if q1[1]==cq[1] and q1[0]>cq[0] and q1[0]/cq[0]<1.5:
            out.append(dict(code=p["code"],product=p["name"],brand=p["brand"],category=p["category"],before=q1[0],after=cq[0],unit=cq[1],
                before_label=s1,after_label=cur["product"].get("quantity"),before_rev=r1,before_time=datetime.datetime.fromtimestamp(t1).date().isoformat() if t1 else None,current_rev=R))
            break
    print(p["code"],len(hist),"flag" if out and out[-1]["code"]==p["code"] else "",flush=True)
json.dump(out,open("raw/off_rev_cases.json","w"),indent=1)
print("flags",len(out))
