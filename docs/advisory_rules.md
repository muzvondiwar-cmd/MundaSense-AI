# Guarded advisory rule catalogue

## Boundary

Advice is deterministic, versioned separately from the regression model, and limited to safe
verification, observation, monitoring, soil-testing, and extension-review categories. No rule gives
an exact fertiliser, pesticide, herbicide, chemical, or irrigation dose; no rule guarantees a yield
improvement. Rule version `advisory-demo-v1` remains pending local agronomic and bilingual review.

## Precedence

Rules are sorted by descending numeric priority, then stable rule ID. The highest action is displayed
as the prioritised next step; up to two further matched actions are supporting steps. Severe data
warnings outrank confidence and risk, because measurements must be verified before interpreting a
model. The monitoring rule is the safe default.

| ID | Priority | Trigger | Permitted action | Referral | Review status |
|---|---:|---|---|---|---|
| `ADV-DATA-001` | 100 | Any severe OOD warning | Verify values, units, and assessment period | Yes | Engineering safety rule; agronomic review pending |
| `ADV-CONF-001` | 90 | Low or insufficient confidence | Inspect field and use professional review | Yes | Engineering safety rule; agronomic review pending |
| `ADV-RISK-001` | 80 | Provisional high-risk estimate | Review field, crop stage, and records with extension | Yes | Local policy validation pending |
| `ADV-WATER-001` | 60 | Rainfall below 400 mm or temperature above 30 °C | Inspect moisture stress/drainage and monitor weather | No by itself | Agronomic review pending |
| `ADV-SOIL-001` | 50 | Soil pH below 5.3 or above 7.4 | Obtain/review a suitable soil test before strategy changes | No by itself | Agronomic review pending |
| `ADV-MONITOR-001` | 10 | Always | Continue structured rainfall/crop/input records | No | Agronomic review pending |

## Referral matrix

Referral is required independently of individual rule matches when risk is high, confidence is low
or insufficient, any severe OOD warning exists, or at least two features are unusual. The deployment
contact remains configurable and must be supplied by a real partner; no phone number is invented.

## Change control

Changing a trigger, priority, message key, rationale, referral flag, locale applicability, or review
status creates a new rules version. Release review includes schema validation, regression tests for
all high-priority rules, bilingual placeholder checks, agronomic approval, and a rollback copy.

