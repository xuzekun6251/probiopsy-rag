import glob
import json

for jp in sorted(glob.glob("outputs/demo_cases/case*.json")):
    d = json.load(open(jp, encoding="utf-8"))
    print(d["case_id"], "elapsed_s =", d.get("elapsed_s"),
          "action =", d["verdict"]["action"],
          "degraded =", d["verdict"].get("degraded"))
