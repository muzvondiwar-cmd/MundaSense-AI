# MundaSense AI

![MundaSense AI logo](assets/mundasense_logo.png)

> **Synthetic demonstration:** the included model and presets use deterministic synthetic data.
> Predictions and model metrics are illustrative, not field-validated agronomic evidence.

**Know the risk. Understand the cause. Act before harvest.**

MundaSense AI is a local-first maize yield-risk decision-support prototype for Zimbabwean
smallholder farmers and agricultural extension officers. Its responsive React PWA is backed by a
versioned FastAPI API and the existing Python assessment service. Inference, uncertainty,
explanations, guarded advisory rules, SQLAlchemy/SQLite history, IndexedDB drafts and sync, CSV
export, and printable reports all run on the local device after installation. No account, paid API,
cloud inference, or generative AI is required.

## Product scope

- One crop: maize.
- Five model inputs: seasonal rainfall, recorded fertiliser applied, seasonal mean temperature,
  seasonal mean humidity, and soil pH.
- Farm and field context: province, district, ward, optional GPS, field size, variety, planting date,
  season, growth stage, irrigation availability and visible stress observations. Context is stored
  but never silently presented as a model feature.
- One immutable result snapshot with yield estimate, plausible range, risk, confidence, three
  approximate drivers, warnings, a guarded priority action, and extension-referral guidance.
- A scenario lab that reuses the same validated backend assessment path and never saves a
  simulation unless the user explicitly chooses **Save as new assessment**.
- A reporting dashboard calculated only from stored local records, with URL-persisted filters,
  small-sample warnings, priority cases, and visibly separated synthetic/demo records.
- Searchable history, confirmed archiving, formula-safe CSV export, and a printable Field Health
  Passport.
- English plus partial reviewed Shona demonstration copy with English fallback.
- Installable PWA behavior with IndexedDB drafts, an idempotent offline queue, retry/backoff and a
  strict “prediction pending” state while Python inference is unavailable.

MundaSense does not prescribe exact fertiliser, chemical, seed, or irrigation rates; guarantee
yield; automate farm actions; determine credit or insurance; or replace field inspection and local
extension advice.

## Quick start

Prerequisites: Python 3.12 or 3.13, Node.js 20 or newer, npm, and a modern browser. Internet access
is needed only for dependency installation.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python -m pip install -e . --no-deps --no-build-isolation
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python scripts\seed_demo.py
Set-Location frontend
npm ci
Set-Location ..
.venv\Scripts\python scripts\dev.py
```

### macOS or Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install -e . --no-deps --no-build-isolation
.venv/bin/python -m alembic upgrade head
.venv/bin/python scripts/seed_demo.py
(cd frontend && npm ci)
.venv/bin/python scripts/dev.py
```

Open `http://127.0.0.1:5173`. The launcher also exposes interactive API documentation at
`http://127.0.0.1:8000/docs`. Stop both processes with `Ctrl+C`.

To restore only the fictional demonstration records while preserving manual assessments, run
`.venv\Scripts\python scripts\seed_demo.py --reset`.

### Production-style local build

```powershell
Set-Location frontend
npm run build
Set-Location ..
.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. FastAPI serves the built single-page application and local API from
the same origin. Core inference continues to work without internet access. The service worker caches
the application shell only, never API results, and shows an explicit reload banner when a new shell
is ready.

### Docker Compose

```powershell
docker compose build
docker compose up
```

Open `http://127.0.0.1:8080`; OpenAPI remains available at `http://127.0.0.1:8000/docs`. SQLite is
stored in the `mundasense-data` named volume. After images and packages are installed, the complete
demonstration requires no internet connection.

### Vercel deployment

The repository includes a Vite build configuration and `api/index.py` FastAPI entrypoint for a
single Vercel project:

```powershell
vercel link
vercel deploy
vercel deploy --prod
```

Set `MUNDASENSE_DATABASE_URL` to a PostgreSQL SQLAlchemy URL in Vercel for durable assessment
history. When it is absent, preview deployments use SQLite in `/tmp` so the demo can run, but that
filesystem is ephemeral and records may disappear between function instances. The React app's
IndexedDB draft/outbox support remains available in either mode.

## Demo path

1. Open **Dashboard** and confirm the green backend-ready status plus seeded demo labels.
2. Open **New assessment** and load **Balanced field**.
3. Review all four assessment steps, then select **Assess and save**.
4. Inspect the yield range, text-and-icon risk/confidence labels, model drivers, data warnings,
   advisory, referral state, and technical disclosure.
5. Open **Climate Scenario Lab**, choose the saved baseline, move a slider, and review the
   clearly labelled unsaved simulation. Save it only when you want a separate scenario record.
6. Open **Dashboard**, **History**, and **Insights** to see filters, charts, sync state, export,
   archive, and the printable Field Health Passport.
7. Stop FastAPI or enable browser offline mode, submit a draft, and show **Saved
   offline—prediction pending** before synchronizing once the service returns.

Demo and scenario records are stored as `synthetic_demo`; manual assessments are `real`. This label
describes record provenance, not model validation—the bundled model itself remains synthetic.

## Architecture

```text
React + TypeScript + Vite + Tailwind + Dexie/PWA
            |
      typed /api/v1 client
            |
      FastAPI adapter
            |
     AssessmentService
      |      |       |
 trusted   YAML    SQLAlchemy/Alembic
 model     rules   SQLite snapshots
```

The API adapter validates transport payloads and serialises stable view models. Statistical and
advisory logic stays in the framework-independent Python domain layer. Both assessment and scenario
simulation call the same `AssessmentService`; the only scenario difference is `persist=False` until
an explicit save. The original Streamlit UI remains available as a legacy diagnostic adapter via
`python -m streamlit run app.py`, but it is no longer the primary product interface.

See [architecture](docs/ARCHITECTURE.md), [API reference](docs/API.md),
[model card](docs/MODEL_CARD.md), [offline synchronization](docs/OFFLINE_SYNC.md),
[three-minute demo](docs/DEMO_GUIDE.md), [user guide](docs/USER_GUIDE.md),
[pitch notes](docs/HACKATHON_PITCH_NOTES.md), [data sheet](docs/data_sheet.md),
[responsible AI](docs/responsible_ai.md), and [testing](docs/testing.md).

## Test and verify

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest
.venv\Scripts\python scripts\verify_release.py
Set-Location frontend
npm run lint
npm test
npm run build
```

On Windows, `scripts\quality.ps1` runs the complete sequence. GNU Make targets include `make dev`,
`make api`, `make test`, `make frontend-test`, `make frontend-build`, `make lint`, and `make verify`.

## Train and evaluate

A valid checksum-protected demonstration bundle is included. To regenerate deterministic synthetic
data, compare candidates, train, and evaluate:

```powershell
.venv\Scripts\python scripts\train_demo_model.py --regenerate-data
.venv\Scripts\python scripts\evaluate_model.py
```

Generated artefacts include the trusted Joblib bundle and SHA-256 sidecar, machine-readable metrics,
and actual-versus-predicted and residual plots. A model is never retrained automatically at startup.

## Local data, security, and configuration

The default database is `data/local/mundasense.sqlite3` and is ignored by Git. Optional GPS is a
user-controlled farm field and is never a model input. Demonstration data uses fictional contacts;
do not enter national identifiers, credentials, or payment details. Browser inputs are untrusted and are
validated again by the API/domain boundary. CORS is restricted to explicit local development
origins, request bodies are capped, SQL is parameterised, report text is HTML-escaped, CSV formulas
are neutralised, and model deserialisation is restricted to a checksum-verified local directory.

Copy values from `.env.example` into the process environment when paths, locale, contact text, or
allowed origins must change. No secrets are required. See [threat model](docs/threat_model.md) and
[operations](docs/operational_notes.md) before a pilot.

## Project structure

```text
frontend/               Primary React application, tests, and service worker
backend/                Thin FastAPI transport and reporting adapter
migrations/             Alembic schema history
src/mundasense/         Domain, ML, advisory, persistence, and translation modules
app.py / pages/         Legacy Streamlit diagnostic adapter
data/sample/            Safe synthetic demonstration data
models/                 Trusted versioned local bundle and checksum
reports/                Evaluation metrics and figures
scripts/                Dev launcher, training, verification, and quality commands
tests/                  Python unit, integration, service, and API tests
docs/                   Architecture, API, model, data, safety, and pilot notes
docker-compose.yml      Complete local two-container deployment
```

## Known limitations

- The model and every displayed evaluation metric use deterministic synthetic data and are not
  field-validated.
- Risk thresholds and confidence rules are provisional demonstration policies.
- Shona coverage is partial and requires bilingual review.
- Browser synchronization has server-first UUID conflict handling; it does not yet provide a manual
  merge screen.
- The hackathon deployment has no authentication, encrypted database, managed backup, or multi-user
  authorization.
- PostgreSQL is enabled through a SQLAlchemy URL and bundled driver, but still needs a managed
  database, migration rehearsal, backups, and production operations before a real pilot.

## Licence and pilot status

MIT License. Product ownership, deployment partner, qualified agronomic reviewer, extension contact,
retention policy, backup owner, and incident process remain explicit pilot prerequisites.
