# Model card - MundaSense synthetic demonstration model

## Release summary

| Field | Value |
|---|---|
| Model version | `demo-2026.08-v1` |
| Bundle schema | `1.0` |
| Status | Demonstration only; not field-validated |
| Dataset | 720 deterministic synthetic maize records |
| Champion | Gradient Boosting Regressor |
| Created | 2026-08-31T20:49:56+00:00 |
| Features | rainfall, recorded fertiliser, temperature, humidity, soil pH |
| Target | maize yield in t/ha |
| Explanation | One-feature-at-a-time replacement with training median |
| Uncertainty | 90th percentile of absolute residuals on a held-out calibration district |

## Intended use

The model supports an offline demonstration of an end-to-end maize yield-risk assessment for
smallholder-farmer and extension-officer workflows. It is suitable for software evaluation,
explanation comprehension, policy testing, and pilot planning. It is not suitable for real farm
management until verified representative observations, locally reviewed thresholds, and an
appropriately governed pilot replace the synthetic evidence.

## Prohibited use

Do not use this model to prescribe inputs or chemicals, automate irrigation, guarantee yield,
determine credit or insurance, make legal or eligibility decisions, compare farmer performance, or
claim farmer impact. Do not describe driver values as biological causes.

## Training data

The bundled generator creates 720 labelled synthetic records spanning eight Zimbabwean district
names and four season labels. Relationships were designed to be learnable without implying observed
agronomic truth. `is_synthetic=true` and a generator provenance string are present in every row.
No confidential, personal, or observed farm data were used.

## Validation design

District groups were sorted and held apart:

- fit: Bindura, Chinhoyi, Gokwe South, Goromonzi, Masvingo;
- calibration/model selection: Mutare;
- untouched test: Plumtree and Zvishavane.

This approximates deployment to unseen locations more strongly than a random row split, but the
district effects and all observations remain synthetic. Candidate selection used calibration MAE;
the test set was evaluated only after selection. Preprocessing was fitted only on the fitting rows.

## Candidate families

The experiment compares a median `DummyRegressor`, ridge regression, random forest, and gradient
boosting. Gradient boosting had the lowest calibration MAE. Its calibration MAE was 0.479 t/ha,
compared with 0.862 t/ha for the naive median baseline: a 44.4% improvement under this synthetic
split. This is a release-engineering gate, not a real-world performance claim.

## Untouched synthetic test metrics

| Metric | Result |
|---|---:|
| Samples | 186 |
| MAE | 0.475 t/ha |
| RMSE | 0.604 t/ha |
| R² | 0.618 |
| Median absolute error | 0.399 t/ha |
| 90th percentile absolute error | 0.985 t/ha |
| Nominal interval coverage | 90.0% |
| Empirical interval coverage | 90.3% |
| Mean interval width | 2.028 t/ha |

R² alone is not an acceptance criterion. All values describe the deterministic synthetic release
shown in `reports/metrics/evaluation.json`.

## Subgroup slices

| Held-out district label | n | MAE (t/ha) | RMSE (t/ha) | R² |
|---|---:|---:|---:|---:|
| Plumtree | 99 | 0.486 | 0.625 | 0.576 |
| Zvishavane | 87 | 0.462 | 0.579 | 0.662 |

These slices are pipeline checks, not evidence about the named locations. A field model must report
sample size, provenance, representativeness, missingness, and uncertainty for real subgroups.

## Interval and confidence

The displayed range adds/subtracts the calibration district's 90th-percentile absolute residual.
Negative presentation bounds are clipped to zero while raw bounds remain in technical metadata.
Coverage is empirical and not guaranteed for an individual field. Confidence is a separate,
deterministic policy based on interval width, model-metadata presence, and unusual-input severity;
it is not the probability that advice will work.

## Explanation

For each feature, the system replaces only that feature with its fitted-data median and measures the
prediction difference. The three largest absolute differences are shown. Interactions mean these
contributions need not sum to the prediction. Wording deliberately says “the model associated” and
never claims causality.

## Limitations and ethical considerations

- Synthetic relationships, named location labels, risk thresholds, and calibration cannot represent
  Zimbabwean farming systems.
- The five variables omit variety, planting date, crop stage, soil moisture, pests, diseases,
  management timing, extremes, measurement error, and many local factors.
- Recorded fertiliser is an input, not a basis for a dose recommendation.
- One season-total contract may be misunderstood without user training.
- Shona messages and guarded advice await bilingual and agronomic review.
- Historical and climate shift could invalidate an otherwise field-trained model.

## Monitoring and replacement plan

A pilot must capture consented, provenance-rich inputs and observed outcomes; compare error,
coverage, OOD rates, and warning rates by sufficiently large location/season slices; review
explanation comprehension and unsafe reliance; and recalibrate thresholds before expansion. Model
replacement requires a new version, data sheet, checksum, held-out report, rule compatibility check,
independent review, and rollback target.

## Version history

- `demo-2026.08-v1`: first complete synthetic demonstration release.

