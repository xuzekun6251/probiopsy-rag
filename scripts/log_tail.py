"""Show the tail of the current build log with error lines."""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
lines = open("outputs/phase4_build_log.txt", encoding="utf-8", errors="ignore").read().splitlines()
print(f"total {len(lines)} lines; last 30:")
for l in lines[-30:]:
    print("  ", l[:170])
