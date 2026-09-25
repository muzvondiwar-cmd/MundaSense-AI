# Architecture

## Decision

MundaSense AI is a local modular monolith with two presentation adapters. The primary adapter is a
React single-page application using a small FastAPI transport layer. The original Streamlit UI is
retained as a legacy diagnostic adapter. Neither owns statistical, safety, advisory, or persistence
logic.

```text
Browser
  React Router + TanStack Query + React Hook Form + Recharts
                   |
              typed JSON API
                   |
FastAPI: validation, serialisation, filters, report rendering
                   |
AssessmentService
  |-- feature-contract validation
  |-- trusted model -> prediction -> residual interval
  |-- unusual-input detector -> risk/confidence policy
  |-- approximate local explanation
  |-- versioned YAML advisory rules
  `-- SQLite immutable snapshot repository -> safe CSV
```

The Vite development server proxies `/api` to `127.0.0.1:8000`. A production frontend build is
served by FastAPI with SPA route fallback. Route components are lazy-loaded, so dashboard charting
code is not part of the initial page chunk.

## Boundaries

- `frontend/` owns interaction, responsive layout, URL filters, local interface preferences, and
  human-readable visualisation. It does not reproduce model or advisory decisions.
- `backend/` maps HTTP payloads to domain requests and stable response schemas. It aggregates stored
  records for dashboards and escapes printable report output.
- `src/mundasense/schemas.py` defines framework-independent contracts.
- `validation.py` enforces maize scope, five numeric fields, units, text bounds, language, and
  provenance source.
- `ml/` owns feature order, candidate training, grouped splits, uncertainty, explanations, drift
  checks, and bundle integrity.
- `advisory/` is versioned independently from the model; a model update cannot silently change
  advice.
- `storage/` persists complete immutable snapshots and neutralises spreadsheet formulas.
- `i18n/` validates Python catalogues and falls back to English. The React demonstration dictionary
  applies the same fallback rule for shell copy.

## Assessment and scenario flow

1. The React form validates for immediate accessible feedback.
2. FastAPI/Pydantic rejects unexpected fields, impossible values, oversized text, and oversized
   bodies.
3. `AssessmentService` revalidates and runs the checksum-verified local bundle.
4. It produces a non-negative calibrated range, warnings, provisional risk/confidence, three local
   drivers, deterministic advice, and referral state.
5. A normal assessment is saved as one immutable SQLite snapshot.
6. A scenario uses the same service with changed numeric values and `persist=False`; only an
   explicit save creates a new `source=scenario`, `data_status=synthetic_demo` snapshot.

## Dashboard and reporting

Dashboard summaries are computed only from stored snapshots matching explicit server-side filters.
The API returns counts, average central estimates, distributions, common top drivers, district
aggregates with sample sizes, and a transparent priority ordering. Empty and small samples remain
visible rather than being hidden. CSV export applies the same filters. Printable Field Health
Passports are server-rendered, escaped, local-only documents with inputs, versions, warnings,
advice, referral, data status, and disclaimers.

## Trust and offline boundaries

- Browser and entered text are untrusted; validation occurs before inference and storage.
- Joblib is code-capable. Only the configured file below `models/` is accepted and its SHA-256
  sidecar must match.
- SQL uses parameters. Report values are HTML-escaped. Formula-leading CSV cells receive a safe
  apostrophe.
- CORS permits only configured exact origins; the default list contains local Vite/preview origins.
- The service worker caches static shell files only. Live API state is never silently replaced by a
  cached response, and a waiting release activates only after the user accepts the update banner.
- Core operation requires no network after packages are installed. Weather, satellite, sync,
  messaging, and cloud analytics remain out of scope.

Crop expansion requires a separate data contract, model, risk policy, and reviewed advisory package;
the maize policy must not be relabelled for another crop.
