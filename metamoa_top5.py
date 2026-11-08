#!/usr/bin/env python3
"""산사의 현재 접속자 수로 최종 정수 값을 계산해 저장합니다."""
import csv
import json
import os
import random
import urllib.request
from datetime import datetime, timezone, timedelta

BASE = "https://metamoa.com/api"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
SPACE_ID = "sansa-temple"
KST = timezone(timedelta(hours=9))

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "metamoa-top5-logger"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    payload = get("/spaces")
    space = next((s for s in payload["spaces"] if s["id"] == SPACE_ID), None)
    if space is None:
        raise ValueError("산사 항목을 찾을 수 없습니다.")
    online = space.get("online")
    if type(online) is not int or online < 0:
        raise ValueError(f"산사의 현재 접속자 수가 올바르지 않습니다: {online!r}")

    extra = random.randint(0, 9)
    # 양수에 대해 int(online * 0.9 + extra)와 같으며 부동소수점 오차를 피합니다.
    result = online * 9 // 10 + extra
    ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    latest = {
        "checked_at_kst": ts,
        "source_url": BASE + "/spaces",
        "source_built_at": payload.get("built_at"),
        "space_id": SPACE_ID,
        "name": space.get("name", SPACE_ID),
        "online": online,
        "online_at": space.get("online_at"),
        "random_digit": extra,
        "formula": "floor(online * 0.9 + random_digit)",
        "value": result,
    }

    os.makedirs(DATA, exist_ok=True)
    history = os.path.join(DATA, "sansa.csv")
    new = not os.path.exists(history)
    with open(history, "a", newline="", encoding="utf-8-sig" if new else "utf-8") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["확인시각(KST)", "id", "이름", "현재접속자수", "접속자수갱신시각(UTC)", "랜덤숫자", "최종값"])
        writer.writerow([ts, SPACE_ID, latest["name"], online, latest["online_at"], extra, result])

    value = f"{result}\n"
    for path in (os.path.join(ROOT, "metamoaAPI.txt"), os.path.join(DATA, "random.txt")):
        with open(path, "w", encoding="utf-8") as f:
            f.write(value)
    with open(os.path.join(DATA, "numbers.txt"), "w", encoding="utf-8") as f:
        f.write(f"{online}\n")
    with open(os.path.join(DATA, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)

    print(f"[{ts}] 산사 {online}명 × 0.9 + {extra} → {result}")


if __name__ == "__main__":
    main()
