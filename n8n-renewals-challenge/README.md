# n8n Renewals Specialist: challenge submission

**Paula Zabala.** Scenario date: **Tuesday 20 October 2026.** Mid-October keeps the brief's premise: one renewal overdue and nine due within 60 days.

## Summary

**Part 1: Triage and forecast**

- **Uplift:** the contractual 5% is built into the renewal value when the renewal opportunity is created (closed ARR × 1.05), so every number here is what the customer will be billed and nothing is added on top. Multi-year paid annually: +5% each year; paid upfront: price locked from year 2. Any waiver counts as a discount under policy C.
- I rank by **slack** (days left against the work still needed) × ARR at risk.
- Northwind, Vantage and Pixelforge each need about an hour of work today to remove most of their risk. Halden (€45k, red) and Tessera (€50k, MSA redlines) get **escalated today**.
- **The forecast is driven by Renewal Status × days to renewal.**
  - Manual renewals: later statuses rise as the date approaches, early ones fall.
  - Auto-renewals have their own statuses.
  - Overdue renewals only count if they close within the quarter.
- **Today: €133k weighted. By 30 Oct: €245k if this week's actions land, €119k if nothing is done.** The countdown lowers early statuses on its own, so this week's work is worth about €126k of forecast.
- **Lost:** €23k regrettable contraction (Halden, Quanta) and a €3.6k price concession (Brightloop ramp, year 1). That's 92.9% gross and net retention: net equals gross until Kestrel's upsell signs (then about 96%).
- The number I'm least sure about: Halden.

**Part 2: Brightloop**

- I decline the termination right, auto-renewal removal and the 25% discount. Renewal values already include the 5% uplift. Procurement chooses between two structures:
  - **Ramp:** keep the plan, pay annually. €32,400 → €35,910, 7.4% total, Finance approval.
  - **Downsize + lock:** pay upfront. €28,800 a year for 2 or 3 years, net 60.
- **Walk-away:** no termination right, and no more than 12% off the current plan. Below that, a smaller plan at list price.

**Part 3: Automation**

- I extended my own n8n renewal-alerts workflow. Every morning it takes each renewal with an approved CPQ quote, has AI draft the email, waits for my approval, then sends it with the order form and sets the CRM status to *Quoted*.
- It chases unsigned order forms on days 3 and 7, alerts the CSM on at-risk accounts, and reminds me when a quote isn't ready. Numbers always come from the approved quote.

## What's in the pack

| File | What it is |
|---|---|
| `n8n_renewals_challenge_Paula_Zabala.pdf` | The submission: Parts 1–3 |
| `brightloop_one_pager.pdf` | The one-page negotiation plan for Part 2 |
| `renewal_tracker.xlsx` | The model behind the numbers: triage, pipeline, product lines, churn, monthly report, probability matrix |
| `crm_design_appendix.pdf` | Appendix: how the process lives in Salesforce (fields, formulas, guardrails, alerts, reports) |
| `ai_use_statement.pdf` | How I used AI: what came from me, what AI did, how I checked it |
| n8n workflow JSON | Importable into your own n8n |

## How I used AI and automation

In short (details in `ai_use_statement.pdf`):

- **My process and judgement:** the stage and probability logic, product-line and churn model, uplift and price-lock rules, account calls and the Brightloop packages.
- **An AI assistant (Claude):** pressure-tested the maths, drafted text I edited, and built the Excel model and n8n workflow from my specifications. I reviewed every number.
- **n8n:** Part 3 extends a workflow I'd already built, with the same principles as my renewal quotation agent at Bizzdesign: numbers from the tool of record, AI only for language, a human on every customer-facing output.
