"""2026-10-17: add hand-picked US products. Food picks come from recent USD Open Prices receipts (so they arrive with a shelf price);
household/personal-care picks from Open Beauty Facts US searches. Each code is re-fetched from its database; kept only if it has a
name and a numeric product_quantity."""
import json,urllib.request,time
UA={"User-Agent":"ShrinkRadar/0.2 (https://shrinkradar.com)"}
HOST={"off":"https://world.openfoodfacts.org","opf":"https://world.openproductsfacts.org","obf":"https://world.openbeautyfacts.org"}
PICK=[
# coffee
("0180626000155","Ground Coffees","off"),("0180626000162","Ground Coffees","off"),("0855186006281","Coffees","off"),("0604913006342","Coffees","off"),
("0041953026020","Ground Coffees","off"),("0041953075080","Ground Coffees","off"),("0762111206091","Coffees","off"),("0762111885548","Coffees","off"),
("0043000043011","Ground Coffees","off"),("0873562000944","Ground Coffees","off"),("0819385023326","Instant Coffees","off"),
# cereal / oats / granola
("0884912434296","Breakfast Cereals","off"),("0041190093045","Breakfast Cereals","off"),("0855140002687","Breakfast Cereals","off"),
("0039978041401","Breakfast Cereals","off"),("0039978039521","Breakfast Cereals","off"),
# other big-brand groceries with USD receipts
("0051500255186","Peanut Butters","off"),("0037600105064","Peanut Butters","off"),("0037600105002","Peanut Butters","off"),
("0038000138607","Chips","off"),("0028400199988","Chips","off"),("0037466016450","Chocolate Candies","off"),("0009800000715","Chocolate Candies","off"),
("0071720539446","Candies","off"),("0010700021526","Candies","off"),("0041186000415","Candies","off"),
("0076840485116","Ice Creams","off"),("0076840100583","Ice Creams","off"),("0074570810116","Ice Creams","off"),
("0049000050141","Sodas","off"),("0049000050103","Sodas","off"),("4099100008616","Breads","off"),("0013764028074","Breads","off"),("0072945601369","Breads","off"),
("0041271025644","Coffee Creamers","off"),("0078742148908","Cheeses","off"),("0044000046545","Cookies","off"),("0810291001057","Cookies","off"),
("0070177267728","Teas","off"),("0076950203280","Teas","off"),
# household / personal care (Open Beauty Facts)
("0035000444349","Toothpaste","obf"),("0035000511126","Toothpaste","obf"),("0035000521019","Toothpaste","obf"),("0037000772521","Toothpaste","obf"),
("0077326832608","Toothpaste","obf"),("0827854026402","Toothpaste","obf"),
("0381519183379","Shampoo","obf"),("0022400011776","Shampoo","obf"),("0603084459490","Shampoo","obf"),("0381519188787","Shampoo","obf"),("3606000607019","Shampoo","obf"),
("0022200941525","Deodorant","obf"),("0030772149379","Deodorant","obf"),("0079400352972","Deodorant","obf"),("0012044065570","Deodorant","obf"),
("0047400098190","Deodorant","obf"),("0812154035223","Deodorant","obf"),("0019045001743","Deodorant","obf"),
("0030772253717","Mouthwash","obf"),("0037000943228","Mouthwash","obf"),
("0011111051249","Body Wash","obf"),("0018787788059","Soap","obf"),("0018787767160","Soap","obf"),("0856294008174","Soap","obf"),
]
P=json.load(open("products.json")); have={p["code"] for p in P}; added=[];skipped=[]
for code,cat,db in PICK:
    if code in have: skipped.append((code,"dup")); continue
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(f'{HOST[db]}/api/v2/product/{code}.json?fields=product_name,product_name_en,brands,quantity,product_quantity,product_quantity_unit',headers=UA),timeout=40))
    except Exception as e: skipped.append((code,str(e)[:60])); continue
    pr=d.get("product") or {}; name=(pr.get("product_name_en") or pr.get("product_name") or "").strip()
    try: q=float(pr.get("product_quantity") or 0)
    except: q=0
    if d.get("status")!=1 or not name or not q: skipped.append((code,"no name/qty",name,pr.get("product_quantity"))); continue
    P.append({"code":code,"name":name,"brand":(pr.get("brands") or "").split(",")[0].strip(),"category":cat,"db":db}); have.add(code); added.append((code,name,pr.get("brands"),pr.get("quantity"),q,pr.get("product_quantity_unit")))
    time.sleep(0.8)
json.dump(P,open("products.json","w"),indent=1,ensure_ascii=False)
for a in added: print("ADD",a)
for s in skipped: print("SKIP",s)
print(len(added),"added; total",len(P))
