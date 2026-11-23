# Glow backdrops behind portraits, from the user's screenshot (1:1, 1.345 px/unit).
# The black is keyed out of the 2D portrait to stand in for a 3D model (which has
# no background); deep-black shadows in the fur key out too, so it's approximate.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
K = 1.345
CRESTS = {"pet": (167.5, 244, 58), "target": (792.5, 97.5, 80)}
C, E = (85, 155, 215), (14, 30, 58)
LOOKS = [("Brighter middle", (C, E, 0.0)),
         ("Larger middle", (C, E, 0.35)),
         ("Largest middle", (C, E, 0.55))]
def crest(name, look):
    cx, cy, S = CRESTS[name]
    pad = S * K / 2 + 6
    box = (round(cx - pad), round(cy - pad), round(cx + pad), round(cy + pad))
    c = np.array(src.crop(box)).astype(np.float32)
    if look is None: return Image.fromarray(c.astype(np.uint8))
    inner = S - (14 if S > 60 else 10)
    fr = (inner - 2) / 2 * K                         # the face circle, in px
    h, w = c.shape[:2]; ox, oy = cx - box[0], cy - box[1]
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    d = np.hypot(xx - ox, yy - oy)
    inside = np.clip(fr - d + 0.5, 0, 1)[..., None]  # antialiased circle
    # glow: brightest a little above center (backlight behind the head)
    core = look[2]                                   # share of the radius at full brightness
    t = np.clip(np.hypot(xx - ox, yy - (oy - 0.18 * fr)) / (fr * 1.1), 0, 1)
    t = np.clip((t - core) / (1 - core), 0, 1)
    t = t * t * (3 - 2 * t)
    cen, edg = np.array(look[0], np.float32), np.array(look[1], np.float32)
    glow = cen * (1 - t[..., None]) + edg * t[..., None]
    a = np.clip((c.max(-1) - 3) / 14, 0, 1)
    a = np.array(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)[..., None] / 255
    face = c * a + glow * (1 - a)
    res = c * (1 - inside) + face * inside
    return Image.fromarray(res.clip(0, 255).astype(np.uint8))
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 20)
Z = 3
rows = []
for label, look in LOOKS:
    p, t = crest("pet", look), crest("target", look)
    rows.append((label, p, t, p.resize((p.width * Z, p.height * Z), Image.NEAREST), t.resize((t.width * Z, t.height * Z), Image.NEAREST)))
colw = [rows[0][1].width, rows[0][2].width, rows[0][3].width, rows[0][4].width]
rowh = max(r[4].height for r in rows)
W = 200 + sum(colw) + 4 * 20; H = 40 + len(rows) * (rowh + 20)
sheet = Image.new("RGB", (W, H), (20, 22, 28)); d = ImageDraw.Draw(sheet)
x = 200
for hdr, cw in zip(["Actual", "", "Zoom x3: your wolf", "Zoom x3: target"], colw):
    d.text((x, 8), hdr, font=font, fill=(255, 209, 0)); x += cw + 20
y = 40
for label, *imgs in rows:
    d.text((10, y + rowh // 2 - 12), label, font=font, fill=(255, 255, 255))
    x = 200
    for im, cw in zip(imgs, colw):
        sheet.paste(im, (x, y + (rowh - im.height) // 2)); x += cw + 20
    y += rowh + 20
sheet.save(out); print(sheet.size)
