#!/usr/bin/env python3
"""Génère l'icône 16x16 de l'item kart.

L'icône est un rendu isométrique du vrai modèle
(`LinesiaEntity/models/entity/linesia_kart.geo.json`) réduit en 16x16 :
l'item et l'entité posée montrent ainsi exactement le même kart.

    python3 tools/gen_kart_icon.py  ->  textures/items/item/kart.png
"""

import json
import math
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTITY_PACK = os.path.join(os.path.dirname(ROOT), "LinesiaEntity")
GEO = os.path.join(ENTITY_PACK, "models", "entity", "linesia_kart.geo.json")
TEX = os.path.join(ENTITY_PACK, "textures", "entity", "linesia_kart.png")

SUPERSAMPLE = 24
YAW = math.radians(218)
PITCH = math.radians(24)

FACES = {
    "north": ([0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]),
    "south": ([0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]),
    "west":  ([0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]),
    "east":  ([1, 0, 0], [1, 0, 1], [1, 1, 1], [1, 1, 0]),
    "up":    ([0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]),
    "down":  ([0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]),
}
NORMALS = {
    "north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0),
    "east": (1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0),
}


def project(point):
    x, y, z = point
    cx = x * math.cos(YAW) - z * math.sin(YAW)
    cz = x * math.sin(YAW) + z * math.cos(YAW)
    return cx, -(y * math.cos(PITCH) - cz * math.sin(PITCH)), y * math.sin(PITCH) + cz * math.cos(PITCH)


def rotate_x(point, degrees, pivot):
    a = math.radians(degrees)
    x, y, z = point[0] - pivot[0], point[1] - pivot[1], point[2] - pivot[2]
    return (x + pivot[0],
            y * math.cos(a) - z * math.sin(a) + pivot[1],
            y * math.sin(a) + z * math.cos(a) + pivot[2])


def main():
    geo = json.load(open(GEO, encoding="utf-8"))
    bones = geo["minecraft:geometry"][0]["bones"]
    tex = Image.open(TEX).convert("RGB")

    polys = []
    for bone in bones:
        rotation = bone.get("rotation")
        pivot = bone["pivot"]
        for cube in bone.get("cubes", []):
            ox, oy, oz = cube["origin"]
            sx, sy, sz = cube["size"]
            for name, corners in FACES.items():
                points, depths = [], []
                for cx, cy, cz in corners:
                    p = (ox + cx * sx, oy + cy * sy, oz + cz * sz)
                    if rotation:
                        p = rotate_x(p, rotation[0], pivot)
                    px, py, depth = project(p)
                    points.append((px, py))
                    depths.append(depth)
                uv = cube["uv"][name]
                x, y = uv["uv"]
                w, h = uv["uv_size"]
                color = tex.crop((x, y, x + w, y + h)).resize((1, 1), Image.BOX).getpixel((0, 0))
                nx, ny, nz = NORMALS[name]
                light = 0.66 + 0.44 * max(0.0, nx * -0.45 + ny * 0.85 + nz * -0.3)
                polys.append((sum(depths) / 4,
                              points,
                              tuple(min(255, int(c * light)) for c in color)))

    polys.sort(key=lambda item: item[0])

    xs = [p[0] for _, pts, _ in polys for p in pts]
    ys = [p[1] for _, pts, _ in polys for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    scale = (16 * SUPERSAMPLE) / (span * 1.14)
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    size = 16 * SUPERSAMPLE

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for _, pts, color in polys:
        draw.polygon([(size / 2 + (px - cx) * scale, size / 2 + (py - cy) * scale) for px, py in pts],
                     fill=color + (255,))

    icon = img.resize((16, 16), Image.LANCZOS)
    px = icon.load()
    for j in range(16):
        for i in range(16):
            r, g, b, a = px[i, j]
            px[i, j] = (r, g, b, 255) if a >= 110 else (0, 0, 0, 0)

    out = os.path.join(ROOT, "textures", "items", "item", "kart.png")
    icon.save(out)
    print("icône ->", out)


if __name__ == "__main__":
    main()
