# Mockup: Blizzard's Reputation window in the Aether look, three interior styles.
import sys; sys.path.insert(0, '/home/claude/mock')
from skins_lib import *
from PIL import Image
import textwrap
SRC = Image.open('/mnt/user-data/uploads/b3ef3650-image.png').convert('RGBA')
HAT = SRC.crop((10, 8, 90, 88))
WORLD = Image.open('/tmp/v4/f_057.png').convert('RGBA')
ROWS = [("H", "Horde"), ("Darkspear Trolls", "Honored", .22, GREEN), ("Orgrimmar", "Honored", .33, GREEN),
        ("Thunder Bluff", "Friendly", .95, GREEN), ("Undercity", "Friendly", .05, GREEN),
        ("H", "Steamwheedle Cartel"), ("Booty Bay", "Neutral", .85, GOLD), ("Everlook", "Neutral", .80, GOLD),
        ("Gadgetzan", "Neutral", .80, GOLD), ("Powderfuse", "Neutral", .80, GOLD), ("Ratchet", "Friendly", .30, GREEN),
        ("H", "Other")]
DESC = ("This tribe of exiled trolls has joined forces with Thrall and the Horde. "
        "They now call Durotar their home, which they share with their orc allies.")

def draw(style, chev3d=False):
    bg = WORLD.crop((300, 250, 300 + 1040, 250 + 860))
    c = Canvas(bg)
    box = (40, 50, 1000, 810)
    c.window(box, "Reputation", alpha=(205 if style == 'C' else 242), chev3d=chev3d)
    c.crest((86, 96), 40, HAT)
    c.close(974, 69)
    # left list
    y = 132; L0, L1 = 72, 572
    for r in ROWS:
        if r[0] == "H":
            if style == 'A': c.header((L0, y, L1, y + 34), r[1])
            elif style == 'B':
                c.text((L0 + 4, y + 17), r[1], 18, GOLD, 'SemiBold', 'lm'); c.text((L1 - 10, y + 16), "–", 20, GOLD, 'Bold', 'mm')
                c.d.line(c.P(L0, y + 32, L1, y + 32), fill=GOLD + (140,), width=SS)
            else:
                c.text((L0 + 4, y + 17), r[1].upper(), 15, GOLD, 'SemiBold', 'lm'); c.text((L1 - 10, y + 16), "–", 20, GOLD, 'Bold', 'mm')
            y += 42; continue
        name, st, fr, col = r
        sel = name == "Darkspear Trolls"
        if style == 'A':
            if sel:
                Lr, d = c.layer(); d.rounded_rectangle(c.P(L0 - 4, y - 5, L1 + 4, y + 37), u(4), fill=BLUE + (48,)); c.over(Lr)
            c.text((L0 + 16, y + 16), name, 17, WHITE, 'Regular', 'lm')
            c.bar((330, y + 5, L1 - 4, y + 27), fr, col, st, pill=True)
            y += 44
        elif style == 'B':
            Lr, d = c.layer()
            d.rounded_rectangle(c.P(L0, y - 3, L1, y + 37), u(5), fill=(NAVY + (255,)) if sel else (22, 30, 46, 255),
                                outline=(BLUE + (255,)) if sel else (40, 60, 95, 255), width=SS)
            c.over(Lr)
            c.text((L0 + 14, y + 17), name, 17, WHITE, 'Regular', 'lm')
            c.bar((330, y + 7, L1 - 12, y + 27), fr, col, st, pill=True)
            y += 44
        else:
            if sel:
                Lr, d = c.layer(); d.rectangle(c.P(L0 - 4, y - 4, L0 - 1, y + 38), fill=GOLD + (255,)); c.over(Lr)
            c.text((L0 + 12, y + 10), name, 17, WHITE, 'Regular', 'lm')
            c.text((L1 - 6, y + 10), st, 15, col, 'SemiBold', 'rm')
            c.bar((L0 + 12, y + 24, L1 - 6, y + 31), fr, col, None, pill=True)
            y += 44
    # scrollbar
    Lr, d = c.layer()
    d.rounded_rectangle(c.P(584, 116, 590, 790), u(3), fill=(30, 45, 70, 255))
    d.rounded_rectangle(c.P(583, 130, 591, 560), u(3), fill=BLUE + (200,))
    c.over(Lr)
    # divider
    Lr, d = c.layer(); d.line(c.P(608, 96, 608, 796), fill=BLUE + (90,), width=SS); c.over(Lr)
    # detail panel
    cx = 800
    c.text((cx, 132), "Darkspear Trolls", 21, WHITE, 'SemiBold', 'mm')
    c.text((cx, 158), "Honored", 17, GREEN, 'Regular', 'mm')
    if style == 'A':
        Lr, d = c.layer(); d.line(c.P(650, 178, 950, 178), fill=GOLD + (120,), width=SS); c.over(Lr)
    c.bar((656, 196, 944, 226), .22, GREEN, "2,651 / 12,000", pill=True)
    yy = 252
    for line in textwrap.wrap(DESC, 34):
        c.text((652, yy), line, 16, DIM if style == 'C' else (205, 210, 220), 'Regular'); yy += 24
    for i, (lab, on) in enumerate((("At War", False), ("Move to Inactive", False), ("Show as Experience Bar", True))):
        c.check((652, 690 + i * 36), lab, on)
    return c.done()

if __name__ == '__main__':
    out = []
    for k, name in (('A', "Reputation: Clean + capsule bars"),):
        im = draw(k); im.save('/tmp/sk/rep_%s.png' % k); out.append(label(im, name))
    W = sum(o.width for o in out); sheet = Image.new('RGB', (W, out[0].height))
    x = 0
    for o in out: sheet.paste(o, (x, 0)); x += o.width
    sheet.save('/tmp/sk/rep_sheet.png'); print(sheet.size)
