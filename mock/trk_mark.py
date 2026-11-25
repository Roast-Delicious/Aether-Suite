# Marking the hand-in section without new space (user, Nov 25: no overlap
# with quest text). The gap above the first hand-in quest is only a few
# pixels, so a text label can't fit there; instead the hand-in quests' "?"
# icons turn Aether blue (matching "Ready for turn-in").
import numpy as np
from PIL import Image, ImageDraw
from talent_details import F
SRC = Image.open('/mnt/user-data/uploads/052f5d45-image.png').convert('RGB')
LINE_Y = 368
def blue_icons(im):
    a = np.array(im).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gold = (r > 150) & (g > 90) & (b < 90) & (r - b > 90)
    region = np.zeros_like(gold); region[LINE_Y:, 18:58] = True
    m = gold & region
    lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255
    a[m, 0] = 77 * lum[m] / 0.62; a[m, 1] = 166 * lum[m] / 0.62; a[m, 2] = 255 * lum[m] / 0.62
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
crop = (0, 230, 456, 640)
A = SRC.crop(crop); B = blue_icons(SRC).crop(crop)
Z = 2
A = A.resize((A.width * Z, A.height * Z), Image.LANCZOS); B = B.resize((B.width * Z, B.height * Z), Image.LANCZOS)
W = A.width * 2 + 60
sh = Image.new('RGB', (W, A.height + 110), (16, 18, 24)); d = ImageDraw.Draw(sh)
d.text((20, 16), "Now: gold line only", font=F(22, 'SemiBold'), fill=(255, 176, 0))
d.text((A.width + 40, 16), "Gold line + blue icons for hand-ins  (my pick)", font=F(22, 'SemiBold'), fill=(255, 176, 0))
sh.paste(A, (20, 56)); sh.paste(B, (A.width + 40, 56))
d.text((20, A.height + 70), "2x zoom of your screenshot. Nothing moves and nothing new is added, so nothing can overlap.", font=F(17), fill=(170, 176, 188))
sh.save('out_trk_mark.png'); print(sh.size)
