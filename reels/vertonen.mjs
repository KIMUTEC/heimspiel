// Legt einen Sprecher auf ein fertiges Video (z. B. aus Canva oder After Effects).
// Aufruf: node reels/vertonen.mjs <vertonung.json> <video.mp4>
// Ergebnis neben der vertonung.json: vertont.mp4, untertitel.srt, sprecher.wav
//
// teile: [{ "start": Sekunde im Originalvideo, "text": "…" }] – ein Teil ohne "text" markiert nur eine Grenze
// (z. B. den Szenenwechsel), damit die Ansage davor fertig ist, bevor die nächste Szene kommt.
//
// "anhalten": true  → Text und Bild bleiben synchron: Braucht eine Ansage länger als bis zum nächsten Teil,
//                     wird das Bild kurz vor dem nächsten Element eingefroren, bis die Ansage fertig ist.
//                     Das Video wird dadurch länger, das Design bleibt unverändert.
// "kuerzen": true   → (mit anhalten) stehende Bilder nach einer Ansage auf eine kurze Pause kürzen.
// "anhalten": false → Video bleibt gleich lang; zu lange Ansagen werden bis 15 % schneller gesprochen.
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';

const [jsonPfad, videoPfad] = process.argv.slice(2).map(p => p && resolve(p));
if (!jsonPfad || !videoPfad || !existsSync(jsonPfad) || !existsSync(videoPfad)) {
  console.error('Aufruf: node reels/vertonen.mjs <vertonung.json> <video.mp4>'); process.exit(1);
}
const cfg = JSON.parse(readFileSync(jsonPfad, 'utf8'));
const ordner = dirname(jsonPfad), tmp = join(ordner, '.tmp');
mkdirSync(tmp, { recursive: true });
const stimme = join(process.env.HOME, '.cache/piper', (cfg.stimme || 'de_DE-thorsten-high') + '.onnx');
if (!existsSync(stimme)) { console.error('Stimme fehlt. Einrichten: bash reels/einrichten.sh'); process.exit(1); }
const ff = (...a) => execFileSync('ffmpeg', ['-v', 'error', '-y', ...a]);
const dauer = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());
const videoDauer = dauer(videoPfad);
const VOR = cfg.vorlauf ?? 0.35;    // Ansage beginnt so viele Sekunden nach dem Element
const NACH = cfg.abstand ?? 0.45;   // Pause nach der Ansage, bevor das nächste Element kommt
const anhalten = !!cfg.anhalten;

// 1. Ansagen erzeugen
const teile = cfg.teile.map((t, i) => {
  const ende = cfg.teile[i + 1]?.start ?? videoDauer;
  const o = { ...t, platz: ende - t.start, d: 0, wav: null };
  if (!t.text) return o;
  let txt = t.text;
  for (const [a, b] of Object.entries(cfg.aussprache || {})) txt = txt.replaceAll(a, b);
  const roh = join(tmp, `r${i}.wav`), wav = join(tmp, `t${i}.wav`);
  execFileSync('python3', ['-m', 'piper', '-m', stimme, '-f', roh, '--length-scale', String(cfg.tempo || 1), '--sentence-silence', String(cfg.satzpause ?? 0.3)],
    { input: txt, stdio: ['pipe', 'ignore', 'ignore'] });
  ff('-i', roh, '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse', wav);
  o.d = dauer(wav); o.wav = wav;
  if (!anhalten && o.d > o.platz - VOR - NACH) {
    const f = Math.min(1.15, o.d / (o.platz - VOR - NACH));
    ff('-i', wav, '-af', `atempo=${f}`, roh); ff('-i', roh, '-c', 'copy', wav);
    o.d = dauer(wav);
  }
  return o;
});

// 2. Zeitplan: wie lange jedes Stück im neuen Video steht
let neu = teile[0].start;
for (const [i, t] of teile.entries()) {
  t.neuStart = neu;
  if (anhalten && t.text) {
    const vorWechsel = !teile[i + 1] || !teile[i + 1].text ? (cfg.ruhe ?? 1.0) : 0;   // kurze Ruhe vor Szenenwechsel
    const soll = VOR + t.d + NACH + vorWechsel;
    t.halt = Math.max(0, soll - t.platz);
    // "kuerzen": langes Stehen nach der Ansage abschneiden (mind. 1,5 s, damit Animationen fertig werden)
    if (cfg.kuerzen && soll < t.platz) t.platz = Math.max(soll, Math.min(t.platz, 1.5));
  } else t.halt = 0;
  neu += t.platz + t.halt;
  if (t.text) console.log(`${String(t.start.toFixed(1)).padStart(6)} → ${t.neuStart.toFixed(1).padStart(6)} s  ${t.d.toFixed(1)} s${t.halt ? `  (+${t.halt.toFixed(1)} s Halt)` : ''}  ${t.text.slice(0, 60)}`);
}
const gesamt = neu;

// 3. Video: Stücke zuschneiden und am Ende einfrieren (kurz bevor das nächste Element erscheint)
const vid = join(tmp, 'video.mp4');
if (teile.some(t => t.halt > 0) || cfg.kuerzen) {
  const vorher = teile[0].start > 0 ? [{ start: 0, platz: teile[0].start, halt: 0 }] : [];
  const stuecke = [...vorher, ...teile];
  // Jedes Stück einzeln (spart Speicher), dann verlustfrei aneinanderhängen
  const liste = stuecke.map((s, k) => {
    const f = join(tmp, `v${k}.mp4`);
    ff('-ss', s.start.toFixed(3), '-t', s.platz.toFixed(3), '-i', videoPfad, '-an',
      '-vf', `fps=30${s.halt > 0 ? `,tpad=stop_mode=clone:stop_duration=${s.halt.toFixed(3)}` : ''}`,
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-threads', '2', f);
    return `file '${f}'`;
  });
  writeFileSync(join(tmp, 'liste.txt'), liste.join('\n'));
  ff('-f', 'concat', '-safe', '0', '-i', join(tmp, 'liste.txt'), '-c', 'copy', vid);
} else {
  ff('-i', videoPfad, '-an', '-c:v', 'copy', vid);
}

// 4. Tonspur und Zusammenführen
const mitText = teile.filter(t => t.wav);
const ton = join(ordner, 'sprecher.wav');
const filterA = mitText.map((t, k) => `[${k}]adelay=${Math.round((t.neuStart + (anhalten ? VOR : 0)) * 1000)}:all=1[a${k}]`).join(';')
  + ';' + mitText.map((_, k) => `[a${k}]`).join('')
  + `amix=inputs=${mitText.length}:normalize=0,apad,atrim=0:${gesamt},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aus]`;
ff(...mitText.flatMap(t => ['-i', t.wav]), '-filter_complex', filterA, '-map', '[aus]', '-ac', '2', ton);
const ziel = join(ordner, 'vertont.mp4');
ff('-i', vid, '-i', ton, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', ziel);

const zeit = s => { const ms = Math.round(s * 1000); const p = (n, l = 2) => String(n).padStart(l, '0');
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
writeFileSync(join(ordner, 'untertitel.srt'), mitText.map((t, i) => {
  const s = t.neuStart + (anhalten ? VOR : 0);
  return `${i + 1}\n${zeit(s)} --> ${zeit(s + t.d)}\n${t.text}\n`;
}).join('\n'));
rmSync(tmp, { recursive: true, force: true });
console.log(`Fertig: ${ziel}  (${dauer(ziel).toFixed(1)} s, Original ${videoDauer.toFixed(1)} s)`);
