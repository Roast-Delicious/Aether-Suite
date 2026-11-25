# Vendor (MerchantFrame) spruce-up: user, Nov 25 — "simplistic, spruce it
# up", tabs "all over the place", text/images too dark, repair icons not
# visible, "make the repair/sell art flat". Two layouts, shown at game size.
from PIL import Image, ImageDraw
from talent_details import F
from sidetabs_flat import NAVY, GOLD, BLUE, DIM

K = 1.55                       # px per UI unit
TEXT = (235, 238, 245); BG = (10, 16, 28); ROW = (24, 46, 82); EDGE = (40, 70, 115)
Q = {2: (30, 255, 0), 3: (0, 112, 221), 4: (163, 53, 238), 1: (235, 238, 245)}
ITEMS = [("Simple Flour", 1, "25c", 'sack'), ("Mild Spices", 1, "10c", 'jar'), ("Refreshing Spring Water", 1, "25c", 'flask'),
         ("Ice Cold Milk", 1, "1s 25c", 'flask'), ("Tough Hunk of Bread", 1, "25c", 'bread'), ("Fishing Pole", 1, "23c", 'pole'),
         ("Heavy Linen Bandage", 2, "1s", 'bandage'), ("Thieves' Tools", 1, "18s", 'box'), ("Coarse Thread", 1, "9c", 'spool'),
         ("Mithril Pick", 3, "4g 20s", 'pick')]

def icon(d, kind, x, y, s):
    """Placeholder item art: Blizzard's real icons show in game."""
    cols = {'sack': (196, 170, 120), 'jar': (190, 90, 50), 'flask': (120, 180, 230), 'bread': (200, 140, 70), 'pole': (150, 110, 70),
            'bandage': (230, 225, 210), 'box': (110, 100, 90), 'spool': (220, 210, 180), 'pick': (170, 190, 210)}
    c = cols[kind]; d.rectangle([x, y, x + s, y + s], fill=(40, 34, 30))
    d.ellipse([x + s * .2, y + s * .2, x + s * .8, y + s * .8], fill=c)
    d.ellipse([x + s * .3, y + s * .26, x + s * .5, y + s * .42], fill=tuple(min(255, v + 50) for v in c))

def frame(d, x, y, s, qual):
    col = Q[qual] if qual >= 2 else BLUE
    d.rectangle([x - 2, y - 2, x + s + 2, y + s + 2], outline=col, width=2)

def coin(d, x, y, r, kind):
    c = {'g': GOLD, 's': (200, 206, 216), 'c': (196, 112, 60)}[kind]
    d.ellipse([x - r, y - r, x + r, y + r], fill=c)

def price(d, x, y, txt, f, anchor='ls'):
    # "1s 25c" -> digits in light text + flat coin dots, right-aligned when anchor='rs'
    parts = txt.split(); w = 0; segs = []
    for p in parts:
        n, k = p[:-1], p[-1]; tw = d.textlength(n, font=f); segs.append((n, k, tw)); w += tw + 14
    if anchor == 'rs': x -= w
    for n, k, tw in segs:
        d.text((x, y), n, font=f, fill=TEXT, anchor='ls'); coin(d, x + tw + 6, y - 5, 4, k); x += tw + 14

import math
def _rot(pts, cx, cy, r, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return [(cx + r * (x * c - y * s_), cy + r * (x * s_ + y * c)) for x, y in pts]

def glyph_img(kind, S, C, SS=4):
    """Flat gold glyph, drawn at SS x then reduced for clean edges."""
    N = S * SS; im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = cy = N / 2; r = N * .42; navy = NAVY + (255,)
    def hammer(cx, cy, r):
        a = -math.pi / 4
        d.polygon(_rot([(-.09, -.15), (.09, -.15), (.09, 1.0), (-.09, 1.0)], cx, cy, r, a), fill=C)           # handle
        d.polygon(_rot([(-.55, -.62), (.45, -.62), (.45, -.18), (-.55, -.18)], cx, cy, r, a), fill=C)        # head
        d.polygon(_rot([(.45, -.55), (.62, -.5), (.62, -.3), (.45, -.25)], cx, cy, r, a), fill=C)            # striking face
    def anvil(cx, cy, r):
        d.polygon([(cx - r * .95, cy - r * .45), (cx + r * .75, cy - r * .45), (cx + r * .75, cy - r * .05),
                   (cx + r * .3, cy + r * .1), (cx + r * .3, cy + r * .45), (cx + r * .6, cy + r * .75),
                   (cx - r * .6, cy + r * .75), (cx - r * .3, cy + r * .45), (cx - r * .3, cy + r * .1),
                   (cx - r * .6, cy - r * .05)], fill=C)
        d.polygon([(cx - r * .95, cy - r * .45), (cx - r * .6, cy - r * .05), (cx - r * .6, cy - r * .45)], fill=C)
    if kind == 'repair':
        hammer(cx + r * .12, cy - r * .12, r * .95)
    elif kind == 'repairall':
        anvil(cx, cy + r * .3, r * .9)
        hammer(cx + r * .3, cy - r * .55, r * .55)
    elif kind == 'guild':
        d.polygon([(cx - r * .8, cy - r * .85), (cx + r * .8, cy - r * .85), (cx + r * .8, cy + r * .1),
                   (cx, cy + r * .95), (cx - r * .8, cy + r * .1)], fill=C)                                     # shield
        d.polygon([(cx - r * .62, cy - r * .68), (cx + r * .62, cy - r * .68), (cx + r * .62, cy + r * .02),
                   (cx, cy + r * .73), (cx - r * .62, cy + r * .02)], fill=navy)
        hammer(cx, cy - r * .08, r * .58)
    elif kind == 'junk':     # coin sack
        d.ellipse([cx - r * .8, cy - r * .35, cx + r * .8, cy + r * .95], fill=C)
        d.polygon([(cx - r * .3, cy - r * .3), (cx + r * .3, cy - r * .3), (cx + r * .15, cy - r * .55), (cx - r * .15, cy - r * .55)], fill=C)
        d.polygon([(cx - r * .45, cy - r * .95), (cx + r * .45, cy - r * .95), (cx + r * .15, cy - r * .55), (cx - r * .15, cy - r * .55)], fill=C)
        d.ellipse([cx - r * .3, cy + r * .05, cx + r * .3, cy + r * .65], outline=navy, width=int(r * .12))
        d.ellipse([cx - r * .12, cy + r * .23, cx + r * .12, cy + r * .47], fill=C)
    return im.resize((S, S), Image.LANCZOS)

def tbutton(im, kind, x, y, s):
    big = Image.new('RGBA', (s * 4 + 4, s * 4 + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    d.rounded_rectangle([2, 2, s * 4, s * 4], 20, fill=NAVY + (255,), outline=BLUE + (255,), width=8)
    big = big.resize((s + 1, s + 1), Image.LANCZOS)
    g = glyph_img(kind, int(s * .74), GOLD + (255,)); big.alpha_composite(g, ((s + 1 - g.width) // 2, (s + 1 - g.height) // 2))
    im.alpha_composite(big, (int(x), int(y)))

def tabs(d, x, y, sel, w=110, h=30):
    for i, t in enumerate(("Merchant", "Buyback")):
        X = x + i * (w + 6); on = i == sel
        d.rounded_rectangle([X, y, X + w, y + h], 6, fill=(ROW if on else NAVY), outline=(GOLD if on else EDGE), width=2)
        d.text((X + w / 2, y + h / 2), t, font=F(15, 'SemiBold' if on else 'Regular'), fill=(GOLD if on else DIM), anchor='mm')

def window(layout):
    W, H = int(336 * K), int(444 * K)
    im = Image.new('RGBA', (W + 20, H + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W, H], 8, fill=BG, outline=BLUE, width=2)
    d.rectangle([2, 2, W - 2, 40], fill=NAVY); d.line([(2, 41), (W - 2, 41)], fill=GOLD, width=2)
    d.text((W / 2, 22), "Innkeeper Farley", font=F(18, 'SemiBold'), fill=GOLD, anchor='mm')
    d.text((W - 20, 22), "x", font=F(18), fill=TEXT, anchor='mm')
    fs, fp = F(14), F(13)
    if layout == 'grid':
        tw, th = (W - 36) / 2, 64
        for i, (n, q, p, k) in enumerate(ITEMS):
            c, r = i % 2, i // 2; x = 12 + c * (tw + 12); y = 54 + r * (th + 10)
            d.rounded_rectangle([x, y, x + tw, y + th], 6, fill=ROW, outline=EDGE, width=1)
            s = 42; icon(d, k, x + 10, y + 11, s); frame(d, x + 10, y + 11, s, q)
            nm = n if d.textlength(n, font=fs) < tw - 66 else n[:16] + "..."
            d.text((x + 62, y + 24), nm, font=fs, fill=Q[q] if q >= 2 else TEXT, anchor='ls')
            price(d, x + 62, y + 48, p, fp)
        ybot = 54 + 5 * (th + 10)
    else:
        rh = 40
        for i, (n, q, p, k) in enumerate(ITEMS):
            y = 52 + i * (rh + 4)
            d.rounded_rectangle([12, y, W - 12, y + rh], 5, fill=ROW if i % 2 == 0 else (19, 37, 68))
            s = 30; icon(d, k, 20, y + 5, s); frame(d, 20, y + 5, s, q)
            d.text((62, y + rh / 2), n, font=fs, fill=Q[q] if q >= 2 else TEXT, anchor='lm')
            price(d, W - 22, y + rh / 2 + 5, p, fp, anchor='rs')
        ybot = 52 + 10 * (rh + 4)
    # page row: our chevrons in gold
    d.text((W / 2, ybot + 14), "Page 1 of 2", font=F(14), fill=TEXT, anchor='mm')
    for sx, dirn in ((W / 2 - 80, -1), (W / 2 + 80, 1)):
        d.polygon([(sx - dirn * 6, ybot + 6), (sx + dirn * 6, ybot + 14), (sx - dirn * 6, ybot + 22)], fill=GOLD)
    # bottom bar
    yb = H - 66; d.line([(12, yb - 8), (W - 12, yb - 8)], fill=EDGE, width=1)
    for i, k in enumerate(('repairall', 'repair', 'guild', 'junk')):
        tbutton(im, k, 14 + i * 50, yb, 42)
    d.text((W - 16, yb + 14), "Repair: 2s 40c", font=F(13), fill=DIM, anchor='rm')
    price(d, W - 16, yb + 42, "127g 34s 9c", F(15), anchor='rs')
    tabs(d, 14, H + 6, 0)
    return im

a, b = window('grid'), window('list')
G = 40; W = a.width + b.width + G * 3; H = a.height + 120
sheet = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
d.text((G, 18), "A  Cards (Blizzard's 2x5 grid, restyled)  (my pick)", font=F(20, 'SemiBold'), fill=GOLD)
d.text((G * 2 + a.width, 18), "B  List (one row per item)", font=F(20, 'SemiBold'), fill=GOLD)
sheet.alpha_composite(a, (G, 60)); sheet.alpha_composite(b, (G * 2 + a.width, 60))
d.text((G, H - 44), "Buttons, left to right: repair all, repair one item, guild repair, sell junk. Item art is a placeholder;"
       " Blizzard's icons show in game.", font=F(14), fill=DIM)
d.text((G, H - 22), "Frames take the item's quality colour (green and up), blue otherwise. Empty slots are hidden.", font=F(14), fill=DIM)
sheet.convert('RGB').save('out_vendor.png')
# zoom on the buttons
z = Image.new('RGBA', (760, 250), (16, 18, 24, 255)); zd = ImageDraw.Draw(z)
for i, (k, n) in enumerate((('repairall', "Repair all"), ('repair', "Repair item"), ('guild', "Guild repair"), ('junk', "Sell junk"))):
    tbutton(z, k, 30 + i * 185, 30, 140); zd.text((100 + i * 185, 205), n, font=F(18), fill=DIM + (255,), anchor='ma')
z.convert('RGB').save('out_vendor_zoom.png'); print(sheet.size)
