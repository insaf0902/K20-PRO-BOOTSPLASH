"""Compose the 1080x2340 boot picture (red Resurrection Remix theme).

usage: make.py SOURCE_PNG SWOOSH_MASK_PNG OUT_PNG

SOURCE_PNG  original artwork; only the #GETRESURRECTED tagline is taken from it
SWOOSH_MASK white-on-black render of assets/rr_swoosh.svg (tools/render_svg.js)

Layout: red swoosh on a dark disc with a red halo, centred on the screen;
#GETRESURRECTED and an unlocked padlock at the bottom. No glow touches the text.
"""
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

src, rrmask, out = sys.argv[1:4]
W, H = 1080, 2340

# palette
RED_HI = (255, 70, 60)      # top-right of the swoosh
RED_LO = (170, 0, 28)       # bottom-left of the swoosh
GLOW = (255, 20, 30)
DISC = (10, 2, 4)

CX, CY = W // 2, H // 2     # logo sits in the exact centre of the screen
R = 290                     # disc radius
TAG_Y = 2010                # top of #GETRESURRECTED
LOCK_Y = 2112               # top of the padlock


def lin_gradient(size, c0, c1):
    """Diagonal gradient: c0 at the top-right corner, c1 at the bottom-left."""
    w, h = size
    g = Image.new('RGB', size)
    px = g.load()
    span = w + h
    for y in range(h):
        for x in range(w):
            t = (x + (h - y)) / span
            px[x, y] = tuple(int(c1[i] + (c0[i] - c1[i]) * t) for i in range(3))
    return g


def add_glow(canvas, mask, color, radius, strength=1.0):
    """Additive blurred glow of `mask` in `color`."""
    blur = mask.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        blur = blur.point(lambda v: min(255, int(v * strength)))
    glow = ImageChops.multiply(Image.new('RGB', canvas.size, color), Image.merge('RGB', [blur] * 3))
    return ImageChops.add(canvas, glow)


def circle(r, width=0):
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    if width:
        d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=255, width=width)
    else:
        d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=255)
    return m


def padlock(h, s=4):
    """Open padlock, white on black, height h (drawn s-times larger, then downscaled).
    Returns (image, x offset of the lock body's centre inside the image)."""
    H4 = h * s
    w = int(H4 * 0.80)
    img = Image.new('L', (int(w * 1.35), H4), 0)
    d = ImageDraw.Draw(img)
    body_top = int(H4 * 0.45)
    d.rounded_rectangle([0, body_top, w, H4 - 1], radius=int(H4 * 0.09), fill=255)
    # shackle: lifted and swung open to the right
    sw = int(H4 * 0.11)
    sx0, sx1 = int(w * 0.18), int(w * 0.82)
    lift = int(H4 * 0.10)
    ox = int(w * 0.38)
    d.arc([sx0 + ox, 0, sx1 + ox, sx1 - sx0], 180, 360, fill=255, width=sw)
    mid = (sx1 - sx0) // 2
    d.rectangle([sx1 + ox - sw, mid, sx1 + ox, body_top + lift], fill=255)
    d.rectangle([sx0 + ox, mid, sx0 + ox + sw, body_top - lift], fill=255)
    # keyhole
    kx, ky = w // 2, body_top + int((H4 - body_top) * 0.42)
    kr = int(H4 * 0.075)
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=0)
    d.polygon([(kx - kr * 0.55, ky), (kx + kr * 0.55, ky), (kx + kr * 0.8, ky + kr * 2.6),
               (kx - kr * 0.8, ky + kr * 2.6)], fill=0)
    bb = img.getbbox()
    img = img.crop(bb)
    return img.resize((img.width // s, img.height // s), Image.LANCZOS), (w / 2 - bb[0]) / s


c = Image.new('RGB', (W, H), 0)

# 1. red splash: soft halo around the disc, a little stronger to the lower left
c = add_glow(c, circle(R), GLOW, 55, 0.55)
c = add_glow(c, circle(R), (110, 0, 18), 85, 0.5)
spot = Image.new('L', (W, H), 0)
ImageDraw.Draw(spot).ellipse([CX - R - 30, CY - 60, CX - 20, CY + R - 30], fill=255)
c = add_glow(c, spot, GLOW, 80, 0.45)

# dark disc with a faint red rim
c.paste(DISC, (0, 0), circle(R).filter(ImageFilter.GaussianBlur(2)))
rim = circle(R - 1, width=2).filter(ImageFilter.GaussianBlur(1)).point(lambda v: v * 45 // 100)
c.paste(RED_LO, (0, 0), rim)

# 2. swoosh with red gradient + its own glow, optically centred in the disc
m = Image.open(rrmask).convert('L')
m = m.crop(m.getbbox())
lw = 380
lh = round(m.height * lw / m.width)
m = m.resize((lw, lh), Image.LANCZOS)
# centre by the shape's centre of mass, not its bounding box
hist_x = [sum(m.getpixel((x, y)) for y in range(0, lh, 2)) for x in range(lw)]
hist_y = [sum(m.getpixel((x, y)) for x in range(0, lw, 2)) for y in range(lh)]
mx = sum(i * v for i, v in enumerate(hist_x)) / sum(hist_x)
my = sum(i * v for i, v in enumerate(hist_y)) / sum(hist_y)
lx, ly = round(CX - mx), round(CY - my)
logo = Image.new('L', (W, H), 0)
logo.paste(m, (lx, ly))
c = add_glow(c, logo, GLOW, 28, 0.7)
grad = Image.new('RGB', (W, H))
grad.paste(lin_gradient((lw, lh), RED_HI, RED_LO), (lx, ly))
c.paste(grad, (0, 0), logo)

# 3. #GETRESURRECTED at the bottom (original pixels, no glow behind it)
im = Image.open(src).convert('RGB')
tag = im.crop((0, 1003, im.width, 1070))
tag = tag.crop(tag.convert('L').point(lambda v: 255 if v > 12 else 0).getbbox())
sc = W / im.width * 0.62
tag = tag.resize((round(tag.width * sc), round(tag.height * sc)), Image.LANCZOS)
tag_layer = Image.new('RGB', (W, H), 0)
tag_layer.paste(tag, ((W - tag.width) // 2, TAG_Y))
c = ImageChops.lighter(c, tag_layer)

# 4. unlocked padlock, lock body centred under the tagline
lock, body_cx = padlock(60)
lock_mask = Image.new('L', (W, H), 0)
lock_mask.paste(lock, (round(W / 2 - body_cx), LOCK_Y))
c = add_glow(c, lock_mask, GLOW, 12, 0.6)
c.paste(RED_HI, (0, 0), lock_mask)

c.save(out)
