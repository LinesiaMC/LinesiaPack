#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les icônes 16x16 des pommes en améthyste, rubis et onyx.

La silhouette est celle de la pomme vanilla (même convention que la pomme
d'or : seule la chair est recolorée, la queue reste brune), repeinte avec la
rampe de teintes du matériau — les mêmes que `textures/items/ingot/*.png`,
pour que la pomme se lise immédiatement comme « du même métal » que le
lingot et l'armure.

    python3 tools/gen_gem_apples.py  ->  textures/items/apple/*.png
"""

import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "textures", "items", "apple")

# Silhouette vanilla. a/b/c = queue et contour brun (conservés tels quels),
# 0..6 = rampe de chair du plus sombre au plus clair.
SHAPE = (
    "................",
    ".........a......",
    "........bc......",
    "........a.......",
    ".....11acaa.....",
    "...1262c132aa...",
    "..1245666542aa..",
    "..12444444342a..",
    "..123434333430..",
    "..a22332232430..",
    "..a22222322420..",
    "...a223222320...",
    "...a122233210...",
    "....01211210....",
    ".....0aaa00.....",
    "................",
)

STEM = {
    "a": (117, 40, 2, 255),
    "b": (126, 55, 14, 255),
    "c": (84, 36, 9, 255),
}

# Éclat blanc unique, comme sur les lingots. L'onyx n'en porte pas : sa rampe
# monte déjà au gris clair et un pixel blanc y ferait une tache.
GLINT = (6, 6)

APPLES = {
    "amethyste_apple": (
        [(14, 2, 117), (63, 17, 178), (103, 19, 220), (127, 21, 233),
         (173, 74, 250), (208, 95, 253), (245, 224, 255)],
        True,
    ),
    "rubis_apple": (
        [(117, 2, 69), (178, 17, 81), (220, 19, 72), (233, 21, 60),
         (250, 74, 95), (253, 100, 95), (255, 224, 224)],
        True,
    ),
    "onyx_apple": (
        [(5, 5, 5), (13, 13, 13), (21, 21, 21), (30, 30, 30),
         (43, 43, 43), (61, 61, 61), (104, 104, 108)],
        False,
    ),
}


def build(ramp, glint):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(SHAPE):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch in STEM:
                px[x, y] = STEM[ch]
            else:
                px[x, y] = ramp[int(ch)] + (255,)
    if glint:
        px[GLINT] = (255, 255, 255, 255)
    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, (ramp, glint) in APPLES.items():
        path = os.path.join(OUT_DIR, name + ".png")
        build(ramp, glint).save(path)
        print("icône ->", path)


if __name__ == "__main__":
    main()
