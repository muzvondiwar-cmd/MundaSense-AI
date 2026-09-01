# Data dictionary

## Assessment-period contract

Every weather value must refer to the same explicitly understood maize assessment season. The demo
uses seasonal totals/means; it does not combine daily and seasonal values. A real-data adapter must
record exact start/end dates, station or product provenance, aggregation, missingness, and unit
conversion.

## Canonical training columns

| Column | Type | Unit / meaning | Required | Missing policy | Leakage note |
|---|---|---|---|---|---|
| `record_id` | string | Unique source-safe row ID | Yes | Reject missing/duplicate | Identifier; never a model feature |
| `crop` | string | Must be `maize` | Yes | Reject | Scope control; not a feature |
| `district` | string | Location group | Yes for demo | Reject in demo | Split group only; not a feature |
| `season` | string | Crop season/year | Yes for demo | Reject in demo | Context/slicing only; not a feature |
| `rainfall_mm` | float | Millimetres for assessment season | Yes | Median imputation in fitted pipeline; ingestion reports missing | Must be available at assessment time |
| `fertilizer_kg_ha` | float | kg/ha already recorded/applied | Yes | Median imputation in fitted pipeline; app requires value | Historical input, never converted to dosage advice |
| `temperature_c` | float | Mean °C for assessment season | Yes | Median imputation | Must use same time window as rainfall |
| `humidity_pct` | float | Mean relative humidity, 0-100% | Yes | Median imputation | Must use same time window as rainfall |
| `soil_ph` | float | Representative soil pH, 0-14 | Yes | Median imputation | Measurement date/method required in real data |
| `yield_t_ha` | float | Observed yield, tonnes/hectare | Yes | Reject missing target for training | Target only; explicitly excluded from feature matrix |
| `data_source` | string | Dataset provenance statement | Yes | Reject | Metadata only |
| `is_synthetic` | boolean | Synthetic/proxy/observed status | Yes | Reject | Metadata and disclosure only |

## Inference text fields

`season` is at most 30 characters. `district` and `farm_reference` are at most 80 characters and
have control characters removed. A farm reference should be a non-sensitive alias. Legal name,
national ID, phone, exact GPS, financial status, and demographic attributes are not collected.

## Hard application limits

| Feature | Hard limit | Behaviour |
|---|---:|---|
| Rainfall | 0-2,000 mm | Outside range blocks assessment |
| Recorded fertiliser | 0-1,000 kg/ha | Outside range blocks assessment |
| Temperature | -10-60 °C | Outside range blocks assessment |
| Humidity | 0-100% | Outside range blocks assessment |
| Soil pH | 0-14 | Outside range blocks assessment |

Hard limits prevent impossible or unsafe values; they are not claims about agronomic suitability.
The model additionally stores fitted-data min/max and 1st/99th percentiles. Values outside robust
ranges proceed with a warning; values outside observed synthetic min/max are severe and trigger
referral.

## Encoding and units

CSV input is UTF-8, comma-delimited, and has normalised lower-snake-case headers. Unit conversion is
not implicit. A future adapter must implement and test each conversion explicitly rather than
relabeling values.

