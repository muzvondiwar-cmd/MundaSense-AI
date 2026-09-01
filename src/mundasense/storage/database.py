from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS assessments (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    crop TEXT NOT NULL,
    district TEXT NOT NULL,
    farm_reference TEXT NOT NULL,
    inputs_json TEXT NOT NULL,
    predicted_yield_t_ha REAL NOT NULL,
    interval_lower_t_ha REAL NOT NULL,
    interval_upper_t_ha REAL NOT NULL,
    risk_code TEXT NOT NULL,
    confidence_code TEXT NOT NULL,
    warnings_json TEXT NOT NULL,
    drivers_json TEXT NOT NULL,
    advisories_json TEXT NOT NULL,
    referral_required INTEGER NOT NULL,
    model_version TEXT NOT NULL,
    rules_version TEXT NOT NULL,
    is_synthetic_model INTEGER NOT NULL,
    app_version TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assessments_risk ON assessments(risk_code);
CREATE INDEX IF NOT EXISTS idx_assessments_district ON assessments(district);
"""


class Database:
    def __init__(self, path: Path):
        self.path = path

    def initialise(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA_SQL)
            connection.commit()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
        finally:
            connection.close()

    def readiness(self) -> tuple[bool, str]:
        try:
            self.initialise()
            with self.connect() as connection:
                connection.execute("SELECT 1").fetchone()
            return True, "database is writable"
        except sqlite3.Error as exc:
            return False, f"database error: {exc}"
