// Prices the renewal from its product lines and builds the order form.
// Policy C: 5% uplift on renewed base; changes at list; discount vs uplifted list;
// approvals for discount and payment terms; auto-renewal always in, no termination for convenience.
const req = $('Quote request').first().json;
const term = String(req['Term']).startsWith('2') ? 2 : 1;
const pay = req['Payment terms'] || 'Net 30';
const UPLIFT = 0.05;
const eur = n => '€' + Math.round(n).toLocaleString('en-US');

const lines = $input.all().map(i => i.json).filter(l => l.Opportunity === req['Opportunity']);
if (!lines.length) throw new Error('No product lines found for ' + req['Opportunity']);

let original = 0, list = 0;
const priced = lines.map(l => {
  const orig = Number(l.OriginalARR) || 0;
  const change = Number(l.ChangeAtList) || 0;
  const type = l.LineType || 'Renewal';
  const uplift = type === 'Renewal' ? orig * UPLIFT : 0;
  const lineList = type === 'Churn' ? 0 : orig + uplift + change;
  original += orig; list += lineList;
  return { product: l.Product, type, orig, uplift, change, lineList };
});
// Either a discount % or a target annual fee; the fee wins and the discount is derived from it.
const target = Number(req['Or target annual fee (EUR)']) || 0;
const disc = target > 0 ? Math.max(0, 1 - target / list) : (Number(req['Discount % vs list']) || 0) / 100;
const annual = list * (1 - disc);

// Who must approve (highest wins)
const reasons = [];
let level = 0; // 0 none, 1 Finance, 2 VP CS
if (disc > 0) {
  const free = term === 2 ? 0.05 : 0;
  if (disc > 0.12) { level = 2; reasons.push('Discount ' + (Math.round(disc * 1000) / 10) + '% > 12%: VP Customer Success'); }
  else if (disc > free) { level = Math.max(level, 1); reasons.push('Discount ' + (Math.round(disc * 1000) / 10) + '% on ' + term + '-year: Finance'); }
}
if (pay === 'Net 60') { level = Math.max(level, 1); reasons.push('Net 60: Finance'); }
const approver = ['None', 'Finance', 'VP Customer Success'][level];

const first = lines[0];
const start = String(first.RenewalDate).substring(0, 10);
const td = 'style="padding:6px 8px;border-bottom:1px solid #ddd"';
const th = 'style="padding:6px 8px;text-align:left;background:#2b2b3c;color:#fff"';
const rows = priced.map(p =>
  '<tr><td ' + td + '>' + p.product + '</td><td ' + td + '>' + p.type + '</td><td ' + td + '>' + eur(p.orig) +
  '</td><td ' + td + '>' + eur(p.lineList) + '</td><td ' + td + '><b>' + eur(p.lineList * (1 - disc)) + '</b></td></tr>').join('');
const delta = annual - original;
const html =
  '<div style="font-family:Arial,sans-serif;font-size:13px;max-width:720px">' +
  '<h2>Renewal Order Form: ' + req['Opportunity'] + '</h2>' +
  '<p>Term: <b>' + term + ' year' + (term > 1 ? 's' : '') + '</b> from <b>' + start + '</b> · Payment terms: <b>' + pay +
  '</b> · Quote valid until ' + start + '</p>' +
  '<table cellspacing="0"><tr><th ' + th + '>Product</th><th ' + th + '>Line</th><th ' + th + '>Current ARR</th><th ' + th +
  '>List (incl. 5% uplift)</th><th ' + th + '>Annual fee</th></tr>' + rows + '</table>' +
  '<p>Annual fee: <b>' + eur(annual) + '</b>' + (disc ? ' (includes ' + (Math.round(disc * 1000) / 10) + '% discount)' : '') +
  ' · Total contract value: <b>' + eur(annual * term) + '</b></p>' +
  '<p style="font-size:12px;color:#444">This Order Form renews automatically for successive 12-month terms unless either party gives written notice ' +
  'of non-renewal at least 30 days before the end of the current term. Fees are fixed for the term and payable annually in advance. ' +
  'Governed by the Master Subscription Agreement in force between the parties.</p>' +
  '<p>Customer signature: ____________________ Name / title: ____________________ Date: __________</p></div>';

return [{ json: {
  Opportunity: req['Opportunity'], Term: term, PaymentTerms: pay, DiscountPct: disc,
  OriginalARR: original, ListARR: Math.round(list), AnnualFee: Math.round(annual), TCV: Math.round(annual * term),
  DeltaARR: Math.round(delta), Approver: approver, ApprovalReasons: reasons.join('; ') || 'Within policy',
  Champion: first.Champion || '', ChampionEmail: first.ChampionEmail || '', RenewalDate: start, orderFormHtml: html,
} }];
