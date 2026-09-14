"""Vercel's Python runtime looks for a module-level `app` (ASGI) object here and
routes all requests to it per vercel.json. The actual FastAPI app and all its logic
live in app/main.py — this file is deployment wiring only, nothing else."""

from app.main import app  # noqa: F401
