# Part 3: Scaling the renewal motion

## The step I automate: getting the approved quote out, signed and tracked

**Why this step**
- **Quotes go out late,** and then everything after them is late too. In this book, only 1 of the 7 manual renewals had its quote out by day 60.
- **Once a quote exists, getting it to the customer is pure repetition:** write the email, attach the order form, send it, update the CRM, and chase the signature. At 221 renewals a quarter, that's where Renewals and CSM time goes, and where renewals slip.
- **The rule I follow: the workflow never prices anything.** The CRM and the CPQ are the source of truth for the quote, the order form, the approvals and every number. The workflow reads what's there, mirrors it, and handles the sending, the status updates and the chasing.

**I've done this before.** At my current company there was no CPQ tool, so I built *Roberto*, a renewal quotation agent. It ran our quote spreadsheet with deterministic pricing, and a human approved every quote. It cut about a week of quote work per quarter to hours. **Here I assume n8n has a CPQ,** so quote creation belongs there. I also already had a **Daily renewal alerts** workflow (AI drafts renewal and upsell emails, and the CSM approves them). For Part 3 I extended a copy of it, rather than building a second workflow that would overlap.

## The workflow (working prototype)

**Daily renewals: alerts, CPQ quote send and signature chase**, in my n8n Cloud: https://paulazabala95.app.n8n.cloud/workflow/mvDDTTwQYTpurdtP (details in `n8n/`)

```
Every day 8:00 ─► Renewals (unsigned, ≤90 days) ─┐
               └► Approved quotes from CPQ ──────┴► Match quote to renewal ─► Route
   Upsell ─────────► AI renewal + upsell emails ─► Renewals Manager approves ─► send with order form ─► Status = Quoted
   On track ───────► AI renewal email ───────────► Renewals Manager approves ─► send with order form ─► Status = Quoted
   Chase signature ► AI follow-up (day 3, day 7) ► Renewals Manager approves ─► send
   Risk ───────────► alert to the CSM (no customer email)
   Quote not ready ► reminder to the Renewals Manager to finish the quote in the CPQ
```

**What changed from my original Daily renewal alerts workflow:**
1. **It mirrors the CPQ.** The approved quote is added to each renewal. Before, the email wrote its own "quotation" from the ARR in the sheet, without the uplift. Now it copies the approved offer word for word.
2. **Gated on an approved quote.** A renewal email only goes out once the quote is approved in the CPQ. If it isn't, the Renewals Manager gets a reminder instead.
3. **The order form goes with the email** for e-signature.
4. **The CRM is updated:** after sending, the Renewal Status is set to *Quoted*, with the date sent.
5. **New signature chase** at 3 and 7 days unsigned.
6. **Approvals go to the Renewals Manager,** who owns the renewal.

| | Prototype | Production |
|---|---|---|
| **Trigger** | Daily at 8:00 | Same, plus a CRM event when a quote reaches *Approved* |
| **Renewals and quotes** | Google Sheet: `Renewals` tab and a `Quotes` tab standing in for the CPQ | Salesforce renewal opportunities and CPQ quotes |
| **Order form** | Link to the CPQ PDF | The CPQ document sent for **e-signature** |
| **Status updates** | Status = Quoted and QuoteSentDate in the sheet | Renewal Status = Quoted, with the quote file attached (which the CRM's *Quoted* rule requires). The e-signature event then sets *Waiting for PO* or *PO received*. |

## Where AI is used, and where a human stays in the loop

| Step | Who | Why |
|---|---|---|
| Prices, terms, approvals, order form | **CRM / CPQ** | The source of truth. The workflow never calculates a number. |
| Renewal, upsell and follow-up emails | **AI** | Personal wording at scale. It copies the approved offer word for word and may not mention discounts, approvals or internal notes. |
| Approve before sending | **Human** (Renewals Manager) | Nothing reaches a customer without a person's approval |
| At-risk accounts | **Human** (CSM) | Gets an alert, not an automated email |

**What testing taught me.** In an earlier version, the AI wrote the cover email from internal account notes and leaked them into the draft ("budget cut", "executions down 10%"). Now the AI only gets the approved offer to copy, plus strict rules, and a person approves every email. That's the case for keeping a human on customer-facing output until the workflow has a track record.

## Tested

The test used pinned data: no real emails were sent and the sheet wasn't changed. The AI drafts ran for real.

| Account | Route | Result |
|---|---|---|
| Northwind | On track | Email with the approved offer Q-1042 (€50,400) copied exactly → approved → sent with the order form → Quoted |
| Kestrel | Upsell | Renewal email with Q-1051 (€36,750) + upsell email → approved → both sent → Quoted |
| Halden | Risk | Alert to the CSM only |
| Tessera | Chase signature | Unsigned for 7 days → AI follow-up restating Q-1047 exactly → approved → sent |
| Marlowe | Quote not ready | Reminder to finish the quote in the CPQ |

## How I'd know it works

| Metric | Today | Target |
|---|---|---|
| Manual renewals quoted by day 60 | 1 of 7 in this book | **100%** (the CPQ quote, plus this workflow sending it the same day it's approved) |
| Time from quote approved to sent | not measured | **same day** |
| Order forms signed within 7 days of sending | not measured | tracked weekly; the chase should raise it |
| Emails with a wrong number | not measured | **0**. Numbers are copied from the CPQ, never written by AI. |
| AI drafts approved without edits | – | tracked weekly; when it's consistently high, consider auto-sending standard renewals |

## What I'd build next

1. **Graduated autonomy.** Standard renewals (no discount, green account, approved quote) go out without the email approval step. Negotiated or at-risk ones keep the human check.
2. **Close the loop on signature.** The e-signature event sets *Waiting for PO* or *PO received* in the CRM and attaches the signed document.
3. **At-risk routing before quoting.** Health, usage and notice deadline decide whether the account gets a quote or a CSM call first.
4. **AI security-questionnaire assistant** (Marlowe, Tessera): answers drafted from the trust centre and past answers, reviewed by Security.
