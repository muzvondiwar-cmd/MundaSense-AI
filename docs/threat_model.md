# Threat model

## Assets and objectives

Protect the confidentiality of local assessment records, integrity of models/rules/locales, safe and
honest output, reproducibility of evidence, and availability of the offline assessment path. The MVP
has no public API, account system, cloud sync, or user-uploaded models.

| Threat | Possible harm | Current controls | Pilot follow-up |
|---|---|---|---|
| Malicious/tampered joblib | Code execution or misleading output | Trusted `models/` path only; SHA-256 sidecar; no uploads; schema validation | Signed release packages, restricted OS permissions, revocation process |
| Untrusted CSV | Parser failure, poisoned data, silent unit errors | UTF-8/comma contract; required/type/duplicate/impossible checks; quality report; explicit provenance | Sandboxed staging, file-size limits, human data approval, unit adapters |
| Modified advisory YAML | Unsafe or altered advice | Required fields, unique IDs, fixed version, deterministic tests, separate release | Signed rules, named agronomic approver, review audit trail |
| Data leakage from local history/backups | Farm information disclosed from shared device | Minimum collection, no legal name/GPS/account, Git-ignore local DB, no raw-input logs | Device encryption, access control, retention/deletion and backup policy |
| CSV formula injection | Spreadsheet command/formula execution | Prefix cells beginning with formula characters | Repeat export tests for target spreadsheet tools |
| Text/SQL injection | Corrupt queries or stored content | Bounded/control-cleaned text and parameterised SQL | Abuse tests and stronger identity/access layer if accounts are added |
| Dependency compromise | Malicious package or known vulnerability | Exact tested top-level pins, restricted CI permissions, no runtime downloads | Lock with hashes, dependency/secret scanning, update SLA and SBOM |
| Misleading precision or causal language | Unsafe management decision | Range, confidence, OOD warnings, non-causal driver wording, no gauges, disclaimers | Comprehension/usability study and incident monitoring |
| Stale model under climate/data shift | Systematic error | Stored ranges/OOD warnings and version trace | Outcome monitoring, drift/coverage review, seasonal revalidation |
| Missing or corrupt assets | Silent fallback or fabricated result | Controlled startup/readiness failure and exact training command; no auto-retrain | Known-good offline recovery bundle and operator runbook |

## Logging

Structured local events include timestamp, severity, event, and relevant model/rules versions.
Assessment events do not log raw feature values, farm aliases, or exported content by default. Debug
logging for a pilot must be time-bounded and privacy-reviewed.

## Assumptions

The user trusts the repository source and installation channel; local OS/browser are not already
compromised; the operator controls the trusted model directory; and physical device security is an
operator responsibility. Cloud, sync, authentication, public network, and remote-update threats must
be modelled before those features are added.

