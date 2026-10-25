<style>body{font-size:9pt;line-height:1.35} h1{font-size:15pt} h2{font-size:11pt;margin-top:10px} td,th{font-size:8.3pt;padding:3px 5px}</style>

# How I used AI on this challenge

The brief invited any tools, including AI. Here is exactly what I did, what AI did, and how I checked it.

**Time:** about **4 hours** of my own time over two sessions. Part 3 builds on an n8n workflow I created on 13 October, before this exercise.

## What came from me

These are the decisions the work is built on. I specified them, and corrected the AI where its first version didn't match how I run renewals. I also used it as a sparring partner to check whether I was missing an option.

| Area | My decision |
|---|---|
| **Forecast** | Renewal Status × days to renewal drives the probability. Later statuses rise as the date approaches, early ones fall. Statuses are set from what we know today, with a second view after this week's actions ("forecast of the forecast"). |
| **Overdue renewals** | A separate league: they only count if they close within the quarter. Otherwise they count as zero for that quarter. |
| **Auto-renewals** | Their own statuses: blockers, at risk before or after the notice deadline. Over-usage opens an upsell opportunity, never an automatic charge. Under-usage flags the CSM. |
| **Product lines and churn** | Each line is renewal, upsell, downgrade or churn. Original ARR is kept next to new ARR, and Salesforce recalculates everything else. Churn sits on the opportunity: **regrettable** means revenue lost for good; **non-regrettable** means revenue kept elsewhere at n8n (e.g. self-hosted → Cloud). Upsell is its own opportunity. |
| **Commercial rules** | 5% uplift in year 1, announced in one bulk notice each January. The price is locked from year 2 only for upfront multi-year deals. The Renewals Manager owns the numbers. A new renewal opportunity is created when the current one closes won. |
| **Brightloop** | Two structures instead of a discount: downsize + multi-year lock, or keep the plan with a small buffer. Net 60 only with upfront payment; top SLA tier. |
| **Automation** | **The workflow never prices; everything mirrors the CRM/CPQ.** Extend my existing workflow rather than build a duplicate. A human approves every customer-facing email. |

## What AI (Claude) did

- **Built from my specifications:** the Excel tracker (formulas, tabs, formatting), the n8n workflow, and the PDFs.
- **Drafted** text I then edited: the email to Sam, the playbook, the write-ups.
- **Did and checked the maths:** the policy C approval thresholds and the multi-year discount maths, e.g. why a 10% + 5% ramp is 7.4% overall, not 15%.
- **Researched** facts about n8n (self-hosted and Cloud editions, pricing by executions) and flagged the assumptions it couldn't verify. One example: the price of a smaller Enterprise tier.

## How I checked it

- I reviewed every number in the tracker and documents. The totals tie out across files.
- I tested the n8n workflow on the challenge accounts (pinned data, no real emails sent).
- **Where AI got it wrong, and I corrected it:**
  - its first forecast relied on judgement instead of my status × countdown model;
  - it put churn type on the product lines instead of the opportunity;
  - it proposed waiving the uplift on 2-year deals without upfront payment;
  - its first Part 3 calculated prices in the workflow, which broke my rule that the CRM is the source of truth.
- **An AI failure I caught in testing:** an early AI-drafted email leaked internal notes ("budget cut", "usage down 10%"). That's why every customer-facing draft goes to a person for approval.

## My principle

The same as in the AI agents I build at work: numbers come from the tool of record, never from the model; AI is used where language helps; a human approves anything customer-facing; and autonomy is earned with a track record. I know what was built, why and how, because I designed it. AI let me build it in hours instead of days.
