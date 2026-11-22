# Erzeugt drehbuch.json für das Reel „So arbeiten wir“ (Kontakt bis Abnahme).
# Aufruf: python3 reels/projekte/09-ablauf/bauen.py && node reels/render.mjs reels/projekte/09-ablauf/drehbuch.json
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from figuren import mann

INK, AKZ, MUT, LIN, GLAS, GLASR = '#EEEAE2', '#D8B79C', '#A3A09A', '#3A3E3C', '#1F2A30', '#9FB3BC'

def zahnrad(cx, cy, r1, r2, n):
    pts = []
    for k in range(n * 2):
        a0 = math.pi * k / n
        r = r2 if k % 2 == 0 else r1
        for da in (-0.32, 0.32):
            a = a0 + da * math.pi / n
            pts.append(f'{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}')
    return f"<polygon points='{' '.join(pts)}' fill='none' stroke='{INK}' stroke-width='4'/><circle cx='{cx}' cy='{cy}' r='{r1 * .35:.0f}' fill='none' stroke='{AKZ}' stroke-width='4'/>"

def stern(cx, cy, r):
    p = ' '.join(f'{cx + (r if k % 2 == 0 else r * .45) * math.cos(-math.pi / 2 + k * math.pi / 5):.1f},{cy + (r if k % 2 == 0 else r * .45) * math.sin(-math.pi / 2 + k * math.pi / 5):.1f}' for k in range(10))
    return f"<polygon points='{p}' fill='{AKZ}'/>"

def fenster(x, y, w, h, alt=False):
    rahmen = '#8A8F8C' if alt else '#F2EFE8'
    s = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='4' fill='{rahmen}'/><rect x='{x+22}' y='{y+22}' width='{w-44}' height='{h-44}' fill='{GLAS}'/>"
    if alt:
        s += f"<path d='M{x+40} {y+60} l40 30 l-20 40 l50 20' fill='none' stroke='#5A605D' stroke-width='3'/>"
    else:
        s += f"<line x1='{x+50}' y1='{y+h*.35:.0f}' x2='{x+w*.45:.0f}' y2='{y+60}' stroke='#3A4246' stroke-width='3'/><rect x='{x+w-18}' y='{y+h/2-22:.0f}' width='8' height='44' rx='3' fill='#2A2D2C'/>"
    return s

def chip(x, y, text, t, voll=False, breite=None):
    b = breite or 34 + len(text) * 19
    fill, farbe = (AKZ, '#111312') if voll else ('#1A1D1C', INK)
    return (f"<g class='pop' data-t='{t}' data-d='0.5'><rect x='{x}' y='{y}' width='{b}' height='64' rx='32' fill='{fill}' stroke='{AKZ}' stroke-width='2'/>"
            f"<text x='{x + b/2}' y='{y + 42}' text-anchor='middle' style='font-family:Montserrat;font-weight:700;font-size:29px;fill:{farbe}'>{text}</text></g>")

def blase(x, y, w, zeilen, t, kunde=True):
    h = 30 + 42 * len(zeilen)
    fill, farbe = ('#2A2E2D', INK) if kunde else (AKZ, '#111312')
    spitze = f"M{x+30} {y+h} l0 26 l30 -26z" if kunde else f"M{x+w-30} {y+h} l0 26 l-30 -26z"
    txt = ''.join(f"<text x='{x+28}' y='{y+48+42*k}' style='font-family:Montserrat;font-weight:600;font-size:30px;fill:{farbe}'>{z}</text>" for k, z in enumerate(zeilen))
    return f"<g class='pop' data-t='{t}' data-d='0.55' data-ursprung='{'left bottom' if kunde else 'right bottom'}'><rect x='{x}' y='{y}' width='{w}' height='{h}' rx='26' fill='{fill}'/><path d='{spitze}' fill='{fill}'/>{txt}</g>"

# ---------- Szene 1: Der Weg in 8 Schritten
schritte = ['Kontakt', 'Beratung', 'Aufmaß', 'Angebot', 'Produktion', 'Lieferung', 'Montage', 'Abnahme']
pkt = [(60 + k * 114, 430 - k * 44) for k in range(8)]
weg = f"<path class='zeichnen' data-t='m1' data-d='2.4' d='M{' L'.join(f'{x} {y}' for x, y in pkt)}' fill='none' stroke='{AKZ}' stroke-width='5'/>"
punkte = ''
for k, (x, y) in enumerate(pkt):
    ty = y + 66 if (k % 2 == 0 or k == 7) else y - 40
    punkte += (f"<g class='pop' data-t='m1+{k*0.3:.1f}' data-d='0.45'><circle cx='{x}' cy='{y}' r='26' fill='#111312' stroke='{AKZ}' stroke-width='4'/>"
               f"<text x='{x}' y='{y+10}' text-anchor='middle' style='font-family:Montserrat;font-weight:800;font-size:26px;fill:{INK}'>{k+1}</text>"
               f"<text x='{x}' y='{ty}' text-anchor='middle' style='font-family:Montserrat;font-weight:600;font-size:21px;fill:{MUT}'>{schritte[k]}</text></g>")
haken = f"<g class='pop' data-t='m2+0.6'><circle cx='858' cy='40' r='40' fill='{AKZ}'/><path d='M838 40 l14 14 l26 -28' fill='none' stroke='#111312' stroke-width='7' stroke-linecap='round'/></g>"
bild1 = weg + punkte

# ---------- Szene 2: Kontakt
handy = (f"<g data-t='0.5' data-schweben='4'><rect x='30' y='40' width='230' height='440' rx='36' fill='#161918' stroke='{INK}' stroke-width='5'/>"
         f"<rect x='110' y='60' width='70' height='10' rx='5' fill='{LIN}'/><rect x='52' y='92' width='186' height='300' rx='8' fill='#1E2120'/>"
         f"<circle cx='145' cy='440' r='18' fill='none' stroke='{LIN}' stroke-width='3'/></g>"
         f"<g class='pop' data-t='m1'><circle cx='240' cy='60' r='26' fill='{AKZ}'/><text x='240' y='70' text-anchor='middle' style='font-family:Montserrat;font-weight:800;font-size:28px;fill:#111312'>1</text></g>")
bild2 = (handy + blase(300, 30, 600, ['Hallo! Wir brauchen', 'neue Fenster.'], 'm1+0.3')
         + chip(300, 230, 'Nachricht', 'm2') + chip(520, 230, 'E-Mail', 'm2+0.35') + chip(690, 230, 'Telefon', 'm2+0.7')
         + blase(300, 340, 600, ['Gern! Wann passt', 'ein Termin bei Ihnen?'], 'm3', kunde=False))

# ---------- Szene 3: Beratung vor Ort
haus = (f"<g data-t='0.5'><path class='zeichnen' data-t='0.5' data-d='1.2' d='M40 260 L230 100 L420 260 M80 230 L80 520 L380 520 L380 230' fill='none' stroke='{INK}' stroke-width='6' stroke-linejoin='round'/>"
        f"<rect x='120' y='300' width='100' height='120' fill='{GLAS}' stroke='{INK}' stroke-width='4'/><rect x='260' y='380' width='80' height='140' fill='none' stroke='{AKZ}' stroke-width='4'/></g>"
        f"<g class='pop' data-t='m1'><g transform='rotate(-8 300 120)'><rect x='220' y='90' width='190' height='56' rx='8' fill='{AKZ}'/>"
        f"<text x='315' y='128' text-anchor='middle' style='font-family:Montserrat;font-weight:800;font-size:26px;fill:#111312'>KOSTENLOS</text></g></g>")
bild3 = haus + chip(500, 150, 'Wärme', 'm3', breite=330) + chip(500, 240, 'Sicherheit', 'm4', breite=330) + chip(500, 330, 'Design', 'm5', breite=330) + chip(500, 420, 'Budget', 'm6', breite=330, voll=True)

# ---------- Szene 4: Aufmaß mit Laser
def laser(y, m, plus, wert, klein=False):
    farbe = AKZ if klein else INK
    t = f'{m}+{plus:.1f}' if plus else m
    t2 = f'{m}+{plus+0.3:.1f}'
    return (f"<line class='zeichnen' data-t='{t}' data-d='0.5' x1='272' y1='{y}' x2='648' y2='{y}' stroke='{AKZ}' stroke-width='10' stroke-opacity='.25'/>"
            f"<line class='zeichnen' data-t='{t}' data-d='0.5' x1='272' y1='{y}' x2='648' y2='{y}' stroke='{AKZ}' stroke-width='3'/>"
            f"<g data-t='{t2}'><rect x='370' y='{y-52}' width='180' height='40' rx='6' fill='#111312'/>"
            f"<text x='460' y='{y-22}' text-anchor='middle' data-t='{t2}' data-d='1.2' data-zahl='{wert}' data-einheit=' mm' style='font-family:Montserrat;font-weight:700;font-size:28px;fill:{farbe}'>0 mm</text></g>")
bild4 = (f"<rect class='wand' x='0' y='0' width='920' height='520'/><rect class='offen' x='260' y='40' width='400' height='440'/>"
         + laser(90, 'm2', 0.4, 1012) + laser(260, 'm3', 0, 1008) + laser(430, 'm3', 0.6, 960, True)
         + f"<g class='pop' data-t='m4'><rect x='640' y='470' width='260' height='60' rx='30' fill='{AKZ}'/><text x='770' y='510' text-anchor='middle' style='font-family:Montserrat;font-weight:800;font-size:26px;fill:#111312'>KLEINSTES ZÄHLT</text></g>")

# ---------- Szene 5: Angebot und Bestellung
zeilen = ''.join(f"<line class='zeichnen' data-t='m1+{k*0.18:.2f}' data-d='0.35' x1='110' y1='{150+k*46}' x2='{380 if k % 3 else 300}' y2='{150+k*46}' stroke='{MUT}' stroke-width='6' stroke-linecap='round'/>" for k, _ in enumerate(range(6)))
bild5 = (f"<g data-t='0.5'><rect x='80' y='20' width='340' height='500' rx='10' fill='#1A1D1C' stroke='{INK}' stroke-width='4'/>"
         f"<text x='110' y='90' style='font-family:Montserrat;font-weight:800;font-size:32px;fill:{INK}'>ANGEBOT</text></g>" + zeilen
         + f"<g data-t='m2'><line x1='110' y1='450' x2='390' y2='450' stroke='{LIN}' stroke-width='3'/><text x='110' y='494' style='font-family:Montserrat;font-weight:700;font-size:23px;fill:{AKZ}'>Ohne versteckte Kosten</text></g>"
         + f"<g class='pop' data-t='m3' data-d='0.5'><g transform='rotate(-14 260 330)'><rect x='130' y='290' width='260' height='80' rx='10' fill='none' stroke='{AKZ}' stroke-width='6'/>"
           f"<text x='260' y='344' text-anchor='middle' style='font-family:Montserrat;font-weight:800;font-size:34px;fill:{AKZ}'>FREIGEGEBEN</text></g></g>"
         + f"<path class='zeichnen' data-t='m4' data-d='0.7' d='M440 270 C 520 270 540 270 600 270' fill='none' stroke='{AKZ}' stroke-width='5' marker-end='url(#pfeil)'/>"
         + f"<g class='pop' data-t='m4+0.6'><path d='M640 380 L640 230 L700 270 L700 230 L760 270 L760 230 L820 270 L820 380 Z' fill='#1A1D1C' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/>"
           f"<rect x='840' y='170' width='34' height='210' fill='#1A1D1C' stroke='{INK}' stroke-width='4'/><text x='740' y='430' text-anchor='middle' style='font-family:Montserrat;font-weight:700;font-size:26px;fill:{MUT}'>Hersteller</text></g>")

# ---------- Szene 6: Produktion
band = (f"<line x1='40' y1='420' x2='880' y2='420' stroke='{INK}' stroke-width='5'/><line x1='40' y1='470' x2='880' y2='470' stroke='{INK}' stroke-width='5'/>"
        + ''.join(f"<g data-t='0.3' data-drehen='240'><circle cx='{x}' cy='445' r='20' fill='none' stroke='{MUT}' stroke-width='4'/><line x1='{x-20}' y1='445' x2='{x+20}' y2='445' stroke='{MUT}' stroke-width='3'/></g>" for x in range(80, 880, 100)))
rahmen_lauf = ''.join(f"<g data-t='{0.3+k*0.1:.1f}' data-bewegung='620,0,{0.4+k*0.9:.1f},3.2'><g>{fenster(-120 - k*230, 250, 150, 170)}</g></g>" for k in range(3))
bild6 = (f"<g data-t='0.3' data-drehen='70'>{zahnrad(170, 140, 70, 95, 10)}</g><g data-t='0.3' data-drehen='-100'>{zahnrad(320, 90, 42, 60, 8)}</g>"
         f"<g data-t='0.4'><rect x='430' y='40' width='280' height='150' rx='10' fill='#1A1D1C' stroke='{INK}' stroke-width='4'/><text x='570' y='105' text-anchor='middle' style='font-family:Montserrat;font-weight:800;font-size:32px;fill:{INK}'>NACH MASS</text>"
         f"<text x='570' y='150' text-anchor='middle' style='font-family:Montserrat;font-weight:600;font-size:22px;fill:{MUT}'>gefertigt für Ihr Haus</text></g>"
         + band + f"<g style='clip-path:inset(0 0 0 0)'>{rahmen_lauf}</g>"
         + f"<g class='pop' data-t='m2'><rect x='730' y='40' width='170' height='150' rx='10' fill='#111312' stroke='{AKZ}' stroke-width='4'/><rect x='730' y='40' width='170' height='40' rx='10' fill='{AKZ}'/>"
           f"<text x='815' y='150' text-anchor='middle' style='font-family:Montserrat;font-weight:800;font-size:44px;fill:{INK}'>KW 12</text></g>")

# ---------- Szene 7: Lieferung
lkw = (f"<g data-t='0.2' data-bewegung='760,0,m1,2.2'><g>"
       f"<rect x='-640' y='170' width='380' height='200' rx='8' fill='#1A1D1C' stroke='{INK}' stroke-width='4'/>"
       f"<image href='../marke/kimutec-logo.png' x='-610' y='225' width='320' height='97'/>"
       f"<path d='M-260 370 L-260 230 L-170 230 L-120 290 L-120 370 Z' fill='#1A1D1C' stroke='{INK}' stroke-width='4' stroke-linejoin='round'/><rect x='-240' y='248' width='60' height='40' fill='{GLAS}'/>"
       + ''.join(f"<g data-t='0.2' data-drehen='300'><circle cx='{x}' cy='378' r='32' fill='#111312' stroke='{INK}' stroke-width='5'/><line x1='{x-30}' y1='378' x2='{x+30}' y2='378' stroke='{MUT}' stroke-width='4'/></g>" for x in (-560, -360, -180))
       + ''.join(f"<line x1='{-720 - k*30}' y1='{210+k*50}' x2='{-670 - k*30}' y2='{210+k*50}' stroke='{AKZ}' stroke-width='4' stroke-linecap='round'/>" for k in range(3))
       + "</g></g>")
bild7 = (f"<line x1='0' y1='412' x2='920' y2='412' stroke='{INK}' stroke-width='4'/>"
         + ''.join(f"<line x1='{x}' y1='450' x2='{x+60}' y2='450' stroke='{LIN}' stroke-width='6'/>" for x in range(0, 920, 120))
         + f"<g data-t='0.4'><path d='M660 412 L660 260 L770 180 L880 260 L880 412' fill='none' stroke='{INK}' stroke-width='5' stroke-linejoin='round'/><rect x='740' y='300' width='60' height='112' fill='none' stroke='{AKZ}' stroke-width='4'/></g>"
         + lkw
         + f"<g class='pop' data-t='m2'><path d='M770 30 c-40 0 -60 30 -60 60 c0 40 60 90 60 90 c0 0 60 -50 60 -90 c0 -30 -20 -60 -60 -60z' fill='{AKZ}'/><circle cx='770' cy='88' r='20' fill='#111312'/></g>")

# ---------- Szene 8: Montage
bild8 = (f"<rect class='wand' x='0' y='0' width='920' height='520'/><rect class='offen' x='290' y='40' width='340' height='440'/>"
         f"<g data-t='0.1' data-aus='m1+1.1' data-bewegung='-700,0,m1,1.0'><g>{fenster(290, 40, 340, 440, alt=True)}</g></g>"
         f"<g data-t='m2' data-d='0.3' data-bewegung='-700,0,m2,1.0'><g>{fenster(990, 40, 340, 440)}</g></g>"
         f"<g data-t='m3'><rect x='282' y='32' width='356' height='456' fill='none' stroke='{AKZ}' stroke-width='8'/></g>"
         f"<g data-t='m3+1.2'><rect x='272' y='22' width='376' height='476' fill='none' stroke='#6E5A48' stroke-width='10' stroke-dasharray='14 8'/></g>"
         + chip(20, 120, 'innen luftdicht', 'm3+0.4', breite=250) + chip(652, 380, 'außen regendicht', 'm3+1.6', breite=262)
         + ''.join(f"<g class='pop' data-t='m4+{k*0.2:.1f}'>{stern(x, y, r)}</g>" for k, (x, y, r) in enumerate([(250, 60, 22), (680, 120, 16), (210, 470, 18), (700, 300, 24)])))

# ---------- Szene 9: Abnahme
def pruef(text, t):
    return (f"<div data-t='{t}' style='display:flex;align-items:center;gap:28px;border-top:2px solid {LIN};padding:22px 0'>"
            f"<svg width='52' height='52' viewBox='0 0 52 52' class='pop' data-t='{t}+0.2'><circle cx='26' cy='26' r='24' fill='{AKZ}'/><path d='M14 27 l8 8 l17 -18' fill='none' stroke='#111312' stroke-width='5' stroke-linecap='round'/></svg>"
            f"<b style='font-size:38px'>{text}</b></div>")
html9 = (pruef('Funktion geprüft', 'm2') + pruef('Anschlüsse dicht und sauber', 'm3') + pruef('Bedienung erklärt', 'm4') + pruef('Übergabe mit Protokoll', 'm5')
         + f"<svg viewBox='0 0 920 150' style='width:920px;height:150px;margin-top:30px;overflow:visible'><path class='zeichnen' data-t='m5+1' data-d='1.4' d='M60 100 C 100 20 140 20 150 90 S 210 40 240 80 S 300 120 330 60 C 350 30 380 110 420 70 L 520 80' fill='none' stroke='{AKZ}' stroke-width='5' stroke-linecap='round'/>"
           f"<line x1='40' y1='130' x2='560' y2='130' stroke='{LIN}' stroke-width='3' data-t='m5+0.8'/><text x='600' y='110' data-t='m5+0.8' style='font-family:Montserrat;font-weight:600;font-size:24px;fill:{MUT}'>Unterschrift Kunde</text></svg>")

# ---------- Szene 10: Zufrieden (mit Augenzwinkern)
gesicht = (f"<g data-t='0.4'>{fenster(80, 20, 340, 420)}</g>"
           f"<g class='pop' data-t='m4'><circle cx='190' cy='170' r='22' fill='{INK}'/></g>"
           f"<g class='pop' data-t='m4+0.2'><path d='M290 170 q22 -22 44 0' fill='none' stroke='{INK}' stroke-width='8' stroke-linecap='round'/></g>"
           f"<path class='zeichnen' data-t='m4+0.3' data-d='0.6' d='M170 290 Q250 370 330 290' fill='none' stroke='{AKZ}' stroke-width='10' stroke-linecap='round'/>")
woerter = chip(480, 40, 'WARM', 'm1', breite=200, voll=True) + chip(480, 130, 'LEISE', 'm2', breite=200, voll=True) + chip(480, 220, 'ZUFRIEDEN', 'm3', breite=300, voll=True)
sterne = ''.join(f"<g class='pop' data-t='m4+{0.5+k*0.15:.2f}'>{stern(500 + k*76, 345, 30)}</g>" for k in range(5))
bild10 = gesicht + woerter + sterne + blase(60, 470, 840, ['„Warum haben wir das', 'nicht früher gemacht?“'], 'm6')

# ---------- Männchen
LAUF = dict(laufen=True, arm_l=20, arm_r=-20, wipp_l=(25, 1.6, 0.5), wipp_r=(25, 1.6))
bild1 += f"<g data-t='m1' data-bewegung='798,-308,m1,2.6'>{mann(60, 402, 0.42, 'm1', **LAUF)}</g>"
bild3 += (mann(150, 520, 0.72, 'm1', kunde=True, arm_r=-30, wipp_r=(14, 1.4), blick=1)
          + mann(330, 520, 0.75, 'm1+0.3', arm_r=-40, werkzeug_r='tablet', wipp_l=(12, 1.2), blick=-1)
          + f"<g class='pop' data-t='m2'><rect x='372' y='250' width='96' height='54' rx='27' fill='#2A2E2D'/>"
          + ''.join(f"<circle cx='{396+k*24}' cy='277' r='6' fill='{INK}'/>" for k in range(3)) + "</g>")
bild4 += mann(130, 515, 0.9, 'm2', arm_r=-90, werkzeug_r='laser', wipp_r=(12, 0.45), blick=1)
bild6 += (mann(380, 410, 0.85, 'm1', arm_r=150, werkzeug_r='hammer', wipp_r=(32, 2.4), arm_l=-25, blick=-1)
          + mann(872, 410, 0.7, 'm2+0.5', arm_l=40, werkzeug_l='tablet', blick=-1))
kiste = f"<rect x='573' y='318' width='54' height='44' rx='4' fill='{AKZ}'/>"
bild7 += f"<g data-t='m2' data-bewegung='120,0,m2,1.6'>{mann(600, 412, 0.6, 'm2', laufen=True, arm_l=-30, arm_r=30, extra=kiste)}</g>"
bild8 += (mann(150, 515, 0.85, '0.4', arm_r=-60, werkzeug_r='brecheisen', wipp_r=(14, 2.2), klasse='pop', extra='').replace("data-t='0.4' data-d='0.5'", "data-t='0.4' data-d='0.5' data-aus='m1'")
          + f"<g data-t='0.6' data-aus='m1+1.1' data-bewegung='-700,0,m1,1.0'>"
          f"{mann(262, 500, 0.85, '0.6', laufen=True, arm_r=-100, arm_l=-70)}{mann(658, 500, 0.85, '0.6', laufen=True, arm_l=100, arm_r=70)}</g>")
bild8 += (f"<g data-t='m2' data-aus='m3' data-bewegung='-700,0,m2,1.0'>"
          f"{mann(960, 500, 0.85, 'm2', laufen=True, arm_r=-100, arm_l=-60)}{mann(1360, 500, 0.85, 'm2', laufen=True, arm_l=100, arm_r=60)}</g>"
          + mann(150, 515, 0.85, 'm3', arm_r=-78, werkzeug_r='bohrer', wipp_r=(3, 9), blick=1))
html9 += (f"<svg viewBox='0 0 920 300' style='width:920px;height:300px;margin-top:10px;overflow:visible'>"
          + mann(370, 290, 0.9, 'm5+2', arm_r=-62, wipp_r=(6, 2), blick=1)
          + mann(550, 290, 0.9, 'm5+2', kunde=True, arm_l=62, wipp_l=(6, 2, 0.5), blick=-1) + "</svg>")
bild10 += (f"<g data-t='m5' data-huepfen='18,1.4'>{mann(835, 300, 0.55, 'm5', kunde=True, arm_l=150, arm_r=-150, wipp_l=(15, 2.8), wipp_r=(15, 2.8, 0.5))}</g>"
           f"<g data-t='m5+0.3' data-huepfen='18,1.4'>{mann(900, 300, 0.55, 'm5+0.3', arm_l=150, arm_r=-150, wipp_l=(15, 2.8, 0.25), wipp_r=(15, 2.8, 0.75))}</g>")

db = {
    "titel": "KIMUTEC – So arbeiten wir: vom Kontakt bis zur Abnahme",
    "fps": 30, "stimme": "chatterbox",
    "aussprache": {"kimutec.com": "Kimutek Punkt com", "KIMUTEC": "Kimutek"},
    "szenen": [
        {"label": "KIMUTEC | So arbeiten wir", "titel": "Neue Fenster?\nAlles aus\n<em>einer Hand.</em>", "bildHoehe": 500, "bild": bild1,
         "sprecher": "Neue Fenster? Bei KIMUTEC bekommen Sie alles aus einer Hand. |Vom ersten Kontakt |bis zur fertigen Abnahme.", "pause": 0.6},
        {"label": "01 | Kontakt", "titel": "Sie melden\nsich.", "schritt": 1, "bildHoehe": 520, "bild": bild2,
         "sprecher": "Schritt eins: |Sie melden sich, |per Nachricht, E-Mail oder Telefon. |Wir antworten schnell und machen einen Termin aus."},
        {"label": "02 | Beratung", "titel": "Beratung\nbei Ihnen\nzu Hause.", "schritt": 2, "bildHoehe": 530, "bild": bild3,
         "sprecher": "Schritt zwei: |die kostenlose Beratung vor Ort. |Wir schauen uns alles an und klären, was Ihnen wichtig ist: |Wärme, |Sicherheit, |Design |und Budget."},
        {"label": "03 | Aufmaß", "titel": "Wir messen\nselbst.", "schritt": 3, "bildHoehe": 520, "bild": bild4,
         "sprecher": "Schritt drei: das Aufmaß. |Wir messen selbst, |mit Laser |und an mehreren Punkten. |Das kleinste Maß zählt. So passt später jedes Fenster genau."},
        {"label": "04 | Angebot & Bestellung", "titel": "Klares\nAngebot.", "schritt": 4, "bildHoehe": 530, "bild": bild5,
         "sprecher": "Schritt vier: |Sie bekommen ein klares Angebot, |ohne versteckte Kosten. |Sie geben frei, |und wir bestellen direkt beim Hersteller."},
        {"label": "05 | Produktion", "titel": "Ihre Fenster\nentstehen.", "schritt": 5, "bildHoehe": 500, "bild": bild6,
         "sprecher": "Schritt fünf: die Produktion. |Ihre Fenster werden millimetergenau für Sie gebaut. |Den Liefertermin behalten wir für Sie im Blick."},
        {"label": "06 | Lieferung", "titel": "Pünktlich\ngeliefert.", "schritt": 6, "bildHoehe": 470, "bild": bild7,
         "sprecher": "Schritt sechs: die Lieferung. |Pünktlich zum Termin, |direkt zu Ihnen nach Hause."},
        {"label": "07 | Montage", "titel": "Montage\nnach Plan.", "schritt": 7, "bildHoehe": 520, "bild": bild8,
         "sprecher": "Schritt sieben: die Montage. |Das alte Fenster raus, |das neue rein, |fachgerecht abgedichtet: innen luftdicht, außen schlagregendicht. |Und wir hinterlassen alles sauber."},
        {"label": "08 | Abnahme", "titel": "Gemeinsame\nAbnahme.", "schritt": 8, "html": html9,
         "sprecher": "Schritt acht: |die Abnahme. |Wir prüfen gemeinsam jedes Fenster, |alle Anschlüsse, |zeigen Ihnen die Bedienung |und übergeben alles mit Protokoll."},
        {"label": "Das Ergebnis", "titel": "Und am\nEnde?", "bildHoehe": 640, "bild": bild10,
         "sprecher": "Und am Ende? |Schön warm. |Schön leise. |Zufrieden. |Und fast immer |dieselbe Frage: Warum haben wir das nicht früher gemacht?", "pause": 1.0},
        {"art": "abschluss", "label": "Alles aus einer Hand", "titel": "Jetzt Beratung\nvereinbaren.", "unter": "Kostenlose Erstberatung vor Ort\nin Pforzheim und Umgebung.",
         "kontakt": {"zeilen": [["NACHRICHT", "Direkt hier auf Instagram"], ["E-MAIL", "sales@kimutec.com"], ["WEB", "www.kimutec.com"]]},
         "motto": "QUALITÄT. WERTE. ZUHAUSE.",
         "sprecher": "KIMUTEC: alles aus einer Hand. Jetzt kostenlose Beratung vereinbaren, direkt hier per Nachricht oder über kimutec.com.", "pause": 1.4},
    ]}
ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drehbuch.json')
json.dump(db, open(ziel, 'w'), ensure_ascii=False, indent=1)
print('geschrieben:', ziel)
