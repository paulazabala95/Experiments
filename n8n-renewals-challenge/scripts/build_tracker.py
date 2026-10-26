"""Builds renewal_tracker.xlsx: a mock-up of the CRM renewal model behind the n8n challenge.

Tabs: Read me | Pipeline | Products | Opp summary | Monthly report | Probability | Policy
All figures are fictional (from the challenge brief). "Today" is a single input cell.
"""
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

OUT = "/home/user/Experiments/n8n-renewals-challenge/renewal_tracker.xlsx"
F = "Arial"
BLUE = Font(name=F, color="0000FF")
BLACK = Font(name=F)
GREEN_LINK = Font(name=F, color="008000")
BOLD = Font(name=F, bold=True)
HDR = Font(name=F, bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="2B2B3C")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
RED_FILL = PatternFill("solid", fgColor="F8D7DA")
GRN_FILL = PatternFill("solid", fgColor="D4EDDA")
AMB_FILL = PatternFill("solid", fgColor="FFF3CD")
thin = Side(style="thin", color="D0D0D8")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
EUR = '€#,##0;[Red]-€#,##0;"-"'
PCT = '0%;[Red]-0%;"-"'
DATE = "dd mmm yyyy"
WRAP = Alignment(wrap_text=True, vertical="top")

wb = Workbook()


def header(ws, row, cols, widths=None):
    for i, h in enumerate(cols, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font, c.fill, c.border = HDR, HDR_FILL, BOX
        c.alignment = Alignment(wrap_text=True, vertical="center")
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 32


def style_range(ws, r1, r2, c1, c2):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ws.cell(row=r, column=c).border = BOX


def inp(cell):
    cell.font, cell.fill = BLUE, INPUT_FILL


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = Font(name=F, bold=True, size=13)
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(name=F, italic=True)


# ---------------------------------------------------------------- Probability
pr = wb.active
pr.title = "Probability"
title(pr, "Renewal probability: Renewal Status x days to renewal",
      "Manual: late statuses (Quoted and after) rise as the date gets closer; early statuses fall. Auto-renewal: a "
      "clean renewal rises; an open blocker or risk falls as the date gets closer. Blue = editable.")
BUCKETS = ["Overdue", "0-30", "31-60", "61-90", ">90"]
header(pr, 4, ["Renewal Status"] + BUCKETS + ["Exit criteria (what must be true to be in this status)", "Applies to"],
       [30, 11, 11, 11, 11, 11, 70, 11])
MATRIX = [
    ("--None--", [0, 0, 0, 0, 0], "Not allowed. Every open renewal must have a status."),
    ("Not started", [0.05, 0.10, 0.20, 0.30, 0.35], "Renewal opportunity exists; no customer contact about the renewal yet."),
    ("Engaging customer", [0.10, 0.25, 0.35, 0.45, 0.50], "Decision maker and signatory known; renewal timeline agreed."),
    ("Negotiation", [0.20, 0.40, 0.50, 0.55, 0.55], "Commercial terms under discussion; customer asks are in writing."),
    ("Quoted", [0.50, 0.75, 0.70, 0.65, 0.60], "Final quote and order form sent and accepted by the champion."),
    ("Waiting for PO", [0.70, 0.90, 0.85, 0.80, 0.75], "Order form approved by the buyer; in their PO or signature workflow."),
    ("PO received", [0.95, 0.99, 0.97, 0.95, 0.90], "PO or signature in hand; only booking and invoicing remain."),
    ("Closed won", [1, 1, 1, 1, 1], "Signed, booked, invoiced. (Suggested addition to the picklist.)"),
    ("Cancelled", [0, 0, 0, 0, 0], "Customer gave notice or will not renew."),
    # Auto-renewals: probability depends on whether anything stands between today and a clean renewal.
    ("Renewing: no blockers", [0.40, 0.97, 0.95, 0.92, 0.90],
     "Valid payment method, correct billing entity, usage stable or growing. (Overdue = payment failed: move to Billing blocker.)"),
    ("Billing blocker", [0.40, 0.60, 0.70, 0.75, 0.80],
     "Expired card, wrong legal entity, PO required. Admin fix, usually recoverable."),
    ("At risk: before notice deadline", [0.20, 0.35, 0.40, 0.45, 0.50],
     "Usage down 20%+, silence or budget cuts, and the customer can still give notice."),
    ("At risk: notice deadline passed", [0.50, 0.80, 0.80, 0.80, 0.80],
     "Same signals, but no notice was given: the contract has renewed. Risk shifts to payment."),
    ("Notice received", [0, 0.10, 0.10, 0.10, 0.10],
     "Customer gave non-renewal or downgrade notice. Becomes a manual save negotiation."),
    ("Renewed", [1, 1, 1, 1, 1], "Invoiced and paid."),
]
AUTO_FROM = 10  # index in MATRIX where auto-renewal statuses start
for i, (s, ps, crit) in enumerate(MATRIX, start=5):
    pr.cell(row=i, column=1, value=s).font = BOLD
    for j, p in enumerate(ps, start=2):
        c = pr.cell(row=i, column=j, value=p)
        inp(c)
        c.number_format = "0%"
    pr.cell(row=i, column=7, value=crit).alignment = WRAP
    applies = "Auto" if i - 5 >= AUTO_FROM - 1 else ("Both" if s == "Cancelled" else "Manual")
    pr.cell(row=i, column=8, value=applies)
PE = 4 + len(MATRIX)  # last matrix row
style_range(pr, 5, PE, 1, 8)
pr.conditional_formatting.add(f"B5:F{PE}", FormulaRule(formula=["B5>=0.8"], fill=GRN_FILL))
pr.conditional_formatting.add(f"B5:F{PE}", FormulaRule(formula=["AND(B5>0,B5<0.4)"], fill=RED_FILL))
pr.conditional_formatting.add(f"H5:H{PE}", FormulaRule(formula=['H5="Auto"'], fill=AMB_FILL))
OV = PE + 2
pr.cell(row=OV, column=1, value="Overdue rule").font = BOLD
pr.cell(row=OV + 4, column=1, value="Usage rule").font = BOLD
pr.cell(row=OV + 4, column=2, value=(
    "n8n prices by workflow executions (users are unlimited). Usage +20% or more: renew as is, open an Upsell opportunity and a "
    "CSM + Renewals task; never auto-charge unless the contract has an overage clause. Usage -20% or more: flag the CSM "
    "for an adoption plan; on an auto-renewal, set At risk.")).alignment = WRAP
pr.merge_cells(start_row=OV + 4, start_column=2, end_row=OV + 6, end_column=7)
pr["B" + str(OV)] = ("Overdue renewals use the Overdue column and are shown as Late. They still count in the quarter's forecast "
             "only if the expected close date is on or before quarter end. If they slip past quarter end they count "
             "0% for that quarter and come back next quarter as a late renewal.")
pr["B" + str(OV)].alignment = WRAP
pr.merge_cells(start_row=OV, start_column=2, end_row=OV + 2, end_column=7)

# ------------------------------------------------------------------- Pipeline
pl = wb.create_sheet("Pipeline", 0)
title(pl, "Q4 2026 renewal pipeline: first slice (10 renewals, €375k ARR)")
pl["A2"] = "Today"
pl["A2"].font = BOLD
pl["B2"] = date(2026, 10, 20)
inp(pl["B2"])
pl["B2"].number_format = DATE
pl["B2"].comment = Comment("Exercise date: Tue 20 Oct 2026, so Vantage is overdue and the other nine fall inside "
                           "60 days. Use =TODAY() in live use.", "Renewals")
pl["D2"] = "Target date"
pl["D2"].font = BOLD
pl["E2"] = date(2026, 10, 30)
inp(pl["E2"])
pl["E2"].number_format = DATE
pl["G2"] = "Blue on yellow = input. Everything else is a formula. Columns AF-AH: the forecast after this week's actions."
pl["G2"].font = Font(name=F, italic=True)

cols = ["Customer", "Base ARR (€)", "Renewal date", "Type", "Usage 90d", "Health", "Renewal Status", "Blocker",
        "Expected close", "Days to renewal", "Window", "Overdue?", "Month", "Quarter", "Quarter end",
        "Probability", "Counts in quarter?", "Forecast prob.", "New ARR (€)", "Weighted new ARR (€)", "Forecast bucket",
        "Next action", "Owner", "Due", "Rank", "Why first", "Also involved", "Escalate today",
        "Notice period (days)", "Notice deadline", "Usage signal", "Target status by 30 Oct", "Target prob.",
        "Weighted after actions (€)"]
header(pl, 4, cols, [20, 12, 13, 8, 9, 9, 18, 28, 13, 9, 9, 9, 9, 9, 12, 10, 10, 10, 13, 14, 13, 60, 10, 12,
                     7, 50, 20, 40, 10, 13, 34, 26, 10, 14])

# Triage: rank by slack (days left vs work still needed) x ARR at risk. Owner is one of Me / CSM / Finance / Legal.
TRIAGE = {
    "Northwind Logistics": (1, "Biggest near-term ARR, 9 days out, no quote, signed 3 days late last year. One hour of work removes most of the risk.",
                            "Me", "CSM", ""),
    "Vantage Freight": (2, "Already overdue. The blocker is a shared inbox, not price: find a named person.",
                        "Me", "CSM, Manager", "Yes: Manager, to agree the grace period before access is restricted"),
    "Pixelforge": (3, "Auto-renewal fails in 13 days on an expired card: involuntary churn on a green account.",
                   "CSM", "Me, Finance", ""),
    "Halden Health": (4, "Red, usage -35%, champion gone, new owner unknown, 18 days left.",
                      "CSM", "Me, Manager, VP CS (exec sponsor)", "Yes: Manager + VP CS, exec sponsor meeting with the new owner this week"),
    "Tessera Finance": (5, "MSA redlines open since September and a security review can block the PO; 29 days left.",
                        "Legal", "Me, Security", "Yes: Legal lead, redline response by 30 Oct and renew on the current MSA"),
    "Brightloop": (6, "Live negotiation; procurement sets the pace. Reply and pre-approvals today.",
                   "Me", "Finance, Legal, CSM", ""),
    "Marlowe Insurance": (7, "Insurance procurement is slow; no DPA and questionnaire means no PO.",
                          "Me", "Legal, Security", ""),
    "Kestrel Analytics": (8, "Usage +40%, near the execution cap: expansion, and a throttling risk.",
                          "CSM", "Me", ""),
    "Lumen Retail": (9, "Auto-renewal would invoice the wrong legal entity; cancellation deadline 22 Oct (assumed 30-day notice).",
                     "Me", "Finance, Legal", ""),
    "Quanta Labs": (10, "Auto-renewal, usage -20%, Q1 budget cuts, unresponsive. 60 days, but the notice deadline is ~19 Nov (assumed 30-day notice).",
                    "CSM", "Me", ""),
}

# Status today = what we know (brief), agreed with Paula. Target = where this week's actions should get it by 30 Oct.
# Notice period: 30 days is given for Halden; for the auto-renewals it is an assumption to confirm against the contract.
STATUS = {
    "Vantage Freight": ("Quoted", "Waiting for PO", None),
    "Northwind Logistics": ("Engaging customer", "PO received", None),
    "Pixelforge": ("Billing blocker", "Renewing: no blockers", 30),
    "Halden Health": ("Not started", "Engaging customer", 30),
    "Brightloop": ("Negotiation", "Negotiation", None),
    "Tessera Finance": ("Negotiation", "Quoted", None),
    "Lumen Retail": ("Billing blocker", "Renewing: no blockers", 30),
    "Kestrel Analytics": ("Not started", "Quoted", None),
    "Marlowe Insurance": ("Engaging customer", "Quoted", None),
    "Quanta Labs": ("At risk: before notice deadline", "At risk: before notice deadline", 30),
}
P = [
    ("Vantage Freight", 21000, date(2026, 10, 15), "Manual", 0.00, "Yellow", "Quoted",
     "No named contact (shared inbox)", date(2026, 11, 6),
     "CSM pulls instance owner/admin emails from product data; I call and email the named person and agree a signing "
     "date. Manager confirms the grace period before access is restricted.", "Me + CSM", date(2026, 10, 21)),
    ("Northwind Logistics", 48000, date(2026, 10, 29), "Manual", 0.12, "Green", "Waiting for PO",
     "No quote sent; signatory unknown; signed 3 days late last year", date(2026, 10, 29),
     "Quote and order form out today at €48k for e-signature; champion confirms signatory and PO need; signature "
     "booked for 27 Oct.", "Me", date(2026, 10, 20)),
    ("Pixelforge", 26000, date(2026, 11, 2), "Auto", 0.00, "Green", "Waiting for PO",
     "Card expired; billing contact unknown", date(2026, 11, 2),
     "CSM gets the billing contact today; I send a secure card-update link or switch to invoice; Finance holds "
     "dunning. Renews at €26k (renewal value).", "CSM + Me", date(2026, 10, 22)),
    ("Halden Health", 45000, date(2026, 11, 7), "Manual", -0.35, "Red", "Engaging customer",
     "Champion left; new owner unknown", date(2026, 11, 20),
     "ESCALATE TODAY. CSM, me and exec sponsor meet the new owner this week. Legal checks the 8 Oct notice date. "
     "Right-sized option ready.", "CSM (lead) + Me", date(2026, 10, 23)),
    ("Brightloop", 36000, date(2026, 12, 14), "Manual", -0.10, "Yellow", "Negotiation",
     "Procurement asks: 25% off, net 60, no auto-renew, 3-month TfC", date(2026, 11, 30),
     "Reply to Sam today; Finance pre-approval (up to 12% on 2 years, net 60); call with Sam and Priya this week. "
     "Target signature 30 Nov.", "Me", date(2026, 10, 20)),
    ("Tessera Finance", 50000, date(2026, 11, 18), "Manual", 0.05, "Yellow", "Negotiation",
     "MSA redlines open since Sep; security review", date(2026, 12, 4),
     "ESCALATE TODAY to Legal: redline response by 30 Oct. Security pack today. Renew on the current MSA and "
     "negotiate the MSA in parallel.", "Legal + Me", date(2026, 10, 23)),
    ("Lumen Retail", 28000, date(2026, 11, 21), "Auto", 0.08, "Green", "Waiting for PO",
     "Invoice to a different legal entity", date(2026, 11, 21),
     "New entity details (name, VAT, address); Legal: billing change or assignment; Finance updates billing before the "
     "invoice run. Cancellation deadline 22 Oct (assumed 30 days).", "Me + Finance", date(2026, 10, 22)),
    ("Kestrel Analytics", 35000, date(2026, 11, 28), "Manual", 0.40, "Green", "Quoted",
     "Close to execution cap", date(2026, 11, 28),
     "CSM usage review; quote like-for-like (€35k) and open a linked Upsell opportunity for the next execution tier.",
     "CSM + Me", date(2026, 10, 28)),
    ("Marlowe Insurance", 46000, date(2026, 12, 9), "Manual", 0.00, "Yellow", "Quoted",
     "Vendor questionnaire + DPA needed for PO", date(2026, 12, 9),
     "Quote sent with standard DPA and questionnaire (AI first draft, Security reviews) by 27 Oct. Work back from "
     "their PO lead time.", "Me + Legal", date(2026, 10, 27)),
    ("Quanta Labs", 40000, date(2026, 12, 19), "Auto", -0.20, "Yellow", "Engaging customer",
     "Budget cuts in Q1; 2 check-ins unanswered", date(2026, 12, 19),
     "CSM and exec sponsor via a new contact; I confirm the ~19 Nov notice date; offer right-sizing or a 2-year "
     "price lock before they cancel.", "CSM + Me", date(2026, 10, 30)),
]
EARLY = '{"--None--","Not started","Engaging customer","Negotiation"}'
r0 = 5
for i, (cust, arr, rdate, typ, use, hl, status, blocker, exp, action, _, due) in enumerate(P):
    r = r0 + i
    rank, why, owner, involved, esc = TRIAGE[cust]
    status, target, notice = STATUS[cust]
    for c, v in {1: cust, 2: arr, 3: rdate, 4: typ, 5: use, 6: hl, 7: status, 8: blocker, 9: exp,
                 22: action, 23: owner, 24: due, 25: rank, 26: why, 27: involved, 28: esc,
                 29: notice, 32: target}.items():
        cell = pl.cell(row=r, column=c, value=v)
        if c != 1:
            inp(cell)
    pl.cell(row=r, column=10, value=f"=C{r}-$B$2")
    pl.cell(row=r, column=11, value=f'=IF(J{r}<0,"Overdue",IF(J{r}<=30,"0-30",IF(J{r}<=60,"31-60",IF(J{r}<=90,"61-90",">90"))))')
    pl.cell(row=r, column=12, value=f'=IF(AND(J{r}<0,G{r}<>"Closed won",G{r}<>"Cancelled"),"YES","")')
    pl.cell(row=r, column=13, value=f'=TEXT(C{r},"yyyy-mm")')
    pl.cell(row=r, column=14, value=f'="Q"&ROUNDUP(MONTH(C{r})/3,0)&" "&YEAR(C{r})')
    pl.cell(row=r, column=15, value=f"=EOMONTH(DATE(YEAR(C{r}),ROUNDUP(MONTH(C{r})/3,0)*3,1),0)")
    pl.cell(row=r, column=16, value=(f"=INDEX(Probability!$B$5:$F${PE},MATCH(G{r},Probability!$A$5:$A${PE},0),"
                                     f"MATCH(K{r},Probability!$B$4:$F$4,0))"))
    pl.cell(row=r, column=17, value=f'=IF(I{r}<=O{r},"Yes","No")')
    pl.cell(row=r, column=18, value=f'=IF(Q{r}="Yes",P{r},0)')
    pl.cell(row=r, column=19, value=f"=SUMIFS(Products!$K:$K,Products!$A:$A,A{r})")
    pl.cell(row=r, column=20, value=f"=S{r}*R{r}")
    pl.cell(row=r, column=21, value=(f'=IF(G{r}="Cancelled","Lost",IF(Q{r}="No","Slips quarter",'
                                     f'IF(OR(J{r}<0,AND(J{r}<=30,OR(G{r}="--None--",G{r}="Not started",'
                                     f'G{r}="Engaging customer",G{r}="Negotiation",G{r}="Billing blocker",'
                                     f'G{r}="At risk: before notice deadline",G{r}="Notice received"))),"Late","On time")))'))
    pl.cell(row=r, column=30, value=f'=IF(AC{r}="","",C{r}-AC{r})')
    pl.cell(row=r, column=31, value=(f'=IF(E{r}>=0.2,"Over-usage: open Upsell opp + CSM/Renewals task",'
                                     f'IF(E{r}<=-0.2,"Under-usage: flag CSM"&IF(D{r}="Auto","; set At risk",""),""))'))
    tw = (f'IF(C{r}-$E$2<0,"Overdue",IF(C{r}-$E$2<=30,"0-30",IF(C{r}-$E$2<=60,"31-60",'
          f'IF(C{r}-$E$2<=90,"61-90",">90"))))')
    pl.cell(row=r, column=33, value=(f"=IF(I{r}<=O{r},INDEX(Probability!$B$5:$F${PE},MATCH(AF{r},Probability!$A$5:$A${PE},0),"
                                     f"MATCH({tw},Probability!$B$4:$F$4,0)),0)"))
    pl.cell(row=r, column=34, value=f"=S{r}*AG{r}")
    inp(pl.cell(row=r, column=29))
    inp(pl.cell(row=r, column=32))
    pl.cell(row=r, column=30).number_format = DATE
    pl.cell(row=r, column=33).number_format = PCT
    pl.cell(row=r, column=34).number_format = EUR
    for c in (2, 19, 20):
        pl.cell(row=r, column=c).number_format = EUR
    for c in (3, 9, 15, 24):
        pl.cell(row=r, column=c).number_format = DATE
    for c in (5, 16, 18):
        pl.cell(row=r, column=c).number_format = PCT
    for c in (8, 22, 26, 27, 28, 31, 32):
        pl.cell(row=r, column=c).alignment = WRAP
    pl.row_dimensions[r].height = 48
rN = r0 + len(P) - 1
style_range(pl, r0, rN, 1, 34)
t = rN + 1
pl.cell(row=t, column=1, value="Total").font = BOLD
for c in (2, 19, 20, 34):
    L = get_column_letter(c)
    cell = pl.cell(row=t, column=c, value=f"=SUM({L}{r0}:{L}{rN})")
    cell.font, cell.number_format = BOLD, EUR

for rng, f1 in (("G", f"=Probability!$A$5:$A${PE}"), ("AF", f"=Probability!$A$5:$A${PE}"), ("F", '"Green,Yellow,Red"'), ("D", '"Manual,Auto"'),
                ("W", '"Me,CSM,Finance,Legal"')):
    dv = DataValidation(type="list", formula1=f1)
    pl.add_data_validation(dv)
    dv.add(f"{rng}{r0}:{rng}{rN}")

pl.conditional_formatting.add(f"L{r0}:L{rN}", FormulaRule(formula=[f'L{r0}="YES"'], fill=RED_FILL, font=Font(name=F, bold=True, color="9C0006")))
pl.conditional_formatting.add(f"K{r0}:K{rN}", FormulaRule(formula=[f'K{r0}="0-30"'], fill=AMB_FILL))
pl.conditional_formatting.add(f"F{r0}:F{rN}", FormulaRule(formula=[f'F{r0}="Red"'], fill=RED_FILL))
pl.conditional_formatting.add(f"F{r0}:F{rN}", FormulaRule(formula=[f'F{r0}="Green"'], fill=GRN_FILL))
pl.conditional_formatting.add(f"P{r0}:P{rN}", CellIsRule(operator="lessThan", formula=["0.4"], fill=RED_FILL))
pl.conditional_formatting.add(f"P{r0}:P{rN}", CellIsRule(operator="greaterThanOrEqual", formula=["0.8"], fill=GRN_FILL))
pl.conditional_formatting.add(f"Q{r0}:Q{rN}", FormulaRule(formula=[f'Q{r0}="No"'], fill=RED_FILL))
pl.conditional_formatting.add(f"U{r0}:U{rN}", FormulaRule(formula=[f'U{r0}="Late"'], fill=AMB_FILL))
pl.conditional_formatting.add(f"U{r0}:U{rN}", FormulaRule(formula=[f'OR(U{r0}="Lost",U{r0}="Slips quarter")'], fill=RED_FILL))
pl.conditional_formatting.add(f"U{r0}:U{rN}", FormulaRule(formula=[f'U{r0}="On time"'], fill=GRN_FILL))
pl.conditional_formatting.add(f"AB{r0}:AB{rN}", FormulaRule(formula=[f'LEFT(AB{r0},3)="Yes"'], fill=RED_FILL, font=Font(name=F, bold=True, color="9C0006")))
# Status must belong to the renewal type (manual vs auto)
for Lc in ("G", "AF"):
    pl.conditional_formatting.add(f"{Lc}{r0}:{Lc}{rN}", FormulaRule(
        formula=[f'AND({Lc}{r0}<>"",INDEX(Probability!$H$5:$H${PE},MATCH({Lc}{r0},Probability!$A$5:$A${PE},0))<>"Both",'
                 f'INDEX(Probability!$H$5:$H${PE},MATCH({Lc}{r0},Probability!$A$5:$A${PE},0))<>$D{r0})'],
        fill=RED_FILL))
pl.conditional_formatting.add(f"AE{r0}:AE{rN}", FormulaRule(formula=[f'LEFT(AE{r0},5)="Under"'], fill=AMB_FILL))
pl.conditional_formatting.add(f"AE{r0}:AE{rN}", FormulaRule(formula=[f'LEFT(AE{r0},4)="Over"'], fill=GRN_FILL))
pl.conditional_formatting.add(f"AD{r0}:AD{rN}", FormulaRule(formula=[f'AND(AD{r0}<>"",AD{r0}<$B$2)'], fill=RED_FILL))
pl.freeze_panes = "B5"

# Forecast block
f0 = t + 3
pl.cell(row=f0, column=1, value="Q4 forecast vs €375k base ARR").font = Font(name=F, bold=True, size=12)
for j, h in enumerate(["Bucket", "Weighted new ARR (€)", "Unweighted new ARR (€)", "Accounts"], 1):
    c = pl.cell(row=f0 + 1, column=j, value=h)
    c.font, c.fill, c.border = HDR, HDR_FILL, BOX
U = f"U{r0}:U{rN}"
rows = [("On time", "On time"), ("Late, still in quarter", "Late"), ("Slips past quarter end (0%)", "Slips quarter")]
for k, (lbl, key) in enumerate(rows):
    r = f0 + 2 + k
    pl.cell(row=r, column=1, value=lbl)
    pl.cell(row=r, column=2, value=f'=SUMIFS(T{r0}:T{rN},{U},"{key}")').number_format = EUR
    pl.cell(row=r, column=3, value=f'=SUMIFS(S{r0}:S{rN},{U},"{key}")').number_format = EUR
    pl.cell(row=r, column=4, value=f'=COUNTIFS({U},"{key}")&" renewals"')
r = f0 + 5
pl.cell(row=r, column=1, value="Total forecast (weighted)").font = BOLD
pl.cell(row=r, column=2, value=f"=SUM(B{f0+2}:B{f0+4})").number_format = EUR
pl.cell(row=r, column=3, value=f"=SUM(C{f0+2}:C{f0+4})").number_format = EUR
pl.cell(row=r, column=2).font = BOLD
lost = r + 2
pl.cell(row=lost - 1, column=1, value="Lost (from product lines)").font = BOLD
items = [("Regrettable churn / contraction", "='Opp summary'!E15"),
         ("Non-regrettable churn (revenue kept)", "='Opp summary'!F15"),
         ("Price concession (discount)", "='Opp summary'!H15")]
for k, (lbl, f) in enumerate(items):
    pl.cell(row=lost + k, column=1, value=lbl)
    c = pl.cell(row=lost + k, column=2, value=f)
    c.number_format, c.font = EUR, GREEN_LINK
k = lost + 3
pl.cell(row=k, column=1, value="Gross retention (base less regrettable churn and concessions)")
pl.cell(row=k, column=2, value=f"=(B{t}+B{lost}+B{lost+2})/B{t}").number_format = "0.0%"
pl.cell(row=k + 1, column=1, value="Net retention (new ARR / base)")
pl.cell(row=k + 1, column=2, value=f"=S{t}/B{t}").number_format = "0.0%"
ff = k + 3
pl.cell(row=ff, column=1, value="Forecast of the forecast").font = Font(name=F, bold=True, size=12)
pl.cell(row=ff + 1, column=1, value="Weighted today (statuses from what we know)")
pl.cell(row=ff + 1, column=2, value=f"=T{t}").number_format = EUR
pl.cell(row=ff + 2, column=1, value="Weighted by 30 Oct, if this week's actions land")
pl.cell(row=ff + 2, column=2, value=f"=AH{t}").number_format = EUR
pl.cell(row=ff + 3, column=1, value="Gain from this week's actions")
pl.cell(row=ff + 3, column=2, value=f"=B{ff+2}-B{ff+1}").number_format = EUR
for rr in (ff + 1, ff + 2, ff + 3):
    pl.cell(row=rr, column=2).font = BOLD
style_range(pl, f0 + 2, f0 + 5, 1, 4)
style_range(pl, lost, k + 1, 1, 2)
style_range(pl, ff + 1, ff + 3, 1, 2)

# --------------------------------------------------------------------- Triage
tr = wb.create_sheet("Triage", 1)
title(tr, "Triage: what I do first, who owns it, by when",
      "Ranked by slack (days left vs work still needed) x ARR at risk. Linked to Pipeline: change a rank there and "
      "this list re-sorts.")
tcols = ["Rank", "Customer", "ARR (€)", "Renewal date", "Days", "Renewal Status", "Why first", "Next action",
         "Owner", "Also involved", "Due", "Escalate today"]
header(tr, 4, tcols, [6, 20, 11, 13, 7, 17, 42, 60, 9, 22, 12, 40])
src = {2: "A", 3: "B", 4: "C", 5: "J", 6: "G", 7: "Z", 8: "V", 9: "W", 10: "AA", 11: "X", 12: "AB"}
for k in range(1, len(P) + 1):
    r = 4 + k
    tr.cell(row=r, column=1, value=k).font = BOLD
    for c, Lc in src.items():
        tr.cell(row=r, column=c, value=f'=INDEX(Pipeline!${Lc}${r0}:${Lc}${rN},MATCH($A{r},Pipeline!$Y${r0}:$Y${rN},0))&""'
                if c in (7, 8, 10, 12) else
                f"=INDEX(Pipeline!${Lc}${r0}:${Lc}${rN},MATCH($A{r},Pipeline!$Y${r0}:$Y${rN},0))")
        tr.cell(row=r, column=c).alignment = WRAP
    tr.cell(row=r, column=3).number_format = EUR
    tr.cell(row=r, column=4).number_format = DATE
    tr.cell(row=r, column=11).number_format = DATE
    tr.row_dimensions[r].height = 62
tE = 4 + len(P)
style_range(tr, 5, tE, 1, 12)
tr.conditional_formatting.add(f"L5:L{tE}", FormulaRule(formula=['LEFT(L5,3)="Yes"'], fill=RED_FILL, font=Font(name=F, bold=True, color="9C0006")))
tr.conditional_formatting.add(f"E5:E{tE}", CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL))
tr.conditional_formatting.add(f"K5:K{tE}", FormulaRule(formula=["K5=Pipeline!$B$2"], fill=AMB_FILL))
tr.cell(row=tE + 2, column=1, value="Escalations today").font = BOLD
tr.cell(row=tE + 2, column=3, value=f'=COUNTIF(L5:L{tE},"Yes*")&" accounts, "&TEXT(SUMIF(L5:L{tE},"Yes*",C5:C{tE}),"€#,##0")&" ARR"')
tr.cell(row=tE + 3, column=1, value="Process").font = BOLD
tr.cell(row=tE + 3, column=3, value=("5 of 7 manual renewals inside 60 days had no quote (policy: quote at 60 days). Raise with my manager: "
                                     "60-day quote task in the CRM, and quote generation automated (Part 3)."))
tr.merge_cells(start_row=tE + 3, start_column=3, end_row=tE + 3, end_column=12)
tr.freeze_panes = "C5"

# ------------------------------------------------------------------- Products
pd_ = wb.create_sheet("Products", 1)
title(pd_, "Opportunity products: the Renewals Manager only sets the line type and the new numbers; everything else recalculates")
pd_["A2"] = ("Renewals Manager inputs (yellow): line type and change at list. Original ARR is the renewal value and already "
             "includes the 5% uplift (applied when the renewal opportunity is created), so nothing is added on top. On multi-year deals paid upfront the price is locked from "
             "year 2 (no further uplift); paid annually, 5% applies every year. An Upsell line opens a linked Upsell "
             "opportunity so expansion is forecast separately. Churn category and reason live on the opportunity.")
pd_["A2"].alignment = WRAP
pd_.merge_cells("A2:N2")
pd_.row_dimensions[2].height = 58
pcols = ["Opportunity", "Product", "Line type", "Term (yrs)", "Payment", "Original ARR (€)", "Change at list (€)",
         "Extra uplift %", "Discount %", "List renewal price (€)", "New ARR (€)", "Δ vs original (€)", "Δ %",
         "Approval needed", "Year 2+ uplift", "Note"]
header(pd_, 4, pcols, [20, 28, 12, 8, 10, 13, 13, 10, 10, 14, 13, 13, 8, 22, 12, 44])
L = [
    ("Vantage Freight", "n8n Cloud Business", "Renewal", 1, "Annual", 21000, 0, 0, "Quote of 1 Sep at the renewal value"),
    ("Northwind Logistics", "n8n Cloud Enterprise", "Renewal", 1, "Annual", 48000, 0, 0, "Usage +12%: check cap next quarter"),
    ("Pixelforge", "n8n Cloud Business", "Renewal", 1, "Annual", 26000, 0, 0, "Renewal value; the contractual uplift is already in it"),
    ("Halden Health", "n8n Enterprise (self-hosted)", "Downgrade", 1, "Annual", 45000, -15000, 0, "Right-sized at list (assumed €30k)"),
    ("Brightloop", "n8n Enterprise", "Renewal", 2, "Annual", 36000, 0, 0.10, "Ramp year 1: 10% off; year 2 €35,910"),
    ("Tessera Finance", "n8n Enterprise (self-hosted)", "Renewal", 1, "Annual", 50000, 0, 0, ""),
    ("Lumen Retail", "n8n Cloud Business", "Renewal", 1, "Annual", 28000, 0, 0, "Bill to new legal entity"),
    ("Kestrel Analytics", "n8n Cloud Business", "Renewal", 1, "Annual", 35000, 0, 0, "Commit line"),
    ("Kestrel Analytics", "Next execution tier", "Upsell", 1, "Annual", 0, 0, 0, "Opens a linked Upsell opportunity (upside)"),
    ("Marlowe Insurance", "n8n Cloud Enterprise", "Renewal", 1, "Annual", 46000, 0, 0, ""),
    ("Quanta Labs", "n8n Cloud Enterprise", "Downgrade", 1, "Annual", 40000, -8000, 0, "Right-sized in line with -20% usage"),
]
for i, (opp, prod, lt, term, pay, orig, chg, disc, note) in enumerate(L):
    r = 5 + i
    for c, v in {1: opp, 2: prod, 3: lt, 4: term, 5: pay, 6: orig, 7: chg, 9: disc, 16: note}.items():
        cell = pd_.cell(row=r, column=c, value=v)
        if c in (3, 4, 5, 7, 9):
            inp(cell)
    pd_.cell(row=r, column=8, value=0)  # renewal ARR already includes the 5% uplift
    pd_.cell(row=r, column=10, value=f'=IF(C{r}="Churn",0,F{r}*(1+H{r})+G{r})')
    pd_.cell(row=r, column=11, value=f"=J{r}*(1-I{r})")
    pd_.cell(row=r, column=12, value=f"=K{r}-F{r}")
    pd_.cell(row=r, column=13, value=f'=IF(F{r}=0,"new",L{r}/F{r})')
    pd_.cell(row=r, column=14, value=(
        f'=IF(I{r}=0,"None",IF(AND(D{r}>=2,I{r}<=0.05),"None (multi-year)",'
        f'IF(I{r}<=0.12,"Finance","VP Customer Success")))'))
    pd_.cell(row=r, column=15, value=f'=IF(D{r}<2,"n/a",IF(E{r}="Upfront","Locked (0%)","5% a year"))')
    for c in (6, 7, 10, 11, 12):
        pd_.cell(row=r, column=c).number_format = EUR
    for c in (8, 9, 13):
        pd_.cell(row=r, column=c).number_format = PCT
pN = 5 + len(L) - 1
style_range(pd_, 5, pN, 1, 16)
for rng, f1 in (("C", '"Renewal,Upsell,Downgrade,Churn"'), ("E", '"Annual,Upfront"')):
    dvl = DataValidation(type="list", formula1=f1)
    pd_.add_data_validation(dvl)
    dvl.add(f"{rng}5:{rng}{pN + 40}")
pd_.conditional_formatting.add(f"L5:M{pN + 40}", FormulaRule(formula=["AND(ISNUMBER(L5),L5>0)"], fill=GRN_FILL, font=Font(name=F, color="006100", bold=True)))
pd_.conditional_formatting.add(f"L5:M{pN + 40}", FormulaRule(formula=["AND(ISNUMBER(L5),L5<0)"], fill=RED_FILL, font=Font(name=F, color="9C0006", bold=True)))
pd_.conditional_formatting.add(f"N5:N{pN + 40}", FormulaRule(formula=['LEFT(N5,4)<>"None"'], fill=AMB_FILL))
pd_.cell(row=pN + 2, column=1, value="Total").font = BOLD
for c in (6, 7, 10, 11, 12):
    Lc = get_column_letter(c)
    cell = pd_.cell(row=pN + 2, column=c, value=f"=SUM({Lc}5:{Lc}{pN})")
    cell.font, cell.number_format = BOLD, EUR
pd_.cell(row=pN + 4, column=1, value="Assumptions").font = BOLD
pd_.cell(row=pN + 5, column=1, value=(
    "Plan names and downgrade prices are assumptions: n8n does not publish self-hosted Enterprise prices. A year-1 "
    "uplift waiver is an exception (e.g. three years paid upfront) and counts as a discount under policy C."))
pd_.merge_cells(start_row=pN + 5, start_column=1, end_row=pN + 5, end_column=16)
pd_.cell(row=pN + 5, column=1).alignment = WRAP
pd_.row_dimensions[pN + 5].height = 34
pd_.freeze_panes = "C5"

# ---------------------------------------------------------------- Opp summary
os_ = wb.create_sheet("Opp summary", 2)
title(os_, "Opportunity roll-up: calculated from product lines; churn category and reason set on the opportunity")
oc = ["Opportunity", "Original ARR (€)", "Uplift (€)", "Upsell (€) → Upsell opp", "Churned amount (€)",
      "Churn category", "Churn reason", "Price concession below current (€)", "New ARR (€)", "Net change (€)", "Net change %"]
header(os_, 3, oc, [20, 14, 12, 16, 14, 16, 34, 16, 13, 13, 11])
PR = "Products!$A$5:$A$200"
CHURN = {"Halden Health": ("Regrettable", "Low adoption / champion left"),
         "Quanta Labs": ("Regrettable", "Budget cut")}
for i, p in enumerate(P):
    r = 4 + i
    n = f"$A{r}"
    os_.cell(row=r, column=1, value=f"=Pipeline!A{r0 + i}").font = GREEN_LINK
    os_.cell(row=r, column=2, value=f"=SUMIFS(Products!$F:$F,Products!$A:$A,{n})")
    os_.cell(row=r, column=3, value=f"=SUMPRODUCT(({PR}={n})*Products!$F$5:$F$200*Products!$H$5:$H$200)")
    os_.cell(row=r, column=4, value=f'=SUMIFS(Products!$G:$G,Products!$A:$A,{n},Products!$C:$C,"Upsell")')
    os_.cell(row=r, column=5, value=(f'=SUMIFS(Products!$G:$G,Products!$A:$A,{n},Products!$C:$C,"Downgrade")'
                                     f'-SUMIFS(Products!$F:$F,Products!$A:$A,{n},Products!$C:$C,"Churn")'))
    cat, reason = CHURN.get(p[0], ("", ""))
    for c, v in ((6, cat), (7, reason)):
        inp(os_.cell(row=r, column=c, value=v))
    # Revenue given up below today's price; the waived uplift alone is not a loss.
    os_.cell(row=r, column=8, value=f"=MIN(0,C{r}-(SUMIFS(Products!$J:$J,Products!$A:$A,{n})-SUMIFS(Products!$K:$K,Products!$A:$A,{n})))")
    os_.cell(row=r, column=9, value=f"=SUMIFS(Products!$K:$K,Products!$A:$A,{n})")
    os_.cell(row=r, column=10, value=f"=I{r}-B{r}")
    os_.cell(row=r, column=11, value=f"=IF(B{r}=0,0,J{r}/B{r})")
    for c in (2, 3, 4, 5, 8, 9, 10):
        os_.cell(row=r, column=c).number_format = EUR
    os_.cell(row=r, column=11).number_format = PCT
oN = 4 + len(P) - 1
style_range(os_, 4, oN, 1, 11)
REASONS = ("Regrettable: Budget cut,Regrettable: Price,Regrettable: Competitor,Regrettable: Moved to free Community edition,"
           "Regrettable: Product gaps,Regrettable: Support or service,Regrettable: Low adoption / champion left,"
           "Regrettable: Company closed,Non-regrettable: Migrated to another n8n product,"
           "Non-regrettable: Consolidated into another n8n contract,Non-regrettable: Moved to another legal entity")
for rng, f1 in (("F", '"Regrettable,Non-regrettable"'),):
    dv = DataValidation(type="list", formula1=f1)
    os_.add_data_validation(dv)
    dv.add(f"{rng}4:{rng}{oN}")
tt = oN + 1  # row 14
os_.cell(row=tt, column=1, value="Total").font = BOLD
for c in (2, 3, 4, 5, 8, 9, 10, 11):
    Lc = get_column_letter(c)
    if c == 11:
        os_.cell(row=tt, column=c, value=f"=IF(B{tt}=0,0,J{tt}/B{tt})").number_format = PCT
    else:
        os_.cell(row=tt, column=c, value=f"=SUM({Lc}4:{Lc}{oN})").number_format = EUR
    os_.cell(row=tt, column=c).font = BOLD
# Row 15: totals the Pipeline forecast links to (E = regrettable, F = non-regrettable, H = price concession).
os_.cell(row=tt + 1, column=1, value="(linked to Pipeline)").font = Font(name=F, italic=True, color="888888")
os_.cell(row=tt + 1, column=5, value=f'=SUMIFS(E4:E{oN},F4:F{oN},"Regrettable")').number_format = EUR
os_.cell(row=tt + 1, column=6, value=f'=SUMIFS(E4:E{oN},F4:F{oN},"Non-regrettable")').number_format = EUR
os_.cell(row=tt + 1, column=8, value=f"=H{tt}").number_format = EUR
os_.cell(row=tt + 2, column=1, value="Churn reasons").font = BOLD
os_.cell(row=tt + 2, column=2, value=REASONS.replace(",", " · ")).alignment = WRAP
os_.merge_cells(start_row=tt + 2, start_column=2, end_row=tt + 2, end_column=11)
os_.row_dimensions[tt + 2].height = 44
os_.cell(row=tt + 3, column=1, value="Missing reason").font = BOLD
os_.cell(row=tt + 3, column=2, value=f'=COUNTIFS(E4:E{oN},"<0",F4:F{oN},"")&" opportunities with churn but no category"')
os_.cell(row=tt + 4, column=1, value="Check: new ARR ties to Pipeline")
os_.cell(row=tt + 4, column=2, value=f'=IF(ABS(I{tt}-Pipeline!S{t})<1,"OK","MISMATCH")')
os_.conditional_formatting.add(f"J4:K{tt}", CellIsRule(operator="greaterThan", formula=["0"], fill=GRN_FILL, font=Font(name=F, color="006100", bold=True)))
os_.conditional_formatting.add(f"J4:K{tt}", CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL, font=Font(name=F, color="9C0006", bold=True)))
os_.conditional_formatting.add(f"E4:E{tt}", CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL))
os_.conditional_formatting.add(f"F4:F{oN}", FormulaRule(formula=['AND(E4<0,F4="")'], fill=RED_FILL))

# ------------------------------------------------------------- Monthly report
mr = wb.create_sheet("Monthly report", 3)
title(mr, "Renewals by quarter and month (by renewal date)")
mc = ["Quarter", "Month", "# renewals", "Base ARR (€)", "New ARR (€)", "Weighted (€)", "On time, weighted (€)",
      "Late, weighted (€)", "Overdue ARR (€)", "Regrettable churn (€)"]
header(mr, 3, mc, [10, 10, 11, 13, 13, 13, 16, 15, 14, 16])


def col(Lc):
    return f"Pipeline!${Lc}${r0}:${Lc}${rN}"


for i, m in enumerate(["2026-10", "2026-11", "2026-12"]):
    r = 4 + i
    mr.cell(row=r, column=1, value="Q4 2026")
    mr.cell(row=r, column=2, value=m)
    mr.cell(row=r, column=3, value=f'=COUNTIFS({col("M")},B{r})')
    mr.cell(row=r, column=4, value=f'=SUMIFS({col("B")},{col("M")},B{r})')
    mr.cell(row=r, column=5, value=f'=SUMIFS({col("S")},{col("M")},B{r})')
    mr.cell(row=r, column=6, value=f'=SUMIFS({col("T")},{col("M")},B{r})')
    mr.cell(row=r, column=7, value=f'=SUMIFS({col("T")},{col("M")},B{r},{col("U")},"On time")')
    mr.cell(row=r, column=8, value=f'=SUMIFS({col("T")},{col("M")},B{r},{col("U")},"Late")')
    mr.cell(row=r, column=9, value=f'=SUMIFS({col("B")},{col("M")},B{r},{col("L")},"YES")')
    mr.cell(row=r, column=10, value=(f"=SUMPRODUCT((TEXT(Pipeline!$C${r0}:$C${rN},\"yyyy-mm\")=B{r})"
                                     f"*('Opp summary'!$F$4:$F${oN}=\"Regrettable\")*'Opp summary'!$E$4:$E${oN})"))
    for c in range(4, 11):
        mr.cell(row=r, column=c).number_format = EUR
style_range(mr, 4, 6, 1, 10)
mr.cell(row=7, column=1, value="Q4 2026 total").font = BOLD
for c in range(3, 11):
    Lc = get_column_letter(c)
    cell = mr.cell(row=7, column=c, value=f"=SUM({Lc}4:{Lc}6)")
    cell.font = BOLD
    if c >= 4:
        cell.number_format = EUR
mr.conditional_formatting.add("I4:I7", CellIsRule(operator="greaterThan", formula=["0"], fill=RED_FILL))
mr.conditional_formatting.add("J4:J7", CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL))

# --------------------------------------------------------------------- Policy
po = wb.create_sheet("Policy")
title(po, "Commercial policy (section C) and the approval it triggers")
header(po, 3, ["Topic", "Standard", "Needs approval"], [28, 50, 50])
pol = [("Discount on renewal", "Up to 5% for a 2-year commitment; none for 1 year", "6-12%: Finance. Above 12%: VP Customer Success"),
       ("Payment terms", "Net 30", "Net 45: allowed. Net 60+: Finance"),
       ("Auto-renewal clause", "Required in all order forms", "Waiver: Legal + VP Customer Success"),
       ("Termination for convenience", "Not offered", "Any such right: Legal, normally declined"),
       ("Downgrade", "Allowed at renewal, list price of the new plan", "None"),
       ("Price uplift", "5% on 1-year renewals", "Waiving it counts as a discount"),
       ("Quote lead time", "Quote sent 60 days before expiry", "n/a")]
for i, row in enumerate(pol, start=4):
    for j, v in enumerate(row, 1):
        po.cell(row=i, column=j, value=v).alignment = WRAP
style_range(po, 4, 10, 1, 3)

# -------------------------------------------------------------------- Read me
rm = wb.create_sheet("Read me", 0)
rm.column_dimensions["A"].width = 22
rm.column_dimensions["B"].width = 110
rm["A1"] = "Renewal tracker: a mock-up of the CRM renewal model"
rm["A1"].font = Font(name=F, bold=True, size=14)
notes = [
    ("Purpose", "Shows the numbers the CRM would hold: renewals by month and quarter, by status, by product line, and a "
                "forecast driven by Renewal Status x countdown."),
    ("Today", "Pipeline!B2 = 20 Oct 2026 (exercise date). Use =TODAY() in live use."),
    ("Triage", "Rank, why first, next action, one owner (Me / CSM / Finance / Legal) plus who else is involved, due date, "
               "and today's escalations. Sorted by rank; edit the rank on the Pipeline tab."),
    ("Probability", "Renewal Status x days to renewal. Late statuses rise as the date gets closer; early statuses fall. "
                    "Overdue has its own, lower column."),
    ("Auto-renewals", "Own statuses: Renewing: no blockers / Billing blocker / At risk (before or after the notice deadline) / "
                      "Notice received / Renewed. A red status cell means the status does not match the renewal type."),
    ("Usage rule", "Usage +20%: renew as is plus an Upsell opportunity and task (no automatic charge). Usage -20%: flag the CSM; "
                   "auto-renewals move to At risk."),
    ("Forecast of the forecast", "Weighted today vs weighted by 30 Oct if this week's actions move each status to its target."),
    ("Overdue rule", "Overdue renewals are Late. They count in the quarter only if the expected close date is on or before "
                     "quarter end; otherwise 0% for the quarter."),
    ("Forecast", "Weighted new ARR = new ARR from product lines x probability. Buckets: On time, Late (still in quarter), "
                 "Slips quarter. Lost comes from the product lines."),
    ("Products", "The Renewals Manager only sets the line type (Renewal / Upsell / Downgrade / Churn) and the new numbers. Original ARR, "
                 "list price, new ARR and Δ (green/red) recalculate; the renewal value already includes the uplift. Upsell lines open a linked Upsell opportunity."),
    ("Churn", "Set on the opportunity: churned amount (from the lines), category (Regrettable = revenue lost for good; "
              "Non-regrettable = revenue kept, e.g. self-hosted moving to n8n Cloud) and a granular reason."),
    ("Colour code", "Blue on yellow = input. Black = formula. Green text = link to another tab. Red/amber/green fills = risk."),
    ("Source", "Customers, numbers and policies are fictional, from the challenge brief. Plan names and downgrade prices "
               "are assumptions."),
]
for i, (k, v) in enumerate(notes, start=3):
    rm.cell(row=i, column=1, value=k).font = BOLD
    c = rm.cell(row=i, column=2, value=v)
    c.alignment = WRAP
    rm.row_dimensions[i].height = 32

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and c.font.name != F:
                c.font = Font(name=F, bold=c.font.bold, italic=c.font.italic, color=c.font.color, size=c.font.size)
order = ["Read me", "Triage", "Pipeline", "Products", "Opp summary", "Monthly report", "Probability", "Policy"]
wb._sheets = [wb[n] for n in order]
wb.active = 1
wb.save(OUT)
print("saved", OUT)
