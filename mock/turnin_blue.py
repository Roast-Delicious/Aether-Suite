# Mockup: "Ready for turn-in" in blue instead of green (quest titles keep
# their level colors). Recolors the user's tracker screenshot.
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
src = Image.open(sys.argv[1]).convert('RGB'); OUT = sys.argv[2]
a = np.array(src).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
sat = g - np.maximum(r, b)
green = sat > 25
# the "Ready for turn-in" lines sit under each title, 57 px apart in this
# screenshot (the 7th quest isn't complete); titles keep their level colors
m = np.zeros_like(green)
for k in range(10):
    if k == 6: continue
    yc = 159 + 57 * k
    m[yc - 11:yc + 11] = green[yc - 11:yc + 11]
peak = np.array([np.median(c[(sat > 90) & m]) for c in (r, g, b)])
alpha = np.clip(sat / (peak[1] - max(peak[0], peak[2])), 0, 1)[..., None]
opts = {'Now': None, 'A  baby blue': (137, 207, 240), 'B  Aether sky blue': (115, 191, 255),
        'C  pale ice blue': (185, 225, 255)}
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
tiles = []
for k, t in opts.items():
    im = a if t is None else np.clip(a + alpha * (np.array(t) - peak) * m[..., None], 0, 255)
    img = Image.fromarray(im.astype('uint8')).crop((40, 60, 462, 700))
    c = Image.new('RGB', (img.width, img.height + 40), (20, 20, 24))
    ImageDraw.Draw(c).text((6, 8), k, font=F, fill=(255, 176, 0)); c.paste(img, (0, 40)); tiles.append(c)
out = Image.new('RGB', (tiles[0].width * 4 + 60, tiles[0].height), (20, 20, 24))
for i, t in enumerate(tiles): out.paste(t, (i * (t.width + 20), 0))
out.save(OUT)
