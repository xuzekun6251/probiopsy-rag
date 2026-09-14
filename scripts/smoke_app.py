"""Import-level smoke: streamlit app module + pipeline + registries resolve."""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "app"))

# streamlit app imports `streamlit` — guard: only test if installed
try:
    import streamlit_app  # noqa
    print("streamlit_app import: OK")
except ImportError as e:
    print(f"streamlit missing (app not smoke-tested here): {e}")
except Exception as e:
    print(f"streamlit_app import FAILED: {type(e).__name__}: {e}")
    sys.exit(1)

from probiopsy_rag_agent.pipeline import load_assets, build_question  # noqa
assets = load_assets()
print(f"assets: rules={len(assets.rules)} items={len(assets.items)} "
      f"pfrs={len(assets.pfrs)} chunks={len(assets.store.chunks)}")
q = build_question(["d_route_transperineal"], assets.items)
print("build_question:", q[:100])
print("PIPELINE SMOKE OK")
