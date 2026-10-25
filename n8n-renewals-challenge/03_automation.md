# Part 3: Scaling the renewal motion

**The step:** getting the approved quote out to the customer, the CRM updated, and the signature chased. In this book, only 1 of 7 manual renewals had its quote out by day 60, and every later step slips with it. Once a quote is approved, the rest is repetition: write the email, attach the order form, send it, update the CRM, chase. That's exactly the work that doesn't scale to 221 renewals a quarter.

**My rule: the workflow never prices anything.** The CRM and CPQ own the quote, the order form, the approvals and every number. The workflow mirrors them. *(At Bizzdesign there was no CPQ, so I built Roberto, an agent that ran our quote tool with deterministic pricing and a human approving every quote. Here I assume n8n has a CPQ.)*

**The prototype:** I extended a copy of my existing *Daily renewal alerts* workflow in n8n. The workflow JSON is attached.

| | |
|---|---|
| **Trigger** | Daily at 8:00. In production, also a CRM event when a quote is approved. |
| **Systems** | CRM renewal opportunity + **approved CPQ quote** (prototype: Google Sheet tabs) · Gmail (production: e-signature) · AI model for drafting |
| **Routes** | **On track / Upsell:** AI drafts the email, copying the approved offer word for word → Renewals Manager approves → sent with the order form → status *Quoted*. **Chase:** AI follow-up at days 3 and 7 if unsigned. **Risk:** alert to the CSM, no customer email. **Quote not ready:** reminder to finish the quote in the CPQ. |
| **What a human still checks** | Every customer-facing email before it goes out, all pricing and terms (in the CPQ), and at-risk accounts (CSM) |
| **How I'd know it works** | Manual renewals quoted by day 60: 1 of 7 → **100%** · Approved quote to sent: **same day** · Order forms signed within 7 days of sending: tracked · Emails with a wrong number: **0** · AI drafts approved without edits: tracked weekly. Once that's consistently high, standard renewals can go out without the approval step. |

**What testing taught me.** An earlier version leaked internal notes into the AI draft ("budget cut", "executions down 10%"). Now the AI only gets the approved offer and strict rules, and a person approves every email. Autonomy is earned once the workflow has a track record. It isn't switched on from day one.
