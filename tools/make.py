"""Compose the 1080x2340 boot picture (red Resurrection Remix theme).

usage: make.py SOURCE_PNG SWOOSH_MASK_PNG OUT_PNG

SOURCE_PNG  original artwork; only the #GETRESURRECTED tagline is taken from it
SWOOSH_MASK white-on-black render of assets/rr_swoosh.svg (tools/render_svg.js)
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

src, rrmask, out = sys.argv[1:4]
W, H = 1080, 2340
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'assets', 'fonts')
INTER = os.environ.get('FONT_DIR', '/usr/share/fonts/opentype/inter/').rstrip('/') + '/'

# palette
RED_HI = (255, 70, 60)      # top-right of the swoosh
RED_LO = (170, 0, 28)       # bottom-left of the swoosh
GLOW = (255, 20, 30)
DISC = (10, 2, 4)

CX, CY = W // 2, 1110       # centre of the logo


def lin_gradient(size, c0, c1, angle_dir=(1, -1)):
    """Diagonal gradient: c0 at the end pointed to by angle_dir, c1 at the other."""
    w, h = size
    g = Image.new('RGB', size)
    px = g.load()
    dx, dy = angle_dir
    vals = [x * dx + y * dy for x in (0, w) for y in (0, h)]
    lo, hi = min(vals), max(vals)
    for y in range(h):
        for x in range(w):
            t = ((x * dx + y * dy) - lo) / (hi - lo)
            px[x, y] = tuple(int(c1[i] + (c0[i] - c1[i]) * t) for i in range(3))
    return g


def v_gradient(mask, top, bot):
    bb = mask.getbbox()
    g = Image.new('RGB', mask.size)
    d = ImageDraw.Draw(g)
    for y in range(bb[1], bb[3] + 1):
        t = (y - bb[1]) / max(1, bb[3] - bb[1])
        d.line([(0, y), (mask.width, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g


def add_glow(canvas, mask, color, radius, strength=1.0):
    blur = mask.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        blur = blur.point(lambda v: min(255, int(v * strength)))
    layer = Image.new('RGB', canvas.size, color)
    # additive blend so overlapping glows brighten instead of overwrite
    glow_rgb = ImageChops.multiply(layer, Image.merge('RGB', [blur] * 3))
    return ImageChops.add(canvas, glow_rgb)


def spaced_mask(text, font, sp, y, x_center=W / 2):
    ws = [font.getlength(ch) for ch in text]
    tw = sum(ws) + sp * (len(text) - 1)
    mk = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(mk)
    x = x_center - tw / 2
    for ch, w in zip(text, ws):
        d.text((x, y), ch, font=font, fill=255)
        x += w + sp
    return mk, tw


c = Image.new('RGB', (W, H), 0)

# 1. red splash: soft halo around a dark disc, brighter towards the lower left
R = 290
ring = Image.new('L', (W, H), 0)
ImageDraw.Draw(ring).ellipse([CX - R, CY - R, CX + R, CY + R], fill=255)
c = add_glow(c, ring, GLOW, 55, 0.55)
c = add_glow(c, ring, (110, 0, 18), 140, 0.55)
spot = Image.new('L', (W, H), 0)
ImageDraw.Draw(spot).ellipse([CX - R - 40, CY - 40, CX + 10, CY + R + 40], fill=255)
c = add_glow(c, spot, GLOW, 100, 0.5)
disc = Image.new('L', (W, H), 0)
ImageDraw.Draw(disc).ellipse([CX - R, CY - R, CX + R, CY + R], fill=255)
disc = disc.filter(ImageFilter.GaussianBlur(3))
c.paste(DISC, (0, 0), disc)

# 2. swoosh logo with red gradient + inner glow
m = Image.open(rrmask).convert('L')
m = m.crop(m.getbbox())
lw = 380
lh = round(m.height * lw / m.width)
m = m.resize((lw, lh), Image.LANCZOS)
logo = Image.new('L', (W, H), 0)
logo.paste(m, (CX - lw // 2 + 8, CY - lh // 2))
c = add_glow(c, logo, GLOW, 28, 0.7)
grad = Image.new('RGB', (W, H))
grad.paste(lin_gradient((lw, lh), RED_HI, RED_LO), (CX - lw // 2 + 8, CY - lh // 2))
c.paste(grad, (0, 0), logo)

# 3. #GETRESURRECTED, original pixels, scaled small, under the disc
im = Image.open(src).convert('RGB')
tag = im.crop((0, 1003, im.width, 1070))
tag = tag.crop(tag.convert('L').point(lambda v: 255 if v > 12 else 0).getbbox())
sc = W / im.width * 0.60
tag = tag.resize((round(tag.width * sc), round(tag.height * sc)), Image.LANCZOS)
tag_layer = Image.new('RGB', (W, H), 0)
tag_layer.paste(tag, ((W - tag.width) // 2, CY + R + 70))
c = ImageChops.lighter(c, tag_layer)   # no dark box over the glow

# 4. REDMI K20 PRO in Road Rage
rr_font = ImageFont.truetype(os.path.join(FONTS, 'RoadRage-Regular.ttf'), 96)
mk, _ = spaced_mask("REDMI K20 PRO", rr_font, 6, 1985)
c.paste(v_gradient(mk, (255, 255, 255), (200, 200, 200)), (0, 0), mk)


# 5. bootloader-unlocked badge: open padlock + text
def padlock(h, s=4):
    """Open padlock, white on black, height h (drawn at s-times then downscaled)."""
    H4 = h * s
    w = int(H4 * 0.80)
    img = Image.new('L', (int(w * 1.35), H4), 0)
    d = ImageDraw.Draw(img)
    body_top = int(H4 * 0.45)
    d.rounded_rectangle([0, body_top, w, H4 - 1], radius=int(H4 * 0.09), fill=255)
    # shackle: arc lifted and swung open to the right
    sw = int(H4 * 0.11)
    sx0, sx1 = int(w * 0.18), int(w * 0.82)
    lift = int(H4 * 0.10)
    ox = int(w * 0.38)
    top = 0
    d.arc([sx0 + ox, top, sx1 + ox, top + (sx1 - sx0)], 180, 360, fill=255, width=sw)
    mid = top + (sx1 - sx0) // 2
    d.rectangle([sx1 + ox - sw, mid, sx1 + ox, body_top + lift], fill=255)   # right leg (free)
    d.rectangle([sx0 + ox, mid, sx0 + ox + sw, body_top - lift], fill=255)   # left leg, out of the body
    # keyhole
    kx, ky = w // 2, body_top + int((H4 - body_top) * 0.42)
    kr = int(H4 * 0.075)
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=0)
    d.polygon([(kx - kr * 0.55, ky), (kx + kr * 0.55, ky), (kx + kr * 0.8, ky + kr * 2.6),
               (kx - kr * 0.8, ky + kr * 2.6)], fill=0)
    img = img.crop(img.getbbox())
    return img.resize((img.width // s, img.height // s), Image.LANCZOS)


badge_font = ImageFont.truetype(INTER + 'Inter-SemiBold.otf', 28)
lock = padlock(46)
text = "BOOTLOADER UNLOCKED"
sp = 7
tw = sum(badge_font.getlength(ch) for ch in text) + sp * (len(text) - 1)
gap = 18
total = lock.width + gap + tw
x0 = (W - total) / 2
y = 2140
asc = badge_font.getmetrics()[0]
cap = badge_font.getbbox("H")
cap_h = cap[3] - cap[1]
lock_y = int(y + asc - lock.height + 2)
lock_mask = Image.new('L', (W, H), 0)
lock_mask.paste(lock, (int(x0), lock_y))
c = add_glow(c, lock_mask, GLOW, 10, 0.6)
c.paste(RED_HI, (0, 0), lock_mask)
tm, _ = spaced_mask(text, badge_font, sp, y, x_center=x0 + lock.width + gap + tw / 2)
c.paste((190, 190, 190), (0, 0), tm)

c.save(out)
