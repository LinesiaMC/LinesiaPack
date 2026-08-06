#!/usr/bin/env python3
"""Génère l'icône 16x16 de l'item ballon de foot.

Comme pour le kart, l'icône est un rendu isométrique du vrai modèle
(`LinesiaEntity/models/entity/linesia_football.geo.json`) : l'item et
l'entité posée montrent exactement le même ballon. Le rendu est fait
texel par texel — un aplat par face effacerait les pentagones.

    python3 tools/gen_football_icon.py           ->  textures/items/item/football.png
    python3 tools/gen_football_icon.py preview.png 512   ->  aperçu

"""

import math
import json
import os
import sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTITY_PACK = os.path.join(os.path.dirname(ROOT), "LinesiaEntity")
GEO = os.path.join(ENTITY_PACK, "models", "entity", "linesia_football.geo.json")
TEX = os.path.join(ENTITY_PACK, "textures", "entity", "linesia_football.png")

SUPERSAMPLE = 24
YAW = math.radians(214)
PITCH = math.radians(20)

CORNERS = {
    "north": ([0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, 0]),
    "south": ([1, 1, 1], [0, 1, 1], [0, 0, 1], [1, 0, 1]),
    "west":  ([0, 1, 1], [0, 1, 0], [0, 0, 0], [0, 0, 1]),
    "east":  ([1, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]),
    "up":    ([0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]),
    "down":  ([0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 0, 0]),
}


def project(point):
    x, y, z = point
    cx = x * math.cos(YAW) - z * math.sin(YAW)
    cz = x * math.sin(YAW) + z * math.cos(YAW)
    return (cx,
            -(y * math.cos(PITCH) - cz * math.sin(PITCH)),
            y * math.sin(PITCH) + cz * math.cos(PITCH))


def lerp(a, b, t):
    return [a[i] + (b[i] - a[i]) * t for i in range(3)]


def quads():
    """Un quad projeté par texel, avec sa couleur et sa profondeur."""
    geo = json.load(open(GEO, encoding="utf-8"))
    tex = Image.open(TEX).convert("RGB")
    pixels = tex.load()

    out = []
    for bone in geo["minecraft:geometry"][0]["bones"]:
        for cube in bone.get("cubes", []):
            ox, oy, oz = cube["origin"]
            sx, sy, sz = cube["size"]
            for face, corners in CORNERS.items():
                uv = cube["uv"].get(face)
                if uv is None:
                    continue
                ux, uy = uv["uv"]
                uw, uh = uv["uv_size"]
                # Coins de la face, dans l'ordre du repère UV : (0,0) en haut
                # à gauche du rectangle d'atlas.
                pts = [[ox + c[0] * sx, oy + c[1] * sy, oz + c[2] * sz]
                       for c in corners]
                for j in range(int(uh)):
                    for i in range(int(uw)):
                        u0, u1 = i / uw, (i + 1) / uw
                        v0, v1 = j / uh, (j + 1) / uh
                        cell = [
                            lerp(lerp(pts[0], pts[1], u0), lerp(pts[3], pts[2], u0), v0),
                            lerp(lerp(pts[0], pts[1], u1), lerp(pts[3], pts[2], u1), v0),
                            lerp(lerp(pts[0], pts[1], u1), lerp(pts[3], pts[2], u1), v1),
                            lerp(lerp(pts[0], pts[1], u0), lerp(pts[3], pts[2], u0), v1),
                        ]
                        flat = [project(p) for p in cell]
                        depth = sum(p[2] for p in flat) / 4
                        out.append((depth,
                                    [(p[0], p[1]) for p in flat],
                                    pixels[ux + i, uy + j]))
    out.sort(key=lambda q: q[0])
    return out


def render(size):
    polys = quads()
    xs = [p[0] for _, pts, _ in polys for p in pts]
    ys = [p[1] for _, pts, _ in polys for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    scale = size / (span * 1.06)
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for _, pts, color in polys:
        draw.polygon(
            [(size / 2 + (px - cx) * scale, size / 2 + (py - cy) * scale)
             for px, py in pts],
            fill=color + (255,), outline=color + (255,))
    return img


def main():
    if len(sys.argv) > 1:
        out = sys.argv[1]
        size = int(sys.argv[2]) if len(sys.argv) > 2 else 512
        render(size).save(out)
        print("aperçu ->", out)
        return

    icon = render(16 * SUPERSAMPLE).resize((16, 16), Image.LANCZOS)
    px = icon.load()
    for j in range(16):
        for i in range(16):
            r, g, b, a = px[i, j]
            px[i, j] = (r, g, b, 255) if a >= 110 else (0, 0, 0, 0)

    out = os.path.join(ROOT, "textures", "items", "item", "football.png")
    icon.save(out)
    print("icône ->", out)


if __name__ == "__main__":
    main()
