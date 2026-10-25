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

The 60-day quote policy has already been missed on at least five manual renewals. That is a process gap, not a problem with individual deals, and Part 3 fixes it.

## Ranked actions

| # | Customer | ARR | Due | Why now | Next action | Owner | Date |
|---|---|---|---|---|---|---|---|
| 1 | **Northwind Logistics** | €48k | 29 Oct (9d) | Biggest near-term ARR, no quote, signed 3 days late last year | Send quote and order form for e-signature today at **€50.4k** (5% uplift). Ask the champion who signs and whether a PO is needed. Book the signature for 27 Oct. | Me | **Today** |
| 2 | **Vantage Freight** | €21k | 15 Oct (**overdue**) | Every day overdue costs credibility and cash. The shared inbox is the blocker, not the price. | The CSM pulls the instance owner and admin emails from product data. I phone and email a named person and agree a signing date. The manager confirms the grace period before access is restricted. | Me + CSM | 21 Oct |
| 3 | **Pixelforge** | €26k | 2 Nov (13d) | Auto-renewal will fail on the expired card. That is involuntary churn on a green account. | The CSM gets the billing contact today. I send a secure card-update link, or switch them to invoice. Finance holds dunning. It renews at €27.3k with the contractual 5% uplift. | CSM + Me + Finance | 22 Oct |
| 4 | **Halden Health** | €45k | 7 Nov (18d) | Red account, usage −35%, champion gone, nobody knows the new owner | **Escalate today** to my manager and VP CS. The CSM and an exec sponsor meet the new owner this week, with a value review before any quote. Legal checks whether the cancellation-notice date (8 Oct) passed without notice. I prepare a right-sized option at list price. | CSM (lead) + Me | 23 Oct |
| 5 | **Tessera Finance** | €50k | 18 Nov (29d) | MSA redlines open since September and a security review not yet started. Both can block the PO. | **Escalate today** to Legal with a deadline of 30 Oct for the redline response. I send the security pack today (SOC 2, pen-test summary, DPA, sub-processors). I propose renewing on the **current MSA** and negotiating the MSA in parallel, so the renewal is not held hostage. | Legal + Me | 23 Oct |
| 6 | **Brightloop** | €36k | 14 Dec (55d) | Live negotiation, and procurement is setting the pace | Reply to Sam today (see Part 2). Get Finance pre-approval before the call. Call Sam and Priya on 22–23 Oct. Target signature 30 Nov. | Me | **Today** |
| 7 | **Marlowe Insurance** | €46k | 9 Dec (50d) | Insurance procurement is slow. Without the questionnaire and DPA there is no PO. | Send the standard DPA and the questionnaire, answered from the trust centre (AI first draft, Security reviews). Send the quote with it. Ask for their PO lead time and work back from 9 Dec. | Me + Legal | 27 Oct |
| 8 | **Kestrel Analytics** | €35k | 28 Nov (39d) | Usage +40%, close to the execution cap. Expansion, and a risk of throttling. | The CSM runs a usage review. I send two quotes: like-for-like (€36.75k) and the next execution tier. If the upsell slows things down, we sign the renewal and add the upsell later as an amendment. | CSM + Me | 28 Oct |
| 9 | **Lumen Retail** | €28k | 21 Nov (32d) | Auto-renewal, but the invoice would go to the wrong entity. Cancellation deadline 22 Oct (assumed 30 days). | Get the new entity's name, VAT number and address. Legal decides whether this is a billing change (affiliate) or an assignment (new order form). Finance updates billing before the invoice run. | Me + Finance | 22 Oct |
| 10 | **Quanta Labs** | €40k | 19 Dec (60d) | Auto-renewal, usage −20%, budget cuts in Q1, two check-ins unanswered | The CSM and exec sponsor go in through a new contact (economic buyer or finance). I confirm the cancellation-notice date (~19 Nov). I offer an in-policy **2-year price lock** or a right-size *before* they decide to cancel. | CSM + Me | 30 Oct |

### Escalations I raise today

1. **Halden Health (€45k, red, 18 days).** To my manager and VP CS. I need an exec sponsor on a call with the new owner this week.
2. **Tessera Finance (€50k).** To the Legal lead: redlines have been open for 6+ weeks, and I need a response date of 30 Oct and agreement to renew on the current MSA.
3. **Vantage Freight (€21k, overdue).** To my manager: what is our grace period before access is restricted? I'd propose day 14 for exec-to-exec contact and day 30 for formal notice under the contract.
4. **Brightloop.** Not an escalation, but a pre-approval request to Finance (up to 12% on a 2-year deal, net 60). I want room to trade during the call.
5. **Process.** At least five manual renewals inside 60 days still have no quote, which breaks the quote policy. The fix is a 60-day quote task and alert in the CRM, plus Part 3, which makes producing the quote itself a few minutes' work.

## Forecast: driven by Renewal Status × countdown

Each renewal's **Renewal Status** is set from *what we know* today. Its probability comes from the status × days-to-renewal matrix. For manual renewals, late statuses rise as the date gets closer and early statuses fall, because no progress near the date is the risk. **Auto-renewals have their own statuses** (Renewing: no blockers · Billing blocker · At risk before or after the notice deadline · Notice received). On those, an open blocker or risk lowers the probability as the date approaches. **Weighted new ARR = new ARR from the product lines × probability.**

| Customer | Days | What we know | Status today | Prob. | New ARR | Weighted | Bucket |
|---|---|---|---|---|---|---|---|
| Vantage Freight | −5 | Quote sent 1 Sep, no reply | Quoted | 50% (overdue) | €22,050 | €11,025 | Late |
| Northwind Logistics | 9 | No quote; champion says "just send it"; signatory unknown | Engaging customer | 25% | €50,400 | €12,600 | Late |
| Pixelforge (auto) | 13 | Card expired, billing contact unknown | Billing blocker | 60% | €27,300 | €16,380 | Late |
| Halden Health | 18 | Champion left; new owner not met | Not started | 10% | €30,000 | €3,000 | Late |
| Tessera Finance | 29 | MSA redlines; security review | Negotiation | 40% | €52,500 | €21,000 | Late |
| Lumen Retail (auto) | 32 | Invoice to a different entity | Billing blocker | 70% | €29,400 | €20,580 | On time |
| Kestrel Analytics | 39 | Near execution cap | Not started | 20% | €36,750 | €7,350 | On time |
| Marlowe Insurance | 50 | Needs questionnaire and DPA for a PO | Engaging customer | 35% | €48,300 | €16,905 | On time |
| Brightloop | 55 | Live negotiation | Negotiation | 50% | €33,264 | €16,632 | On time |
| Quanta Labs (auto) | 60 | Usage −20%, silent, Q1 budget cuts | At risk: before notice deadline | 40% | €32,000 | €12,800 | On time |
| **Total** | | | | | **€361,964** | **€138,272** | |

**Overdue rule.** Overdue renewals use their own, lower probability column and are always **Late**. They still count in the quarter **only if the expected close date is on or before quarter end**. Vantage is overdue since 15 Oct but expected by 6 Nov, so it counts in Q4. A renewal that slips past quarter end counts 0% for that quarter and returns next quarter as a late renewal. So I report two numbers: **quarter retention** (did we keep the revenue?) and **on-time rate** (did we close by the renewal date?).

**Notice deadlines.** The brief gives a 30-day cancellation notice only for Halden (deadline 8 Oct, already passed). For the three auto-renewals I've **assumed 30 days**, to confirm against each contract. That gives Pixelforge 3 Oct and Lumen 22 Oct (both effectively passed), and Quanta ~19 Nov. The 5% uplift is contractual and announced to all customers in one notice each January, so it applies to the auto-renewals too.

**Usage rule.** n8n prices by workflow executions, not users.
- **Over-usage** (+20% or more, e.g. Kestrel at +40%): renew as is, add an Upsell line, and set a task to propose the right tier. No automatic charge unless the contract has an overage clause. It's upside, not in the forecast.
- **Under-usage** (−20% or more, e.g. Halden and Quanta): flag the CSM for an adoption plan. Auto-renewals move to *At risk*.

| Q4 forecast (today) | Weighted new ARR | Unweighted |
|---|---|---|
| **On time** | **€74k** | €180k (5 renewals) |
| **Late, still in Q4** (overdue, or still early or blocked inside 30 days) | **€64k** | €182k (Vantage, Northwind, Pixelforge, Halden, Tessera) |
| Slips past quarter end | €0 | none today |
| **Total weighted forecast** | **€138k** | €362k |

### Forecast of the forecast

Each action in the triage moves a status. If this week's actions land, this is the forecast on **30 Oct**:

| Customer | Today → target by 30 Oct | Weighted today | Weighted 30 Oct |
|---|---|---|---|
| Northwind | Engaging → PO received (signature 27 Oct) | €12,600 | €47,880 |
| Tessera | Negotiation → Quoted (renewal on the current MSA) | €21,000 | €39,375 |
| Kestrel | Not started → Quoted | €7,350 | €27,563 |
| Marlowe | Engaging → Quoted | €16,905 | €33,810 |
| Pixelforge | Billing blocker → Renewing: no blockers (card updated) | €16,380 | €26,481 |
| Lumen | Billing blocker → Renewing: no blockers (entity fixed) | €20,580 | €28,518 |
| Vantage | Quoted → Waiting for PO (named signer) | €11,025 | €15,435 |
| Halden | Not started → Engaging customer (new owner met) | €3,000 | €7,500 |
| Brightloop, Quanta | No change this week | €29,432 | €29,432 |
| **Total** | | **€138k** | **€256k** |

**This week's actions are worth about €118k of weighted forecast.** Northwind, Tessera, Kestrel and Marlowe carry about €91k of that, which is why they sit at the top of the triage.

**Lost.** This comes from the product lines, and churn is split by type:

| | Amount | Accounts |
|---|---|---|
| **Regrettable** churn/contraction (revenue lost to n8n for good) | **−€23k** | Halden −€15k (right-sized), Quanta −€8k (budget cut) |
| **Non-regrettable** (a line churns but is replaced by another n8n product, e.g. self-hosted Enterprise → n8n Cloud) | €0 | none in this slice |
| Price concession below current price | −€2.7k | Brightloop (2 years at the Finance floor) |

- **Gross retention 93%** (base less regrettable churn and concessions). **Net retention 96.5%** (new ARR / base, including the 5% uplift).
- **Kestrel upsell is upside, not in the forecast.** It's worth roughly +€10–15k if they move up a tier.
- The gap between €361k and the €221k weighted forecast is **risk, not loss**. Moving each deal to the next status closes it, which is what the ranked actions above are for.

### The number I'm least sure about: Lost (€23k regrettable)

Halden alone ranges from €0 to €45k. There's no relationship with the new owner, usage is down 35%, and I don't yet know whether the 8 Oct notice date locked in the renewal. Quanta is second: if a cancellation notice lands before ~19 Nov (an assumed 30-day notice), that's €40k, not €8k. On timing, **Tessera** is the least certain: Late versus on time depends on Legal and their security team.

## How the CRM supports this (my standard setup)

- **Renewal Status picklist** (Not started → Engaging customer → Negotiation → Quoted → Waiting for PO → PO received, plus Cancelled), with written exit criteria for each status. I'd add **Closed won**.
- **Probability = status × countdown**, as above, with separate auto-renewal statuses, an overdue column and the in-quarter rule.
- **Product lines on each renewal opportunity:** the Renewals Manager only sets the line type (*Renewal / Upsell / Downgrade / Churn*) and the new numbers. Salesforce recalculates the rest: Original ARR is kept for comparison, and new ARR adds the uplift, prices any change at list, then applies the discount. The difference shows **green or red**, and an approval column reads policy C.
- **Churn on the opportunity:** the churned amount rolls up from the lines, and the owner sets a **Churn Category** (Regrettable or Non-regrettable) and a granular **Churn Reason**. Upsell opens its own linked opportunity. Full design in `01b_crm_design.md`.
- **Indexation:** 5% on every renewal line in year 1. On multi-year deals paid upfront the price is locked from year 2; paid annually, 5% applies every year.
