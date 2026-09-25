from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select

from mundasense.storage.database import Database
from mundasense.storage.models import (
    AppSettingRecord,
    FarmRecord,
    FieldRecord,
    SyncEventRecord,
    record_dict,
)


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class CatalogRepository:
    def __init__(self, database: Database):
        self.database = database
        self.database.initialise()

    def create_farm(self, values: dict[str, Any]) -> dict[str, Any]:
        farm_id = str(values.get("id") or uuid4())
        with self.database.session() as session:
            existing = session.get(FarmRecord, farm_id)
            if existing:
                return {**record_dict(existing), "field_count": self._field_count(session, farm_id)}
            timestamp = str(values.get("created_at") or now_iso())
            record = FarmRecord(
                id=farm_id,
                name=values["name"],
                contact_name=values.get("contact_name", ""),
                province=values["province"],
                district=values["district"],
                ward=values.get("ward", ""),
                latitude=values.get("latitude"),
                longitude=values.get("longitude"),
                notes=values.get("notes", ""),
                created_at=timestamp,
                updated_at=str(values.get("updated_at") or timestamp),
                sync_status=values.get("sync_status", "synchronized"),
                is_demo=bool(values.get("is_demo", False)),
            )
            session.add(record)
            session.flush()
            return {**record_dict(record), "field_count": 0}

    @staticmethod
    def _field_count(session, farm_id: str) -> int:
        return int(
            session.scalar(select(func.count(FieldRecord.id)).where(FieldRecord.farm_id == farm_id))
            or 0
        )

    def list_farms(self) -> list[dict[str, Any]]:
        with self.database.session() as session:
            records = session.scalars(select(FarmRecord).order_by(FarmRecord.name)).all()
            return [
                {**record_dict(item), "field_count": self._field_count(session, item.id)}
                for item in records
            ]

    def get_farm(self, farm_id: str) -> dict[str, Any] | None:
        with self.database.session() as session:
            record = session.get(FarmRecord, farm_id)
            if not record:
                return None
            return {**record_dict(record), "field_count": self._field_count(session, farm_id)}

    def create_field(self, values: dict[str, Any]) -> dict[str, Any]:
        field_id = str(values.get("id") or uuid4())
        with self.database.session() as session:
            existing = session.get(FieldRecord, field_id)
            if existing:
                return record_dict(existing)
            if not session.get(FarmRecord, values["farm_id"]):
                raise LookupError("Farm not found")
            timestamp = str(values.get("created_at") or now_iso())
            record = FieldRecord(
                id=field_id,
                farm_id=values["farm_id"],
                name=values["name"],
                size_hectares=float(values["size_hectares"]),
                maize_variety=values.get("maize_variety", ""),
                planting_date=values.get("planting_date"),
                season=values.get("season", "2025/26"),
                target_yield_t_ha=values.get("target_yield_t_ha"),
                notes=values.get("notes", ""),
                created_at=timestamp,
                updated_at=str(values.get("updated_at") or timestamp),
                sync_status=values.get("sync_status", "synchronized"),
                is_demo=bool(values.get("is_demo", False)),
            )
            session.add(record)
            session.flush()
            return record_dict(record)

    def list_fields(self, farm_id: str | None = None) -> list[dict[str, Any]]:
        statement = select(FieldRecord).order_by(FieldRecord.name)
        if farm_id:
            statement = statement.where(FieldRecord.farm_id == farm_id)
        with self.database.session() as session:
            return [record_dict(item) for item in session.scalars(statement).all()]

    def get_field(self, field_id: str) -> dict[str, Any] | None:
        with self.database.session() as session:
            record = session.get(FieldRecord, field_id)
            return record_dict(record) if record else None

    def get_sync_event(self, idempotency_key: str) -> dict[str, Any] | None:
        with self.database.session() as session:
            record = session.scalar(
                select(SyncEventRecord).where(SyncEventRecord.idempotency_key == idempotency_key)
            )
            return record_dict(record) if record else None

    def record_sync_event(
        self,
        *,
        idempotency_key: str,
        entity_type: str,
        entity_id: str,
        status: str,
        request: dict[str, Any],
        response: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self.get_sync_event(idempotency_key)
        if existing:
            return existing
        timestamp = now_iso()
        with self.database.session() as session:
            record = SyncEventRecord(
                id=str(uuid4()),
                idempotency_key=idempotency_key,
                entity_type=entity_type,
                entity_id=entity_id,
                status=status,
                request_json=json.dumps(request, ensure_ascii=False, sort_keys=True, default=str),
                response_json=json.dumps(response, ensure_ascii=False, sort_keys=True, default=str),
                created_at=timestamp,
                updated_at=timestamp,
            )
            session.add(record)
            session.flush()
            return record_dict(record)

    def set_setting(self, key: str, value: Any) -> None:
        with self.database.session() as session:
            record = session.get(AppSettingRecord, key)
            if record:
                record.value_json = json.dumps(value, ensure_ascii=False)
                record.updated_at = now_iso()
            else:
                session.add(
                    AppSettingRecord(
                        key=key,
                        value_json=json.dumps(value, ensure_ascii=False),
                        updated_at=now_iso(),
                    )
                )

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self.database.session() as session:
            value = session.scalar(
                select(AppSettingRecord.value_json).where(AppSettingRecord.key == key)
            )
        return json.loads(value) if value is not None else default

    def delete_setting(self, key: str) -> None:
        with self.database.session() as session:
            record = session.get(AppSettingRecord, key)
            if record:
                session.delete(record)
