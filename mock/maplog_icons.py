# Map quest log: quest icons and track boxes in the tracker's colors
# (user, Nov 25: "same color scheme we use in the quest list").
from PIL import Image, ImageDraw
from talent_details import F
SRC = Image.open('/mnt/user-data/uploads/ccef87ac-image.png').convert('RGBA')
GOLD = (255, 176, 0); NAVY = (19, 40, 74); BLUE = (77, 166, 255)
ICONS = [(1099, 183), (1099, 240), (1099, 297)]; BOXES = [(1499, 184), (1499, 241), (1499, 298)]
S = 8
def icon(r=15):
    n = r * 2 * S; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, n - 1, n - 1], fill=GOLD + (255,)); k = int(n * .13)
    d.ellipse([k, k, n - 1 - k, n - 1 - k], fill=NAVY + (255,))
    for dx in (-.24, 0, .24):
        cx, cy = n / 2 + dx * n, n / 2; rr = n * .065
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=GOLD + (255,))
    return im.resize((r * 2, r * 2), Image.LANCZOS)
def box(s=18):
    n = s * S; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, n - 1, n - 1], int(n * .18), fill=NAVY + (255,), outline=BLUE + (255,), width=int(n * .09))
    return im.resize((s, s), Image.LANCZOS)
B = SRC.copy()
for cx, cy in ICONS:
    ImageDraw.Draw(B).ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(14, 18, 28, 255))
    B.alpha_composite(icon(), (cx - 15, cy - 15))
for cx, cy in BOXES:
    ImageDraw.Draw(B).rectangle([cx - 11, cy - 11, cx + 11, cy + 11], fill=(14, 18, 28, 255))
    B.alpha_composite(box(), (cx - 9, cy - 9))
crop = (1078, 125, 1530, 360); Z = 2
a = SRC.crop(crop).resize(((crop[2] - crop[0]) * Z, (crop[3] - crop[1]) * Z), Image.LANCZOS)
b = B.crop(crop).resize(a.size, Image.LANCZOS)
sh = Image.new('RGB', (a.width * 2 + 60, a.height + 80), (16, 18, 24)); d = ImageDraw.Draw(sh)
d.text((20, 14), "Now", font=F(22, 'SemiBold'), fill=GOLD)
d.text((a.width + 40, 14), "Tracker colors: navy disc, gold ring and dots; navy track boxes", font=F(20, 'SemiBold'), fill=GOLD)
sh.paste(a, (20, 50)); sh.paste(b, (a.width + 40, 50))
sh.save('out_maplog_icons.png'); print(sh.size)
