# n8n Renewals Specialist: challenge submission

**Paula Zabala.** Scenario date: **Tuesday 20 October 2026.** This keeps the brief's premise intact: one renewal overdue and nine due within 60 days.

## What's in the pack

| File | What it is |
|---|---|
| `01_triage_and_forecast.md` | **Part 1:** renewals ranked with owner and date for each, today's escalations, and the forecast (on time / late / lost) |
| `02_brightloop_negotiation.md` | **Part 2:** reply to Sam, a one-page plan (target, walk-away, gives and gets, who's involved), and the call playbook with expected surprises |
| `03_automation.md` | **Part 3:** a working n8n prototype for daily triage, forecast scoring and escalation |
| `renewal_tracker.xlsx` | The CRM model behind the numbers: Pipeline, Products (renewal/upsell/downgrade/churn lines with 5% uplift), Opp summary, Monthly report, Probability matrix, Policy |
| `n8n/` | Workflow source (`workflow_sdk.ts`), the scoring and brief code, test rows, and a sample brief (`sample_digest.html`) |

## The 40 minutes, in summary

**Part 1 (12 min).** I rank by slack × ARR. Northwind, Vantage and Pixelforge each need about an hour of work today to remove most of their risk. Halden and Tessera get escalated today. **Forecast: €248k on time, €101k late, €26k lost. That is 93% gross retention and 96% net retention after the 5% uplift.** The number I'm least sure of is the lost number, because of Halden.

**Part 2 (18 min).** Brightloop: I decline the termination right, the auto-renewal removal and the 25% discount. I trade **term, structure and right-sizing** instead. Target: 2 years at €36k flat, with no approvals needed. Floor: €33.3k a year on 2 years, with Finance approval. Below that, they move to a smaller plan at list price, not a deeper discount.

**Part 3 (10 min).** An n8n workflow scores the book every weekday morning. It raises nine kinds of alert, writes scores back to the CRM, and sends one brief plus P1 escalations. A person still makes the forecast call and approves anything that goes to a customer.

**Timing I'll hold:** Part 1 at 0–12 min, Part 2 at 12–30 min (3 min to set up, 15 min live), Part 3 at 30–40 min. I'll flag the time when each part ends.

## How I used AI and automation

- **My process, my judgement:** the renewal stages and their probability logic, the product-line model (renewal/upsell/downgrade with original-versus-new comparison), 5% indexation, the account calls, and the negotiation strategy all come from how I've run renewals before.
- **An AI assistant (Claude)** helped me pressure-test the triage and the forecast, check the policy maths (discount against the uplifted list price, approval thresholds), draft the email and playbook text I then edited, and generate the Excel model and the n8n workflow code. I checked every number in the workbook.
- **n8n:** I built the Part 3 prototype in my own n8n Cloud instance on top of my existing renewal-alert workflow (AI drafting with CSM approval), and tested it on this book with pinned data.
