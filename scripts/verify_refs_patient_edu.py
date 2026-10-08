# -*- coding: utf-8 -*-
"""Find consensus ref number + PubMed-verify HGPIN/ASAP anchor sources (temp).

Outputs PMIDs with full esummary metadata; prints candidate selection.
"""
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

# --- 1. consensus ref number
order = json.load(open("outputs/paper/refs_order.json", encoding="utf-8"))
for n, key in enumerate(order, 1):
    if "probiopsy" in key or "chernysheva" in key or "consensus" in key:
        print(f"consensus key: {key} -> ref [{n}]")

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def esearch(term, retmax=8):
    url = (EUTILS + "esearch.fcgi?db=pubmed&retmode=json&retmax=" + str(retmax)
           + "&term=" + urllib.parse.quote(term))
    with urllib.request.urlopen(url, timeout=45) as r:
        return json.load(r)["esearchresult"]["idlist"]


def esummary(pmids):
    url = (EUTILS + "esummary.fcgi?db=pubmed&retmode=json&id="
           + ",".join(pmids))
    with urllib.request.urlopen(url, timeout=45) as r:
        data = json.load(r)["result"]
        return [data[u] for u in data["uids"]]


queries = {
    "ASAP_repeat": ('"atypical small acinar proliferation" AND ("repeat biopsy" OR '
                    '"early repeat") AND prostate', 2020),
    "HGPIN_extended": ('"high-grade prostatic intraepithelial neoplasia" AND '
                       '("extended biopsy" OR "repeat biopsy")', 2018),
}
for name, (term, ymin) in queries.items():
    print(f"\n=== {name}: {term}")
    try:
        pmids = esearch(term)
    except Exception as e:
        print("  ESEARCH FAILED:", e)
        continue
    if not pmids:
        print("  no hits")
        continue
    for d in esummary(pmids):
        year = d.get("pubdate", "")[:4]
        doi = next((a["value"] for a in d.get("articleids", []) if a["idtype"] == "doi"), "")
        print(f"  PMID {d.get('uid')} | {year} | {d.get('source')} | "
              f"{d.get('title','')[:110]} | doi:{doi}")
