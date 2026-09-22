# -*- coding: utf-8 -*-
"""Poll Zenodo public API for the new record (temp, self-deleting)."""
import json
import sys
import time
import urllib.request

Q = "https://zenodo.org/api/records?q=%22probiopsy-rag%22&size=3"
for i in range(8):
    try:
        with urllib.request.urlopen(Q, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        total = data.get("hits", {}).get("total", 0)
        print(f"[{i}] total={total}")
        if total:
            for h in data["hits"]["hits"]:
                md = h.get("metadata", {})
                print("  title:", md.get("title", "")[:80])
                print("  doi:", h.get("doi"))
                print("  html:", h.get("links", {}).get("self_html"))
            sys.exit(0)
    except Exception as e:
        print(f"[{i}] error: {e}")
    time.sleep(20)
print("not indexed yet after ~2.5 min")
