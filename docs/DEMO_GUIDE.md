# Three-minute HACK4AFRICA demonstration

Before the session, run migrations, seed data, start both services and open
`http://127.0.0.1:5173`. Keep the browser zoom at 100% and verify the green backend-ready indicator.

## 0:00–0:25 — Dashboard

1. Open **Dashboard**.
2. Point to total assessments, current-season count, high-risk fields, average predicted yield,
   pending synchronization and the exact model version.
3. Note that yellow **Synthetic demo** labels prevent demonstration records from masquerading as
   observed evidence.

Say: “MundaSense is an offline-first decision-support prototype for Zimbabwean maize farmers and
extension officers.”

## 0:25–1:10 — Balanced assessment

1. Select **New assessment**.
2. Choose **Balanced field** under demonstration presets.
3. Move through the four steps; point out units, progress, auto-save and unusual-value warnings.
4. On Review, choose **Assess and save**.

## 1:10–1:45 — Explain the result

1. Show predicted yield and plausible range.
2. Show low/moderate/high risk as text, icon, colour and a 0–100 concern score.
3. Explain that confidence reflects input completeness, familiarity and interval width—not validated
   accuracy.
4. Show the three model associations, supporting/risk factors, data-quality notes and guarded action.
5. Open **How was this calculated?** and state that the model is synthetic and not field-validated.

## 1:45–2:20 — Scenario simulator

1. Choose **Scenario baseline**.
2. Lower rainfall substantially.
3. Show original versus scenario yield, risk-point change and changed drivers.
4. Reset the sliders.

Say: “This is a model what-if response, not proof that changing one factor causes the projected
improvement.”

## 2:20–2:45 — History and insights

1. Open **History** and show search, risk badges, synchronization status, CSV export, printable
   report and archive action.
2. Open **Insights** briefly to show trends, risk distribution, unusual-record count and model-version
   distribution.

## 2:45–3:00 — Offline proof

1. Open **Settings** and show the pending queue and IndexedDB storage.
2. Mention that a disconnected submission is stored as **prediction pending**, never given a fake
   result, and synchronized idempotently when the laptop service returns.

Close with: “Know the risk. Understand the cause. Act before harvest—while keeping scientific limits
visible.”

## Prepared scenarios

| Scenario | Expected demonstration behavior |
| --- | --- |
| Balanced field | Approximately 3.1 t/ha, low provisional risk, no extreme input warning |
| Water-stressed field | Very low estimate, high risk, water/temperature influence and referral |
| Unusual data | Strong out-of-range warnings, low confidence and manual-review requirement |
