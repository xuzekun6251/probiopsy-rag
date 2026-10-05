# -*- coding: utf-8 -*-
"""Verify Yaoshi-RAG citation via Crossref."""
import io
import json
import sys
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = "probiopsy-rag-refcheck/1.0 (mailto:xuzekunurology@163.com)"
url = "https://api.crossref.org/works/" + urllib.parse.quote("10.2196/75279")
req = urllib.request.Request(url, headers={"User-Agent": UA})
with urllib.request.urlopen(req, timeout=40) as r:
    m = json.loads(r.read().decode())["message"]
title = (m.get("title") or ["?"])[0][:120]
jr = (m.get("container-title") or ["?"])[0][:45]
year = (m.get("issued", {}).get("date-parts") or [[0]])[0][0]
auth = m.get("author") or []
first = auth[0].get("family", "?") if auth else "?"
print(f"OK: {first} {year} | {jr} | {title}")
print(f"   vol={m.get('volume')} pages={m.get('page')} type={m.get('type')}")
