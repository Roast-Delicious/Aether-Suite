# Before/after of /af center on the user's own screenshot (1:1, 1.345 px per frame unit).
# The only visible in-row change: the target of target comes up 3 px to the pet's row.
import sys
from PIL import Image, ImageDraw, ImageFont
src = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
K = 1.345
W, H = 860, 305
before = src.crop((0, 0, W, H))
after = before.copy()
strip = before.crop((486, 196, 790, 300))            # target of target (ground around it is plain)
after.paste(before.crop((486, 300, 790, 303)), (486, 297))   # refill the 3 px it leaves
after.paste(strip, (486, 193))
XR, XL = 407.5, 407.5 + 61 * K
ROW1, ROW2 = 61, 217                                  # capsule tops: player row, pet row
def guides(img, s, rows):
    d = ImageDraw.Draw(img)
    for x in (XR, XL):
        for y in range(0, img.height, 8 * s): d.line([(x * s, y), (x * s, y + 4 * s)], fill=(77, 166, 255), width=max(1, s // 2))
    for y in rows:
        for x in range(0, img.width, 8 * s): d.line([(x, y * s), (x + 4 * s, y * s)], fill=(77, 166, 255), width=max(1, s // 2))
    return img
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 22)
z = 4; box = (380, 200, 520, 280)
def zoom(img): return guides(img.resize((W * z, H * z), Image.NEAREST), z, [ROW2]).crop(tuple(v * z for v in box))
zb, za = zoom(before), zoom(after)
sheet = Image.new("RGB", (W * 2 + 30, H + 40 + zb.height + 50), (20, 22, 28))
d = ImageDraw.Draw(sheet)
d.text((10, 8), "Before (your screenshot)", font=font, fill=(255, 209, 0))
d.text((W + 30, 8), "After (actual size)", font=font, fill=(255, 209, 0))
sheet.paste(before, (0, 40)); sheet.paste(after, (W + 30, 40))
y0 = H + 50
d.text((10, y0), "Zoom x4, pet row. Blue: the shared capsule top and inner edges", font=font, fill=(255, 209, 0))
sheet.paste(zb, (10, y0 + 36)); sheet.paste(za, (zb.width + 40, y0 + 36))
d.text((20, y0 + 40), "before", font=font, fill=(255, 255, 255)); d.text((zb.width + 50, y0 + 40), "after", font=font, fill=(255, 255, 255))
sheet.save(out); print(sheet.size)
