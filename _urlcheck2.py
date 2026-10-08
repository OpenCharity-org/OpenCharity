import json, re, csv, urllib.request, socket
from concurrent.futures import ThreadPoolExecutor, as_completed
socket.setdefaulttimeout(12)
rows = list(csv.DictReader(open("charities_by_country_v2.csv")))
url2c = {}
for r in rows:
    for u in re.findall(r"https?://[^\s;|,]+", r["Sources"]):
        u = u.rstrip(".")
        url2c.setdefault(u, set()).add(r["Country"])

def clean(u):
    u = u.rstrip(".,;]")
    if u.count("(") > u.count(")"):
        u = u[:u.rfind("(")]
    if u.count("[") > u.count("]"):
        u = u[:u.rfind("[")]
    return u.rstrip(" ()[]")

url2c2 = {clean(u): url2c[u] for u in url2c}
# merge any cleaned-to-same
merged = {}
for u, cs in url2c2.items():
    merged.setdefault(u, set()).update(cs)
urls = sorted(merged)
json.dump(urls, open("_all_urls2.json","w"), indent=1)

def check(u):
    req = urllib.request.Request(u, method="GET", headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept":"text/html,*/*"})
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read(512); return u, resp.status, None
    except urllib.error.HTTPError as e:
        return u, e.code, None
    except Exception as e:
        return u, None, type(e).__name__

bad = []
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = {ex.submit(check, u): u for u in urls}
    for f in as_completed(futs):
        u, code, err = f.result()
        if code is not None and code >= 400:
            bad.append({"url":u,"status":code,"countries":sorted(merged[u])})
        elif code is None:
            bad.append({"url":u,"status":None,"error":err,"countries":sorted(merged[u])})
json.dump(bad, open("_urlcheck2.json","w"), indent=1)
s404=[b for b in bad if b["status"]==404]; s4=[b for b in bad if b["status"] and 400<=b["status"]<500 and b["status"]!=404]
s5=[b for b in bad if b["status"] and b["status"]>=500]; ne=[b for b in bad if b["status"] is None]
print(f"unique cleaned URLs: {len(urls)}")
print(f"  404: {len(s404)} | 4xx: {len(s4)} | 5xx: {len(s5)} | net-err: {len(ne)}")
print("--- 404 ---")
for b in s404: print(f"  {b['url'][:95]}  [{', '.join(b['countries'])}]")
print("--- 4xx ---")
for b in s4: print(f"  {b['status']} {b['url'][:90]}  [{', '.join(b['countries'])[:40]}]")
print("--- 5xx ---")
for b in s5: print(f"  {b['status']} {b['url'][:90]}  [{', '.join(b['countries'])[:40]}]")
print("--- net-err ---")
for b in ne: print(f"  {b['error']} {b['url'][:85]}  [{', '.join(b['countries'])[:40]}]")
