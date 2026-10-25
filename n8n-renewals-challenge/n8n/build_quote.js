// CPQ stand-in: prices the renewal from its product lines and builds the order form.
// In production the CPQ owns pricing and approvals; this step reproduces its rules for the prototype.
// Rules: 5% uplift on renewal lines in year 1; changes at list. Multi-year: price locked from
// year 2 if paid upfront, +5% a year if paid annually. Discount per year (year 1 / year 2+) vs list.
// Approvals (policy C) on the total discount vs the annual list path, plus net 60.
const req = $('Quote request').first().json;
const term = Number(String(req['Term']).charAt(0)) || 1;
const upfront = String(req['Payment schedule']).startsWith('Upfront');
const d1 = (Number(req['Discount % year 1']) || 0) / 100;
const d2 = (Number(req['Discount % year 2+']) || 0) / 100;
const planChange = Number(req['Plan change at list (EUR, - to downsize)']) || 0;
const pay = req['Payment terms'] || 'Net 30';
const UPLIFT = 0.05;
const eur = n => '€' + Math.round(n).toLocaleString('en-US');
const pct = n => (Math.round(n * 1000) / 10) + '%';

const lines = $input.all().map(i => i.json).filter(l => l.Opportunity === req['Opportunity']);
if (!lines.length) throw new Error('No product lines found for ' + req['Opportunity']);

// Year-1 list price per line; the plan change (if any) is applied to the first line at list.
let original = 0;
const priced = lines.map((l, idx) => {
  const orig = Number(l.OriginalARR) || 0;
  const type = l.LineType || 'Renewal';
  const change = (Number(l.ChangeAtList) || 0) + (idx === 0 ? planChange : 0);
  const uplift = type === 'Renewal' ? orig * UPLIFT : 0;
  const y1List = type === 'Churn' ? 0 : orig + uplift + change;
  original += orig;
  return { product: l.Product, type: idx === 0 && planChange < 0 ? 'Downgrade' : type, orig, y1List };
});
const y1List = priced.reduce((s, p) => s + p.y1List, 0);

// Yearly schedule: list path (annual indexation) vs what we quote.
const years = [];
let listPath = 0, quoted = 0;
for (let y = 1; y <= term; y++) {
  const listY = y1List * Math.pow(1 + UPLIFT, y - 1);
  const basis = upfront ? y1List : listY;          // upfront = price locked from year 2
  const priceY = basis * (1 - (y === 1 ? d1 : d2));
  years.push({ year: y, list: listY, price: priceY });
  listPath += listY; quoted += priceY;
}
const totalDisc = listPath ? 1 - quoted / listPath : 0;

// Policy C approvals: highest wins.
const reasons = [];
let level = 0; // 0 none, 1 Finance, 2 VP CS
const free = term >= 2 ? 0.05 : 0;
if (totalDisc > 0.12) { level = 2; reasons.push('Total discount ' + pct(totalDisc) + ' > 12%: VP Customer Success'); }
else if (totalDisc > free + 0.0005) { level = 1; reasons.push('Total discount ' + pct(totalDisc) + ' on ' + term + ' year(s): Finance'); }
if (pay === 'Net 60') { level = Math.max(level, 1); reasons.push('Net 60: Finance'); }
if (term >= 3) { level = Math.max(level, 1); reasons.push('3-year term: Finance to confirm (policy C names 2-year deals)'); }
const approver = ['None', 'Finance', 'VP Customer Success'][level];

const first = lines[0];
const start = String(first.RenewalDate).substring(0, 10);
const td = 'style="padding:6px 8px;border-bottom:1px solid #ddd"';
const th = 'style="padding:6px 8px;text-align:left;background:#2b2b3c;color:#fff"';
const lineRows = priced.map(p => '<tr><td ' + td + '>' + p.product + '</td><td ' + td + '>' + p.type + '</td><td ' + td + '>' +
  eur(p.orig) + '</td><td ' + td + '>' + eur(p.y1List) + '</td></tr>').join('');
const yearRows = years.map(y => '<tr><td ' + td + '>Year ' + y.year + '</td><td ' + td + '><b>' + eur(y.price) + '</b></td></tr>').join('');
const orderForm =
  '<div style="font-family:Arial,sans-serif;font-size:13px;max-width:720px">' +
  '<h2>Renewal Order Form: ' + req['Opportunity'] + '</h2>' +
  '<p>Service start: <b>' + start + '</b> · Term: <b>' + term + ' year' + (term > 1 ? 's' : '') + '</b> · Payment: <b>' +
  (upfront ? 'upfront for the full term' : 'annually in advance') + ', ' + pay + '</b> · Quote valid until ' + start + '</p>' +
  '<table cellspacing="0"><tr><th ' + th + '>Product</th><th ' + th + '>Line</th><th ' + th + '>Current ARR</th><th ' + th +
  '>Year-1 list (incl. 5% uplift)</th></tr>' + lineRows + '</table><br>' +
  '<table cellspacing="0"><tr><th ' + th + '>Period</th><th ' + th + '>Fee</th></tr>' + yearRows + '</table>' +
  '<p>Total contract value: <b>' + eur(quoted) + '</b>' + (upfront && term > 1 ? ' (price locked for the term)' : '') + '</p>' +
  '<p style="font-size:12px;color:#444">After the committed term, this Order Form renews automatically for successive 12-month terms ' +
  'unless either party gives written notice at least 30 days before the end of the then-current term. The plan may not be ' +
  'reduced during the committed term. Governed by the Master Subscription Agreement in force between the parties.</p>' +
  '<p>Customer signature: ____________________ Name / title: ____________________ Date: __________</p></div>';

const fmtDate = d => new Date(d + 'T00:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
const offerSummary = term + '-year renewal starting ' + fmtDate(start) + ', paid ' + (upfront ? 'upfront for the full term' : 'annually') +
  ' (' + pay + '): ' + years.map(y => 'year ' + y.year + ' ' + eur(y.price)).join(', ') + '; total ' + eur(quoted) +
  (upfront && term > 1 ? ', price locked for the term' : '') + '.';

return [{ json: {
  OfferSummary: offerSummary,
  Opportunity: req['Opportunity'], Term: term, Upfront: upfront, PaymentTerms: pay,
  OriginalARR: original, Year1Price: Math.round(years[0].price), TCV: Math.round(quoted), ListPathTCV: Math.round(listPath),
  TotalDiscount: Math.round(totalDisc * 1000) / 10, DeltaYear1: Math.round(years[0].price - original),
  Schedule: years.map(y => 'Year ' + y.year + ': ' + eur(y.price)).join(' · '),
  Approver: approver, ApprovalReasons: reasons.join('; ') || 'Within policy',
  Context: req['What we know (for the cover email)'] || '',
  Champion: first.Champion || '', ChampionEmail: first.ChampionEmail || '', RenewalDate: start, orderFormHtml: orderForm,
} }];
