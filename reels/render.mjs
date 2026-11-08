// Erstellt ein Reel (1080×1920, 30 fps, MP4) aus einem Drehbuch.
// Aufruf: node reels/render.mjs reels/projekte/<name>/drehbuch.json [--schnell]
//   --schnell  nur Vorschaubilder und Ton, kein Video (zum Prüfen)
// Ergebnis im Projektordner: reel.mp4, vorschau.jpg, untertitel.srt, sprecher.wav
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { execFileSync, spawn } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const arg = process.argv.slice(2);
const dbPfad = resolve(arg.find(a => !a.startsWith('--')) || '');
if (!existsSync(dbPfad)) { console.error('Drehbuch fehlt: node reels/render.mjs <drehbuch.json>'); process.exit(1); }
const schnell = arg.includes('--schnell');
const db = JSON.parse(readFileSync(dbPfad, 'utf8'));
const ordner = dirname(dbPfad), tmp = join(ordner, '.tmp');
mkdirSync(tmp, { recursive: true });
const FPS = db.fps || 30;
const STIMME = db.stimme || 'de_DE-thorsten-high';
const stimmPfad = join(process.env.HOME, '.cache/piper', STIMME + '.onnx');

const dauer = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

// 1. Sprecher pro Szene (Piper, lokal). "aussprache" ersetzt Wörter nur für die Stimme.
// "stimme": "edge:de-DE-ConradNeural" = Microsoft-Neural-Stimme (online, flüssiger), sonst Piper-Stimme (lokal).
// Bei edge-Stimmen markiert "|" im Sprechertext Stellen, auf die sich Elemente mit data-t="m1", "m2" … beziehen.
const EDGE = STIMME.startsWith('edge:');
if (!db.tonspur && !EDGE && !existsSync(stimmPfad)) {
  console.error(`Stimme fehlt: ${stimmPfad}\nEinrichten: bash reels/einrichten.sh`); process.exit(1);
}
const zeiten = { szenen: [], gesamt: 0 };
let t = 0;
db.szenen.forEach((s, i) => {
  let sp = 0, marken = [];
  const wav = join(tmp, `s${i}.wav`);
  if (s.sprecher && !db.tonspur) {
    let txt = s.sprecher;
    for (const [a, b] of Object.entries(db.aussprache || {})) txt = txt.replaceAll(a, b);
    if (EDGE) {
      const mp3 = join(tmp, `s${i}.mp3`);
      const aus = execFileSync('python3', ['-I', join(import.meta.dirname, 'stimme.py'), STIMME.slice(5), db.tempo ?? '-5%', mp3], { input: txt }).toString();
      marken = JSON.parse(aus).marken;
      execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', mp3, '-ar', '48000', '-ac', '1', wav]);
    } else {
      execFileSync('python3', ['-m', 'piper', '-m', stimmPfad, '-f', wav, '--length-scale', String(db.tempo || 1), '--sentence-silence', '0.25'],
        { input: txt.replaceAll('|', ''), stdio: ['pipe', 'ignore', 'ignore'] });
    }
    sp = dauer(wav);
  }
  const sprechStart = s.sprechStart ?? 0.3;
  const d = s.dauer || Math.max(2.5, sprechStart + sp + (s.pause ?? 0.7));
  zeiten.szenen.push({ start: t, dauer: d, sprechStart, sprechDauer: sp, marken, wav: sp ? wav : null });
  console.log(`Szene ${i + 1}: ${d.toFixed(1)} s  ${s.titel?.replace(/\n/g, ' ') || ''}`);
  t += d;
});
zeiten.gesamt = t;
console.log(`Gesamt: ${t.toFixed(1)} s`);

// 2. Tonspur: Szenen-Ansagen an ihre Startzeit legen, Lautheit für Instagram angleichen
const ton = join(ordner, 'sprecher.wav');
if (db.tonspur) {
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', resolve(ordner, db.tonspur), '-t', String(t), '-ar', '48000', '-ac', '2', ton]);
} else {
  const teile = zeiten.szenen.filter(z => z.wav);
  const ein = teile.flatMap(z => ['-i', z.wav]);
  const filter = teile.map((z, k) => `[${k}]adelay=${Math.round((z.start + z.sprechStart) * 1000)}:all=1[a${k}]`).join(';')
    + ';' + teile.map((_, k) => `[a${k}]`).join('') + `amix=inputs=${teile.length}:normalize=0,apad,atrim=0:${t},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aus]`;
  execFileSync('ffmpeg', ['-v', 'error', '-y', ...ein, '-filter_complex', filter, '-map', '[aus]', '-ac', '2', ton]);
}

// 3. Untertitel
const zeit = s => { const ms = Math.round(s * 1000); const p = (n, l = 2) => String(n).padStart(l, '0');
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
writeFileSync(join(ordner, 'untertitel.srt'), zeiten.szenen.map((z, i) => db.szenen[i].sprecher && z.sprechDauer
  ? `${i + 1}\n${zeit(z.start + z.sprechStart)} --> ${zeit(z.start + z.sprechStart + z.sprechDauer)}\n${db.szenen[i].sprecher.replaceAll('|', '')}\n` : '').filter(Boolean).join('\n'));

// 4. Bilder rendern
const req = createRequire(import.meta.url);
let pw; try { pw = req('playwright'); } catch { pw = await import('playwright'); }
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('Fehler auf der Bühne:', e.message));
await page.goto(pathToFileURL(join(import.meta.dirname, 'engine/buehne.html')).href);
await page.evaluate(async ([d, z]) => { await document.fonts.ready; ladeReel(d, z); }, [db, zeiten]);
await page.evaluate(() => document.fonts.ready);

// Vorschau: Bild aus der Mitte jeder Szene (kurz vor Ende, wenn alles sichtbar ist)
const vorschau = [];
for (const [i, z] of zeiten.szenen.entries()) {
  await page.evaluate(s => zeige(s), z.start + z.dauer - 0.45);
  const f = join(tmp, `v${i}.png`); await page.screenshot({ path: f }); vorschau.push(f);
}
const spalten = Math.min(5, vorschau.length), zeilen = Math.ceil(vorschau.length / spalten);
execFileSync('ffmpeg', ['-v', 'error', '-y', ...vorschau.flatMap(f => ['-i', f]), '-filter_complex',
  vorschau.map((_, k) => `[${k}]scale=270:480[v${k}]`).join(';') + ';' + vorschau.map((_, k) => `[v${k}]`).join('')
  + `xstack=inputs=${vorschau.length}:layout=${vorschau.map((_, k) => `${(k % spalten) * 270}_${Math.floor(k / spalten) * 480}`).join('|')}:fill=black`,
  '-frames:v', '1', join(ordner, 'vorschau.jpg')]);
console.log('Vorschau: ' + join(ordner, 'vorschau.jpg'));

if (!schnell) {
  const n = Math.round(t * FPS), aus = join(ordner, 'reel.mp4');
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', ton,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', aus], { stdio: ['pipe', 'inherit', 'inherit'] });
  const fertig = new Promise((ok, nein) => ff.on('close', c => c === 0 ? ok() : nein(new Error('ffmpeg ' + c))));
  for (let k = 0; k < n; k++) {
    await page.evaluate(s => zeige(s), k / FPS);
    const bild = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(bild)) await new Promise(r => ff.stdin.once('drain', r));
    if (k % (FPS * 5) === 0) process.stdout.write(`\rBilder ${k}/${n}`);
  }
  ff.stdin.end(); await fertig;
  console.log(`\rVideo: ${aus} (${t.toFixed(1)} s)`);
}
await browser.close();
rmSync(tmp, { recursive: true, force: true });
