# How the renewal process lives in the CRM (Salesforce)

The forecast, statuses, product lines and alerts in Part 1 are CRM fields, formulas and Flows. They are not a spreadsheet, and not a separate tool. `renewal_tracker.xlsx` is a mock-up of this design, with one tab per object. The only renewal step automated outside the CRM is quote and order-form generation (Part 3).

| Workbook tab | Lives in Salesforce as |
|---|---|
| Triage | List view on Renewal opportunities, sorted by Rank |
| Pipeline | Opportunity (Renewal record type): fields and formulas below |
| Products | Opportunity Product (line items): fields and formulas below |
| Opp summary | Roll-up summary fields on the Opportunity |
| Monthly report | Summary report grouped by Renewal Quarter and Renewal Month |
| Probability | Renewal probability formula (or a Custom Metadata matrix) |

## 1. Renewal opportunity

**Created automatically** 120 days before the contract ends, from the expiring contract. A Flow copies the product lines across, with Original ARR on each line.

| Field | Type | Logic |
|---|---|---|
| Renewal Date | Date | Contract end + 1 day. Never edited by reps. |
| Close Date (standard) | Date | **Expected** close date, maintained by the owner. Drives the in-quarter rule and standard forecasting. |
| Renewal Type | Picklist | Manual · Auto. From the contract. Sets the record type, so each type gets its own status path. |
| Renewal Status | Picklist (values depend on record type) | **Manual:** Not started · Engaging customer · Negotiation · Quoted · Waiting for PO · PO received · **Closed won** (new) · Cancelled. **Auto:** Renewing: no blockers · Billing blocker · At risk: before notice deadline · At risk: notice deadline passed · Notice received · Renewed · Cancelled. Each has written exit criteria. |
| Notice Period (days) | Number | From the contract. On an auto-renewal, this is the deadline for the customer to cancel and for us to send the uplift notice. |
| Notice Deadline | Formula (date) | `Renewal_Date__c - Notice_Period_Days__c` |
| Usage Change 90d | Percent | From the product usage data (workflow executions), synced daily |
| Usage Signal | Formula (text) | `IF(Usage_Change_90d__c >= 0.2, "Over-usage", IF(Usage_Change_90d__c <= -0.2, "Under-usage", ""))`. Drives the usage rule in section 5. |
| Days to Renewal | Formula (number) | `Renewal_Date__c - TODAY()` |
| Renewal Window | Formula (text) | `IF(Days_to_Renewal__c < 0, "Overdue", IF(Days_to_Renewal__c <= 30, "0-30", IF(Days_to_Renewal__c <= 60, "31-60", IF(Days_to_Renewal__c <= 90, "61-90", ">90"))))` |
| Overdue | Formula (checkbox) | `AND(Days_to_Renewal__c < 0, NOT(ISPICKVAL(Renewal_Status__c, "Closed won")), NOT(ISPICKVAL(Renewal_Status__c, "Cancelled")))` |
| Renewal Month | Formula (text) | `TEXT(YEAR(Renewal_Date__c)) & "-" & LPAD(TEXT(MONTH(Renewal_Date__c)), 2, "0")` |
| Renewal Quarter | Formula (text) | `"Q" & TEXT(CEILING(MONTH(Renewal_Date__c) / 3)) & " " & TEXT(YEAR(Renewal_Date__c))` |
| Quarter End | Formula (date) | `ADDMONTHS(DATE(YEAR(Renewal_Date__c), CEILING(MONTH(Renewal_Date__c) / 3) * 3, 1), 1) - 1` |
| Renewal Probability | Formula (percent) | Renewal Status × Renewal Window. See below. |
| Counts in Quarter | Formula (checkbox) | `CloseDate <= Quarter_End__c` |
| Forecast Probability | Formula (percent) | `IF(Counts_in_Quarter__c, Renewal_Probability__c, 0)` |
| Weighted New ARR | Formula (currency) | `New_ARR__c * Forecast_Probability__c` |
| Forecast Bucket | Formula (text) | On time / Late / Slips quarter / Lost. See below. |
| Rank, Why First, Next Action, Next Action Owner (Renewals · CSM · Finance · Legal), Next Action Due, Escalate Today, Escalation Note | Number, text, picklist, date, checkbox | The triage fields. Reviewed every Monday, and daily for P1s. |
| Target Status, Target Date | Picklist, date | Where the next actions should take the renewal, and by when. |
| Target Probability, Weighted After Actions | Formula (percent, currency) | The same probability formula, applied to Target Status and the window at Target Date. Gives the **forecast of the forecast**. |

**Renewal Probability.** For manual renewals, late statuses rise as the date gets closer and early statuses fall. For auto-renewals, a clean renewal rises as the date gets closer, and an open blocker or risk falls:

```
CASE(TEXT(Renewal_Status__c),
  "Not started",       CASE(Renewal_Window__c, "Overdue", 0.05, "0-30", 0.10, "31-60", 0.20, "61-90", 0.30, 0.35),
  "Engaging customer", CASE(Renewal_Window__c, "Overdue", 0.10, "0-30", 0.25, "31-60", 0.35, "61-90", 0.45, 0.50),
  "Negotiation",       CASE(Renewal_Window__c, "Overdue", 0.20, "0-30", 0.40, "31-60", 0.50, "61-90", 0.55, 0.55),
  "Quoted",            CASE(Renewal_Window__c, "Overdue", 0.50, "0-30", 0.75, "31-60", 0.70, "61-90", 0.65, 0.60),
  "Waiting for PO",    CASE(Renewal_Window__c, "Overdue", 0.70, "0-30", 0.90, "31-60", 0.85, "61-90", 0.80, 0.75),
  "PO received",       CASE(Renewal_Window__c, "Overdue", 0.95, "0-30", 0.99, "31-60", 0.97, "61-90", 0.95, 0.90),
  "Closed won", 1,
  "Renewing: no blockers",          CASE(Renewal_Window__c, "Overdue", 0.40, "0-30", 0.97, "31-60", 0.95, "61-90", 0.92, 0.90),
  "Billing blocker",                CASE(Renewal_Window__c, "Overdue", 0.40, "0-30", 0.60, "31-60", 0.70, "61-90", 0.75, 0.80),
  "At risk: before notice deadline", CASE(Renewal_Window__c, "Overdue", 0.20, "0-30", 0.35, "31-60", 0.40, "61-90", 0.45, 0.50),
  "At risk: notice deadline passed", CASE(Renewal_Window__c, "Overdue", 0.50, 0.80),
  "Notice received",                CASE(Renewal_Window__c, "Overdue", 0, 0.10),
  "Renewed", 1,
  0)
```

A Flow moves an auto-renewal from *At risk: before notice deadline* to *At risk: notice deadline passed* on the Notice Deadline, unless notice was received.

If Finance wants to recalibrate every quarter without an admin, the matrix can move to a Custom Metadata type, with a Flow setting the field each night.

**Forecast Bucket**

```
IF(ISPICKVAL(Renewal_Status__c, "Cancelled"), "Lost",
 IF(NOT(Counts_in_Quarter__c), "Slips quarter",
  IF(OR(Days_to_Renewal__c < 0,
        AND(Days_to_Renewal__c <= 30,
            OR(ISBLANK(TEXT(Renewal_Status__c)),
               ISPICKVAL(Renewal_Status__c, "Not started"),
               ISPICKVAL(Renewal_Status__c, "Engaging customer"),
               ISPICKVAL(Renewal_Status__c, "Negotiation"),
               ISPICKVAL(Renewal_Status__c, "Billing blocker"),
               ISPICKVAL(Renewal_Status__c, "At risk: before notice deadline"),
               ISPICKVAL(Renewal_Status__c, "Notice received")))),
     "Late", "On time")))
```

**Standard forecasting.** A Flow sets the standard Forecast Category from the bucket, so Collaborative Forecasts and the VP's roll-up use the same logic:

| Condition | Forecast Category |
|---|---|
| On time and probability ≥ 85% | Commit |
| On time or Late | Best Case |
| Slips quarter | Pipeline |
| Cancelled | Omitted |

## 2. Opportunity product (line item)

| Field | Type | Logic |
|---|---|---|
| Line Type | Picklist | Renewal · Upsell · Downgrade · Cross-sell · Churn |
| Original ARR | Currency | Copied from the expiring contract. **Locked** after creation (validation rule). Kept for comparison. |
| Change at List | Currency | + for upsell or cross-sell, − for downgrade, at the list price of the new plan |
| Uplift % | Percent | Set by Flow: **5%** on Renewal lines, 0 on others. Can be waived on 2-year terms within the 5% multi-year allowance. |
| Discount (standard) | Percent | Measured against the uplifted list price |
| List Renewal Price | Formula (currency) | `IF(ISPICKVAL(Line_Type__c, "Churn"), 0, Original_ARR__c * (1 + Uplift_Pct__c) + Change_at_List__c)` |
| New ARR | Formula (currency) | `List_Renewal_Price__c * (1 - BLANKVALUE(Discount, 0))`. A Flow copies it to Sales Price, so the Opportunity Amount equals new ARR. |
| Δ vs Original | Formula (currency) | `New_ARR__c - Original_ARR__c` |
| Δ Indicator | Formula (text) | `IMAGE(IF(Delta_ARR__c >= 0, "/img/samples/color_green.gif", "/img/samples/color_red.gif"), "", 12, 12) & " " & TEXT(Delta_ARR__c)`: **green for growth, red for contraction** |
| Replaced By | Lookup (Product) | Filled in when a churned or downgraded line moves to another n8n product (e.g. self-hosted Enterprise → n8n Cloud) |
| Churn Type | Picklist (set by Flow) | Churn or Downgrade line **with** Replaced By → **Non-regrettable**. Without it → **Regrettable**. Stored rather than calculated, so it can filter roll-ups and reports. |
| Churn Amount | Formula (currency) | `IF(ISPICKVAL(Line_Type__c, "Churn"), -Original_ARR__c, IF(ISPICKVAL(Line_Type__c, "Downgrade"), Change_at_List__c, 0))` |
| Approval Required | Formula (text) | Reads policy C, combining the line Discount with the opportunity's Term and Payment Terms: None / Finance / VP Customer Success. Drives the approval process. |

## 3. Roll-ups on the opportunity (the churn and new ARR calculation)

| Field | Roll-up |
|---|---|
| Original ARR | SUM of line Original ARR |
| New ARR | SUM of line New ARR |
| Uplift | SUM of line Uplift Amount (`Original_ARR__c * Uplift_Pct__c`) |
| Upsell / Cross-sell | SUM of Change at List where Line Type = Upsell or Cross-sell |
| Regrettable Churn | SUM of Churn Amount where Churn Type = Regrettable |
| Non-regrettable Churn | SUM of Churn Amount where Churn Type = Non-regrettable |
| Price Concession | Formula: `MIN(0, Uplift__c - (List_Total__c - New_ARR__c))`, i.e. revenue given up below today's price |
| Net Change, Net Change % | Formulas: `New_ARR__c - Original_ARR__c`, with a red/green indicator |

## 4. Guardrails (validation rules)

1. **No open renewal without a status:** `AND(NOT(IsClosed), ISBLANK(TEXT(Renewal_Status__c)))`
2. **Status matches reality:** Quoted or later requires Quote Sent Date. PO received requires a PO number or signature date.
3. **Original ARR can't be edited** after the renewal is created, except by admins.
4. **No quote above policy without approval:** status can't move to Quoted while Approval Required ≠ None and Approval Status ≠ Approved.
5. **Order-form terms:** the Auto-renewal clause can't be unchecked, and Termination for convenience can't be checked, without an approval record from Legal (and VP CS for auto-renewal).

## 5. Alerts and tasks (CRM-native: Flow scheduled paths + report subscriptions)

| When (relative to Renewal Date) | Condition | Action |
|---|---|---|
| T−90 | Open renewal | Task for the CSM: health and usage review. Status → Engaging customer. |
| T−60 | Manual renewal | Task for Renewals: **send quote**. This triggers Part 3. |
| T−45 | Manual, still before Quoted | Alert to Renewals and manager: quote lead time missed |
| Notice Deadline − 14 | Auto-renewal | Task: send the uplift notice, confirm the payment method and billing entity, check cancellation risk |
| Notice Deadline | Auto-renewal, At risk, no notice received | Status → *At risk: notice deadline passed* |
| Billing event | Card expired or payment failed (billing system) | Status → *Billing blocker*; task for Renewals and Finance |
| Usage sync (daily) | Usage Signal = Over-usage | **No automatic charge** unless the contract has an overage clause. Add an Upsell line (upside, not in the forecast), plus a task for the CSM and Renewals to propose the right execution tier. |
| Usage sync (daily) | Usage Signal = Under-usage | Task for the CSM: adoption plan. On an auto-renewal, status → *At risk*. |
| T−30 | Not yet Waiting for PO | Alert to manager; Escalate Today candidate |
| T−14 | Not yet PO received | Daily reminder to the owner |
| T+1 | Overdue | Overdue flag; alert to manager; grace-period clock starts |
| Daily 8:00 | Report subscription with a condition | "Overdue or Escalate Today count > 0" → email the Renewals Specialist and manager |

## 6. Reports and dashboard

- **Renewals by Quarter and Month:** grouped by Renewal Quarter → Renewal Month. Shows count, Original ARR, New ARR, Weighted New ARR, Overdue ARR and Regrettable Churn. This is the base report every other view filters.
- **Forecast:** Weighted New ARR by Forecast Bucket (On time · Late · Slips quarter), plus quarter retention and on-time rate.
- **Forecast of the forecast:** weighted today next to Weighted After Actions, by renewal. This shows the VP how much the plan is worth and which actions carry it.
- **Churn by type:** Opportunity Products grouped by Churn Type → Line Type → product.
- **Triage list view:** open renewals inside 60 days, sorted by Rank, showing Next Action, Owner, Due and Escalate Today.
- **Dashboard for the VP:** gross and net retention, weighted forecast against target, overdue count and ARR, and the share of renewals quoted by day 60.
