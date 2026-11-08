#!/usr/bin/env python3
"""GitHub 실행기에서 7분 간격으로 값을 갱신합니다."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parent
INTERVAL_SECONDS = 7 * 60
KST = timezone(timedelta(hours=9))


def next_due(latest_path, now):
    """실행 교체 시에도 마지막 확인 시각으로부터 7분 간격을 유지합니다."""
    try:
        latest = json.loads(Path(latest_path).read_text(encoding="utf-8"))
        checked = datetime.strptime(latest["checked_at_kst"], "%Y-%m-%d %H:%M:%S")
        return max(now, checked.replace(tzinfo=KST).timestamp() + INTERVAL_SECONDS)
    except (OSError, ValueError, KeyError, TypeError):
        return now


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, timeout=120)


def publish():
    git("pull", "--rebase", "origin", "main")
    subprocess.run([sys.executable, "metamoa_top5.py"], cwd=ROOT, check=True, timeout=120)
    git("add", "data/", "metamoaAPI.txt")
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, timeout=30)
    if diff.returncode == 0:
        return
    if diff.returncode != 1:
        raise RuntimeError("git diff failed")
    stamp = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    git("commit", "-m", f"4개 공간 최대값 자동 갱신 {stamp}")
    for attempt in range(3):
        try:
            git("push", "origin", "HEAD:main")
            return
        except subprocess.CalledProcessError:
            if attempt == 2:
                raise
            git("pull", "--rebase", "origin", "main")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-minutes", type=int, default=300)
    args = parser.parse_args()
    if not 1 <= args.run_minutes <= 300:
        parser.error("--run-minutes must be between 1 and 300")

    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "41898283+github-actions[bot]@users.noreply.github.com")
    end = time.monotonic() + args.run_minutes * 60
    due = next_due(ROOT / "data" / "latest.json", time.time())
    print(f"GitHub worker started: interval={INTERVAL_SECONDS}s, run={args.run_minutes}min", flush=True)
    while time.monotonic() < end:
        wait = max(0, due - time.time())
        if wait:
            target = datetime.fromtimestamp(due, KST).isoformat(timespec="seconds")
            print(f"Next update: {target}", flush=True)
            time.sleep(min(wait, max(0, end - time.monotonic())))
        if time.monotonic() >= end:
            break
        succeeded = False
        for attempt in range(3):
            try:
                publish()
                succeeded = True
                break
            except (subprocess.SubprocessError, RuntimeError) as error:
                print(f"Update attempt {attempt + 1} failed: {error}", flush=True)
                if attempt < 2:
                    time.sleep(min(15, max(0, end - time.monotonic())))
        if succeeded:
            latest = json.loads((ROOT / "data" / "latest.json").read_text(encoding="utf-8"))
            print(f"Published: {latest['checked_at_kst']} value={latest['value']}", flush=True)
            summary = os.environ.get("GITHUB_STEP_SUMMARY")
            if summary:
                with open(summary, "a", encoding="utf-8") as f:
                    f.write(f"- {latest['checked_at_kst']} KST: {latest['name']} {latest['online']}명, 최종값 **{latest['value']}**\n")
            due = next_due(ROOT / "data" / "latest.json", time.time())
        else:
            due = time.time() + INTERVAL_SECONDS
    print("Worker finished; the workflow will start its successor.", flush=True)


if __name__ == "__main__":
    main()
