# -*- coding: utf-8 -*-
"""Round 2: exact DOI lookups + PubMed second-source confirmation for chosen refs."""
import io
import json
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = "probiopsy-rag-refcheck/1.0 (mailto:xuzekunurology@163.com)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


# --- Crossref DOI resolution for two unresolved candidates -------------------
CROSSREF_QUERIES = [
    ("aua_part2_2022",
     "Clinically Localized Prostate Cancer AUA ASTRO Guideline Part II "
     "Treatment Journal of Urology 2022"),
    ("bryant_proba_2025",
     "Local anaesthetic transperineal biopsy versus transrectal prostate "
     "biopsy in prostate cancer Bryant Lancet Oncology"),
]

for key, q in CROSSREF_QUERIES:
    print("=" * 100)
    print(f"[{key}]")
    url = ("https://api.crossref.org/works?rows=3&select=DOI,title,"
           "container-title,issued,author,volume,page&query.bibliographic="
           + urllib.parse.quote(q))
    try:
        for i, it in enumerate(get(url)["message"]["items"]):
            title = (it.get("title") or ["?"])[0][:100]
            jr = (it.get("container-title") or ["?"])[0][:40]
            year = (it.get("issued", {}).get("date-parts") or [[0]])[0][0]
            auth = it.get("author") or []
            first = auth[0].get("family", "?") if auth else "?"
            print(f"  CR{i+1}: {first} {year} | {jr} | {title}")
            print(f"       DOI {it['DOI']} vol={it.get('volume')} pages={it.get('page')}")
    except Exception as e:
        print(f"  FAILED: {e}")
    time.sleep(1.2)

# --- PubMed second-source confirmation (title searches) ----------------------
PUBMED_QUERIES = {
    "eastham_aua_part1": "Clinically Localized Prostate Cancer AUA/ASTRO "
                         "Guideline Part I Introduction Risk Assessment[ti]",
    "aua_amend_2026": "Clinically Localized Prostate Cancer AUA/ASTRO "
                      "Guideline Amendment[ti]",
    "aua_part2_2022": "Clinically Localized Prostate Cancer AUA/ASTRO "
                      "Guideline Part II Treatment[ti]",
    "borghesi_2017": "Complications After Systematic Random and Image-guided "
                     "Prostate Biopsy[ti]",
    "bryant_proba_2025": "Local anaesthetic transperineal biopsy versus "
                         "transrectal prostate biopsy[ti]",
    "epstein_concord_2012": "Upgrading and Downgrading of Prostate Cancer from "
                            "Biopsy to Radical Prostatectomy[ti]",
    "park_pirads_2020": "Interreader Agreement with Prostate Imaging Reporting "
                        "and Data System Version 2[ti]",
    "liss_proph_2015": "Comparative Effectiveness of Targeted vs Empirical "
                       "Antibiotic Prophylaxis to Prevent Sepsis[ti]",
}

print("=" * 100)
for key, q in PUBMED_QUERIES.items():
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
           f"?db=pubmed&term={urllib.parse.quote(q)}&retmax=3&retmode=json")
    try:
        ids = get(url).get("esearchresult", {}).get("idlist", [])
        if not ids:
            print(f"[{key}] PubMed: NO HITS")
            continue
        sm = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                 f"?db=pubmed&id={','.join(ids)}&retmode=json")
        for pid in ids:
            d = sm.get("result", {}).get(pid, {})
            print(f"[{key}] PMID {pid}: {d.get('sortfirstauthor','?')} "
                  f"{d.get('pubdate','?')[:4]} | {d.get('source','?')} | "
                  f"{d.get('volume','?')}:{d.get('pages','?')} | "
                  f"{d.get('title','?')[:80]}")
    except Exception as e:
        print(f"[{key}] PubMed FAILED: {e}")
    time.sleep(1.2)
print("=" * 100)
print("DONE")
