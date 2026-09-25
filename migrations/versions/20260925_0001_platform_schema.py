"""Add platform entities, prediction snapshots and synchronization metadata."""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect, text

from mundasense.storage.models import Base

revision = "20260925_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("assessments")}
    additions = {
        "updated_at": "TEXT NOT NULL DEFAULT ''",
        "sync_status": "TEXT NOT NULL DEFAULT 'synchronized'",
        "idempotency_key": "TEXT",
        "archived": "BOOLEAN NOT NULL DEFAULT 0",
        "field_id": "TEXT",
    }
    for name, definition in additions.items():
        if name not in columns:
            bind.execute(text(f"ALTER TABLE assessments ADD COLUMN {name} {definition}"))
    bind.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_assessments_idempotency "
            "ON assessments(idempotency_key)"
        )
    )
    bind.execute(
        text(
            "UPDATE assessments SET updated_at = created_at "
            "WHERE updated_at IS NULL OR updated_at = ''"
        )
    )


def downgrade() -> None:
    for name in (
        "app_settings",
        "sync_events",
        "model_metadata",
        "prediction_results",
        "fields",
        "farms",
    ):
        op.execute(text(f"DROP TABLE IF EXISTS {name}"))
