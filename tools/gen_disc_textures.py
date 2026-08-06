#!/usr/bin/env python3
"""Génère les textures 16x16 des disques de musique custom.

Silhouette identique aux disques vanilla (ellipse 13x10 centrée, sillons
concentriques, pastille centrale 3x3) pour que les disques Linesia se
fondent dans l'inventaire à côté des disques Mojang. Seule la palette
change d'un disque à l'autre : `LABEL` donne la couleur de la pastille.

    python3 tools/gen_disc_textures.py
"""

from pathlib import Path

from PIL import Image

OUT_DIR = Path(__file__).resolve().parent.parent / "textures" / "items" / "record"

# Corps du vinyle, du sillon le plus clair au bord le plus sombre.
GROOVE_LIGHT = (74, 70, 82, 255)
GROOVE_MID = (52, 49, 58, 255)
VINYL = (34, 32, 39, 255)
RIM = (18, 17, 21, 255)

# Pastille centrale, par disque.
LABEL = {
    "disc_werenoi": {
        "core": (196, 84, 232, 255),
        "shine": (240, 190, 255, 255),
        "edge": (108, 38, 138, 255),
    },
}

CX, CY = 7.5, 8.0
RX, RY = 6.6, 5.1


def _inside(x, y, rx, ry):
    dx = (x + 0.5 - CX) / rx
    dy = (y + 0.5 - CY) / ry
    return dx * dx + dy * dy


def build(name, label):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()

    for y in range(16):
        for x in range(16):
            d = _inside(x, y, RX, RY)
            if d > 1.0:
                continue
            if d > 0.80:
                px[x, y] = RIM
            elif d > 0.62:
                px[x, y] = VINYL
            elif d > 0.42:
                # Sillon clair : n'éclaire que le quart haut-gauche, la
                # lumière vient de là sur tous les items du pack.
                lit = (x + 0.5 - CX) + (y + 0.5 - CY) < 0
                px[x, y] = GROOVE_LIGHT if lit else GROOVE_MID
            elif d > 0.22:
                px[x, y] = VINYL
            else:
                px[x, y] = GROOVE_MID

    # Pastille centrale 3x3 + reflet en haut à gauche.
    for y in range(7, 10):
        for x in range(6, 9):
            px[x, y] = label["core"]
    px[6, 7] = label["shine"]
    px[8, 9] = label["edge"]
    px[6, 9] = label["edge"]
    px[8, 7] = label["edge"]

    out = OUT_DIR / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def main():
    for name, label in LABEL.items():
        print("écrit", build(name, label))


if __name__ == "__main__":
    main()
