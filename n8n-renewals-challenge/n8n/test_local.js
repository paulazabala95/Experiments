const fs = require('fs');
const rows = [
 ['Vantage Freight',21000,'2026-10-15','Manual',0,'Yellow','Quoted','No named contact (shared inbox)'],
 ['Northwind Logistics',48000,'2026-10-29','Manual',0.12,'Green','Not started','No quote sent'],
 ['Pixelforge',26000,'2026-11-02','Auto',0,'Green','Engaging customer','Card expired; billing contact unknown'],
 ['Halden Health',45000,'2026-11-07','Manual',-0.35,'Red','Not started','Champion left'],
 ['Brightloop',36000,'2026-12-14','Manual',-0.10,'Yellow','Negotiation','Procurement asks'],
 ['Tessera Finance',50000,'2026-11-18','Manual',0.05,'Yellow','Engaging customer','MSA redlines; security review'],
 ['Lumen Retail',28000,'2026-11-21','Auto',0.08,'Green','Engaging customer','Invoice to a different legal entity'],
 ['Kestrel Analytics',35000,'2026-11-28','Manual',0.40,'Green','Engaging customer','Close to execution cap'],
 ['Marlowe Insurance',46000,'2026-12-09','Manual',0,'Yellow','Engaging customer','Vendor questionnaire + DPA'],
 ['Quanta Labs',40000,'2026-12-19','Auto',-0.20,'Yellow','Not started','Budget cuts; unresponsive'],
].map(a => ({ json: { Customer:a[0], ARR:a[1], RenewalDate:a[2], Type:a[3], UsagePct:a[4], Health:a[5], Status:a[6], Blocker:a[7], Owner:'Paula' } }));
const run = (file, input) => new Function('$input', fs.readFileSync(file, 'utf8'))({ all: () => input });
const scored = run('score_renewals.js', rows);
for (const s of scored) console.log(s.json.Severity, s.json.Customer, s.json.DaysToRenewal, s.json.Window, s.json.FinalProb, s.json.WeightedARR, '|', s.json.AlertCodes);
const d = run('build_digest.js', scored);
console.log(d[0].json.subject);
fs.writeFileSync('sample_digest.html', d[0].json.html);
fs.writeFileSync('pin_rows.json', JSON.stringify(rows));
