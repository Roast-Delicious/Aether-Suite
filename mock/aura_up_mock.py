# Mockup: the aura/hawk row under the player capsule moved up by N UI units.
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
src = sys.argv[1]; out = sys.argv[2]
im = np.array(Image.open(src).convert('RGB'))
H, W, _ = im.shape
blue = (im[:, :, 2] > 200) & (im[:, :, 0] < 120) & (im[:, :, 1] > 120)
ys, xs = np.where(blue[100:200, 100:260]); ys += 100; xs += 100
cols = sorted(set(xs))
groups = []
for x in cols:
    if groups and x - groups[-1][-1] <= 3: groups[-1].append(x)
    else: groups.append([x])
boxes = []
for g in groups:
    sel = (xs >= g[0]) & (xs <= g[-1])
    boxes.append((g[0], ys[sel].min(), g[-1], ys[sel].max()))
print("icons:", boxes)
mask = np.zeros((H, W), np.uint8)
for (x0, y0, x1, y1) in boxes:
    mask[y0 - 1:y1 + 2, x0 - 1:x1 + 2] = 255
# the "60 m" timer text under the first icon: light/dark text pixels
x0, y0, x1, y1 = boxes[0]
sub = im[y1 + 1:y1 + 17, x0 - 5:x1 + 3].astype(int)
txt = ((sub.sum(2) < 200) | (sub.min(2) > 200)).astype(np.uint8) * 255
txt = cv2.dilate(txt, np.ones((3, 3), np.uint8))
mask[y1 + 1:y1 + 17, x0 - 5:x1 + 3] |= txt
PX = 1.34                     # screen px per frame unit (scale 1.17 on this screen)
fnt = ImageFont.load_default()
def shifted(units):
    d = int(round(units * PX))
    bg = cv2.inpaint(im, mask, 5, cv2.INPAINT_TELEA)
    outi = bg.copy()
    m = mask > 0
    yy, xx = np.where(m)
    outi[yy - d, xx] = im[yy, xx]
    return Image.fromarray(outi), d
panels = [("Now (11 units below)", Image.fromarray(im), 0)]
for u in [float(a) for a in sys.argv[3:]] or (3, 5):
    p, d = shifted(u)
    panels.append((f"Up {u:g} units ({d} px)", p, d))
# actual size + 3x zoom of the row area
crop = (20, 40, 290, 228)
cw, ch = crop[2] - crop[0], crop[3] - crop[1]
Z = 3
zw, zh = (130 - 0) , 0
pad = 16
colw = max(cw, 160 * Z)
canvas = Image.new('RGB', (pad + len(panels) * (colw + pad), 30 + ch + 30 + 80 * Z + pad), (18, 20, 26))
dr = ImageDraw.Draw(canvas)
for i, (label, p, d) in enumerate(panels):
    x = pad + i * (colw + pad)
    dr.text((x, 8), label, fill=(255, 210, 80), font=fnt)
    dr.text((x, 22 + ch + 4), "actual size  /  3x zoom below", fill=(150, 160, 180), font=fnt)
    canvas.paste(p.crop(crop), (x, 20))
    z = p.crop((95, 120, 95 + cw // 1 * 0 + 160, 120 + 80)).resize((160 * Z, 80 * Z), Image.NEAREST)
    canvas.paste(z, (x, 20 + ch + 24))
canvas.save(out)
print(canvas.size)
