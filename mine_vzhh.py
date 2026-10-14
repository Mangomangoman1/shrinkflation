#!/usr/bin/env python3
"""Parse Verbraucherzentrale Hamburg Mogelpackungsliste pages (raw/vzhh/p*.html)."""
import re,html,glob,json
def T(h): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>","|",h)))
def clean(x): return re.sub(r"(\s*\|\s*)+","|",x).strip("| ")
MON={"Januar":1,"Februar":2,"März":3,"April":4,"Mai":5,"Juni":6,"Juli":7,"August":8,"September":9,"Oktober":10,"November":11,"Dezember":12}
def qty(s):
    m=re.match(r"\s*(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|Liter|Stück|Blatt|Beutel|Rollen|Tabs|Kapseln|WL|Waschladungen|cl)\b",s,re.I)
    if not m: return None
    return float(m.group(1).replace(".","").replace(",",".") if re.search(r"\d\.\d{3}$",m.group(1)) else m.group(1).replace(",",".")),m.group(2)
out={};
for f in sorted(glob.glob("raw/vzhh/p*.html"),key=lambda f:int(re.findall(r"\d+",f)[-1])):
    pn=int(re.findall(r"\d+",f)[-1]); x=clean(T(open(f).read()))
    for chunk in x.split("|Hersteller|")[1:]:
        pass
    parts=x.split("|© Verbraucherzentrale Hamburg|")
    for i in range(1,len(parts)):
        name=parts[i-1].rsplit("|",1)[-1].strip()
        body=parts[i]
        g=lambda k: (re.search(re.escape(k)+r"\s*\|([^|]+)",body) or [None,None])[1]
        old,new=g("Alte Füllmenge"),g("Neue Füllmenge")
        if not old or not new: continue
        qo,qn=qty(old),qty(new)
        if not qo or not qn: continue
        date=g("Datum") or ""; ym=re.search(r"(\w+) (\d{4})",date)
        year=ym.group(2) if ym else None
        c=dict(product=name,brand=name.split(" ")[0],maker=(g("Hersteller") or "").strip(),before=qo[0],after=qn[0],unit=qo[1].replace("Liter","l"),
               unit_after=qn[1],when=year,date_reported=date.strip(),country="DE",old_price=(g("Alter Preis") or "").strip(),new_price=(g("Neuer Preis") or "").strip(),
               hidden_increase=(g("Preiserhöhung") or "").strip(),retailer=(g("Gekauft bei") or "").strip(),
               source_url="https://www.vzhh.de/mogelpackungsliste"+(f"?page={pn}" if pn else ""),source="Verbraucherzentrale Hamburg — Mogelpackungsliste",
               evidence=f'Alte Füllmenge {old.strip()} → Neue Füllmenge {new.strip()}; Preis {(g("Alter Preis") or "?").strip()} → {(g("Neuer Preis") or "?").strip()} ({date.strip()})',
               evidence_type="consumer-protection agency list (purchased packages, manufacturer statement)",confidence="high")
        if c["unit"].lower()!=c["unit_after"].lower(): continue
        if c["after"]>=c["before"]: continue
        out.setdefault((name.lower(),c["before"],c["after"],c["when"]),c)
json.dump(list(out.values()),open("raw/vzhh_cases.json","w"),indent=1,ensure_ascii=False)
print(len(out))
