# Testing and release guide

## Quality gates

From an activated Python 3.12 environment with development requirements installed:

```text
python -m ruff check .
python -m ruff format --check .
python -m pytest
python scripts/train_model.py --regenerate-data
python scripts/evaluate_model.py
python scripts/verify_release.py
python -m streamlit run app.py
```

The PowerShell wrapper `scripts/quality.ps1` runs lint, formatting, tests, and release verification.
CI repeats these gates and performs a compact synthetic retraining smoke test.

## Automated coverage

Unit tests cover numeric/text boundaries, crop scope, feature-order enforcement, risk threshold
edges, confidence, OOD severity, interval clipping, rule precedence, safe default advice, Shona
fallback and placeholder parity, SQLite idempotence, snapshot mapping, and CSV formula neutralisation.

Integration tests train a self-contained bundle, check candidate families and the baseline gate,
produce a finite deterministic prediction, verify no target leakage, run the full service, persist and
reopen an unchanged result, and convert missing/corrupt bundles into controlled errors.

Service-level smoke tests run balanced, water-stress, and unusual-data scenarios through validation,
prediction, uncertainty, risk, confidence, explanation, advice, and referral.

## Manual UI acceptance

1. Launch Streamlit and confirm the home page shows the logo, tagline, local-operation statement,
   synthetic-data banner, safety boundary, three-step flow, and working start button.
2. Run Scenario A. Confirm yield, range, labelled/icon risk, confidence, three drivers, one priority
   action, disclaimer, and technical trace.
3. Run Scenario B. Confirm current model/policy computation (no hardcoded result) and water-stress or
   risk action as applicable.
4. Run Scenario C. Confirm visible OOD warnings, reduced confidence, and extension referral.
5. Open history. Confirm newest-first order, filters, immutable detail, CSV download, and confirmed
   deletion.
6. Open model evaluation. Confirm exact release metadata, candidate table, two plots, subgroup sizes,
   limitations, and readiness.
7. Toggle Shona. Confirm priority strings change, English fallback remains readable, and review
   status is visible.
8. Stop network access and repeat an assessment to verify the core path remains local.

## Failure cases

- Rename the bundle: startup and readiness must show the exact training recovery command.
- Alter a bundle byte: checksum verification must block deserialisation.
- Supply an invalid rules catalogue in a test: catalogue loading must fail before advice is shown.
- Enter impossible numeric values or overlong text: the assessment must not run.
- Export a farm alias beginning with `=`, `+`, `-`, or `@`: the CSV cell must be prefixed safely.

## ML validation notes

Fitting uses only the fitting districts; the calibration district selects the champion and calibrates
the interval; test districts remain untouched until final evaluation. The target and context metadata
never enter the feature matrix. Same-seed runs use deterministic generators and estimator seeds.
Metric thresholds are provisional engineering gates rather than agronomic acceptance criteria.

