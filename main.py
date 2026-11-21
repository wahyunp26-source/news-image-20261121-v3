#!/usr/bin/env python3
"""News-image-20261121 v3 entrypoint (Python 3.13, standard library only).

Reads layout.json and the prepared assets, draws the newspaper chrome
(rules, stats dividers, region bar, dotted world map with numbered pins,
date-check frame) and pastes the 13 illustrations plus the transparent
text layer, then writes a deterministic 1024x1024 PNG to entry.png.

Run:  python3 main.py [output-path]
Default output is /output/entry.png when /output exists, else entry.png
next to this file. Two runs write byte-identical files.
"""
import binascii
import json
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
W = 1024
MARGIN = 28
RIGHT = 996
CREAM = (247, 243, 232)
INK = (26, 26, 26)
RED = (192, 0, 0)
MAPDOT = (120, 110, 95)

# 3x5 pixel digits, for the numbered map pins.
DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(width, height, rgb):
    """Encode an RGB bytearray as a PNG. Fixed filter + level: deterministic."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(path):
    """Decode a non-interlaced 8-bit RGB or RGBA PNG to (w, h, RGBA bytearray)."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: " + path)
    pos = 8
    idat = bytearray()
    width = height = bitdepth = ctype = interlace = None
    while pos < len(data):
        (ln,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if kind == b"IHDR":
            width, height, bitdepth, ctype, _, _, interlace = struct.unpack(
                ">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
        elif kind == b"IEND":
            break
        pos += 12 + ln
    if bitdepth != 8 or interlace != 0 or ctype not in (2, 6):
        raise ValueError("unsupported PNG (need 8-bit RGB/RGBA): " + path)
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(bytes(idat))
    stride = width * bpp
    out = bytearray(width * height * 4)
    prev = bytearray(stride)
    for y in range(height):
        line = raw[y * (stride + 1):(y + 1) * (stride + 1)]
        ftype = line[0]
        cur = bytearray(line[1:])
        for i in range(stride):
            a = cur[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ftype == 0:
                pass
            elif ftype == 1:
                cur[i] = (cur[i] + a) & 0xFF
            elif ftype == 2:
                cur[i] = (cur[i] + b) & 0xFF
            elif ftype == 3:
                cur[i] = (cur[i] + (a + b) // 2) & 0xFF
            elif ftype == 4:
                cur[i] = (cur[i] + paeth(a, b, c)) & 0xFF
            else:
                raise ValueError("bad filter type %d" % ftype)
        prev = cur
        for x in range(width):
            o = (y * width + x) * 4
            s = x * bpp
            out[o:o + 3] = cur[s:s + 3]
            out[o + 3] = cur[s + 3] if bpp == 4 else 255
    return width, height, out


class Canvas:
    """An RGB canvas with rect / disc / paste helpers."""

    def __init__(self, width, height, color):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)
        self.rect(0, 0, width, height, color)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o:o + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + len(row)] = row

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.set(cx + dx, cy + dy, color)

    def paste(self, img, x, y):
        """Paste an RGBA image; img is (w, h, RGBA bytearray)."""
        iw, ih, data = img
        for yy in range(ih):
            ty = y + yy
            if ty < 0 or ty >= self.h:
                continue
            for xx in range(iw):
                tx = x + xx
                if tx < 0 or tx >= self.w:
                    continue
                o = (yy * iw + xx) * 4
                a = data[o + 3]
                if a == 0:
                    continue
                to = self._off(tx, ty)
                if a == 255:
                    self.px[to:to + 3] = data[o:o + 3]
                else:
                    for c in range(3):
                        self.px[to + c] = (
                            data[o + c] * a + self.px[to + c] * (255 - a)
                        ) // 255


def draw_digit(canvas, x, y, ch, color):
    glyph = DIGITS[ch]
    for r in range(5):
        for c in range(3):
            if glyph[r][c] == "1":
                canvas.set(x + c, y + r, color)


def draw_pin(canvas, cx, cy, num):
    # white ring first so the pin reads over the dotted map
    canvas.disc(cx, cy, 7, (255, 255, 255))
    canvas.disc(cx, cy, 6, RED)
    text = str(num)
    total = len(text) * 4 - 1
    x0 = cx - total // 2
    for i, ch in enumerate(text):
        draw_digit(canvas, x0 + i * 4, cy - 2, ch, (255, 255, 255))


def build(lay):
    cv = Canvas(W, W, CREAM)
    assets = os.path.join(HERE, "assets")

    # masthead rules
    cv.rect(MARGIN, 10, RIGHT - MARGIN, 3, RED)
    cv.rect(MARGIN, 36, RIGHT - MARGIN, 2, INK)
    cv.rect(MARGIN, 150, RIGHT - MARGIN, 1, INK)
    cv.rect(MARGIN, 212, RIGHT - MARGIN, 1, INK)

    # stats strip: red vertical dividers between the 6 columns
    colw = (RIGHT - MARGIN) / 6.0
    for i in range(1, 6):
        x = int(MARGIN + i * colw)
        cv.rect(x, 156, 2, 54, RED)

    # region bar: segments sized by story count; the last one runs
    # exactly to the right margin so no cream sliver shows
    total = sum(r["n"] for r in lay["regions"])
    x = MARGIN
    for j, r in enumerate(lay["regions"]):
        if j == len(lay["regions"]) - 1:
            wseg = RIGHT - x
        else:
            wseg = int(round((RIGHT - MARGIN) * r["n"] / total))
        cv.rect(x, 218, wseg, 20, tuple(r["color"]))
        x += wseg

    # illustrations
    for i, f in enumerate(lay["features"]):
        img = decode_png(os.path.join(assets, "img_%s.png" % f["key"]))
        cv.paste(img, MARGIN + i * (312 + 16), 242)
    for row in range(2):
        for j in range(5):
            m = lay["medium"][row * 5 + j]
            img = decode_png(os.path.join(assets, "img_%s.png" % m["key"]))
            cv.paste(img, int(MARGIN + j * (186 + 9.5)), 502 + row * 168)

    # dotted world map + numbered pins
    mp = lay["map"]
    rows = mp["rows"]
    nrows = len(rows)
    ncols = len(rows[0])
    for r in range(nrows):
        for c in range(ncols):
            if rows[r][c] == "#":
                dx = mp["x"] + int((c + 0.5) * mp["w"] / ncols) - 1
                dy = mp["y"] + int((r + 0.5) * mp["h"] / nrows) - 1
                cv.rect(dx, dy, 2, 2, MAPDOT)
    stories = lay["features"] + lay["medium"]
    for st in stories:
        px = mp["x"] + int((st["lon"] + 180.0) / 360.0 * mp["w"])
        py = mp["y"] + int((75.0 - st["lat"]) / 130.0 * mp["h"])
        draw_pin(cv, px, py, st["num"])

    # date-check frame
    cv.rect(MARGIN, 956, RIGHT - MARGIN, 2, RED)
    cv.rect(MARGIN, 992, RIGHT - MARGIN, 2, RED)
    cv.rect(MARGIN, 956, 2, 38, RED)
    cv.rect(RIGHT - 2, 956, 2, 38, RED)

    # text layer on top
    over = decode_png(os.path.join(assets, "over.png"))
    cv.paste(over, 0, 0)
    return cv.px


def main():
    with open(os.path.join(HERE, "layout.json"), encoding="utf-8") as fh:
        lay = json.load(fh)
    rgb = build(lay)
    png = encode_png(W, W, rgb)
    local = os.path.join(HERE, "entry.png")
    if len(sys.argv) > 1:
        dest = sys.argv[1]
    elif os.path.isdir("/output"):
        dest = "/output/entry.png"
    else:
        dest = local
    with open(dest, "wb") as fh:
        fh.write(png)
    if dest != local:
        with open(local, "wb") as fh:
            fh.write(png)
    print("wrote %s (%d bytes)" % (dest, len(png)))


if __name__ == "__main__":
    main()
