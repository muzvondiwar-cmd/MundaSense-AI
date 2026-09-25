"""Vercel entrypoint for the MundaSense FastAPI application."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure_serverless_runtime() -> None:
    """Expose the src layout and select writable fallback storage."""
    source_dir = Path(__file__).resolve().parents[1] / "src"
    if str(source_dir) not in sys.path:
        sys.path.insert(0, str(source_dir))
    if os.getenv("VERCEL") and not os.getenv("MUNDASENSE_DATABASE_URL"):
        os.environ.setdefault("MUNDASENSE_DATABASE_PATH", "/tmp/mundasense.sqlite3")


_configure_serverless_runtime()

from backend.main import app as app  # noqa: E402
