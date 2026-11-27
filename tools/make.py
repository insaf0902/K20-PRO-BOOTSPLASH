import sys, math
from PIL import Image, ImageDraw, ImageFont
src, rrmask, out = sys.argv[1:4]
W,H = 1080,2340
import os
F=os.environ.get('FONT_DIR','/usr/share/fonts/opentype/inter/').rstrip('/')+'/'
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

def spaced(text, font, sp, y):
    ws=[font.getlength(ch) for ch in text]; tw=sum(ws)+sp*(len(text)-1)
    mk=Image.new('L',(W,H),0); d=ImageDraw.Draw(mk); x=(W-tw)/2
    for ch,w in zip(text,ws): d.text((x,y),ch,font=font,fill=255); x+=w+sp
    return mk

# REDMI K20 PRO in bold
mk = spaced("REDMI K20 PRO", ImageFont.truetype(F+'Inter-Bold.otf',54), 10, 2045)
c.paste(silver(mk,250,165),(0,0),mk)

# "Powered by android" with bugdroid head (Android robot, CC BY 3.0, Google)
def bugdroid(h):
    S4=4; R=h*S4; img=Image.new('L',(int(R*2.0),int(R*1.35)),0); d=ImageDraw.Draw(img)
    cx, base = img.width/2, img.height-1
    r = R*0.9
    d.pieslice([cx-r, base-r, cx+r, base+r], 180, 360, fill=255)           # head
    for s in (-1,1):                                                       # antennae
        x0=cx+s*r*0.45; y0=base-r*0.80
        x1=x0+s*r*0.28; y1=y0-r*0.42
        d.line([x0,y0,x1,y1], fill=255, width=int(R*0.09)); w=R*0.045
        d.ellipse([x1-w,y1-w,x1+w,y1+w], fill=255)
        ex=cx+s*r*0.42; ey=base-r*0.38; er=r*0.09                           # eyes
        d.ellipse([ex-er,ey-er,ex+er,ey+er], fill=0)
    img=img.crop(img.getbbox())
    return img.resize((img.width//S4, img.height//S4), Image.LANCZOS)

# "POWERED BY ANDROID" in spaced caps, robot head in front
light = ImageFont.truetype(F+'Inter-Regular.otf',28)
semi  = ImageFont.truetype(F+'Inter-SemiBold.otf',28)
sp = 7
parts = [("POWERED BY ", light, 175), ("ANDROID", semi, 230)]
head = bugdroid(22)
def plen(t,f): return sum(f.getlength(ch) for ch in t)+sp*len(t)
total = head.width + 16 + sum(plen(t,f) for t,f,_ in parts) - sp
x = (W-total)/2; y = 2165
asc = light.getmetrics()[0]
capH = light.getbbox("H")[3]-light.getbbox("H")[1]
c.paste((61,220,132), (int(x), int(y+asc-head.height)), head)
x += head.width + 16
d = ImageDraw.Draw(c)
for t,f,v in parts:
    for ch in t:
        d.text((x,y),ch,font=f,fill=(v,v,v)); x += f.getlength(ch)+sp
c.save(out)
