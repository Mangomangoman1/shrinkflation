#!/usr/bin/env python3
"""Extract before/after size changes from the Mouse Print* archive (raw/mouseprint/*.json, WP REST dump).
Each case keeps a verbatim evidence quote from the fetched post."""
import json,glob,re,html
U=r"(fl\.? ?oz\.?|fluid ounces|ounces?|oz\.?|pounds?|lbs?\.?|grams?|g|kg|ml|milliliters?|liters?|litres?|sheets?|rolls?|count|pods?|loads?|bars?|tablets?|pieces?|bags?|packets?|wipes?|tissues?|cookies|crackers|slices|servings|cups|squares|feet|square feet|sq\.? ft\.?|yards?|pairs?|diapers?|k-cups|capsules|cans|bottles|tea bags|filters|plates|napkins|towels|dusters|pads|liners|cones|bagels|muffins|rolls|links|franks)"
N=r"(\d{1,4}(?:,\d{3})?(?:\.\d+)?)"
PATS=[re.compile(p,re.I) for p in [
 rf"from (?:about |roughly |a )?{N}[- ]?{U}?(?: \w+){{0,3}}? (?:down )?to (?:just |only |a mere |now |about )?{N}[- ]?{U}",
 rf"{N}[- ]?{U} (?:down )?to (?:just |only |a mere )?{N}(?:[- ]?{U})?",
 rf"{N}[- ]{U}\b[^.;]{{0,70}}? (?:down to|to just|to only|to a mere|reduced to|now just|now only|to) {N}[- ]?{U}",
 rf"(?:now|just|only) {N}[- ]?{U},? (?:down|reduced) from {N}[- ]?{U}?",
 rf"(?:shr[au]nk|dropped|downsized|reduced|went|cut|decreased|fell|slimmed)(?: \w+){{0,5}}? from {N}[- ]?{U}? to (?:just |only )?{N}[- ]?{U}?",
]]
UNIT={"fl oz":"fl oz","fl. oz":"fl oz","fluid ounce":"fl oz","ounce":"oz","oz":"oz","pound":"lb","lb":"lb","gram":"g","g":"g","kg":"kg","ml":"ml","milliliter":"ml","liter":"L","litre":"L"}
def nu(u):
    if not u: return None
    u=u.lower().rstrip(".").strip()
    for k,v in UNIT.items():
        if u==k or u==k+"s" or u.replace(" ","")==k.replace(" ",""): return v
    if u.startswith("fl"): return "fl oz"
    return u.rstrip("s") if u not in("pieces","tissues","sheets","rolls","pods","loads","bars","tablets","wipes","diapers") else u
def num(x): return float(x.replace(",",""))
def text(h): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",h))).strip()
out=[];seen=set()
for f in sorted(glob.glob("raw/mouseprint/p*.json")):
    d=json.load(open(f))
    if not isinstance(d,list): continue
    for post in d:
        c=post["content"]["rendered"]; title=text(post["title"]["rendered"]); date=post["date"][:10]
        secs=[]
        for part in re.split(r"<hr\s*/?>|<HR>|(?=<th[ >])|(?=<h[23][ >])",c):
            hm=re.search(r"<th[^>]*>(.*?)</th>|<h[23][^>]*>(.*?)</h[23]>",part,re.S)
            name=text(hm.group(1) or hm.group(2)) if hm else None
            if not name:
                am=re.search(r'<img[^>]*alt="([^"]{3,60})"',part); name=html.unescape(am.group(1)) if am else None
            body=part[hm.end():] if hm else part
            body=text(re.sub(r"\*MOUSE PRINT:?","",body))
            if name and body: secs.append((name,body))
        for prod,body in secs:
            if not prod or len(prod)>70 or re.search(r"downsize again|shrink again|mouse print|related|comments?$|news|\btv\b|video|update|reader|letter",prod,re.I): continue
            for sent in re.split(r"(?<![Oo]z)(?<!fl)(?<!lb)(?<!lbs)(?<!\d)\.\s+(?=[A-Z*])",re.sub(r"(\d+)-(\d)/(\d)",lambda m:str(round(int(m.group(1))+int(m.group(2))/int(m.group(3)),3)),body.replace("a full pound","16 ounces").replace("a pound","16 ounces").replace("a full quart","32 ounces"))):
                hit=None
                for P in PATS:
                    m=P.search(sent)
                    if not m: continue
                    g=m.groups()
                    if len(g)==4 and P.pattern.startswith("(?:now|just|only)"): b,ub,a,ua=g
                    elif len(g)==4: a,ua,b,ub=g
                    else: a,ua,b,ub=g[0],g[1],g[2],g[3] if len(g)>3 else None
                    ua,ub=nu(ua),nu(ub); u=ub or ua
                    if not u or (ua and ub and ua!=ub): continue
                    A,B=num(a),num(b)
                    if not (0<B<A) or A/B>3 or re.fullmatch(r"(19|20)\d\d",a) or re.fullmatch(r"(19|20)\d\d",b): continue
                    if re.search(r"\$|cents|price|percent|%|calorie",sent[max(0,m.start()-15):m.end()+5],re.I) and not re.search(r"ounce|oz|sheet|count|pound|gram",u): continue
                    hit=(A,B,u,sent[:400]); break
                if hit:
                    key=(prod.lower(),hit[0],hit[1],hit[2])
                    if key in seen: break
                    seen.add(key)
                    out.append(dict(product=prod,brand=prod.split(" ")[0].replace("’s","'s"),before=hit[0],after=hit[1],unit=hit[2],when=date[:4],date_reported=date,
                        country="US",source_url=post["link"],source=f"Mouse Print* — {title}",evidence=hit[3],evidence_type="consumer-advocate report (photo of old/new packages)",confidence="high"))
                    break
json.dump(out,open("raw/mouseprint_cases.json","w"),indent=1,ensure_ascii=False)
print(len(out))
