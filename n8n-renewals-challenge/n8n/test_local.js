// Runs build_quote.js against the sample product lines with a few quote requests.
const fs = require('fs');
const lines = require('./product_lines.json');
const run = req => new Function('$input', '$', fs.readFileSync('build_quote.js', 'utf8'))(
  { all: () => lines.map(l => ({ json: l })) },
  () => ({ first: () => ({ json: req }) }));
const cases = [
  { Opportunity: 'Northwind Logistics', Term: '1 year', 'Discount % vs list': 0, 'Payment terms': 'Net 30' },
  { Opportunity: 'Brightloop', Term: '2 years', 'Or target annual fee (EUR)': 36000, 'Payment terms': 'Net 45' },
  { Opportunity: 'Brightloop', Term: '2 years', 'Discount % vs list': 12, 'Payment terms': 'Net 60' },
  { Opportunity: 'Brightloop', Term: '1 year', 'Discount % vs list': 25, 'Payment terms': 'Net 60' },
  { Opportunity: 'Halden Health', Term: '1 year', 'Discount % vs list': 0, 'Payment terms': 'Net 30' },
];
for (const c of cases) {
  const o = run(c)[0].json;
  console.log(o.Opportunity, o.Term + 'y', 'list', o.ListARR, 'fee', o.AnnualFee, 'TCV', o.TCV, 'Δ', o.DeltaARR, '|', o.Approver, '|', o.ApprovalReasons);
}
fs.writeFileSync('sample_order_form.html', run(cases[1])[0].json.orderFormHtml);
