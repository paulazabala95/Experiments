# Part 3: Scaling the renewal motion

## The step I automate: quote and order-form generation

**Why this step**
- **It's the root cause in this book.** 5 of the 7 manual renewals had no quote inside 60 days (Northwind, Halden, Tessera, Kestrel, Marlowe), against a policy of quoting at 60 days. At 221 renewals a quarter, producing quotes by hand doesn't scale. The quotes go out late, and then everything after them is late too.
- **It's rules-based, so it's safe to automate.** The uplift, the price lock on upfront multi-year deals, the policy C approvals and the fixed clauses are exactly where people make mistakes under time pressure.
- **It's real integration work:** CRM → pricing → approval → document → e-signature → back to CRM. That's what n8n is for. The forecast, statuses and alerts live in the CRM itself (`01b_crm_design.md`), so they don't need a workflow.

**I've done this before.** At my current company there was no CPQ tool, so I built *Roberto*, a renewal quotation agent. It ran our existing quote spreadsheet as the source of truth, with deterministic pricing and a human approving every quote. It cut about a week of quote work per quarter to hours. **Here I assume n8n has a CPQ.** So pricing and approvals belong in the CPQ, n8n orchestrates the steps around it, and AI moves to the one part that needs language: the cover email.

## The workflow (working prototype)

**Renewal quote and order form**, in my n8n Cloud: https://paulazabala95.app.n8n.cloud/workflow/mvDDTTwQYTpurdtP (source in `n8n/`)

```
Quote request ─► Read product lines ─► Price + order form (CPQ stand-in) ─► Draft cover email (AI)
                                                                               │
          Mark renewal as Quoted ◄─ Send order form ◄─ Approved? ◄─ Review and approve (human)
```

| | Prototype | Production |
|---|---|---|
| **Trigger** | Form: renewal, term (1–3 years), annual or upfront payment, discount for year 1 and year 2+, plan change, payment terms, what we know | The CRM's **T−60 task** for every manual renewal, or a "Generate quote" button on the opportunity |
| **Data** | Google Sheet (`Products` tab) | Salesforce renewal opportunity and product lines |
| **Pricing and approvals** | A deterministic code step that reproduces the rules (below) | **The CPQ**, with its approval chain |
| **Cover email** | AI (Basic LLM chain, low-cost model) | Same |
| **Human approval** | Gmail email with Approve and Reject buttons | Same, or Slack. Finance or the VP are added when the CPQ flags them. |
| **Send and update** | Email the order form; set Status = Quoted | Send for **e-signature**; attach the quote file to the opportunity (which the *Quoted* validation rule requires); set the status |

**The pricing rules (deterministic, never AI)**
- **Year 1:** 5% uplift on renewal lines; upsell and downgrade lines at list.
- **Multi-year:** price **locked from year 2 if paid upfront**, +5% a year if paid annually.
- **Discount:** set separately for year 1 and year 2+, so a ramp can be quoted.
- **Approver under policy C:** based on the total discount against the annual list path. Net 60 goes to Finance, and a 3-year term is flagged for Finance to confirm.
- **Order form:** the auto-renewal clause applies after the committed term, there's no termination for convenience, and no downgrade during the term.

## Where AI is used, and where a human stays in the loop

| Step | Who does it | Why |
|---|---|---|
| Prices, schedule, approver | **Rules** (CPQ) | Commercial terms must be exact and repeatable. No AI. |
| Cover email | **AI** | Personal wording at scale, from what we know about the account. It's the only free-text step. |
| Approve before sending | **Human** (Renewals Manager; Finance or VP when flagged) | Nothing reaches a customer without a person's approval |
| Negotiation, exceptions, at-risk accounts | **Human** | Judgement. At-risk accounts get a call before any quote. |

**The AI has guardrails.**
- It gets a ready-made offer sentence to copy exactly, so it never writes or changes a number.
- Account notes are marked internal, for tone only.
- It's told never to mention discounts, approvals or policy.

**What the first test taught me:** before these guardrails, the draft repeated internal notes to the customer ("budget cut", "executions down 10%") and pasted unformatted numbers. The human check caught it, and the fix went into the prompt and the data I give the model. That's the case for keeping a person on every customer-facing output, at least until the workflow has a track record.

## Tested on this book

| Scenario | Quote | Approver |
|---|---|---|
| Northwind, 1 year | €50,400 | None: send straight to review |
| Brightloop **ramp**, 2 years, annual | Year 1 €34,020 · Year 2 €37,706 · total €71,726 (7.4%) | Finance |
| Brightloop **downsize + lock**, 2 years, upfront, net 60 | €28,800 × 2 · total €57,600 (2.4% waived uplift) | Finance (net 60) |
| Brightloop **downsize + lock**, 3 years, upfront, net 60 | €28,800 × 3 · total €86,400 (4.8%) | Finance (net 60, 3-year term) |
| Brightloop at Sam's 25% ask | Year 1 ≈ €27,000 (28.6%) | VP CS |

These match the Part 2 negotiation plan exactly. During the call, I can produce any option Priya picks within minutes, already approved and ready to sign.

## How I'd know it works

| Metric | Today | Target |
|---|---|---|
| Manual renewals quoted by day 60 | 1 of 7 in this book (Brightloop; Vantage was quoted at day 44) | **100%** |
| Time to produce a quote | 30–60 minutes each | **under 5 minutes**, plus the review |
| Pricing or approval errors on quotes sent | not measured | **0** |
| Quote to approval turnaround | not measured | **under 24 hours** |
| AI drafts sent without edits | – | tracked weekly; when it's consistently high, consider removing the check for standard renewals |

## What I'd build next

Each step widens what runs on its own as the workflow earns trust:

1. **Graduated autonomy.** Standard renewals with no discount, a green account and Approver = None go straight to e-signature. Anything negotiated or at risk keeps the human check.
2. **At-risk routing.** Before quoting, check health, usage and notice deadline. At-risk accounts get a CSM call task instead of a quote.
3. **Expansion variant.** When usage is above the plan, produce the renewal quote plus an upsell variant, and open the linked Upsell opportunity.
4. **AI security-questionnaire assistant** (Marlowe, Tessera): answers drafted from the trust centre and past answers, reviewed by Security.
