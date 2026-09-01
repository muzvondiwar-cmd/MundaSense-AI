from __future__ import annotations

APP_VERSION = "0.1.0"
MODEL_BUNDLE_SCHEMA_VERSION = "1.0"
MODEL_VERSION = "demo-2026.08-v1"
RISK_POLICY_VERSION = "risk-demo-v1"
RULES_VERSION = "advisory-demo-v1"
DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "sn")

FEATURE_SPEC = {
    "rainfall_mm": {
        "display_key": "field.rainfall",
        "unit": "mm / assessment season",
        "required": True,
        "hard_min": 0.0,
        "hard_max": 2_000.0,
        "example": 650.0,
    },
    "fertilizer_kg_ha": {
        "display_key": "field.fertilizer",
        "unit": "kg/ha recorded application",
        "required": True,
        "hard_min": 0.0,
        "hard_max": 1_000.0,
        "example": 120.0,
    },
    "temperature_c": {
        "display_key": "field.temperature",
        "unit": "°C seasonal mean",
        "required": True,
        "hard_min": -10.0,
        "hard_max": 60.0,
        "example": 24.0,
    },
    "humidity_pct": {
        "display_key": "field.humidity",
        "unit": "% seasonal mean",
        "required": True,
        "hard_min": 0.0,
        "hard_max": 100.0,
        "example": 62.0,
    },
    "soil_ph": {
        "display_key": "field.soil_ph",
        "unit": "pH",
        "required": True,
        "hard_min": 0.0,
        "hard_max": 14.0,
        "example": 6.2,
    },
}

FEATURE_ORDER = tuple(FEATURE_SPEC)
