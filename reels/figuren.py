# Figuren für KIMUTEC-Reels: Handwerker und Kunde im flachen Linienstil.
# Arme und Beine sind eigene Gruppen mit Drehpunkt an Schulter bzw. Hüfte,
# damit sie per data-wippen schwingen können (hämmern, messen, laufen, winken).
#
#   mann(x, y, s=1, t='0.3', ...)  x/y = Fußpunkt (Mitte unten), s = Größe (1 ≈ 270 px hoch)
#   arm_l / arm_r: Grundwinkel in Grad (0 = hängt nach unten, 90 = zeigt nach links, -90 = nach rechts, 180 = hoch)
#   wipp_l / wipp_r: (Grad, Schwünge pro Sekunde[, Versatz]) – Arm schwingt um den Grundwinkel
#   laufen=True: Beine schwingen, Figur hüpft leicht
#   werkzeug_l / werkzeug_r: 'hammer', 'laser', 'bohrer', 'tablet', 'daumen', 'mappe' oder None
#   kunde=True: ohne Helm, andere Kleidung
INK, AKZ, JACKE, HAUT, KUNDE = '#EEEAE2', '#D8B79C', '#2A2E2D', '#E9D3BF', '#4A5A60'

def _werkzeug(art, hx, hy, s):
    if art == 'hammer':
        return (f"<line x1='{hx}' y1='{hy}' x2='{hx}' y2='{hy+46*s}' stroke='#8A6A4E' stroke-width='{7*s}' stroke-linecap='round'/>"
                f"<rect x='{hx-22*s}' y='{hy+40*s}' width='{44*s}' height='{18*s}' rx='{3*s}' fill='{INK}'/>")
    if art == 'laser':
        return (f"<rect x='{hx-14*s}' y='{hy-6*s}' width='{28*s}' height='{40*s}' rx='{5*s}' fill='{AKZ}'/>"
                f"<circle cx='{hx}' cy='{hy+38*s}' r='{5*s}' fill='#C0392B'/>")
    if art == 'bohrer':
        return (f"<rect x='{hx-12*s}' y='{hy-4*s}' width='{24*s}' height='{34*s}' rx='{4*s}' fill='{AKZ}'/>"
                f"<rect x='{hx-16*s}' y='{hy+26*s}' width='{32*s}' height='{22*s}' rx='{4*s}' fill='{AKZ}'/>"
                f"<line x1='{hx}' y1='{hy+48*s}' x2='{hx}' y2='{hy+74*s}' stroke='{INK}' stroke-width='{4*s}'/>")
    if art == 'tablet':
        return f"<rect x='{hx-24*s}' y='{hy-6*s}' width='{48*s}' height='{62*s}' rx='{5*s}' fill='#111312' stroke='{INK}' stroke-width='{3*s}'/><rect x='{hx-17*s}' y='{hy+2*s}' width='{34*s}' height='{40*s}' fill='{AKZ}' opacity='.5'/>"
    if art == 'daumen':
        return f"<rect x='{hx-6*s}' y='{hy-30*s}' width='{12*s}' height='{26*s}' rx='{6*s}' fill='{HAUT}'/>"
    if art == 'mappe':
        return f"<rect x='{hx-26*s}' y='{hy}' width='{52*s}' height='{40*s}' rx='{4*s}' fill='{AKZ}'/><rect x='{hx-8*s}' y='{hy-8*s}' width='{16*s}' height='{10*s}' rx='{3*s}' fill='none' stroke='{AKZ}' stroke-width='{3*s}'/>"
    return ''

def _arm(sx, sy, s, winkel, wipp, werkzeug, farbe, seite):
    L = 92 * s
    inner = (f"<line x1='{sx}' y1='{sy}' x2='{sx}' y2='{sy+L}' stroke='{INK}' stroke-width='{22*s}' stroke-linecap='round'/>"
             f"<line x1='{sx}' y1='{sy}' x2='{sx}' y2='{sy+L}' stroke='{farbe}' stroke-width='{15*s}' stroke-linecap='round'/>"
             f"<circle cx='{sx}' cy='{sy+L+4*s}' r='{10*s}' fill='{HAUT}'/>" + _werkzeug(werkzeug, sx, sy + L + 4 * s, s))
    g = f"<g transform='rotate({winkel} {sx} {sy})'>{inner}</g>"
    if wipp:
        w, f, *ph = wipp
        return f"<g data-t='0' data-wippen='{w},{f},{ph[0] if ph else 0}' data-ursprung='{sx}px {sy}px'>{g}</g>"
    return g

def _bein(hx, hy, s, laufen, phase, hose):
    L = 110 * s
    b = (f"<line x1='{hx}' y1='{hy}' x2='{hx}' y2='{hy+L}' stroke='{INK}' stroke-width='{24*s}' stroke-linecap='round'/>"
         f"<line x1='{hx}' y1='{hy}' x2='{hx}' y2='{hy+L}' stroke='{hose}' stroke-width='{17*s}' stroke-linecap='round'/>"
         f"<rect x='{hx-14*s}' y='{hy+L-4*s}' width='{34*s}' height='{14*s}' rx='{6*s}' fill='{INK}'/>")
    if laufen:
        return f"<g data-t='0' data-wippen='22,1.6,{phase}' data-ursprung='{hx}px {hy}px'>{b}</g>"
    return b

def mann(x, y, s=1.0, t='0.3', arm_l=12, arm_r=-12, wipp_l=None, wipp_r=None, laufen=False,
         werkzeug_l=None, werkzeug_r=None, kunde=False, klasse='pop', extra='', blick=0):
    jacke = KUNDE if kunde else JACKE
    hose = '#1B1E1D' if not kunde else '#2E3436'
    hy = y - 124 * s                      # Hüfthöhe
    top = y - 230 * s                     # Oberkante Rumpf
    sy = top + 14 * s                     # Schulterhöhe
    kopf_y = top - 34 * s
    teile = [
        _bein(x - 13 * s, hy, s, laufen, 0, hose), _bein(x + 13 * s, hy, s, laufen, 0.5, hose),
        _arm(x - 34 * s, sy, s, arm_l, wipp_l, werkzeug_l, jacke, 'l') if arm_l is not None else '',
        f"<rect x='{x-36*s}' y='{top}' width='{72*s}' height='{112*s}' rx='{18*s}' fill='{jacke}' stroke='{INK}' stroke-width='{3.5*s}'/>",
    ]
    if not kunde:
        teile.append(f"<rect x='{x-36*s}' y='{top+56*s}' width='{72*s}' height='{11*s}' fill='{AKZ}'/>")
    else:
        teile.append(f"<path d='M{x-14*s} {top} L{x} {top+22*s} L{x+14*s} {top}' fill='none' stroke='{INK}' stroke-width='{3*s}'/>")
    teile.append(f"<circle cx='{x}' cy='{kopf_y}' r='{30*s}' fill='{HAUT}' stroke='{INK}' stroke-width='{3*s}'/>")
    auge = blick * 7 * s
    teile.append(f"<circle cx='{x-10*s+auge}' cy='{kopf_y+2*s}' r='{3.6*s}' fill='#111312'/><circle cx='{x+10*s+auge}' cy='{kopf_y+2*s}' r='{3.6*s}' fill='#111312'/>"
                 f"<path d='M{x-9*s+auge} {kopf_y+13*s} q{9*s} {8*s} {18*s} 0' fill='none' stroke='#111312' stroke-width='{2.6*s}' stroke-linecap='round'/>")
    if not kunde:   # Helm
        teile.append(f"<path d='M{x-33*s} {kopf_y-6*s} a{33*s} {32*s} 0 0 1 {66*s} 0 z' fill='{INK}'/><rect x='{x-4*s}' y='{kopf_y-37*s}' width='{8*s}' height='{31*s}' fill='{AKZ}'/><rect x='{x-40*s}' y='{kopf_y-10*s}' width='{80*s}' height='{9*s}' rx='{4*s}' fill='{AKZ}'/>")
    else:           # Haare
        teile.append(f"<path d='M{x-30*s} {kopf_y-4*s} a{30*s} {30*s} 0 0 1 {60*s} 0 q{-30*s} {-14*s} {-60*s} 0z' fill='#5A4636'/>")
    teile.append(_arm(x + 34 * s, sy, s, arm_r, wipp_r, werkzeug_r, jacke, 'r') if arm_r is not None else '')
    koerper = ''.join(teile) + extra
    huepf = f" data-huepfen='{6*s:.0f},1.6'" if laufen else ''
    innen = f"<g data-t='0'{huepf}>{koerper}</g>" if laufen else koerper
    return f"<g class='{klasse}' data-t='{t}' data-d='0.5' data-ursprung='50% 100%'>{innen}</g>"
