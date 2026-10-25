// Runs build_quote.js (the CPQ stand-in) against the sample product lines.
const fs = require('fs');
const lines = require('./product_lines.json');
const run = req => new Function('$input', '$', fs.readFileSync('build_quote.js', 'utf8'))(
  { all: () => lines.map(l => ({ json: l })) },
  () => ({ first: () => ({ json: req }) }));
const base = { 'Payment schedule': 'Annual', 'Discount % year 1': 0, 'Discount % year 2+': 0, 'Payment terms': 'Net 30' };
const cases = [
  ['Northwind 1y', { ...base, Opportunity: 'Northwind Logistics', Term: '1 year' }],
  ['Brightloop ramp', { ...base, Opportunity: 'Brightloop', Term: '2 years', 'Discount % year 1': 10, 'Discount % year 2+': 5, 'Payment terms': 'Net 45' }],
  ['Brightloop downsize+lock 2y', { ...base, Opportunity: 'Brightloop', Term: '2 years', 'Payment schedule': 'Upfront', 'Plan change at list (EUR, - to downsize)': -9000, 'Payment terms': 'Net 60' }],
  ['Brightloop downsize+lock 3y', { ...base, Opportunity: 'Brightloop', Term: '3 years', 'Payment schedule': 'Upfront', 'Plan change at list (EUR, - to downsize)': -9000, 'Payment terms': 'Net 60' }],
  ['Brightloop 25% ask', { ...base, Opportunity: 'Brightloop', Term: '1 year', 'Discount % year 1': 28.6 }],
];
for (const [name, c] of cases) {
  const o = run(c)[0].json;
  console.log(name.padEnd(28), o.Schedule, '| TCV', o.TCV, '| disc', o.TotalDiscount + '%', '|', o.Approver, '|', o.ApprovalReasons);
}
fs.writeFileSync('sample_order_form.html', run(cases[1][1])[0].json.orderFormHtml);
