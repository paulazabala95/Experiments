// Scores every renewal row: countdown, window, month/quarter, status x time probability,
// weighted new ARR, and the alerts a Renewals Specialist must act on today.
// Exercise date: set DEMO_TODAY to '' to use the real date.
const DEMO_TODAY = '2026-10-20';
const UPLIFT = 0.05;
const AUTO_FLOOR = 0.8;
const BUCKETS = ['Overdue', '0-30', '31-60', '61-90', '>90'];
const MATRIX = {
  '--None--':          [0, 0, 0, 0, 0],
  'Not started':       [0.05, 0.10, 0.20, 0.30, 0.35],
  'Engaging customer': [0.10, 0.25, 0.35, 0.45, 0.50],
  'Negotiation':       [0.20, 0.40, 0.50, 0.55, 0.55],
  'Quoted':            [0.40, 0.65, 0.70, 0.70, 0.70],
  'Waiting for PO':    [0.60, 0.85, 0.85, 0.80, 0.80],
  'PO received':       [0.90, 0.98, 0.97, 0.95, 0.95],
  'Closed won':        [1, 1, 1, 1, 1],
  'Cancelled':         [0, 0, 0, 0, 0],
};
const HEALTH = { Green: 1, Yellow: 0.85, Red: 0.6 };
const EARLY = ['--None--', 'Not started', 'Engaging customer'];
const SIGNED_OR_LATE_STAGE = ['Waiting for PO', 'PO received', 'Closed won'];
const CLOSED = ['Closed won', 'Cancelled'];
const DAY = 86400000;

function toDate(v) {
  if (typeof v === 'number') return new Date(Date.UTC(1899, 11, 30) + v * DAY);
  return new Date(String(v).substring(0, 10) + 'T00:00:00Z');
}
function num(v) {
  if (typeof v === 'number') return v;
  const n = parseFloat(String(v || '').replace(/[^0-9.\-]/g, ''));
  return isNaN(n) ? 0 : n;
}
function pct(v) {
  // Accepts -0.35, "-35%" or -35
  if (typeof v === 'string' && v.indexOf('%') > -1) return num(v) / 100;
  const n = num(v);
  return Math.abs(n) > 1 ? n / 100 : n;
}

const today = DEMO_TODAY ? new Date(DEMO_TODAY + 'T00:00:00Z') : new Date(new Date().toISOString().substring(0, 10) + 'T00:00:00Z');
const rank = { P1: 1, P2: 2, P3: 3 };
const out = [];

for (const item of $input.all()) {
  const r = item.json;
  const status = String(r.Status || '--None--').trim() || '--None--';
  const type = String(r.Type || '').trim();
  const health = String(r.Health || '').trim();
  const blocker = String(r.Blocker || '').trim();
  const arr = num(r.ARR);
  const usage = pct(r.UsagePct);
  const renewal = toDate(r.RenewalDate);
  const days = Math.round((renewal - today) / DAY);
  const bucket = days < 0 ? 'Overdue' : days <= 30 ? '0-30' : days <= 60 ? '31-60' : days <= 90 ? '61-90' : '>90';
  const month = renewal.toISOString().substring(0, 7);
  const quarter = 'Q' + Math.ceil((renewal.getUTCMonth() + 1) / 3) + ' ' + renewal.getUTCFullYear();

  const row = MATRIX[status] || MATRIX['--None--'];
  let stageProb = row[BUCKETS.indexOf(bucket)];
  if (type === 'Auto' && !blocker && !CLOSED.includes(status)) stageProb = Math.max(stageProb, AUTO_FLOOR);
  const prob = Math.round(stageProb * (HEALTH[health] || 0.85) * 100) / 100;
  const newArr = r.NewARR ? num(r.NewARR) : Math.round(arr * (1 + UPLIFT));
  const weighted = Math.round(newArr * prob);

  const alerts = [];
  const add = (sev, code, msg, owner) => alerts.push({ sev, code, msg, owner });
  const open = !CLOSED.includes(status);
  if (open && days < 0)
    add('P1', 'OVERDUE', 'Overdue by ' + (-days) + ' days. Find a named signer today; manager decides grace period.', 'Renewals + Manager');
  if (open && type === 'Manual' && days <= 60 && EARLY.includes(status))
    add(days <= 30 ? 'P1' : 'P2', 'QUOTE_LEAD_TIME', 'No quote out and ' + days + ' days left (policy: quote at 60 days). Send quote + order form.', 'Renewals');
  if (open && type === 'Manual' && days >= 0 && days <= 14 && !SIGNED_OR_LATE_STAGE.includes(status))
    add('P1', 'SIGNATURE_RISK', days + ' days left and not yet with procurement/signature.', 'Renewals');
  if (open && type === 'Auto' && /card|billing|payment|entity|invoice/i.test(blocker))
    add(days <= 30 ? 'P1' : 'P2', 'PAYMENT_BLOCKER', 'Auto-renewal will fail or misbill: ' + blocker + '.', 'Renewals + Finance');
  const notice = num(r.NoticeDays) || 30;
  if (open && type === 'Auto' && days >= 0 && days <= notice + 14)
    add('P2', 'NOTICE_WINDOW', (days - notice >= 0
      ? 'Notice deadline (cancellation / price uplift) in ' + (days - notice) + ' days. Send uplift notice now; check cancellation risk.'
      : 'Notice deadline passed ' + (notice - days) + ' days ago: renews on current terms, uplift likely not enforceable this cycle.'), 'Renewals');
  if (open && (health === 'Red' || usage <= -0.2))
    add(days <= 30 ? 'P1' : 'P2', 'HEALTH_RISK', 'Health ' + health + ', usage ' + Math.round(usage * 100) + '%. CSM-led save plan before any quote.', 'CSM');
  if (open && usage >= 0.25)
    add('P3', 'UPSELL_SIGNAL', 'Usage +' + Math.round(usage * 100) + '% in 90 days. Quote renewal + next tier.', 'CSM + Renewals');
  if (open && type === 'Manual' && blocker && days <= 60 && !alerts.length)
    add('P2', 'BLOCKER_OPEN', 'Open blocker: ' + blocker + '. Confirm approvals and next step are dated.', 'Renewals');
  if (status === '--None--' || !r.Owner || !arr)
    add('P2', 'CRM_HYGIENE', 'Missing Renewal Status, owner or ARR.', 'Renewals');

  alerts.sort((a, b) => rank[a.sev] - rank[b.sev]);
  out.push({
    json: {
      ...r,
      DaysToRenewal: days,
      Window: bucket,
      Month: month,
      Quarter: quarter,
      StageProb: stageProb,
      FinalProb: prob,
      NewARR: newArr,
      WeightedARR: weighted,
      Severity: alerts.length ? alerts[0].sev : 'OK',
      AlertCodes: alerts.map(a => a.code).join(', '),
      Alerts: alerts.map(a => '[' + a.sev + '] ' + a.code + ': ' + a.msg + ' (' + a.owner + ')').join('\n'),
      LastChecked: today.toISOString().substring(0, 10),
    },
  });
}
out.sort((a, b) => rank[a.json.Severity] - rank[b.json.Severity] || a.json.DaysToRenewal - b.json.DaysToRenewal);
return out;
