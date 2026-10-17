import json,urllib.request,urllib.parse,time,sys
UA={"User-Agent":"ShrinkRadar/0.2 (https://shrinkradar.com)"}
out={}
for page in range(1,41):
    u="https://prices.openfoodfacts.org/api/v1/prices?"+urllib.parse.urlencode({"currency":"USD","order_by":"-date","size":100,"page":page})
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: print("err",page,e); time.sleep(10); continue
    for it in d["items"]:
        p=it.get("product") or {}
        c=p.get("code") or it.get("product_code")
        if not c: continue
        o=out.setdefault(c,{"code":c,"product":p,"prices":[]})
        o["prices"].append({"id":it["id"],"price":it["price"],"date":it.get("date"),"store":(it.get("location") or {}).get("osm_name")})
    print(page,len(d["items"]),len(out),flush=True)
    if not d["items"]: break
    time.sleep(1.5)
json.dump(out,open("raw/openprices/usd_2026-10-17.json","w"))
