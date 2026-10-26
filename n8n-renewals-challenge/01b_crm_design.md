# How the renewal process lives in the CRM (Salesforce)

The forecast, statuses, product lines, churn and alerts in Part 1 are CRM fields, formulas and Flows. They are not a spreadsheet, and not a separate tool. `renewal_tracker.xlsx` is a mock-up of this design. Outside the CRM, n8n only sends the approved CPQ quote, updates the status and chases the signature (Part 3). It never prices anything.

| Workbook tab | Lives in Salesforce as |
|---|---|
| Triage | List view on Renewal opportunities, sorted by Priority and ARR at risk |
| Pipeline | Opportunity (Renewal record types: Manual and Auto) |
| Products | Opportunity Product (line items): the Renewals Manager sets the line type and new numbers only |
| Opp summary | Roll-ups and the Churn section on the Opportunity |
| Monthly report | Summary report grouped by Renewal Quarter and Renewal Month, filterable by CSM and Region |
| Probability | Renewal probability formula (or a Custom Metadata matrix) |

## 1. Renewal lifecycle

1. When the current renewal is closed won, the owner ticks **Create renewal opportunity** on the close screen. It is required, unless the contract is ending.
2. A Flow creates the **next renewal opportunity** straight away:
   - Renewal Date = **service start date of the next term** (current contract end + 1 day).
   - Each product line is copied with **Original ARR = the ARR just closed × 1.05** (the contractual uplift is in the renewal value from day one).
   - Renewal Type, Notice Period, CSM and Region are copied from the contract and account.
3. The renewal therefore exists for the whole year. It sits in *Not started* (manual) or *Renewing: no blockers* (auto) until the tasks in section 6 bring it forward.

## 2. Renewal opportunity

**Core and forecast** (maintained by Renewals; the formulas are automatic)

| Field | Type | Logic |
|---|---|---|
| Renewal Date | Date | Service start date of the next term (contract end + 1). Never edited by reps. |
| Close Date (standard) | Date | **Expected** close date, kept up to date by the owner. Drives the in-quarter rule and standard forecasting. |
| Renewal Type | Picklist | Manual · Auto. Sets the record type, so each type gets its own status path. |
| Renewal Status | Picklist (values depend on record type) | **Manual:** Not started · Engaging customer · Negotiation · Quoted · Waiting for PO · PO received · **Closed won** (new) · Cancelled. **Auto:** Renewing: no blockers · Billing blocker · At risk: before notice deadline · At risk: notice deadline passed · Notice received · Renewed · Cancelled. Each has written exit criteria and the evidence rules in section 5. |
| Term (years), Payment Schedule | Number, picklist (Annual · Upfront) | Drive the uplift rule in section 3. |
| Notice Period (days) | Number | From the contract: how long before the Renewal Date the customer must give notice to cancel. |
| Notice Deadline | Formula (date) | `Renewal_Date__c - Notice_Period_Days__c` |
| Days to Renewal | Formula (number) | `Renewal_Date__c - TODAY()` |
| Renewal Window | Formula (text) | `IF(Days_to_Renewal__c < 0, "Overdue", IF(Days_to_Renewal__c <= 30, "0-30", IF(Days_to_Renewal__c <= 60, "31-60", IF(Days_to_Renewal__c <= 90, "61-90", ">90"))))` |
| Overdue | Formula (checkbox) | `AND(Days_to_Renewal__c < 0, NOT(IsClosed))` |
| Renewal Month, Renewal Quarter, Quarter End | Formulas | `TEXT(YEAR(Renewal_Date__c)) & "-" & LPAD(TEXT(MONTH(Renewal_Date__c)), 2, "0")` · `"Q" & TEXT(CEILING(MONTH(Renewal_Date__c) / 3)) & " " & TEXT(YEAR(Renewal_Date__c))` · `ADDMONTHS(DATE(YEAR(Renewal_Date__c), CEILING(MONTH(Renewal_Date__c) / 3) * 3, 1), 1) - 1` |
| Renewal Probability | Formula (percent) | Renewal Status × Renewal Window. See below. |
| Counts in Quarter | Formula (checkbox) | `CloseDate <= Quarter_End__c` |
| Forecast Probability | Formula (percent) | `IF(Counts_in_Quarter__c, Renewal_Probability__c, 0)` |
| Weighted New ARR | Formula (currency) | `New_ARR__c * Forecast_Probability__c` |
| ARR at Risk | Formula (currency) | `New_ARR__c * (1 - Renewal_Probability__c)` |
| Forecast Bucket | Formula (text) | On time / Late / Slips quarter / Lost. See below. |
| Target Status, Target Date, Target Probability, Weighted After Actions | Picklist, date, formulas | Where the next actions should take the renewal, and the **forecast of the forecast** that results. |

**Triage** (replaces a typed-in rank, which goes stale within days)

| Field | Type | Logic |
|---|---|---|
| Priority | Formula (text) | **P1:** overdue, Escalate Today ticked, or ≤30 days and still early or blocked. **P2:** ≤60 days and not yet Quoted (manual) or not *Renewing: no blockers* (auto). **P3:** everything else. The triage list sorts by Priority, then ARR at Risk. |
| Next Action, Next Action Owner (Renewals · CSM · Finance · Legal), Next Action Due | Text, picklist, date | Kept current by the owner |
| Escalate Today, Escalation Note | Checkbox, text | Feeds the daily escalation email |

**CSM section** (maintained by the CSM)

| Field | Type | Logic |
|---|---|---|
| CSM, Region | Lookup, formula | From the account. Used to filter every report. |
| Health | Picklist | Green · Yellow · Red |
| Usage Change 90d | Percent | From product usage data (workflow executions), synced daily |
| Usage Signal | Formula (text) | `IF(Usage_Change_90d__c >= 0.2, "Over-usage", IF(Usage_Change_90d__c <= -0.2, "Under-usage", ""))` |
| Adoption Plan | Text | Required when Usage Signal = Under-usage |

**Churn section** (on the opportunity, not on the product lines)

| Field | Type | Logic |
|---|---|---|
| Churned Amount | Roll-up (currency) | SUM of the Downgrade line changes, plus the Original ARR of Churn lines. A negative number. |
| Churn Category | Picklist | **Regrettable**: revenue lost to n8n for good. **Non-regrettable**: the revenue is kept elsewhere at n8n. Required when Churned Amount < 0. |
| Churn Reason | Dependent picklist | **Regrettable:** Budget cut · Price · Competitor · Moved to free Community edition · Product gaps · Support or service · Low adoption / champion left · Company closed. **Non-regrettable:** Migrated to another n8n product (e.g. self-hosted → n8n Cloud) · Consolidated into another n8n contract (merger, acquired by an existing customer) · Moved to another legal entity. |
| Churn Notes | Text | Context for win-back and product feedback |

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
  "Renewing: no blockers",           CASE(Renewal_Window__c, "Overdue", 0.40, "0-30", 0.97, "31-60", 0.95, "61-90", 0.92, 0.90),
  "Billing blocker",                 CASE(Renewal_Window__c, "Overdue", 0.40, "0-30", 0.60, "31-60", 0.70, "61-90", 0.75, 0.80),
  "At risk: before notice deadline", CASE(Renewal_Window__c, "Overdue", 0.20, "0-30", 0.35, "31-60", 0.40, "61-90", 0.45, 0.50),
  "At risk: notice deadline passed", CASE(Renewal_Window__c, "Overdue", 0.50, 0.80),
  "Notice received",                 CASE(Renewal_Window__c, "Overdue", 0, 0.10),
  "Renewed", 1,
  0)
```

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

## 3. Product lines: the Renewals Manager's only inputs

The Renewals Manager (who owns the renewal) edits **two things per line**: the **Line Type** (Renewal · Upsell · Downgrade · Churn) and the **new numbers** (Change at List, or the new quantity or plan). Salesforce recalculates everything else.

| Field | Who | Logic |
|---|---|---|
| Line Type | **Renewals Manager** | Renewal · Upsell · Downgrade · Churn |
| Change at List | **Renewals Manager** | + for upsell, − for downgrade, at the list price of the new plan |
| Original ARR (renewal value) | Automatic | Set when the opportunity is created: **ARR just closed × 1.05**, so the contractual uplift is already in. Locked. Every report and forecast uses this number; the uplift is never added on top later. |
| Year-1 uplift waiver | Renewals | The 5% is already in the renewal value. Waiving it is an exception (e.g. three years paid upfront), counts as a discount, and goes to approval under policy C. |
| Year 2+ Uplift | Automatic | Multi-year **paid upfront → price locked** (0% from year 2). Multi-year **paid annually → 5% every year**. |
| Discount (standard) | Renewals | Measured against the renewal value (uplift included) |
| List Renewal Price | Formula | `IF(ISPICKVAL(Line_Type__c, "Churn"), 0, Original_ARR__c + Change_at_List__c)` |
| New ARR | Formula | `List_Renewal_Price__c * (1 - BLANKVALUE(Discount, 0))`. A Flow copies it to Sales Price, so the Opportunity Amount equals new ARR. |
| Δ vs Original, Δ Indicator | Formula | `New_ARR__c - Original_ARR__c`, with `IMAGE(IF(Delta_ARR__c >= 0, "/img/samples/color_green.gif", "/img/samples/color_red.gif"), "", 12, 12)`: **green for growth, red for contraction** |
| Approval Required | Formula | Policy C, using the line Discount with the opportunity's Term and Payment Terms: None / Finance / VP Customer Success |

**Upsell = its own opportunity.** When the Renewals Manager sets a line to Upsell, or Usage Signal = Over-usage, a Flow opens a linked **Upsell opportunity** (Expansion record type) for the added ARR. Expansion is then forecast in its own pipeline and never inflates the renewal number. If it signs together with the renewal, both go on one order form but are booked separately.

**Roll-ups on the opportunity:** Original ARR · New ARR · Upsell (mirrors the linked Upsell opportunity) · Churned Amount · Price Concession (`MIN(0, New_ARR__c - List_Total__c)`, i.e. revenue given up below the renewal value) · Net Change and Net Change % (red/green).

## 4. Annual uplift communication

The 5% uplift is in every contract. **One bulk notice goes to all customers in January**, saying the contractual uplift applies at each renewal date. No per-renewal notice is sent. The uplifted price is shown again where the customer sees it before paying:

- **Manual renewals:** in the quote, at T−60.
- **Auto-renewals:** in an invoice preview, about 45 days before the renewal date.

## 5. Guardrails (validation rules)

| Rule | Logic |
|---|---|
| Status required | `AND(NOT(IsClosed), ISBLANK(TEXT(Renewal_Status__c)))` |
| **Quoted** needs the quote | The quote file must be uploaded to Files with Document Type = Quote. A Flow ticks Quote Attached on upload; the rule blocks Quoted while it's unticked. |
| **Waiting for PO** needs the accepted order form | Signed or accepted order form uploaded (Document Type = Order Form) |
| **PO received** needs the PO | PO Number filled and the PO file uploaded |
| **Closed won** needs closure | PO received (or signature date for no-PO customers), and the Create renewal opportunity decision made |
| Churn needs a reason | Churned Amount < 0 requires Churn Category and Churn Reason |
| No quote above policy without approval | Can't move to Quoted while Approval Required ≠ None and Approval Status ≠ Approved |
| Original ARR is locked | Editable only by admins |
| Order-form terms | Auto-renewal clause can't be removed, and termination for convenience can't be added, without an approval from Legal (and VP CS for auto-renewal) |

## 6. Alerts and tasks (Flow scheduled paths + report subscriptions)

| When | Condition | Action |
|---|---|---|
| T−90 | Open renewal | CSM task: health and usage review. Manual → Engaging customer. |
| T−60 | Manual | Renewals task: **create the quote in the CPQ**. Once it's approved, the daily renewal alert (Part 3) drafts the renewal email with it for approval. |
| T−45 | Manual, still before Quoted | Alert to Renewals and manager: quote lead time missed |
| T−45 | Auto | Invoice preview check: payment method valid, billing entity correct, uplifted price shown |
| Notice Deadline − 14 | Auto | CSM and Renewals: check cancellation risk before the customer's last day to give notice |
| Notice Deadline | Auto, At risk, no notice received | Status → *At risk: notice deadline passed* |
| Billing event | Card expired or payment failed (billing system) | Status → *Billing blocker*; task for Renewals and Finance |
| Usage sync (daily) | Over-usage | **No automatic charge** unless the contract has an overage clause. Open a linked **Upsell opportunity**, plus a CSM and Renewals task to propose the right execution tier. |
| Usage sync (daily) | Under-usage | CSM task: adoption plan. Auto → *At risk*. |
| T−30 | Manual, not yet Waiting for PO | Alert to manager; Escalate Today candidate |
| T−14 | Manual, not yet PO received | Daily reminder to the owner |
| T+1 | Overdue | Alert to manager; grace-period clock starts |
| Daily 8:00 | Report subscription with a condition | Count of P1 or Escalate Today > 0 → email to the Renewals Specialist and manager |

## 7. Reports and dashboard

Every report below can be **filtered by CSM and Region**, as well as quarter and month.

- **Renewals by Quarter and Month** (the base report): grouped by Renewal Quarter → Renewal Month. Shows count, Original ARR, New ARR, Weighted New ARR, Overdue ARR and Regrettable Churn.
- **Forecast:** Weighted New ARR by Forecast Bucket (On time · Late · Slips quarter), with quarter retention and on-time rate.
- **Forecast of the forecast:** weighted today next to Weighted After Actions, by renewal.
- **Churn:** Churned Amount by Churn Category → Churn Reason, by CSM and Region.
- **Expansion:** Upsell opportunities linked to renewals, by stage. Kept separate from the renewal forecast.
- **Triage list view:** open renewals inside 60 days, sorted by Priority then ARR at Risk, showing Next Action, Owner, Due and Escalate Today.
- **VP dashboard:**
  - gross and net retention;
  - weighted forecast against target;
  - overdue count and ARR;
  - share of renewals quoted by day 60;
  - regrettable churn by reason.
