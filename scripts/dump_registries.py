"""Dump unique A flags and B ids from the seed registries."""
import csv
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

rows = list(csv.DictReader(open("data/seed/entities_a.csv", encoding="utf-8-sig")))
flags = set()
for r in rows:
    flags.update((r.get("flags") or "").split("|"))
flags.discard("")
print("A rows:", len(rows), "| unique flags:", len(flags))
print(sorted(flags))
print()
brows = list(csv.DictReader(open("data/seed/entities_b.csv", encoding="utf-8-sig")))
print("B rows:", len(brows))
for r in brows:
    print(f"  {r['entity_b_id']}  | {r['flags']}  | {r['generic_name'][:60]}")
