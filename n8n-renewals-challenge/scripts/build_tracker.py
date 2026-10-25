"""Builds renewal_tracker.xlsx: the CRM model behind the n8n renewals challenge.

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
SUB_FILL = PatternFill("solid", fgColor="EDEDF3")
RED_FILL = PatternFill("solid", fgColor="F8D7DA")
GRN_FILL = PatternFill("solid", fgColor="D4EDDA")
AMB_FILL = PatternFill("solid", fgColor="FFF3CD")
thin = Side(style="thin", color="D0D0D8")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
EUR = '€#,##0;[Red]-€#,##0;"-"'
PCT = '0%;[Red]-0%;"-"'
DATE = "dd mmm yyyy"

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

def style_range(ws, r1, r2, c1, c2, font=BLACK):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BOX
            if cell.font == Font() or cell.font.name != F:
                cell.font = font

# ---------------------------------------------------------------- Probability
pr = wb.active
pr.title = "Probability"
pr["A1"] = "Close-on-time probability: Renewal Status x days to renewal"
pr["A1"].font = Font(name=F, bold=True, size=13)
pr["A2"] = ("Later status + closer date = higher probability. Early status + closer date = LOWER "
            "probability, because there is no longer time to finish the cycle. Blue = editable.")
pr["A2"].font = Font(name=F, italic=True)
buckets = ["Overdue", "0-30", "31-60", "61-90", ">90"]
header(pr, 4, ["Renewal Status"] + buckets + ["Exit criteria (what must be true to be in this status)"],
       [22, 11, 11, 11, 11, 11, 70])
matrix = [
    ("--None--", [0, 0, 0, 0, 0], "Not allowed. Hygiene alert: every open renewal must have a status."),
    ("Not started", [0.05, 0.10, 0.20, 0.30, 0.35], "Renewal opp exists; no customer contact about the renewal yet."),
    ("Engaging customer", [0.10, 0.25, 0.35, 0.45, 0.50], "Decision maker and signatory known; renewal timeline agreed."),
    ("Negotiation", [0.20, 0.40, 0.50, 0.55, 0.55], "Commercial terms under discussion; customer asks are in writing."),
    ("Quoted", [0.40, 0.65, 0.70, 0.70, 0.70], "Final quote + order form sent and verbally accepted by the champion."),
    ("Waiting for PO", [0.60, 0.85, 0.85, 0.80, 0.80], "Order form approved by buyer; in their PO / signature workflow."),
    ("PO received", [0.90, 0.98, 0.97, 0.95, 0.95], "PO or signature in hand; only booking and invoicing remain."),
    ("Closed won", [1, 1, 1, 1, 1], "Signed, booked in CRM, invoiced. (Suggested addition to the picklist.)"),
    ("Cancelled", [0, 0, 0, 0, 0], "Customer gave notice or will not renew. Churn is booked."),
]
for i, (s, ps, crit) in enumerate(matrix, start=5):
    pr.cell(row=i, column=1, value=s).font = BOLD
    for j, p in enumerate(ps, start=2):
        c = pr.cell(row=i, column=j, value=p)
        c.font, c.number_format, c.fill = BLUE, "0%", INPUT_FILL
    pr.cell(row=i, column=7, value=crit).alignment = Alignment(wrap_text=True)
style_range(pr, 5, 13, 1, 7)
pr.conditional_formatting.add("B5:F13", FormulaRule(formula=["B5>=0.8"], fill=GRN_FILL))
pr.conditional_formatting.add("B5:F13", FormulaRule(formula=["AND(B5>0,B5<0.4)"], fill=RED_FILL))

pr["A16"] = "Health multiplier (from CSM)"; pr["A16"].font = BOLD
header(pr, 17, ["Health", "Multiplier"])
for i, (h, m) in enumerate([("Green", 1.0), ("Yellow", 0.85), ("Red", 0.6)], start=18):
    pr.cell(row=i, column=1, value=h)
    c = pr.cell(row=i, column=2, value=m); c.font, c.number_format, c.fill = BLUE, "0.00", INPUT_FILL
style_range(pr, 18, 20, 1, 2)

pr["A23"] = "Auto-renew floor"; pr["A23"].font = BOLD
pr["B23"] = 0.80; pr["B23"].font, pr["B23"].number_format, pr["B23"].fill = BLUE, "0%", INPUT_FILL
pr["C23"] = ("Auto-renewals with no cancellation notice and a valid payment method are at least this likely "
             "(before health). A blocker (expired card, entity change) removes the floor.")
pr["C23"].alignment = Alignment(wrap_text=True)
pr.merge_cells("C23:G24")

# ------------------------------------------------------------------- Pipeline
pl = wb.create_sheet("Pipeline", 0)
pl["A1"] = "Q4 2026 renewal pipeline: first slice (10 renewals, €375k ARR)"
pl["A1"].font = Font(name=F, bold=True, size=13)
pl["A2"] = "Today"; pl["A2"].font = BOLD
pl["B2"] = date(2026, 10, 20); pl["B2"].font, pl["B2"].fill, pl["B2"].number_format = BLUE, INPUT_FILL, DATE
pl["B2"].comment = Comment("Exercise date set to Tue 20 Oct 2026 so that Vantage is overdue and the other nine "
                           "fall inside 60 days. Replace with =TODAY() in live use.", "Renewals")
pl["D2"] = "Target date"; pl["D2"].font = BOLD
pl["E2"] = date(2026, 10, 30); pl["E2"].font, pl["E2"].fill, pl["E2"].number_format = BLUE, INPUT_FILL, DATE
pl["F2"] = "Blue / yellow cells are inputs. Everything else is a formula. Columns Y-AA show where this week's actions move the forecast."
pl["F2"].font = Font(name=F, italic=True)

cols = ["Customer", "Base ARR (€)", "Renewal date", "Type", "Usage 90d", "Health", "Renewal Status",
        "Blocker", "Days to renewal", "Window", "Overdue?", "Month", "Quarter",
        "Stage prob.", "Health mult.", "Final prob.", "New ARR (€) from Products",
        "Weighted New ARR (€)", "Forecast call", "Call ARR retained (€)", "Call new ARR (€)",
        "Next action", "Owner", "Due", "Target status by 30 Oct", "Target prob.", "Weighted after actions (€)"]
header(pl, 4, cols, [20, 12, 13, 8, 10, 9, 18, 26, 10, 9, 9, 10, 9, 9, 9, 9, 13, 13, 12, 13, 13, 60, 12, 12, 18, 9, 14])

# Status reflects reality as inherited on 20 Oct; call = my judgement after triage.
P = [
 ("Vantage Freight", 21000, date(2026,10,15), "Manual", -0.00, "Yellow", "Quoted",
  "No named contact (shared inbox)", "Late", 21000, 22050,
  "CSM pulls instance owner/admin emails from product data; I call + email the named person; agree signing date. Manager decides grace period before access is restricted.",
  "Me + CSM", date(2026,10,21)),
 ("Northwind Logistics", 48000, date(2026,10,29), "Manual", 0.12, "Green", "Not started",
  "No quote sent; signed 3 days late last year", "On time", 48000, 50400,
  "Send quote + order form (e-sign) at €50.4k today. Ask champion for signatory name and book signature for 27 Oct.",
  "Me", date(2026,10,20)),
 ("Pixelforge", 26000, date(2026,11,2), "Auto", 0.00, "Green", "Engaging customer",
  "Card expired; billing contact unknown", "On time", 26000, 26000,
  "CSM gets billing contact today; I send secure card-update link or switch to invoice. Check if uplift notice is still contractually possible (likely not).",
  "CSM + Me", date(2026,10,22)),
 ("Halden Health", 45000, date(2026,11,7), "Manual", -0.35, "Red", "Not started",
  "Champion left; new owner unknown", "Late", 30000, 30000,
  "ESCALATE TODAY. CSM + me + exec sponsor meet new owner this week. Legal checks if the 30-day notice window (8 Oct) passed without notice. Prepare right-sized option.",
  "CSM (lead) + Me", date(2026,10,23)),
 ("Brightloop", 36000, date(2026,12,14), "Manual", -0.10, "Yellow", "Negotiation",
  "Procurement asks: 25% off, net 60, no auto-renew, 3-month TfC", "On time", 33264, 33264,
  "Reply to Sam today; Finance pre-approval for up to 12% + net 60 on 2-year; call with Sam + Priya this week. Target signature 30 Nov.",
  "Me", date(2026,10,20)),
 ("Tessera Finance", 50000, date(2026,11,18), "Manual", 0.05, "Yellow", "Engaging customer",
  "MSA redlines open since Sep; security review", "Late", 50000, 52500,
  "ESCALATE TODAY to Legal: close redlines by 6 Nov. Send security pack today. Offer to renew on the current MSA so the renewal is not blocked by the MSA.",
  "Legal + Me", date(2026,10,23)),
 ("Lumen Retail", 28000, date(2026,11,21), "Auto", 0.08, "Green", "Engaging customer",
  "Invoice to a different legal entity", "On time", 28000, 29400,
  "Get new entity details (name, VAT, address). Legal: billing change only or assignment? Finance updates billing before invoice run. Send uplift notice.",
  "Me + Finance", date(2026,10,27)),
 ("Kestrel Analytics", 35000, date(2026,11,28), "Manual", 0.40, "Green", "Engaging customer",
  "Close to execution cap", "On time", 35000, 36750,
  "CSM runs usage review; I send two quotes: like-for-like renewal (€36.75k) and next execution tier. Upsell is upside, not in commit.",
  "CSM + Me", date(2026,10,28)),
 ("Marlowe Insurance", 46000, date(2026,12,9), "Manual", 0.00, "Yellow", "Engaging customer",
  "Vendor questionnaire + DPA needed for PO", "On time", 46000, 48300,
  "Send standard DPA + questionnaire answered from the trust centre (AI first draft, Security reviews) by 27 Oct. Send quote with it.",
  "Me + Legal", date(2026,10,27)),
 ("Quanta Labs", 40000, date(2026,12,19), "Auto", -0.20, "Yellow", "Not started",
  "Budget cuts in Q1; 2 check-ins unanswered", "On time", 32000, 32000,
  "CSM + exec sponsor reach out via a new contact; I check the cancellation-notice deadline. Offer right-sizing or a 2-year price lock before they send notice.",
  "CSM + Me", date(2026,10,30)),
]
TARGET = ["Waiting for PO", "PO received", "Waiting for PO", "Engaging customer", "Negotiation",
          "Quoted", "Quoted", "Quoted", "Quoted", "Engaging customer"]
r0 = 5
for i, p in enumerate(P):
    r = r0 + i
    (cust, arr, rdate, typ, use, hl, status, blocker, call, retained, callnew, action, owner, due) = p
    vals = {1: cust, 2: arr, 3: rdate, 4: typ, 5: use, 6: hl, 7: status, 8: blocker,
            19: call, 20: retained, 21: callnew, 22: action, 23: owner, 24: due}
    for c, v in vals.items():
        cell = pl.cell(row=r, column=c, value=v)
        if c in (2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 23, 24):
            cell.font, cell.fill = BLUE, INPUT_FILL
    pl.cell(row=r, column=9, value=f"=C{r}-$B$2")
    pl.cell(row=r, column=10, value=f'=IF(I{r}<0,"Overdue",IF(I{r}<=30,"0-30",IF(I{r}<=60,"31-60",IF(I{r}<=90,"61-90",">90"))))')
    pl.cell(row=r, column=11, value=f'=IF(AND(I{r}<0,G{r}<>"Closed won",G{r}<>"Cancelled"),"YES","")')
    pl.cell(row=r, column=12, value=f'=TEXT(C{r},"yyyy-mm")')
    pl.cell(row=r, column=13, value=f'="Q"&ROUNDUP(MONTH(C{r})/3,0)&" "&YEAR(C{r})')
    pl.cell(row=r, column=14, value=(f"=MAX(INDEX(Probability!$B$5:$F$13,MATCH(G{r},Probability!$A$5:$A$13,0),"
                                     f"MATCH(J{r},Probability!$B$4:$F$4,0)),"
                                     f'IF(AND(D{r}="Auto",H{r}=""),Probability!$B$23,0))'))
    pl.cell(row=r, column=15, value=f"=INDEX(Probability!$B$18:$B$20,MATCH(F{r},Probability!$A$18:$A$20,0))")
    pl.cell(row=r, column=16, value=f"=N{r}*O{r}")
    pl.cell(row=r, column=17, value=f"=SUMIFS(Products!$I:$I,Products!$A:$A,A{r})")
    pl.cell(row=r, column=18, value=f"=Q{r}*P{r}")
    c = pl.cell(row=r, column=25, value=TARGET[i]); c.font, c.fill = BLUE, INPUT_FILL
    tb = f'IF(C{r}-$E$2<0,"Overdue",IF(C{r}-$E$2<=30,"0-30",IF(C{r}-$E$2<=60,"31-60",IF(C{r}-$E$2<=90,"61-90",">90"))))'
    pl.cell(row=r, column=26, value=(f"=MAX(INDEX(Probability!$B$5:$F$13,MATCH(Y{r},Probability!$A$5:$A$13,0),"
                                     f"MATCH({tb},Probability!$B$4:$F$4,0)),"
                                     f'IF(D{r}="Auto",Probability!$B$23,0))*O{r}'))
    pl.cell(row=r, column=27, value=f"=Q{r}*Z{r}")
    pl.cell(row=r, column=26).number_format = PCT
    pl.cell(row=r, column=27).number_format = EUR
    for c in (2, 17, 18, 20, 21): pl.cell(row=r, column=c).number_format = EUR
    for c in (3, 24): pl.cell(row=r, column=c).number_format = DATE
    for c in (5, 14, 15, 16): pl.cell(row=r, column=c).number_format = PCT
    pl.cell(row=r, column=15).number_format = "0.00"
    pl.cell(row=r, column=22).alignment = Alignment(wrap_text=True, vertical="top")
    pl.cell(row=r, column=8).alignment = Alignment(wrap_text=True, vertical="top")
    pl.row_dimensions[r].height = 48
rN = r0 + len(P) - 1
style_range(pl, r0, rN, 1, 27)
t = rN + 1
pl.cell(row=t, column=1, value="Total").font = BOLD
for c in (2, 17, 18, 20, 21, 27):
    L = get_column_letter(c)
    cell = pl.cell(row=t, column=c, value=f"=SUM({L}{r0}:{L}{rN})")
    cell.font, cell.number_format = BOLD, EUR
pl.cell(row=t, column=16, value=f"=IFERROR(R{t}/Q{t},0)").number_format = PCT

dv = DataValidation(type="list", formula1="=Probability!$A$5:$A$13", allow_blank=False)
pl.add_data_validation(dv); dv.add(f"G{r0}:G{rN}")
dv2 = DataValidation(type="list", formula1='"Green,Yellow,Red"'); pl.add_data_validation(dv2); dv2.add(f"F{r0}:F{rN}")
dv3 = DataValidation(type="list", formula1='"On time,Late,Lost"'); pl.add_data_validation(dv3); dv3.add(f"S{r0}:S{rN}")
dv4 = DataValidation(type="list", formula1='"Manual,Auto"'); pl.add_data_validation(dv4); dv4.add(f"D{r0}:D{rN}")

rng = f"A{r0}:X{rN}"
pl.conditional_formatting.add(f"K{r0}:K{rN}", FormulaRule(formula=[f'K{r0}="YES"'], fill=RED_FILL, font=Font(name=F, bold=True, color="9C0006")))
pl.conditional_formatting.add(f"J{r0}:J{rN}", FormulaRule(formula=[f'J{r0}="0-30"'], fill=AMB_FILL))
pl.conditional_formatting.add(f"F{r0}:F{rN}", FormulaRule(formula=[f'F{r0}="Red"'], fill=RED_FILL))
pl.conditional_formatting.add(f"F{r0}:F{rN}", FormulaRule(formula=[f'F{r0}="Green"'], fill=GRN_FILL))
pl.conditional_formatting.add(f"P{r0}:P{rN}", CellIsRule(operator="lessThan", formula=["0.4"], fill=RED_FILL))
pl.conditional_formatting.add(f"P{r0}:P{rN}", CellIsRule(operator="greaterThanOrEqual", formula=["0.8"], fill=GRN_FILL))
pl.conditional_formatting.add(f"S{r0}:S{rN}", FormulaRule(formula=[f'S{r0}="Late"'], fill=AMB_FILL))
pl.conditional_formatting.add(f"S{r0}:S{rN}", FormulaRule(formula=[f'S{r0}="Lost"'], fill=RED_FILL))
# Quote-lead-time breach: manual, <=60 days, still before "Quoted"
pl.conditional_formatting.add(f"A{r0}:A{rN}", FormulaRule(
    formula=[f'AND($D{r0}="Manual",$I{r0}<=60,OR($G{r0}="Not started",$G{r0}="Engaging customer",$G{r0}="--None--"))'],
    fill=AMB_FILL))
pl.freeze_panes = "B5"

# Forecast block
f0 = t + 3
pl.cell(row=f0, column=1, value="Forecast vs €375k base (my call, column S/T)").font = Font(name=F, bold=True, size=12)
header_cells = ["Bucket", "ARR (€)", "% of base", "New ARR incl. uplift (€)"]
for j, h in enumerate(header_cells, 1):
    c = pl.cell(row=f0 + 1, column=j, value=h); c.font, c.fill, c.border = HDR, HDR_FILL, BOX
rows = [("On time", f'=SUMIFS(T{r0}:T{rN},S{r0}:S{rN},"On time")', f'=SUMIFS(U{r0}:U{rN},S{r0}:S{rN},"On time")'),
        ("Late", f'=SUMIFS(T{r0}:T{rN},S{r0}:S{rN},"Late")', f'=SUMIFS(U{r0}:U{rN},S{r0}:S{rN},"Late")'),
        ("Lost (churn + contraction)", f"=B{t}-T{t}", "")]
for k, (lbl, f1, f2) in enumerate(rows):
    r = f0 + 2 + k
    pl.cell(row=r, column=1, value=lbl)
    pl.cell(row=r, column=2, value=f1).number_format = EUR
    pl.cell(row=r, column=3, value=f"=B{r}/$B${t}").number_format = "0.0%"
    if f2: pl.cell(row=r, column=4, value=f2).number_format = EUR
r = f0 + 5
pl.cell(row=r, column=1, value="Total").font = BOLD
pl.cell(row=r, column=2, value=f"=SUM(B{f0+2}:B{f0+4})").number_format = EUR
pl.cell(row=r, column=3, value=f"=B{r}/$B${t}").number_format = "0.0%"
pl.cell(row=r, column=4, value=f"=SUM(D{f0+2}:D{f0+3})").number_format = EUR
pl.cell(row=r+1, column=1, value="Gross retention (GRR)")
pl.cell(row=r+1, column=2, value=f"=T{t}/B{t}").number_format = "0.0%"
pl.cell(row=r+2, column=1, value="Net retention (NRR, incl. uplift)")
pl.cell(row=r+2, column=2, value=f"=U{t}/B{t}").number_format = "0.0%"
pl.cell(row=r+3, column=1, value="System-weighted New ARR today (statuses as inherited)")
pl.cell(row=r+3, column=2, value=f"=R{t}").number_format = EUR
pl.cell(row=r+4, column=1, value="System-weighted New ARR after this week's actions")
pl.cell(row=r+4, column=2, value=f"=AA{t}").number_format = EUR
style_range(pl, f0 + 2, r + 4, 1, 4)
pl.cell(row=r+5, column=1, value=("Reading: the weighted number today is low because statuses lag the dates (quotes not sent inside 60 days). "
                                  "It is the forecast if nothing changes. The call assumes this week's actions land."))
pl.cell(row=r+5, column=1).font = Font(name=F, italic=True)
pl.cell(row=r+6, column=1, value=("Least certain: the Lost number. Halden alone can land anywhere from €0 to €47k. "
                                  "Second: Tessera's timing (on time vs late).")).font = Font(name=F, italic=True)

# ------------------------------------------------------------------- Products
pd_ = wb.create_sheet("Products", 1)
pd_["A1"] = "Opportunity products: renewal / upsell / downgrade / churn per line"
pd_["A1"].font = Font(name=F, bold=True, size=13)
pd_["A2"] = ("Original ARR is never overwritten: it stays for comparison. Change at list = +upsell / -downgrade. "
             "Uplift applies to the renewed base only. Discount is measured against the uplifted list renewal price, "
             "so waiving the uplift counts as a discount (policy C).")
pd_["A2"].alignment = Alignment(wrap_text=True); pd_.merge_cells("A2:N2"); pd_.row_dimensions[2].height = 30
pcols = ["Opportunity", "Product", "Line type", "Term (yrs)", "Original ARR (€)", "Change at list (€)",
         "Uplift %", "Discount %", "New ARR (€)", "Δ vs original (€)", "Δ %", "List renewal price (€)",
         "Approval needed", "Note"]
header(pd_, 4, pcols, [20, 30, 12, 8, 13, 13, 9, 10, 13, 13, 8, 14, 22, 50])
# Line examples. Plan names / list prices for downgrades are illustrative assumptions.
L = [
 ("Vantage Freight", "n8n Business (annual)", "Renewal", 1, 21000, 0, 0.05, 0, "Quote of 1 Sep assumed to include 5% uplift"),
 ("Northwind Logistics", "n8n Enterprise Cloud", "Renewal", 1, 48000, 0, 0.05, 0, "Usage +12%: check cap; upsell later in year"),
 ("Pixelforge", "n8n Business (annual)", "Renewal", 1, 26000, 0, 0, 0, "Auto-renew: uplift notice likely too late this cycle"),
 ("Halden Health", "n8n Enterprise Cloud", "Downgrade", 1, 45000, -15000, 0, 0, "Right-size to smaller plan at list (assumed €30k)"),
 ("Brightloop", "n8n Enterprise (Tier 3)", "Renewal", 2, 36000, 0, 0.05, 0.12, "Walk-away line: 2-yr at Finance max 12%"),
 ("Tessera Finance", "n8n Enterprise Cloud", "Renewal", 1, 50000, 0, 0.05, 0, ""),
 ("Lumen Retail", "n8n Business (annual)", "Renewal", 1, 28000, 0, 0.05, 0, "Bill to new legal entity"),
 ("Kestrel Analytics", "n8n Business (annual)", "Renewal", 1, 35000, 0, 0.05, 0, "Commit line"),
 ("Kestrel Analytics", "Execution tier upgrade", "Upsell", 1, 0, 0, 0, 0, "Fill in when the customer picks a tier (upside, not commit)"),
 ("Marlowe Insurance", "n8n Enterprise Cloud", "Renewal", 1, 46000, 0, 0.05, 0, ""),
 ("Quanta Labs", "n8n Enterprise Cloud", "Downgrade", 1, 40000, -8000, 0, 0, "Right-sized in line with -20% usage"),
]
for i, (opp, prod, lt, term, orig, chg, up, disc, note) in enumerate(L):
    r = 5 + i
    for c, v in {1: opp, 2: prod, 3: lt, 4: term, 5: orig, 6: chg, 7: up, 8: disc, 14: note}.items():
        cell = pd_.cell(row=r, column=c, value=v)
        if c in (3, 4, 5, 6, 7, 8): cell.font, cell.fill = BLUE, INPUT_FILL
    # Uplift only on the renewed base; upsell/downgrade priced at list.
    pd_.cell(row=r, column=12, value=f'=IF(C{r}="Churn",0,E{r}*(1+G{r})+F{r})')
    pd_.cell(row=r, column=9, value=f"=L{r}*(1-H{r})")
    pd_.cell(row=r, column=10, value=f"=I{r}-E{r}")
    pd_.cell(row=r, column=11, value=f"=IF(E{r}=0,\"new\",J{r}/E{r})")
    pd_.cell(row=r, column=13, value=(
        f'=IF(H{r}=0,IF(AND(G{r}=0,C{r}="Renewal",D{r}=1),"Finance (uplift waived)","None"),'
        f'IF(AND(D{r}>=2,H{r}<=0.05),"None (multi-year)",'
        f'IF(H{r}<=0.12,"Finance","VP Customer Success")))'))
    for c in (5, 6, 9, 10, 12): pd_.cell(row=r, column=c).number_format = EUR
    for c in (7, 8, 11): pd_.cell(row=r, column=c).number_format = PCT
pN = 5 + len(L) - 1
style_range(pd_, 5, pN, 1, 14)
dvl = DataValidation(type="list", formula1='"Renewal,Upsell,Downgrade,Cross-sell,Churn"'); pd_.add_data_validation(dvl); dvl.add(f"C5:C{pN+40}")
pd_.conditional_formatting.add(f"J5:K{pN+40}", FormulaRule(formula=["AND(ISNUMBER(J5),J5>0)"], fill=GRN_FILL, font=Font(name=F, color="006100", bold=True)))
pd_.conditional_formatting.add(f"J5:K{pN+40}", FormulaRule(formula=["AND(ISNUMBER(J5),J5<0)"], fill=RED_FILL, font=Font(name=F, color="9C0006", bold=True)))
pd_.conditional_formatting.add(f"M5:M{pN+40}", FormulaRule(formula=['LEFT(M5,4)<>"None"'], fill=AMB_FILL))
pd_.cell(row=pN+2, column=1, value="Total").font = BOLD
for c in (5, 6, 9, 10, 12):
    Lc = get_column_letter(c)
    cell = pd_.cell(row=pN+2, column=c, value=f"=SUM({Lc}5:{Lc}{pN})"); cell.font, cell.number_format = BOLD, EUR
pd_.cell(row=pN+4, column=1, value="Uplift (indexation) rule").font = BOLD
pd_.cell(row=pN+5, column=1, value=("Default 5% on every 1-year renewal line (policy C). For n8n the index is a flat 5% across "
    "industries; if the business later indexes by segment (e.g. regulated industries with CPI clauses), change column G per line. "
    "On a 2-year term the uplift may be waived inside the 5% multi-year allowance with no approval."))
pd_.merge_cells(start_row=pN+5, start_column=1, end_row=pN+5, end_column=14)
pd_.cell(row=pN+5, column=1).alignment = Alignment(wrap_text=True); pd_.row_dimensions[pN+5].height = 44
pd_.freeze_panes = "C5"

# ---------------------------------------------------------------- Opp summary
os_ = wb.create_sheet("Opp summary", 2)
os_["A1"] = "Opportunity roll-up: churn, contraction, upsell and new ARR calculated from product lines"
os_["A1"].font = Font(name=F, bold=True, size=13)
oc = ["Opportunity", "Original ARR (€)", "Uplift (€)", "Upsell / cross-sell (€)", "Downgrade (€)",
      "Churn (€)", "Discount (€)", "New ARR (€)", "Net change (€)", "Net change %", "Gross retained (€)"]
header(os_, 3, oc, [20, 14, 12, 14, 13, 12, 12, 13, 13, 11, 14])
for i, p in enumerate(P):
    r = 4 + i; n = f"$A{r}"
    os_.cell(row=r, column=1, value=f"=Pipeline!A{r0+i}").font = GREEN_LINK
    os_.cell(row=r, column=2, value=f"=SUMIFS(Products!$E:$E,Products!$A:$A,{n})")
    os_.cell(row=r, column=3, value=f"=SUMPRODUCT((Products!$A$5:$A$200={n})*Products!$E$5:$E$200*Products!$G$5:$G$200)")
    os_.cell(row=r, column=4, value=f'=SUMIFS(Products!$F:$F,Products!$A:$A,{n},Products!$C:$C,"Upsell")+SUMIFS(Products!$F:$F,Products!$A:$A,{n},Products!$C:$C,"Cross-sell")')
    os_.cell(row=r, column=5, value=f'=SUMIFS(Products!$F:$F,Products!$A:$A,{n},Products!$C:$C,"Downgrade")')
    os_.cell(row=r, column=6, value=f'=-SUMIFS(Products!$E:$E,Products!$A:$A,{n},Products!$C:$C,"Churn")')
    os_.cell(row=r, column=7, value=f"=-(SUMIFS(Products!$L:$L,Products!$A:$A,{n})-SUMIFS(Products!$I:$I,Products!$A:$A,{n}))")
    os_.cell(row=r, column=8, value=f"=SUMIFS(Products!$I:$I,Products!$A:$A,{n})")
    os_.cell(row=r, column=9, value=f"=H{r}-B{r}")
    os_.cell(row=r, column=10, value=f"=IF(B{r}=0,0,I{r}/B{r})")
    os_.cell(row=r, column=11, value=f"=B{r}+E{r}+F{r}+MIN(0,C{r}+G{r})")
    for c in (2, 3, 4, 5, 6, 7, 8, 9, 11): os_.cell(row=r, column=c).number_format = EUR
    os_.cell(row=r, column=10).number_format = PCT
oN = 4 + len(P) - 1
style_range(os_, 4, oN, 1, 11)
os_.conditional_formatting.add(f"I4:J{oN+1}", CellIsRule(operator="greaterThan", formula=["0"], fill=GRN_FILL, font=Font(name=F, color="006100", bold=True)))
os_.conditional_formatting.add(f"I4:J{oN+1}", CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL, font=Font(name=F, color="9C0006", bold=True)))
os_.conditional_formatting.add(f"E4:G{oN+1}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, color="9C0006")))
tt = oN + 1
os_.cell(row=tt, column=1, value="Total").font = BOLD
for c in range(2, 12):
    Lc = get_column_letter(c)
    if c == 10:
        os_.cell(row=tt, column=c, value=f"=IF(B{tt}=0,0,I{tt}/B{tt})").number_format = PCT
    else:
        cell = os_.cell(row=tt, column=c, value=f"=SUM({Lc}4:{Lc}{oN})"); cell.number_format = EUR
    os_.cell(row=tt, column=c).font = BOLD
os_.cell(row=tt+2, column=1, value="GRR (product view)"); os_.cell(row=tt+2, column=2, value=f"=K{tt}/B{tt}").number_format = "0.0%"
os_.cell(row=tt+3, column=1, value="NRR (product view)"); os_.cell(row=tt+3, column=2, value=f"=H{tt}/B{tt}").number_format = "0.0%"
os_.cell(row=tt+4, column=1, value="Check: ties to Pipeline col Q"); os_.cell(row=tt+4, column=2, value=f'=IF(ABS(H{tt}-Pipeline!Q{t})<1,"OK","MISMATCH")')

# ------------------------------------------------------------- Monthly report
mr = wb.create_sheet("Monthly report", 3)
mr["A1"] = "Renewals by quarter and month (by renewal date): base for every alert and automation"
mr["A1"].font = Font(name=F, bold=True, size=13)
mc = ["Quarter", "Month", "# renewals", "Base ARR (€)", "Overdue ARR (€)", "Weighted New ARR (€)",
      "Call: on time (€)", "Call: late (€)", "Call: lost (€)", "# without quote ≤60d"]
header(mr, 3, mc, [10, 10, 11, 13, 14, 16, 14, 13, 13, 14])
months = [("Q4 2026", "2026-10"), ("Q4 2026", "2026-11"), ("Q4 2026", "2026-12")]
PR = f"Pipeline!$A${r0}:$A${rN}"
def col(L): return f"Pipeline!${L}${r0}:${L}${rN}"
for i, (q, m) in enumerate(months):
    r = 4 + i
    mr.cell(row=r, column=1, value=q); mr.cell(row=r, column=2, value=m)
    mr.cell(row=r, column=3, value=f'=COUNTIFS({col("L")},B{r})')
    mr.cell(row=r, column=4, value=f'=SUMIFS({col("B")},{col("L")},B{r})')
    mr.cell(row=r, column=5, value=f'=SUMIFS({col("B")},{col("L")},B{r},{col("K")},"YES")')
    mr.cell(row=r, column=6, value=f'=SUMIFS({col("R")},{col("L")},B{r})')
    mr.cell(row=r, column=7, value=f'=SUMIFS({col("T")},{col("L")},B{r},{col("S")},"On time")')
    mr.cell(row=r, column=8, value=f'=SUMIFS({col("T")},{col("L")},B{r},{col("S")},"Late")')
    mr.cell(row=r, column=9, value=f"=D{r}-G{r}-H{r}")
    mr.cell(row=r, column=10, value=(f'=COUNTIFS({col("L")},B{r},{col("D")},"Manual",{col("I")},"<=60",{col("G")},"Not started")'
                                     f'+COUNTIFS({col("L")},B{r},{col("D")},"Manual",{col("I")},"<=60",{col("G")},"Engaging customer")'))
    for c in range(4, 10): mr.cell(row=r, column=c).number_format = EUR
style_range(mr, 4, 6, 1, 10)
mr.cell(row=7, column=1, value="Q4 2026 total").font = BOLD
for c in range(3, 11):
    Lc = get_column_letter(c)
    cell = mr.cell(row=7, column=c, value=f"=SUM({Lc}4:{Lc}6)"); cell.font = BOLD
    if 4 <= c <= 9: cell.number_format = EUR
mr.conditional_formatting.add("E4:E7", CellIsRule(operator="greaterThan", formula=["0"], fill=RED_FILL))
mr.conditional_formatting.add("J4:J7", CellIsRule(operator="greaterThan", formula=["0"], fill=AMB_FILL))
mr["A9"] = ("In the CRM this is a report grouped by Renewal Date (calendar month) and Fiscal Quarter, with the same "
            "columns as summary fields. Every alert (overdue, 60-day quote, 30-day signature, auto-renew notice) "
            "keys off the same Renewal Date field.")
mr["A9"].alignment = Alignment(wrap_text=True); mr.merge_cells("A9:J9"); mr.row_dimensions[9].height = 44

# --------------------------------------------------------------------- Policy
po = wb.create_sheet("Policy")
po["A1"] = "Commercial policy (section C) and the approval it triggers"; po["A1"].font = Font(name=F, bold=True, size=13)
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
        po.cell(row=i, column=j, value=v).alignment = Alignment(wrap_text=True, vertical="top")
style_range(po, 4, 10, 1, 3)

# -------------------------------------------------------------------- Read me
rm = wb.create_sheet("Read me", 0)
rm.column_dimensions["A"].width = 22; rm.column_dimensions["B"].width = 110
rm["A1"] = "Renewal tracker: how this model works"; rm["A1"].font = Font(name=F, bold=True, size=14)
notes = [
 ("Purpose", "One source of truth for the renewal book: by month/quarter, by status, by product line, with a forecast the VP can trust."),
 ("Today", "Pipeline!B2 = 20 Oct 2026 (exercise date). Switch to =TODAY() in live use."),
 ("Pipeline", "One row per renewal opportunity. Days to renewal, window, overdue flag, month and quarter are formulas off Renewal Date. "
              "Amber customer name = manual renewal inside 60 days that has not reached 'Quoted' (quote lead-time breach)."),
 ("Probability", "Close-on-time probability = Status x Days-to-renewal matrix, x CSM health multiplier. "
                 "Auto-renewals with no blocker get a floor. Edit the blue cells to recalibrate after each quarter."),
 ("Products", "Each opportunity's lines: Renewal / Upsell / Downgrade / Cross-sell / Churn. Original ARR is kept; new ARR applies the 5% uplift "
              "to renewed base, list price to changes, and discount. Δ is green for growth, red for contraction. Approval column reads the policy."),
 ("Opp summary", "Rolls product lines up: uplift, upsell, downgrade, churn, discount, new ARR, net change (green/red). Feeds Pipeline col Q."),
 ("Monthly report", "Renewals grouped by quarter and month: count, ARR, overdue, weighted forecast, my call, and quote-lead-time breaches."),
 ("Two forecasts", "System-weighted (probability x new ARR) is the cross-check; the Forecast call (On time / Late / Lost, columns S-U) is "
                   "my judgement per deal and what I would send to the VP. When the two disagree by >10% I review the deal."),
 ("Colour code", "Blue text on yellow = input. Black = formula. Green text = link to another tab. Red/green fills = risk/healthy."),
 ("Source", "All customers, numbers and policies are fictional, from the n8n Renewals Specialist challenge brief. Plan names and the "
            "downgrade price points are illustrative assumptions."),
]
for i, (k, v) in enumerate(notes, start=3):
    rm.cell(row=i, column=1, value=k).font = BOLD
    c = rm.cell(row=i, column=2, value=v); c.alignment = Alignment(wrap_text=True, vertical="top"); c.font = BLACK
    rm.row_dimensions[i].height = 34

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and c.font.name != F:
                c.font = Font(name=F, bold=c.font.bold, italic=c.font.italic, color=c.font.color, size=c.font.size)
wb.save(OUT)
print("saved", OUT)
