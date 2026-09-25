from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from mundasense.storage.models import Base


class Database:
    """SQLAlchemy database boundary with a SQLite default and PostgreSQL-ready URL support."""

    def __init__(self, path: Path | str):
        raw = str(path)
        is_url = raw.startswith(("sqlite:", "postgresql:"))
        self.path = Path(".") if is_url else Path(path)
        self.url = raw if is_url else f"sqlite+pysqlite:///{self.path.resolve().as_posix()}"
        if self.url.startswith("sqlite") and not is_url:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine: Engine = create_engine(
            self.url,
            future=True,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False, "timeout": 10}
            if self.url.startswith("sqlite")
            else {},
        )
        if self.url.startswith("sqlite"):

            @event.listens_for(self.engine, "connect")
            def _sqlite_pragmas(dbapi_connection, _connection_record) -> None:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.close()

        self._session_factory = sessionmaker(
            bind=self.engine, class_=Session, expire_on_commit=False, future=True
        )

    def initialise(self) -> None:
        Base.metadata.create_all(self.engine)
        self._upgrade_legacy_assessments()
        if self.url.startswith("sqlite"):
            with self.engine.begin() as connection:
                connection.execute(text("PRAGMA journal_mode = WAL"))
                connection.execute(text("PRAGMA foreign_keys = ON"))

    def _upgrade_legacy_assessments(self) -> None:
        """Keep pre-SQLAlchemy local databases readable before Alembic is run."""
        inspector = inspect(self.engine)
        if "assessments" not in inspector.get_table_names():
            return
        columns = {item["name"] for item in inspector.get_columns("assessments")}
        additions = {
            "updated_at": "TEXT NOT NULL DEFAULT ''",
            "sync_status": "TEXT NOT NULL DEFAULT 'synchronized'",
            "idempotency_key": "TEXT",
            "archived": "BOOLEAN NOT NULL DEFAULT 0",
            "field_id": "TEXT",
        }
        with self.engine.begin() as connection:
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(
                        text(f"ALTER TABLE assessments ADD COLUMN {name} {definition}")
                    )
            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_assessments_idempotency "
                    "ON assessments(idempotency_key)"
                )
            )
            connection.execute(
                text(
                    "UPDATE assessments SET updated_at = created_at "
                    "WHERE updated_at IS NULL OR updated_at = ''"
                )
            )

    @contextmanager
    def session(self) -> Iterator[Session]:
        current = self._session_factory()
        try:
            yield current
            current.commit()
        except Exception:
            current.rollback()
            raise
        finally:
            current.close()

    def readiness(self) -> tuple[bool, str]:
        try:
            self.initialise()
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True, f"{self.engine.dialect.name} database is writable"
        except (OSError, SQLAlchemyError) as exc:  # pragma: no cover - environment failure path
            return False, f"database error: {exc}"
