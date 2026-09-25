# Testing and release guide

## Automated gates

Run from the repository root after Python and frontend dependencies are installed:

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest
.venv\Scripts\python scripts\verify_release.py
Set-Location frontend
npm test
npm run build
```

`scripts\quality.ps1` runs this sequence on Windows. Python tests cover domain boundaries, risk and
confidence policies, intervals, OOD warnings, advisory precedence, i18n fallback, persistence,
formula-safe export, API validation, CORS, non-persisting scenarios, dashboard filters, report
escaping, and filtered-empty export. Frontend tests cover form validation, text-and-icon status
badges, i18n fallback, and the scenario simulation warning. The production build is a required type
and bundling gate.

## Browser acceptance matrix

Verify at 360 px mobile, 768 px tablet, and 1440 px desktop widths with the local API running.

1. Home: readiness, synthetic-model banner, safety boundary, three-step explanation, demo presets,
   and all primary links are visible and keyboard reachable.
2. Assessment: step progress, back/continue behavior, units, hard limits, optional-text bounds,
   preset provenance, review summary, processing state, and preserved field values after errors.
3. Result: yield/range, labelled and icon-supported risk/confidence, drivers, warnings, advisory,
   referral, disclaimer, versions, history link, scenario link, and print link.
4. Scenario: baseline selection, sliders and numeric controls, debounced same-backend recomputation,
   visible deltas, persistent simulation notice, and no history change before explicit save.
5. Dashboard: empty/small-sample states, KPI definitions, filters in the URL, risk cross-filter,
   chart text alternatives, sample sizes, synthetic-data notice, and priority-case links.
6. History/detail: search, all filters/sorts, responsive table/cards, matching CSV export, immutable
   snapshot, exact-ID delete confirmation, and printable report.
7. Model/About/404: release metadata, limitations, data-use copy, route recovery, and no dead links.
8. Navigation: collapsible desktop rail, keyboard-contained mobile dialog, bottom navigation,
   language switch, farmer/officer mode, skip link, focus indicators, and backend-offline banner.

## Deterministic API checks

- Balanced demo returns finite yield/range, three drivers, and a saved synthetic-demo snapshot.
- Water-stress demo exercises the current model and rules; no UI result is hardcoded.
- Unusual demo returns OOD warnings, reduced confidence as policy determines, and referral when
  thresholds require it.
- Invalid numeric and overlong text payloads return structured `422` responses without inference.
- Scenario simulation returns `persisted=false`; list count changes only after explicit save.
- Dashboard totals and export rows match the same filter query. A zero-match export has one header
  row only.
- Aliases beginning with `=`, `+`, `-`, or `@` are neutralised in CSV; HTML-like text is escaped in
  reports.

## Offline and failure checks

After dependencies are installed, disconnect networking and repeat assessment, history, scenario,
dashboard, export, and report flows. Stop FastAPI and confirm the frontend shows an honest offline
banner instead of stale operational data. Restore it and confirm queries recover.

Rename the model bundle or alter its checksum in a disposable checkout: startup must fail closed.
Invalid rule or locale catalogues must also fail before advice is served. A release must never
auto-train, download, or silently substitute a model.
