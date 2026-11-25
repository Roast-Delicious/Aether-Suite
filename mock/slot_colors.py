# Gear and bag slot frames (user, Nov 25 test: rare blue and empty slots
# looked the same). Empty, plain (white/gray items), uncommon, rare, epic.
from PIL import Image, ImageDraw
from talent_details import F
from vendor import icon
GOLD = (255, 176, 0); BLUE = (77, 166, 255); DIM = (150, 156, 170)
Q = {'unc': (30, 255, 0), 'rare': (0, 112, 221), 'epic': (163, 53, 238)}
OPTS = [('now', "Now", {'empty': BLUE, 'plain': BLUE}),
        ('A', "A  Empty dim, plain silver  (my pick)", {'empty': (52, 64, 84), 'plain': (200, 205, 215)}),
        ('B', "B  Empty dim, plain Aether blue", {'empty': (52, 64, 84), 'plain': BLUE})]
SLOTS = [('empty', "empty"), ('plain', "plain"), ('unc', "uncommon"), ('rare', "rare"), ('epic', "epic")]
S = 58; W = 1180; H = 120 + len(OPTS) * 120
im = Image.new('RGB', (W, H), (16, 18, 24)); d = ImageDraw.Draw(im)
d.text((20, 16), "Item frames: Character slots and Pack (2x game size)", font=F(22, 'SemiBold'), fill=GOLD)
for r, (o, t, cols) in enumerate(OPTS):
    y = 70 + r * 120
    d.text((20, y + S / 2), t, font=F(17, 'SemiBold'), fill=GOLD, anchor='lm')
    for i, (k, lab) in enumerate(SLOTS):
        x = 520 + i * 125
        d.rectangle([x, y, x + S, y + S], fill=(14, 18, 26))
        if k != 'empty': icon(d, ['sack', 'spool', 'pick', 'flask', 'jar'][i], x, y, S)
        c = cols.get(k) or Q[k]
        d.rectangle([x - 2, y - 2, x + S + 2, y + S + 2], outline=c, width=2)
        d.text((x + S / 2, y + S + 10), lab, font=F(14), fill=DIM, anchor='ma')
im.save('out_slot_colors.png'); print(im.size)
