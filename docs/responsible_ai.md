# Responsible AI and data governance

## Purpose and evidence boundary

MundaSense organises limited field information and supports a conversation; it does not replace an
agronomist, create biological knowledge, or prove that an intervention will work. Synthetic status
is visible on home, assessment, and evaluation pages and in every stored result. Metrics are software
evidence only until representative outcomes exist.

## Safeguards

- **Human in the loop:** high risk, low/insufficient confidence, severe warnings, or several unusual
  inputs require extension review.
- **Uncertainty:** every valid prediction includes a calibrated plausible range and confidence label.
- **Explainability:** three approximate local associations use non-causal language.
- **Guarded advice:** YAML rules produce only permitted observation, verification, testing,
  monitoring, and referral actions.
- **Traceability:** inputs, result, warnings, drivers, model/risk/rules versions, timestamp, and
  synthetic status are immutable in local history.
- **Failure safety:** missing/tampered bundles and invalid rules stop assessment with a recovery
  command rather than silently retraining or falling back to invented output.

## Privacy and consent

The MVP requests no account, legal name, national identifier, phone, exact GPS, medical, financial,
or demographic data. A farm alias is optional. Local storage reduces transmission but not device,
backup, or shared-computer risk. Before a pilot, the data controller must define purpose, notice,
consent or other lawful basis, access, correction, withdrawal, retention, deletion, sharing,
incident response, and community governance in locally understandable language.

## Fairness

Future fairness analysis should compare error, interval coverage/width, missingness, OOD warnings,
and unsafe reliance across sufficiently large and relevant location, season, agro-ecological, farm
scale, and source-quality slices. Every metric needs sample size and uncertainty. Collect sensitive
attributes only when a reviewed fairness question justifies them. The current district slices are
synthetic and must not be interpreted as geographic performance.

## Language

English is authoritative in the MVP. Shona priority strings are demonstrative and must be reviewed
with farmers, a bilingual language specialist, and an agronomic reviewer for meaning, tone,
literacy, and technical safety. Missing Shona keys fall back to English rather than exposing internal
keys or inventing translations.

## Prohibited claims

Do not claim improved yield, reduced water/fertiliser use, farm accuracy, climate resilience impact,
or farmer adoption without a governed pilot and observed outcomes. Do not turn a driver into a causal
claim or confidence into the probability that advice succeeds.

## Incident and concern handling

Capture assessment ID, component versions, observed issue, and device/app version without copying
more farm data than necessary. A deployment owner must triage misleading output, unsafe advice,
translation harm, data exposure, tampered assets, or dependency concerns; suspend the affected
release; preserve evidence; notify partners/users as appropriate; and publish a versioned fix or
rollback.

