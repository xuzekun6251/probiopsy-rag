import re

t = open("data/raw/ProBIOPSY_consensus_main.txt", encoding="utf-8").read()[:6000]
for pat in ("doi", "DOI", "10.1016", "Eur Urol", "ProBIOPSY"):
    hits = [l.strip() for l in t.splitlines() if pat in l][:3]
    if hits:
        print(pat, "->", hits)
head = re.sub(r"\s+", " ", t[:1200])
print("---HEAD---")
print(head)
