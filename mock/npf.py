# Group Finder's 4th button is "New Player Friendly" (Blizzard: leader crown +
# newcomer sprout). Options for its glyph, style A role button.
import math
from PIL import Image, ImageDraw
import roles
from roles import F, GOLD, BLUE, NAVY, SS, check

def sprout(d, cx, cy, r, C):
    d.line([(cx, cy + r * .95), (cx, cy - r * .15)], fill=C, width=int(r * .16))
    for s in (-1, 1):   # two leaves
        pts = []
        for i in range(25):
            t = i / 24; x = s * r * .9 * t; y = -r * .1 - r * .55 * math.sin(t * math.pi) * .6 - r * .35 * t
            pts.append((cx + x, cy + y))
        for i in range(24, -1, -1):
            t = i / 24; x = s * r * .9 * t; y = -r * .1 + r * .3 * math.sin(t * math.pi) * .6 - r * .35 * t
            pts.append((cx + x, cy + y))
        d.polygon(pts, fill=C)
    d.rounded_rectangle([cx - r * .55, cy + r * .75, cx + r * .55, cy + r * 1.0], int(r * .1), fill=C)   # soil

def button(kind, sel, px):
    S = px * SS; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = cy = S / 2; R = S * .44
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=NAVY, outline=(GOLD if sel else BLUE), width=int(S * .045))
    g = GOLD + (255,)
    if kind == 'crown':
        roles.glyph(d, 'leader', cx, cy, R * .52, g)
    elif kind == 'sprout':
        sprout(d, cx, cy, R * .5, g)
    else:                                   # crown with a small sprout badge
        roles.glyph(d, 'leader', cx - R * .1, cy + R * .08, R * .44, g)
        bx, by, br = cx + R * .5, cy - R * .5, R * .3
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=NAVY, outline=g, width=int(S * .02))
        sprout(d, bx, by, br * .6, g)
    if kind != 'none': check(d, int(S * .66), int(S * .66), int(S * .3), sel)
    return im.resize((px, px), Image.LANCZOS)

OPTS = [('crown', "A  Crown (as now)"), ('sprout', "B  Sprout only (my pick)"), ('both', "C  Crown + sprout badge")]
GAME, ZOOM = 99, 198
W = 1260; H = 470
im = Image.new('RGBA', (W, H), roles.PANEL + (255,)); d = ImageDraw.Draw(im)
d.text((30, 20), "Group Finder: New Player Friendly button", font=F(30, 'Medium'), fill=GOLD)
d.text((30, 62), "Top: game size, unticked and ticked. Bottom: 2x zoom.", font=F(18), fill=roles.DIM)
for i, (k, name) in enumerate(OPTS):
    x = 30 + i * 410
    d.text((x, 110), name, font=F(20, 'SemiBold'), fill=GOLD)
    im.alpha_composite(button(k, False, GAME), (x, 150)); im.alpha_composite(button(k, True, GAME), (x + 120, 150))
    im.alpha_composite(button(k, True, ZOOM), (x, 260))
im.convert('RGB').save('out_npf.png'); print(im.size)
