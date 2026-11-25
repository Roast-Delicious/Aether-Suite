# Window crests (the round icon at each window's top-left) and the other
# windows' side tabs as flat gold glyphs on navy (user, Nov 25: the map's
# book "disappears", "replace with a flat version"; "flat art style icons
# for the tabs"). Windows showing your character keep your portrait.
import math
from PIL import Image, ImageDraw
from talent_details import F
from sidetabs_flat import glyph as tabglyph, tab, NAVY, GOLD, BLUE, DIM

def g(d, kind, cx, cy, r, C):
    if kind == 'map':        # folded map with a pin
        w, h = r * .95, r * .7
        xs = [cx - w, cx - w / 3, cx + w / 3, cx + w]
        for i in range(3):
            off = -h * .12 if i % 2 == 0 else h * .12
            d.polygon([(xs[i], cy - h + off), (xs[i + 1], cy - h - off), (xs[i + 1], cy + h - off), (xs[i], cy + h + off)], fill=C if i != 1 else tuple(int(v * .8) for v in C[:3]) + (255,))
        d.ellipse([cx - r * .2, cy - r * .55, cx + r * .2, cy - r * .15], fill=NAVY + (255,))
    elif kind == 'book':     # open book
        for s in (-1, 1):
            d.polygon([(cx, cy - r * .55), (cx + s * r * .95, cy - r * .7), (cx + s * r * .95, cy + r * .55), (cx, cy + r * .7)], fill=C)
        d.line([(cx, cy - r * .55), (cx, cy + r * .7)], fill=NAVY + (255,), width=max(2, int(r * .08)))
    elif kind == 'talents':  # three-node tree
        pts = [(cx, cy - r * .7), (cx - r * .6, cy + r * .5), (cx + r * .6, cy + r * .5)]
        for p in pts[1:]: d.line([pts[0], p], fill=C, width=max(2, int(r * .14)))
        for x, y in pts: d.ellipse([x - r * .25, y - r * .25, x + r * .25, y + r * .25], fill=C)
    elif kind == 'eye':      # group finder: magnifier
        d.ellipse([cx - r * .7, cy - r * .7, cx + r * .3, cy + r * .3], outline=C, width=max(2, int(r * .18)))
        d.line([(cx + r * .2, cy + r * .2), (cx + r * .8, cy + r * .8)], fill=C, width=max(3, int(r * .24)))
    elif kind == 'eyeball':  # Group Finder listing tab: a flat eye
        w = r * .95; h = r * .55; pts = []
        for i in range(41):
            t = i / 40 * math.pi; pts.append((cx - w * math.cos(t), cy - h * math.sin(t)))
        for i in range(41):
            t = i / 40 * math.pi; pts.append((cx + w * math.cos(t), cy + h * math.sin(t)))
        d.polygon(pts, fill=C)
        d.ellipse([cx - r * .38, cy - r * .38, cx + r * .38, cy + r * .38], fill=NAVY + (255,))
        d.ellipse([cx - r * .1, cy - r * .3, cx + r * .1, cy + r * .3], fill=C)
    elif kind == 'friends':  # two people
        for dx, s in ((-r * .35, .85), (r * .35, 1)):
            d.ellipse([cx + dx - r * .25 * s, cy - r * .7 * s, cx + dx + r * .25 * s, cy - r * .2 * s], fill=C)
            d.pieslice([cx + dx - r * .5 * s, cy - r * .1, cx + dx + r * .5 * s, cy + r * .9], 180, 360, fill=C)
    elif kind == 'people':   # three people (raid)
        for dx in (-r * .6, 0, r * .6):
            d.ellipse([cx + dx - r * .2, cy - r * .55, cx + dx + r * .2, cy - r * .15], fill=C)
            d.pieslice([cx + dx - r * .38, cy - r * .05, cx + dx + r * .38, cy + r * .75], 180, 360, fill=C)
    elif kind == 'request':  # person with a plus
        d.ellipse([cx - r * .55, cy - r * .7, cx - r * .05, cy - r * .2], fill=C)
        d.pieslice([cx - r * .8, cy - r * .1, cx + r * .2, cy + r * .9], 180, 360, fill=C)
        d.rectangle([cx + r * .35, cy - r * .5, cx + r * .5, cy + r * .1], fill=C); d.rectangle([cx + r * .12, cy - r * .27, cx + r * .73, cy - r * .12], fill=C)
    elif kind == 'clock':    # recent allies
        d.ellipse([cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8], outline=C, width=max(2, int(r * .16)))
        d.line([(cx, cy), (cx, cy - r * .5)], fill=C, width=max(2, int(r * .14))); d.line([(cx, cy), (cx + r * .4, cy)], fill=C, width=max(2, int(r * .14)))
    elif kind == 'track':    # progress track: flag at the end of a path
        d.line([(cx - r * .8, cy + r * .6), (cx - r * .2, cy), (cx + r * .2, cy + r * .3), (cx + r * .55, cy - r * .2)], fill=C, width=max(2, int(r * .16)))
        d.rectangle([cx + r * .5, cy - r * .9, cx + r * .62, cy - r * .1], fill=C)
        d.polygon([(cx + r * .62, cy - r * .9), (cx + r * .95, cy - r * .72), (cx + r * .62, cy - r * .55)], fill=C)
    else:
        tabglyph(d, kind, cx, cy, r, C)

def crest(kind, S=88):
    im = Image.new('RGBA', (S + 20, S + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(8, 0, -1):
        d.ellipse([10 - k, 10 - k, 10 + S + k, 10 + S + k], outline=BLUE + (int(40 * (9 - k) / 8),), width=2)
    d.ellipse([10, 10, 10 + S, 10 + S], fill=NAVY + (255,), outline=BLUE + (255,), width=3)
    g(d, kind, 10 + S / 2, 10 + S / 2, S * .3, GOLD + (255,))
    return im

def ftab(kind, sel, S=56):
    im = tab('stats', sel, 'B', S)          # frame, glow and notch from the side tab design
    d = ImageDraw.Draw(im); pad = 14
    d.rounded_rectangle([pad + 4, pad + 4, pad + S - 4, pad + S - 4], 6, fill=((28, 58, 104) if sel else NAVY) + (255,))
    g(d, kind, pad + S / 2, pad + S / 2, S * .3, GOLD + (255,))
    return im

W, H = 1120, 600
sheet = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
d.text((20, 14), "Window crests, flat gold on navy", font=F(24, 'SemiBold'), fill=GOLD + (255,))
for i, (k, name) in enumerate((('map', "World Map"), ('book', "Spellbook"), ('talents', "Talents"), ('eyeball', "Group Finder"),
                               ('friends', "Friends"), ('track', "Progress Track"))):
    x = 20 + i * 180
    sheet.alpha_composite(crest(k), (x, 56))
    d.text((x + 54, 172), name, font=F(16), fill=DIM + (255,), anchor='ma')
d.text((20, 214), "Windows about your character (Character, Reputation, Skills...) keep your portrait.", font=F(15), fill=DIM + (255,))
d.text((20, 260), "Other windows' side tabs, same style as the Character tabs (first one open)", font=F(24, 'SemiBold'), fill=GOLD + (255,))
rows = [("Friends", ['friends', 'clock', 'request', 'people']), ("Group Finder", ['eyeball', 'eye', 'people']),
        ("Progress Track", ['track', 'pvp', 'talents'])]
for r, (name, kinds) in enumerate(rows):
    y = 310 + r * 92
    d.text((20, y + 40), name, font=F(17), fill=(235, 238, 245, 255), anchor='lm')
    for i, k in enumerate(kinds):
        sheet.alpha_composite(ftab(k, i == 0), (200 + i * 90, y))
d.text((560, 330), "Friends: friends list, recent allies,\nfriend requests, raid", font=F(15), fill=DIM + (255,))
d.text((560, 422), "Group Finder: list yourself (eye), browse\ngroups (magnifier), who's around (people)", font=F(15), fill=DIM + (255,))
d.text((560, 514), "Progress Track: rewards, challenges, tree", font=F(15), fill=DIM + (255,))
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_crests.png'); print(sheet.size)
