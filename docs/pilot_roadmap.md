# Pilot and scaling roadmap

## Gate 0 - demonstration readiness

Current release. Use only synthetic data to verify complete user journeys, offline operation,
explanation comprehension, failure behaviour, and review workflows. Do not recruit farms for
prediction use.

## Gate 1 - evidence and governance

- Identify a Zimbabwean data owner and agronomic partner.
- Establish provenance, permissions/licence, assessment periods, units, outcome measurement, and
  data-quality ownership.
- Complete privacy notice, consent/lawful-basis, access, retention, deletion, incident, and community
  governance plans.
- Perform leakage review and define a deployment-representative held-out design before modelling.
- Review risk thresholds, advice, referral contacts, English text, and Shona text locally.

Exit evidence: approved data sheet, protocol, threat/privacy review, rules sign-off, and pilot stop
criteria.

## Gate 2 - technical validation

Replace or supplement synthetic data through the same ingestion contract. Compare baseline and
candidate families; report MAE, RMSE, R², error percentiles, interval coverage/width, OOD rate, and
subgroup evidence with sample sizes. Test measurement consistency and model stability. A new model
version must not inherit demonstration thresholds without recalibration.

Exit evidence: independently reviewed held-out report, model card, checksum release, rollback plan,
and approved risk/confidence policies.

## Gate 3 - supervised usability and safety study

Run researcher/extension-supervised sessions rather than autonomous farm decisions. Measure task
completion, unit/period errors, comprehension of risk/range/confidence/drivers, Shona meaning,
unsafe over-reliance, referral uptake, latency, offline reliability, and accessibility. Interview
participants about trust and burden.

Exit evidence: documented harms/issues, resolved critical findings, agronomic and bilingual approval,
and an operations/support model.

## Gate 4 - limited seasonal pilot

Deploy to a bounded set of locations with trained extension support, outcome follow-up, incident
monitoring, version pinning, and a comparison design suitable for the research question. Do not make
impact claims before outcome analysis.

## Gate 5 - responsible expansion

Expand geography only when representativeness, OOD, subgroup, support, and governance evidence is
adequate. New crops require crop-specific data, feature meanings, model, risk policy, advisory rules,
language review, and evaluation. Cloud synchronisation, satellite/weather adapters, institutional
dashboards, or accounts remain optional and undergo their own threat/privacy review.

## Pilot research questions

- Are periods and units consistently understood and measured?
- Does the model outperform an honest local baseline on unseen locations/seasons?
- Are plausible ranges calibrated, and where do OOD warnings concentrate?
- Do farmers and extension officers understand association versus cause?
- Do referral prompts reduce unsafe reliance without making the tool unusable?
- Are Shona messages accurate, respectful, and actionable?
- Who maintains devices, models, rules, contacts, and user support sustainably?

