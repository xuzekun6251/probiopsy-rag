# -*- coding: utf-8 -*-
"""Round 7: verify medical LLM-agent family DOIs (from PULSE paper reference list)."""
import io
import json
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = "probiopsy-rag-refcheck/1.0 (mailto:xuzekunurology@163.com)"

DOIS = {
    "pulse_af_agent":    "10.1038/s41746-026-03038-x",
    "wang_htn_agent":    "10.1161/HYPERTENSIONAHA.125.25305",
    "hao_pca_agent":     "10.1038/s41746-025-02166-0",
    "caread_agent":      "10.1038/s41746-025-01940-4",
    "geneagent":         "10.1038/s41592-025-02748-6",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


for key, doi in DOIS.items():
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    try:
        m = get(url)["message"]
        title = (m.get("title") or ["?"])[0][:100]
        jr = (m.get("container-title") or ["?"])[0][:45]
        year = (m.get("issued", {}).get("date-parts") or [[0]])[0][0]
        auth = m.get("author") or []
        first = auth[0].get("family", "?") if auth else "?"
        print(f"[{key}] OK: {first} {year} | {jr} | {title}")
        print(f"        vol={m.get('volume')} issue={m.get('issue')} pages={m.get('page')}")
    except Exception as e:
        print(f"[{key}] FAILED: {e}")
    time.sleep(1.0)
print("DONE")
