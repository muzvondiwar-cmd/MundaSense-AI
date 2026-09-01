# Data sheet - deterministic synthetic maize demonstration data

## Motivation

The dataset exists solely to make the MundaSense software, ML, explanation, persistence, and safety
workflow reproducible when no verified field dataset is supplied. It must not be used as a proxy for
evidence about actual Zimbabwean farms.

## Composition

- 720 rows generated with NumPy seed 42.
- Crop is maize for every row.
- Five numeric model features: seasonal rainfall, recorded fertiliser, mean temperature, mean
  humidity, and soil pH.
- Target is synthetic yield in tonnes/hectare.
- Eight district labels and four season labels support grouped splitting and slices.
- Every row contains `is_synthetic=true` and generator provenance.
- No personal, household, demographic, financial, or precise-location data.

## Generation

`src/mundasense/data/demo_data.py` samples bounded feature distributions and creates the target from
non-linear rainfall and fertiliser terms, temperature/humidity/pH penalties, small context effects,
and random noise. These relationships were chosen to exercise candidate comparison, explanations,
intervals, and OOD warnings. They are not calibrated agronomic equations.

Regenerate exactly with:

```text
python scripts/train_model.py --regenerate-data --seed 42 --rows 720
```

## Preprocessing and quality

The loader expects UTF-8 comma-delimited CSV, normalises headers, validates the canonical columns,
coerces numeric values, rejects non-numeric conversion, duplicate IDs, non-maize records, and
impossible values, then writes a JSON quality summary. The fitted pipeline applies median imputation
and scaling based only on training rows. The demonstration generator currently produces complete
rows; imputation exists for replaceable real-data ingestion.

## Splitting and leakage

District is a split group, not a model feature. Yield, record ID, crop, source, synthetic flag,
district, and season never enter the feature matrix. Five districts fit the pipeline, one calibrates
and selects the model, and two remain untouched for final evaluation.

## Sensitive attributes

None are included. Future demographic attributes must not be collected merely for reporting. Each
requires a defined fairness question, lawful basis, minimisation review, access control, retention,
and community governance.

## Recommended uses

- Reproducing and testing the MundaSense demonstration.
- Verifying data contracts, model packaging, intervals, explanations, and UI states.
- Training reviewers on synthetic/field evidence distinctions.

## Prohibited uses

- Field agronomic decisions, yield forecasts, regional comparisons, policy allocation, credit,
  insurance, farmer ranking, scientific inference, or impact claims.
- Combining with real farmer identifiers or presenting named district slices as observations.

## Provenance, licence, and maintenance

Created by the repository's deterministic generator and released under the repository MIT License.
The maintainer must regenerate the quality report and model card after any generator, schema, seed,
row-count, split, or feature change. Verified real data require a separate data sheet documenting
owner, permission/licence, collection process, measurement periods, missingness, corrections,
representativeness, and withdrawal/maintenance procedures.

