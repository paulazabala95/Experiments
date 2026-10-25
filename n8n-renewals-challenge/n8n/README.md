# n8n prototype: daily renewals with CPQ quote send and signature chase (Part 3)

Workflow in my n8n Cloud: https://paulazabala95.app.n8n.cloud/workflow/mvDDTTwQYTpurdtP

This is a copy of my existing **Daily renewal alerts** workflow, which stays unchanged, extended so that every number mirrors the CRM/CPQ. The workflow never prices anything.

**Prototype data** (Google Sheet, standing in for Salesforce and the CPQ):
- `Renewals` tab: the existing tab, plus a **QuoteSentDate** column, which the workflow writes after sending.
- `Quotes` tab: approved quotes from the CPQ. The template is `quotes_sheet.csv` (QuoteId, QuoteStatus, QuoteSummary, QuotePdfUrl).

**Routes, every day at 8:00:**

| Route | Condition | What happens |
|---|---|---|
| Upsell | Flag = Upsell and the CPQ quote is Approved | AI renewal email + upsell email → Renewals Manager approves → sent with the order form link → Status = Quoted |
| Risk | Flag = Risk | Alert to the CSM; nothing goes to the customer |
| On track | No flag and the CPQ quote is Approved | AI renewal email → Renewals Manager approves → sent with the order form link → Status = Quoted |
| Chase signature | Quoted 3 or 7 days ago, still unsigned | AI follow-up → Renewals Manager approves → sent |
| Quote not ready | No approved CPQ quote | Reminder to the Renewals Manager to finish the quote in the CPQ |
