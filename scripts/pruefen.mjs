// Prüft beide Apps: JS-Syntax aller Inline-Skripte und Start im Browser ohne Fehler.
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, join, normalize } from 'node:path';
import vm from 'node:vm';
import { createRequire } from 'node:module';

const root = new URL('..', import.meta.url).pathname;
let fehler = 0;

for (const app of ['index.html', 'vital/index.html']) {
  const html = readFileSync(join(root, app), 'utf8');
  const skripte = [...html.matchAll(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  skripte.forEach((code, i) => {
    try { new vm.Script(code, { filename: `${app}#skript${i + 1}` }); }
    catch (e) { fehler++; console.error(`✗ Syntax ${app} Skript ${i + 1}: ${e.message}`); }
  });
  console.log(`✓ Syntax ${app} (${skripte.length} Skripte)`);
}
for (const sw of ['sw.js', 'vital/sw.js']) {
  try { new vm.Script(readFileSync(join(root, sw), 'utf8')); console.log(`✓ Syntax ${sw}`); }
  catch (e) { fehler++; console.error(`✗ Syntax ${sw}: ${e.message}`); }
}

let pw;
try { pw = await import('playwright'); } catch {
  try { pw = createRequire(import.meta.url)('playwright'); } catch { console.log('… Playwright fehlt, Browser-Test übersprungen'); }
}
if (pw) {
  const typen = { '.html': 'text/html', '.js': 'text/javascript', '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.woff2': 'font/woff2' };
  const server = createServer((req, res) => {
    let p = normalize(decodeURIComponent(req.url.split('?')[0]));
    if (p.endsWith('/')) p += 'index.html';
    try {
      const body = readFileSync(join(root, p));
      res.writeHead(200, { 'content-type': typen[extname(p)] || 'application/octet-stream' });
      res.end(body);
    } catch { res.writeHead(404); res.end(); }
  }).listen(0);
  const port = server.address().port;
  const browser = await pw.chromium.launch();
  for (const pfad of ['/', '/vital/']) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    const probleme = [];
    page.on('pageerror', e => probleme.push(e.message));
    page.on('console', m => { if (m.type() === 'error') probleme.push(m.text()); });
    await page.goto(`http://localhost:${port}${pfad}`, { waitUntil: 'load' });
    await page.waitForTimeout(800);
    if (probleme.length) { fehler++; console.error(`✗ Browser ${pfad}:\n  ` + probleme.join('\n  ')); }
    else console.log(`✓ Browser ${pfad} startet ohne Fehler`);
    await page.close();
  }
  await browser.close();
  server.close();
}
console.log(fehler ? `\n${fehler} Problem(e) gefunden` : '\nAlles in Ordnung');
process.exit(fehler ? 1 : 0);
