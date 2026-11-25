# Professions overview cards: navy -> black (user, Nov 25 15:24), drawn on
# the user's screenshot. A black + blue edges, B black + faint navy edges,
# C charcoal + blue edges. Usage: python3 prof_black.py <screenshot>
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
src = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(float)
NAVY = np.array([19, 40, 74.]); EDGE = np.array([57, 103, 166.])
BOX = (44, 100, 1081, 960)                      # window inside, side tabs excluded
def make(card, edge=None):
    a = src.copy(); x0, y0, x1, y1 = BOX; r = a[y0:y1, x0:x1]
    d = np.linalg.norm(r - NAVY, axis=2)
    w = np.clip(1 - d / 70, 0, 1)[..., None]   # navy and the soft edges of text on it
    r += w * (np.array(card) - NAVY)
    if edge is not None:
        e = (np.linalg.norm(src[y0:y1, x0:x1] - EDGE, axis=2) < 4)
        r[e] = edge
    a[y0:y1, x0:x1] = r
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
opts = [('A  black cards, blue edges (recommended)', make((10, 11, 14))),
        ('B  black cards, faint navy edges', make((10, 11, 14), (31, 52, 86))),
        ('C  charcoal cards, blue edges', make((24, 27, 34)))]
F = ImageFont.truetype('/home/claude/brand/AetherHub/Media/Fonts/FiraSans-SemiBold.ttf', 28)
for i, (lbl, im) in enumerate(opts):
    bar = Image.new('RGB', (im.width, 46), (16, 18, 24)); ImageDraw.Draw(bar).text((14, 8), lbl, font=F, fill=(255, 176, 0))
    out = Image.new('RGB', (im.width, im.height + 46)); out.paste(bar, (0, 0)); out.paste(im, (0, 46))
    out.save('out_prof_%s.png' % 'ABC'[i])
print('ok')
