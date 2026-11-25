# Whole Aether Pack window (hunter), game size, with the three ways to show
# quiver room in the space rows. Layout follows AetherPack_Layout: title +
# coins + close, search, sections (header + blue line, 10 columns of 37 +
# 2 gap), deposit slot with the chalk ink, space rows beside it.
from PIL import Image, ImageDraw
import random
from talent_details import F
from vendor import icon

K = 1.55; SS = 2; U = K * SS          # UI unit -> px on the big canvas
GOLD = (255, 176, 0); BLUE = (77, 166, 255); DIM = (170, 176, 188); WHITE = (255, 255, 255)
GREEN = (34, 230, 80); RED = (240, 94, 84); BG = (13, 15, 23)
Q = {2: (30, 255, 0), 3: (0, 112, 221), 4: (163, 53, 238)}
MEDIA = '/home/claude/aether-repo/AetherPack/Media/'
BUTTON, GAP, PAD, COLS, ROW_H = 37, 2, 10, 10, 15
KINDS = ['sack', 'jar', 'flask', 'bread', 'pole', 'bandage', 'box', 'spool', 'pick']
random.seed(4)
SECTIONS = [("Ammo", [('pole', 1, 200)] * 6 + [('pole', 1, 40)]),
            ("Quest items", [('box', 1, 1), ('jar', 1, 3)]),
            ("Gear", [('pick', 2, 1), ('box', 3, 1), ('spool', 2, 1), ('jar', 1, 1), ('flask', 4, 1), ('bread', 2, 1)]),
            ("Consumables", [('flask', 1, 20), ('flask', 1, 14), ('bread', 1, 20), ('bread', 1, 7), ('bandage', 1, 12),
                             ('bandage', 2, 5), ('jar', 1, 3), ('flask', 2, 2)]),
            ("Trade goods", [('spool', 1, 20), ('sack', 1, 8), ('box', 2, 4), ('jar', 1, 11), ('pick', 1, 2)]),
            ("Other", [('sack', 1, 1), ('box', 1, 1), ('spool', 1, 1)]),
            ("Junk", [('sack', 1, 3), ('pole', 1, 1)])]

def tga(name, w, h):
    return Image.open(MEDIA + name).convert('RGBA').resize((int(w * U), int(h * U)), Image.LANCZOS)

HDR = {'R1': ("Arrows:", "1,240", "buy 9 stacks to fill", 'right', (235, 238, 245)),
       'R2': ("Bullets:", "380", "buy 2 stacks to fill", 'right', (235, 238, 245)),
       'R3': ("Arrows:", "3,200", "quiver full", 'right', GREEN),
       'R4': ("Soul shards:", "14", "room for 6 more", 'right', (235, 238, 245)),
       'R5': ("Arrows:", "220", "buy 14 stacks to fill", 'right', RED)}
def window(opt):
    W = COLS * (BUTTON + GAP) - GAP + 2 * PAD
    rows_h = sum(18 + 2 + ((len(items) + COLS - 1) // COLS) * (BUTTON + GAP) + 6 for _, items in SECTIONS) + 22
    H = 56 + rows_h + 70 + 10
    im = Image.new('RGBA', (int(W * U), int(H * U)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    s = lambda v: v * U
    d.rectangle([0, 0, s(W) - 1, s(H) - 1], fill=BG + (240,), outline=(77, 166, 255, 230), width=int(U))
    # title, coins, close
    d.text((s(PAD), s(9)), "AETHER PACK", font=F(13 * U, 'SemiBold'), fill=BLUE)
    d.rounded_rectangle([s(W - 6 - 18), s(6), s(W - 6), s(24)], int(s(3)), fill=(19, 40, 74), outline=BLUE, width=int(U))
    d.text((s(W - 15), s(15)), "x", font=F(12 * U), fill=WHITE, anchor='mm')
    xr = s(W - 32)
    for txt, col in (("9", (196, 112, 60)), ("34", (200, 206, 216)), ("127", GOLD)):
        d.ellipse([xr - s(10), s(10), xr - s(1), s(19)], fill=col); xr -= s(12)
        d.text((xr, s(15)), txt, font=F(12 * U, 'SemiBold'), fill=WHITE, anchor='rm'); xr -= d.textlength(txt, font=F(12 * U, 'SemiBold')) + s(6)
    # search
    d.rectangle([s(PAD), s(30), s(W - PAD), s(50)], fill=(18, 43, 82, 150), outline=(77, 166, 255, 150), width=int(U))
    d.text((s(PAD + 6), s(40)), "Search", font=F(11 * U), fill=(120, 126, 138), anchor='lm')
    y = 56
    for title, items in SECTIONS:
        hdr = HDR.get(opt) if title == "Ammo" else None
        if hdr: title = hdr[0]
        f = F(13 * U, 'SemiBold'); d.text((s(PAD + 2), s(y + 9)), title, font=f, fill=GOLD, anchor='lm')
        tw = d.textlength(title, font=f) / U
        lx0, lx1 = PAD + 2 + tw + 8, W - PAD
        if hdr:
            d.text((s(lx0 - 2), s(y + 9)), hdr[1], font=f, fill=DIM, anchor='lm')
            lx0 += d.textlength(hdr[1], font=f) / U + 8
            if hdr[3] == 'right':
                d.text((s(W - PAD), s(y + 9)), hdr[2], font=F(12 * U, 'SemiBold'), fill=hdr[4], anchor='rm')
                lx1 = W - PAD - d.textlength(hdr[2], font=F(12 * U, 'SemiBold')) / U - 8
            else:
                d.text((s(lx0 - 2), s(y + 9)), hdr[2], font=F(12 * U, 'SemiBold'), fill=hdr[4], anchor='lm')
                lx0 += d.textlength(hdr[2], font=F(12 * U, 'SemiBold')) / U + 8
        d.line([(s(lx0), s(y + 9)), (s(lx1), s(y + 9))], fill=(77, 166, 255, 90), width=int(U))
        y += 20
        for i, (k, q, n) in enumerate(items):
            x = PAD + (i % COLS) * (BUTTON + GAP); yy = y + (i // COLS) * (BUTTON + GAP)
            icon(d, k, s(x), s(yy), s(BUTTON))
            col = Q[q] if q >= 2 else BLUE
            d.rectangle([s(x), s(yy), s(x + BUTTON), s(yy + BUTTON)], outline=col, width=int(2 * U))
            if n > 1:
                d.text((s(x + BUTTON - 3), s(yy + BUTTON - 3)), str(n), font=F(11 * U, 'Bold'), fill=WHITE, anchor='rs',
                       stroke_width=int(U), stroke_fill=(0, 0, 0))
        y += ((len(items) + COLS - 1) // COLS) * (BUTTON + GAP) + 6
    # Free slots, folded
    f = F(13 * U, 'SemiBold'); d.text((s(PAD + 2), s(y + 9)), "Free slots", font=f, fill=GOLD, anchor='lm')
    tw = d.textlength("Free slots", font=f) / U
    d.text((s(PAD + 2 + tw + 6), s(y + 9)), "12", font=f, fill=DIM, anchor='lm')
    d.line([(s(PAD + 2 + tw + 30), s(y + 9)), (s(W - PAD - 40), s(y + 9))], fill=(77, 166, 255, 90), width=int(U))
    d.text((s(W - PAD), s(y + 9)), "Show", font=F(11 * U), fill=(110, 171, 255), anchor='rm')
    y += 26
    # deposit slot + chalk ink
    for nm in ('dep_well.tga', 'dep_rim.tga'):
        t = tga(nm, BUTTON + 6, BUTTON + 6); im.alpha_composite(t, (int(s(PAD - 3)), int(s(y - 3))))
    ink = tga('dep_ink.tga', 256, 64); im.alpha_composite(ink, (int(s(PAD)), int(s(y - 12))))
    # space rows beside the ink
    rows = {'A': [("Bags", "12 free", GREEN), ("Ammo", "1,240", WHITE), ("Quiver", "9 of 16 free", GREEN)],
            'B': [("Bags", "12 free", GREEN), ("Ammo", "1,240", WHITE), ("Quiver", "room for 1,960", GREEN)],
            'C': [("Bags", "12 free", GREEN), ("Ammo", "1,240 / 3,200", WHITE), ("Quiver", "9 slots free", GREEN)],
            'D': [("Bags", "12 free", GREEN), ("Sharp Arrow", "1,240", WHITE, "buy 9 stacks")],
            'E': [("Bags", "12 free", GREEN), ("Sharp Arrow", "1,240", WHITE), ("", "buy 9 stacks to fill", GOLD)],
            'F': [("Bags", "12 free", GREEN), ("Solid Shot", "380", WHITE), ("", "buy 2 stacks to fill", GOLD)],
            'G': [("Bags", "12 free", GREEN), ("Soul Shard", "14", WHITE), ("", "room for 6 more", GOLD)],
            'R1': [("Bags", "12 free", GREEN), ("Ammo", "1,240", WHITE)],
            'R2': [("Bags", "12 free", GREEN), ("Ammo", "380", WHITE)],
            'R3': [("Bags", "12 free", GREEN), ("Ammo", "3,200", WHITE)],
            'R4': [("Bags", "12 free", GREEN), ("Shards", "14", WHITE)],
            'R5': [("Bags", "12 free", GREEN), ("Ammo", "220", WHITE)],
            'H': [("Bags", "12 free", GREEN), ("Sharp Arrow", "3,200", WHITE), ("", "quiver full", GREEN)]}[opt]
    x0, x1 = PAD + 227 + 8, W - PAD
    ry = y + (BUTTON - len(rows) * ROW_H) / 2
    for row in rows:
        lab, val, col = row[:3]; hint = row[3] if len(row) > 3 else None
        d.text((s(x0), s(ry + ROW_H / 2)), lab, font=F(12 * U), fill=(200, 205, 215), anchor='lm')
        xv = s(x1)
        if hint:
            d.text((xv, s(ry + ROW_H / 2)), hint, font=F(12 * U, 'SemiBold'), fill=GOLD, anchor='rm')
            xv -= d.textlength(hint, font=F(12 * U, 'SemiBold')) + s(8)
        d.text((xv, s(ry + ROW_H / 2)), val, font=F(12 * U, 'SemiBold'), fill=col, anchor='rm')
        ry += ROW_H
    return im.resize((im.width // SS, im.height // SS), Image.LANCZOS), (x0 - 4) * K, (y - 8) * K

import os
OPTS = [('R1', "Bow: header says Arrows"), ('R2', "Gun: Bullets"), ('R3', "Quiver full"), ('R4', "Warlock: Soul shards"),
        ('R5', "Running low (red, as the Low warning)")] if os.environ.get('V') == '3' else \
       [('E', "Hunter with a bow (quiver)"), ('F', "Hunter with a gun (ammo pouch)"),
        ('H', "Quiver full"), ('G', "Warlock (soul bag)")] if os.environ.get('V') == '2' else \
       [('A', "A  Slots free"), ('B', "B  Room for N arrows  (my pick)"), ('C', "C  Both")]
wins = [window(o) for o, _ in OPTS]
w0 = wins[0][0]; G = 30
sheet = Image.new('RGBA', (w0.width + 2 * G if os.environ.get('V') in ('2', '3') else 3 * w0.width + 4 * G, w0.height + 90), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
for i, ((o, t), (im, _, _)) in enumerate(list(zip(OPTS, wins))[:1 if os.environ.get('V') in ('2', '3') else 3]):
    x = G + i * (w0.width + G)
    d.text((x, 20), t, font=F(22, 'SemiBold'), fill=GOLD)
    sheet.alpha_composite(im, (x, 60)) if i < 3 else None
d.text((G, sheet.height - 26), "Game size. Example: 16-slot quiver, stacks of 200, 1,240 arrows. Item art is a placeholder.",
       font=F(15), fill=DIM)
sheet.convert('RGB').save('out_pack_full%s.png' % os.environ.get('V', ''))
# 2x zoom of each footer
zs = []
for (o, t), (im, fx, fy) in zip(OPTS, wins):
    c = im.crop((0, int(56 * K), im.width, int(76 * K))) if os.environ.get('V') == '3' else im.crop((0, int(fy), im.width, int(fy + 70 * K))); zs.append((t, c.resize((c.width * 2, c.height * 2), Image.LANCZOS)))
zw = zs[0][1].width; zh = zs[0][1].height
z = Image.new('RGBA', (zw + 2 * G, len(zs) * (zh + 50) + 20), (16, 18, 24, 255)); zd = ImageDraw.Draw(z)
for i, (t, c) in enumerate(zs):
    zd.text((G, 14 + i * (zh + 50)), t, font=F(20, 'SemiBold'), fill=GOLD); z.alpha_composite(c, (G, 44 + i * (zh + 50)))
z.convert('RGB').save('out_pack_full_zoom%s.png' % os.environ.get('V', '')); print(sheet.size, z.size)
