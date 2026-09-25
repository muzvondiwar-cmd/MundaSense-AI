# MundaSense AI API

The primary base URL is `http://127.0.0.1:8000/api/v1`. OpenAPI documentation is available at
`http://127.0.0.1:8000/docs`. JSON bodies are limited to 32 KiB.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Model, database, rules and offline-asset readiness |
| GET | `/config?language=en` | Feature contract, units and versions |
| GET | `/model/info` | Model type, synthetic metrics, ranges and limitations |
| GET | `/demo-scenarios` | Balanced, water-stressed and unusual presets |
| DELETE | `/demo-data` | Remove only demo/scenario assessments; preserve manual records |
| GET | `/dashboard/summary` | Filtered KPIs, trend data, drivers and alerts |
| GET/POST | `/farms` | List or create farms |
| GET/POST | `/fields` | List or create fields; `farm_id` filters the list |
| GET/POST | `/assessments` | List snapshots or create/predict/persist one |
| GET | `/assessments/{assessment_id}` | Retrieve an immutable result snapshot |
| PATCH | `/assessments/{assessment_id}/archive` | Remove a record from active views without deletion |
| POST | `/predictions` | Validate and predict without persistence |
| POST | `/scenarios/compare` | Compare overrides against a saved baseline without mutation |
| POST | `/sync/batch` | Idempotently synchronize queued farm, field or assessment records |
| GET | `/insights` | Local portfolio analytics and data-quality summary |

Compatibility endpoints below `/api` continue to provide CSV export, printable reports and the
original assessment transport.

## Assessment request

The five model values are required. Context values are stored for reproducibility but are not silently
fed to a model that was not trained to use them.

```json
{
  "crop": "maize",
  "rainfall_mm": 690,
  "fertilizer_kg_ha": 125,
  "temperature_c": 24,
  "humidity_pct": 63,
  "soil_ph": 6.2,
  "season": "2025/26",
  "district": "Goromonzi",
  "farm_reference": "North Block",
  "field_id": "20000000-0000-4000-8000-000000000001",
  "province": "Mashonaland East",
  "ward": "12",
  "planting_date": "2025-11-20",
  "maize_variety": "Demo medium-season variety",
  "growth_stage": "Vegetative",
  "field_size_hectares": 2.4,
  "fertilizer_type": "",
  "irrigation_available": false,
  "crop_stress_observations": "",
  "language": "en",
  "source": "manual"
}
```

Send a stable `Idempotency-Key` header for retried create requests. Repeating the key returns the
first stored assessment rather than running and storing a duplicate.

## Prediction contract

`POST /predictions` returns the required typed summary plus the complete presentation result:

```json
{
  "predicted_yield_t_ha": 3.11,
  "yield_range_t_ha": { "lower": 2.10, "upper": 4.12 },
  "risk_score": 38.5,
  "risk_level": "low",
  "confidence": "medium",
  "confidence_explanation": "Deterministic policy using interval width and input familiarity.",
  "top_drivers": [],
  "warnings": [],
  "recommended_next_actions": [],
  "model_version": "demo-2026.08-v1",
  "is_demo_model": true,
  "full_result": {}
}
```

The risk score is a transparent concern scale derived from provisional yield thresholds; it is not a
probability. Confidence is not accuracy. Drivers are associations, not causal proof.

## Batch synchronization

```json
{
  "items": [
    {
      "entity_type": "assessment",
      "idempotency_key": "7f8467c6-1227-4b0c-b5b0-535bdfbcd596",
      "payload": { "crop": "maize", "rainfall_mm": 690 }
    }
  ]
}
```

Each item receives `synchronized` or `failed`. A repeated successful key has `duplicate=true` and the
same `entity_id`. One bad record does not block unrelated batch items.

## Filters

History supports `search`, `risk`, `confidence`, `district`, `field`, `season`, `referral`,
`data_status`, `from_date`, `to_date` and `sort`. Dashboard supports province, district, field,
season, risk, confidence, referral, data status and dates. Province is applied through the farm
catalogue in the UI; historical snapshots retain district even if farm metadata later changes.

## Error envelope

Versioned endpoints return predictable errors:

```json
{
  "error": {
    "code": "request_validation_error",
    "message": "One or more request values are invalid.",
    "details": []
  }
}
```

No normal API response includes a Python stack trace.
