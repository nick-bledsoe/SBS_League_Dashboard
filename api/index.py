"""Vercel entrypoint for the single-project deployment. Vercel auto-detects any
Python file under a root-level api/ folder as a serverless function and looks for
a module-level `app` (ASGI) object here.

The actual backend package lives in backend/app/ (kept there for local dev: the
usual `cd backend && uvicorn app.main:app` workflow is untouched). Its internal
imports are all written as `from app.xxx import yyy`, assuming `app` is directly
importable — so we add backend/ to sys.path here rather than duplicating the
whole package under api/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402,F401
