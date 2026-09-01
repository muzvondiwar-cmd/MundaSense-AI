# Known limitations

- The model, ranges, thresholds, district labels, metrics, and scenarios are synthetic demonstrations
  and cannot support real farm decisions or impact claims.
- Only maize and five seasonal numeric variables are enabled. Variety, planting timing, crop stage,
  soil moisture, pests, diseases, extremes, management timing, and measurement error are omitted.
- The interval uses one held-out synthetic calibration district and assumes future residual behaviour
  is comparable; individual coverage is not guaranteed.
- Risk thresholds of 2.0 and 3.5 t/ha are provisional engineering values, not local evidence-based
  targets.
- Local driver calculations are approximate counterfactual associations and do not allocate model
  interactions or prove causes.
- Advice is deliberately general and cannot replace a reviewed local agronomic rule set.
- Shona priority strings require bilingual farmer and agronomic review; long-form content falls back
  to English.
- Local SQLite has no account-level access control, encryption, automatic backup, or multi-device
  synchronisation.
- Browser automation covers app health and service-level journeys; final field accessibility and
  responsive behaviour need testing on target devices and with representative users.
- Exact top-level package pins are tested on Python 3.12; long-term maintenance needs a hash-locked
  dependency process and vulnerability-response policy.

