# Mockup: shorter tab strip in AetherChat, built from the user's screenshot.
from PIL import Image, ImageDraw, ImageFont
import sys
SRC = sys.argv[1]; OUT = sys.argv[2]
src = Image.open(SRC).convert('RGB'); W, H = src.size
BG = (28, 21, 14)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
def rows(y0, y1): return src.crop((0, y0, W, y1))
def ghost(im, y0, y1):
    # reclaimed space: older chat would show here (clipped like real chat)
    layer = im.crop((0, y0, W, y1)); d = ImageDraw.Draw(layer)
    y = (y1 - y0) - 25
    while y > -25:
        d.text((24, y + 2), "(older chat line)", font=F, fill=(110, 95, 80)); y -= 25
    im.paste(layer, (0, y0))
def build(kind):
    im = src.copy(); d = ImageDraw.Draw(im)
    text = rows(84, H)                     # chat text + bottom edge, stays anchored at the bottom
    if kind == 'now': return im
    if kind == 'A':                        # compact strip: labels right under the edge
        strip = [rows(30, 36), rows(56, 84)]
    elif kind == 'B':                      # thinner still: no gap under the underline
        strip = [rows(30, 36), rows(57, 78), rows(82, 84)]
    elif kind == 'C':                      # tabs only on mouseover
        strip = [rows(30, 36), rows(82, 84)]
    im.paste(rows(0, 30), (0, 0))
    y = 30
    for s in strip: im.paste(s, (0, y)); y += s.height
    top_text = H - text.height
    # fill the gap (keeps the side edges and corners)
    gap = src.crop((0, 50, W, 51)).resize((W, top_text - y))
    im.paste(gap, (0, y)); ghost(im, y + 1, top_text)
    im.paste(text, (0, top_text))
    return im
names = {'now': 'Now', 'A': 'A  compact strip', 'B': 'B  slim strip', 'C': 'C  tabs on mouseover'}
L = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
tiles = []
for k in names:
    t = build(k)
    z = t.resize((W * 2 // 1, H * 2 // 1), Image.LANCZOS)
    c = Image.new('RGB', (z.width, z.height + 34), (20, 20, 24))
    ImageDraw.Draw(c).text((6, 6), names[k], font=L, fill=(255, 176, 0)); c.paste(z, (0, 34)); tiles.append(c)
out = Image.new('RGB', (tiles[0].width * 2 + 20, (tiles[0].height + 16) * 2), (20, 20, 24))
for i, t in enumerate(tiles): out.paste(t, ((i % 2) * (t.width + 20), (i // 2) * (t.height + 16)))
out.save(OUT)
