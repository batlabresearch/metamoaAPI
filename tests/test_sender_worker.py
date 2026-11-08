"""Check timing without network requests or real sleeps."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('worker', Path(__file__).resolve().parents[1] / 'scripts/metamoa_sender_worker.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


class Clock:
    def __init__(self):
        self.now = 1000.0
        self.sends = []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds

    def send(self):
        self.sends.append(self.now)
        self.now += 2  # Account for the request duration.

    def run(self, duration, due=0):
        return worker.run_loop(duration, due, clock=self.time, sleep=self.sleep, send=self.send)


class TimingTests(unittest.TestCase):
    def test_repeated_sends_wait_after_request_completion(self):
        clock = Clock()
        clock.run(1300)
        self.assertEqual(clock.sends, [1000, 1602, 2204])

    def test_handoff_preserves_interval(self):
        clock = Clock()
        due = clock.run(60)
        self.assertEqual(clock.sends, [1000])
        clock.run(650, due)
        self.assertEqual(clock.sends, [1000, 1602])

    def test_worker_finishing_before_due_does_not_send(self):
        clock = Clock()
        due = clock.run(60, 1700)
        self.assertEqual(clock.sends, [])
        self.assertEqual(due, 1700)


if __name__ == '__main__':
    unittest.main()
