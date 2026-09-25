# MundaSense AI architecture

## Architectural decision

MundaSense AI is an offline-first modular monolith. React owns interaction and local browser state;
FastAPI owns transport and server validation; framework-independent Python modules own prediction,
uncertainty, explanations, safety policy and cautious recommendations. The existing Streamlit UI is
retained only as a diagnostic adapter.

```text
React + TypeScript + Vite + Tailwind
  |-- React Router / TanStack Query / React Hook Form / Zod
  |-- Recharts / Lucide / accessible responsive components
  |-- service worker + web manifest
  `-- Dexie IndexedDB
       |-- assessment drafts
       |-- pending/failed synchronization queue
       `-- cached completed results
                    |
              /api/v1 JSON
                    |
FastAPI + Pydantic + predictable error envelopes
  |-- farms and fields
  |-- assessments and predictions
  |-- dashboard and insights
  |-- idempotent synchronization
  `-- printable/CSV compatibility routes
                    |
AssessmentService (framework independent)
  |-- hard validation and model feature order
  |-- checksum-verified scikit-learn pipeline
  |-- residual-calibrated interval
  |-- unfamiliar-input checks and confidence policy
  |-- local approximate explanations
  `-- versioned YAML advisory rules
                    |
SQLAlchemy 2 repository + Alembic -> SQLite
  |-- farms / fields / assessments / prediction_results
  |-- model_metadata / sync_events / app_settings
  `-- complete immutable result snapshots
```

## Key decisions

1. **Preserve the trusted model bundle.** The existing `demo-2026.08-v1` bundle remains the only
   inference artifact. It is loaded only from the trusted `models/` directory after SHA-256
   verification. It is never retrained during application startup.
2. **Version the public API.** New clients use `/api/v1`. Existing `/api` endpoints remain as a
   compatibility surface for printable reports, CSV exports and existing tests/bookmarks.
3. **Keep prediction logic out of HTTP handlers.** FastAPI maps validated transport objects to
   `AssessmentService`; scenario comparison calls the same service with `persist=False`.
4. **Persist complete snapshots.** Every assessment keeps original validated model inputs, submitted
   field context, model output, interval, risk, confidence, explanations, warnings,
   recommendations, versions and data provenance. A later model upgrade cannot rewrite history.
5. **Use SQLAlchemy now, retain a PostgreSQL path.** SQLite is the default hackathon store. The
   `Database` boundary accepts a SQLAlchemy URL through `MUNDASENSE_DATABASE_URL`; no domain code is
   SQLite-specific. PostgreSQL still requires a production driver and deployment testing.
6. **Never fake an offline prediction.** When FastAPI is unavailable, the form is saved to Dexie with
   a UUID idempotency key and shown as `Saved offline—prediction pending`. The backend performs the
   real prediction after synchronization.
7. **Keep advice deterministic and guarded.** Versioned rules may suggest verification, inspection,
   soil testing or extension review. They do not prescribe fertiliser or pesticide doses.

## Offline and synchronization flow

1. Form changes are debounced into `drafts` in IndexedDB.
2. A normal online submission sends an `Idempotency-Key` to `/api/v1/assessments`.
3. A failed/unavailable backend submission is added to `queue`; no result is generated locally.
4. Online events, a 30-second retry loop or **Sync now** call `/api/v1/sync/batch`.
5. The backend records a unique `sync_events.idempotency_key` and associates the same key with the
   assessment. A repeated batch returns the original entity ID.
6. Successful queue items are removed. Failed items retain the input and retry with capped
   exponential backoff.
7. UUIDs are client-generated for farms and fields. Existing IDs win; timestamps and immutable
   assessment semantics prevent silent overwrites.

See [OFFLINE_SYNC.md](OFFLINE_SYNC.md) for operational and conflict detail.

## Security and trust boundaries

- Browser data and text are untrusted and validated again with Pydantic/domain rules.
- Request bodies are capped; CORS uses configured exact origins.
- SQLAlchemy parameterizes database operations.
- Printable reports HTML-escape stored text; CSV output neutralizes spreadsheet formulas.
- Joblib can execute code, so only checksum-verified local bundles are loaded.
- No account, analytics tracker, cloud inference or real secret is required.
- Unhandled exceptions are logged locally; versioned API validation and HTTP errors return stable
  envelopes without stack traces.

## Deployment modes

- **Development:** Vite on port 5173 proxies API requests to FastAPI on port 8000.
- **Single process:** build `frontend/dist`; FastAPI serves the SPA and API on port 8000.
- **Docker Compose:** nginx serves the PWA on port 8080 and proxies to FastAPI; SQLite lives in a
  named volume.
- **Local network:** bind FastAPI/nginx to the host network and open the local firewall deliberately;
  all core functions continue without internet after installation.

## Known architectural limits

The service has no user authentication, multi-tenant authorization, encrypted database, background
worker, real weather feed or merge UI. These are deliberate hackathon limits. A managed pilot needs
role-based access, encrypted backup, audit review, PostgreSQL migration rehearsal and supervised
field validation.
