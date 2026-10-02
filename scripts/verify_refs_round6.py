# -*- coding: utf-8 -*-
"""Verify candidate references via Crossref API + PubMed E-utilities (two sources).

Prints top Crossref hits per candidate and matching PubMed PMIDs so the exact
DOI can be selected. NO reference is added to the manuscript unless both
sources agree on title/journal/year.
"""
import io
import json
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = "probiopsy-rag-refcheck/1.0 (mailto:xuzekunurology@163.com)"

CANDIDATES = [
    ("eastham_aua2023",
     "Clinically Localized Prostate Cancer AUA ASTRO SUO Guideline Part I "
     "Staging Risk Assessment Role of Active Surveillance Eastham"),
    ("morgans_aua2023",
     "Clinically Localized Prostate Cancer AUA ASTRO SUO Guideline Part II "
     "Morgans"),
    ("borghesi_comp2017",
     "Complications and adverse events of systematic random and image-guided "
     "prostate biopsy Borghesi European Urology"),
    ("nossiter_tps_trs",
     "Transrectal versus transperineal prostate biopsy adverse events hospital "
     "admissions national database Nossiter"),
    ("epstein_concord2012",
     "Upgrading and downgrading of prostate cancer from biopsy to radical "
     "prostatectomy incidence predictive factors modified Gleason Epstein"),
    ("pirads_agreement",
     "interreader agreement Prostate Imaging Reporting and Data System "
     "version 2 meta-analysis"),
    ("cussans_raid",
     "targeted antibiotic prophylaxis sepsis transrectal prostate biopsy "
     "multicentre quality improvement RAID"),
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


for key, query in CANDIDATES:
    print("=" * 100)
    print(f"[{key}] {query[:80]}...")
    # 1) Crossref bibliographic
    cr_url = ("https://api.crossref.org/works?rows=3&select=DOI,title,"
              "container-title,issued,author,volume,page,type&query.bibliographic="
              + urllib.parse.quote(query))
    try:
        data = get(cr_url)
        for i, it in enumerate(data["message"]["items"]):
            title = (it.get("title") or ["?"])[0][:95]
            jr = (it.get("container-title") or ["?"])[0][:40]
            year = (it.get("issued", {}).get("date-parts") or [[0]])[0][0]
            auth = it.get("author") or []
            first = f"{auth[0].get('family','?')}" if auth else "?"
            print(f"  CR{i+1}: {first} {year} | {jr} | {title}")
            print(f"       DOI {it['DOI']} vol={it.get('volume')} "
                  f"pages={it.get('page')} type={it.get('type')}")
    except Exception as e:
        print(f"  Crossref FAILED: {e}")
    # 2) PubMed esearch (title-ish terms, first 8 words)
    pm_terms = " AND ".join(query.split()[:9])
    es_url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
              f"?db=pubmed&term={urllib.parse.quote(pm_terms)}&retmax=3&retmode=json")
    try:
        es = get(es_url)
        ids = es.get("esearchresult", {}).get("idlist", [])
        if ids:
            sm = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                     f"?db=pubmed&id={','.join(ids)}&retmode=json")
            for pid in ids:
                d = sm.get("result", {}).get(pid, {})
                print(f"  PMID {pid}: {d.get('sortfirstauthor','?')} "
                      f"{d.get('pubdate','?')[:4]} | {d.get('source','?')} | "
                      f"{d.get('title','?')[:90]}")
        else:
            print("  PubMed: no hits")
    except Exception as e:
        print(f"  PubMed FAILED: {e}")
    time.sleep(1.2)
print("=" * 100)
print("DONE")
