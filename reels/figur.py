# Figuren und Spuren für KIMUTEC-Drehbücher (Gegenstück zu reels/engine/bewegung.js).
#
#   figur('monteur', boden=600, z=[k(0, x=120, b=1), k('m1', x=400, gehen=True), k('m2', pose='messen', zV=[520, 300])])
#   spur(inhalt, [k(0, x=0), k('m3', x=-200, e='w')], id='s4-fenster')
#
# Zeiten: Sekunden ab Szenenstart, "40%" der Sprechzeit oder "m2+0.3" (0,3 s nach dem Wort hinter dem 2. |).
# Griffziele: [x, y] im Bild oder an(id, x, y) = Punkt eines Elements mit Spur (die Hand folgt ihm).
# Posen: stehen zeigen erklaeren tippen telefon messen tragen heben hocken knien bohren schreiben jubeln daumen sitzen winken haende
# Werkzeuge (pV/pH): handy laser klemmbrett stift bohrer kartusche tasse tablet daumen
import json

def _json(d):
    s = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
    assert "'" not in s and '&' not in s, 'Kein Apostroph oder & in Figuren-/Spurdaten verwenden'
    return s

def k(t, **w):
    """Ein Key: Zeitpunkt plus Werte (x, b, pose, Winkel, zV, zH, pV, pH, gehen, d, e, osz)."""
    d = {'t': t}
    d.update(w)
    return d

def an(id, x, y, dx=0, dy=0):
    """Griffziel: Punkt (x, y) eines Elements mit Spur, bewegt sich mit ihm."""
    z = {'an': id, 'x': x, 'y': y}
    if dx or dy:
        z.update(dx=dx, dy=dy)
    return z

def osz(g, a, f, dauer=None, ab=0):
    """Schwingen eines Gelenks: g = Winkelname (z. B. 'eV', 'ko'), a = Grad, f = pro Sekunde."""
    o = {'g': g, 'a': a, 'f': f}
    if dauer is not None:
        o['dauer'] = dauer
    if ab:
        o['ab'] = ab
    return o

def figur(typ, boden, z, s=1.0, t='0', d=0.4, saat=None):
    spec = {'typ': typ, 's': s, 'boden': boden, 'z': z}
    if saat is not None:
        spec['saat'] = saat
    return f"<g data-t='{t}' data-d='{d}' data-figur='{_json(spec)}'></g>"

def spur(inhalt, keys, id=None, ursprung=None, t=None, d=None):
    a = f" id='{id}'" if id else ''
    if ursprung:
        a += f" data-ursprung='{ursprung}'"
    if t is not None:
        a += f" data-t='{t}'"
    if d is not None:
        a += f" data-d='{d}'"
    return f"<g{a} data-spur='{_json(keys)}'>{inhalt}</g>"
