"""One-off connectivity check for DATABASE_URL. Prints only pass/fail and a
sanitized error class/message — never the connection string itself, even on
failure — so it's safe to run and share output from without leaking credentials."""

import re
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.settings import get_settings


def redact(message: str, secret_fragments: list[str]) -> str:
    for fragment in secret_fragments:
        if fragment:
            message = message.replace(fragment, "[REDACTED]")
    return message


def main() -> int:
    settings = get_settings()
    url = settings.database_url

    if url.startswith("sqlite"):
        print("DATABASE_URL is still set to the local SQLite default — nothing to test against Supabase.")
        return 1

    # Extract the password so we can scrub it from any error text before printing.
    password_match = re.search(r"://[^:]+:([^@]+)@", url)
    password = password_match.group(1) if password_match else ""

    print(f"Testing connection to host: {re.sub(r'://.*@', '://[REDACTED]@', url)}")

    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
        print("SUCCESS: connected and ran a test query.")
        print(f"Postgres version: {result}")
        return 0
    except SQLAlchemyError as e:
        safe_message = redact(str(e), [password, url])
        print(f"FAILED: {type(e).__name__}: {safe_message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
