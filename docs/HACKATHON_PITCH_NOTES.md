# HACK4AFRICA pitch notes

## One-line pitch

MundaSense AI turns five accessible seasonal observations into an explainable maize yield-risk
picture, highlights unreliable data and gives one cautious next step—even when the field team has no
continuous internet connection.

## Problem

Farmers and extension officers often make time-sensitive decisions with fragmented rainfall,
management and soil information. A bare prediction is not enough: people need to see uncertainty,
why the model responded, whether the data look unusual and when a human specialist should review the
case.

## Differentiators

- Offline-first PWA and local Python inference; no cloud account or paid API.
- Explainable result with yield range, risk score, confidence meaning, drivers and input-quality
  warnings on one screen.
- Honest offline queue: no JavaScript substitute and no fake result.
- Immutable, versioned result snapshots for traceability.
- Guarded, rules-based next actions instead of generated agronomic prescriptions.
- Farmer/mobile and extension/dashboard workflows in the same deployable system.
- Synthetic/demo provenance is visible in records and aggregates.

## Architecture in 20 seconds

React/TypeScript and Dexie form the installable offline PWA. FastAPI/Pydantic exposes `/api/v1`.
SQLAlchemy/Alembic persist SQLite snapshots and idempotent sync events. A checksum-verified
scikit-learn pipeline performs local prediction; a separate deterministic advisory engine limits
recommendations.

## Claims we can make

- The included held-out metrics are genuinely calculated on deterministic synthetic data.
- Identical inputs produce deterministic output for the bundled model.
- The application works without internet after installation; disconnected submissions wait for the
  local Python service.
- The system detects configured out-of-range inputs and lowers confidence/refers cases.
- Tests cover balanced, water-stress, unusual inputs, API behavior, persistence and idempotent sync.

## Claims we must not make

- Do not claim field accuracy, farmer impact, validated Zimbabwe-wide thresholds or causal effects.
- Do not call confidence a probability or validated accuracy.
- Do not promise yield or prescribe fertiliser/pesticide rates.
- Do not present named synthetic districts as observed district evidence.

## Responsible close

MundaSense AI is a decision-support prototype. Before scale deployment it needs consented and
representative field data, supervised agronomic validation, bilingual review, calibrated local
thresholds, security hardening and a governed pilot with extension partners.

## Next investment priorities

1. Partner-led Zimbabwe field data collection and data-governance protocol.
2. Prospective validation across agro-ecological regions and seasons.
3. Local weather-station ingestion with provenance and missingness handling.
4. Role-based access, encrypted backup and managed PostgreSQL deployment.
5. Shona usability testing and extension-officer training materials.
