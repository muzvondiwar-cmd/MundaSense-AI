from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class Base(DeclarativeBase):
    pass


class FarmRecord(Base):
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    contact_name: Mapped[str] = mapped_column(String(120), default="")
    province: Mapped[str] = mapped_column(String(80), index=True)
    district: Mapped[str] = mapped_column(String(80), index=True)
    ward: Mapped[str] = mapped_column(String(80), default="")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)
    sync_status: Mapped[str] = mapped_column(String(24), default="synchronized", index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class FieldRecord(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    size_hectares: Mapped[float] = mapped_column(Float)
    maize_variety: Mapped[str] = mapped_column(String(100), default="")
    planting_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    season: Mapped[str] = mapped_column(String(30), default="2025/26")
    target_yield_t_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)
    sync_status: Mapped[str] = mapped_column(String(24), default="synchronized", index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class AssessmentRecord(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[str] = mapped_column(String(40), index=True)
    crop: Mapped[str] = mapped_column(String(30))
    district: Mapped[str] = mapped_column(String(80), index=True)
    farm_reference: Mapped[str] = mapped_column(String(80))
    inputs_json: Mapped[str] = mapped_column(Text)
    predicted_yield_t_ha: Mapped[float] = mapped_column(Float)
    interval_lower_t_ha: Mapped[float] = mapped_column(Float)
    interval_upper_t_ha: Mapped[float] = mapped_column(Float)
    risk_code: Mapped[str] = mapped_column(String(16), index=True)
    confidence_code: Mapped[str] = mapped_column(String(20))
    warnings_json: Mapped[str] = mapped_column(Text)
    drivers_json: Mapped[str] = mapped_column(Text)
    advisories_json: Mapped[str] = mapped_column(Text)
    referral_required: Mapped[bool] = mapped_column(Boolean)
    model_version: Mapped[str] = mapped_column(String(80))
    rules_version: Mapped[str] = mapped_column(String(80))
    is_synthetic_model: Mapped[bool] = mapped_column(Boolean)
    app_version: Mapped[str] = mapped_column(String(40))
    result_json: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)
    sync_status: Mapped[str] = mapped_column(String(24), default="synchronized", index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    field_id: Mapped[str | None] = mapped_column(
        ForeignKey("fields.id", ondelete="SET NULL"), nullable=True, index=True
    )

    __table_args__ = (Index("uq_assessments_idempotency", "idempotency_key", unique=True),)


class PredictionRecord(Base):
    __tablename__ = "prediction_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), unique=True, index=True
    )
    prediction_timestamp: Mapped[str] = mapped_column(String(40))
    predicted_yield_t_ha: Mapped[float] = mapped_column(Float)
    lower_yield_t_ha: Mapped[float] = mapped_column(Float)
    upper_yield_t_ha: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(16))
    confidence: Mapped[str] = mapped_column(String(20))
    drivers_json: Mapped[str] = mapped_column(Text)
    warnings_json: Mapped[str] = mapped_column(Text)
    recommendations_json: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(80))
    is_demo_model: Mapped[bool] = mapped_column(Boolean)


class ModelMetadataRecord(Base):
    __tablename__ = "model_metadata"

    version: Mapped[str] = mapped_column(String(80), primary_key=True)
    model_type: Mapped[str] = mapped_column(String(120))
    data_status: Mapped[str] = mapped_column(String(120))
    metadata_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class SyncEventRecord(Base):
    __tablename__ = "sync_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[str] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(String(24), index=True)
    request_json: Mapped[str] = mapped_column(Text)
    response_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)


class AppSettingRecord(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value_json: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso)


def record_dict(record: Base) -> dict[str, Any]:
    return {column.name: getattr(record, column.name) for column in record.__table__.columns}
