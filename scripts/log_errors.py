"""Extract error/degraded lines from the phase4 build log."""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

lines = open("outputs/phase4_build_log.txt", encoding="utf-8", errors="ignore").read().splitlines()
errs = [l for l in lines if ("degraded" in l.lower() or "error" in l.lower()
                             or "empty" in l.lower() or "WARNING" in l)]
print(f"{len(errs)} error-ish lines (of {len(lines)}):")
for l in errs[-25:]:
    print("  ", l[:220])
