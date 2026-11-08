#!/usr/bin/env python3
"""네 공간의 현재 접속자 수 중 최댓값으로 최종 정수를 계산합니다."""
import csv
import json
import os
import random
import urllib.request
from datetime import datetime, timezone, timedelta

BASE = "https://metamoa.com/api"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
SPACE_IDS = (
    "sansa-temple",
    "gatbawi-online",
    "korulive-com-mw0jtwgu",
    "metabus-fortunecafe-kr-mw1p2ecl",
)
KST = timezone(timedelta(hours=9))

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "metamoa-top5-logger"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    payload = get("/spaces")
    by_id = {s["id"]: s for s in payload["spaces"]}
    sources = []
    for space_id in SPACE_IDS:
        space = by_id.get(space_id)
        if space is None:
            raise ValueError(f"공간 항목을 찾을 수 없습니다: {space_id}")
        online = space.get("online")
        if type(online) is not int or online < 0:
            raise ValueError(f"현재 접속자 수가 올바르지 않습니다: {space_id}={online!r}")
        sources.append({"id": space_id, "name": space.get("name", space_id),
                        "online": online, "online_at": space.get("online_at")})
    space = max(sources, key=lambda s: s["online"])
    online = space["online"]

    extra = random.randint(-5, 5)
    # floor(online * 0.9 + extra)를 정수 연산으로 계산해 부동소수점 오차를 피합니다.
    result = online * 9 // 10 + extra
    ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    latest = {
        "checked_at_kst": ts,
        "source_url": BASE + "/spaces",
        "source_built_at": payload.get("built_at"),
        "spaces": sources,
        "space_id": space["id"],
        "name": space["name"],
        "online": online,
        "max_online": online,
        "online_at": space.get("online_at"),
        "random_digit": extra,
        "random_range": [-5, 5],
        "formula": "floor(max_online * 0.9 + random_digit)",
        "value": result,
    }

    os.makedirs(DATA, exist_ok=True)
    history = os.path.join(DATA, "four_spaces.csv")
    new = not os.path.exists(history)
    with open(history, "a", newline="", encoding="utf-8-sig" if new else "utf-8") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["확인시각(KST)", "산사", "갓바위", "코루라이브", "온라인신당", "최대공간id", "최대접속자수", "랜덤숫자", "최종값"])
        writer.writerow([ts, *(s["online"] for s in sources), space["id"], online, extra, result])

    value = f"{result}\n"
    for path in (os.path.join(ROOT, "metamoaAPI.txt"), os.path.join(DATA, "random.txt")):
        with open(path, "w", encoding="utf-8") as f:
            f.write(value)
    with open(os.path.join(DATA, "numbers.txt"), "w", encoding="utf-8") as f:
        f.write(",".join(str(s["online"]) for s in sources) + "\n")
    with open(os.path.join(DATA, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)

    print(f"[{ts}] " + ", ".join(f"{s['name']}={s['online']}명" for s in sources))
    print(f"최대: {space['name']} {online}명 × 0.9 + {extra} → {result}")


if __name__ == "__main__":
    main()
