# -*- coding: utf-8 -*-
"""Erzeugt die rote Nadel fuer fremde Faenge aus Leaflets eigener blauer Nadel.

    python nadel-rot.py

Karls Ansage vom 22.09.2026: "mach die markierungen fuer andere fische genauso wie
meine nur in rot".

Deshalb wird hier NICHTS gezeichnet, sondern Leaflets Bild genommen und je Pixel NUR
der Farbton gedreht. Helligkeit, Saettigung, Schattierung, Kanten und Durchsicht
bleiben exakt, wie sie sind -- und der weisse Punkt bleibt weiss, weil Weiss keinen
Farbton hat.

⚠️ Warum kein CSS-Filter: am 22.09.2026 gemessen. `hue-rotate(148deg)` allein trifft
   Rot, macht die Nadel aber heller (0,62 statt 0,50); mit `brightness()` stimmt die
   Helligkeit, dafuer wird der weisse Punkt GRAU. Beides waere nicht "genauso".
⚠️ Ergebnis wird von pruefungen.py nachgemessen (Farbton, Groesse, weisser Punkt).
"""
import colorsys, pathlib
from PIL import Image

HIER = pathlib.Path(__file__).resolve().parent
QUELLE = HIER / 'leaflet' / 'images'
# Leaflets Blau liegt bei 206 Grad (gemessen). Um 154 Grad weiter ist Rot bei 0 Grad.
DREH = 154 / 360

for alt, neu in [('marker-icon.png', 'nadel-rot.png'), ('marker-icon-2x.png', 'nadel-rot-2x.png')]:
    bild = Image.open(QUELLE / alt).convert('RGBA')
    px = bild.load()
    for x in range(bild.width):
        for y in range(bild.height):
            r, g, b, a = px[x, y]
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            r, g, b = colorsys.hls_to_rgb((h + DREH) % 1.0, l, s)
            px[x, y] = (round(r * 255), round(g * 255), round(b * 255), a)
    bild.save(HIER / neu, optimize=True)
    print(f'{neu}: {bild.width}x{bild.height}')
