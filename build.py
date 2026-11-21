#!/usr/bin/env python3
"""Build-time composer for the news-image-20261121 v3 front page.

Renders the transparent text layer (assets/over.png) with PIL and prepares
the 13 illustrations at their exact placement sizes (assets/img_*.png).
Then runs main.py (the stdlib-only entrypoint) to produce entry.png and
slices the three preview crops. Not part of the graded run.
"""
import glob
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "/tmp/news21-v3-raw"
ASSETS = os.path.join(HERE, "assets")

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_IT = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

CREAM = (247, 243, 232)
INK = (26, 26, 26)
RED = (192, 0, 0)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

W = 1024
M = 28
X1 = 996


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = cur + " " + w
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_size(draw, text, path, start, width):
    size = start
    while size > 10:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= width:
            return fnt
        size -= 1
    return font(path, 10)


def prep_image(key, tw, th):
    """Fit the whole illustration inside (tw, th): the side bars are the
    source's own edge columns stretched sideways, so they continue the
    picture's background exactly, with the correctly-proportioned image
    pasted centred on top. Nothing is cropped, so no motif is ever cut off,
    and no motif is ever doubled."""
    srcs = glob.glob(os.path.join(RAW, "media-generation-%s-*.png" % key))
    if not srcs:
        raise SystemExit("missing illustration: " + key)
    im = Image.open(srcs[0]).convert("RGB")
    scale = min(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    small = im.resize((nw, nh), Image.LANCZOS)
    bg = Image.new("RGB", (tw, th))
    left_w = (tw - nw) // 2
    right_w = tw - nw - left_w
    top = (th - nh) // 2
    if left_w:
        bg.paste(im.crop((0, 0, 1, im.height)).resize((left_w, th)),
                 (0, 0))
    if right_w:
        bg.paste(im.crop((im.width - 1, 0, im.width, im.height))
                 .resize((right_w, th)), (left_w + nw, 0))
    if top:
        bg.paste(im.crop((0, 0, im.width, 1)).resize((tw, top)), (0, 0))
        bg.paste(im.crop((0, im.height - 1, im.width, im.height))
                 .resize((tw, th - nh - top)), (0, top + nh))
    bg.paste(small, (left_w, top))
    bg.save(os.path.join(ASSETS, "img_%s.png" % key))
    return bg.size


def main():
    with open(os.path.join(HERE, "layout.json"), encoding="utf-8") as fh:
        lay = json.load(fh)
    os.makedirs(ASSETS, exist_ok=True)

    # --- illustrations at placement size (whole motif, never cropped) ---
    for f in lay["features"]:
        prep_image(f["key"], 312, 136)
    for m in lay["medium"]:
        prep_image(m["key"], 186, 78)

    # --- text layer ---
    over = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)

    # kicker row (baseline-anchored so the rule below stays clear)
    d.text((M, 30), lay["kicker_left"], font=font(SANS_B, 13),
           fill=RED + (255,), anchor="ls")
    d.text((X1, 30), lay["kicker_right"], font=font(SANS_B, 11),
           fill=INK + (255,), anchor="rs")

    # headline + subhead, auto-fit to the content width
    hf = fit_size(d, lay["headline"], SERIF, 82, W - 2 * M)
    d.text((W // 2, 46), lay["headline"], font=hf, fill=INK + (255,),
           anchor="ma")
    sf = fit_size(d, lay["subhead"], SERIF_IT, 19, W - 2 * M)
    d.text((W // 2, 126), lay["subhead"], font=sf, fill=INK + (255,),
           anchor="ma")

    # stats strip: 6 columns
    colw = (W - 2 * M) / 6.0
    for i, st in enumerate(lay["stats"]):
        cx = M + i * colw
        d.text((cx + 2, 158), st["big"], font=font(SANS_B, 28),
               fill=INK + (255,), anchor="la")
        lines = wrap(d, st["cap"], font(SANS, 11), colw - 14)
        assert len(lines) <= 2, ("stat caption too long", st["cap"])
        y = 188
        for ln in lines:
            d.text((cx + 2, y), ln, font=font(SANS, 11),
                   fill=INK + (255,), anchor="la")
            y += 12

    # region bar labels (segments are drawn by main.py)
    total = sum(r["n"] for r in lay["regions"])
    x = M
    for r in lay["regions"]:
        wseg = (W - 2 * M) * r["n"] / total
        label = "%s %d" % (r["name"], r["n"])
        d.text((x + wseg / 2, 228), label, font=font(SANS_B, 10),
               fill=WHITE + (255,), anchor="ma")
        x += wseg

    def draw_card(story, x, y_img, iw, ih, tag_r, tag_px, head_px,
                  body_px, kick_px, src_px):
        # kicker label + source strip sit on the picture
        k = story["kicker"]
        kf = font(SANS_B, kick_px)
        kw = d.textlength(k, font=kf)
        kh = kick_px + 11
        d.rectangle([x, y_img, x + kw + 12, y_img + kh], fill=RED + (255,))
        d.text((x + 6, y_img + kh / 2), k, font=kf, fill=WHITE + (255,),
               anchor="lm")
        s = story["source"]
        sfnt = font(SANS, src_px)
        sw = d.textlength(s, font=sfnt)
        sh = src_px + 8
        d.rectangle([x, y_img + ih - sh, x + sw + 10, y_img + ih],
                    fill=BLACK + (255,))
        d.text((x + 5, y_img + ih - sh / 2), s, font=sfnt,
               fill=WHITE + (255,), anchor="lm")
        # numbered tag
        ty = y_img + ih + 6
        d.ellipse([x, ty, x + 2 * tag_r, ty + 2 * tag_r], fill=RED + (255,))
        num = str(story["num"])
        d.text((x + tag_r, ty + tag_r), num, font=font(SANS_B, tag_px),
               fill=WHITE + (255,), anchor="mm")
        d.text((x + 2 * tag_r + 5, ty + tag_r), story["tag"],
               font=font(SANS_B, tag_px), fill=RED + (255,), anchor="lm")
        # headline + body
        hy = ty + 2 * tag_r + 4
        hlines = wrap(d, story["head"], font(SERIF, head_px), iw)
        assert len(hlines) <= 2, ("headline too long", story["head"])
        yy = hy
        for ln in hlines:
            d.text((x, yy), ln, font=font(SERIF, head_px),
                   fill=INK + (255,), anchor="la")
            yy += head_px + 2
        by = yy + 2
        blines = wrap(d, story["body"], font(SANS, body_px), iw)
        maxbody = 3 if iw > 200 else 2
        assert len(blines) <= maxbody, ("body too long", story["body"])
        for ln in blines:
            d.text((x, by), ln, font=font(SANS, body_px),
                   fill=INK + (255,), anchor="la")
            by += body_px + 3

    # 3 features
    for i, f in enumerate(lay["features"]):
        x = M + i * (312 + 16)
        draw_card(f, x, 242, 312, 136, 7, 11, 22, 12, 15, 10)
    # 10 medium cards, 2 rows x 5
    for row in range(2):
        for j in range(5):
            m = lay["medium"][row * 5 + j]
            x = M + j * (186 + 9.5)
            y_img = 502 + row * 168
            draw_card(m, x, y_img, 186, 78, 6, 9, 15, 11, 11, 9)

    # bottom headings
    d.text((M, 836), "WHERE IT HAPPENED", font=font(SANS_B, 11),
           fill=INK + (255,), anchor="la")
    d.text((424, 836), "ALSO ON SATURDAY 21 NOVEMBER — 22 MORE STORIES",
           font=font(SANS_B, 11), fill=INK + (255,), anchor="la")
    # briefs, 2 columns x 11 rows
    bf = font(SANS, 9)
    for i, b in enumerate(lay["briefs"]):
        col = i // 11
        row = i % 11
        bx = 424 + col * 292
        by = 852 + row * 9.0
        num = "%d " % (14 + i)
        full = num + b
        wdt = d.textlength(full, font=bf)
        assert wdt <= 282, ("brief too wide", full, wdt)
        d.text((bx, by), num, font=font(SANS_B, 9), fill=RED + (255,),
               anchor="la")
        nw = d.textlength(num, font=font(SANS_B, 9))
        d.text((bx + nw, by), b, font=bf, fill=INK + (255,), anchor="la")

    # date check (inside the red box drawn by main.py): bold red lead-in,
    # then the rest of the sentence; first line is narrower by the lead.
    reg = font(SANS, 11)
    bold = font(SANS_B, 11)
    lead = "DATE CHECK — "
    lead_w = d.textlength(lead, font=bold)
    total_w = X1 - M - 16
    rest = lay["datecheck"][len(lead):]
    dc_lines = []
    cur = ""
    limit = total_w - lead_w
    for w in rest.split():
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=reg) <= limit:
            cur = trial
        else:
            dc_lines.append(cur)
            cur = w
            limit = total_w
    dc_lines.append(cur)
    assert len(dc_lines) <= 2, ("datecheck too long", dc_lines)
    d.text((M + 8, 963), lead, font=bold, fill=RED + (255,), anchor="la")
    d.text((M + 8 + lead_w, 963), dc_lines[0], font=reg,
           fill=INK + (255,), anchor="la")
    if len(dc_lines) > 1:
        d.text((M + 8, 976), dc_lines[1], font=reg, fill=INK + (255,),
               anchor="la")

    # footer
    d.text((M, 1012), lay["footer"], font=font(SANS, 9),
           fill=GREY + (255,), anchor="la")

    over.save(os.path.join(ASSETS, "over.png"))

    # --- run the entrypoint, then slice previews ---
    subprocess.run([sys.executable, "main.py", "entry.png"],
                   cwd=HERE, check=True)
    entry = Image.open(os.path.join(HERE, "entry.png"))
    assert entry.size == (1024, 1024), entry.size
    entry.crop((0, 0, 1024, 360)).save(os.path.join(HERE, "preview-top.png"))
    entry.crop((0, 360, 1024, 700)).save(
        os.path.join(HERE, "preview-medium.png"))
    entry.crop((0, 700, 1024, 1024)).save(
        os.path.join(HERE, "preview-bottom.png"))
    raw = open(os.path.join(HERE, "entry.png"), "rb").read()
    print("entry.png magic:", raw[:8].hex(), "size:", len(raw), "bytes")


if __name__ == "__main__":
    main()
