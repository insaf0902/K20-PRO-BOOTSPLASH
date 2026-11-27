import sys, math
from PIL import Image, ImageDraw, ImageFont
src, rrmask, out = sys.argv[1:4]
W,H = 1080,2340
import os
im = Image.open(src).convert('RGB')
# cut out #GETRESURRECTED (source rows 1009-1063) before erasing
tag = im.crop((0,1003,im.width,1070))
d0 = ImageDraw.Draw(im)
d0.rectangle([0,712,im.width,892], fill=0)     # old slanted mark
d0.rectangle([0,1003,im.width,1070], fill=0)   # old tagline
nh = round(im.height*W/im.width); oy=(H-nh)//2
sc = W/im.width
im = im.resize((W,nh), Image.LANCZOS)
c = Image.new('RGB',(W,H),0); c.paste(im,(0,oy))
mark_cy = oy + (718+886)/2*sc

def silver(mask, top_v=250, bot_v=140):
    bb = mask.getbbox(); g = Image.new('RGB', mask.size); d = ImageDraw.Draw(g)
    for y in range(bb[1], bb[3]+1):
        t=(y-bb[1])/max(1,bb[3]-bb[1]); v=int(top_v-(top_v-bot_v)*t)
        d.line([(0,y),(mask.width,y)], fill=(v,v,v))
    return g

# RR swoosh logo (unchanged from v2)
m = Image.open(rrmask).convert('L'); m = m.crop(m.getbbox())
lw = 340; lh = round(m.height*lw/m.width); m = m.resize((lw,lh), Image.LANCZOS)
full = Image.new('L',(W,H),0); ly=round(mark_cy-lh/2); full.paste(m,((W-lw)//2, ly))
c.paste(silver(full),(0,0),full)

# smaller #GETRESURRECTED: original pixels scaled to 60%
TS = 0.60
tw_, th_ = round(tag.width*sc*TS), round(tag.height*sc*TS)
t = tag.resize((tw_,th_), Image.LANCZOS)
ty = ly + lh + 70
c.paste(t, ((W-tw_)//2, ty))


FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'fonts')
WHITE = (240, 240, 240)
GREEN = (61, 220, 132)   # Android green


def bugdroid(h, s=4):
    """Android robot head (CC BY 3.0, Google): half-disc, antennae, eyes. Height ~h px."""
    R = h * s
    img = Image.new('L', (int(R * 2.0), int(R * 1.35)), 0)
    d = ImageDraw.Draw(img)
    cx, base = img.width / 2, img.height - 1
    r = R * 0.9
    d.pieslice([cx - r, base - r, cx + r, base + r], 180, 360, fill=255)
    for side in (-1, 1):
        x0 = cx + side * r * 0.45; y0 = base - r * 0.80
        x1 = x0 + side * r * 0.28; y1 = y0 - r * 0.42
        d.line([x0, y0, x1, y1], fill=255, width=int(R * 0.09))
        w = R * 0.045
        d.ellipse([x1 - w, y1 - w, x1 + w, y1 + w], fill=255)
        ex = cx + side * r * 0.42; ey = base - r * 0.38; er = r * 0.09
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=0)
    img = img.crop(img.getbbox())
    return img.resize((img.width // s, img.height // s), Image.LANCZOS)


def unlock_icon(h, stroke, s=4):
    """Outline open padlock (like the stock Xiaomi 'unlocked' mark). Height h px."""
    H4, st = h * s, int(stroke * s)
    bw = int(H4 * 0.78)                       # body width
    img = Image.new('L', (bw + st * 2, H4 + st), 0)
    d = ImageDraw.Draw(img)
    ox = st // 2
    body_top = int(H4 * 0.47)
    d.rounded_rectangle([ox, body_top, ox + bw, H4], radius=int(H4 * 0.10), outline=255, width=st)
    # shackle: right leg goes into the body, left leg lifted out (open)
    sx0, sx1 = ox + int(bw * 0.20), ox + int(bw * 0.80)
    top = int(H4 * 0.02)
    d.arc([sx0, top, sx1, top + (sx1 - sx0)], 180, 360, fill=255, width=st)
    mid = top + (sx1 - sx0) // 2
    d.rectangle([sx1 - st, mid, sx1, body_top], fill=255)                     # right leg
    d.rectangle([sx0, mid, sx0 + st, mid + int(H4 * 0.08)], fill=255)          # left leg, short = open
    img = img.crop(img.getbbox())
    return img.resize((img.width // s, img.height // s), Image.LANCZOS)


d = ImageDraw.Draw(c)

# unlocked mark at the top centre, like the stock Redmi unlocked boot screen
lock = unlock_icon(46, 3.2)
c.paste((225, 225, 225), ((W - lock.width) // 2, 105), lock)

# "Powered by / android" lockup with the robot head, as on stock Android boot screens
f_small = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Medium.ttf'), 30)
f_big = ImageFont.truetype(os.path.join(FONTS, 'Poppins-SemiBold.ttf'), 72)
word = "android"
bb_word = f_big.getbbox(word)                 # (l, t, r, b) relative to draw origin
word_w = bb_word[2] - bb_word[0]
asc_top = bb_word[1]                          # top of the 'd' ascender
x_h = f_big.getbbox("o")
xh_top = x_h[1]
robot = bugdroid(48)
gap = 12
total = word_w + gap + robot.width
x0 = (W - total) / 2 - bb_word[0]
base_y = 2215                                 # baseline of "android"
f_asc = f_big.getmetrics()[0]
wy = base_y - f_asc
d.text((x0, wy), word, font=f_big, fill=WHITE)
# "Powered by" left-aligned with "android", sitting just above it
pb = f_small.getbbox("Powered by")
py = wy + asc_top - (pb[3]) - 6
d.text((x0 + bb_word[0] - pb[0], py), "Powered by", font=f_small, fill=WHITE)
# robot head on the same line as "android": bottom on the text baseline
rx = int(x0 + bb_word[2] + gap)
ry = int(base_y - robot.height)
c.paste(GREEN, (rx, ry), robot)

c.save(out)
