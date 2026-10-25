import { workflow, node, trigger, sticky, ifElse, expr } from '@n8n/workflow-sdk';

const schedule = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.2,
  config: {
    name: 'Weekdays at 7:30',
    parameters: { rule: { interval: [{ field: 'cronExpression', expression: '30 7 * * 1-5' }] } },
    position: [0, 300]
  }
});

const readPipeline = node({
  type: 'n8n-nodes-base.googleSheets',
  version: 4.7,
  config: {
    name: 'Read renewal pipeline',
    parameters: {
      resource: 'sheet',
      operation: 'read',
      documentId: { __rl: true, mode: 'id', value: '1PQm-aqOaNSstP6bbpvB-OgTvDWQoe-pdB41HfkCnq3g' },
      sheetName: { __rl: true, mode: 'name', value: 'Pipeline' },
      options: {}
    },
    credentials: { googleSheetsOAuth2Api: { id: 'h9lcpLixGuP5ku24', name: 'Google Sheets account' } },
    position: [224, 300]
  }
});

const score = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Score renewals and raise alerts',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: "// Scores every renewal row: countdown, window, month/quarter, status x time probability,\n// weighted new ARR, and the alerts a Renewals Specialist must act on today.\n// Exercise date: set DEMO_TODAY to '' to use the real date.\nconst DEMO_TODAY = '2026-10-20';\nconst UPLIFT = 0.05;\nconst AUTO_FLOOR = 0.8;\nconst BUCKETS = ['Overdue', '0-30', '31-60', '61-90', '>90'];\nconst MATRIX = {\n  '--None--':          [0, 0, 0, 0, 0],\n  'Not started':       [0.05, 0.10, 0.20, 0.30, 0.35],\n  'Engaging customer': [0.10, 0.25, 0.35, 0.45, 0.50],\n  'Negotiation':       [0.20, 0.40, 0.50, 0.55, 0.55],\n  'Quoted':            [0.40, 0.65, 0.70, 0.70, 0.70],\n  'Waiting for PO':    [0.60, 0.85, 0.85, 0.80, 0.80],\n  'PO received':       [0.90, 0.98, 0.97, 0.95, 0.95],\n  'Closed won':        [1, 1, 1, 1, 1],\n  'Cancelled':         [0, 0, 0, 0, 0],\n};\nconst HEALTH = { Green: 1, Yellow: 0.85, Red: 0.6 };\nconst EARLY = ['--None--', 'Not started', 'Engaging customer'];\nconst SIGNED_OR_LATE_STAGE = ['Waiting for PO', 'PO received', 'Closed won'];\nconst CLOSED = ['Closed won', 'Cancelled'];\nconst DAY = 86400000;\n\nfunction toDate(v) {\n  if (typeof v === 'number') return new Date(Date.UTC(1899, 11, 30) + v * DAY);\n  return new Date(String(v).substring(0, 10) + 'T00:00:00Z');\n}\nfunction num(v) {\n  if (typeof v === 'number') return v;\n  const n = parseFloat(String(v || '').replace(/[^0-9.\\-]/g, ''));\n  return isNaN(n) ? 0 : n;\n}\nfunction pct(v) {\n  // Accepts -0.35, \"-35%\" or -35\n  if (typeof v === 'string' && v.indexOf('%') > -1) return num(v) / 100;\n  const n = num(v);\n  return Math.abs(n) > 1 ? n / 100 : n;\n}\n\nconst today = DEMO_TODAY ? new Date(DEMO_TODAY + 'T00:00:00Z') : new Date(new Date().toISOString().substring(0, 10) + 'T00:00:00Z');\nconst rank = { P1: 1, P2: 2, P3: 3 };\nconst out = [];\n\nfor (const item of $input.all()) {\n  const r = item.json;\n  const status = String(r.Status || '--None--').trim() || '--None--';\n  const type = String(r.Type || '').trim();\n  const health = String(r.Health || '').trim();\n  const blocker = String(r.Blocker || '').trim();\n  const arr = num(r.ARR);\n  const usage = pct(r.UsagePct);\n  const renewal = toDate(r.RenewalDate);\n  const days = Math.round((renewal - today) / DAY);\n  const bucket = days < 0 ? 'Overdue' : days <= 30 ? '0-30' : days <= 60 ? '31-60' : days <= 90 ? '61-90' : '>90';\n  const month = renewal.toISOString().substring(0, 7);\n  const quarter = 'Q' + Math.ceil((renewal.getUTCMonth() + 1) / 3) + ' ' + renewal.getUTCFullYear();\n\n  const row = MATRIX[status] || MATRIX['--None--'];\n  let stageProb = row[BUCKETS.indexOf(bucket)];\n  if (type === 'Auto' && !blocker && !CLOSED.includes(status)) stageProb = Math.max(stageProb, AUTO_FLOOR);\n  const prob = Math.round(stageProb * (HEALTH[health] || 0.85) * 100) / 100;\n  const newArr = r.NewARR ? num(r.NewARR) : Math.round(arr * (1 + UPLIFT));\n  const weighted = Math.round(newArr * prob);\n\n  const alerts = [];\n  const add = (sev, code, msg, owner) => alerts.push({ sev, code, msg, owner });\n  const open = !CLOSED.includes(status);\n  if (open && days < 0)\n    add('P1', 'OVERDUE', 'Overdue by ' + (-days) + ' days. Find a named signer today; manager decides grace period.', 'Renewals + Manager');\n  if (open && type === 'Manual' && days <= 60 && EARLY.includes(status))\n    add(days <= 30 ? 'P1' : 'P2', 'QUOTE_LEAD_TIME', 'No quote out and ' + days + ' days left (policy: quote at 60 days). Send quote + order form.', 'Renewals');\n  if (open && type === 'Manual' && days >= 0 && days <= 14 && !SIGNED_OR_LATE_STAGE.includes(status))\n    add('P1', 'SIGNATURE_RISK', days + ' days left and not yet with procurement/signature.', 'Renewals');\n  if (open && type === 'Auto' && /card|billing|payment|entity|invoice/i.test(blocker))\n    add(days <= 30 ? 'P1' : 'P2', 'PAYMENT_BLOCKER', 'Auto-renewal will fail or misbill: ' + blocker + '.', 'Renewals + Finance');\n  const notice = num(r.NoticeDays) || 30;\n  if (open && type === 'Auto' && days >= 0 && days <= notice + 14)\n    add('P2', 'NOTICE_WINDOW', 'Cancellation/price-notice deadline in ' + (days - notice) + ' days. Confirm uplift notice sent and no cancellation risk.', 'Renewals');\n  if (open && (health === 'Red' || usage <= -0.2))\n    add(days <= 30 ? 'P1' : 'P2', 'HEALTH_RISK', 'Health ' + health + ', usage ' + Math.round(usage * 100) + '%. CSM-led save plan before any quote.', 'CSM');\n  if (open && usage >= 0.25)\n    add('P3', 'UPSELL_SIGNAL', 'Usage +' + Math.round(usage * 100) + '% in 90 days. Quote renewal + next tier.', 'CSM + Renewals');\n  if (open && type === 'Manual' && blocker && days <= 60 && !alerts.length)\n    add('P2', 'BLOCKER_OPEN', 'Open blocker: ' + blocker + '. Confirm approvals and next step are dated.', 'Renewals');\n  if (status === '--None--' || !r.Owner || !arr)\n    add('P2', 'CRM_HYGIENE', 'Missing Renewal Status, owner or ARR.', 'Renewals');\n\n  alerts.sort((a, b) => rank[a.sev] - rank[b.sev]);\n  out.push({\n    json: {\n      ...r,\n      DaysToRenewal: days,\n      Window: bucket,\n      Month: month,\n      Quarter: quarter,\n      StageProb: stageProb,\n      FinalProb: prob,\n      NewARR: newArr,\n      WeightedARR: weighted,\n      Severity: alerts.length ? alerts[0].sev : 'OK',\n      AlertCodes: alerts.map(a => a.code).join(', '),\n      Alerts: alerts.map(a => '[' + a.sev + '] ' + a.code + ': ' + a.msg + ' (' + a.owner + ')').join('\\n'),\n      LastChecked: today.toISOString().substring(0, 10),\n    },\n  });\n}\nout.sort((a, b) => rank[a.json.Severity] - rank[b.json.Severity] || a.json.DaysToRenewal - b.json.DaysToRenewal);\nreturn out;\n" },
    position: [448, 300]
  }
});

const writeBack = node({
  type: 'n8n-nodes-base.googleSheets',
  version: 4.7,
  config: {
    name: 'Write scores back to pipeline',
    parameters: {
      resource: 'sheet',
      operation: 'update',
      documentId: { __rl: true, mode: 'id', value: '1PQm-aqOaNSstP6bbpvB-OgTvDWQoe-pdB41HfkCnq3g' },
      sheetName: { __rl: true, mode: 'name', value: 'Pipeline' },
      columns: {
        mappingMode: 'defineBelow',
        matchingColumns: ['Customer'],
        value: {
          Customer: expr('{{ $json.Customer }}'),
          DaysToRenewal: expr('{{ $json.DaysToRenewal }}'),
          Window: expr('{{ $json.Window }}'),
          Month: expr('{{ $json.Month }}'),
          Quarter: expr('{{ $json.Quarter }}'),
          FinalProb: expr('{{ $json.FinalProb }}'),
          WeightedARR: expr('{{ $json.WeightedARR }}'),
          Severity: expr('{{ $json.Severity }}'),
          AlertCodes: expr('{{ $json.AlertCodes }}'),
          LastChecked: expr('{{ $json.LastChecked }}')
        },
        schema: [
          { id: 'Customer', displayName: 'Customer', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
          { id: 'DaysToRenewal', displayName: 'DaysToRenewal', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'Window', displayName: 'Window', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'Month', displayName: 'Month', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'Quarter', displayName: 'Quarter', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'FinalProb', displayName: 'FinalProb', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'WeightedARR', displayName: 'WeightedARR', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'Severity', displayName: 'Severity', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'AlertCodes', displayName: 'AlertCodes', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false },
          { id: 'LastChecked', displayName: 'LastChecked', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: false }
        ]
      },
      options: {}
    },
    credentials: { googleSheetsOAuth2Api: { id: 'h9lcpLixGuP5ku24', name: 'Google Sheets account' } },
    position: [672, 96]
  }
});

const digest = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build daily brief',
    parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: "// One digest per run: book by quarter/month, forecast, and today's action list.\nconst rows = $input.all().map(i => i.json);\nconst eur = n => '\u20ac' + Math.round(n).toLocaleString('en-US');\nconst months = {};\nfor (const r of rows) {\n  const k = r.Quarter + ' | ' + r.Month;\n  months[k] = months[k] || { n: 0, arr: 0, weighted: 0, overdue: 0, p1: 0 };\n  const m = months[k];\n  m.n += 1; m.arr += Number(r.ARR) || 0; m.weighted += r.WeightedARR;\n  if (r.Window === 'Overdue') m.overdue += Number(r.ARR) || 0;\n  if (r.Severity === 'P1') m.p1 += 1;\n}\nconst td = 'style=\"padding:4px 8px;border-bottom:1px solid #ddd\"';\nlet monthRows = '';\nfor (const k of Object.keys(months).sort()) {\n  const m = months[k];\n  monthRows += '<tr><td ' + td + '>' + k + '</td><td ' + td + '>' + m.n + '</td><td ' + td + '>' + eur(m.arr) +\n    '</td><td ' + td + '>' + eur(m.weighted) + '</td><td ' + td + (m.overdue ? ' bgcolor=\"#f8d7da\"' : '') + '>' + eur(m.overdue) +\n    '</td><td ' + td + '>' + m.p1 + '</td></tr>';\n}\nlet actionRows = '';\nfor (const r of rows.filter(r => r.Severity !== 'OK')) {\n  const color = r.Severity === 'P1' ? '#f8d7da' : r.Severity === 'P2' ? '#fff3cd' : '#d4edda';\n  actionRows += '<tr><td ' + td + ' bgcolor=\"' + color + '\"><b>' + r.Severity + '</b></td><td ' + td + '>' + r.Customer +\n    '</td><td ' + td + '>' + eur(Number(r.ARR) || 0) + '</td><td ' + td + '>' + r.DaysToRenewal + 'd</td><td ' + td + '>' +\n    r.Status + '</td><td ' + td + '>' + String(r.Alerts).replace(/\\n/g, '<br>') + '</td></tr>';\n}\nconst total = rows.reduce((s, r) => s + (Number(r.ARR) || 0), 0);\nconst weighted = rows.reduce((s, r) => s + r.WeightedARR, 0);\nconst p1 = rows.filter(r => r.Severity === 'P1').length;\nconst th = 'style=\"text-align:left;padding:4px 8px;background:#2b2b3c;color:#fff\"';\nconst html =\n  '<div style=\"font-family:Arial,sans-serif;font-size:13px\">' +\n  '<h2 style=\"margin:0\">Renewals daily brief: ' + rows[0].LastChecked + '</h2>' +\n  '<p>' + rows.length + ' open renewals | ' + eur(total) + ' ARR | system-weighted new ARR ' + eur(weighted) +\n  ' | <b>' + p1 + ' P1 actions</b></p>' +\n  '<h3>Book by quarter and month</h3><table cellspacing=\"0\"><tr><th ' + th + '>Quarter | Month</th><th ' + th + '>#</th><th ' + th +\n  '>ARR</th><th ' + th + '>Weighted new ARR</th><th ' + th + '>Overdue ARR</th><th ' + th + '>P1</th></tr>' + monthRows + '</table>' +\n  '<h3>Today\\'s actions (highest severity first)</h3><table cellspacing=\"0\"><tr><th ' + th + '>Sev</th><th ' + th + '>Customer</th><th ' + th +\n  '>ARR</th><th ' + th + '>Due in</th><th ' + th + '>Status</th><th ' + th + '>What to do (owner)</th></tr>' + actionRows + '</table>' +\n  '<p style=\"color:#666\">Human check: confirm every P1 has an owner and a date in the CRM before 10:00. Forecast call is updated in the CRM, not here.</p></div>';\nreturn [{ json: { subject: 'Renewals brief ' + rows[0].LastChecked + ': ' + p1 + ' P1, ' + eur(total) + ' open', html, p1 } }];\n" },
    position: [672, 300]
  }
});

const sendBrief = node({
  type: 'n8n-nodes-base.gmail',
  version: 2.2,
  config: {
    name: 'Email brief to Renewals Specialist',
    parameters: {
      resource: 'message',
      operation: 'send',
      sendTo: 'paulazabala95@gmail.com',
      subject: expr('{{ $json.subject }}'),
      emailType: 'html',
      message: expr('{{ $json.html }}'),
      options: { appendAttribution: false }
    },
    credentials: { gmailOAuth2: { id: 'td4rz6YDiV5af77y', name: 'Gmail account' } },
    position: [896, 300]
  }
});

const isP1 = ifElse({
  version: 2.2,
  config: {
    name: 'P1 escalation?',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'strict' },
        conditions: [{ leftValue: expr('{{ $json.Severity }}'), operator: { type: 'string', operation: 'equals' }, rightValue: 'P1' }],
        combinator: 'and'
      }
    },
    position: [672, 504]
  }
});

const escalate = node({
  type: 'n8n-nodes-base.gmail',
  version: 2.2,
  config: {
    name: 'Escalate P1 to owner and manager',
    parameters: {
      resource: 'message',
      operation: 'send',
      sendTo: 'paulazabala95@gmail.com',
      subject: expr('{{ "[P1 renewal] " + $json.Customer + ": " + $json.AlertCodes + " (" + $json.DaysToRenewal + "d)" }}'),
      emailType: 'text',
      message: expr('{{ "Customer: " + $json.Customer + "\\nARR: EUR " + $json.ARR + "\\nRenewal date: " + $json.RenewalDate + " (" + $json.DaysToRenewal + " days, " + $json.Window + ")\\nRenewal Status: " + $json.Status + "\\nOn-time probability: " + Math.round($json.FinalProb * 100) + "%\\n\\nWhat has to happen:\\n" + $json.Alerts + "\\n\\nReply with the owner and date, or update the CRM." }}'),
      options: { appendAttribution: false }
    },
    credentials: { gmailOAuth2: { id: 'td4rz6YDiV5af77y', name: 'Gmail account' } },
    position: [896, 504]
  }
});

const note = sticky(
  '## Renewal forecast and escalation engine\n\nRuns every weekday at 7:30 on the Pipeline tab (same Google Sheet as Daily renewal alerts).\n\n1. **Score**: days to renewal, 30/60/90 window, month and quarter, Renewal Status x countdown probability, health multiplier, weighted new ARR (5% uplift).\n2. **Alerts**: overdue, no quote inside 60 days, signature risk, auto-renew payment blocker, notice window, health risk, upsell signal, CRM hygiene.\n3. **Write back** scores to the sheet (CRM hygiene, forecast).\n4. **One brief** by quarter/month with today\'s actions.\n5. **P1 escalation** email per account.\n\nHuman check: the specialist confirms each P1 owner/date and makes the forecast call. Customer emails stay in Daily renewal alerts (AI draft + approval).\n\nDEMO_TODAY in the Score node is set to 2026-10-20 for the exercise; blank it for live use.',
  [],
  { color: 4, position: [-40, 600], width: 620, height: 380 }
);

export default workflow('renewal-forecast-engine', 'Renewal forecast and escalation engine')
  .add(schedule)
  .to(readPipeline)
  .to(score)
  .to(writeBack)
  .add(score)
  .to(digest)
  .to(sendBrief)
  .add(score)
  .to(isP1.onTrue(escalate))
  .add(note)
  .group('Score the book', [readPipeline, score], { description: 'Reads the Pipeline tab, then scores each renewal: countdown, window, probability, weighted new ARR and alerts' })
  .group('Brief', [digest, sendBrief], { description: 'One email per day: book by quarter and month plus today\'s actions by severity' })
  .group('Escalate', [isP1, escalate], { description: 'Sends a P1 email per account that is overdue, unquoted inside 30 days or blocked' });
