#!/usr/bin/env python3
"""Draw the GTA 6 launch-week meme for make.fun bounty gta6-meme-x-01.

1024x1024 PNG, PIL only, fully deterministic (no randomness, no time, no
network). Run: python3 draw_meme.py  -> writes meme.png next to this script.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meme.png")

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    return ImageFont.truetype(BOLD, size)


def fit_font(draw, text, max_w, start_size):
    """Shrink font until text fits max_w."""
    size = start_size
    while size > 10:
        f = font(size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(size)


def text_center(draw, y, text, size, fill, stroke_w=6, stroke_fill=(20, 0, 40)):
    f = fit_font(draw, text, W - 80, size)
    draw.text((W / 2, y), text, font=f, fill=fill, anchor="mm",
              stroke_width=stroke_w, stroke_fill=stroke_fill)
    return f.getbbox(text)[3]  # approx height


def main():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # --- synthwave sky gradient: deep purple -> magenta -> orange ---
    top = (26, 0, 51)
    mid = (140, 10, 90)
    bot = (255, 90, 60)
    for y in range(H):
        t = y / H
        if t < 0.55:
            k = t / 0.55
            c = tuple(int(top[i] + (mid[i] - top[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    # --- retro sun with slits, centered upper-middle ---
    cx, cy, r = W // 2, 430, 210
    sun_top, sun_bot = (255, 214, 64), (255, 46, 136)
    sun = Image.new("RGB", (2 * r, 2 * r))
    sd = ImageDraw.Draw(sun)
    for yy in range(2 * r):
        k = yy / (2 * r)
        c = tuple(int(sun_top[i] + (sun_bot[i] - sun_top[i]) * k) for i in range(3))
        sd.line([(0, yy), (2 * r, yy)], fill=c)
    mask = Image.new("L", (2 * r, 2 * r), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, 2 * r, 2 * r], fill=255)
    # horizontal slits, thicker toward the bottom of the sun
    for i, (sy, th) in enumerate([(215, 6), (250, 9), (290, 13), (335, 18), (385, 24)]):
        md.rectangle([0, sy, 2 * r, sy + th], fill=0)
    img.paste(sun, (cx - r, cy - r), mask)

    # --- neon grid floor (bottom third) ---
    horizon = 640
    d.line([(0, horizon), (W, horizon)], fill=(0, 255, 255), width=4)
    for i in range(1, 7):
        y = horizon + int((H - horizon) * (i / 6) ** 1.6)
        d.line([(0, y), (W, y)], fill=(255, 46, 136), width=3)
    for x in range(-W, 2 * W, 128):
        d.line([(W // 2, horizon), (x, H)], fill=(0, 255, 255), width=2)

    # --- headline (top) ---
    text_center(d, 78, "GTA VI IS", 96, (255, 255, 255), stroke_w=8)
    text_center(d, 178, "FINALLY OUT", 96, (255, 235, 59), stroke_w=8)

    # --- loading bar joke (under headline, above sun) ---
    bar_x0, bar_x1, bar_y = 262, 762, 268
    d.rounded_rectangle([bar_x0, bar_y, bar_x1, bar_y + 26], radius=13,
                        outline=(255, 255, 255), width=4)
    d.rounded_rectangle([bar_x0 + 4, bar_y + 4, bar_x0 + 4 + 12, bar_y + 22],
                        radius=9, fill=(0, 255, 255))
    text_center(d, 312, "DOWNLOADING... 1%", 34, (255, 255, 255), stroke_w=4)

    # --- make.fun ghost mascot (center, in front of the sun) ---
    gx0, gx1 = 392, 632          # ghost body x-range (240 wide)
    gy_top, gy_bot = 380, 660    # ghost y-range
    # soft glow behind ghost
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([gx0 - 55, gy_top - 45, gx1 + 55, gy_bot + 55],
               fill=(255, 255, 255, 60))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    d = ImageDraw.Draw(img)
    # body: dome + straight sides + wavy hem
    body = [(gx0, gy_bot - 40)]
    body += [(gx0, gy_top + 90)]
    # dome arc (sampled)
    import math
    dome_cx, dome_cy, dome_r = (gx0 + gx1) // 2, gy_top + 90, (gx1 - gx0) // 2
    for ang in range(180, 361, 6):
        rad = math.radians(ang)
        body.append((dome_cx + dome_r * math.cos(rad),
                     dome_cy + dome_r * math.sin(rad)))
    body += [(gx1, gy_bot - 40)]
    # wavy hem: 4 smooth scallops dipping down
    seg = (gx1 - gx0) / 4
    for i in range(4):
        x_a = gx1 - i * seg
        x_b = gx1 - (i + 1) * seg
        for s in range(1, 11):
            t = s / 10
            x = x_a + (x_b - x_a) * t
            y = (gy_bot - 40) + 58 * math.sin(math.pi * t)
            body.append((x, y))
    d.polygon(body, fill=(255, 255, 255), outline=(20, 0, 40))
    d.line(body + [body[0]], fill=(20, 0, 40), width=5, joint="curve")
    # eyes
    d.ellipse([452, 500, 486, 552], fill=(20, 0, 40))
    d.ellipse([538, 500, 572, 552], fill=(20, 0, 40))
    # smile
    d.ellipse([492, 566, 532, 592], fill=(20, 0, 40))

    # --- punchline (below ghost) ---
    text_center(d, 726, "MY AI AGENT GOT PAID", 58, (255, 255, 255), stroke_w=6)
    text_center(d, 792, "BEFORE THE DOWNLOAD", 58, (255, 255, 255), stroke_w=6)
    text_center(d, 856, "FINISHED", 58, (0, 255, 255), stroke_w=6)

    # --- make.fun wordmark band (bottom) ---
    d.rectangle([0, 920, W, H], fill=(20, 0, 40))
    d.line([(0, 920), (W, 920)], fill=(255, 46, 136), width=5)
    # mini ghost left of the wordmark
    mgx, mgy = 268, 972
    d.ellipse([mgx - 26, mgy - 30, mgx + 26, mgy + 10], fill=(255, 255, 255))
    d.polygon([(mgx - 26, mgy - 2), (mgx + 26, mgy - 2), (mgx + 26, mgy + 22),
               (mgx + 13, mgy + 12), (mgx, mgy + 22), (mgx - 13, mgy + 12),
               (mgx - 26, mgy + 22)], fill=(255, 255, 255))
    d.ellipse([mgx - 14, mgy - 16, mgx - 4, mgy - 2], fill=(20, 0, 40))
    d.ellipse([mgx + 4, mgy - 16, mgx + 14, mgy - 2], fill=(20, 0, 40))
    f = fit_font(d, "make.fun", 560, 72)
    d.text((mgx + 40, mgy), "make.fun", font=f, fill=(255, 255, 255),
           anchor="lm", stroke_width=3, stroke_fill=(20, 0, 40))

    img.convert("RGB").save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
