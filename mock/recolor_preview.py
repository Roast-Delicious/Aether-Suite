# Preview: the Aether gold text (255, 209, 0) shifted to the deposit slot's color
# (37% orange: 255, 176, 0), in the user's real Hub and Pack screenshot. Only
# window interiors are touched (not the window chevrons), and item icons are skipped.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
im = np.array(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W, _ = im.shape
R, G, B = im[..., 0], im[..., 1], im[..., 2]
# gold-ish text pixels: red high, blue low, green 70-92% of red
gold = (R > 90) & (B < 0.45 * R) & (G > 0.62 * R) & (G < 0.95 * R)
region = np.zeros((H, W), bool)
region[62:1135, 60:1105] = True          # AetherHub window interior
region[245:1212, 1172:1765] = True       # AetherPack window interior
for y0, y1 in [(358, 472), (514, 630), (670, 726), (768, 824), (865, 980), (1021, 1077)]:
    region[y0:y1, 1176:1762] = False     # item icon rows in the Pack
m = gold & region
out = im.copy()
k = 176 / 209                            # pull green down: gold -> amber, keeping the shading
out[..., 1] = np.where(m, G * k, G)
before = Image.fromarray(im.astype(np.uint8)); after = Image.fromarray(out.clip(0, 255).astype(np.uint8))
f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/ofl/firasans/FiraSans-Regular.ttf', 22)
crops = [(60, 62, 760, 700), (1172, 245, 1765, 700)]
pad = 16
rows = []
for c in crops:
    b, a = before.crop(c), after.crop(c)
    rows.append((b, a))
Wc = pad * 3 + max(r[0].width for r in rows) * 2
Hc = sum(r[0].height + 50 for r in rows) + pad
cv = Image.new('RGB', (Wc, Hc), (18, 20, 26)); d = ImageDraw.Draw(cv)
y = 8
for b, a in rows:
    d.text((pad, y), "Now: Aether gold", fill=(255, 209, 0), font=f)
    d.text((pad * 2 + b.width, y), "Matched to the deposit slot", fill=(255, 176, 0), font=f)
    cv.paste(b, (pad, y + 34)); cv.paste(a, (pad * 2 + b.width, y + 34))
    y += b.height + 50
cv.save(OUT); print(cv.size, int(m.sum()), "pixels recolored")
