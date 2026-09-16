"""Duty-cycled build supervisor for the Zhipu quota-depletion pattern.

Empirical behavior (2026-09, glm-5.3-flash bulk extraction):
  - ~20-30 min of sustained load → account quota window depletes → calls HANG
    (server-side queueing) → LLM_CALL_BUDGET aborts → docs fail fast;
  - after a cooldown with zero traffic, the full rate returns.

This supervisor therefore cycles: timed build run → doc_status reset →
cooldown → repeat, until every evidence chunk is 'processed', then one final
uninterrupted pass (all dedup-skipped) writes stats, runs the smoke query and
marks executor.phase4 complete.

Usage: py scripts/build_supervisor.py [--max-cycles 12] [--run-sec 1200]
                                      [--cool-sec 1500]
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DS_PATH = ROOT / "data" / "processed" / "lightrag_index" / "kv_store_doc_status.json"
LOG = ROOT / "outputs" / "phase4_supervisor_log.txt"
EXPECT_TOTAL = 357


def log(msg: str) -> None:
    line = f"[supervisor {time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def processed_count() -> tuple[int, dict]:
    try:
        ds = json.loads(DS_PATH.read_text(encoding="utf-8"))
        c = Counter(v.get("status") for v in ds.values())
        return c.get("processed", 0), dict(c)
    except FileNotFoundError:
        return 0, {}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--max-cycles", type=int, default=12)
    ap.add_argument("--run-sec", type=int, default=1200)   # 20 min build window
    ap.add_argument("--cool-sec", type=int, default=1500)  # 25 min cooldown
    args = ap.parse_args()

    venv_py = str(ROOT / ".venv" / "Scripts" / "python.exe")
    build_script = str(ROOT / "scripts" / "build_lightrag_index.py")
    reset_script = str(ROOT / "scripts" / "reset_doc_status.py")

    env = dict(os.environ)
    env.update({
        "LLM_MIN_INTERVAL": "8",      # gentle pace: 7.5 RPM start cap
        "LIGHTRAG_MAX_ASYNC": "1",    # serial — fewer wasted tokens when depleted
        "LLM_CALL_BUDGET": "90",      # hang-abort fast in depleted windows
    })

    n, dist = processed_count()
    log(f"start: processed={n}/{EXPECT_TOTAL} dist={dist}")

    for cycle in range(1, args.max_cycles + 1):
        n, dist = processed_count()
        if n >= EXPECT_TOTAL:
            break
        log(f"cycle {cycle}: build window {args.run_sec}s (processed={n})")
        try:
            subprocess.run(
                [venv_py, build_script],
                cwd=str(ROOT), env=env,
                timeout=args.run_sec,
                check=False,
            )
        except subprocess.TimeoutExpired:
            log(f"cycle {cycle}: build window expired (killed — progress banked)")
        except Exception as e:
            log(f"cycle {cycle}: build error: {e}")

        # re-enable docs that did not finish this window
        subprocess.run([venv_py, reset_script], cwd=str(ROOT), check=False)
        n, dist = processed_count()
        log(f"cycle {cycle}: after reset processed={n} dist={dist}")
        if n >= EXPECT_TOTAL:
            break
        log(f"cycle {cycle}: cooldown {args.cool_sec}s")
        time.sleep(args.cool_sec)

    n, dist = processed_count()
    if n < EXPECT_TOTAL:
        log(f"NOT complete after {args.max_cycles} cycles: processed={n}/{EXPECT_TOTAL}")
        return 1

    # final uninterrupted pass: everything dedup-skips, merges flush, stats +
    # smoke query + phase4 marking run inside the build script
    log(f"final pass (processed={n}); running full build to completion")
    r = subprocess.run([venv_py, build_script], cwd=str(ROOT), env=env, check=False)
    log(f"final pass exit={r.returncode}")
    stats = ROOT / "outputs" / "lightrag_build_stats.json"
    log(f"stats file exists: {stats.exists()}")
    return 0 if r.returncode == 0 else r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
