// Schneller Check vor jedem Commit: node tools/check.mjs
// 1) JavaScript in index.html und sw.js auf Syntaxfehler prüfen
// 2) Alle Dateien aus der Offline-Liste in sw.js müssen existieren
import {readFileSync, writeFileSync, existsSync, mkdtempSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

let fail = 0;
const html = readFileSync('index.html', 'utf8');
const js = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
const tmp = join(mkdtempSync(join(tmpdir(), 'heimspiel-')), 'app.js');
writeFileSync(tmp, js);
for (const f of [tmp, 'sw.js']) {
  try { execFileSync(process.execPath, ['--check', f], {stdio: 'pipe'}); }
  catch (e) { fail++; console.error('Syntaxfehler in', f === tmp ? 'index.html' : f, '\n' + e.stderr); }
}

const sw = readFileSync('sw.js', 'utf8');
const assets = JSON.parse(sw.match(/ASSETS=(\[[^\]]*\])/)[1].replace(/'/g, '"'));
for (const a of assets) {
  const p = a === './' ? 'index.html' : a.replace(/^\.\//, '');
  if (!existsSync(p)) { fail++; console.error('Fehlt (in sw.js gelistet):', a); }
}

console.log(fail ? `${fail} Problem(e)` : `OK – Syntax sauber, ${assets.length} Offline-Dateien vorhanden, Cache ${sw.match(/V='([^']+)'/)[1]}`);
process.exit(fail ? 1 : 0);
