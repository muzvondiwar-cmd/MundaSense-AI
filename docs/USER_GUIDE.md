# User guide

## Start here

Use **Home** for the product introduction, **Dashboard** for portfolio attention, or **New
assessment** for a field visit. The green/amber/red status in the navigation distinguishes backend
ready, backend unavailable and browser offline states.

## Farms and fields

Create a farm with a non-sensitive contact label, province, district and ward. GPS coordinates are
optional. Add fields with area, maize variety, planting date, season and target yield. Demo farms are
labelled; no real personal information is included in the seed data.

## Assessment wizard

1. Select or enter the field context.
2. Record rainfall, average temperature and relative humidity for the same assessment period.
3. Record soil pH, fertiliser already applied and optional management observations.
4. Review every value and unit before submission.

Hard technical limits block submission. Values inside those limits but outside the demonstration
model's familiar range show a warning and may lower confidence. Drafts auto-save in the browser.

## Reading a result

- **Predicted yield** is a central model estimate in t/ha.
- **Range** reflects held-out synthetic residual calibration, not a guaranteed interval.
- **Risk** uses provisional yield thresholds and a transparent 0–100 concern scale.
- **Confidence** reflects interval width, metadata and input familiarity; it is not model accuracy.
- **Drivers** are approximate model associations and do not prove biological causes.
- **Next action** comes from reviewed deterministic rules and remains cautious.

Always read the warnings and responsible-use disclaimer. Involve a qualified extension officer where
the app flags referral, high risk or low confidence.

## Scenario Lab

Choose a saved baseline and adjust rainfall, fertiliser already applied, temperature, humidity or
soil pH. The original record is never overwritten. Reset restores the baseline. Saving creates a new
record visibly labelled as a scenario.

Do not treat a simulated improvement as a recommended fertiliser dose or causal claim.

## History, reports and archive

Search, filter, sort and page through saved assessments. Export the current filtered view to CSV or
open a print-friendly Field Health Passport. Archive removes a record from active views after
confirmation without rewriting its result.

## Settings and language

Choose English or partial Shona, light/dark/system theme and demonstration-mode visibility. Export
browser data before clearing storage. The Shona interface is incomplete and requires bilingual
review before deployment.

## Offline use

A disconnected form can be saved and queued. It receives no prediction until the Python backend is
available. Keep the browser profile intact, reconnect, choose **Sync now**, then open History.
