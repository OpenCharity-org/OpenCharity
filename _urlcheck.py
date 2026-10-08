import json, re, csv, urllib.request, socket
from concurrent.futures import ThreadPoolExecutor, as_completed
socket.setdefaulttimeout(12)
urls = json.load(open("_all_urls.json"))
rows = list(csv.DictReader(open("charities_by_country_v2.csv")))
url2c = {}
for r in rows:
    for u in re.findall(r"https?://[^\s;|,)]+", r["Sources"]):
        url2c.setdefault(u.rstrip("."), set()).add(r["Country"])

def check(u):
    req = urllib.request.Request(u, method="GET", headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept":"text/html,*/*"})
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read(512)
            return u, resp.status, None
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
            bad.append({"url": u, "status": code, "countries": sorted(url2c[u])})
        elif err and code is None:
            bad.append({"url": u, "status": None, "error": err, "countries": sorted(url2c[u])})
json.dump(bad, open("_urlcheck_results.json","w"), indent=1)
http404 = [b for b in bad if b.get("status")==404]
http4xx = [b for b in bad if b.get("status") and 400<=b["status"]<500 and b["status"]!=404]
http5xx = [b for b in bad if b.get("status") and b["status"]>=500]
neterr  = [b for b in bad if b.get("status") is None]
print(f"checked {len(urls)} unique URLs")
print(f"  404: {len(http404)}   other 4xx: {len(http4xx)}   5xx: {len(http5xx)}   network/TLS/timeout: {len(neterr)}")
for b in http404: print("  404:", b["url"][:90], "|", ", ".join(b["countries"])[:40])
