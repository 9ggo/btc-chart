# 미국 비트코인 현물 ETF 일별 순유입(백만 달러)을 Farside에서 받아 etf.json으로 저장
import json, re, sys, datetime, html, urllib.request

URL = "https://farside.co.uk/bitcoin-etf-flow-all-data/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"

def num(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", s)).strip().replace(",", "")
    if s in ("", "-"): return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try: v = float(s)
    except ValueError: return None
    return -v if neg else v

req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept": "text/html", "Accept-Language": "en-US,en;q=0.9"})
page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
rows = []
for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
    if len(cells) < 3: continue
    d = html.unescape(re.sub(r"<[^>]+>", "", cells[0])).strip()
    try: day = datetime.datetime.strptime(d, "%d %b %Y").date()
    except ValueError: continue
    total = num(cells[-1])
    if total is None: continue   # 아직 집계 안 된 날
    rows.append({"date": day.isoformat(), "total": total})
if not rows:
    sys.exit("no rows parsed")
rows.sort(key=lambda r: r["date"])
out = {"source": "Farside Investors", "unit": "USD million", "updated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"), "rows": rows[-60:]}
json.dump(out, open("etf.json", "w"), ensure_ascii=False, indent=1)
print("last", rows[-1])
