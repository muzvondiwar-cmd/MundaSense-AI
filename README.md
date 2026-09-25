# MundaSense AI

![MundaSense AI logo](assets/mundasense_logo.png)

> **Synthetic demonstration:** the included model and presets use deterministic synthetic data.
> Predictions and model metrics are illustrative, not field-validated agronomic evidence.

**Know the risk. Understand the cause. Act before harvest.**

MundaSense AI is a local-first maize yield-risk decision-support prototype for smallholder farmers
and agricultural extension officers. Its primary interface is a responsive React dashboard backed
by a thin FastAPI adapter over the existing Python assessment service. Inference, uncertainty,
explanations, guarded advisory rules, SQLite history, CSV export, and printable reports all run on
the local device after installation. No account, paid API, cloud inference, or generative AI is
required.

## Product scope

- One crop: maize.
- Five inputs: seasonal rainfall, recorded fertiliser applied, seasonal mean temperature,
  seasonal mean humidity, and soil pH.
- One immutable result snapshot with yield estimate, plausible range, risk, confidence, three
  approximate drivers, warnings, a guarded priority action, and extension-referral guidance.
- A scenario lab that reuses the same validated backend assessment path and never saves a
  simulation unless the user explicitly chooses **Save as new assessment**.
- A reporting dashboard calculated only from stored local records, with URL-persisted filters,
  small-sample warnings, priority cases, and visibly separated synthetic/demo records.
- Searchable history, confirmed deletion, formula-safe CSV export, and a printable Field Health
  Passport.
- English plus partial reviewed Shona demonstration copy with English fallback.

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
Set-Location frontend
npm install
Set-Location ..
.venv\Scripts\python scripts\dev.py
```

### macOS or Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install -e . --no-deps --no-build-isolation
(cd frontend && npm install)
.venv/bin/python scripts/dev.py
```

Open `http://127.0.0.1:5173`. The launcher also exposes interactive API documentation at
`http://127.0.0.1:8000/docs`. Stop both processes with `Ctrl+C`.

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

## Demo path

1. Open **Home** and confirm the green **Local system ready** status.
2. Choose **Start with balanced demo**, or open **New assessment** and load a preset.
3. Review all four assessment steps, then select **Assess and save**.
4. Inspect the yield range, text-and-icon risk/confidence labels, model drivers, data warnings,
   advisory, referral state, and technical disclosure.
5. Open **Climate Scenario Lab**, choose the saved baseline, move a slider, and review the
   clearly labelled unsaved simulation. Save it only when you want a separate scenario record.
6. Open **Extension dashboard** and **History** to see records, filters, charts, export, and the
   printable Field Health Passport.

Demo and scenario records are stored as `synthetic_demo`; manual assessments are `real`. This label
describes record provenance, not model validation—the bundled model itself remains synthetic.

## Architecture

```text
React + TypeScript + Vite + Tailwind
            |
      typed /api client
            |
      FastAPI adapter
            |
     AssessmentService
      |      |       |
 trusted   YAML    SQLite
 model     rules   snapshots
```

The API adapter validates transport payloads and serialises stable view models. Statistical and
advisory logic stays in the framework-independent Python domain layer. Both assessment and scenario
simulation call the same `AssessmentService`; the only scenario difference is `persist=False` until
an explicit save. The original Streamlit UI remains available as a legacy diagnostic adapter via
`python -m streamlit run app.py`, but it is no longer the primary product interface.

See [architecture](docs/architecture.md), [API reference](docs/api.md),
[model card](docs/model_card.md), [data sheet](docs/data_sheet.md),
[responsible AI](docs/responsible_ai.md), and [testing](docs/testing.md).

## Test and verify

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest
.venv\Scripts\python scripts\verify_release.py
Set-Location frontend
npm test
npm run build
```

On Windows, `scripts\quality.ps1` runs the complete sequence. GNU Make targets include `make dev`,
`make api`, `make test`, `make frontend-test`, `make frontend-build`, `make lint`, and `make verify`.

## Train and evaluate

A valid checksum-protected demonstration bundle is included. To regenerate deterministic synthetic
data, compare candidates, train, and evaluate:

```powershell
.venv\Scripts\python scripts\train_model.py --regenerate-data
.venv\Scripts\python scripts\evaluate_model.py
```

Generated artefacts include the trusted Joblib bundle and SHA-256 sidecar, machine-readable metrics,
and actual-versus-predicted and residual plots. A model is never retrained automatically at startup.

## Local data, security, and configuration

The default database is `data/local/mundasense.sqlite3` and is ignored by Git. MundaSense asks only
for a coarse district and optional non-sensitive field alias—never precise GPS, a legal name, phone
number, national identifier, credential, or payment detail. Browser inputs are untrusted and are
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
src/mundasense/         Domain, ML, advisory, persistence, and translation modules
app.py / pages/         Legacy Streamlit diagnostic adapter
data/sample/            Safe synthetic demonstration data
models/                 Trusted versioned local bundle and checksum
reports/                Evaluation metrics and figures
scripts/                Dev launcher, training, verification, and quality commands
tests/                  Python unit, integration, service, and API tests
docs/                   Architecture, API, model, data, safety, and pilot notes
```

## Licence and pilot status

MIT License. Product ownership, deployment partner, qualified agronomic reviewer, extension contact,
retention policy, backup owner, and incident process remain explicit pilot prerequisites.
