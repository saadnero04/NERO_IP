// Build the ebook PDF: node ebook/build.js
// Adds a full-page opener before every chapter (with an "In this chapter" list
// taken from its headings) and "Key takeaways" boxes for chapters 1-10.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const TAKEAWAYS = {
  1: ['Cutting costs has a floor; earning more has no ceiling.', 'A service is the fastest second income: one client = income this month.', 'Set one clear target: an amount, a date and weekly hours.'],
  2: ['Sell a result (posts, videos, replies), not "AI".', 'Local and small online businesses are the easiest first clients.', 'Reliability and real samples beat competition.'],
  3: ['Pick ONE service and ONE niche.', 'Posts + short videos is the easiest combo to sell.', 'Write your offer as one sentence.'],
  4: ['One focused hour a day for 7 days is enough to start.', 'Use the prompt formula: role, goal, audience, style, include, avoid, format.', 'Never deliver raw AI output: edit and add real details.'],
  5: ['Samples sell better than experience.', 'Label concept work clearly as concepts.', 'Limit free work to one or two pilots.'],
  6: ['Run local, online and platform outreach at the same time.', 'Personal messages with a free sample get replies.', 'Track every contact and follow up after 3–4 days.'],
  7: ['Sell monthly packages, not hours.', 'Use the minimum-price formula, then raise prices over time.', 'A simple process (onboard, plan, batch, review, report) keeps clients.'],
  8: ['Turn one-off jobs into monthly retainers.', 'Ask for referrals and build real case studies.', 'Systems and templates save hours every week.'],
  9: ['Guaranteed income claims are a red flag.', 'Ask: who is the end customer paying, and for what?', 'Walk away from offers that pay you to recruit.'],
  10: ['About one hour a day for 30 days.', 'Measure: messages → replies → calls → clients.', 'No client yet? Adjust and run another 30 days.'],
};

function opener(label, num, title, headings) {
  const items = headings.slice(0, 8).map(h => `<li>${h}</li>`).join('');
  const badge = num ? `<div class="num">${num}</div>` : '<div class="num">★</div>';
  return `<section class="divider">${badge}<div class="label">${label}</div><h1>${title}</h1>` +
    (items ? `<div class="inside"><p>In this chapter</p><ul>${items}</ul></div>` : '') + `</section>\n`;
}

(async () => {
  const src = path.join(__dirname, 'src');
  let html = fs.readdirSync(src).filter(f => f.endsWith('.html')).sort()
    .map(f => fs.readFileSync(path.join(src, f), 'utf8')).join('\n');

  const parts = html.split('<section class="chapter">');
  let out = parts[0];
  for (const chunk of parts.slice(1)) {
    const m = chunk.match(/^\s*<div class="kicker">(.*?)<\/div>\s*<h1>([\s\S]*?)<\/h1>/);
    let body = chunk;
    if (m) {
      const label = m[1];
      const n = (label.match(/Chapter (\d+)/) || [])[1];
      const end = chunk.indexOf('</section>');
      const section = chunk.slice(0, end);
      const heads = [...section.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/g)].map(x => x[1]);
      if (n === '01') {
        out += `<section class="part"><div class="label">PART 1</div><h1>Your first income with AI services</h1>` +
          `<p style="font-size:14pt;max-width:150mm;opacity:.9">From zero to your first paying client: choose a service, learn it, prove it and sell it.</p></section>\n`;
      }
      out += opener(label, n ? String(parseInt(n, 10)) : null, m[2], heads);
      const tk = n && TAKEAWAYS[parseInt(n, 10)];
      if (tk && !section.includes('class="takeaways"')) {
        const box = `<div class="takeaways"><h3>Key takeaways</h3><ul>${tk.map(t => `<li>${t}</li>`).join('')}</ul></div>\n`;
        body = section + box + chunk.slice(end);
      }
    }
    out += '<section class="chapter">' + body;
  }

  const htmlPath = path.join(__dirname, 'ebook.html');
  fs.writeFileSync(htmlPath, out);

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle', timeout: 20000 }).catch(() => {});
  await page.pdf({
    path: path.join(__dirname, 'AI-Side-Income-Playbook-2026.pdf'),
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:8px;color:#8a958f;font-family:Arial;padding:0 20mm;display:flex;justify-content:space-between"><span>The AI Side Income Playbook 2026</span><span class="pageNumber"></span></div>',
  });
  await browser.close();
  console.log('PDF written');
})();
