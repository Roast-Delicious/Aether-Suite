# Composite AetherPack's deposit art the way the addon layers it, for checking.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
MEDIA, OUT = sys.argv[1], sys.argv[2]
AMBER = (255, 176, 0)
S = 12                                   # px per unit for this preview
def tex(name): return Image.open(MEDIA + '/' + name + '.tga').convert('RGBA')
def tint(im, col):
    a = np.array(im).astype(np.float32)
    for k in range(3): a[..., k] = a[..., k] * col[k] / 255
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))
W, H = 68, 64
cv = Image.new('RGBA', (W * S, H * S), (14, 16, 22, 255))
SX, SY, SL = 13, 23, 37
def put(im, x, y, w, h): cv.alpha_composite(im.resize((int(w * S), int(h * S)), Image.LANCZOS), (int(x * S), int(y * S)))
put(tex('dep_well'), SX, SY, SL, SL)
put(tint(tex('dep_glow'), AMBER), SX, SY, SL, SL)
put(tex('dep_dark'), SX, SY, SL, SL)
put(tint(tex('dep_rim'), AMBER), SX, SY, SL, SL)
put(tint(tex('dep_numglow'), AMBER).point(lambda v: v), SX + SL / 2 - 15, SY + SL / 2 - 10, 30, 20)
f = ImageFont.truetype('/home/claude/aether-suite/AetherHub/Media/Fonts/FiraSans-Black.ttf' if len(sys.argv) < 4 else sys.argv[3], int(10.5 * S))
d = ImageDraw.Draw(cv)
from PIL import ImageFilter
shl = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(shl).text(((SX + SL / 2) * S + S * 0.7, (SY + SL / 2) * S + S * 0.7), "20", font=f, fill=(0, 0, 0, 170), anchor='mm')
cv.alpha_composite(shl.filter(ImageFilter.GaussianBlur(S * 0.5)))
d = ImageDraw.Draw(cv)
d.text(((SX + SL / 2) * S, (SY + SL / 2) * S), "20", font=f, fill=(255, 199, 77, 255), anchor='mm')
sh = tex('dep_ink_sh'); cv.alpha_composite(sh.resize((68 * S, 68 * S), Image.LANCZOS).crop((0, 0, W * S, H * S)), (int(0.7 * S), int(0.7 * S)))
ink = tint(tex('dep_ink'), AMBER); cv.alpha_composite(ink.resize((68 * S, 68 * S), Image.LANCZOS).crop((0, 0, W * S, H * S)), (0, 0))
cv.convert('RGB').save(OUT)
