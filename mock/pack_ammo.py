# Pack's space rows: how to show quiver room (user, Nov 25: "10 of 20 slots
# remaining" helps decide how many arrows to buy). Example: 16-slot quiver,
# stacks of 200, 1,240 arrows -> 7 slots used, 9 free, room for 1,960 more.
from PIL import Image, ImageDraw
from talent_details import F
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74); DIM = (170, 176, 188)
WHITE = (255, 255, 255); GREEN = (34, 230, 80); BG = (10, 16, 28)
K = 2   # rows drawn at 2x game size so they're readable on a phone
OPTS = [("A  Slots free (as you described)", [("Bags", "12 free", GREEN, None), ("Ammo", "1,240", WHITE, None), ("Quiver", "9 of 16 free", GREEN, None)]),
        ("B  Arrows you can still fit  (my pick)", [("Bags", "12 free", GREEN, None), ("Ammo", "1,240", WHITE, None), ("Quiver", "room for 1,960", GREEN, "9 of 16 slots free")]),
        ("C  Both on one line", [("Bags", "12 free", GREEN, None), ("Ammo", "1,240 / 3,200", WHITE, None), ("Quiver", "9 slots free", GREEN, None)])]
W, H = 1180, 520
im = Image.new('RGB', (W, H), (16, 18, 24)); d = ImageDraw.Draw(im)
d.text((24, 16), "Pack: quiver room under the bag grid (2x game size)", font=F(26, 'SemiBold'), fill=GOLD)
d.text((24, 52), "Example: 16-slot quiver, stacks of 200, 1,240 arrows carried.", font=F(17), fill=DIM)
for i, (title, rows) in enumerate(OPTS):
    x = 24 + i * 385; y = 100
    d.text((x, y), title, font=F(18, 'SemiBold'), fill=GOLD)
    d.rounded_rectangle([x, y + 34, x + 360, y + 34 + 3 * 15 * K + 30], 8, fill=BG, outline=(40, 70, 115), width=2)
    for r, (lab, val, col, tip) in enumerate(rows):
        yy = y + 50 + r * 15 * K
        d.text((x + 16, yy), lab, font=F(12 * K), fill=DIM)
        d.text((x + 344, yy), val, font=F(12 * K, 'SemiBold'), fill=col, anchor='ra')
    # tooltip for the quiver row
    ty = y + 34 + 3 * 15 * K + 50
    lines = {0: ["Quiver: 7 of 16 slots used", "9 free", "Room for 1,960 more arrows"],
             1: ["Quiver: 9 of 16 slots free", "1,240 of 3,200 arrows", "Room for 1,960 more"],
             2: ["1,240 of 3,200 arrows", "Room for 1,960 more", "9 of 16 slots free"]}[i]
    d.text((x, ty - 22), "Hover the row:", font=F(15), fill=DIM)
    d.rounded_rectangle([x, ty, x + 300, ty + 26 * len(lines) + 16], 6, fill=(8, 12, 22), outline=BLUE, width=2)
    for j, ln in enumerate(lines):
        d.text((x + 12, ty + 10 + j * 26), ln, font=F(17), fill=WHITE if j == 0 else DIM)
d.text((24, H - 60), "Colour follows the bag rows: green with room, gold in the last 25%, red in the last 10%.", font=F(16), fill=DIM)
d.text((24, H - 34), "Ammo pouches say \"Pouch\", soul bags say \"Soul bag\" and count shards the same way.", font=F(16), fill=DIM)
im.save('out_pack_ammo.png'); print(im.size)
