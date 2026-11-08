"""Run the sender every ten minutes, handing its next due time to the next job."""

import argparse
from datetime import datetime, timezone, timedelta
import math
import os
from pathlib import Path
import subprocess
import sys
import time

INTERVAL = 600
KST = timezone(timedelta(hours=9))


def send_once():
    script = Path(__file__).with_name('send_metamoa.py')
    try:
        result = subprocess.run([sys.executable, '-u', str(script)], timeout=90)
        if result.returncode:
            print(f'::warning::Sender failed (exit {result.returncode}); next attempt in ten minutes.', flush=True)
    except subprocess.TimeoutExpired:
        print('::warning::Sender timed out; next attempt in ten minutes.', flush=True)


def run_loop(duration, not_before=0, *, clock=time.time, sleep=time.sleep, send=send_once):
    deadline = clock() + duration
    due = max(clock(), not_before)
    while clock() < deadline:
        if due > clock():
            stamp = datetime.fromtimestamp(due, KST).isoformat(timespec='seconds')
            print(f'Next send: {stamp}', flush=True)
            sleep(min(due - clock(), max(0, deadline - clock())))
        if clock() >= deadline:
            break
        stamp = datetime.fromtimestamp(clock(), KST).isoformat(timespec='seconds')
        print(f'Sending latest file value at {stamp}', flush=True)
        send()
        # Wait a full interval after completion, including failures/timeouts.
        due = clock() + INTERVAL
    return due


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-minutes', type=int, default=300)
    parser.add_argument('--not-before', type=float, default=0)
    args = parser.parse_args()
    if not 1 <= args.run_minutes <= 300:
        parser.error('--run-minutes must be between 1 and 300')
    if not math.isfinite(args.not_before) or args.not_before < 0:
        parser.error('--not-before must be a finite nonnegative Unix timestamp')
    print(f'Sender worker started: interval={INTERVAL}s; duration={args.run_minutes}min', flush=True)
    due = run_loop(args.run_minutes * 60, args.not_before)
    output = os.environ.get('GITHUB_OUTPUT')
    if output:
        with open(output, 'a', encoding='utf-8') as stream:
            stream.write(f'next_send_at={math.ceil(due)}\n')
    print('Worker complete; the workflow will hand off to its successor.', flush=True)


if __name__ == '__main__':
    main()
