#!/usr/bin/env python3
"""Merge all mined/verified case sources into data/cases.json (deduped)."""
import json,re,os
BRANDS="""Angel Soft|Charmin|Cottonelle|Quilted Northern|Scott|Bounty|Sparkle|Brawny|Viva|Great Value|Kirkland|Frosted Flakes|Raisin Bran|Cheerios|Cocoa Puffs|Reese's|Rolo|Hershey's|M&M's|Lay's|Cheetos|Wheat Thins|Tostitos|Doritos|Folgers|Maxwell House|Tropicana|Simply Orange|Florida's Natural|Ivory|Kraft|Haagen-Dazs|Häagen-Dazs|Lanacane|Chicken of the Sea|Classico|Hebrew National|Gatorade|Powerade|Tide|Gain|Downy|Dawn|Crest|Colgate|Pringles|Oreo|Nabisco|Ritz|Kellogg's|Post|General Mills|Betty Crocker|Quaker|Cap'n Crunch|Jif|Skippy|Peter Pan|Nathan's|Oscar Mayer|Ball Park|Breyers|Tillamook|Chobani|Dannon|Yoplait|Ben & Jerry's|Edy's|Dreyer's|Puffs|Kleenex|Huggies|Pampers|Febreze|Swiffer|Clorox|Lysol|Dove|Suave|Pantene|Head & Shoulders|Gillette|Listerine|Scope|Starbucks|Dunkin|Peet's|Green Mountain|Keurig|Lipton|Pure Leaf|Gold Peak|Snapple|Ocean Spray|Minute Maid|Welch's|Smucker's|Hungry Jack|Aunt Jemima|Pearl Milling|Mrs. Butterworth's|Pillsbury|Duncan Hines|Ghirardelli|Nestlé|Nestle|KitKat|Kit Kat|Cadbury|Lindt|Toblerone|Milka|Ritter Sport|Mars|Snickers|Twix|Milky Way|Dove|Whiskas|Iams|Purina|Pedigree|Meow Mix|Fancy Feast|Friskies|Thomas'|Sara Lee|Nature's Own|Pepperidge Farm|Keebler|Chips Ahoy|Nutter Butter|Triscuit|Goldfish|Cheez-It|Utz|Ruffles|Fritos|SunChips|Sun Chips|Kettle|Cape Cod|Planters|Blue Diamond|Werther's|Jolly Rancher|Life Savers|Skittles|Starburst|Haribo|Trolli|Sour Patch|Junior Mints|Hostess|Little Debbie|Entenmann's|Breton|Kashi|Special K|Corn Pops|Froot Loops|Apple Jacks|Rice Krispies|Lucky Charms|Chex|Kix|Trix|Honey Nut|Ortega|Old El Paso|Taco Bell|Barilla|Ronzoni|Mueller's|Prego|Ragu|Rao's|Heinz|Hunt's|French's|Hellmann's|Best Foods|Miracle Whip|Hidden Valley|Kraft|Velveeta|Philadelphia|Sargento|Tillamook|Land O Lakes|Country Crock|I Can't Believe|Hormel|Spam|StarKist|Bumble Bee|Season|Del Monte|Dole|Green Giant|Birds Eye|Stouffer's|Lean Cuisine|DiGiorno|Totino's|Hot Pockets|Farm Rich|Tyson|Perdue|Jimmy Dean|Johnsonville|Charmin|Equate|Up & Up|Publix|Kroger|Walmart|Costco|Trader Joe's|Aldi|Coles|Woolworths|Tesco|Sainsbury's|Lurpak|Yeo Valley|Bisto|McVitie's|Walkers|Quality Street|Celebrations|Terry's|Aquafresh|Gaviscon|PG Tips|Andrex|Comfort|Magnum|Richmond|Coffee Mate|Nescafé|Kiri|Lindt|St Hubert|Saint Louis|Teisseire|Salvetat|Auchan|Carrefour|Reflets de France|Redpath|Pearl Milling Company|Red Rock Deli|Community Co|Jif|Vim|Sensodyne|Johnson's|Neutrogena|Aveeno|Olay|Irish Spring|Softsoap|Dial|Palmolive|Ajax|Cascade|Finish|Bounce|Snuggle|Arm & Hammer|OxiClean|Purex|All|Persil|Glad|Hefty|Ziploc|Reynolds|Kingsford|Duracell|Energizer|Breyers|Klondike|Good Humor|Popsicle|Drumstick|Blue Bell|Turkey Hill|Talenti|Halo Top|Edy's|Friendly's|Simply|Florida's Natural|Minute Maid|Capri Sun|Kool-Aid|Crystal Light|Country Time|Hawaiian Punch|V8|Campbell's|Progresso|Lipton|Knorr|Bear Creek|Idahoan|Uncle Ben's|Ben's Original|Minute Rice|Zatarain's|Rice-A-Roni|Pasta Roni|Stove Top|Jell-O|Cool Whip|Reddi-wip|Hershey|Brach's|Russell Stover|Whitman's|Ferrero|Nutella|Tic Tac|Mentos|Trident|Extra|Orbit|Wrigley's|5 Gum|Ice Breakers|Altoids|Lifesavers|Sour Punch|Twizzlers|Swedish Fish|Mike and Ike|Hot Tamales|Peeps|Funpops|FunPops|Sparkle|Puffs"""
BL=sorted(set(BRANDS.split("|")),key=len,reverse=True)
ALIAS={"Hershey":"Hershey's","Nestle":"Nestlé","Kit Kat":"KitKat","Haagen-Dazs":"Häagen-Dazs","Sun Chips":"SunChips","Funpops":"FunPops","Lifesavers":"Life Savers","Simply":"Simply Orange","Honey Nut":"Cheerios"}
def norm(s): return s.replace("’","'").replace("‘","'")
def brand_of(c):
    t=norm(c["product"])
    for b in BL:
        if re.search(r"(?<![A-Za-z])"+re.escape(b)+r"(?![A-Za-z])",t,re.I): return ALIAS.get(b,b)
    b=norm(c.get("brand") or t.split(" ")[0])
    return ALIAS.get(b,b)
def slugish(x): return re.sub(r"[^a-z0-9]+","",x.lower())
UNITS={"ounce":"oz","ounces":"oz","sheets":"sheets","sheet":"sheets","sheets/roll":"sheets/roll","gram":"g"}
src=[("data/cases_seed.json","seed"),("raw/manual_cases.json","manual"),("raw/table_cases.json","tables"),("raw/mouseprint_cases.json","mouseprint"),("raw/vzhh_cases.json","vzhh"),("raw/cb_cases.json","cb"),("raw/off_rev_final.json","off")]
if not os.path.exists("data/cases_seed.json"): os.rename("data/cases.json","data/cases_seed.json")
out={};order=[]
for f,tag in src:
    if not os.path.exists(f): continue
    for c in json.load(open(f)):
        c=dict(c); c["brand"]=brand_of(c); c.setdefault("country","US" if tag in("seed","mouseprint","tables") else c.get("country"))
        if tag=="seed":
            c.setdefault("evidence_type","news / advocacy report"); c.setdefault("confidence","high")
            if "Wikipedia" in c.get("source",""): c["evidence_type"]="reference work (Wikipedia list with primary citations)"; c["confidence"]="medium"
            cc={"(UK)":"UK","(Europe)":"EU","(Australia)":"AU"}
            for k,v in cc.items():
                if k in c["product"]: c["country"]=v
        c["unit"]=UNITS.get(c["unit"],c["unit"])
        c["source_tag"]=tag
        c["category"]=c.get("category") or "Other"
        key=(slugish(c["brand"]),round(float(c["before"]),2),round(float(c["after"]),2),c["unit"].split("/")[0][:5],c.get("country"))
        if key in out:
            o=out[key]
            if c["source_url"]!=o["source_url"] and c["source_url"] not in [a["url"] for a in o.setdefault("also_reported",[])]:
                o["also_reported"].append({"url":c["source_url"],"source":c["source"]})
            continue
        out[key]=c
FIX={"costcotuna":"Kirkland tuna (Costco)","tropicana":"Tropicana orange juice","Tide 84 oz to 80 oz":"Tide","Tostitos Hint of …":"Tostitos Hint of Guacamole","Turkey Hill ice cream changes":"Turkey Hill ice cream","Publix Baby Shampoo":"Johnson's Baby Shampoo"}
DROP={"Jif still 18 oz.","Cinemark 24 oz cup"}
CAT=[("Toilet Paper",r"toilet|bath tissue|toilettenpapier|charmin|cottonelle|quilted northern|angel soft|mega roll"),("Paper Towels",r"paper towel|küchenrolle|kitchen roll"),("Tissues",r"tissue|taschentücher|kleenex|kosmetikt|^puffs$|puffs (facial|tissue)"),
("Laundry",r"detergent|laundry|fabric|softener|waschmittel|weichspüler|downy|tide|gain|persil|comfort|vernel|ariel"),("Dish & Cleaning",r"dish|dawn|spülmittel|cleaner|reiniger|wipes|swiffer|febreze|lysol|somat|finish|jif cream|air fresh"),
("Oral Care",r"tooth|zahn|crest|colgate|listerine|mouthwash|aquafresh|sensodyne"),("Personal Care",r"shampoo|body wash|soap|duschgel|dusch|deodorant|deo|seife|lotion|creme|tresemme|dove body"),
("Coffee & Tea",r"coffee|kaffee|tea\b|tee\b|k-cups|nescaf|folgers|maxwell|peet|jacobs|pg tips"),("Juice & Drinks",r"juice|saft|orange juice|tropicana|simply orange|drink|gatorade|powerade|cola|limo|sirup|syrup|wasser|water|beer|bier|eistee"),
("Breakfast Cereals",r"cereal|flakes|müsli|muesli|granola|oats|cheerios|puffs|loops|crunch|chex|corn pops|bran|haferflocken|knusper"),("Chips & Snacks",r"chip|crisp|doritos|tostitos|pringles|cheetos|lay|pretzel|popcorn|snack|nuts|nüsse|erdnüsse|studenten|chex mix|goldfish|gold fish"),
("Chocolate & Candy",r"chocolate|schoko|candy|kisses|m&m|caramel|bonbon|praline|riegel|gummi|fruchtgummi|haribo|kitkat|milka|lindt|ritter|cadbury|hershey|rolo|reese|snickers|twix|mars|milky|quality street|celebrations|toblerone|smarties|lion|merci|toffifee|kinder|duplo|mints"),
("Cookies & Crackers",r"cookie|cracker|keks|biscuit|kekse|oreo|ritz|wheat thins|digestive|club|waffel|zwieback|breton|keebler"),("Ice Cream",r"ice cream|eis\b|frozen yogurt|magnum|breyers|häagen|haagen|ben & jerry|cremissimo|langnese"),
("Dairy",r"yogurt|joghurt|cheese|käse|butter|milch|milk|quark|sahne|cream cheese|margarine|spread|kiri"),("Meat & Fish",r"frank|hot dog|sausage|wurst|würstchen|schinken|ham|jambon|tuna|thunfisch|sardine|salmon|lachs|chicken|bacon"),
("Pasta, Rice & Meals",r"dips?\b|hummus|meat alternative|salami|mozzarella|veggie|vegan|fleisch|pasta|spaghetti|nudeln|rice|reis|dinner|mac|soup|suppe|pizza|meal|lasagne|salad|salat|taco|sauce|soße|gravy|ketchup|mayo|dressing|pesto|würz|gewürz|fix\b"),
("Baking & Spreads",r"cake mix|backmischung|flour|mehl|sugar|zucker|jam|marmelade|konfitüre|honey|honig|peanut butter|nutella|spread|aufstrich|syrup|pancake"),("Bread & Bakery",r"bread|brot|bagel|toast|brötchen|muffin|tart"),
("Pet Food",r"dog food|cat food|katzen|hunde|whiskas|iams|sheba|pedigree|purina|felix")]
CAT=[("Health & Supplements",r"gaviscon|lanacane|venen|zirkulin|curafit|taxofit|tetesept|kapseln|magnesium|biotin|billy boy|first aid|balm|einschlafen"),
("Tobacco & Alcohol",r"tabak|pall mall|glo neo|baileys|captain morgan|mojito|verpoort|winston|lancia|giants"),
("Frozen Foods",r"iglo|frosta|freeze pop|funpops|frutti di mare|prawns|kabeljau|deutsche see"),
("Household",r"spee|bref|pril|kreide|always|binde|slipeinlagen|pflegetücher|babydream|nagellack|rasierklingen|gillette"),
("Personal Care",r"nivea|maria nila|haarspray|elnett|head & shoulders|garnier|alverde|puder|skin stories|dr\. hauschka|gesichtsöl|rituals|scrub|beauty cream bar"),
("Chocolate & Candy",r"lebkuchen|vivani|marabou|kägi|katjes|trolli|winegums|gums|vitaminis|hitschies|yogurette|ferrero|nocciolata|feine bitter"),
("Dairy",r"halloumi|salakis|brunch|alpro|andros|zaziki|hirte|bedda|rama|lätta|becel|deli reform|zentis belmandel|natur$"),
("Coffee & Tea",r"teekanne|kakao|kaba|nesquik|suchard"),("Juice & Drinks",r"valensina|pepsi|bitter lemon|orancia|florida"),
("Breakfast Cereals",r"hearts & hoops|choco balls|clusters|cini minis"),("Baking & Spreads",r"sweet ‘n low|sesam|olivenöl|paprika|cocos|zetti|rote grütze|dessert|knorr|bouillon"),
("Meat & Fish",r"hering|beyond meat|protein chunks|beef jerky|jack links|lammsteak"),("Cookies & Crackers",r"marmor|kuchen|christmas cake|salzbrezeln|tuc|wasa"),("Pasta, Rice & Meals",r"lentil penne"),
("Pet Food",r"wolfsblut|trockenfutter"),("Baby",r"beba")]+CAT
for c in out.values():
    c["product"]=FIX.get(c["product"],c["product"]).replace("’","'")
    t=(c["product"]+" "+(c.get("category") or "")+" "+c.get("maker","")).lower()
    c["category"]=next((k for k,r in CAT if re.search(r,t)),"Other")
cases=[c for c in out.values() if c["product"] not in DROP]
CATFIX={'Meat & Fish': ['Revilla chorizo'], 'Tobacco & Alcohol': ['Peroni', 'Beck', 'La Trappe'], 'Dairy': ['Philadelphia Light', 'Blue Band', 'Vache Qui Rit', 'gruyere', 'Maaslander'], 'Personal Care': ['Pantene Pro-V Curl', 'Andrélon', 'Dove Deeply'], 'Juice & Drinks': ['Dixap'], 'Cookies & Crackers': ['Jodekoek', 'Gemberkoek', 'ontbijtkoek', 'Beschuit'], 'Breakfast Cereals': ['Zonnatura', "L'Atelier"], 'Laundry': ['Seepje', 'Vanish', 'Robijn', 'Dreft', 'Lenor'], 'Frozen Foods': ['diepvriescroissants'], 'Chips & Snacks': ['Multimix', 'Johnny Cashew', 'Eat Natural'], 'Chocolate & Candy': ['Van Melle', 'Sportlife', 'Klene', 'Mentos'], 'Pasta, Rice & Meals': ['Ananas stukjes'], 'Dish & Cleaning': ['vaatwastabletten'], 'Baby': ['Pampers'], 'Household': ['Ambi Pur'], 'Coffee & Tea': ['Dolce Gusto', 'Lipton']}
for c in cases:
    if c.get("category")=="Other":
        for k,v in CATFIX.items():
            if any(w.lower() in c["product"].lower() for w in v): c["category"]=k;break
for c in cases:
    if c["brand"]=="Puffs": c["category"]="Tissues"
json.dump(cases,open("data/cases.json","w"),indent=1,ensure_ascii=False)
import collections
print(len(cases),collections.Counter(c["source_tag"] for c in cases),collections.Counter(c["country"] for c in cases))
