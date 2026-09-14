from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.settings import get_settings

settings = get_settings()

if settings.database_url.startswith("sqlite"):
    # SQLite (local dev): one file, one process — SQLAlchemy's default pool is fine,
    # just needs the classic check_same_thread escape hatch for FastAPI's threadpool.
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
else:
    # Postgres via Supabase's pooler (Supavisor), used in serverless deployment: each
    # function invocation is short-lived, so NullPool disables SQLAlchemy's own client-side
    # pooling and lets every request open/close a connection through the pooler instead —
    # the recommended pattern for serverless + an external transaction-mode pooler.
    engine = create_engine(settings.database_url, poolclass=NullPool, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
