# Places AetherPack's real deposit textures on a screenshot the way the code does
# (slot at the row's left, ink's top-left 12 units above the slot), for checking.
# Usage: dep_place_check.py <Media dir> <screenshot> <slot_x_px> <slot_y_px> <px_per_unit> <out>
import sys
import numpy as np
from PIL import Image
M, SRC, SX, SY, PXU, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
AMBER = (255, 176, 0)
img = Image.open(SRC).convert('RGBA')
def tex(n): return Image.open(M + '/' + n + '.tga').convert('RGBA')
def tint(im, a=1.0):
    x = np.array(im).astype(np.float32)
    for k in range(3): x[..., k] *= AMBER[k] / 255
    x[..., 3] *= a; return Image.fromarray(x.clip(0, 255).astype(np.uint8))
n = round(37 * PXU)
for name, t in (('dep_well', False), ('dep_glow', True), ('dep_dark', False), ('dep_rim', True)):
    im = tex(name).resize((n, n), Image.LANCZOS)
    img.alpha_composite(tint(im) if t else im, (SX, SY))
ink = tint(tex('dep_ink').resize((round(256 * PXU), round(64 * PXU)), Image.LANCZOS))
img.alpha_composite(ink, (SX, SY - round(12 * PXU)))
img.convert('RGB').save(OUT)
