# n8n prototype: renewal quote and order form (Part 3)

Workflow in my n8n Cloud: https://paulazabala95.app.n8n.cloud/workflow/mvDDTTwQYTpurdtP

| Node | Type | What it does |
|---|---|---|
| Quote request | Form trigger | Prototype trigger. Production: the CRM's T−60 task or a "Generate quote" button. |
| Read product lines | Google Sheets (stand-in for Salesforce) | Reads the renewal's lines from the `Products` tab (`products_sheet.csv`) |
| Price and build order form (CPQ stand-in) | Code, deterministic | `build_quote.js`: uplift, price lock, discount per year, policy C approver, order form |
| Draft cover email (AI) | Basic LLM chain + OpenAI model | Writes the cover email; copies the offer sentence verbatim; internal notes for tone only |
| Review and approve | Gmail, send and wait for approval | The Renewals Manager (Finance or the VP when flagged) approves or rejects |
| Approved? → Send order form to customer → Mark renewal as Quoted | IF, Gmail, Google Sheets | Production: e-signature, and the quote file attached to the opportunity |

`test_local.js` runs the pricing step against the sample lines:

```
node test_local.js
```
