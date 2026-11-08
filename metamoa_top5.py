#!/usr/bin/env python3
"""메타모아 랭킹 '지금 인기' 1~5위 접속수를 한 번 확인해 data/metamoa_top5.csv 에 추가합니다."""
import csv, json, os, random, urllib.request
from datetime import datetime, timezone, timedelta

BASE = "https://metamoa.com/api"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "metamoa_top5.csv")
KST = timezone(timedelta(hours=9))

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "metamoa-top5-logger"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

rk = get("/rankings")
names = {s["id"]: s.get("name", s["id"]) for s in get("/spaces").get("spaces", [])}
ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
rows = [(ts, i, it["id"], names.get(it["id"], it["id"]), it["n"], rk.get("built_at"))
        for i, it in enumerate(rk["now"][:5], 1)]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
new = not os.path.exists(OUT)
with open(OUT, "a", newline="", encoding="utf-8-sig" if new else "utf-8") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["확인시각(KST)", "순위", "id", "이름", "접속수", "랭킹갱신시각(UTC)"])
    w.writerows(rows)

# 5위~1위 사이 랜덤 숫자 (양 끝 포함) -> data/random.txt
lo, hi = sorted((rows[4][4], rows[0][4]))
with open(os.path.join(os.path.dirname(OUT), "random.txt"), "w", encoding="utf-8") as f:
    f.write(f"{random.randint(lo, hi)}\n")

# 최신 값만 담은 파일 (http 주소로 바로 볼 용도)
d = os.path.dirname(OUT)
with open(os.path.join(d, "numbers.txt"), "w", encoding="utf-8") as f:
    f.write(",".join(str(r[4]) for r in rows) + "\n")
with open(os.path.join(d, "latest.json"), "w", encoding="utf-8") as f:
    json.dump({"checked_at_kst": ts, "ranking_built_at": rk.get("built_at"),
               "top5": [{"rank": r[1], "id": r[2], "name": r[3], "n": r[4]} for r in rows]},
              f, ensure_ascii=False, indent=2)

print(f"[{ts}]")
for _, i, _, name, n, _ in rows:
    print(f"  {i}위 {n:>5}명  {name}")
