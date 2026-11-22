# Erzeugt drehbuch.json für das Reel „So arbeiten wir“ (Kontakt bis Abnahme), Version 2:
# erklärender, fachlicher Sprechertext und Strichmännchen mit Gelenken, die die echten Tätigkeiten zeigen.
# Aufruf: python3 reels/projekte/09-ablauf/bauen.py && node reels/render.mjs reels/projekte/09-ablauf/drehbuch.json
# Stille Vorschau ohne Stimme: … render.mjs …/drehbuch.json --schaetzen --szene=4
import json, math, os, sys, random

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, '..', '..'))
from figur import figur, spur, k, an, osz

INK, AKZ, MUT, LIN, GLAS = '#EEEAE2', '#D8B79C', '#A3A09A', '#3A3E3C', '#1F2A30'
DUNKEL, KARTE, BLAU = '#111312', '#1A1D1C', '#9FB3BC'

# ---------- Bausteine
def T(x, y, s, size=28, w=700, fill=INK, anchor='start', ls=None, attr=''):
    st = f'font-family:Montserrat;font-weight:{w};font-size:{size}px;fill:{fill}' + (f';letter-spacing:{ls}px' if ls else '')
    return f"<text x='{x}' y='{y}' text-anchor='{anchor}' style='{st}'{attr}>{s}</text>"

def chip(x, y, text, t, voll=False, breite=None, h=64, size=29):
    b = breite or 34 + len(text) * 19
    fill, farbe = ('url(#verlauf-akzent)', DUNKEL) if voll else ('url(#verlauf-karte)', INK)
    return (f"<g class='pop' data-t='{t}' data-d='0.5'><rect x='{x}' y='{y}' width='{b}' height='{h}' rx='{h/2}' fill='{fill}' stroke='{AKZ}' stroke-opacity='.55' stroke-width='2' filter='url(#schatten)'/>"
            + T(x + b / 2, y + h / 2 + size * .36, text, size, 700, farbe, 'middle') + '</g>')

def blase(x, y, w, zeilen, t, kunde=True, spitze=None):
    h = 30 + 42 * len(zeilen)
    fill, farbe = ('url(#verlauf-karte)', INK) if kunde else ('url(#verlauf-akzent)', DUNKEL)
    sx = spitze if spitze is not None else (x + 30 if kunde else x + w - 30)
    pfeil = f'M{sx} {y+h-1} l0 26 l30 -26z' if sx < x + w / 2 else f'M{sx} {y+h-1} l0 26 l-30 -26z'
    txt = ''.join(T(x + 28, y + 48 + 42 * i, z, 30, 600, farbe) for i, z in enumerate(zeilen))
    return (f"<g class='pop' data-t='{t}' data-d='0.55' data-ursprung='{'left bottom' if sx < x + w / 2 else 'right bottom'}'>"
            f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='26' fill='{fill}' filter='url(#schatten)'/><path d='{pfeil}' fill='{fill}'/>{txt}</g>")

def haken(cx, cy, r=26, fill=AKZ, farbe=DUNKEL):
    return (f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{fill}'/>"
            f"<path d='M{cx-r*.45:.1f} {cy+r*.02:.1f} l{r*.3:.1f} {r*.3:.1f} l{r*.62:.1f} {-r*.64:.1f}' fill='none' stroke='{farbe}' stroke-width='{r*.22:.1f}' stroke-linecap='round' stroke-linejoin='round'/>")

def stern(cx, cy, r, fill=AKZ):
    p = ' '.join(f'{cx + (r if i % 2 == 0 else r * .45) * math.cos(-math.pi / 2 + i * math.pi / 5):.1f},{cy + (r if i % 2 == 0 else r * .45) * math.sin(-math.pi / 2 + i * math.pi / 5):.1f}' for i in range(10))
    return f"<polygon points='{p}' fill='{fill}'/>"

def funkeln(cx, cy, r, t):
    return f"<g class='pop' data-t='{t}' data-d='0.4' data-aus='{t}+1.6'><path d='M{cx} {cy-r} Q{cx} {cy} {cx+r} {cy} Q{cx} {cy} {cx} {cy+r} Q{cx} {cy} {cx-r} {cy} Q{cx} {cy} {cx} {cy-r}z' fill='{INK}'/></g>"

def zahnrad(cx, cy, r1, r2, n):
    pts = []
    for i in range(n * 2):
        a0 = math.pi * i / n
        r = r2 if i % 2 == 0 else r1
        for da in (-0.32, 0.32):
            a = a0 + da * math.pi / n
            pts.append(f'{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}')
    return f"<polygon points='{' '.join(pts)}' fill='none' stroke='{INK}' stroke-width='4'/><circle cx='{cx}' cy='{cy}' r='{r1 * .35:.0f}' fill='none' stroke='{AKZ}' stroke-width='4'/>"

def fenster(x, y, w, h, alt=False, griff=True):
    rahmen = '#8A8F8C' if alt else '#F2EFE8'
    s = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='4' fill='{rahmen}'/><rect x='{x+22}' y='{y+22}' width='{w-44}' height='{h-44}' fill='{GLAS}'/>"
    if alt:
        s += f"<path d='M{x+40} {y+60} l40 30 l-20 40 l50 20' fill='none' stroke='#5A605D' stroke-width='3'/>"
    else:
        s += f"<line x1='{x+44}' y1='{y+h*.38:.0f}' x2='{x+w*.42:.0f}' y2='{y+52}' stroke='#3A4246' stroke-width='3'/>"
        if griff:
            s += f"<rect x='{x+w-17}' y='{y+h/2-22:.0f}' width='8' height='44' rx='3' fill='#2A2D2C'/>"
    return s

def schraube(cx, cy, t):
    return (f"<g class='pop' data-t='{t}' data-d='0.35'><circle cx='{cx}' cy='{cy}' r='9' fill='{AKZ}' stroke='{DUNKEL}' stroke-width='2'/>"
            f"<path d='M{cx-5} {cy} h10 M{cx} {cy-5} v10' stroke='{DUNKEL}' stroke-width='2.5'/></g>"
            + ''.join(f"<g data-t='{t}' data-d='0.15' data-aus='{t}+0.5' data-bewegung='{dx},{dy},{t},0.6'><circle cx='{cx}' cy='{cy}' r='4' fill='{MUT}'/></g>"
                      for dx, dy in ((-26, -14), (-18, 16), (22, -20), (26, 12))))

random.seed(9)
def konfetti(cx, cy, t, n=64):
    farben = [AKZ, INK, BLAU, '#C49A78']
    out = ''
    for i in range(n):
        w = random.uniform(-1, 1) * math.pi; r = random.uniform(200, 560)
        dx, dy = r * math.cos(w), r * math.sin(w) * 0.8 - 60
        form = (f"<rect x='{cx-13}' y='{cy-6}' width='26' height='12' rx='3' fill='{random.choice(farben)}'/>" if i % 2
                else f"<circle cx='{cx}' cy='{cy}' r='9' fill='{random.choice(farben)}'/>")
        tt = f'{t}+{random.uniform(0, .25):.2f}'
        out += (f"<g data-t='{tt}' data-d='0.2' data-aus='{t}+{3.0+random.uniform(0,.8):.1f}' data-bewegung='{dx:.0f},{dy:.0f},{tt},1.8'>"
                f"<g data-t='{tt}' data-drehen='{random.choice([-1,1])*random.uniform(200,520):.0f}'>{form}</g></g>")
    return out

def wand(y0, y1, boden=None):
    s = f"<rect class='wand' x='0' y='{y0}' width='920' height='{y1-y0}'/>"
    if boden:
        s += f"<line x1='0' y1='{boden}' x2='920' y2='{boden}' stroke='{INK}' stroke-width='4'/>"
    return s

def hand_y(boden, s=1.0, tiefe=0.42):
    """Griffhöhe auf Hüft-/Brusthöhe einer stehenden Figur."""
    becken = boden - 133.5 * s
    return round(becken - 92 * s * tiefe)

# ============ Szene 1: Der Weg in 8 Schritten, Kunde und Monteur geben sich die Hand
schritte = ['Kontakt', 'Beratung', 'Aufmaß', 'Angebot', 'Produktion', 'Lieferung', 'Montage', 'Abnahme']
pkt = [(70 + i * 111, 300 - i * 33) for i in range(8)]
b1 = f"<path class='zeichnen leuchten' data-t='m2' data-d='2.2' d='M{' L'.join(f'{x} {y}' for x, y in pkt)}' fill='none' stroke='{AKZ}' stroke-width='5'/>"
for i, (x, y) in enumerate(pkt):
    ty = y + 62 if i % 2 == 0 else y - 40
    b1 += (f"<g class='pop' data-t='m2+{i*0.26:.2f}' data-d='0.45'><circle cx='{x}' cy='{y}' r='25' fill='{DUNKEL}' stroke='{AKZ}' stroke-width='4'/>"
           + T(x, y + 9, i + 1, 25, 800, INK, 'middle') + T(x, ty, schritte[i], 21, 600, MUT, 'middle') + '</g>')
dx1, dy1 = pkt[7][0] - pkt[0][0], pkt[7][1] - pkt[0][1]
b1 += spur(f"<circle cx='{pkt[0][0]}' cy='{pkt[0][1]}' r='14' fill='#F6E3D2' class='leuchten'/>",
           [k(-9, x=0, y=0, o=0), k('m3-0.2', o=0), k('m3', o=1), k('m4+0.2', x=dx1, y=dy1, e='s'), k('m4+0.5', o=0)])
b1 += f"<g class='pop' data-t='m4+0.3'>{haken(pkt[7][0], pkt[7][1] - 62, 22)}</g>"
b1 += (f"<g class='pop' data-t='0.5' data-aus='m2' data-ursprung='left bottom'><circle cx='226' cy='300' r='36' fill='url(#verlauf-karte)' stroke='{AKZ}' stroke-width='3'/>"
       + T(226, 316, '?', 44, 800, AKZ, 'middle') + f"<circle cx='196' cy='344' r='8' fill='url(#verlauf-karte)' stroke='{AKZ}' stroke-width='2'/><circle cx='182' cy='362' r='5' fill='{AKZ}'/></g>")
B1, S1 = 590, 0.85
hy1 = hand_y(B1, S1)
b1 += figur('kunde', B1, [k(-9, x=150, b=1, pose='telefon'), k('m2', pose='stehen', d=.5), k('m3', x=395, gehen=True, d=1.7),
                          k('m4+0.1', pose='haende', zV=[460, hy1], d=.45, osz=[osz('zyV', 6, 2.6, dauer=1.4, ab=.4)]),
                          k('m4+1.8', pose='stehen', zV=None)], s=S1, t='0.2')
b1 += figur('monteur', B1, [k(-9, x=770, b=-1), k('m1', pose='winken', osz=[osz('eV', 20, 2.3, dauer=1.8)], d=.45), k('m2', pose='stehen', d=.4), k('m3', x=525, gehen=True, d=1.7),
                            k('m4+0.1', pose='haende', zV=[460, hy1], d=.45, osz=[osz('zyV', 6, 2.6, dauer=1.4, ab=.4)]),
                            k('m4+1.8', pose='stehen', zV=None)], s=S1, t='0.2', saat=2.1)

# ============ Szene 2: Kontakt – Kunde schreibt, KIMUTEC antwortet, Termin steht
B2 = 620
b2 = (blase(230, 10, 470, ['Hallo! Wir brauchen', 'neue Fenster.'], 'm1+0.4')
      + chip(230, 170, 'Nachricht', 'm2') + chip(452, 170, 'E-Mail', 'm3') + chip(618, 170, 'Telefon', 'm4')
      + blase(250, 272, 480, ['Gern! Wann passt', 'ein Termin bei Ihnen?'], 'm5+0.3', kunde=False))
b2 += (f"<g class='pop' data-t='m6+0.2' data-d='0.55'><rect x='330' y='430' width='260' height='176' rx='16' fill='url(#verlauf-karte)' stroke='{AKZ}' stroke-opacity='.6' stroke-width='2' filter='url(#schatten)'/>"
       f"<path d='M330 446 a16 16 0 0 1 16 -16 h228 a16 16 0 0 1 16 16 v30 h-260z' fill='{AKZ}'/>"
       + T(460, 467, 'TERMIN', 24, 800, DUNKEL, 'middle', 3) + ''.join(f"<rect x='{356 + c*44}' y='{496 + r*30}' width='30' height='20' rx='4' fill='{LIN}'/>" for r in range(3) for c in range(5) if (r, c) != (1, 2))
       + haken(460, 536, 22) + '</g>')
b2 += figur('kunde', B2, [k(-9, x=120, b=1, pose='tippen', pV='handy'),
                          k('m1', pose='tippen', osz=[osz('eV', 5, 4.2, dauer=2.6), osz('aV', 3, 3.1, dauer=2.6)], d=.3),
                          k('m6+0.6', osz=[osz('ko', 7, 2.2, dauer=1.2)], d=.2)], t='0.2')
b2 += figur('monteur', B2, [k(-9, x=800, b=-1, pose='stehen', pH='tablet'),
                            k('m5-0.4', pose='tippen', pV='tablet', pH=None, osz=[osz('eV', 5, 4.4, dauer=1.6)], d=.4),
                            k('m6+0.6', pose='daumen', pV='daumen', osz=[osz('ko', 6, 2.2, dauer=1.0)], d=.45)], t='0.3', saat=3.3)

# ============ Szene 3: Beratung vor Ort – Begrüßung, Blick auf Fenster und Mauerwerk, Wünsche
B3, S3 = 620, 0.92
hy3 = hand_y(B3, S3)
b3 = (f"<path class='zeichnen' data-t='0.2' data-d='1.1' d='M20 270 L200 110 L380 270 M50 252 L50 620 L350 620 L350 252' fill='none' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
      f"<g data-t='0.6'>{fenster(92, 318, 116, 136, alt=True)}<rect x='252' y='470' width='76' height='150' fill='none' stroke='{AKZ}' stroke-width='4'/></g>"
      f"<g class='pop' data-t='m1'><g transform='rotate(-8 300 120)'><rect x='205' y='92' width='190' height='56' rx='8' fill='{AKZ}'/>"
      + T(300, 130, 'KOSTENLOS', 26, 800, DUNKEL, 'middle') + '</g></g>'
      f"<g class='pop' data-t='m2+0.5'><circle cx='150' cy='386' r='86' fill='none' stroke='{AKZ}' stroke-width='5' stroke-dasharray='14 10'/></g>")
for i, (w, m) in enumerate([('Wärmeschutz', 'm4'), ('Schallschutz', 'm5'), ('Sicherheit', 'm6'), ('Design', 'm7'), ('Budget', 'm8')]):
    b3 += chip(560, i * 70, w, m, voll=(w == 'Budget'), breite=340, h=58, size=27)
b3 += figur('monteur', B3, [k(-9, x=-130, b=1), k('m1-1.4', x=455, gehen=True, d=2.1),
                            k('m1+0.8', pose='haende', zV=[520, hy3], d=.4, osz=[osz('zyV', 6, 2.6, dauer=1.2, ab=.35)]),
                            k('m2', b=-1, pose='zeigen', zV=[150, 380], d=.5),
                            k('m3', b=1, pose='erklaeren', zV=None, pH='tablet', osz=[osz('aV', 7, 1.3)], d=.5)], s=S3, t='-1')
b3 += figur('kunde', B3, [k(-9, x=640, b=-1),
                          k('m1+0.8', pose='haende', zV=[520, hy3], d=.4, osz=[osz('zyV', 6, 2.6, dauer=1.2, ab=.35)]),
                          k('m2', pose='stehen', zV=None, ko=-6, d=.5),
                          k('m4', ko=4, osz=[osz('ko', 6, 2.2, dauer=1.0)], d=.3), k('m6', osz=[osz('ko', 6, 2.2, dauer=1.0)], d=.3)],
                s=S3, t='0.3', saat=1.3)

# ============ Szene 4: Aufmaß – Laser an drei Stellen, Höhe, kleinstes Maß, Fuge
B4 = 660
oeff = [(346, 300), (578, 300), (564, 500), (358, 500)]
b4 = wand(130, B4, B4) + f"<polygon class='offen' points='{' '.join(f'{x},{y}' for x, y in oeff)}'/>"
def strahl(y, x0, x1, m, wert, txt_y, klein=False):
    aus = " data-aus='m8'"
    return (f"<line class='zeichnen' data-t='{m}+0.35' data-d='0.4'{aus} x1='{x0}' y1='{y}' x2='{x1}' y2='{y}' stroke='{AKZ}' stroke-width='10' stroke-opacity='.25'/>"
            f"<line class='zeichnen leuchten' data-t='{m}+0.35' data-d='0.4'{aus} x1='{x0}' y1='{y}' x2='{x1}' y2='{y}' stroke='#F6E3D2' stroke-width='3'/>"
            + T(594, txt_y, '0 mm', 25, 700, INK, attr=f" data-t='{m}+0.6' data-d='1.0' data-aus='m8' data-zahl='{wert}' data-einheit=' mm'"))
b4 += strahl(314, 388, 577, 'm2', 1012, 323) + strahl(400, 393, 571, 'm3', 1000, 409) + strahl(486, 400, 565, 'm4', 987, 495)
b4 += (f"<line class='zeichnen' data-t='m5+0.45' data-d='0.5' x1='380' y1='452' x2='380' y2='302' data-aus='m8' stroke='{AKZ}' stroke-width='10' stroke-opacity='.25'/>"
       f"<line class='zeichnen leuchten' data-t='m5+0.45' data-d='0.5' x1='380' y1='452' x2='380' y2='302' data-aus='m8' stroke='#F6E3D2' stroke-width='3'/>"
       + T(380, 286, '0 mm', 24, 700, INK, 'middle', attr=" data-t='m5+0.7' data-d='1.0' data-aus='m8' data-zahl='1250' data-einheit=' mm'"))
# schief: Lot-Linien gegen die echten Laibungen
b4 += (f"<g data-t='m6'><line x1='346' y1='286' x2='346' y2='512' stroke='{MUT}' stroke-width='2' stroke-dasharray='8 8'/><line x1='578' y1='286' x2='578' y2='512' stroke='{MUT}' stroke-width='2' stroke-dasharray='8 8'/></g>"
       f"<g data-t='m6+0.3' data-aus='m8'><polygon points='346,300 358,500 346,500' fill='{AKZ}'/><polygon points='578,300 578,500 564,500' fill='{AKZ}'/></g>")
# kleinstes Maß
b4 += (f"<g class='pop' data-t='m7' data-aus='m8'><rect x='584' y='468' width='108' height='38' rx='6' fill='none' stroke='{AKZ}' stroke-width='4'/></g>"
       f"<g class='pop' data-t='m7+0.35' data-aus='m8'><rect x='700' y='459' width='212' height='56' rx='28' fill='{AKZ}'/>" + T(806, 494, 'KLEINSTES ZÄHLT', 20, 800, DUNKEL, 'middle') + '</g>')
# Fuge: Bestellmaß kleiner als Rohbaumaß
b4 += (f"<rect class='zeichnen' data-t='m8+0.2' data-d='0.8' x='374' y='314' width='176' height='172' fill='none' stroke='{INK}' stroke-width='7'/>"
       f"<g data-t='m8+0.9'><path d='M352 400 h18 M362 393 l-8 7 l8 7 M572 400 h-18 M562 393 l8 7 l-8 7' fill='none' stroke='{AKZ}' stroke-width='3'/></g>"
       f"<g class='pop' data-t='m8+0.3' data-d='0.55'><rect x='606' y='150' width='300' height='190' rx='16' fill='url(#verlauf-karte)' stroke='{AKZ}' stroke-opacity='.55' stroke-width='2' filter='url(#schatten)'/>"
       + T(630, 196, 'Rohbaumaß', 22, 600, MUT) + T(882, 196, '987 mm', 24, 800, INK, 'end')
       + T(630, 248, '− Fuge', 27, 800, AKZ) + f"<line x1='630' y1='272' x2='882' y2='272' stroke='{LIN}' stroke-width='3'/>"
       + T(630, 314, '= Bestellmaß', 27, 800, INK) + '</g>')
for i, (w, m) in enumerate([('Größe', 'm10'), ('Material', 'm11'), ('Farbe', 'm12')]):
    b4 += chip((330, 516, 716)[i], 560, w, m, breite=(170, 184, 170)[i], h=60, size=27)
b4 += figur('monteur', B4, [k(-9, x=-130, b=1), k('m1-1.2', x=250, gehen=True, d=1.7),
                            k('m1+0.2', pose='messen', pV='laser', d=.6),
                            k('m2', zV=[350, 314], d=.55), k('m3', zV=[354, 400], d=.5), k('m4', zV=[360, 486], d=.5),
                            k('m5', x=282, pose='knien', zV=[381, 494], pV={'art': 'laser', 'w': 90}, d=.7),
                            k('m6', x=210, pose='stehen', zV=None, pV=None, gehen=True, d=1.0),
                            k('m7', pose='zeigen', zV=[600, 486], d=.5),
                            k('m8', pose='stehen', zV=None, d=.5),
                            k('m9', pose='erklaeren', pH='tablet', osz=[osz('aV', 6, 1.2)], d=.5)], t='-1')

# ============ Szene 5: Angebot – jede Position einzeln, Freigabe, Bestellung beim Hersteller
B5 = 660
doc = (f"<rect x='330' y='10' width='560' height='550' rx='14' fill='{KARTE}' stroke='{INK}' stroke-opacity='.7' stroke-width='3' filter='url(#schatten)'/>"
       + T(362, 74, 'ANGEBOT', 36, 800) + f"<image href='../marke/kimutec-logo.png' x='690' y='34' width='170' height='52'/>"
       f"<line x1='362' y1='104' x2='858' y2='104' stroke='{LIN}' stroke-width='3'/>")
for i, (w, m) in enumerate([('Fenster nach Maß', 'm3'), ('Demontage', 'm4'), ('Montage', 'm4+0.35'), ('Entsorgung', 'm5')]):
    y = 150 + i * 64
    doc += f"<g class='pop' data-t='{m}' data-d='0.4'><circle cx='346' cy='{y-9}' r='7' fill='{AKZ}'/></g>"
    doc += (f"<g data-t='m2+{i*0.2:.1f}' data-d='0.45'>" + T(362, y, w, 29, 600) + f"<rect x='730' y='{y-17}' width='128' height='16' rx='8' fill='{LIN}'/>"
            f"<line x1='362' y1='{y+22}' x2='858' y2='{y+22}' stroke='#262A29' stroke-width='2'/></g>")
doc += (f"<g class='pop' data-t='m6' data-d='0.5'><rect x='350' y='402' width='520' height='62' rx='10' fill='url(#verlauf-akzent)'/>"
        + T(388, 442, 'OHNE VERSTECKTE KOSTEN', 25, 800, DUNKEL) + haken(828, 433, 19, DUNKEL, AKZ) + '</g>'
        f"<line x1='362' y1='520' x2='600' y2='520' stroke='{MUT}' stroke-width='2'/>" + T(362, 546, 'Freigabe Kunde', 19, 600, MUT)
        + f"<path class='zeichnen' data-t='m7+0.3' data-d='1.0' d='M372 512 C 392 470 412 470 418 506 S 452 486 470 500 S 500 520 520 486 C 530 474 548 512 586 500' fill='none' stroke='{AKZ}' stroke-width='5' stroke-linecap='round'/>"
        f"<g class='pop' data-t='m7+0.9' data-d='0.45'><g transform='rotate(-12 760 512)'><rect x='652' y='484' width='216' height='58' rx='8' fill='none' stroke='{AKZ}' stroke-width='5'/>"
        + T(760, 524, 'FREIGEGEBEN', 27, 800, AKZ, 'middle') + '</g></g>')
b5 = spur(doc, [k(-9, x=0, y=0, s=1), k('m8', s=1), k('m8+0.9', x=-66, y=0, s=.6, e='s')], id='s5-doc', ursprung='330px 10px', t='m1')
b5 += (f"<path class='zeichnen' data-t='m8+0.8' data-d='0.6' d='M620 180 L700 180' fill='none' stroke='{AKZ}' stroke-width='5' marker-end='url(#pfeil)'/>"
       f"<g class='pop' data-t='m8+1.2'><path d='M716 330 L716 190 L766 222 L766 190 L816 222 L816 190 L866 222 L866 330 Z' fill='{KARTE}' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
       f"<rect x='880' y='130' width='26' height='200' fill='{KARTE}' stroke='{INK}' stroke-width='4'/>" + T(805, 372, 'Hersteller', 26, 700, MUT, 'middle') + '</g>')
b5 += figur('kunde', B5, [k(-9, x=-130, b=1, pose='stehen', pH='klemmbrett'), k(0.3, x=170, gehen=True, d=1.6), k(2.0, ko=10, d=.5),
                          k('m2', osz=[osz('ko', 5, 2.0, dauer=1.0)], d=.3), k('m6', osz=[osz('ko', 6, 2.2, dauer=1.2)], d=.3),
                          k('m7', pose='schreiben', pV='stift', osz=[osz('eV', 6, 3.6, dauer=1.4), osz('aV', 3, 2.7, dauer=1.4)], d=.45),
                          k('m8', pose='daumen', pV='daumen', d=.5)], t='0.3')

# ============ Szene 6: Produktion beim Hersteller – Rahmen, Glas, Beschläge
B6 = 640
b6 = (f"<g data-t='0.2' data-drehen='60'>{zahnrad(150, 106, 60, 82, 10)}</g><g data-t='0.2' data-drehen='-96'>{zahnrad(282, 56, 36, 52, 8)}</g>"
      f"<g class='pop' data-t='m2'><rect x='640' y='10' width='266' height='128' rx='14' fill='url(#verlauf-karte)' stroke='{INK}' stroke-opacity='.7' stroke-width='3'/>"
      + T(773, 70, 'NACH MASS', 32, 800, INK, 'middle') + T(773, 108, 'millimetergenau', 22, 600, MUT, 'middle') + '</g>'
      f"<line x1='300' y1='478' x2='800' y2='478' stroke='{INK}' stroke-width='10' stroke-linecap='round'/>"
      f"<line x1='336' y1='484' x2='336' y2='{B6}' stroke='{MUT}' stroke-width='8'/><line x1='764' y1='484' x2='764' y2='{B6}' stroke='{MUT}' stroke-width='8'/>"
      f"<line x1='0' y1='{B6}' x2='920' y2='{B6}' stroke='{INK}' stroke-width='4'/>")
b6 += (f"<g class='pop' data-t='m2+0.2' data-d='0.55' data-ursprung='center bottom'><path d='M400 194 h240 v278 h-240z M424 218 v230 h192 v-230z' fill='#F2EFE8' fill-rule='evenodd'/></g>"
       f"<rect class='zeichnen leuchten' data-t='m3' data-d='0.8' data-aus='m4' x='392' y='186' width='256' height='294' fill='none' stroke='{AKZ}' stroke-width='5'/>")
b6 += spur(f"<rect x='426' y='220' width='188' height='226' fill='{GLAS}'/><line x1='456' y1='300' x2='530' y2='238' stroke='#3A4246' stroke-width='4'/><line x1='476' y1='330' x2='560' y2='258' stroke='#3A4246' stroke-width='2'/>",
           [k(-9, y=-150, o=0), k('m4', y=-150, o=0), k('m4+0.3', o=1), k('m4+1.5', y=0, e='s')], id='s6-glas')
b6 += f"<g class='pop' data-t='m5+0.55'><rect x='620' y='312' width='12' height='52' rx='4' fill='#2A2D2C' stroke='{INK}' stroke-width='2'/><rect x='616' y='306' width='20' height='16' rx='4' fill='{INK}'/></g>"
for i, (w, m) in enumerate([('Rahmen', 'm3'), ('Glas', 'm4'), ('Beschläge', 'm5')]):
    b6 += chip(20, 250 + i * 80, w, m, breite=230, h=60, size=27)
b6 += (f"<g class='pop' data-t='m6+0.2' data-d='0.55'><rect x='640' y='156' width='266' height='170' rx='14' fill='url(#verlauf-karte)' stroke='{AKZ}' stroke-opacity='.6' stroke-width='2' filter='url(#schatten)'/>"
       f"<path d='M640 170 a14 14 0 0 1 14 -14 h238 a14 14 0 0 1 14 14 v28 h-266z' fill='{AKZ}'/>" + T(773, 190, 'LIEFERTERMIN', 21, 800, DUNKEL, 'middle', 2)
       + ''.join(f"<rect x='{662 + c*44}' y='{214 + r*32}' width='30' height='20' rx='4' fill='{LIN}'/>" for r in range(3) for c in range(4) if (r, c) != (1, 3))
       + haken(806, 256, 21) + '</g>')
b6 += figur('arbeiter', B6, [k(-9, x=1010, b=-1), k(0.2, x=760, gehen=True, d=1.5),
                             k('m2+0.5', zV=[640, 300], zH=[640, 420], pose='tragen', d=.6),
                             k('m4', zV=an('s6-glas', 614, 300), zH=an('s6-glas', 614, 400), d=.5),
                             k('m4+1.7', zV=None, zH=None, pose='stehen', d=.5),
                             k('m5', pose='bohren', zV=[694, 352], pV='bohrer', osz=[osz('aV', 1.6, 9, dauer=1.0, ab=.45)], d=.45),
                             k('m6', pose='daumen', zV=None, pV='daumen', d=.5)], t='0.2')

# ============ Szene 7: Lieferung – Lkw kommt, zwei Monteure tragen das Fenster zum Haus
B7, S7 = 600, 0.95
lkw = (f"<rect x='40' y='360' width='360' height='200' rx='8' fill='{KARTE}' stroke='{INK}' stroke-width='4'/>"
       f"<image href='../marke/kimutec-logo.png' x='66' y='418' width='308' height='92'/>"
       f"<path d='M400 560 L400 420 L490 420 L540 482 L540 560 Z' fill='{KARTE}' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/><rect x='418' y='436' width='60' height='40' fill='{GLAS}'/>")
for x in (110, 300, 470):
    lkw += spur(f"<circle cx='{x}' cy='568' r='32' fill='{DUNKEL}' stroke='{INK}' stroke-width='5'/><line x1='{x-30}' y1='568' x2='{x+30}' y2='568' stroke='{MUT}' stroke-width='4'/>",
                [k(-9, r=0), k('m1-0.3', r=0), k('m1+1.9', r=720, e='a')], ursprung=f'{x}px 568px')
lkw += spur(''.join(f"<line x1='{-30 - i*30}' y1='{400+i*50}' x2='{20 - i*30}' y2='{400+i*50}' stroke='{AKZ}' stroke-width='4' stroke-linecap='round'/>" for i in range(3)),
            [k(-9, o=0), k('m1-0.3', o=1), k('m1+1.5', o=1), k('m1+1.9', o=0)])
b7 = (f"<line x1='0' y1='{B7}' x2='920' y2='{B7}' stroke='{INK}' stroke-width='4'/>" + ''.join(f"<line x1='{x}' y1='632' x2='{x+60}' y2='632' stroke='{LIN}' stroke-width='6'/>" for x in range(0, 920, 120))
      + f"<path class='zeichnen' data-t='0.2' data-d='1.0' d='M690 412 L795 320 L900 412 M705 400 L705 {B7} L885 {B7} L885 400' fill='none' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/>"
      f"<rect data-t='0.6' x='770' y='510' width='52' height='90' fill='none' stroke='{AKZ}' stroke-width='4'/>")
b7 += spur(lkw, [k(-9, x=-900), k('m1-0.3', x=-900), k('m1+1.9', x=0, e='a')], id='s7-lkw')
b7 += (f"<g class='pop' data-t='m2'><rect x='420' y='190' width='250' height='64' rx='32' fill='url(#verlauf-akzent)'/>"
       f"<circle cx='456' cy='222' r='17' fill='none' stroke='{DUNKEL}' stroke-width='4'/><path d='M456 212 v11 l8 5' fill='none' stroke='{DUNKEL}' stroke-width='4' stroke-linecap='round'/>"
       + T(560, 233, 'PÜNKTLICH', 26, 800, DUNKEL, 'middle') + '</g>')
FY7 = 312
b7 += spur(fenster(330, FY7, 150, 176), [k(-9, x=0, o=0), k('m3', o=0), k('m3+0.4', o=1), k('m3+0.6', x=0), k('m3+2.6', x=210, e='w')], id='s7-fenster')
hgy = FY7 + 96
b7 += figur('monteur', B7, [k(-9, x=262, b=1, pose='tragen', zV=an('s7-fenster', 332, hgy), zH=an('s7-fenster', 332, hgy + 40)),
                            k('m3+0.6', x=472, gehen=True, d=2.0)], s=S7, t='m3', d=.4)
b7 += figur('monteur', B7, [k(-9, x=548, b=-1, pose='tragen', zV=an('s7-fenster', 478, hgy), zH=an('s7-fenster', 478, hgy + 40)),
                            k('m3+0.6', x=758, gehen=True, d=2.0)], s=S7, t='m3', d=.4, saat=2.6)

# ============ Szene 8: Montage – altes Fenster raus, neues rein, ausrichten, befestigen
B8 = 640
b8 = wand(90, B8, B8) + "<rect class='offen' x='340' y='230' width='240' height='250'/>"
b8 += spur(fenster(340, 230, 240, 250, alt=True), [k(-9, s=1, o=1), k('m2+0.4', s=1, y=0), k('m2+0.8', y=-8), k('m2+1.8', s=1.24, o=0, e='e')], id='s8-alt')
b8 += spur(fenster(340, 230, 240, 250), [k(-9, s=1.22, o=0), k('m3', s=1.22, o=0), k('m3+0.25', s=1.2, o=1), k('m3+1.3', s=1, e='s')], id='s8-neu')
waage = (f"<rect x='382' y='436' width='156' height='22' rx='5' fill='{INK}'/><rect x='443' y='439' width='34' height='16' rx='8' fill='{GLAS}'/>"
         + spur(f"<circle cx='466' cy='447' r='5.5' fill='#CFE7A0'/>", [k(-9, x=8), k('m4+0.5', x=8), k('m4+1.4', x=-6, e='w')]))
b8 += spur(waage, [k(-9, y=-24, o=0), k('m4', y=-24, o=0), k('m4+0.4', y=0, o=1, e='a'), k('m5-0.2', o=1), k('m5+0.2', o=0)], id='s8-waage')
lot = (f"<rect x='559' y='268' width='20' height='176' rx='5' fill='{INK}'/><rect x='561' y='339' width='16' height='34' rx='8' fill='{GLAS}'/>"
       + spur(f"<circle cx='569' cy='363' r='5.5' fill='#CFE7A0'/>", [k(-9, y=-8), k('m4+0.9', y=-8), k('m4+1.8', y=-7.5 + 9, e='w')]))
b8 += spur(lot, [k(-9, x=30, o=0), k('m4+0.4', x=30, o=0), k('m4+0.8', x=0, o=1, e='a'), k('m5-0.2', o=1), k('m5+0.2', o=0)], id='s8-lot')
b8 += chip(20, 120, 'Waagerecht', 'm4+1.5', breite=230, h=58, size=26) + chip(670, 120, 'Lot', 'm4+1.9', breite=230, h=58, size=26)
for i, (x, y) in enumerate([(352, 300), (352, 438), (568, 300), (568, 438)]):
    b8 += schraube(x, y, f'm5+{0.75 + (i % 2) * 0.95:.2f}')
b8 += figur('monteur', B8, [k(-9, x=300, b=1),
                            k('m2', pose='tragen', zV=an('s8-alt', 343, 340), zH=an('s8-alt', 343, 420), d=.4),
                            k('m2+1.5', pose='stehen', zV=None, zH=None, d=.45),
                            k('m3', pose='tragen', zV=an('s8-neu', 343, 340), zH=an('s8-neu', 343, 420), d=.3),
                            k('m3+1.5', pose='stehen', zV=None, zH=None, d=.4),
                            k('m4', zV=an('s8-waage', 394, 447), d=.5),
                            k('m5-0.1', pose='bohren', zV=[286, 320], pV='bohrer', osz=[osz('aV', 1.5, 9, dauer=.6, ab=.35)], d=.4),
                            k('m5+1.05', zV=[286, 458], osz=[osz('aV', 1.5, 9, dauer=.6, ab=.35)], d=.4),
                            k('m5+2.1', pose='daumen', zV=None, pV='daumen', d=.5)], t='0.1')
b8 += figur('monteur', B8, [k(-9, x=630, b=-1),
                            k('m2', pose='tragen', zV=an('s8-alt', 577, 340), zH=an('s8-alt', 577, 420), d=.4),
                            k('m2+1.5', pose='stehen', zV=None, zH=None, d=.45),
                            k('m3', pose='tragen', zV=an('s8-neu', 577, 340), zH=an('s8-neu', 577, 420), d=.3),
                            k('m3+1.5', pose='stehen', zV=None, zH=None, d=.4),
                            k('m4+0.4', zV=an('s8-lot', 569, 372), d=.5),
                            k('m5-0.1', pose='bohren', zV=[634, 320], pV='bohrer', osz=[osz('aV', 1.5, 9, dauer=.6, ab=.35)], d=.4),
                            k('m5+1.05', zV=[634, 458], osz=[osz('aV', 1.5, 9, dauer=.6, ab=.35)], d=.4),
                            k('m5+2.1', pose='stehen', zV=None, pV=None, d=.5)], t='0.1', saat=2.9)

# ============ Szene 9: Abdichtung in drei Ebenen (Schnitt durch die Fuge, außen oben)
b9 = (chip(150, 0, 'INNEN DICHTER ALS AUSSEN', 'm2', voll=True, breite=620, h=60, size=26)
      + T(40, 104, 'AUSSEN', 22, 800, BLAU, ls=3) + f"<path d='M172 100 v-26 M162 84 l10 -10 l10 10' fill='none' stroke='{BLAU}' stroke-width='3'/>"
      + T(40, 640, 'INNEN', 22, 800, AKZ, ls=3) + f"<path d='M152 616 v26 M142 632 l10 10 l10 -10' fill='none' stroke='{AKZ}' stroke-width='3'/>"
      + f"<rect class='wand' x='40' y='130' width='260' height='460'/>" + T(170, 366, 'Mauerwerk', 22, 600, MUT, 'middle')
      + f"<rect x='300' y='160' width='70' height='400' fill='#0B0C0C'/>"
      + T(335, 146, 'FUGE', 20, 800, AKZ, 'middle', 3, attr=" data-t='m1'")
      + f"<rect class='zeichnen' data-t='m1' data-d='0.8' x='296' y='156' width='78' height='408' fill='none' stroke='{AKZ}' stroke-width='3' stroke-dasharray='10 8'/>")
b9 += spur(f"<rect x='370' y='160' width='190' height='400' rx='6' fill='#F2EFE8'/>"
      + ''.join(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='3' fill='#DAD5CC' stroke='#B9B4AB' stroke-width='2'/>" for x, y, w, h in
                [(386, 180, 70, 110), (468, 180, 76, 110), (386, 302, 158, 96), (386, 410, 70, 130), (468, 410, 76, 130)])
      + T(465, 600, 'Fensterrahmen', 22, 600, MUT, 'middle'), [k(-9, x=220, o=0), k(0.35, x=220, o=0), k(1.3, x=0, o=1, e='a')])
# Ebenen in der Fuge
b9 += spur(f"<rect x='300' y='160' width='70' height='56' fill='#7E95A0'/>" + ''.join(f"<line x1='{300+i*14}' y1='216' x2='{314+i*14}' y2='160' stroke='#5E7380' stroke-width='3'/>" for i in range(5)),
           [k(-9, o=0, s=.6), k('m7', o=0, s=.6), k('m7+0.5', o=1, s=1, e='f')], id='s9-aussen')
b9 += spur(f"<rect class='daemmung' x='300' y='216' width='70' height='290'/>", [k(-9, sy=0), k('m5', sy=0), k('m5+1.0', sy=1, e='s')], ursprung='300px 216px')
b9 += spur(f"<rect x='300' y='506' width='70' height='54' fill='{AKZ}'/><line x1='300' y1='533' x2='370' y2='533' stroke='#B08F74' stroke-width='3' stroke-dasharray='8 6'/>",
           [k(-9, sx=0), k('m3', sx=0), k('m3+0.6', sx=1, e='s')], ursprung='300px 533px')
def karte(y, h, oben, haupt, unter, t_haupt, t_unter, farbe, ziel_y):
    return (f"<g class='pop' data-t='{t_haupt}' data-d='0.5'><rect x='598' y='{y}' width='318' height='{h}' rx='14' fill='url(#verlauf-karte)' stroke='{farbe}' stroke-opacity='.8' stroke-width='2' filter='url(#schatten)'/>"
            + T(620, y + 36, oben, 19, 800, farbe, ls=3) + T(620, y + 76, haupt, 28, 800) + '</g>'
            + T(620, y + 112, unter, 21, 600, MUT, attr=f" data-t='{t_unter}'")
            + f"<path class='zeichnen' data-t='{t_haupt}+0.2' data-d='0.5' d='M596 {y + h/2:.0f} L{380} {ziel_y}' fill='none' stroke='{farbe}' stroke-width='2' stroke-dasharray='6 6'/>")
b9 += karte(120, 132, 'AUSSEN', 'schlagregendicht', 'aber offen für Dampf', 'm7', 'm8', BLAU, 188)
b9 += karte(290, 132, 'MITTE', 'gedämmt', 'Wärme- & Schallschutz', 'm5', 'm6', MUT, 360)
b9 += karte(460, 132, 'INNEN', 'luftdicht', 'keine feuchte Raumluft', 'm3', 'm4', AKZ, 533)
# feuchte Raumluft steigt auf und wird an der inneren Ebene gestoppt
for i, x in enumerate((312, 335, 358)):
    b9 += spur(f"<path d='M{x} 680 q8 -10 0 -20 q-8 -10 0 -20 q8 -10 0 -20' fill='none' stroke='{BLAU}' stroke-width='4' stroke-linecap='round'/>",
               [k(-9, y=40, o=0), k(f'm4+{i*0.15:.2f}', y=40, o=0), k(f'm4+{0.3+i*0.15:.2f}', o=.9), k(f'm4+{1.1+i*0.15:.2f}', y=-50, o=.9, e='a'), k(f'm4+{2.2+i*0.15:.2f}', o=0)])
b9 += f"<g class='pop' data-t='m4+1.1'><path d='M318 572 l34 0' stroke='#E0533F' stroke-width='6' stroke-linecap='round'/></g>"
# Wärme von innen und Lärm von außen bleiben in der Mitte hängen
b9 += spur(f"<path d='M335 660 q14 -16 0 -32 q-14 -16 0 -32' fill='none' stroke='#E59866' stroke-width='5' stroke-linecap='round'/>",
           [k(-9, y=0, o=0), k('m6', o=0), k('m6+0.3', o=1), k('m6+1.4', y=-120, o=0, e='a')])
for i in range(3):
    b9 += spur(f"<path d='M{300-i*0} {90+i*14} q35 -24 70 0' fill='none' stroke='{MUT}' stroke-width='4' stroke-linecap='round'/>",
               [k(-9, y=-40, o=0), k(f'm6+{0.2+i*0.2:.1f}', y=-40, o=0), k(f'm6+{0.4+i*0.2:.1f}', o=.9), k(f'm6+{1.4+i*0.2:.1f}', y=70, o=0, e='a')])
# Schlagregen prallt ab
for i in range(6):
    x0 = 180 + i * 28
    b9 += spur(f"<line x1='{x0}' y1='40' x2='{x0+14}' y2='62' stroke='{BLAU}' stroke-width='4' stroke-linecap='round'/>",
               [k(-9, x=0, y=0, o=0), k(f'm7+{0.2+i*0.12:.2f}', o=0), k(f'm7+{0.3+i*0.12:.2f}', o=1), k(f'm7+{0.9+i*0.12:.2f}', x=120 - i * 10, y=90, o=1, e='e'), k(f'm7+{1.2+i*0.12:.2f}', x=90 - i * 12, y=70, o=0)])
# Dampf kann nach außen entweichen
for i in range(4):
    b9 += spur(f"<circle cx='{318 + i*12}' cy='300' r='{5 + i % 2 * 2}' fill='none' stroke='{INK}' stroke-width='3' stroke-dasharray='3 4'/>",
               [k(-9, y=0, o=0), k(f'm8+{i*0.25:.2f}', o=0), k(f'm8+{0.2+i*0.25:.2f}', o=.9), k(f'm8+{2.4+i*0.25:.2f}', y=-250, o=0, e='w')])

# ============ Szene 10: Abnahme – öffnen, kippen, schließen, Protokoll, Handschlag
B10 = 660
fl = (f"<rect x='352' y='252' width='196' height='216' fill='#F2EFE8'/><rect x='372' y='272' width='156' height='176' fill='{GLAS}'/>"
      f"<line x1='392' y1='350' x2='450' y2='292' stroke='#3A4246' stroke-width='3'/>"
      + spur(f"<rect x='530' y='346' width='12' height='18' rx='4' fill='#2A2D2C'/><rect x='532' y='352' width='8' height='46' rx='4' fill='#2A2D2C'/>",
             [k(-9, r=0), k('m3-0.3', r=0), k('m3', r=90, e='a'), k('m3+0.8', r=90), k('m4-0.2', r=180, e='w'), k('m5-0.1', r=180), k('m5+0.2', r=0, e='w')],
             ursprung='536px 356px'))
b10 = (wand(120, B10, B10) + "<rect class='offen' x='330' y='230' width='240' height='260'/>"
       f"<path d='M330 230 h240 v260 h-240z M352 252 v216 h196 v-216z' fill='#F2EFE8' fill-rule='evenodd'/>")
b10 += spur(fl, [k(-9, sx=1, sy=1), k('m3', sx=1), k('m3+0.5', sx=.8, e='w'), k('m4-0.3', sx=1, e='w'), k('m4', sy=1), k('m4+0.35', sy=.93, e='w'), k('m5', sy=.93), k('m5+0.35', sy=1, e='w')],
            id='s10-fluegel', ursprung='352px 468px')
b10 += (f"<g class='pop' data-t='m3+0.2' data-aus='m6'><path d='M590 300 a70 70 0 0 1 0 110' fill='none' stroke='{AKZ}' stroke-width='4' marker-end='url(#pfeil)'/></g>"
        + T(600, 446, 'öffnen', 24, 700, AKZ, attr=" data-t='m3+0.2' data-aus='m4'")
        + T(600, 446, 'kippen', 24, 700, AKZ, attr=" data-t='m4+0.2' data-aus='m5'")
        + T(600, 446, 'schließen', 24, 700, AKZ, attr=" data-t='m5+0.2' data-aus='m6'"))
b10 += funkeln(318, 220, 18, 'm7') + funkeln(588, 504, 14, 'm7+0.2') + funkeln(300, 470, 12, 'm7+0.4') + chip(640, 150, 'Sauber', 'm7+0.3', breite=200, h=56, size=25)
b10 += (f"<g class='pop' data-t='m8' data-d='0.55'><rect x='20' y='0' width='290' height='214' rx='14' fill='{INK}' filter='url(#schatten)'/>"
        + T(44, 44, 'PROTOKOLL', 22, 800, DUNKEL, ls=3)
        + ''.join(haken(56, 80 + i * 40, 13, AKZ, DUNKEL) + T(80, 89 + i * 40, w, 22, 700, DUNKEL) for i, w in enumerate(['Funktion', 'Anschlüsse', 'Bedienung']))
        + f"<line x1='44' y1='196' x2='286' y2='196' stroke='#A7A29A' stroke-width='2'/></g>"
        f"<path class='zeichnen' data-t='m8+0.5' data-d='1.0' d='M52 190 C 70 160 84 162 88 186 S 112 172 124 182 S 146 196 160 170 C 168 160 182 190 214 182' fill='none' stroke='#B08F74' stroke-width='4' stroke-linecap='round'/>")
hy10 = hand_y(B10)
b10 += figur('monteur', B10, [k(-9, x=600, b=-1),
                              k('m2', pose='erklaeren', zV=an('s10-fluegel', 536, 376), d=.5),
                              k('m6', pose='erklaeren', zV=None, osz=[osz('aV', 7, 1.3, dauer=2.0)], d=.45),
                              k('m8+1.6', x=520, pose='stehen', gehen=True, d=.9),
                              k('m8+2.6', pose='haende', zV=[460, hy10], d=.4, osz=[osz('zyV', 6, 2.6, dauer=1.2, ab=.35)])], t='0.1')
b10 += figur('kunde', B10, [k(-9, x=210, b=1),
                            k('m4', osz=[osz('ko', 6, 2.2, dauer=1.0)], d=.3), k('m6+0.4', osz=[osz('ko', 6, 2.2, dauer=1.0)], d=.3),
                            k('m8+0.1', pose='schreiben', pH='klemmbrett', pV='stift', osz=[osz('eV', 6, 3.6, dauer=1.3), osz('aV', 3, 2.7, dauer=1.3)], d=.4),
                            k('m8+1.6', x=400, pose='stehen', pV=None, pH=None, gehen=True, d=.9),
                            k('m8+2.6', pose='haende', zV=[460, hy10], d=.4, osz=[osz('zyV', 6, 2.6, dauer=1.2, ab=.35)])], t='0.2', saat=1.9)

# ============ Szene 11: Ergebnis – Bewertung, warm, leise, zufrieden
B11, S11 = 690, 0.95
b11 = (f"<g class='pop' data-t='0.4' data-d='0.6'><rect x='30' y='0' width='360' height='290' rx='26' fill='url(#verlauf-karte)' stroke='{AKZ}' stroke-opacity='.5' stroke-width='2' filter='url(#schatten)'/>"
       + T(210, 160, '5,0', 120, 800, AKZ, 'middle') + T(210, 262, 'KUNDENBEWERTUNG', 22, 600, MUT, 'middle', 4) + '</g>'
       + ''.join(f"<g class='pop' data-t='{1.0 + i*0.12:.2f}'>{stern(90 + i*60, 206, 22)}</g>" for i in range(5)))
b11 += chip(430, 20, 'WARM', 'm1', voll=True, breite=460) + chip(430, 114, 'LEISE', 'm2', voll=True, breite=460) + chip(430, 208, 'ZUFRIEDEN', 'm3', voll=True, breite=460)
b11 += (f"<defs><clipPath id='s11-glas'><rect x='584' y='394' width='212' height='232'/></clipPath><radialGradient id='s11-warm'><stop offset='0' stop-color='{AKZ}' stop-opacity='.34'/><stop offset='1' stop-color='{AKZ}' stop-opacity='0'/></radialGradient></defs>"
        f"<circle data-t='m1' data-d='1.2' cx='330' cy='560' r='260' fill='url(#s11-warm)'/>"
        f"<rect x='560' y='370' width='260' height='280' rx='4' fill='#F2EFE8'/><rect x='584' y='394' width='212' height='232' fill='{GLAS}'/>"
        f"<g clip-path='url(#s11-glas)'><g data-t='0' data-fallen='-24,80,0.55'>"
        + ''.join(f"<line x1='{x}' y1='{y}' x2='{x-8}' y2='{y+22}' stroke='{BLAU}' stroke-width='3' stroke-opacity='.55' stroke-linecap='round'/>"
                  for x in range(600, 840, 34) for y in range(300, 660, 80)) + '</g></g>'
        f"<line x1='560' y1='650' x2='820' y2='650' stroke='{INK}' stroke-width='6'/>")
for i in range(3):
    b11 += f"<g data-t='m2' data-fallen='-46,0,{1.2:.1f}'><path d='M{880 + i*26} 470 q-18 40 0 80' fill='none' stroke='{MUT}' stroke-width='4' stroke-linecap='round' opacity='{.8 - i*.22:.2f}'/></g>"
b11 += (f"<path d='M244 {B11} L244 560 Q244 520 284 520 L300 520 Q318 520 318 560 L318 596 L420 596 Q440 596 440 616 L440 {B11}' fill='{KARTE}' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
        f"<line x1='0' y1='{B11}' x2='920' y2='{B11}' stroke='{INK}' stroke-width='4'/>")
b11 += figur('kunde', B11, [k(-9, x=330, b=1, pose='sitzen', pV='tasse', ru=-10, aV=34, eV=86),
                            k('m3', osz=[osz('ko', 5, 2.0, dauer=1.0)], d=.3),
                            k('m4', aV=44, eV=112, ko=-8, d=.8), k('m4+1.4', aV=34, eV=86, ko=-4, d=.8)], s=S11, t='0.2')
b11 += blase(40, 320, 520, ['„Warum haben wir das', 'nicht früher gemacht?“'], 'm5', spitze=330)
b11 += konfetti(210, 150, 'm3')

TEXT = {
 1: "Neue Fenster? |Bei KIMUTEC bekommen Sie alles aus einer Hand. |In acht Schritten, |vom ersten Kontakt |bis zur fertigen Abnahme.",
 2: "Schritt eins: |Sie melden sich, |per Nachricht, |E-Mail |oder Telefon. |Wir antworten schnell |und vereinbaren einen Termin bei Ihnen vor Ort.",
 3: "Schritt zwei: |die kostenlose Beratung vor Ort. |Wir sehen uns Ihre Fenster und das Mauerwerk genau an |und klären, was Ihnen wichtig ist: |Wärmeschutz, |Schallschutz, |Sicherheit |und Design, |passend zu Ihrem Budget.",
 4: "Schritt drei: das Aufmaß. |Wir messen selbst, mit dem Laser: |die Breite oben, |in der Mitte |und unten, |dann die Höhe. |Mauerwerk ist selten ganz gerade, |deshalb zählt das kleinste Maß. |Davon ziehen wir die Fuge für Dämmung und Abdichtung ab. |Wie breit sie sein muss, hängt von |Größe, |Material |und Farbe des Fensters ab.",
 5: "Schritt vier: |Sie bekommen ein klares Angebot. |Jede Position steht einzeln drin, |von den Fenstern |bis zu Montage |und Entsorgung, |ohne versteckte Kosten. |Sie geben frei, |und wir bestellen direkt beim Hersteller.",
 6: "Schritt fünf: |die Produktion. |Ihre Fenster werden genau nach Ihren Maßen gefertigt: |Rahmen, |Glas |und Beschläge. |Den Liefertermin behalten wir für Sie im Blick.",
 7: "Schritt sechs: |die Lieferung. |Pünktlich zum vereinbarten Termin |bringen wir Ihre Fenster direkt zu Ihnen nach Hause.",
 8: "Schritt sieben: |die Montage. |Zuerst bauen wir das alte Fenster aus. |Dann setzen wir das neue ein, |richten es lot- und waagerecht aus |und befestigen es sicher im Mauerwerk.",
 9: "Dann kommt das Wichtigste: |die Abdichtung. |Hier gilt: innen dichter als außen. |Innen luftdicht, |damit keine feuchte Raumluft in die Fuge zieht. |In der Mitte gedämmt, |gegen Wärmeverlust und Lärm. |Außen dicht gegen Schlagregen, |aber offen für Dampf, |damit Feuchtigkeit entweichen kann.",
 10: "Schritt acht: |die Abnahme. |Wir prüfen jedes Fenster gemeinsam mit Ihnen: |öffnen, |kippen, |schließen. |Wir zeigen Ihnen die Bedienung, |räumen sauber auf |und übergeben alles mit Protokoll.",
 11: "Und am Ende? |Schön warm. |Schön leise. |Zufrieden. |Und oft dieselbe Frage: |Warum haben wir das nicht früher gemacht?",
 12: "KIMUTEC: alles aus einer Hand. Jetzt kostenlose Beratung vereinbaren, direkt hier per Nachricht oder über kimutec.com.",
}

db = {
    "titel": "KIMUTEC – So arbeiten wir: vom Kontakt bis zur Abnahme",
    "fps": 30,
    "stimme": "elevenlabs", "tonOrdner": "ton",
    "elevenlabs": {"voice_id": "5KvpaGteYkNayiswuX2h", "model_id": "eleven_multilingual_v2",
                   "voice_settings": {"stability": 0.6, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True, "speed": 1.0}},
    "aussprache": {"kimutec.com": "Kimutek Punkt com", "KIMUTEC": "Kimutek"},
    "szenen": [
        {"label": "KIMUTEC | So arbeiten wir", "titel": "Neue Fenster?\nAlles aus\n<em>einer Hand.</em>", "bildHoehe": 600, "bild": b1, "sprecher": TEXT[1], "pause": 1.0},
        {"label": "01 | Kontakt", "titel": "Sie melden\nsich.", "schritt": 1, "bildHoehe": 640, "bild": b2, "sprecher": TEXT[2], "pause": 1.0},
        {"label": "02 | Beratung", "titel": "Beratung\nbei Ihnen\nzu Hause.", "schritt": 2, "bildHoehe": 640, "bild": b3, "sprecher": TEXT[3], "pause": 0.9},
        {"label": "03 | Aufmaß", "titel": "Wir messen\nselbst.", "schritt": 3, "bildHoehe": 680, "bild": b4, "sprecher": TEXT[4], "pause": 1.0},
        {"label": "04 | Angebot & Bestellung", "titel": "Klares\nAngebot.", "schritt": 4, "bildHoehe": 680, "bild": b5, "sprecher": TEXT[5], "pause": 1.7},
        {"label": "05 | Produktion", "titel": "Ihre Fenster\nentstehen.", "schritt": 5, "bildHoehe": 660, "bild": b6, "sprecher": TEXT[6], "pause": 1.0},
        {"label": "06 | Lieferung", "titel": "Pünktlich\ngeliefert.", "schritt": 6, "bildHoehe": 650, "bild": b7, "sprecher": TEXT[7], "pause": 2.2},
        {"label": "07 | Montage", "titel": "Montage\nnach Plan.", "schritt": 7, "bildHoehe": 660, "bild": b8, "sprecher": TEXT[8], "pause": 1.9},
        {"label": "07 | Montage · Abdichtung", "titel": "Dicht in\n<em>drei Ebenen.</em>", "schritt": 7, "bildHoehe": 700, "bild": b9, "sprecher": TEXT[9], "pause": 1.4},
        {"label": "08 | Abnahme", "titel": "Gemeinsame\nAbnahme.", "schritt": 8, "bildHoehe": 680, "bild": b10, "sprecher": TEXT[10], "pause": 3.3},
        {"label": "Das Ergebnis", "titel": "Und am\nEnde?", "bildHoehe": 700, "bild": b11, "sprecher": TEXT[11], "pause": 1.4},
        {"art": "abschluss", "label": "Alles aus einer Hand", "titel": "Jetzt Beratung\nvereinbaren.", "unter": "Kostenlose Erstberatung vor Ort\nin Pforzheim und Umgebung.",
         "kontakt": {"zeilen": [["NACHRICHT", "Direkt hier auf Instagram"], ["E-MAIL", "sales@kimutec.com"], ["WEB", "www.kimutec.com"]]},
         "motto": "QUALITÄT. WERTE. ZUHAUSE.", "sprecher": TEXT[12], "pause": 1.6},
    ]}

# Kontrolle: Sprechertext ohne Marken muss dem freigegebenen Text entsprechen (Ansagen wurden damit erzeugt)
frei = open(os.path.join(HIER, 'sprechertext.txt'), encoding='utf-8').read() if os.path.exists(os.path.join(HIER, 'sprechertext.txt')) else ''
for nr, s in TEXT.items():
    roh = ' '.join(s.replace('|', '').split())
    if frei and roh not in ' '.join(frei.split()):
        print(f'Hinweis: Szene {nr} weicht vom freigegebenen Sprechertext ab')
ziel = os.path.join(HIER, 'drehbuch.json')
json.dump(db, open(ziel, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('geschrieben:', ziel)
