# Operations and recovery

## Start and readiness

For development, `.venv\Scripts\python scripts\dev.py` supervises FastAPI on port 8000 and Vite on
5173. For a production-style local run, build `frontend/` then start
`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`; the API serves the SPA.

`GET /api/health` reports model, rule catalogue, locale, database, and required-directory readiness
using the already loaded runtime. `python scripts/verify_release.py` performs deeper release checks
and the three service-level scenarios. Do not expose this prototype directly to a public network.

## Local persistence and backup

Assessments live in `data/local/mundasense.sqlite3`. Stop the API before copying the database and
its WAL/SHM companions. Backups must be protected like the source device and include the exact
model, checksum, rule catalogue, and app version required to interpret snapshots. Test restore on a
separate configured path. Do not commit or upload backups to an unapproved service.

Deletion is exact-record and permanent after the UI confirmation; it is not a substitute for a
pilot retention policy. A deployment must name the retention owner, backup owner, authorised
operators, and recovery-time expectations.

## Model, rules, or API failure

The process fails closed when the configured model is missing, outside the trusted directory, or has
an invalid checksum. Do not auto-retrain at startup. Restore the previous known-good model and
sidecar, or intentionally run the documented synthetic training command. A rule/locale failure
requires restoration of its matching reviewed release. Historical snapshots are never recomputed.

If the frontend opens but FastAPI is stopped, a red operational banner appears and new assessment,
history, dashboard, and report operations remain unavailable. Restart the API and check `/api/health`.
The service worker caches the shell only and exposes waiting releases through an **Update now**
banner. Clearing browser site data removes that cache and local UI preferences but does not delete
SQLite records.

## Upgrade and rollback

Package the frontend build, Python source, model/checksum, evaluation metrics/figures, model card,
rules, locale report, tests, and change notes as one release. Run every gate in `docs/testing.md`,
retain the prior known-good package, and record the rollback target. Database schema changes must be
backward-readable or supplied with a tested migration and backup plan.

## Offline and integration policy

Once dependencies are installed, the core workflow is fully local. Weather, satellite, soil data,
sync, messaging, telemetry, authentication, and cloud storage are future integrations and must be
optional, consented, failure-tolerant, and unable to weaken the default local workflow.
