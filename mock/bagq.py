# Bag slot frames: all blue (as built) vs item quality colour (green and up).
from PIL import Image, ImageDraw
from talent_details import F
from vendor import icon, BLUE, GOLD, NAVY, DIM, Q
Q = dict(Q); Q[5] = (255, 128, 0)
KINDS = ['sack', 'jar', 'flask', 'bread', 'pole', 'bandage', 'box', 'spool', 'pick', 'flask', 'jar', 'sack']
QUAL = [1, 1, 2, 1, 3, 2, 1, 4, 1, 1, 2, 5]
def grid(byq, s=58):
    im = Image.new('RGBA', (4 * (s + 10) + 20, 3 * (s + 10) + 20), (10, 16, 28, 255)); d = ImageDraw.Draw(im)
    for i, (k, q) in enumerate(zip(KINDS, QUAL)):
        x = 14 + (i % 4) * (s + 10); y = 14 + (i // 4) * (s + 10)
        icon(d, k, x, y, s)
        col = Q[q] if (byq and q >= 2) else BLUE
        d.rectangle([x - 2, y - 2, x + s + 2, y + s + 2], outline=col, width=2)
        d.rectangle([x - 5, y - 5, x + s + 5, y + s + 5], outline=col if byq and q >= 2 else (40, 70, 115), width=1)
    return im
a, b = grid(False), grid(True)
W = a.width * 2 + 260; sh = Image.new('RGB', (W, a.height + 110), (16, 18, 24)); d = ImageDraw.Draw(sh)
d.text((40, 20), "A  All blue (as built now)", font=F(20, 'SemiBold'), fill=GOLD)
d.text((120 + a.width, 20), "B  Quality colour, green and up (my pick)", font=F(20, 'SemiBold'), fill=GOLD)
sh.paste(a, (40, 60)); sh.paste(b, (120 + a.width, 60))
d.text((40, a.height + 76), "Game size. Item art is a placeholder; real icons show in game.", font=F(15), fill=DIM)
sh.save('out_bagq.png'); print(sh.size)
