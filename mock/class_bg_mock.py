# Portrait background in solid class colors (game's RAID_CLASS_COLORS, from the
# Warcraft Wiki "Class colors" table), unfaded and faded (face at 30% over the
# dark disc, ring at 30% over the ground), on the user's real 3D portrait
# (video frame at 66 s, Jay solid; 1.29 px per unit).
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
K = 1.29
src = np.array(Image.open('/home/claude/vid2/c_%04d.png' % (66 * 4 + 1)).convert('RGB')).astype(np.float32)
grass = np.array(Image.open('/home/claude/vid2/grass.png').convert('RGB')).astype(np.float32)
cx, cy, S = 74.5, 90.2, 80
rf = (S - 14 - 2) / 2 * K            # face circle radius, px
R = S / 2 * K                        # crest outer radius
pad = 10
x0, y0 = round(cx - R - pad), round(cy - R - pad)
crop = src[y0:y0 + round(2 * (R + pad)), x0:x0 + round(2 * (R + pad))]
H, W = crop.shape[:2]
yy, xx = np.mgrid[0:H, 0:W] + 0.5
d = np.hypot(xx - (cx - x0), yy - (cy - y0))
inface = np.clip(rf - d + 0.5, 0, 1)[..., None]
increst = np.clip(R + 1 - d, 0, 1)[..., None]
r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
glow = ((b - r) > 35) & ((b - g) > 10) & (d < rf)
bg = grass[:H, :W]
DARK = np.array((11, 13, 18), np.float32)
CLASSES = [("Druid", (255, 124, 10)), ("Hunter", (170, 211, 114)), ("Mage", (63, 199, 235)),
           ("Paladin", (244, 140, 186)), ("Priest", (255, 255, 255)), ("Rogue", (255, 244, 104)),
           ("Shaman", (0, 112, 221)), ("Warlock", (135, 136, 238)), ("Warrior", (198, 155, 109))]
def look(col):
    img = crop.copy()
    if col is not None: img[glow] = np.array(col, np.float32)
    # put it on the ground (the crop already is), faded: ring at 30% over ground, face at 30% over dark
    faded = img.copy()
    ring = increst * (1 - inface)
    faded = faded * (1 - ring) + (img * 0.3 + bg * 0.7) * ring
    faded = faded * (1 - inface) + (img * 0.3 + DARK * 0.7) * inface
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)), Image.fromarray(faded.clip(0, 255).astype(np.uint8))
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 20)
small = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 15)
entries = [("Now: Aether glow", None)] + CLASSES
Z = 2; tw = W * Z
cellw, cellh = 2 * tw + W + 70, H * Z + 70
cols = 3
sheet = Image.new("RGB", (cols * cellw + 20, ((len(entries) + cols - 1) // cols) * cellh + 20), (20, 22, 28))
dr = ImageDraw.Draw(sheet)
for i, (name, col) in enumerate(entries):
    u, f = look(col)
    x = 10 + (i % cols) * cellw; y = 10 + (i // cols) * cellh
    dr.text((x, y), name, font=font, fill=(255, 209, 0))
    dr.text((x, y + 26), "solid", font=small, fill=(200, 200, 200)); dr.text((x + tw + 20, y + 26), "faded (in combat)", font=small, fill=(200, 200, 200))
    sheet.paste(u.resize((tw, H * Z), Image.LANCZOS), (x, y + 46))
    sheet.paste(f.resize((tw, H * Z), Image.LANCZOS), (x + tw + 20, y + 46))
    ax = x + 2 * tw + 32                                                    # actual size, beside
    sheet.paste(u, (ax, y + 46)); sheet.paste(f, (ax, y + 46 + H + 6))
sheet.save(sys.argv[1]); print(sheet.size)
