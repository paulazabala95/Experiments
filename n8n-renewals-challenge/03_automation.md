# Part 3: Scaling the renewal motion

## The step I automate: daily renewal triage, forecast scoring and escalation

**Why this step:** there are 221 Q4 renewals and four overwhelmed CSMs. The failure in this book is *timing*, not negotiation skill. Quotes go out late (Northwind has none at 9 days out), auto-renewals fail silently (Pixelforge's expired card), notice dates pass unnoticed (Halden, Pixelforge, Lumen), and the forecast is a guess. Triage, the first thing I did by hand in Part 1, is the job a machine should do every morning. I built a **working prototype in n8n**.

**Workflow:** *Renewal forecast and escalation engine* (in my n8n Cloud: https://paulazabala95.app.n8n.cloud/workflow/mvDDTTwQYTpurdtP). The source is in `n8n/`. It is built on my existing *Daily renewal alerts* workflow, which drafts customer emails with AI and sends them only after a CSM approves.

```
Weekdays 7:30 ─► Read renewal pipeline (CRM / Sheet)
                 └► Score renewals + raise alerts (Code)
                     ├► Write scores back to the pipeline (CRM hygiene)
                     ├► Build daily brief ─► Email to Renewals Specialist
                     └► P1? ─► Escalation email to owner + manager
```

| | |
|---|---|
| **Trigger** | Schedule, weekdays at 7:30. In production, also a CRM trigger when Renewal Status, Renewal Date or Amount changes. |
| **Systems** | Prototype: Google Sheets (pipeline) and Gmail. Production: **Salesforce** (renewal opportunities and product lines), **Stripe/billing** (card status, invoice entity), the **product usage warehouse** (90-day execution trend), **Slack** (#renewals-alerts, DMs to owners), and e-signature status. |
| **What it calculates** | Days to renewal, 30/60/90 window, month and quarter, the status × countdown probability (the same matrix as the workbook) × health, and weighted new ARR including the 5% uplift. |
| **Alerts** | OVERDUE · QUOTE_LEAD_TIME (manual, ≤60 days, no quote) · SIGNATURE_RISK (≤14 days, not with procurement) · PAYMENT_BLOCKER (auto-renewal with an expired card or wrong entity) · NOTICE_WINDOW (date to send the uplift notice or watch for cancellation) · HEALTH_RISK · UPSELL_SIGNAL · BLOCKER_OPEN · CRM_HYGIENE (no status, owner or ARR) |
| **Output** | One brief per day grouped by quarter and month, with actions sorted P1 → P3. One escalation email per P1 account. The calculated fields are written back to the pipeline so the forecast report is always current. |

**Tested** on the 10 accounts in this book (pinned data, so no emails were sent). It raised 5 P1s (Vantage, Northwind, Pixelforge, Halden, Tessera) and 5 P2s. That matches my manual triage in Part 1, which took me about an hour. The workflow takes seconds and runs every day.

## What a human still checks

- **The forecast call.** The workflow gives a *system-weighted* number. I make the commit / late / lost call and record it in the CRM. When the two differ by more than 10%, I review that deal.
- **Every P1:** I confirm an owner and a date by 10:00.
- **Anything going to a customer:** AI drafts the emails, and a person approves before sending. This is the approval step in my existing workflow.
- **Commercial terms:** discounts, approvals and contract changes are never automated.
- **Recalibration:** every quarter I compare the probability matrix with actual outcomes and adjust it.

## How I'd know it works

| Metric | Today | Target after 1 quarter |
|---|---|---|
| Manual renewals quoted by day 60 | about 50% (5 of the 7 manual renewals in this book had no quote) | **100%** |
| Overdue renewals (count / ARR) | 1 / €21k | **0** at quarter end |
| Forecast accuracy (call vs. actual, by month) | unknown | within **±5%** |
| Auto-renewals failing on payment | unknown | **0**: caught at day 45 |
| P1 alerts actioned within 24 hours | – | **≥90%**. Below that, the alerts are noise and I tune them. |
| Specialist and CSM hours on triage | ~1 hour a day each | **<10 minutes a day** |

## Next iterations

1. **AI security-questionnaire assistant** (for Marlowe and Tessera): answers drafted from the trust centre and past answers, then reviewed by Security.
2. **Quote and order-form generation** from the opportunity's product lines (uplift and approval rules built in), sent for e-signature automatically when the approval column reads "None".
3. **A Slack bot** ("/renewal Brightloop") that returns status, probability, blockers and the next action from the CRM.
