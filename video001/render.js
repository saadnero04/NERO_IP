// Render frames: node render.js [fps] [onlyTimes,comma,separated]
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
(async () => {
  const fps = parseInt(process.argv[2] || '24', 10);
  const only = process.argv[3] ? process.argv[3].split(',').map(Number) : null;
  const tim = fs.readFileSync(path.join(__dirname, 'timings.json'), 'utf8');
  const html = fs.readFileSync(path.join(__dirname, 'scene.html'), 'utf8').replace('__TIMINGS__', tim);
  fs.writeFileSync(path.join(__dirname, '.scene.built.html'), html);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, '.scene.built.html'));
  const outDir = path.join(__dirname, only ? 'preview' : 'frames'); fs.mkdirSync(outDir, { recursive: true });
  const total = JSON.parse(tim).total;
  const times = only || [...Array(Math.ceil(total * fps)).keys()].map(i => i / fps);
  for (let i = 0; i < times.length; i++) {
    await p.evaluate(t => window.renderFrame(t), times[i]);
    await p.screenshot({ path: path.join(outDir, only ? `t${times[i]}.png` : `f${String(i).padStart(5, '0')}.jpg`), type: only ? 'png' : 'jpeg', ...(only ? {} : { quality: 90 }) });
  }
  await b.close(); console.log('frames', times.length);
})();
