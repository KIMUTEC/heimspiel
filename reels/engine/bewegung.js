// Bewegung für KIMUTEC-Reels: Spuren (Keyframes für beliebige Elemente) und Figuren mit Gelenken.
// Wird von buehne.html geladen. Alles hängt nur von der Zeit ab, jedes Bild ist reproduzierbar.
//
// SPUR   <g id='fenster' data-spur='[{"t":0,"x":0},{"t":"m2","x":-300,"e":"w"}]'>…</g>
//        Felder je Key: t (Zeitwert), x, y (px), r (Grad), s / sx / sy (Skalierung), o (Deckkraft), e (Kurve bis zu diesem Key)
//        Kurven: w weich (Standard), s sanft, l linear, e anfahren, a ausrollen, f federnd.
//        Drehpunkt: data-ursprung='460px 300px' oder 'unten' / 'oben' / 'links' / 'rechts' (sonst Mitte).
// FIGUR  <g data-t='0.3' data-figur='{"typ":"monteur","s":1,"boden":600,"z":[Keys]}'></g>
//        Typen: monteur (beige, Kappe), kunde (hell), kundin (hell, Zopf), arbeiter (grau, Kappe).
//        Key: t, d (Dauer, Standard 0.6), e (Kurve), x, b (Blick 1 = rechts, -1 = links), pose (Name aus POSEN),
//             Winkel ru ko aV eV aH eH bV kV bH kH (Grad), zV / zH (Griffziel der Hand: [x,y] oder
//             {"an":"id","x":…,"y":…} = Punkt eines Elements mit data-spur, null = loslassen),
//             pV / pH (Werkzeug in der Hand: handy laser klemmbrett stift bohrer kartusche tasse tablet daumen, null = leer),
//             gehen (true = läuft zur neuen x-Position), osz (Liste {"g":"eV","a":12,"f":2,"dauer":1.5} = Schwingen).
//        Winkel: 0 = nach unten, positiv = nach vorn (in Blickrichtung). Ellbogen beugen nach vorn, Knie nach hinten.
(function () {
  const r = Math.PI / 180, sin = a => Math.sin(a * r), cos = a => Math.cos(a * r);
  const kl = x => Math.max(0, Math.min(1, x)), kl1 = x => Math.max(-1, Math.min(1, x));
  const KURVE = {
    w: x => .5 - Math.cos(Math.PI * kl(x)) / 2,
    s: x => { x = kl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; },
    l: x => kl(x),
    e: x => Math.pow(kl(x), 3),
    a: x => 1 - Math.pow(1 - kl(x), 3),
    f: x => { x = kl(x); const c = 1.45; return x >= 1 ? 1 : 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }
  };
  window.KURVE = KURVE;
  const SPUR = window.SPUR = {};

  // ---------- Spuren ----------
  window.baueSpur = function (t, el, sz, zeitWert) {
    let v = { x: 0, y: 0, r: 0, s: 1, sx: null, sy: null, o: 1 };
    t.spur = JSON.parse(el.dataset.spur).map(k => { v = { ...v, ...k }; return { ...v, t: zeitWert(k.t, sz, 0), e: k.e || 'w' }; })
      .sort((a, b) => a.t - b.t);
    let ox, oy; const u = el.dataset.ursprung;
    if (u && u.includes('px')) [ox, oy] = u.split(/\s+/).map(parseFloat);
    else {
      const b = el.getBBox(); ox = b.x + b.width / 2; oy = b.y + b.height / 2;
      if (u === 'unten') oy = b.y + b.height; else if (u === 'oben') oy = b.y;
      else if (u === 'links') ox = b.x; else if (u === 'rechts') ox = b.x + b.width;
    }
    t.ox = ox; t.oy = oy;
    el.style.transformBox = 'view-box'; el.style.transformOrigin = `${ox}px ${oy}px`;
    if (el.id) SPUR[el.id] = { tx: 0, ty: 0, r: 0, sx: 1, sy: 1, ox, oy };
  };
  window.spurWert = function (sp, ts) {
    const fertig = k => ({ x: k.x, y: k.y, r: k.r, sx: k.sx ?? k.s, sy: k.sy ?? k.s, o: k.o });
    if (ts <= sp[0].t) return fertig(sp[0]);
    for (let i = 1; i < sp.length; i++) {
      const b = sp[i];
      if (ts < b.t) {
        const a = sp[i - 1], p = (KURVE[b.e] || KURVE.w)((ts - a.t) / Math.max(1e-3, b.t - a.t)), L = (x, y) => x + (y - x) * p;
        return { x: L(a.x, b.x), y: L(a.y, b.y), r: L(a.r, b.r), sx: L(a.sx ?? a.s, b.sx ?? b.s), sy: L(a.sy ?? a.s, b.sy ?? b.s), o: L(a.o, b.o) };
      }
    }
    return fertig(sp[sp.length - 1]);
  };
  // Punkt (px,py) eines Elements mit Spur in Bildkoordinaten (wie die CSS-Transformation)
  function punktVon(id, px, py) {
    const q = SPUR[id]; if (!q) return [px, py];
    const dx = (px - q.ox) * q.sx, dy = (py - q.oy) * q.sy, c = cos(q.r), s = sin(q.r);
    return [q.ox + q.tx + dx * c - dy * s, q.oy + q.ty + dx * s + dy * c];
  }
  function loese(z) {
    if (!z) return null;
    if (Array.isArray(z)) return z;
    if (z.mix) { const a = loese(z.mix[0]), b = loese(z.mix[1]); if (!a) return b; if (!b) return a; return [a[0] + (b[0] - a[0]) * z.p, a[1] + (b[1] - a[1]) * z.p]; }
    if (z.an) { const p = punktVon(z.an, z.x || 0, z.y || 0); return [p[0] + (z.dx || 0), p[1] + (z.dy || 0)]; }
    return null;
  }

  // ---------- Figuren ----------
  const FARBEN = {
    monteur: { v: '#D8B79C', h: '#9E8571', kopf: '#D8B79C', kappe: '#B08F74' },
    kunde: { v: '#EEEAE2', h: '#A7A29A', kopf: '#EEEAE2' },
    kundin: { v: '#EEEAE2', h: '#A7A29A', kopf: '#EEEAE2', zopf: '#C9C4BB' },
    arbeiter: { v: '#C6CDD0', h: '#848C90', kopf: '#C6CDD0', kappe: '#9FB3BC' }
  };
  const M = { rumpf: 92, hals: 39, kopf: 24, oa: 56, ua: 52, os: 64, us: 62, dick: 15, rdick: 18 };
  const POSEN = window.POSEN = {
    stehen: { ru: 2, ko: 0, aV: 8, eV: 14, aH: -8, eH: 12, bV: 4, kV: 2, bH: -4, kH: 2 },
    zeigen: { ru: 1, ko: -6, aV: 112, eV: 4, aH: -6, eH: 14, bV: 4, kV: 2, bH: -4, kH: 2 },
    erklaeren: { ru: 3, ko: -2, aV: 62, eV: 58, aH: 16, eH: 64, bV: 4, kV: 2, bH: -4, kH: 2 },
    tippen: { ru: 5, ko: 24, aV: 26, eV: 108, aH: 22, eH: 112, bV: 4, kV: 2, bH: -4, kH: 2 },
    telefon: { ru: 2, ko: 6, aV: 34, eV: 148, aH: -8, eH: 12, bV: 4, kV: 2, bH: -4, kH: 2 },
    messen: { ru: 3, ko: 4, aV: 86, eV: 6, aH: 30, eH: 72, bV: 8, kV: 4, bH: -10, kH: 4 },
    tragen: { ru: 4, ko: 0, aV: 52, eV: 64, aH: 46, eH: 70, bV: 4, kV: 2, bH: -4, kH: 2 },
    heben: { ru: -2, ko: -8, aV: 128, eV: 26, aH: 120, eH: 30, bV: 6, kV: 4, bH: -6, kH: 4 },
    hocken: { ru: 24, ko: 8, aV: 62, eV: 40, aH: 40, eH: 60, bV: 84, kV: 124, bH: 52, kH: 118 },
    knien: { ru: 8, ko: 4, aV: 70, eV: 30, aH: 30, eH: 60, bV: 86, kV: 90, bH: -18, kH: 106 },
    bohren: { ru: 4, ko: 2, aV: 84, eV: 14, aH: 64, eH: 46, bV: 10, kV: 4, bH: -12, kH: 4 },
    schreiben: { ru: 6, ko: 26, aV: 36, eV: 96, aH: 34, eH: 104, bV: 4, kV: 2, bH: -4, kH: 2 },
    jubeln: { ru: -2, ko: -10, aV: 158, eV: 14, aH: 150, eH: 18, bV: 6, kV: 2, bH: -6, kH: 2 },
    daumen: { ru: 1, ko: -2, aV: 38, eV: 118, aH: -8, eH: 12, bV: 4, kV: 2, bH: -4, kH: 2 },
    sitzen: { ru: -8, ko: -4, aV: 26, eV: 82, aH: 8, eH: 36, bV: 86, kV: 88, bH: 82, kH: 86 },
    winken: { ru: 1, ko: -4, aV: 150, eV: 32, aH: -8, eH: 12, bV: 4, kV: 2, bH: -4, kH: 2 },
    haende: { ru: 3, ko: 0, aV: 52, eV: 30, aH: -8, eH: 14, bV: 4, kV: 2, bH: -4, kH: 2 }
  };
  const FELDER = ['x', 'b', 'ru', 'ko', 'aV', 'eV', 'aH', 'eH', 'bV', 'kV', 'bH', 'kH', 'wV', 'wH', 'zyV', 'zyH'];

  // Werkzeuge: Griff bei (0,0). "abs" = feste Lage, sonst folgt es dem Unterarm (Unterarm zeigt nach +y).
  const W = {
    handy: { abs: true, svg: "<rect x='-10' y='-44' width='20' height='40' rx='4' fill='#151817' stroke='#EEEAE2' stroke-width='3'/><rect x='-6' y='-38' width='12' height='26' rx='1.5' fill='#D8B79C' opacity='.8'/>" },
    laser: { abs: true, svg: "<rect x='-4' y='-11' width='40' height='20' rx='4' fill='#EEEAE2'/><rect x='4' y='-6' width='12' height='9' rx='1.5' fill='#151817'/><circle cx='36' cy='-1' r='4.5' fill='#E0533F'/>" },
    klemmbrett: { abs: true, svg: "<g transform='rotate(-14)'><rect x='-2' y='-62' width='46' height='62' rx='4' fill='#EEEAE2'/><rect x='12' y='-68' width='18' height='10' rx='3' fill='#6E6A64'/><line x1='6' y1='-48' x2='36' y2='-48' stroke='#9A958E' stroke-width='3'/><line x1='6' y1='-38' x2='36' y2='-38' stroke='#9A958E' stroke-width='3'/><line x1='6' y1='-28' x2='28' y2='-28' stroke='#9A958E' stroke-width='3'/></g>" },
    stift: { abs: false, svg: "<line x1='0' y1='-2' x2='0' y2='20' stroke='#151817' stroke-width='5' stroke-linecap='round'/><line x1='0' y1='-2' x2='0' y2='20' stroke='#EEEAE2' stroke-width='2.5' stroke-linecap='round'/>" },
    bohrer: { abs: true, svg: "<rect x='-8' y='-30' width='50' height='20' rx='6' fill='#EEEAE2'/><rect x='-6' y='-14' width='14' height='26' rx='4' fill='#EEEAE2'/><rect x='-8' y='8' width='18' height='8' rx='2' fill='#6E6A64'/><line x1='42' y1='-20' x2='66' y2='-20' stroke='#A7A29A' stroke-width='4' stroke-linecap='round'/>" },
    kartusche: { abs: true, svg: "<rect x='-6' y='-30' width='60' height='18' rx='5' fill='#EEEAE2'/><line x1='54' y1='-21' x2='76' y2='-24' stroke='#EEEAE2' stroke-width='5' stroke-linecap='round'/><rect x='-6' y='-14' width='12' height='26' rx='3' fill='#6E6A64'/>" },
    tasse: { abs: true, svg: "<path d='M-12 -22 h24 v18 a6 6 0 0 1 -6 6 h-12 a6 6 0 0 1 -6 -6z' fill='#EEEAE2'/><path d='M12 -18 a7 7 0 0 1 0 12' fill='none' stroke='#EEEAE2' stroke-width='3'/><path d='M-4 -30 q4 -6 0 -12 M4 -30 q4 -6 0 -12' fill='none' stroke='#A7A29A' stroke-width='2' opacity='.8'/>" },
    tablet: { abs: true, svg: "<rect x='-2' y='-58' width='44' height='58' rx='5' fill='#151817' stroke='#EEEAE2' stroke-width='3'/><rect x='5' y='-50' width='30' height='40' fill='#D8B79C' opacity='.55'/>" },
    daumen: { abs: true, svg: "<line x1='0' y1='-4' x2='0' y2='-22' stroke='currentColor' stroke-width='10' stroke-linecap='round'/>" }
  };

  function ik2(S, T, L1, L2) {
    const dx = T[0] - S[0], dy = T[1] - S[1];
    const d = Math.max(Math.abs(L1 - L2) + 1, Math.min(L1 + L2 - .5, Math.hypot(dx, dy)));
    const ad = Math.atan2(dx, dy) / r;
    const al = Math.acos(kl1((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))) / r;
    const be = Math.acos(kl1((L1 * L1 + L2 * L2 - d * d) / (2 * L1 * L2))) / r;
    return [ad - al, 180 - be];
  }
  const kurz = (a, b) => ((b - a + 540) % 360) - 180;   // kürzester Winkelweg

  // Gangzyklus: Standbein bleibt am Boden stehen (Fußpunkt läuft linear mit der Strecke)
  const GA = 24, SIN_GA = Math.sin(GA * r);
  function gang(phi) {
    const bein = u => {
      u = ((u % 1) + 1) % 1;
      if (u >= .25 && u < .75) { const q = (u - .25) / .5; return [Math.asin(SIN_GA * (1 - 2 * q)) / r, 3]; }
      const q = ((u - .75 + 1) % 1) / .5;
      return [-GA + 2 * GA * KURVE.w(q), 44 * Math.sin(Math.PI * q)];
    };
    const [bV, kV] = bein(phi), [bH, kH] = bein(phi + .5), w = Math.sin(2 * Math.PI * phi);
    return { bV, kV, bH, kH, aV: -17 * w, aH: 17 * w };
  }

  window.baueFigur = function (el, sz, zeitWert) {
    const sp = JSON.parse(el.dataset.figur);
    const F = FARBEN[sp.typ || 'monteur'] || FARBEN.monteur;
    const s = sp.s || 1, boden = sp.boden ?? 560;
    const mk = (tag, a) => { const e = document.createElementNS('http://www.w3.org/2000/svg', tag); for (const k in a) e.setAttribute(k, a[k]); el.appendChild(e); return e; };
    const glied = farbe => mk('path', { fill: 'none', stroke: farbe, 'stroke-width': M.dick * s, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
    const teile = {
      schatten: mk('ellipse', { rx: 44 * s, ry: 8 * s, fill: '#000', opacity: .36 }),
      zopf: F.zopf ? mk('circle', { r: 11 * s, fill: F.zopf }) : null,
      beinH: glied(F.h), armH: glied(F.h), wzH: mk('g', { color: F.h }),
      rumpf: mk('path', { fill: 'none', stroke: F.v, 'stroke-width': M.rdick * s, 'stroke-linecap': 'round' }),
      kopf: mk('circle', { r: M.kopf * s, fill: F.kopf }),
      kappe: F.kappe ? mk('path', { d: 'M-25 -2 A25 25 0 0 1 25 -2 L38 3 Q30 7 24 6 L-25 6 Z', fill: F.kappe }) : null,
      beinV: glied(F.v), armV: glied(F.v), wzV: mk('g', { color: F.v })
    };
    // Keys vorbereiten
    let ziel = { x: 0, b: 1, ...POSEN.stehen, wV: 0, wH: 0, zyV: 0, zyH: 0, zV: null, zH: null, pV: null, pH: null };
    const ks = sp.z.map(k => ({ ...k, t: zeitWert(k.t, sz, 0) })).sort((a, b) => a.t - b.t).map(k => {
      const z = { ...ziel };
      if (k.pose) Object.assign(z, POSEN[k.pose] || {});
      for (const f of FELDER) if (k[f] != null) z[f] = k[f];
      if ('zV' in k) { z.zV = k.zV; z.wV = k.zV ? 1 : 0; }
      if ('zH' in k) { z.zH = k.zH; z.wH = k.zH ? 1 : 0; }
      if ('pV' in k) z.pV = k.pV; if ('pH' in k) z.pH = k.pH;
      const d = k.d ?? (k.gehen ? Math.max(.7, Math.abs(z.x - ziel.x) / (165 * s)) : .6);
      const neu = { t: k.t, d, e: k.e || 'w', ziel: z, gehen: !!k.gehen, osz: k.osz || [], wechselV: z.pV !== ziel.pV, wechselH: z.pH !== ziel.pH };
      ziel = z; return neu;
    });
    let weg = 0;
    ks.forEach((k, i) => {
      k.start = i === 0 ? { ...k.ziel } : zustandKey(ks[i - 1], k.t);
      k.weg0 = weg; k.richt = (k.ziel.b < 0 ? -1 : 1); if (k.gehen) weg += (k.ziel.x - k.start.x) * k.richt;
      k.gehenVor = i > 0 && ks[i - 1].gehen && Math.abs(ks[i - 1].t + ks[i - 1].d - k.t) < .05;
    });
    ks.forEach((k, i) => { k.gehenNach = i < ks.length - 1 && ks[i + 1].gehen && Math.abs(k.t + k.d - ks[i + 1].t) < .05; });
    sz.figuren.push({ el, s, boden, ks, F, teile, cache: {}, saat: (sp.saat ?? (sz.figuren.length * 1.7 + 0.4)) });
  };

  function misch(a, b, p) { if (!a) return b; if (!b) return a; if (a === b) return a; return { mix: [a, b], p }; }
  function zustandKey(k, ts) {
    const p = (KURVE[k.e] || KURVE.w)((ts - k.t) / k.d), a = k.start, b = k.ziel, z = {};
    for (const f of FELDER) z[f] = a[f] + (b[f] - a[f]) * p;
    z.b = a.b + (b.b - a.b) * KURVE.w((ts - k.t) / Math.min(k.d, .3));
    z.zV = misch(a.zV, b.zV, p); z.zH = misch(a.zH, b.zH, p);
    z.pV = b.pV; z.pH = b.pH;
    return z;
  }

  window.zeichneFigur = function (fg, ts) {
    const { ks, s, boden, teile: T } = fg;
    let i = 0; for (let j = 0; j < ks.length; j++) if (ks[j].t <= ts) i = j;
    const k = ks[i];
    const z = ts < ks[0].t ? { ...ks[0].ziel } : zustandKey(k, ts);
    // Gehen
    let geh = 0;
    if (k.gehen && ts >= k.t && ts <= k.t + k.d) {
      const ein = k.gehenVor ? 1 : KURVE.w((ts - k.t) / .3), aus = k.gehenNach ? 1 : KURVE.w((k.t + k.d - ts) / .3);
      geh = Math.min(ein, aus);
      const phi = (k.weg0 + (z.x - k.start.x) * k.richt) / (4 * (M.os + M.us) * s * SIN_GA);
      const g = gang(phi);
      for (const f of ['bV', 'kV', 'bH', 'kH']) z[f] = z[f] + (g[f] - z[f]) * geh;
      z.aV += g.aV * geh; z.aH += g.aH * geh; z.ru += 3 * geh;
    }
    // Atmen und kleine Bewegungen im Stand
    const ruhe = 1 - geh, sd = fg.saat;
    z.ru += .9 * Math.sin(2 * Math.PI * .26 * ts + sd) * ruhe;
    z.ko += 1.3 * Math.sin(2 * Math.PI * .21 * ts + sd * 1.7) * ruhe;
    z.aV += 1.4 * Math.sin(2 * Math.PI * .3 * ts + sd * .6) * ruhe;
    z.aH += 1.4 * Math.sin(2 * Math.PI * .27 * ts + sd * 2.3) * ruhe;
    // Schwingungen aus den Keys
    ks.forEach((q, j) => {
      if (!q.osz.length || ts < q.t) return;
      for (const o of q.osz) {
        const ende = o.dauer != null ? q.t + o.dauer : (j < ks.length - 1 ? ks[j + 1].t : 1e9);
        if (ts > ende + .25) continue;
        const ab = (o.ab || 0), t0 = q.t + ab;
        if (ts < t0) continue;
        const fade = Math.min(KURVE.w((ts - t0) / .2), KURVE.w((ende - ts) / .25 + 1e-9));
        z[o.g] += (o.a || 8) * Math.sin(2 * Math.PI * (o.f || 2) * (ts - t0) + (o.ph || 0)) * fade;
      }
    });
    // Beine und Bodenkontakt
    const knie = b => [sin(b) * M.os, cos(b) * M.os];
    const fuss = (b, kn) => { const K = knie(b), a = b - kn; return [K[0] + sin(a) * M.us, K[1] + cos(a) * M.us]; };
    const KV = knie(z.bV), FV = fuss(z.bV, z.kV), KH = knie(z.bH), FH = fuss(z.bH, z.kH);
    const tief = Math.max(KV[1], FV[1], KH[1], FH[1]) + M.dick / 2;
    const X = z.x, Y = boden - tief * s, bl = z.b, bi = Math.abs(bl) < .15 ? (bl < 0 ? -.15 : .15) : bl;
    const Wp = p => [X + bl * s * p[0], Y + s * p[1]];
    const S = [sin(z.ru) * M.rumpf, -cos(z.ru) * M.rumpf];
    const H = [S[0] + sin(z.ru + z.ko) * M.hals, S[1] - cos(z.ru + z.ko) * M.hals];
    const arm = (a, e, w, ziel, zy) => {
      if (w > .001 && ziel) {
        let t = loese(ziel); if (t && zy) t = [t[0], t[1] + zy];
        if (t) { const L = [(t[0] - X) / (bi * s), (t[1] - Y) / s], [ia, ie] = ik2(S, L, M.oa, M.ua); a = a + kurz(a, ia) * w; e = e + kurz(e, ie) * w; }
      }
      const E = [S[0] + sin(a) * M.oa, S[1] + cos(a) * M.oa], Hd = [E[0] + sin(a + e) * M.ua, E[1] + cos(a + e) * M.ua];
      return { E, Hd, ua: a + e };
    };
    const AV = arm(z.aV, z.eV, z.wV, z.zV, z.zyV), AH = arm(z.aH, z.eH, z.wH, z.zH, z.zyH);
    const pfad = (...ps) => 'M' + ps.map(p => Wp(p).map(v => v.toFixed(1)).join(' ')).join(' L');
    const O = [0, 0];
    T.beinH.setAttribute('d', pfad(O, KH, FH)); T.beinV.setAttribute('d', pfad(O, KV, FV));
    T.armH.setAttribute('d', pfad(S, AH.E, AH.Hd)); T.armV.setAttribute('d', pfad(S, AV.E, AV.Hd));
    const Sr = [S[0] * .94, S[1] * .94];
    T.rumpf.setAttribute('d', pfad([0, -4], Sr));
    const Hw = Wp(H); T.kopf.setAttribute('cx', Hw[0].toFixed(1)); T.kopf.setAttribute('cy', Hw[1].toFixed(1));
    const kw = (z.ru + z.ko).toFixed(1);
    if (T.kappe) T.kappe.setAttribute('transform', `translate(${Hw[0].toFixed(1)} ${Hw[1].toFixed(1)}) scale(${(bl * s).toFixed(3)} ${s}) rotate(${kw})`);
    if (T.zopf) { const Zp = Wp([H[0] - 20 * Math.cos((z.ru + z.ko) * r), H[1] + 6]); T.zopf.setAttribute('cx', Zp[0].toFixed(1)); T.zopf.setAttribute('cy', Zp[1].toFixed(1)); }
    T.schatten.setAttribute('cx', X.toFixed(1)); T.schatten.setAttribute('cy', (boden + 3 * s).toFixed(1));
    // Werkzeuge
    const werkzeug = (g, name, A, seite) => {
      const art = typeof name === 'string' ? name : name && name.art;
      if (fg.cache[seite] !== art) { g.innerHTML = art && W[art] ? W[art].svg : ''; fg.cache[seite] = art; }
      if (!art || !W[art]) return;
      let wechsel = 1;
      if (k[seite === 'V' ? 'wechselV' : 'wechselH'] && ts >= k.t) wechsel = KURVE.f((ts - k.t) / .3);
      const P = Wp(A.Hd), w = W[art].abs ? -(name.w || 0) : -A.ua + (name.w || 0);
      g.setAttribute('transform', `translate(${P[0].toFixed(1)} ${P[1].toFixed(1)}) scale(${(bl * s * wechsel).toFixed(3)} ${(s * wechsel).toFixed(3)}) rotate(${w.toFixed(1)})`);
    };
    werkzeug(T.wzV, z.pV, AV, 'V'); werkzeug(T.wzH, z.pH, AH, 'H');
  };
})();
