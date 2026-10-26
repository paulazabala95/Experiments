# Part 1: Portfolio triage and forecast

**As of Tuesday 20 October 2026.** This puts Vantage Freight 5 days overdue and the other nine renewals inside 60 days, as the brief describes.
Workbook: `renewal_tracker.xlsx`. Every number below comes from it.

## How I rank

I rank on **slack**: the days left minus the days the work still needs, weighted by ARR at risk. A €48k renewal that is 9 days out with no quote sent comes before a €50k renewal that is 29 days out. Three of the renewals need only an hour of my time today to remove most of their risk. I do those first, before the long, multi-party ones.

The book by renewal month (my base report, and what every alert keys off):

| Quarter | Month | # | Base ARR | Overdue | Manual, no quote, ≤60 days |
|---|---|---|---|---|---|
| Q4 2026 | Oct | 2 | €69k | €21k | 1 |
| Q4 2026 | Nov | 5 | €184k | – | 3 |
| Q4 2026 | Dec | 3 | €122k | – | 1 |
| **Total** | | **10** | **€375k** | **€21k** | **5** |

The brief mentions a quote only for Vantage and Brightloop, so I treat the other five manual renewals as not quoted. On that basis, the 60-day quote policy has already been missed on five of them. That is a process gap, not a problem with individual deals. The CRM's 60-day quote task and Part 3 address it.

## Ranked actions

| # | Customer | ARR | Due | Why now | Next action | Owner | Date |
|---|---|---|---|---|---|---|---|
| 1 | **Northwind Logistics** | €48k | 29 Oct (9d) | Biggest near-term ARR, no quote, signed 3 days late last year | Send quote and order form for e-signature today at **€48k** (the renewal value, uplift included). Ask the champion who signs and whether a PO is needed. Book the signature for 27 Oct. | Me | **Today** |
| 2 | **Vantage Freight** | €21k | 15 Oct (**overdue**) | Every day overdue costs credibility and cash. The shared inbox is the blocker, not the price. | The CSM looks up who owns and administers their n8n instance (names and emails from our product data), so we have real people to contact instead of the shared inbox. I phone and email a named person and agree a signing date. The manager confirms the grace period before access is restricted. | Me + CSM | 21 Oct |
| 3 | **Pixelforge** | €26k | 2 Nov (13d) | Auto-renewal will fail on the expired card. That is involuntary churn on a green account. | The CSM gets the billing contact today. I send a secure card-update link, or switch them to invoice. Finance holds dunning. It renews at €26k. | CSM + Me + Finance | 22 Oct |
| 4 | **Halden Health** | €45k | 7 Nov (18d) | Red account, usage −35%, champion gone, nobody knows the new owner | **Escalate today** to my manager and VP CS. The CSM and an exec sponsor meet the new owner this week, with a value review before any quote. Legal checks whether the cancellation-notice date (8 Oct) passed without notice. I prepare a right-sized option at list price. | CSM (lead) + Me | 23 Oct |
| 5 | **Tessera Finance** | €50k | 18 Nov (29d) | MSA redlines open since September and a security review not yet started. Both can block the PO. | **Escalate today** to Legal. I get the list of open redlines, sort out the few that block their PO, and agree our positions on those with Legal in advance. One joint redline call (their legal, ours, me) with a response deadline of **30 Oct**. I send the quote and security pack today (SOC 2, pen-test summary, DPA, sub-processors), so the security review runs in parallel. **Fallback**, agreed with Legal and Finance now: a 1–2 month extension at current terms if the MSA isn't signed by 18 Nov. | Legal + Me | 23 Oct |
| 6 | **Brightloop** | €36k | 14 Dec (55d) | Live negotiation, and procurement is setting the pace | Reply to Sam today (see Part 2). Get Finance pre-approval before the call. Call Sam and Priya on 22–23 Oct. Target signature 30 Nov. | Me | **Today** |
| 7 | **Marlowe Insurance** | €46k | 9 Dec (50d) | Insurance procurement is slow. Without the questionnaire and DPA there is no PO. | Send the standard DPA and the questionnaire, answered from the trust centre (AI first draft, Security reviews). Send the quote with it. Ask for their PO lead time and work back from 9 Dec. | Me + Legal | 27 Oct |
| 8 | **Kestrel Analytics** | €35k | 28 Nov (39d) | Usage +40%, close to the execution cap. Expansion, and a risk of throttling. | The CSM runs a usage review. I send two quotes: like-for-like (€35k) and the next execution tier. If the upsell slows things down, we sign the renewal and add the upsell later as an amendment. | CSM + Me | 28 Oct |
| 9 | **Lumen Retail** | €28k | 21 Nov (32d) | Auto-renewal, but the invoice would go to the wrong entity. Cancellation deadline 22 Oct (assumed 30 days). | Get the new entity's name, VAT number and address. Legal decides whether this is a billing change (affiliate) or an assignment (new order form). Finance updates billing before the invoice run. | Me + Finance | 22 Oct |
| 10 | **Quanta Labs** | €40k | 19 Dec (60d) | Auto-renewal, usage −20%, budget cuts in Q1, two check-ins unanswered | The CSM and exec sponsor go in through a new contact (economic buyer or finance). I confirm the cancellation-notice date (~19 Nov). I offer an in-policy **2-year price lock** or a right-size *before* they decide to cancel. | CSM + Me | 30 Oct |

### Escalations I raise today

1. **Halden Health (€45k, red, 18 days).** To my manager and VP CS. I need an exec sponsor on a call with the new owner this week.
2. **Tessera Finance (€50k).** To the Legal lead: redlines have been open for 6+ weeks, and I need a response by 30 Oct, our positions on the PO-blocking clauses agreed in advance, and the extension fallback approved.
3. **Vantage Freight (€21k, overdue).** To my manager: what is our grace period before access is restricted? I'd propose day 14 for exec-to-exec contact and day 30 for formal notice under the contract.
4. **Brightloop.** Not an escalation, but a pre-approval request to Finance (up to 12% on a 2-year deal, net 60). I want room to trade during the call.
5. **Process.** Five manual renewals inside 60 days have no quote on record, which breaks the quote policy. The fix is a 60-day quote task and alert in the CRM, plus Part 3, which sends the approved quote and chases the signature.

## Forecast: driven by Renewal Status × countdown

Each renewal's **Renewal Status** is set from *what we know* today. Its probability comes from the status × days-to-renewal matrix. For manual renewals, late statuses rise as the date gets closer and early statuses fall, because no progress near the date is the risk. **Auto-renewals have their own statuses** (Renewing: no blockers · Billing blocker · At risk before or after the notice deadline · Notice received). On those, an open blocker or risk lowers the probability as the date approaches. **Weighted new ARR = new ARR from the product lines × probability.**

| Customer | Days | What we know | Status today | Prob. | New ARR | Weighted | Bucket |
|---|---|---|---|---|---|---|---|
| Vantage Freight | −5 | Quote sent 1 Sep, no reply | Quoted | 50% (overdue) | €21,000 | €10,500 | Late |
| Northwind Logistics | 9 | No quote; champion says "just send it"; signatory unknown | Engaging customer | 25% | €48,000 | €12,000 | Late |
| Pixelforge (auto) | 13 | Card expired, billing contact unknown | Billing blocker | 60% | €26,000 | €15,600 | Late |
| Halden Health | 18 | Champion left; new owner not met | Not started | 10% | €30,000 | €3,000 | Late |
| Tessera Finance | 29 | MSA redlines; security review | Negotiation | 40% | €50,000 | €20,000 | Late |
| Lumen Retail (auto) | 32 | Invoice to a different entity | Billing blocker | 70% | €28,000 | €19,600 | On time |
| Kestrel Analytics | 39 | Near execution cap | Not started | 20% | €35,000 | €7,000 | On time |
| Marlowe Insurance | 50 | Needs questionnaire and DPA for a PO | Engaging customer | 35% | €46,000 | €16,100 | On time |
| Brightloop | 55 | Live negotiation | Negotiation | 50% | €32,400 | €16,200 | On time |
| Quanta Labs (auto) | 60 | Usage −20%, silent, Q1 budget cuts | At risk: before notice deadline | 40% | €32,000 | €12,800 | On time |
| **Total** | | | | | **€348,400** | **€132,800** | |

**Overdue rule.** Overdue renewals use their own, lower probability column and are always **Late**. They still count in the quarter **only if the expected close date is on or before quarter end**. Vantage is overdue since 15 Oct but expected by 6 Nov, so it counts in Q4. A renewal that slips past quarter end counts 0% for that quarter and returns next quarter as a late renewal. So I report two numbers: **quarter retention** (did we keep the revenue?) and **on-time rate** (did we close by the renewal date?).

**Notice deadlines.** The brief gives a 30-day cancellation notice only for Halden (deadline 8 Oct, already passed). For the three auto-renewals I've **assumed 30 days**, to confirm against each contract. That gives Pixelforge 3 Oct (passed), Lumen 22 Oct (in two days; low risk, as they are green and growing) and Quanta ~19 Nov. The 5% uplift is contractual, announced to all customers in one notice each January, and already included in every renewal value.

**Usage rule.** n8n prices by workflow executions, not users.

- **Over-usage** (+20% or more, e.g. Kestrel at +40%): renew as is, open a linked Upsell opportunity, and set a task to propose the right tier. No automatic charge unless the contract has an overage clause. It's upside, not in the forecast.
- **Under-usage** (−20% or more, e.g. Halden and Quanta): flag the CSM for an adoption plan. Auto-renewals move to *At risk*.

| Q4 forecast (today) | Weighted new ARR | Unweighted |
|---|---|---|
| **On time** | **€72k** | €173k (5 renewals) |
| **Late, still in Q4** (overdue, or still early or blocked inside 30 days) | **€61k** | €175k (Vantage, Northwind, Pixelforge, Halden, Tessera) |
| Slips past quarter end | €0 | none today |
| **Total weighted forecast** | **€133k** | €348k |

### Forecast of the forecast: with action vs no action

The probability depends on status **and** days to renewal, so the forecast moves even if nobody does anything. On **30 Oct** every renewal is 10 days closer:

- <span style="color:#1e7b34">**With this week's actions**</span>, each status moves to the target below.
- <span style="color:#b42318">**With no action**</span>, statuses stay where they are and the countdown alone lowers the early ones.

| Customer | Today → target by 30 Oct | Weighted today | 🔴 No action, 30 Oct | 🟢 With actions, 30 Oct |
|---|---|---|---|---|
| Northwind | Engaging → PO received (signature 27 Oct) | €12,000 | <span style="color:#b42318">€4,800</span> | <span style="color:#1e7b34">€45,600</span> |
| Tessera | Negotiation → Quoted (quote and security pack out, redline call booked) | €20,000 | <span style="color:#b42318">€20,000</span> | <span style="color:#1e7b34">€37,500</span> |
| Kestrel | Not started → Quoted | €7,000 | <span style="color:#b42318">€3,500</span> | <span style="color:#1e7b34">€26,250</span> |
| Marlowe | Engaging → Quoted | €16,100 | <span style="color:#b42318">€16,100</span> | <span style="color:#1e7b34">€32,200</span> |
| Pixelforge | Billing blocker → Renewing: no blockers (card updated) | €15,600 | <span style="color:#b42318">€15,600</span> | <span style="color:#1e7b34">€25,220</span> |
| Lumen | Billing blocker → Renewing: no blockers (entity fixed) | €19,600 | <span style="color:#b42318">€16,800</span> | <span style="color:#1e7b34">€27,160</span> |
| Vantage | Quoted → Waiting for PO (named signer) | €10,500 | <span style="color:#b42318">€10,500</span> | <span style="color:#1e7b34">€14,700</span> |
| Halden | Not started → Engaging customer (new owner met) | €3,000 | <span style="color:#b42318">€3,000</span> | <span style="color:#1e7b34">€7,500</span> |
| Brightloop, Quanta | No change this week | €29,000 | <span style="color:#b42318">€29,000</span> | <span style="color:#1e7b34">€29,000</span> |
| **Total** | | **€133k** | <span style="color:#b42318">**€119k**</span> | <span style="color:#1e7b34">**€245k**</span> |

- **Doing nothing costs about €13.5k of forecast in 10 days** (€133k → €119k). Northwind turns overdue and Kestrel and Lumen move into their last 30 days.
- **This week's actions add about €112k** (€133k → €245k). Against doing nothing, that's **€126k of difference on 30 Oct**.
- Northwind, Tessera, Kestrel and Marlowe carry about €86k of the gain, which is why they sit at the top of the triage.

**Lost.** This comes from the product lines, and churn is split by type:

| | Amount | Accounts |
|---|---|---|
| **Regrettable** churn/contraction (revenue lost to n8n for good) | **−€23k** | Halden −€15k (right-sized), Quanta −€8k (budget cut) |
| **Non-regrettable** (a line churns but is replaced by another n8n product, e.g. self-hosted Enterprise → n8n Cloud) | €0 | none in this slice |
| Price concession below current price | −€3.6k | Brightloop (ramp year 1, 10% off) |

- **Gross retention 92.9%** (base less regrettable churn and concessions). Every renewal value already includes the 5% uplift, so nothing is added on top.
- **Kestrel upsell is upside, not in the forecast.** It's worth roughly +€10–15k if they move up a tier.
- The gap between €348k and the €133k weighted forecast is **risk, not loss**. Moving each deal to the next status closes it, which is what the ranked actions above are for.

### The number I'm least sure about: Lost (€23k regrettable)

Halden alone ranges from €0 to €45k. There's no relationship with the new owner, usage is down 35%, and I don't yet know whether the 8 Oct notice date locked in the renewal. Quanta is second: if a cancellation notice lands before ~19 Nov (an assumed 30-day notice), that's €40k, not €8k. On timing, **Tessera** is the least certain: Late versus on time depends on Legal and their security team.

## How the CRM supports this

Statuses, the probability matrix, product lines (renewal, upsell, downgrade, churn, with original vs new ARR), the uplift (built into the renewal value) and price lock, churn category and reason, alerts and reports all live in Salesforce. **The full design is in the appendix (`crm_design_appendix.pdf`), and `renewal_tracker.xlsx` is a working mock-up of it.**
