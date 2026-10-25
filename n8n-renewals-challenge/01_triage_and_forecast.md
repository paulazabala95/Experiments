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
| 3 | **Pixelforge** | €26k | 2 Nov (13d) | Auto-renewal will fail on the expired card. That is involuntary churn on a green account. | The CSM gets the billing contact today. I send a secure card-update link, or switch them to invoice. Finance holds dunning. The 30-day uplift-notice date (3 Oct) has passed, so it renews flat. I log it as a known uplift gap. | CSM + Me + Finance | 22 Oct |
| 4 | **Halden Health** | €45k | 7 Nov (18d) | Red account, usage −35%, champion gone, nobody knows the new owner | **Escalate today** to my manager and VP CS. The CSM and an exec sponsor meet the new owner this week, with a value review before any quote. Legal checks whether the cancellation-notice date (8 Oct) passed without notice. I prepare a right-sized option at list price. | CSM (lead) + Me | 23 Oct |
| 5 | **Tessera Finance** | €50k | 18 Nov (29d) | MSA redlines open since September and a security review not yet started. Both can block the PO. | **Escalate today** to Legal with a deadline of 30 Oct for the redline response. I send the security pack today (SOC 2, pen-test summary, DPA, sub-processors). I propose renewing on the **current MSA** and negotiating the MSA in parallel, so the renewal is not held hostage. | Legal + Me | 23 Oct |
| 6 | **Brightloop** | €36k | 14 Dec (55d) | Live negotiation, and procurement is setting the pace | Reply to Sam today (see Part 2). Get Finance pre-approval before the call. Call Sam and Priya on 22–23 Oct. Target signature 30 Nov. | Me | **Today** |
| 7 | **Marlowe Insurance** | €46k | 9 Dec (50d) | Insurance procurement is slow. Without the questionnaire and DPA there is no PO. | Send the standard DPA and the questionnaire, answered from the trust centre (AI first draft, Security reviews). Send the quote with it. Ask for their PO lead time and work back from 9 Dec. | Me + Legal | 27 Oct |
| 8 | **Kestrel Analytics** | €35k | 28 Nov (39d) | Usage +40%, close to the execution cap. Expansion, and a risk of throttling. | The CSM runs a usage review. I send two quotes: like-for-like (€36.75k) and the next execution tier. If the upsell slows things down, we sign the renewal and add the upsell later as an amendment. | CSM + Me | 28 Oct |
| 9 | **Lumen Retail** | €28k | 21 Nov (32d) | Auto-renewal, but the invoice would go to the wrong entity. Notice date for the uplift is 22 Oct. | Send the uplift notice by 22 Oct. Get the new entity's name, VAT number and address. Legal decides whether this is a billing change (affiliate) or an assignment (new order form). Finance updates billing before the invoice run. | Me + Finance | 22 Oct |
| 10 | **Quanta Labs** | €40k | 19 Dec (60d) | Auto-renewal, usage −20%, budget cuts in Q1, two check-ins unanswered | The CSM and exec sponsor go in through a new contact (economic buyer or finance). I confirm the cancellation-notice date (~19 Nov). I offer an in-policy **2-year price lock** or a right-size *before* they decide to cancel. | CSM + Me | 30 Oct |

### Escalations I raise today

1. **Halden Health (€45k, red, 18 days).** To my manager and VP CS. I need an exec sponsor on a call with the new owner this week.
2. **Tessera Finance (€50k).** To the Legal lead: redlines have been open for 6+ weeks, and I need a response date of 30 Oct and agreement to renew on the current MSA.
3. **Vantage Freight (€21k, overdue).** To my manager: what is our grace period before access is restricted? I'd propose day 14 for exec-to-exec contact and day 30 for formal notice under the contract.
4. **Brightloop.** Not an escalation, but a pre-approval request to Finance (up to 12% on a 2-year deal, net 60). I want room to trade during the call.
5. **Process.** At least five manual renewals inside 60 days still have no quote, which breaks the quote policy. I'd show my manager the weekday alert (Part 3) as the fix.

## Forecast (vs. €375k base ARR)

| Bucket | Base ARR | % | New ARR incl. uplift | Accounts |
|---|---|---|---|---|
| **Closes on time** | **€248k** | 66% | €256k | Northwind, Pixelforge, Lumen, Kestrel, Marlowe, Brightloop (€33.3k kept), Quanta (€32k kept) |
| **Closes late** | **€101k** | 27% | €105k | Vantage (already late), Tessera (MSA/security), Halden (right-sized to €30k) |
| **Lost** (churn + contraction) | **€26k** | 7% | – | Halden −€15k, Quanta −€8k, Brightloop −€2.7k |

- **Gross retention 93%, net retention 96%.** The 5% uplift adds about €13k, but it is lost on Pixelforge (notice missed) and on the two downgrades.
- **Kestrel upsell is upside, not commit.** It is worth roughly +€10–15k if they move up a tier.
- **Range:** best case about €400k new ARR (everything renews with uplift, plus the Kestrel upsell). Worst case about €285k (Halden and Quanta churn, Brightloop downgrades to Tier 2).
- **Cross-check:** the system-weighted forecast (Renewal Status × days left × health) is only **€89k today**, because statuses lag the dates. If this week's actions land, it rises to **€224k on time**, which is close to my on-time call. If the two numbers stay more than 10% apart, I review those deals.

### The number I'm least sure about: Lost (€26k)

Halden alone could lose anywhere from €0 to €45k. We have no relationship with the new owner, usage is down 35%, and I don't yet know whether the notice date legally locked in the renewal. Quanta is second: it auto-renews before the Q1 cuts, so the real risk is a cancellation notice landing before ~19 Nov. My second-least-certain number is **timing on Tessera**: on time versus late depends on Legal and their security team, not on me.

## How the CRM supports this (my standard setup)

- **Renewal Status picklist** (Not started → Engaging customer → Negotiation → Quoted → Waiting for PO → PO received, plus Cancelled). I'd add **Closed won**, and give each status written exit criteria so the reps all use it the same way.
- **Probability = status × countdown.** A later status closer to the date means a higher probability. An *early* status close to the date means a *lower* one, because the cycle can't finish in time. That is the signal managers usually miss. The value is multiplied by CSM health. Auto-renewals with no blocker get an 80% floor.
- **Product lines on each renewal opportunity** are tagged *Renewal / Upsell / Downgrade / Cross-sell / Churn*. Original ARR is kept for comparison. New ARR adds the 5% uplift to the renewed base, prices any change at list, then applies the discount. The difference shows **green or red**. An approval column reads policy C (Finance or VP). The opportunity roll-up calculates churn, contraction, upsell, discount and new ARR automatically, so the forecast never relies on someone retyping a number.
- **Indexation:** the default is a 5% uplift on every 1-year renewal line. On 2-year deals, the uplift can be waived within the multi-year 5% allowance with no approval.
