# Guild & Communities crest options (user 16:52: the guild window had no
# icon). Flat gold glyphs like the other crests: A banner, B tabard,
# C shield. Drawn white on black (black = cut-out), tinted gold.
import math, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W, K = 255, 0
GOLD = (255, 176, 0)

def banner(d, n):
    # pole with a round finial, pennant with a swallowtail, round emblem cut-out
    px = n * .26
    d.rectangle([px - n*.03, n*.12, px + n*.03, n*.90], fill=W)
    d.ellipse([px - n*.065, n*.06, px + n*.065, n*.19], fill=W)
    d.rectangle([px, n*.20, n*.80, n*.25], fill=W)                 # crossbar
    x0, x1, y0, y1 = px + n*.07, n*.78, n*.25, n*.80
    d.polygon([(x0, y0), (x1, y0), (x1, y1), ((x0 + x1) / 2, y1 - n*.13), (x0, y1)], fill=W)
    cx, cy, r = (x0 + x1) / 2, n*.47, n*.10
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=K)
    r2 = n*.05
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=W)

def tabard(d, n):
    # shoulders, neck cut, long body, a stripe of emblem cut-outs
    cx = n / 2
    pts = [(cx - n*.36, n*.20), (cx - n*.12, n*.14), (cx + n*.12, n*.14), (cx + n*.36, n*.20),
           (cx + n*.30, n*.36), (cx + n*.22, n*.33), (cx + n*.22, n*.88), (cx - n*.22, n*.88),
           (cx - n*.22, n*.33), (cx - n*.30, n*.36)]
    d.polygon(pts, fill=W)
    d.pieslice([cx - n*.11, n*.04, cx + n*.11, n*.26], 0, 180, fill=K)   # neck
    d.rectangle([cx - n*.045, n*.30, cx + n*.045, n*.82], fill=K)        # center stripe
    r = n*.075
    d.ellipse([cx - r, n*.52 - r, cx + r, n*.52 + r], fill=K)
    r2 = n*.04
    d.ellipse([cx - r2, n*.52 - r2, cx + r2, n*.52 + r2], fill=W)

def shield(d, n):
    # heater shield, a cut-out border line and a chevron
    cx = n / 2
    def outline(s, top):
        pts = []
        for i in range(41):
            t = i / 40
            y = top + (n*.82 - top) * t
            w = s * (1 if t < .45 else math.cos((t - .45) / .55 * math.pi / 2) ** .8)
            pts.append((cx + w, y))
        return [(cx - s, top)] + [(cx + s, top)] + pts + [(2 * cx - x, y) for x, y in reversed(pts)]
    d.polygon(outline(n*.34, n*.12), fill=W)
    d.polygon(outline(n*.27, n*.18), fill=K)
    d.polygon(outline(n*.235, n*.21), fill=W)
    w = n*.06
    d.polygon([(cx - n*.20, n*.52), (cx, n*.36), (cx + n*.20, n*.52), (cx + n*.20, n*.52 + w * 1.6),
               (cx, n*.36 + w * 1.6), (cx - n*.20, n*.52 + w * 1.6)], fill=K)

def glyph(fn, size, S=8):
    N = size * S
    im = Image.new('L', (N, N), 0); d = ImageDraw.Draw(im)
    fn(d, N)
    a = im.resize((size, size), Image.LANCZOS)
    g = Image.new('RGBA', (size, size), GOLD + (0,)); g.putalpha(a)
    return g

shot = Image.open(sys.argv[1]).convert('RGBA')
crop = shot.crop((0, 20, 460, 260))            # crest, title strip and the list corner
cx, cy = 62, 86 - 20                            # crest center in the crop
opts = [("A  Banner", banner), ("B  Tabard", tabard), ("C  Shield", shield)]
Z = 2
tiles = []
for label, fn in opts:
    t = crop.copy()
    # plain navy disc (what our crest shows), then the glyph, as in game
    dd = ImageDraw.Draw(t)
    r = 44
    dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(19, 40, 74, 255))
    gsz = 56
    t.alpha_composite(glyph(fn, gsz), (cx - gsz // 2, cy - gsz // 2))
    t = t.resize((t.width * Z, t.height * Z), Image.LANCZOS)
    tiles.append((label, t))
pad, lab = 16, 46
big = [glyph(fn, 200) for _, fn in opts]
Wd = tiles[0][1].width
H = lab + tiles[0][1].height + pad + 220 + pad
out = Image.new('RGBA', (Wd * 3 + pad * 4, H), (14, 18, 28, 255))
d = ImageDraw.Draw(out)
try: f = ImageFont.truetype('/home/claude/aether/AetherHub/Media/Fonts/FiraSans-SemiBold.ttf', 28)
except Exception: f = ImageFont.load_default()
for i, (label, t) in enumerate(tiles):
    x = pad + i * (Wd + pad)
    d.text((x, 8), label, font=f, fill=GOLD)
    out.alpha_composite(t, (x, lab))
    # the glyph large on navy, to judge the shape
    bx, by = x + (Wd - 220) // 2, lab + t.height + pad
    d.rounded_rectangle([bx, by, bx + 220, by + 220], 12, fill=(19, 40, 74, 255), outline=(77, 166, 255, 255), width=2)
    out.alpha_composite(big[i], (bx + 10, by + 10))
out.convert('RGB').save(sys.argv[2])
print("ok", out.size)
