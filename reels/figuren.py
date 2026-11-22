# Strichmännchen für KIMUTEC-Reels (Comic-Stil, ohne Gesicht).
# Arme und Beine sind eigene Linien-Gruppen mit Drehpunkt an Schulter bzw. Hüfte,
# damit sie per data-wippen schwingen können (hämmern, messen, tragen, laufen, jubeln).
#
#   mann(x, y, s=1, t='0.3', ...)  x/y = Fußpunkt (Mitte unten), s = Größe (1 ≈ 270 px hoch)
#   arm_l / arm_r: Grundwinkel in Grad (0 = hängt nach unten, 90 = zeigt nach links, -90 = nach rechts, 180 = hoch)
#   wipp_l / wipp_r: (Grad, Schwünge pro Sekunde[, Versatz]) – Arm schwingt um den Grundwinkel
#   laufen=True: Beine schwingen, Figur wippt leicht
#   werkzeug_l / werkzeug_r: 'hammer', 'laser', 'bohrer', 'tablet', 'daumen', 'mappe', 'brecheisen' oder None
#   kunde=True: ohne Helm (Handwerker tragen einen beigen Helm)
INK, AKZ = '#EEEAE2', '#D8B79C'

def _werkzeug(art, hx, hy, s):
    if art == 'hammer':
        return (f"<line x1='{hx}' y1='{hy}' x2='{hx}' y2='{hy+50*s}' stroke='{AKZ}' stroke-width='{6*s}' stroke-linecap='round'/>"
                f"<rect x='{hx-22*s}' y='{hy+44*s}' width='{44*s}' height='{18*s}' rx='{3*s}' fill='{INK}'/>")
    if art == 'laser':
        return (f"<rect x='{hx-13*s}' y='{hy-4*s}' width='{26*s}' height='{38*s}' rx='{5*s}' fill='{AKZ}'/>"
                f"<circle cx='{hx}' cy='{hy+36*s}' r='{5*s}' fill='#E0533F'/>")
    if art == 'bohrer':
        return (f"<rect x='{hx-12*s}' y='{hy-4*s}' width='{24*s}' height='{34*s}' rx='{4*s}' fill='{AKZ}'/>"
                f"<rect x='{hx-16*s}' y='{hy+26*s}' width='{32*s}' height='{22*s}' rx='{4*s}' fill='{AKZ}'/>"
                f"<line x1='{hx}' y1='{hy+48*s}' x2='{hx}' y2='{hy+76*s}' stroke='{INK}' stroke-width='{4*s}'/>")
    if art == 'brecheisen':
        return f"<path d='M{hx} {hy-10*s} L{hx} {hy+70*s} q0 {14*s} {-14*s} {14*s}' fill='none' stroke='{AKZ}' stroke-width='{7*s}' stroke-linecap='round'/>"
    if art == 'tablet':
        return f"<rect x='{hx-24*s}' y='{hy-6*s}' width='{48*s}' height='{62*s}' rx='{5*s}' fill='#111312' stroke='{INK}' stroke-width='{4*s}'/><rect x='{hx-16*s}' y='{hy+3*s}' width='{32*s}' height='{38*s}' fill='{AKZ}' opacity='.55'/>"
    if art == 'daumen':
        return f"<line x1='{hx}' y1='{hy}' x2='{hx}' y2='{hy-24*s}' stroke='{INK}' stroke-width='{7*s}' stroke-linecap='round'/>"
    if art == 'mappe':
        return f"<rect x='{hx-26*s}' y='{hy}' width='{52*s}' height='{40*s}' rx='{4*s}' fill='{AKZ}'/>"
    return ''

def _glied(x, y, L, s, winkel, wipp, werkzeug=None):
    linie = f"<line x1='{x}' y1='{y}' x2='{x}' y2='{y+L}' stroke='{INK}' stroke-width='{8*s}' stroke-linecap='round'/>" + _werkzeug(werkzeug, x, y + L, s)
    g = f"<g transform='rotate({winkel} {x} {y})'>{linie}</g>"
    if wipp:
        w, f, *ph = wipp
        return f"<g data-t='0' data-wippen='{w},{f},{ph[0] if ph else 0}' data-ursprung='{x}px {y}px'>{g}</g>"
    return g

def mann(x, y, s=1.0, t='0.3', arm_l=14, arm_r=-14, wipp_l=None, wipp_r=None, laufen=False,
         werkzeug_l=None, werkzeug_r=None, kunde=False, klasse='pop', extra='', blick=0):
    hy = y - 112 * s                       # Hüfte
    sy = y - 196 * s                       # Schulter
    ky = y - 238 * s                       # Kopfmitte
    bein_l = _glied(x, hy, 112 * s, s, 18 if not laufen else 0, (24, 1.6, 0.5) if laufen else None)
    bein_r = _glied(x, hy, 112 * s, s, -18 if not laufen else 0, (24, 1.6, 0) if laufen else None)
    rumpf = f"<line x1='{x}' y1='{ky+28*s}' x2='{x}' y2='{hy}' stroke='{INK}' stroke-width='{8*s}' stroke-linecap='round'/>"
    kopf = f"<circle cx='{x}' cy='{ky}' r='{27*s}' fill='#111312' stroke='{INK}' stroke-width='{7*s}'/>"
    helm = '' if kunde else (f"<path d='M{x-31*s} {ky-6*s} a{31*s} {30*s} 0 0 1 {62*s} 0 z' fill='{AKZ}'/>"
                             f"<line x1='{x-38*s}' y1='{ky-6*s}' x2='{x+38*s}' y2='{ky-6*s}' stroke='{AKZ}' stroke-width='{7*s}' stroke-linecap='round'/>")
    arm_links = _glied(x, sy, 88 * s, s, arm_l, wipp_l, werkzeug_l) if arm_l is not None else ''
    arm_rechts = _glied(x, sy, 88 * s, s, arm_r, wipp_r, werkzeug_r) if arm_r is not None else ''
    koerper = bein_l + bein_r + rumpf + arm_links + kopf + helm + arm_rechts + extra
    huepf = f" data-huepfen='{5*s:.0f},1.6'" if laufen else ''
    innen = f"<g data-t='0'{huepf}>{koerper}</g>" if laufen else koerper
    return f"<g class='{klasse}' data-t='{t}' data-d='0.5' data-ursprung='50% 100%'>{innen}</g>"
