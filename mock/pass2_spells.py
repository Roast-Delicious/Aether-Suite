# Second-pass mockup 3: Talents and Spellbook (PlayerSpellsFrame), crops of
# the top-left of each page at game size (the window is 1218 units wide).
import math, random
from skins_lib import *
from pass2_rep import backdrop, icon
from pass2_friends import searchbox, dropdown
from PIL import Image, ImageDraw, ImageFilter

def winbtn(c, cx, cy, kind):
    s = 11; x0, y0, x1, y1 = c.P(cx - s, cy - s, cx + s, cy + s)
    c.d.rounded_rectangle([x0, y0, x1, y1], u(3), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
    if kind == 'min':
        c.d.line(c.P(cx - 5, cy + 4, cx + 5, cy + 4), fill=WHITE + (255,), width=2 * SS)
    else:
        c.d.rectangle(c.P(cx - 5, cy - 5, cx + 5, cy + 5), outline=WHITE + (255,), width=2 * SS)

def spell_icon(c, box, hue, round_=False):
    """Stand-in for a spell icon (the game's own icons stay)."""
    random.seed(hue)
    col = [(140, 70, 40), (60, 110, 60), (70, 80, 140), (130, 110, 60), (110, 60, 120)][hue % 5]
    L, d = c.layer(); x0, y0, x1, y1 = c.P(*box)
    if round_: d.ellipse([x0, y0, x1, y1], fill=col + (255,))
    else: d.rectangle([x0, y0, x1, y1], fill=col + (255,))
    B = Image.new('RGBA', L.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
    for _ in range(6):
        rx, ry = random.randint(x0, x1), random.randint(y0, y1); rr = random.randint(4, 12) * SS
        bd.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=tuple(min(255, v + 40) for v in col) + (120,))
    m = Image.new('L', L.size, 0); md = ImageDraw.Draw(m)
    (md.ellipse if round_ else md.rectangle)([x0, y0, x1, y1], fill=255)
    B.putalpha(Image.fromarray(np.minimum(np.array(B.split()[3]), np.array(m))))
    L.alpha_composite(B)
    c.over(L)

def node(c, cx, cy, state, hue, pts=None):
    """Talent node, 40 units: square icon; border by state. Maxed (Blizzard
    yellow) -> Aether gold; partial -> green; available -> gray; locked dim."""
    s = 31
    spell_icon(c, (cx - s + 3, cy - s + 3, cx + s - 3, cy + s - 3), hue)
    col = {'max': GOLD, 'part': GREEN, 'avail': (170, 176, 188), 'lock': (70, 74, 84)}[state]
    x0, y0, x1, y1 = c.P(cx - s, cy - s, cx + s, cy + s)
    if state == 'lock':
        L, d = c.layer(); d.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 150)); c.over(L)
    c.d.rounded_rectangle([x0, y0, x1, y1], u(3), outline=col + (255,), width=3 * SS)
    if pts:
        c.d.rounded_rectangle(c.P(cx + 10, cy + 16, cx + 40, cy + 36), u(3), fill=(8, 12, 22, 255), outline=col + (255,), width=SS)
        c.text((cx + 25, cy + 26), pts, 13, col, 'SemiBold', 'mm')

def arrow(c, x, y0, y1, col):
    c.d.line(c.P(x, y0, x, y1 - 8), fill=col + (255,), width=3 * SS)
    c.d.polygon([tuple(c.P(*p)) for p in [(x - 8, y1 - 10), (x + 8, y1 - 10), (x, y1)]], fill=col + (255,))

def specring(c, cx, cy, name, pts):
    R = 40; X0, Y0, X1, Y1 = c.P(cx - R, cy - R, cx + R, cy + R)
    c.d.ellipse([X0, Y0, X1, Y1], fill=NAVY + (255,), outline=BLUE + (255,), width=2 * SS)
    spell_icon(c, (cx - 27, cy - 27, cx + 27, cy + 27), len(name), round_=True)
    c.d.ellipse([X0, Y0, X1, Y1], outline=BLUE + (255,), width=2 * SS)
    c.d.rounded_rectangle(c.P(cx - 17, cy + 28, cx + 17, cy + 50), u(3), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
    c.text((cx, cy + 39), pts, 14, WHITE, 'SemiBold', 'mm')
    c.text((cx + 54, cy - 6), name, 19, GOLD, 'SemiBold', 'lm')
    c.d.line(c.P(cx + 54, cy + 14, cx + 470, cy + 14), fill=BLUE + (150,), width=SS)

def classart(w, h):
    """Stand-in for the class background art (it stays)."""
    im = Image.new('RGB', (w, h), (30, 42, 30)); d = ImageDraw.Draw(im); random.seed(3)
    for _ in range(60):
        x, y, r = random.randint(0, w), random.randint(0, h), random.randint(30, 140)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(random.randint(30, 60), random.randint(50, 80), random.randint(30, 50)))
    return im.filter(ImageFilter.GaussianBlur(30)).convert('RGBA')

def talents():
    W, H = 960, 720
    c = Canvas(backdrop(W, H))
    box = (40, 46, 40 + 1888, 46 + 1100)      # runs off the crop (right, bottom)
    c.window(box, "", chevrons='l')
    c.text((W - 40, box[1] + 19), "Talents", 17, GOLD, 'SemiBold', 'rm')
    c.crest((86, 92), 40); icon(c, 'skill', 86, 92, 22, GOLD)
    # class art area (kept), framed with a blue line instead of the bronze border
    art = classart(W - 62, H - 120); c.over(art.resize((art.width * SS, art.height * SS)), (62, 118))
    L, d = c.layer(); d.rectangle(c.P(62, 118, W, H), fill=(6, 10, 18, 110)); c.over(L)
    c.d.line(c.P(62, 118, W, 118), fill=BLUE + (255,), width=SS)
    # spec headers
    specring(c, 120, 172, "Beast Mastery", "21")
    c.d.line(c.P(62, 236, W, 236), fill=BLUE + (110,), width=SS)
    # nodes: a small part of the tree with every state
    grid = [(160, 300, 'max', 1, '5/5'), (300, 300, 'max', 2, '2/2'), (440, 300, 'part', 3, '3/5'),
            (160, 430, 'max', 4, '5/5'), (300, 430, 'avail', 5, None), (440, 430, 'part', 6, '1/2'),
            (300, 560, 'lock', 7, None), (440, 560, 'lock', 8, None), (580, 430, 'avail', 9, None)]
    arrow(c, 300, 333, 397, GOLD); arrow(c, 300, 463, 527, (90, 94, 104))
    for x, y, st, h, p in grid: node(c, x, y, st, h, p)
    # unspent box, search, apply (bottom-right area of the real window, shown here)
    c.d.rounded_rectangle(c.P(680, 280, 900, 340), u(5), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
    c.text((700, 310), "Unspent", 15, DIM, 'Regular', 'lm'); c.text((880, 310), "2", 26, GOLD, 'SemiBold', 'rm')
    searchbox(c, (680, 370, 900, 404), "Search")
    c.button((680, 430, 900, 466), "Apply Changes")
    # legend
    lx, ly = 640, 520
    for i, (col, t) in enumerate(((GOLD, "Maxed (was Blizzard yellow)"), (GREEN, "Has points"), ((170, 176, 188), "Can take"), ((70, 74, 84), "Locked"))):
        c.d.rounded_rectangle(c.P(lx, ly + i * 34, lx + 20, ly + i * 34 + 20), u(2), outline=col + (255,), width=3 * SS)
        c.text((lx + 32, ly + i * 34 + 10), t, 15, WHITE, 'Regular', 'lm')
    return c.done()

def spellbook():
    W, H = 960, 720
    c = Canvas(backdrop(W, H))
    box = (40, 46, 40 + 1779, 46 + 1116)
    c.window(box, "", chevrons='l')
    c.text((W - 40, box[1] + 19), "Spellbook", 17, GOLD, 'SemiBold', 'rm')
    winbtn(c, W - 230, box[1] + 19, 'min')
    c.crest((86, 92), 40); icon(c, 'skill', 86, 92, 22, GOLD)
    # square category tabs: navy squares, gold edge on the active one
    for i in range(6):
        x = 150 + i * 74; act = i == 0
        x0, y0, x1, y1 = c.P(x, 74, x + 64, 74 + 58)
        c.d.rounded_rectangle([x0, y0, x1, y1], u(5), fill=NAVY + (255,), outline=(GOLD if act else BLUE) + (255,), width=SS * (2 if act else 1))
        spell_icon(c, (x + 8, 80, x + 56, 126), 10 + i)
        c.d.rounded_rectangle([x0, y0, x1, y1], u(5), outline=(GOLD if act else BLUE) + (255,), width=SS * (2 if act else 1))
    searchbox(c, (640, 86, 900, 120), "Search")
    # the page: navy, the book's middle shown as a thin blue line
    c.d.line(c.P(62, 150, W, 150), fill=BLUE + (255,), width=SS)
    c.text((90, 190), "General", 21, GOLD, 'SemiBold', 'lm')
    c.d.line(c.P(90, 212, 760, 212), fill=BLUE + (170,), width=SS)
    spells = [("Attack", "", False), ("Berserking", "Racial", False), ("Dual Wield", "Passive", True),
              ("Parry", "Passive", True), ("Regeneration", "Racial Passive", True), ("Beast Training", "", False),
              ("Armor Proficiency", "Passive", True), ("Dodge", "Passive", True)]
    for i, (n, sub, passive) in enumerate(spells):
        col, row = i % 2, i // 2
        x, y = 90 + col * 340, 240 + row * 96
        L, d = c.layer(); d.rounded_rectangle(c.P(x, y, x + 320, y + 78), u(6), fill=NAVY + (150,)); c.over(L)
        ix, iy = x + 12, y + 11
        spell_icon(c, (ix, iy, ix + 56, iy + 56), i, round_=passive)
        if passive: c.d.ellipse(c.P(ix - 2, iy - 2, ix + 58, iy + 58), outline=BLUE + (255,), width=2 * SS)
        else: c.d.rounded_rectangle(c.P(ix - 2, iy - 2, ix + 58, iy + 58), u(3), outline=BLUE + (255,), width=2 * SS)
        c.text((x + 84, y + (30 if sub else 39)), n, 17, WHITE, 'SemiBold', 'lm')
        if sub: c.text((x + 84, y + 54), sub, 14, DIM, 'Regular', 'lm')
    c.d.line(c.P(800, 160, 800, H), fill=BLUE + (120,), width=SS)
    # page arrows: our chevrons
    c.text((610, 650), "Page 1 / 3", 15, DIM, 'Regular', 'rm')
    for k, x in ((0, 640), (1, 690)):
        c.d.rounded_rectangle(c.P(x, 634, x + 34, 666), u(4), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
        pts = [(x + 21, 642), (x + 13, 650), (x + 21, 658)] if k == 0 else [(x + 13, 642), (x + 21, 650), (x + 13, 658)]
        c.d.line([tuple(c.P(*p)) for p in pts], fill=GOLD + (255,), width=3 * SS, joint='curve')
    return c.done()

if __name__ == '__main__':
    a = label(talents(), "3a  Talents (top-left of the window, game size)")
    b = label(spellbook(), "3b  Spellbook (top-left of the window, game size)")
    out = Image.new('RGB', (a.width, a.height + b.height)); out.paste(a, (0, 0)); out.paste(b, (0, a.height))
    out.save('/home/claude/aether-repo/mock/out_p2_spells.png'); print(out.size)
