# The red hit flash (halo art, tinted) on the user's pet crest, at 0, 0.1, 0.2 and 0.3 s.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
K = 1.342; cx, cy, S = 998.4, 1329, 58
HS = S + 34
halo = Image.open('/home/claude/brand/AetherFrames/Media/halo58.tga').convert('RGBA')
size = round(HS * K)
a = np.array(halo.resize((size, size), Image.LANCZOS)).astype(np.float32)[..., 3] / 255
r = size // 2 + 4
box = (round(cx - r), round(cy - r), round(cx + r), round(cy + r))
base = np.array(im.crop(box)).astype(np.float32)
off = (base.shape[0] - size) // 2
RED = np.array((255, 41, 26), np.float32)
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 20)
tiles = []
for t in (0, 0.1, 0.2, 0.3):
    k = (1 - t / 0.3) ** 2 if t < 0.3 else 0
    img = base.copy()
    al = np.zeros(img.shape[:2], np.float32); al[off:off + size, off:off + size] = a * k
    # the halo sits under the crest: only where the crest is see-through (outside the blue ring)
    yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    outside = np.hypot(xx - r, yy - r) > S / 2 * K - 1
    al *= outside
    img = img * (1 - al[..., None]) + RED * al[..., None]
    tiles.append((t, Image.fromarray(img.clip(0, 255).astype(np.uint8))))
Z = 3
w = tiles[0][1].width * Z
sheet = Image.new("RGB", (len(tiles) * (w + 20) + 10, w + 50), (20, 22, 28)); d = ImageDraw.Draw(sheet)
for i, (t, tile) in enumerate(tiles):
    d.text((10 + i * (w + 20), 8), "%.1f s" % t, font=font, fill=(255, 209, 0))
    sheet.paste(tile.resize((w, w), Image.NEAREST), (10 + i * (w + 20), 40))
sheet.save(out); print(sheet.size)
