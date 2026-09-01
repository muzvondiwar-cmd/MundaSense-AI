from __future__ import annotations

REQUIRED_COLUMNS = (
    "record_id",
    "crop",
    "district",
    "season",
    "rainfall_mm",
    "fertilizer_kg_ha",
    "temperature_c",
    "humidity_pct",
    "soil_ph",
    "yield_t_ha",
    "data_source",
    "is_synthetic",
)

NUMERIC_COLUMNS = (
    "rainfall_mm",
    "fertilizer_kg_ha",
    "temperature_c",
    "humidity_pct",
    "soil_ph",
    "yield_t_ha",
)

TARGET_COLUMN = "yield_t_ha"

