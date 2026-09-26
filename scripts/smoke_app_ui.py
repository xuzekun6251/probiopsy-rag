# -*- coding: utf-8 -*-
"""Headless full-script execution of streamlit_app v3 via streamlit.testing.AppTest.

Executes main() → all 5 tabs render (tabs execute on every run), catches any
runtime exception. Does NOT click through LLM-triggering buttons.
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from streamlit.testing.v1 import AppTest

at = AppTest.from_file(r"D:\Zcode测试文件夹\测试3\app\streamlit_app.py", default_timeout=300)
at.run()

if at.exception:
    for ex in at.exception:
        print("EXCEPTION:", ex.value)
        print(ex.stack_trace if hasattr(ex, "stack_trace") else "")
    sys.exit(1)
print("AppTest run OK — no exceptions")
print("tabs rendered:", len(at.tabs))
print("errors (st.error calls):", [e.value[:120] for e in at.error])
print("warnings:", [w.value[:120] for w in at.warning])
