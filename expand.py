import json,time,urllib.request,urllib.parse
UA={"User-Agent":"ShrinkRadar/0.2 (https://shrinkradar.com)"}
P=json.load(open("products.json")); seen={p["code"] for p in P}
CATS=["breakfast-cereals","coffees","teas","rice","flours","sugars","cooking-oils","ketchup","mayonnaises","mustards","canned-soups","canned-tunas","peanuts","nuts","dried-fruits","frozen-vegetables","frozen-desserts","energy-drinks","sports-drinks","bottled-waters","milks","butters","eggs","jams","honeys","breakfast-bars","pretzels","tortilla-chips","biscuits","chewing-gum","dog-food","cat-food","baby-foods","hot-sauces","pasta-sauces","snacks"]
def get(u):
    for i in range(6):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read()
            return json.loads(r)
        except Exception as e: print("retry",i,e); time.sleep(15*(i+1))
    return None
for c in CATS:
    have=sum(p["category"]==c.replace('-',' ').title() for p in P)
    if have>=6: continue
    d=get("https://world.openfoodfacts.org/api/v2/search?"+urllib.parse.urlencode({"categories_tags_en":c,"countries_tags_en":"united-states","sort_by":"unique_scans_n","page_size":20,"fields":"code,product_name,brands,product_quantity"}))
    n=0
    for p in (d or {}).get("products",[]):
        if p["code"] in seen or not p.get("product_quantity") or not p.get("product_name") or n>=6-have: continue
        seen.add(p["code"]); n+=1
        P.append({"code":p["code"],"name":p["product_name"].strip(),"brand":(p.get("brands") or "").split(",")[0].strip(),"category":c.replace('-',' ').title(),"db":"off"})
    print(c,n,len(P)); json.dump(P,open("products.json","w"),indent=1); time.sleep(12)
