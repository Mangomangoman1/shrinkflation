#!/usr/bin/env python3
"""Daily checker: fetch size (Open Food Facts / Open Products Facts) and latest USD price
(Open Prices, prices.openfoodfacts.org) per product; append to data/snapshots.json.
Only fetched values are stored; failures are recorded with status/error, never filled in."""
import json, pathlib, datetime, time, urllib.request, urllib.parse
R=pathlib.Path(__file__).parent; DATA=R/"data"/"snapshots.json"; DATA.parent.mkdir(exist_ok=True)
UA={"User-Agent":"ShrinkflationTracker/0.1 (github.com/Mangomangoman1)"}
HOST={"off":"https://world.openfoodfacts.org","opf":"https://world.openproductsfacts.org","obf":"https://world.openbeautyfacts.org"}
def get(u):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception as e: err=e; time.sleep(3*(i+1))
    raise err
def main():
    prods=json.load(open(R/"products.json")); snaps=json.load(open(DATA)) if DATA.exists() else []
    today=datetime.date.today().isoformat()
    for p in prods:
        s={"code":p["code"],"date":today,"size":None,"unit":None,"quantity_label":None,"price":None,"currency":None,"price_date":None,"price_source":None}
        s["source_url"]=f'{HOST[p["db"]]}/product/{p["code"]}'
        try:
            d=get(f'{HOST[p["db"]]}/api/v2/product/{p["code"]}.json?fields=product_name,quantity,product_quantity,product_quantity_unit')
            pr=d.get("product") or {}
            if pr.get("product_quantity"):
                s["size"]=round(float(pr["product_quantity"]),2); s["unit"]=pr.get("product_quantity_unit") or "g"
            s["quantity_label"]=pr.get("quantity")
        except Exception as e: s["size_error"]=str(e)[:120]
        try:
            q=get("https://prices.openfoodfacts.org/api/v1/prices?"+urllib.parse.urlencode({"product_code":p["code"],"currency":"USD","order_by":"-date","size":1}))
            if q.get("items"):
                it=q["items"][0]; s.update(price=it["price"],currency="USD",price_date=it.get("date"),
                    price_source=f'https://prices.openfoodfacts.org/prices/{it["id"]}')
        except Exception as e: s["price_error"]=str(e)[:120]
        s["status"]="ok" if s["size"] else "size_missing"
        snaps=[x for x in snaps if not (x["code"]==p["code"] and x["date"]==today)]+[s]
        print(p["code"],s["status"],s["size"],s["unit"],s["price"]); time.sleep(0.7)
    json.dump(snaps,open(DATA,"w"),indent=1)
if __name__=="__main__": main()
