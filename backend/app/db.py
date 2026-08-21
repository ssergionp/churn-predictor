import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

# load_dotenv() never overrides a variable already present in the process
# environment (override=False is the default) - if DATABASE_URL is set
# somewhere else (shell profile, system env var, docker-compose
# `environment:`), that value wins over backend/.env silently.
_was_already_set = "DATABASE_URL" in os.environ
_env_file_found = load_dotenv(ENV_PATH)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy backend/.env.example to backend/.env "
        "and adjust it, or export DATABASE_URL directly."
    )


def _normalize_database_url(url: str) -> str:
    """Rewrites the bare `postgres://`/`postgresql://` schemes that hosting
    providers (Render, Heroku, etc.) hand out to `postgresql+psycopg://`, so
    SQLAlchemy picks the psycopg (v3) driver instead of defaulting to
    psycopg2. Any other scheme (sqlite, an already-qualified
    postgresql+..., etc.) is left untouched.

    Values pasted into a platform's dashboard env var field (as opposed to
    read from backend/.env, which python-dotenv already trims) can carry
    incidental leading/trailing whitespace or mixed case, either of which
    would make a plain `.startswith()` check silently miss - so both are
    normalized away before matching the scheme.
    """
    stripped = url.strip()
    lowered = stripped.lower()
    for scheme in ("postgres://", "postgresql://"):
        if lowered.startswith(scheme):
            return "postgresql+psycopg://" + stripped[len(scheme) :]
    return stripped


DATABASE_URL = _normalize_database_url(DATABASE_URL)


def _mask_database_url(url: str) -> str:
    """Replaces the password in a DB URL with **** for safe logging."""
    parts = urlsplit(url)
    if parts.password is None:
        return url
    userinfo = f"{parts.username or ''}:****"
    netloc = f"{userinfo}@{parts.hostname or ''}"
    if parts.port:
        netloc += f":{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


if _was_already_set:
    _source = "the OS environment (already set before backend/.env was read - it wins over the file)"
elif _env_file_found:
    _source = str(ENV_PATH)
else:
    _source = f"nowhere - {ENV_PATH} was not found and no env var was set"

print(f"[db] DATABASE_URL loaded from: {_source}")
print(f"[db] DATABASE_URL effective value: {_mask_database_url(DATABASE_URL)}")

if DATABASE_URL.startswith("sqlite"):
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
