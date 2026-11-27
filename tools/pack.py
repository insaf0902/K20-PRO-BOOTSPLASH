import sys, io, struct
from PIL import Image
orig, png, out = sys.argv[1:4]
d = bytearray(open(orig,'rb').read())
im = Image.open(png).convert('RGB')
im = im.point(lambda v: 0 if v<=3 else v)  # make near-black background pure black
b = io.BytesIO(); im.save(b,'BMP'); bmp = b.getvalue()
hdr = d[0x4000:0x4000+8+4*8]; assert hdr[:8]==b'LOGO!!!!'
slots = struct.unpack('<8I', hdr[8:40])
for n in (0,2):  # slots 1 and 3
    off, ln = slots[2*n]*4096, slots[2*n+1]*4096
    old = d[off:off+ln]; assert old[:2]==b'BM' and struct.unpack('<I',old[2:6])[0]==len(bmp), 'size mismatch'
    assert old[10:14]==bmp[10:14] and old[18:30]==bmp[18:30]
    d[off:off+len(bmp)] = bmp
open(out,'wb').write(d); print('ok', len(d), len(bmp))
