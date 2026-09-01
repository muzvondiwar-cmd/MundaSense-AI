# MundaSense AI

![MundaSense AI logo](assets/mundasense_logo.png)

> **Demonstration status:** the included model is trained only on deterministic synthetic data.
> Predictions, risk bands, confidence labels, and metrics are illustrative and are **not
> field-validated**.

**Know the risk. Understand the cause. Act before harvest.**

MundaSense AI is an explainable, offline-first maize yield-risk decision-support application for
smallholder farmers and agricultural extension officers in Zimbabwe and similar low-connectivity
settings. A user records five seasonal field conditions and receives a plausible yield estimate,
provisional risk category, confidence label, three model drivers, unusual-input warnings, one
prioritised safe next step, and a clear extension-referral signal.

The core assessment, explanation, advisory, history, and export workflow runs locally after
dependencies are installed. No paid, cloud, or generative-AI service is used.

## What works

- Guided, maize-only field assessment with explicit units and hard input limits.
- Versioned local scikit-learn regression bundle with SHA-256 integrity verification.
- Residual-quantile plausible range and deterministic confidence policy.
- Robust-range and extreme out-of-distribution warnings.
- Three approximate local drivers, phrased as model associations rather than causes.
- YAML-backed guarded advisory rules that never prescribe fertiliser, pesticide, or irrigation
  dosages.
- English interface plus priority Shona demonstration strings and English fallback.
- Local SQLite history, immutable detail view, filtering, confirmed deletion, and formula-safe CSV
  export.
- Technical evaluation page with candidate comparison, held-out metrics, actual-versus-predicted
  plot, residual plot, subgroup slices, ranges, and readiness checks.
- Reproducible training, 32 automated tests, lint/format checks, CI, and release verification.

## Quick start

Prerequisites: Python 3.12 or 3.13 and a modern local browser. Internet is needed only to install
packages; the application is offline after setup.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python -m pip install -e . --no-deps --no-build-isolation
.venv\Scripts\python scripts\verify_release.py
.venv\Scripts\python -m streamlit run app.py
```

### macOS or Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install -e . --no-deps --no-build-isolation
.venv/bin/python scripts/verify_release.py
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Train and evaluate

A valid demonstration bundle is included. Regenerate the same data, model, metrics, and figures:

```powershell
.venv\Scripts\python scripts\train_model.py --regenerate-data
.venv\Scripts\python scripts\evaluate_model.py
```

Training is deterministic for the configured seed. It compares a median baseline, ridge,
random forest, and gradient boosting model using a district-grouped train/calibration/test split.
The untouched test districts are never used for candidate selection. Generated artefacts are:

- `models/mundasense_demo_v1.joblib` and its SHA-256 sidecar;
- `reports/metrics/evaluation.json`;
- `reports/figures/actual_vs_predicted.png`;
- `reports/figures/residuals.png`.

## Test and verify

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest
.venv\Scripts\python scripts\verify_release.py
```

GNU Make equivalents are available as `make train`, `make test`, `make lint`, `make verify`, and
`make run`. Windows users can run the full quality sequence with `scripts\quality.ps1`.

## Demonstration scenarios

- **A - Balanced conditions:** in-range values intended to produce reasonable confidence.
- **B - Water stress:** low rainfall and high temperature, intended to elevate yield risk.
- **C - Unusual data:** several values outside synthetic training ranges, intended to show warnings,
  reduced confidence, and referral.

Every output is computed from the current bundle and policies; predicted values are not hardcoded.
Use `python scripts/seed_demo.py` only when you intentionally want all three saved into local
history.

## Architecture

Streamlit pages call one framework-independent `AssessmentService`. The service validates inputs,
loads the trusted bundle, predicts, calibrates an interval, detects unusual inputs, classifies risk
and confidence, explains drivers, evaluates deterministic advisory rules, and stores a complete
snapshot through a parameterised SQLite repository. Statistical and advisory versions are separate.

See [architecture](docs/architecture.md), [model card](docs/model_card.md),
[data sheet](docs/data_sheet.md), [data dictionary](docs/data_dictionary.md), and
[advisory catalogue](docs/advisory_rules.md).

## Local data and configuration

By default, assessments are stored in `data/local/mundasense.sqlite3`; this directory is ignored by
Git. The application collects no account, legal name, national identifier, phone number, or precise
GPS location. A farm reference should be a non-sensitive alias.

Copy `.env.example` values into your environment when paths or deployment text must change. The
supported variables cover dataset, trusted model, database, default locale, seed, log level,
demonstration banner, and extension-contact placeholder. No secrets are required.

## Responsible use

MundaSense is decision support, not an autonomous agronomist. Do not use it to prescribe exact
fertiliser or chemical doses, automate irrigation, guarantee yield, determine credit or insurance,
or replace a field inspection. High risk, low confidence, severe warnings, or several unusual
features trigger extension referral. English is authoritative; Shona and agronomic rule content
require qualified local review before field use.

Read [responsible AI](docs/responsible_ai.md), [threat model](docs/threat_model.md), and
[known limitations](docs/limitations.md) before a pilot.

## Project structure

```text
app.py / pages/        Streamlit presentation only
src/mundasense/        Domain, data, ML, advisory, storage, i18n, and UI modules
data/sample/            Safe synthetic demonstration data
models/                 Trusted versioned local bundle and checksum
reports/                Machine-readable metrics and evaluation figures
scripts/                Train, evaluate, seed, verify, and quality commands
tests/                  Unit, integration, and service-level smoke tests
docs/                   Architecture, model, data, safety, rules, and pilot notes
```

## Licence and contact

MIT License. Project-owner, deployment-partner, and local extension contact details remain explicit
placeholders and must be configured before a pilot.
