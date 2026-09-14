"""Vercel entrypoint for the single-project deployment. Vercel's Python runtime
gives a full ASGI app export (like this FastAPI `app`) native catch-all routing
under /api/* with no `rewrites` rule needed — a rewrite here was actively harmful:
once Vercel detects a Python function in the repo, it classifies the whole project
as a "backend framework project" and reinterprets rewrite destinations as internal
app routes, which broke serving the static frontend entirely.

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
