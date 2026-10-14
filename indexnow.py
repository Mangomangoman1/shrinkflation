#!/usr/bin/env python3
"""Submit all sitemap URLs to IndexNow (Bing, Yandex, etc.). Run after publish once the key file is live."""
import json,pathlib,re,urllib.request
R=pathlib.Path(__file__).parent; key=(R/"indexnow_key.txt").read_text().strip()
urls=re.findall(r"<loc>(.*?)</loc>",(R/"site/sitemap.xml").read_text())
body=json.dumps({"host":"shrinkradar.com","key":key,"keyLocation":f"https://shrinkradar.com/{key}.txt","urlList":urls}).encode()
r=urllib.request.urlopen(urllib.request.Request("https://api.indexnow.org/indexnow",data=body,headers={"Content-Type":"application/json; charset=utf-8"}),timeout=30)
print("IndexNow",r.status,len(urls),"urls")
