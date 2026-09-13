#!/usr/bin/env python
"""Run the skill's citation hard gate with the project .env loaded.

The skill's verify_rule_citations.py does not load .env itself, but its LLM
relevance layer needs HUANYU_BULK_* (GLM-5.3) in the process environment.
This wrapper exports .env into os.environ (without overriding existing vars)
and then execs the gate via runpy, forwarding all extra CLI args.

Usage:
    .venv/Scripts/python.exe scripts/run_citation_gate.py [--fix] [--no-llm] ...
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = Path(r"C:\Users\31291\.zcode\skills\medical-agent-executor\scripts\verify_rule_citations.py")


def main() -> int:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

    sys.argv = [str(GATE), "--project-root", str(ROOT)] + sys.argv[1:]
    try:
        runpy.run_path(str(GATE), run_name="__main__")
    except SystemExit as e:
        code = e.code
        return int(code) if isinstance(code, int) else (0 if code is None else 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
