# Hand-in quests: a check mark in place of the "?" (user idea, Nov 25).
import numpy as np
from PIL import Image, ImageDraw
from talent_details import F
from trk_mark import blue_icons, SRC, LINE_Y
SS = 4
ICON_YS = []
a = np.array(SRC).astype(int)
# find the ring centers below the line: rows where gold ring pixels peak
col = a[:, 38]
gold = (col[:, 0] > 150) & (col[:, 1] > 90) & (col[:, 2] < 90)
ys = [y for y in range(LINE_Y, SRC.height) if gold[y]]
# group into icons (each ring top and bottom), take centers
groups, cur = [], [ys[0]]
for y in ys[1:]:
    if y - cur[-1] > 3: groups.append(cur); cur = [y]
    else: cur.append(y)
groups.append(cur)
tops = groups[0::2]; bots = groups[1::2]
centers = [((t[0] + b[-1]) / 2) for t, b in zip(tops, bots)]
centers = [387, 498, 591]
def checks(im, col):
    im = im.copy()
    for cy in centers:
        cx = 38.5; r = 16
        big = Image.new('RGBA', (r * 2 * SS, r * 2 * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
        d.ellipse([5 * SS, 5 * SS, (2 * r - 5) * SS, (2 * r - 5) * SS], fill=(20, 26, 44, 255))   # cover the "?"
        w = int(2.6 * SS)
        d.line([(10 * SS, 16.5 * SS), (14.5 * SS, 21 * SS), (22.5 * SS, 11.5 * SS)], fill=col + (255,), width=int(3.2 * SS), joint='curve')
        big = big.resize((r * 2, r * 2), Image.LANCZOS)
        im.paste(big, (int(cx - r), int(cy - r)), big)
    return im
crop = (0, 230, 456, 640); Z = 2
A = checks(SRC, (255, 176, 0)).crop(crop); B = checks(blue_icons(SRC), (77, 166, 255)).crop(crop)
A = A.resize((A.width * Z, A.height * Z), Image.LANCZOS); B = B.resize((B.width * Z, B.height * Z), Image.LANCZOS)
sh = Image.new('RGB', (A.width * 2 + 60, A.height + 110), (16, 18, 24)); d = ImageDraw.Draw(sh)
d.text((20, 16), "A  Gold check", font=F(22, 'SemiBold'), fill=(255, 176, 0))
d.text((A.width + 40, 16), "B  Blue check, blue ring  (my pick)", font=F(22, 'SemiBold'), fill=(255, 176, 0))
sh.paste(A, (20, 56)); sh.paste(B, (A.width + 40, 56))
d.text((20, A.height + 70), "2x zoom. Gold line kept in both. Nothing moves, so nothing can overlap.", font=F(17), fill=(170, 176, 188))
sh.save('out_trk_check.png'); print(centers)
