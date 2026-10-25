// One digest per run: book by quarter/month, forecast, and today's action list.
const rows = $input.all().map(i => i.json);
const eur = n => '€' + Math.round(n).toLocaleString('en-US');
const months = {};
for (const r of rows) {
  const k = r.Quarter + ' | ' + r.Month;
  months[k] = months[k] || { n: 0, arr: 0, weighted: 0, overdue: 0, p1: 0 };
  const m = months[k];
  m.n += 1; m.arr += Number(r.ARR) || 0; m.weighted += r.WeightedARR;
  if (r.Window === 'Overdue') m.overdue += Number(r.ARR) || 0;
  if (r.Severity === 'P1') m.p1 += 1;
}
const td = 'style="padding:4px 8px;border-bottom:1px solid #ddd"';
let monthRows = '';
for (const k of Object.keys(months).sort()) {
  const m = months[k];
  monthRows += '<tr><td ' + td + '>' + k + '</td><td ' + td + '>' + m.n + '</td><td ' + td + '>' + eur(m.arr) +
    '</td><td ' + td + '>' + eur(m.weighted) + '</td><td ' + td + (m.overdue ? ' bgcolor="#f8d7da"' : '') + '>' + eur(m.overdue) +
    '</td><td ' + td + '>' + m.p1 + '</td></tr>';
}
let actionRows = '';
for (const r of rows.filter(r => r.Severity !== 'OK')) {
  const color = r.Severity === 'P1' ? '#f8d7da' : r.Severity === 'P2' ? '#fff3cd' : '#d4edda';
  actionRows += '<tr><td ' + td + ' bgcolor="' + color + '"><b>' + r.Severity + '</b></td><td ' + td + '>' + r.Customer +
    '</td><td ' + td + '>' + eur(Number(r.ARR) || 0) + '</td><td ' + td + '>' + r.DaysToRenewal + 'd</td><td ' + td + '>' +
    r.Status + '</td><td ' + td + '>' + String(r.Alerts).replace(/\n/g, '<br>') + '</td></tr>';
}
const total = rows.reduce((s, r) => s + (Number(r.ARR) || 0), 0);
const weighted = rows.reduce((s, r) => s + r.WeightedARR, 0);
const p1 = rows.filter(r => r.Severity === 'P1').length;
const th = 'style="text-align:left;padding:4px 8px;background:#2b2b3c;color:#fff"';
const html =
  '<div style="font-family:Arial,sans-serif;font-size:13px">' +
  '<h2 style="margin:0">Renewals daily brief: ' + rows[0].LastChecked + '</h2>' +
  '<p>' + rows.length + ' open renewals | ' + eur(total) + ' ARR | system-weighted new ARR ' + eur(weighted) +
  ' | <b>' + p1 + ' P1 actions</b></p>' +
  '<h3>Book by quarter and month</h3><table cellspacing="0"><tr><th ' + th + '>Quarter | Month</th><th ' + th + '>#</th><th ' + th +
  '>ARR</th><th ' + th + '>Weighted new ARR</th><th ' + th + '>Overdue ARR</th><th ' + th + '>P1</th></tr>' + monthRows + '</table>' +
  '<h3>Today\'s actions (highest severity first)</h3><table cellspacing="0"><tr><th ' + th + '>Sev</th><th ' + th + '>Customer</th><th ' + th +
  '>ARR</th><th ' + th + '>Due in</th><th ' + th + '>Status</th><th ' + th + '>What to do (owner)</th></tr>' + actionRows + '</table>' +
  '<p style="color:#666">Human check: confirm every P1 has an owner and a date in the CRM before 10:00. Forecast call is updated in the CRM, not here.</p></div>';
return [{ json: { subject: 'Renewals brief ' + rows[0].LastChecked + ': ' + p1 + ' P1, ' + eur(total) + ' open', html, p1 } }];
