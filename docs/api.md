# Local API reference

The default base URL is `http://127.0.0.1:8000/api`. Interactive OpenAPI documentation is available
at `/docs` while the API runs. JSON requests are limited to 32 KiB. Assessment responses are
versioned immutable snapshots; clients must not infer agronomic policy from numeric fields alone.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Model, rules, locale, database, and directory readiness |
| GET | `/config?language=en` | Five-field contract, units, limits, versions, and product config |
| GET | `/demo-scenarios` | Balanced, water-stress, and unusual synthetic presets |
| POST | `/assessments` | Validate, assess, persist, and return a complete result |
| GET | `/assessments` | Search, filter, sort, and list stored snapshots |
| GET | `/assessments/{id}` | Retrieve one immutable snapshot in the requested locale |
| DELETE | `/assessments/{id}` | Permanently delete one exact local snapshot |
| GET | `/assessments/export.csv` | Export the current server-side filtered record set |
| GET | `/assessments/{id}/report` | Printable A4 Field Health Passport HTML |
| POST | `/scenarios/simulate` | Reassess numeric overrides without persistence |
| GET | `/dashboard/summary` | Aggregate only matching stored snapshots |
| GET | `/model-card` | Release metrics, methods, ranges, and limitations |

Assessment creation accepts `crop=maize`, the five numeric features, optional season/district/field
alias, `language=en|sn`, and `source=manual|demo|scenario`. Unknown fields are rejected. Successful
responses always include explicit units, plausible range, labelled risk/confidence, drivers,
warnings, guarded advisory/referral, model/rule/app versions, `data_status`, synthetic-model status,
explanation method, disclaimer, and technical metadata.

List, export, and dashboard endpoints share these optional filters where applicable:

- `risk=low|moderate|high`
- `confidence=high|medium|low|insufficient`
- `district=<coarse district>`
- `referral=true|false`
- `data_status=real|synthetic_demo`
- `from_date=YYYY-MM-DD` and `to_date=YYYY-MM-DD`

History also accepts `search` and `sort=newest|oldest|highest_risk|lowest_confidence`. An empty
filtered export contains only the CSV header and never falls back to all records.

Simulation accepts a saved `baseline_assessment_id`, a map of overrides limited to the five model
features, and a language. It returns baseline, scenario, deltas, and `persisted=false`. Saving is a
separate explicit `POST /assessments` request with `source=scenario`.
