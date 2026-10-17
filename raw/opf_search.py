import json,urllib.request,urllib.parse,time
UA={"User-Agent":"ShrinkRadar/0.2 (https://shrinkradar.com)"}
P={p["code"] for p in json.load(open("products.json"))}
Q=[("opf","https://world.openproductsfacts.org",c) for c in ["trash-bags","garbage-bags","dishwashing-liquids","dish-soaps","dishwasher-detergents","laundry-detergents","fabric-softeners","paper-towels","toilet-paper","facial-tissues","aluminium-foils","food-storage-bags","cleaning-products","sponges","dishwasher-tablets","laundry-pods"]]+[("obf","https://world.openbeautyfacts.org",c) for c in ["toothpastes","shampoos","conditioners","deodorants","body-washes","shower-gels","mouthwashes","soaps","hand-soaps","body-lotions","razors"]]
res={}
for db,h,c in Q:
    u=f"{h}/api/v2/search?"+urllib.parse.urlencode({"categories_tags":c,"countries_tags":"en:united-states","fields":"code,product_name,brands,quantity,product_quantity,product_quantity_unit,unique_scans_n","page_size":50,"sort_by":"unique_scans_n"})
    d=None
    for i in range(3):
        try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60)); break
        except Exception as e: print("retry",c,e,flush=True); time.sleep(10*(i+1))
    L=[dict(p,db=db,cat=c) for p in (d or {}).get("products",[]) if p.get("code") not in P]
    res[c]=L; print(c,len(L),sum(1 for p in L if p.get("product_quantity")),flush=True); time.sleep(4)
json.dump(res,open("raw/opf_search_2026-10-17.json","w"),indent=1)
