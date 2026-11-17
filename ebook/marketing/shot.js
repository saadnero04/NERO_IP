const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await p.goto('file://' + __dirname + '/mockup.html'); await p.waitForTimeout(500);
  await p.screenshot({ path: __dirname + '/book-mockup.png' }); await b.close();
})();
