// Legt einen Sprecher auf ein fertiges Video (z. B. aus Canva oder After Effects).
// Aufruf: node reels/vertonen.mjs <vertonung.json> <video.mp4>
// Ergebnis neben der vertonung.json: vertont.mp4, untertitel.srt, sprecher.wav
// Ist eine Ansage länger als ihr Abschnitt, wird sie bis 15 % schneller gesprochen, sonst gibt es eine Warnung.
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
const dauer = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());
const videoDauer = dauer(videoPfad);

const teile = cfg.teile.map((t, i) => {
  const ende = t.ende ?? cfg.teile[i + 1]?.start ?? videoDauer;
  const platz = ende - t.start - (cfg.abstand ?? 0.35);
  let txt = t.text;
  for (const [a, b] of Object.entries(cfg.aussprache || {})) txt = txt.replaceAll(a, b);
  const roh = join(tmp, `r${i}.wav`), wav = join(tmp, `t${i}.wav`);
  execFileSync('python3', ['-m', 'piper', '-m', stimme, '-f', roh, '--length-scale', String(cfg.tempo || 1), '--sentence-silence', '0.2'],
    { input: txt, stdio: ['pipe', 'ignore', 'ignore'] });
  // Stille am Anfang/Ende abschneiden, damit die Ansage genau am Abschnittsstart beginnt
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', roh, '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse', wav]);
  let d = dauer(wav), faktor = 1;
  if (d > platz) {
    faktor = Math.min(1.15, d / platz);
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', wav, '-af', `atempo=${faktor}`, roh]);
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', roh, '-c', 'copy', wav]);
    d = dauer(wav);
  }
  const warn = d > platz + 0.05 ? `  ⚠ ${(d - platz).toFixed(1)} s zu lang – Text kürzen` : '';
  console.log(`${String(i + 1).padStart(2)}  ${t.start.toFixed(1).padStart(6)} s  ${d.toFixed(1)}/${platz.toFixed(1)} s${faktor > 1 ? `  (×${faktor.toFixed(2)})` : ''}${warn}`);
  return { ...t, wav, d };
});

const ton = join(ordner, 'sprecher.wav');
const filter = teile.map((t, k) => `[${k}]adelay=${Math.round(t.start * 1000)}:all=1[a${k}]`).join(';')
  + ';' + teile.map((_, k) => `[a${k}]`).join('')
  + `amix=inputs=${teile.length}:normalize=0,apad,atrim=0:${videoDauer},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aus]`;
execFileSync('ffmpeg', ['-v', 'error', '-y', ...teile.flatMap(t => ['-i', t.wav]), '-filter_complex', filter, '-map', '[aus]', '-ac', '2', ton]);
execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', videoPfad, '-i', ton, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
  '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', join(ordner, 'vertont.mp4')]);

const zeit = s => { const ms = Math.round(s * 1000); const p = (n, l = 2) => String(n).padStart(l, '0');
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
writeFileSync(join(ordner, 'untertitel.srt'), teile.map((t, i) => `${i + 1}\n${zeit(t.start)} --> ${zeit(t.start + t.d)}\n${t.text}\n`).join('\n'));
rmSync(tmp, { recursive: true, force: true });
console.log('Fertig: ' + join(ordner, 'vertont.mp4'));
