// Build the ebook PDF: node ebook/build.js
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const src = path.join(__dirname, 'src');
  const html = fs.readdirSync(src).filter(f => f.endsWith('.html')).sort()
    .map(f => fs.readFileSync(path.join(src, f), 'utf8')).join('\n');
  const htmlPath = path.join(__dirname, 'ebook.html');
  fs.writeFileSync(htmlPath, html);

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' }).catch(() => page.goto('file://' + htmlPath));
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
