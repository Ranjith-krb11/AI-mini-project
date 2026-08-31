import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

logger = logging.getLogger(__name__)

# Primary database URL from configuration (PostgreSQL)
db_url = settings.DATABASE_URL

# Fallback: if PostgreSQL isn't running or reachable during local development,
# gracefully use SQLite so the developer can run immediately without friction.
try:
    if db_url.startswith("postgresql"):
        # Test connecting or prepare engine
        engine = create_engine(db_url, pool_pre_ping=True)
        # Try a quick connection test
        with engine.connect() as conn:
            pass
    else:
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
        )
except Exception as e:
    logger.warning(
        f"PostgreSQL connection to '{db_url}' failed: {e}. "
        "Falling back to local SQLite database at data/app.db for local development."
    )
    os.makedirs(os.path.join(os.getcwd(), "data"), exist_ok=True)
    sqlite_path = os.path.join(os.getcwd(), "data", "app.db")
    db_url = f"sqlite:///{sqlite_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates all database tables defined in models."""
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
