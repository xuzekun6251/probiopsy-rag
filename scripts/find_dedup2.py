"""Print apipeline_enqueue_documents dedup logic."""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = open(r".venv/Lib/site-packages/lightrag/lightrag.py", encoding="utf-8").read()
m = re.search(r"def (apipeline_enqueue_documents|_enqueue_documents|apipeline_process_enqueueed_documents)", src)
if not m:
    # find any function mentioning doc_status content-hash filtering
    for mm in re.finditer(r"def (async )?\w*enqueue\w*", src):
        print("found:", mm.group(0))
    for mm in re.finditer(r"\.get\(doc_key\)|content_hash.*doc_status|doc_status.*content_hash", src):
        s = max(0, mm.start() - 300)
        print("---", mm.group(0), "---")
        print(src[s:mm.start() + 300])
        print()
else:
    print(src[m.start():m.start() + 4200])
