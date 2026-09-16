"""Check retry timing distribution in the current build log."""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
lines = open("outputs/phase4_build_log.txt", encoding="utf-8", errors="ignore").read().splitlines()
idx = [i for i, l in enumerate(lines) if "Retrying request" in l]
print(f"retry positions (of {len(lines)} lines): {idx[-15:]}")
print("last 8 lines:")
for l in lines[-8:]:
    print("  ", l[:160])
