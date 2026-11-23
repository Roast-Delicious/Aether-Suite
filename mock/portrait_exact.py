# The exact Aether blue glow (larger middle) on all four crests, in the user's screenshot.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
K = 1.345
CRESTS = [(105.5, 97.5, 80), (792.5, 97.5, 80), (167.5, 244, 58), (734.5, 247, 58)]
CEN, EDGE, CORE = np.array((76, 178, 255), np.float32), np.array((19, 40, 74), np.float32), 0.35
img = np.array(src).astype(np.float32)
H, W = img.shape[:2]
yy, xx = np.mgrid[0:H, 0:W] + 0.5
key = np.clip((img.max(-1) - 3) / 14, 0, 1)
key = np.array(Image.fromarray((key * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255
for cx, cy, S in CRESTS:
    inner = S - (14 if S > 60 else 10); fr = (inner - 2) / 2 * K
    d = np.hypot(xx - cx, yy - cy)
    inside = np.clip(fr - d + 0.5, 0, 1)[..., None]
    t = np.clip(np.hypot(xx - cx, yy - (cy - 0.18 * fr)) / (fr * 1.1), 0, 1)
    t = np.clip((t - CORE) / (1 - CORE), 0, 1); t = t * t * (3 - 2 * t)
    glow = CEN * (1 - t[..., None]) + EDGE * t[..., None]
    face = img * key[..., None] + glow * (1 - key[..., None])
    img = img * (1 - inside) + face * inside
after = Image.fromarray(img.clip(0, 255).astype(np.uint8)).crop((0, 0, 860, 300))
before = src.crop((0, 0, 860, 300))
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 22)
z = 2
zb = after.resize((after.width * z, after.height * z), Image.NEAREST)
sheet = Image.new("RGB", (zb.width + 20, 40 + 300 + 50 + 300 + 50 + zb.height + 10), (20, 22, 28))
d = ImageDraw.Draw(sheet); y = 8
for label, im in [("Now (actual size)", before), ("Exact Aether blue (actual size)", after), ("Exact Aether blue, zoom x2", zb)]:
    d.text((10, y), label, font=font, fill=(255, 209, 0)); sheet.paste(im, (10, y + 32)); y += 32 + im.height + 18
sheet.save(out); print(sheet.size)
