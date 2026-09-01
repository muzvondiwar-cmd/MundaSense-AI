# Architecture

## Decision

MundaSense AI is a local modular monolith. Streamlit is the presentation adapter; every decision is
implemented below the view layer so it can be tested independently and later exposed through a
mobile or API adapter without rewriting policy logic.

```text
Streamlit pages
      |
      v
AssessmentService
  |-- validation and feature contract
  |-- trusted model registry -> prediction -> residual interval
  |-- unusual-input detector -> risk/confidence policy
  |-- local explanation adapter
  |-- YAML advisory engine
  `-- SQLite assessment repository -> CSV export
```

## Dependency boundaries

- `schemas.py` defines typed service contracts and has no Streamlit dependency.
- `validation.py` enforces crop, numeric, unit, text, and hard-bound contracts.
- `data/` owns UTF-8 CSV ingestion, the canonical contract, deterministic demo generation, and a
  machine-readable quality report.
- `ml/` owns feature order, preprocessing, candidate training, grouped splitting, evaluation,
  uncertainty, approximate local explanations, drift checks, and bundle integrity.
- `advisory/` is separate from the statistical model. A model update cannot silently change advice.
- `storage/` stores immutable result snapshots through parameterised queries and neutralises CSV
  formulas.
- `i18n/` loads stable keys, checks interpolation parity, and falls back to English.
- `ui/` contains shared Streamlit rendering only.

## End-to-end assessment flow

1. Validate and coerce required maize inputs; reject impossible values and bounded-text violations.
2. Enforce the five-feature order stored in the model contract.
3. Predict with the checksum-verified local scikit-learn pipeline.
4. Build a non-negative presentation range using the held-out calibration absolute-residual
   quantile; retain raw bounds in technical metadata.
5. Compare each input with fitted-data min/max and robust 1st/99th percentiles.
6. Derive the provisional risk band and confidence label from versioned policies.
7. Estimate three local drivers by replacing one feature at a time with its training median.
8. Select the highest-priority guarded action and up to two supporting actions from `rules.yml`.
9. Trigger human referral for high risk, low/insufficient confidence, severe warnings, or several
   unusual inputs.
10. Persist inputs, outputs, warnings, drivers, rules, versions, and timestamps as one immutable
    SQLite snapshot.

## Trust boundaries

- The browser and entered text are untrusted. Validation occurs before inference or storage.
- CSV training sources are untrusted until the ingestion contract and quality checks pass.
- Joblib is code-capable serialisation. Only the configured path inside `models/` is accepted, and a
  SHA-256 sidecar must match before deserialisation. User model uploads do not exist.
- Rule and locale catalogues are local release files validated at load time.
- CSV exports cross into spreadsheet software, so formula-like leading characters are prefixed with
  an apostrophe.

## Persistence

SQLite is initialised idempotently and uses WAL mode, transactions, parameterised SQL, and indexes
on timestamp, risk, and district. `result_json` preserves the complete immutable snapshot while
scalar columns support filters. Deletion is explicit and confirmed in the interface. A pilot must
define retention, access, backup, recovery, and deletion ownership.

## Offline and extension points

Inference, explanation, rules, history, and export use only local assets. Candidate future adapters
for weather, satellite, soil, synchronisation, mobile, or institutional reporting must remain
optional and cannot become a prerequisite for the default workflow. Crop expansion requires a new
feature contract, model, risk policy, and reviewed advisory package rather than reusing maize rules.

