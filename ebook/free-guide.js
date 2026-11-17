// Build the free lead-magnet PDF: node ebook/free-guide.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + __dirname + '/free-guide.html'); await p.waitForTimeout(300);
  await p.pdf({ path: __dirname + '/Free-Guide-5-AI-Side-Hustles.pdf', format: 'A4', printBackground: true });
  await b.close(); console.log('free guide written');
})();
