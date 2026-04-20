r"""Simple performance smoke test: simulate concurrent login attempts.

Usage (from project root):
    .\.venv\Scripts\python.exe scripts\perf_test_logins.py --users 1000 --workers 100
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "src" / "back end"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from controllers.auth_controller import AuthController  # noqa: E402


VALID_ACCOUNTS = [
    ("admin", "admin123"),
    ("gv01", "gv123"),
    ("gv02", "gv123"),
    ("sv01", "sv123"),
    ("sv02", "sv123"),
    ("sv03", "sv123"),
]


def _try_login(auth: AuthController, username: str, password: str) -> bool:
    return auth.authenticate(username, password) is not None


def run_test(total_users: int, workers: int, invalid_ratio: float) -> int:
    auth = AuthController()

    ok = 0
    fail = 0
    lock = threading.Lock()

    start = time.perf_counter()

    def task(i: int) -> bool:
        nonlocal ok, fail
        try:
            # Inject a small ratio of invalid logins to mimic real traffic.
            if invalid_ratio > 0 and (i % max(1, int(1 / invalid_ratio)) == 0):
                success = _try_login(auth, "unknown", "wrong")
            else:
                u, p = VALID_ACCOUNTS[i % len(VALID_ACCOUNTS)]
                success = _try_login(auth, u, p)
        except Exception:
            success = False
        with lock:
            if success:
                ok += 1
            else:
                fail += 1
        return success

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(task, i) for i in range(total_users)]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception:
                with lock:
                    fail += 1

    elapsed = time.perf_counter() - start
    rps = total_users / elapsed if elapsed > 0 else 0.0

    print("=" * 62)
    print("LOGIN PERFORMANCE SMOKE TEST")
    print("=" * 62)
    print(f"Total requests : {total_users}")
    print(f"Workers        : {workers}")
    print(f"Success        : {ok}")
    print(f"Failed         : {fail}")
    print(f"Counted total  : {ok + fail}")
    print(f"Elapsed (sec)  : {elapsed:.3f}")
    print(f"Throughput req/s: {rps:.2f}")
    print("=" * 62)

    # Non-zero exit if all failed, useful for CI smoke checks.
    return 0 if ok > 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Concurrent login smoke test")
    parser.add_argument("--users", type=int, default=1000,
                        help="Total login attempts (default: 1000)")
    parser.add_argument("--workers", type=int, default=100,
                        help="Concurrent workers (default: 100)")
    parser.add_argument("--invalid-ratio", type=float, default=0.1,
                        help="Fraction of invalid attempts [0..1] (default: 0.1)")
    args = parser.parse_args()

    users = max(1, args.users)
    workers = max(1, min(args.workers, users))
    invalid_ratio = min(1.0, max(0.0, args.invalid_ratio))
    return run_test(users, workers, invalid_ratio)


if __name__ == "__main__":
    raise SystemExit(main())
