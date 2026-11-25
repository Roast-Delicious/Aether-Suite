# Second-pass mockup 1: Character window, Reputation page, in the Aether look
# with the shared pieces: side tabs, header strips, capsule rep bars, blue
# selected row, stronger blue scroll bar, detail panel, checkboxes.
# Scale: 1.55 px per UI unit (Character window 631x484 units).
import math
from skins_lib import *
from PIL import Image, ImageFilter, ImageEnhance

SHOT = '/mnt/user-data/uploads/6245b0e9-image.png'

def backdrop(w, h):
    im = Image.open(SHOT).convert('RGB')
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS).crop((0, 0, w, h))
    im = im.filter(ImageFilter.GaussianBlur(5))
    return ImageEnhance.Brightness(im).enhance(0.55).convert('RGBA')

def sel_row(c, box):
    """Blue selected / hover row: soft blue fill, blue edge, gold left accent."""
    L, d = c.layer(); x0, y0, x1, y1 = c.P(*box)
    d.rounded_rectangle([x0, y0, x1, y1], u(4), fill=BLUE + (48,), outline=BLUE + (150,), width=SS)
    d.rounded_rectangle([x0 + SS, y0 + 3 * SS, x0 + 4 * SS, y1 - 3 * SS], SS, fill=GOLD + (255,))
    c.over(L)

def scrollbar(c, x, y0, y1, t0, t1):
    L, d = c.layer()
    X0, Y0, X1, Y1 = c.P(x - 3, y0, x + 3, y1)
    d.rounded_rectangle([X0, Y0, X1, Y1], 3 * SS, fill=(14, 28, 52, 255))
    X0, Y0, X1, Y1 = c.P(x - 3, t0, x + 3, t1)
    d.rounded_rectangle([X0, Y0, X1, Y1], 3 * SS, fill=BLUE + (235,))
    c.over(L)
    c.tri(x, y0 - 9, 5, BLUE); c.d.polygon([tuple(c.P(*p)) for p in [(x - 5, y1 + 6), (x + 5, y1 + 6), (x, y1 + 12)]], fill=BLUE + (255,))
    c.d.polygon([tuple(c.P(*p)) for p in [(x - 5, y0 - 6), (x + 5, y0 - 6), (x, y0 - 12)]], fill=BLUE + (255,))

def sidetab(c, x, y, glyph, selected=False, hover=False):
    """Side tab (55 units): navy, rounded on the outer side, blue edge;
    selected = gold edge + brighter fill + gold notch on the window side."""
    w, h = 62, 80
    L, d = c.layer(); X0, Y0, X1, Y1 = c.P(x, y, x + w, y + h)
    fill = (28, 58, 104) if selected else ((22, 46, 84) if hover else NAVY)
    d.rounded_rectangle([X0 - u(8), Y0, X1, Y1], u(7), fill=fill + (250,),
                        outline=(GOLD if selected else BLUE) + (255,), width=SS * (2 if selected else 1))
    if selected:
        d.rectangle([X0 - u(8), Y0 + u(8), X0 + SS * 2, Y1 - u(8)], fill=GOLD + (255,))
    c.over(L)
    icon(c, glyph, x + w / 2 + 2, y + h / 2, 18, WHITE if selected else (190, 205, 225))

def icon(c, kind, cx, cy, r, col):
    """Stand-ins for the game's own tab icons (those stay Blizzard's)."""
    d = c.d; P = lambda *v: c.P(*v); C = col + (255,)
    if kind == 'char':
        d.ellipse(P(cx - r * .38, cy - r * .9, cx + r * .38, cy - r * .14), fill=C)
        d.pieslice(P(cx - r * .8, cy - r * .05, cx + r * .8, cy + r * 1.5), 180, 360, fill=C)
    elif kind == 'rep':
        d.rectangle(P(cx - r * .7, cy - r * .9, cx - r * .55, cy + r), fill=C)
        d.polygon([tuple(P(cx - r * .55, cy - r * .9)), tuple(P(cx + r * .8, cy - r * .55)), tuple(P(cx - r * .55, cy - r * .1))], fill=C)
    elif kind == 'skill':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; rr = r * (0.95 if i % 2 == 0 else 0.42)
            pts.append(tuple(P(cx + rr * math.cos(a), cy + rr * math.sin(a))))
        d.polygon(pts, fill=C)
    elif kind == 'pvp':
        d.polygon([tuple(P(cx - r * .75, cy - r * .85)), tuple(P(cx + r * .75, cy - r * .85)), tuple(P(cx + r * .75, cy)),
                   tuple(P(cx, cy + r)), tuple(P(cx - r * .75, cy))], fill=C)
    elif kind == 'stats':
        for i, hgt in enumerate((.6, 1.2, .9, 1.6)):
            x = cx - r * .8 + i * r * .45
            d.rectangle(P(x, cy + r * .8 - r * hgt, x + r * .3, cy + r * .8), fill=C)
    elif kind == 'coin':
        d.ellipse(P(cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8), outline=C, width=int(r * .22 * SS))
        d.ellipse(P(cx - r * .28, cy - r * .28, cx + r * .28, cy + r * .28), fill=C)

ROWS = [("H", "Horde"), ("Darkspear Trolls", "Honored", .22, GREEN), ("Orgrimmar", "Honored", .33, GREEN),
        ("Thunder Bluff", "Friendly", .95, GREEN), ("Undercity", "Friendly", .05, GREEN),
        ("H", "Steamwheedle Cartel"), ("Booty Bay", "Neutral", .85, GOLD), ("Everlook", "Neutral", .80, GOLD),
        ("Gadgetzan", "Neutral", .80, GOLD), ("Ratchet", "Friendly", .30, GREEN),
        ("H", "Other"), ("Magram Clan Centaur", "Hated", .40, RED), ("Gelkis Clan Centaur", "Honored", .55, GREEN)]

def rep():
    W, H = 1180, 850
    c = Canvas(backdrop(W, H))
    box = (40, 46, 40 + 978, 46 + 750)
    c.window(box, "Reputation", chevrons='tbl')
    c.crest((86, 92), 40)
    icon(c, 'char', 86, 96, 20, GOLD)
    c.close(box[2] - 26, box[1] + 19)
    # side tabs (Forever's CharacterFrameModeTab1-6), right side, outside
    for i, (g, s) in enumerate([('char', False), ('rep', True), ('skill', False), ('pvp', False), ('stats', False), ('coin', False)]):
        sidetab(c, box[2] + 4, box[1] + 70 + i * 92, g, selected=s, hover=(i == 2))
    # list pane
    L0, L1 = box[0] + 22, box[0] + 22 + 555
    y = box[1] + 84
    c.d.line(c.P(L0, y - 6, L1 + 14, y - 6), fill=BLUE + (120,), width=SS)
    for r in ROWS:
        if r[0] == "H":
            c.header((L0, y, L1, y + 40), r[1]); y += 46; continue
        name, standing, frac, col = r
        if name == "Orgrimmar": sel_row(c, (L0, y, L1, y + 44))
        c.text((L0 + 16, y + 22), name, 16, WHITE, 'Regular', 'lm')
        c.bar((L1 - 258, y + 10, L1 - 10, y + 34), frac, col, standing, pill=True)
        y += 46
    c.d.line(c.P(L0, box[3] - 28, L1 + 14, box[3] - 28), fill=BLUE + (120,), width=SS)
    scrollbar(c, L1 + 14, box[1] + 92, box[3] - 40, box[1] + 92, box[1] + 440)
    # detail pane
    D0, D1 = L1 + 44, box[2] - 22
    c.d.line(c.P(D0 - 14, box[1] + 40, D0 - 14, box[3] - 18), fill=BLUE + (90,), width=SS)
    c.text(((D0 + D1) / 2, box[1] + 64), "Orgrimmar", 20, GOLD, 'SemiBold', 'mm')
    c.text(((D0 + D1) / 2, box[1] + 90), "Horde", 15, DIM, 'Regular', 'mm')
    c.d.line(c.P(D0 + 10, box[1] + 108, D1 - 10, box[1] + 108), fill=BLUE + (200,), width=SS)
    txt = ["The orcs of Orgrimmar,", "led by Warchief Thrall,", "make their home in the", "harsh land of Durotar."]
    for i, t in enumerate(txt): c.text((D0 + 6, box[1] + 132 + i * 24), t, 15, WHITE, 'Regular', 'lm')
    c.bar((D0 + 6, box[1] + 520, D1 - 6, box[1] + 548), .33, GREEN, "Honored  4,050 / 12,000", pill=True)
    c.check((D0 + 6, box[1] + 580), "At War", False)
    c.check((D0 + 6, box[1] + 614), "Move to Inactive", False)
    c.check((D0 + 6, box[1] + 648), "Show as Experience Bar", True)
    return c.done()

if __name__ == '__main__':
    im = rep(); im = label(im, "1  Character window: Reputation (game size)")
    im.save('/home/claude/aether-repo/mock/out_p2_rep.png'); print(im.size)
