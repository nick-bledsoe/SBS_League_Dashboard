from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.db.session import Base, engine
from app.routers import matchups, meta, players, playoff_matchups, standings, stats, teams, transactions

configure_logging()
settings = get_settings()

app = FastAPI(title="SBS League Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# Called at import time (not via an @app.on_event("startup") lifespan hook) since
# Vercel's serverless Python runtime doesn't reliably fire ASGI lifespan events —
# this way schema creation runs on cold start regardless. create_all() is a no-op
# for tables that already exist, so this is safe to run on every cold start.
Base.metadata.create_all(bind=engine)

app.include_router(meta.router, prefix="/api")
app.include_router(standings.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(matchups.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(playoff_matchups.router, prefix="/api")
app.include_router(players.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
