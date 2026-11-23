# Target portrait glow tinted by difficulty (the level badge's color), on the
# user's in-game target crest (1.342 px per frame unit). Glow pixels are found
# by their blue, then repainted with the same glow shape in each color.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
K = 1.342; cx, cy, S = 1621.5, 1204, 80
inner = S - 14; rf = (inner - 2) / 2
r = round(S / 2 * K) + 8
box = (round(cx - r), round(cy - r), round(cx + r), round(cy + r))
c = np.array(im.crop(box)).astype(np.float32)
H, W = c.shape[:2]
yy, xx = np.mgrid[0:H, 0:W] + 0.5
ox, oy = cx - box[0], cy - box[1]
d = np.hypot(xx - ox, yy - oy) / K
inside = np.clip(rf - d + 0.5, 0, 1)
R_, G_, B_ = c[..., 0], c[..., 1], c[..., 2]
isglow = ((B_ - R_) > 35) & ((B_ - G_) > 10) & (inside > 0.5)
# glow shape (same as the art): full to 35% of the radius, center 18% up
t = np.clip(np.hypot(xx - ox, yy - (oy - 0.18 * rf * K)) / (rf * K * 1.1), 0, 1)
t = np.clip((t - 0.35) / 0.65, 0, 1); t = t * t * (3 - 2 * t)
def paint(center, edge):
    g = np.array(center, np.float32) * (1 - t[..., None]) + np.array(edge, np.float32) * t[..., None]
    o = c.copy(); o[isglow] = g[isglow]; return Image.fromarray(o.clip(0, 255).astype(np.uint8))
NAVY = (19, 40, 74)
looks = [("Now (Aether blue)", None)]
for name, col in [("Gray", (0.55, 0.55, 0.55)), ("Green", (0.25, 0.75, 0.25)), ("Yellow", (1, 0.82, 0)), ("Orange", (1, 0.5, 0.13)), ("Red", (1, 0.13, 0.13))]:
    cen = tuple(v * 255 for v in col); edge = tuple(v * 255 * 0.22 for v in col)
    looks.append((name, (cen, edge)))
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 20)
Z = 3; tiles = []
for name, lk in looks:
    img = Image.fromarray(c.astype(np.uint8)) if lk is None else paint(*lk)
    tiles.append((name, img))
tw = tiles[0][1].width
sheet = Image.new("RGB", (3 * (tw * Z + 20) + 10, 2 * (tw * Z + 50) + 10), (20, 22, 28)); dr = ImageDraw.Draw(sheet)
for i, (name, img) in enumerate(tiles):
    x = 10 + (i % 3) * (tw * Z + 20); y = 10 + (i // 3) * (tw * Z + 50)
    dr.text((x, y), name, font=font, fill=(255, 209, 0))
    sheet.paste(img.resize((tw * Z, tw * Z), Image.NEAREST), (x, y + 32))
    sheet.paste(img, (x + tw * Z - img.width - 4, y + 32 + 4))   # actual size, top-right corner
sheet.save(out); print(sheet.size)
