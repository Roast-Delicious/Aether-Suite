# Navy vignette over the outer edge of the face, to hide the 3D model's square
# edges. Applied to the user's in-game test screenshot (1.342 px per frame unit).
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
K = 1.342
NAVY = np.array((19, 40, 74), np.float32)
CRESTS = [("Your frame", 938.5, 1204, 80), ("Target", 1621.5, 1204, 80), ("Pet", 998.4, 1329, 58), ("Target of target", 1562.5, 1329, 58)]
def vig(x, y, S, fade):
    inner = S - (14 if S > 60 else 10); rf = (inner - 2) / 2
    h = S / 2 ** 0.5 / 2                                   # the model square's half side
    r = S / 2 * K + 6
    box = (round(x - r), round(y - r), round(x + r), round(y + r))
    c = np.array(im.crop(box)).astype(np.float32)
    H, W = c.shape[:2]
    yy, xx = (np.mgrid[0:H, 0:W] + 0.5)
    d = np.hypot(xx - (x - box[0]), yy - (y - box[1])) / K   # units
    a = np.clip((d - (h - fade)) / fade, 0, 1); a = a * a * (3 - 2 * a)
    a = a * np.clip(rf + 0.5 - d, 0, 1)                       # only inside the face circle
    res = c * (1 - a[..., None]) + NAVY * a[..., None]
    if RIM:                                                  # solid dark band between the gold and blue rings
        DARK = np.array((11, 13, 18), np.float32)
        band = np.clip(d - (rf - 0.5), 0, 1) * np.clip((S / 2 - 2.5) - d, 0, 1)
        res = res * (1 - band[..., None]) + DARK * band[..., None]
    # what the game draws over the band: the gold ring, the level badge (6 o'clock),
    # the medallion or happiness face (3 o'clock, or 9 on the mirrored frames)
    gold = (c[..., 0] > 110) & (c[..., 1] > 80) & (c[..., 2] < 90) & (c[..., 0] - c[..., 2] > 70)
    cx0, cy0 = x - box[0], y - box[1]
    br = (12 if S > 60 else 10) * K
    keep = gold.copy()
    for ox, oy in [(0, (S / 2 - 1) * K), ((S / 2 - 1) * K, 0), (-(S / 2 - 1) * K, 0)]:
        keep |= np.hypot(xx - (cx0 + ox), yy - (cy0 + oy)) <= br
    keep &= d > rf - 1
    res[keep] = c[keep]
    return Image.fromarray(c.astype(np.uint8)), Image.fromarray(res.clip(0, 255).astype(np.uint8))
RIM = True
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 20)
Z = 4
rows = []
for label, x, y, S in CRESTS:
    b, a = vig(x, y, S, 4)
    rows.append((label, b, a))
cw = max(r[1].width for r in rows) * Z
sheet = Image.new("RGB", (220 + 2 * (cw + 20) + 2 * (rows[0][1].width + 20), 40 + sum(r[1].height * Z + 20 for r in rows)), (20, 22, 28))
d = ImageDraw.Draw(sheet)
cols = ["Now", "Fixed", "Now, zoom x4", "Fixed, zoom x4"]
xs = [220, 220 + rows[0][1].width + 20, 220 + 2 * (rows[0][1].width + 20), 220 + 2 * (rows[0][1].width + 20) + cw + 20]
for c, x in zip(cols, xs): d.text((x, 8), c, font=font, fill=(255, 209, 0))
y = 40
for label, b, a in rows:
    d.text((10, y + 20), label, font=font, fill=(255, 255, 255))
    for img, x in zip([b, a, b.resize((b.width * Z, b.height * Z), Image.NEAREST), a.resize((a.width * Z, a.height * Z), Image.NEAREST)], xs):
        sheet.paste(img, (x, y))
    y += b.height * Z + 20
sheet.save(out); print(sheet.size)
