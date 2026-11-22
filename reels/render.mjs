// Erstellt ein Reel (1080×1920, 30 fps, MP4) aus einem Drehbuch.
// Aufruf: node reels/render.mjs reels/projekte/<name>/drehbuch.json [Optionen]
//   --schnell          nur Vorschaubilder und Ton, kein Video (zum Prüfen)
//   --schaetzen        ohne Stimme: Sprechzeiten und Marken werden geschätzt (stille Vorschau zum Bauen)
//   --szene=N          nur Szene N als Kontaktbogen vorschau-szeneN.jpg (Abstand --raster=0.5 Sekunden)
//   --szene=N --video  nur Szene N als kurzes Video szeneN.mp4 (mit Ton)
// Ergebnis im Projektordner: reel.mp4, vorschau.jpg, untertitel.srt, sprecher.wav
//
// Stimmen ("stimme" im Drehbuch):
//   "elevenlabs"        fertige Ansagen aus ton/s01.json … (ElevenLabs „with-timestamps“, siehe reels/elevenlabs.py)
//   "edge:<Name>"       Microsoft-Neural-Stimme (online), "chatterbox[:ref.wav]" lokal, sonst Piper-Modellname
// Ein "|" im Sprechertext markiert eine Stelle; Elemente mit data-t="m1", "m2" … erscheinen genau bei diesem Wort.
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync, spawn } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const arg = process.argv.slice(2);
const opt = n => { const a = arg.find(x => x.startsWith(`--${n}=`)); return a ? a.slice(n.length + 3) : null; };
const dbPfad = resolve(arg.find(a => !a.startsWith('--')) || '');
if (!existsSync(dbPfad)) { console.error('Drehbuch fehlt: node reels/render.mjs <drehbuch.json>'); process.exit(1); }
const schnell = arg.includes('--schnell'), schaetzen = arg.includes('--schaetzen');
const nurSzene = +(opt('szene') || 0), raster = +(opt('raster') || 0.5), szVideo = arg.includes('--video');
const db = JSON.parse(readFileSync(dbPfad, 'utf8'));
const ordner = dirname(dbPfad), tmp = join(ordner, '.tmp-' + process.pid);   // eigener Ordner je Lauf (parallele Läufe stören sich nicht)
mkdirSync(tmp, { recursive: true });
const FPS = db.fps || 30;
const STIMME = db.stimme || 'de_DE-thorsten-high';
const stimmPfad = join(process.env.HOME, '.cache/piper', STIMME + '.onnx');

const dauer = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

// Text, wie er an die Stimme geht (Aussprache ersetzt, Leerraum vereinheitlicht) und Position jeder |-Marke darin.
// Dieselbe Regel steht in reels/elevenlabs.py – beide müssen gleich bleiben.
function sendeText(sprecher, aussprache) {
  const teile = sprecher.split('|').map(t => { for (const [a, b] of Object.entries(aussprache || {})) t = t.replaceAll(a, b); return t; });
  const norm = x => x.split(/\s+/).filter(Boolean).join(' ');
  const idx = []; let vor = '';
  for (let k = 0; k < teile.length - 1; k++) { vor += teile[k]; idx.push(norm(vor).length); }
  return { text: norm(teile.join('')), idx };
}
const ersterBuchstabe = (text, i) => { while (i < text.length && /\s/.test(text[i])) i++; return Math.min(i, text.length - 1); };

// Grobe Sprechzeit ohne Stimme (für stille Vorschauen beim Bauen)
function schaetze(sprecher, aussprache) {
  const { text, idx } = sendeText(sprecher, aussprache);
  const bis = []; let tt = 0;
  for (const c of text) { bis.push(tt); tt += /[.!?:]/.test(c) ? .42 : c === ',' ? .24 : c === ' ' ? .02 : .062; }
  return { dauer: tt + .2, marken: idx.map(i => +bis[ersterBuchstabe(text, i)].toFixed(3)) };
}

// Marken aus der Zeichen-Zeitleiste von ElevenLabs
function elfMarken(sprecher, aussprache, al, nr) {
  const { text, idx } = sendeText(sprecher, aussprache);
  const z = al.characters, st = al.character_start_times_seconds;
  const gleich = z.join('') === text;
  if (!gleich) console.warn(`Szene ${nr}: Text der Ansage weicht vom Sprechertext ab – Marken werden angenähert.`);
  return idx.map(i => {
    let j = gleich ? i : Math.round(i * z.length / text.length);
    while (j < z.length - 1 && /\s/.test(z[j])) j++;
    return +st[Math.min(j, st.length - 1)].toFixed(3);
  });
}

// 1. Sprecher pro Szene
const EDGE = STIMME.startsWith('edge:'), ELF = STIMME.startsWith('elevenlabs'), CB = STIMME.startsWith('chatterbox');
if (!db.tonspur && !schaetzen && !EDGE && !ELF && !CB && !existsSync(stimmPfad)) {
  console.error(`Stimme fehlt: ${stimmPfad}\nEinrichten: bash reels/einrichten.sh`); process.exit(1);
}
let cbErg = null;
if (CB && !db.tonspur && !schaetzen) {
  const texte = db.szenen.map(s => { let t = s.sprecher || ''; for (const [a, b] of Object.entries(db.aussprache || {})) t = t.replaceAll(a, b); return t; });
  const nur = texte.map((t, i) => [t, i]).filter(([t]) => t);
  const ref = STIMME.includes(':') ? resolve(ordner, STIMME.split(':')[1]) : null;
  const cache = join(import.meta.dirname, '.cache/stimme'); mkdirSync(cache, { recursive: true });
  const schluessel = t => createHash('sha1').update(t + '|' + (ref || '')).digest('hex').slice(0, 16);
  const fehlt = nur.filter(([t]) => !existsSync(join(cache, schluessel(t) + '.json')));
  if (fehlt.length) {
    writeFileSync(join(tmp, 'cb_auftrag.json'), JSON.stringify({ texte: fehlt.map(([t]) => t), ordner: tmp, referenz: ref, ziele: fehlt.map(([t]) => join(cache, schluessel(t))) }));
    const py = process.env.CHATTERBOX_PY || join(process.env.HOME, '.venv-chatterbox/bin/python');
    console.log(`Stimme: ${fehlt.length} von ${nur.length} Ansagen werden erzeugt (Rest aus dem Zwischenspeicher)`);
    execFileSync(py, [join(import.meta.dirname, 'stimme_chatterbox.py'), join(tmp, 'cb_auftrag.json'), join(tmp, 'cb_erg.json')], { stdio: ['ignore', 'inherit', 'ignore'] });
  }
  cbErg = {}; nur.forEach(([t, i]) => { cbErg[i] = JSON.parse(readFileSync(join(cache, schluessel(t) + '.json'), 'utf8')); });
}
const zeiten = { szenen: [], gesamt: 0 };
let t = 0;
db.szenen.forEach((s, i) => {
  let sp = 0, marken = [], mitTon = false;
  const wav = join(tmp, `s${i}.wav`);
  if (s.sprecher && !db.tonspur) {
    let txt = s.sprecher;
    for (const [a, b] of Object.entries(db.aussprache || {})) txt = txt.replaceAll(a, b);
    if (schaetzen) {
      const g = schaetze(s.sprecher, db.aussprache); marken = g.marken; sp = g.dauer;
    } else {
      if (ELF) {
        const jf = join(ordner, db.tonOrdner || 'ton', `s${String(i + 1).padStart(2, '0')}.json`);
        if (!existsSync(jf)) { console.error(`Ansage fehlt: ${jf} (siehe reels/elevenlabs.py)`); process.exit(1); }
        const ant = JSON.parse(readFileSync(jf, 'utf8'));
        const mp3 = join(tmp, `s${i}.mp3`); writeFileSync(mp3, Buffer.from(ant.audio_base64, 'base64'));
        marken = elfMarken(s.sprecher, db.aussprache, ant.alignment || ant.normalized_alignment, i + 1);
        execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', mp3, '-ar', '48000', '-ac', '1', wav]);
      } else if (cbErg) {
        marken = cbErg[i].marken;
        execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', cbErg[i].wav, '-ar', '48000', '-ac', '1', wav]);
      } else if (EDGE) {
        const mp3 = join(tmp, `s${i}.mp3`);
        const aus = execFileSync('python3', ['-I', join(import.meta.dirname, 'stimme.py'), STIMME.slice(5), db.tempo ?? '-5%', mp3], { input: txt }).toString();
        marken = JSON.parse(aus).marken;
        execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', mp3, '-ar', '48000', '-ac', '1', wav]);
      } else {
        execFileSync('python3', ['-m', 'piper', '-m', stimmPfad, '-f', wav, '--length-scale', String(db.tempo || 1), '--sentence-silence', '0.25'],
          { input: txt.replaceAll('|', ''), stdio: ['pipe', 'ignore', 'ignore'] });
      }
      sp = dauer(wav); mitTon = true;
    }
  }
  const sprechStart = s.sprechStart ?? 0.3;
  const d = s.dauer || Math.max(2.5, sprechStart + sp + (s.pause ?? 0.7));
  zeiten.szenen.push({ start: t, dauer: d, sprechStart, sprechDauer: sp, marken, wav: mitTon ? wav : null });
  console.log(`Szene ${i + 1}: ${d.toFixed(1)} s  ${s.titel?.replace(/\n/g, ' ').replace(/<\/?em>/g, '') || ''}`);
  t += d;
});
zeiten.gesamt = t;
console.log(`Gesamt: ${t.toFixed(1)} s${t > 180 ? '  ACHTUNG: länger als 3 Minuten (Instagram-Grenze)' : ''}`);
writeFileSync(join(ordner, 'zeiten.json'), JSON.stringify(zeiten.szenen.map(({ wav, ...z }) => z), null, 1));

// 2. Tonspur: Szenen-Ansagen an ihre Startzeit legen, Lautheit für Instagram angleichen
const ton = join(ordner, 'sprecher.wav');
const teileTon = zeiten.szenen.filter(z => z.wav);
if (db.tonspur) {
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', resolve(ordner, db.tonspur), '-t', String(t), '-ar', '48000', '-ac', '2', ton]);
} else if (!teileTon.length) {
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', String(t), ton]);
} else {
  const ein = teileTon.flatMap(z => ['-i', z.wav]);
  const filter = teileTon.map((z, k) => `[${k}]adelay=${Math.round((z.start + z.sprechStart) * 1000)}:all=1[a${k}]`).join(';')
    + ';' + teileTon.map((_, k) => `[a${k}]`).join('') + `amix=inputs=${teileTon.length}:normalize=0,apad,atrim=0:${t},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aus]`;
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
const browser = [];
async function neueSeite() {
  const b = await pw.chromium.launch(); browser.push(b);
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('Fehler auf der Bühne:', e.message));
  await p.goto(pathToFileURL(join(import.meta.dirname, 'engine/buehne.html')).href);
  await p.evaluate(async ([d, z]) => { await document.fonts.ready; ladeReel(d, z); }, [db, zeiten]);
  await p.evaluate(() => document.fonts.ready);
  return p;
}
const page = await neueSeite();
const ende = async () => { for (const b of browser) await b.close(); rmSync(tmp, { recursive: true, force: true }); };
const videoAus = (datei, ab, lang, eingabe = ['-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-']) => spawn('ffmpeg', ['-v', 'error', '-y', ...eingabe,
  '-ss', String(ab), '-t', String(lang), '-i', ton, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS),
  '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', datei], { stdio: ['pipe', 'inherit', 'inherit'] });
async function bilderInsVideo(datei, ab, lang) {
  const n = Math.round(lang * FPS);
  // Mehrere Browser rendern abwechselnd Bilder (alles hängt nur von der Zeit ab) – auf 2 Kernen etwa doppelt so schnell
  const W = Math.max(1, Math.min(+(opt('parallel') || (await import('node:os')).cpus().length), 4));
  if (W > 1 && n > 150) {
    const bo = join(tmp, 'bilder'); mkdirSync(bo, { recursive: true });
    const seiten = [page]; for (let w = 1; w < W; w++) seiten.push(await neueSeite());
    let fertig = 0;
    await Promise.all(seiten.map(async (pg, w) => {
      for (let k = w; k < n; k += W) {
        await pg.evaluate(s => zeige(s), ab + k / FPS);
        await pg.screenshot({ type: 'jpeg', quality: 92, path: join(bo, `f${String(k).padStart(6, '0')}.jpg`) });
        if (++fertig % (FPS * 5) === 0) process.stdout.write(`\rBilder ${fertig}/${n}`);
      }
    }));
    const ff = videoAus(datei, ab, lang, ['-framerate', String(FPS), '-i', join(bo, 'f%06d.jpg')]);
    ff.stdin.end();
    await new Promise((ok, nein) => ff.on('close', c => c === 0 ? ok() : nein(new Error('ffmpeg ' + c))));
    rmSync(bo, { recursive: true, force: true });
    return;
  }
  const ff = videoAus(datei, ab, lang);
  const fertig = new Promise((ok, nein) => ff.on('close', c => c === 0 ? ok() : nein(new Error('ffmpeg ' + c))));
  for (let k = 0; k < n; k++) {
    await page.evaluate(s => zeige(s), ab + k / FPS);
    const bild = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(bild)) await new Promise(r => ff.stdin.once('drain', r));
    if (k % (FPS * 5) === 0) process.stdout.write(`\rBilder ${k}/${n}`);
  }
  ff.stdin.end(); await fertig;
}

// --bild=12.5,30 → Einzelbilder in voller Größe (Sekunden ab Reelbeginn), z. B. zum Prüfen von Details
if (opt('bild')) {
  for (const s of opt('bild').split(',').map(Number)) {
    await page.evaluate(x => zeige(x), s);
    await page.screenshot({ path: join(ordner, `bild-${s.toFixed(2)}.png`) });
  }
  console.log('Einzelbilder im Projektordner (bild-*.png)');
  await ende(); process.exit(0);
}

if (nurSzene) {
  const z = zeiten.szenen[nurSzene - 1];
  if (!z) { console.error('Diese Szene gibt es nicht.'); await ende(); process.exit(1); }
  if (szVideo) {
    const aus = join(ordner, `szene${nurSzene}.mp4`);
    await bilderInsVideo(aus, z.start, z.dauer);
    console.log(`\rVideo: ${aus}`);
  } else {
    // Kontaktbogen mit Zeitangabe (Sekunden ab Szenenstart) in jedem Bild
    await page.evaluate(() => { const d = document.createElement('div'); d.id = 'uhr';
      d.style.cssText = 'position:absolute;left:24px;bottom:24px;z-index:9;font:700 64px Montserrat;color:#fff;background:#C0392B;padding:6px 18px'; document.body.appendChild(d); });
    const bilder = [];
    for (let s = 0.05; s < z.dauer; s += raster) {
      await page.evaluate(([sek, rel]) => { zeige(sek); document.getElementById('uhr').textContent = rel.toFixed(2) + ' s'; }, [z.start + s, s]);
      const f = join(tmp, `k${String(bilder.length).padStart(3, '0')}.png`); await page.screenshot({ path: f }); bilder.push(f);
    }
    const sp = 6, zl = Math.ceil(bilder.length / sp);
    while (bilder.length < sp * zl) bilder.push(bilder[bilder.length - 1]);
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '1', '-i', join(tmp, 'k%03d.png'), '-frames:v', '1', '-vf', `scale=270:480,tile=${sp}x${zl}`, join(ordner, `vorschau-szene${nurSzene}.jpg`)]);
    console.log('Kontaktbogen: ' + join(ordner, `vorschau-szene${nurSzene}.jpg`));
  }
  await ende(); process.exit(0);
}

// Vorschau: Bild aus jeder Szene (kurz vor Ende, wenn alles sichtbar ist)
const vorschau = [];
for (const [i, z] of zeiten.szenen.entries()) {
  await page.evaluate(s => zeige(s), z.start + z.dauer - 0.45);
  const f = join(tmp, `v${i}.png`); await page.screenshot({ path: f }); vorschau.push(f);
}
const spalten = Math.min(6, vorschau.length), zeilen = Math.ceil(vorschau.length / spalten);
execFileSync('ffmpeg', ['-v', 'error', '-y', ...vorschau.flatMap(f => ['-i', f]), '-filter_complex',
  vorschau.map((_, k) => `[${k}]scale=270:480[v${k}]`).join(';') + ';' + vorschau.map((_, k) => `[v${k}]`).join('')
  + `xstack=inputs=${vorschau.length}:layout=${vorschau.map((_, k) => `${(k % spalten) * 270}_${Math.floor(k / spalten) * 480}`).join('|')}:fill=black`,
  '-frames:v', '1', join(ordner, 'vorschau.jpg')]);
console.log('Vorschau: ' + join(ordner, 'vorschau.jpg'));

if (!schnell) {
  const aus = join(ordner, 'reel.mp4');
  await bilderInsVideo(aus, 0, t);
  console.log(`\rVideo: ${aus} (${t.toFixed(1)} s)`);
}
await ende();
