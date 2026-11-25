# Role icon mockups (user, Nov 25 06:33): flat Aether gold glyphs on blue,
# for Group Finder's role buttons (64 UI units) and the leader/newcomer
# button. Original glyphs only (shield, cross, crossed blades, crown).
# Three treatments, each shown in game size (1.55 px/unit) and 2x zoom,
# with the three states: available, selected (gold check), unavailable.
import math
from PIL import Image, ImageDraw, ImageFont
SS = 4
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74)
DEEP = (10, 24, 48); PANEL = (12, 14, 19); WHITE = (235, 238, 245)
DIM = (150, 156, 170)
FD = '/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
def F(px, w='Regular'): return ImageFont.truetype(FD + w + '.ttf', int(px))

def rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

def glyph(d, kind, cx, cy, r, col):
    """r = glyph half-size in px (already supersampled)."""
    if kind == 'tank':        # heater shield with a center rib
        w, h = r * 0.92, r * 1.1
        top = cy - h * 0.92
        pts = [(cx - w, top), (cx + w, top), (cx + w, cy + h * 0.05)]
        for i in range(1, 12):  # curved point at the bottom
            t = i / 12
            pts.append((cx + w * (1 - t) ** 1.2 * math.cos(t * math.pi / 2) ** 0.3,
                        cy + h * 0.05 + (h * 0.95) * math.sin(t * math.pi / 2)))
        pts.append((cx, cy + h))
        pts += [(2 * cx - x, y) for x, y in reversed(pts[3:-1])]
        pts.append((cx - w, cy + h * 0.05))
        d.polygon(pts, fill=col)
        rib = max(2, int(r * 0.12))
        d.rectangle([cx - rib / 2, top + r * 0.22, cx + rib / 2, cy + h * 0.72], fill=DEEP)
    elif kind == 'healer':    # rounded plus
        a, b = r * 0.34, r * 0.98
        d.rounded_rectangle([cx - a, cy - b, cx + a, cy + b], int(a * 0.5), fill=col)
        d.rounded_rectangle([cx - b, cy - a, cx + b, cy + a], int(a * 0.5), fill=col)
    elif kind == 'dps':       # two crossed blades, tips up
        for ang in (-math.pi / 4, math.pi / 4):
            L, bw = r * 1.3, r * 0.17
            blade = [(cx - bw, cy + L * 0.42), (cx - bw, cy - L * 0.72), (cx, cy - L),
                     (cx + bw, cy - L * 0.72), (cx + bw, cy + L * 0.42)]
            guard = [(cx - r * 0.42, cy + L * 0.42), (cx + r * 0.42, cy + L * 0.42),
                     (cx + r * 0.42, cy + L * 0.56), (cx - r * 0.42, cy + L * 0.56)]
            grip = [(cx - bw * 0.75, cy + L * 0.56), (cx + bw * 0.75, cy + L * 0.56),
                    (cx + bw * 0.75, cy + L * 0.78), (cx - bw * 0.75, cy + L * 0.78)]
            for p in (blade, guard, grip):
                d.polygon(rot(p, cx, cy, ang), fill=col)
    elif kind == 'leader':    # three-point crown
        w, h = r * 1.0, r * 0.8
        base = cy + h * 0.55
        pts = [(cx - w, base), (cx - w, cy - h * 0.55), (cx - w * 0.5, cy + h * 0.05),
               (cx, cy - h * 0.95), (cx + w * 0.5, cy + h * 0.05), (cx + w, cy - h * 0.55),
               (cx + w, base)]
        d.polygon(pts, fill=col)
        d.rectangle([cx - w, base + r * 0.12, cx + w, base + r * 0.3], fill=col)

def check(d, x, y, s, on):
    """Aether checkbox (s px, supersampled), gold check when on."""
    d.rounded_rectangle([x, y, x + s, y + s], int(s * 0.18), fill=DEEP + (255,), outline=BLUE, width=max(2, s // 10))
    if on:
        w = max(3, s // 6)
        d.line([(x + s * 0.22, y + s * 0.52), (x + s * 0.43, y + s * 0.74), (x + s * 0.8, y + s * 0.26)],
               fill=GOLD, width=w, joint='curve')

def button(style, kind, state, px):
    """One role button, px = on-screen size of the 64-unit button."""
    S = px * SS
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = cy = S / 2; R = S * 0.44
    off = state == 'off'; sel = state == 'sel'
    gcol = GOLD if not off else (120, 96, 50)
    if style == 'A':      # navy disc, blue ring (matches the minimap ring buttons)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=NAVY, outline=(GOLD if sel else BLUE), width=int(S * 0.045))
    elif style == 'B':    # solid Aether blue disc, deep navy rim
        fill = BLUE if not off else (52, 84, 120)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=fill, outline=(GOLD if sel else DEEP), width=int(S * 0.045))
    elif style == 'C':    # rounded square tile, navy, blue edge
        d.rounded_rectangle([cx - R, cy - R, cx + R, cy + R], int(R * 0.28), fill=NAVY,
                            outline=(GOLD if sel else BLUE), width=int(S * 0.04))
    glyph(d, kind, cx, cy, R * 0.52, gcol + (255,))
    cs = int(S * 0.3)
    check(d, int(S * 0.66), int(S * 0.66), cs, sel)
    return im.resize((px, px), Image.LANCZOS)

KINDS = [('tank', 'Tank'), ('healer', 'Healer'), ('dps', 'Damage'), ('leader', 'Leader')]
STYLES = [('A', 'A  Navy disc, blue ring  (recommended)'),
          ('B', 'B  Solid blue disc'),
          ('C', 'C  Navy rounded square')]
GAME = 99    # 64 UI units x 1.55
ZOOM = 198

W = 1500; rowh = 450; H = 120 + rowh * len(STYLES) + 40
img = Image.new('RGBA', (W, H), PANEL + (255,)); d = ImageDraw.Draw(img)
d.text((40, 30), 'Role icons: flat Aether gold on blue', font=F(34, 'Medium'), fill=GOLD)
d.text((40, 76), 'Top: game size, each in three states (available, selected, unavailable).  '
       'Bottom: 2x zoom.', font=F(20), fill=DIM)
for si, (st, name) in enumerate(STYLES):
    y0 = 120 + si * rowh
    d.text((40, y0), name, font=F(24, 'Medium'), fill=WHITE)
    # game-size: each role in the three states
    x = 40
    for k, kname in KINDS:
        for state in ('on', 'sel', 'off'):
            img.alpha_composite(button(st, k, state, GAME), (x, y0 + 50))
            x += GAME + 6
        x += 22
    # labels under the first state group
    x = 40
    for k, kname in KINDS:
        d.text((x + (GAME * 3 + 12) / 2, y0 + 50 + GAME + 10), kname, font=F(18), fill=DIM, anchor='ma')
        x += (GAME + 6) * 3 + 22
    # 2x zoom: tank available, healer selected, damage available, leader available
    x = 40
    for k, _ in KINDS:
        img.alpha_composite(button(st, k, 'sel' if k == 'healer' else 'on', ZOOM), (x, y0 + 200))
        x += ZOOM + 30
    d.line([(40, y0 + rowh - 20), (W - 40, y0 + rowh - 20)], fill=(40, 60, 90), width=1)
img.convert('RGB').save('/home/claude/aether-repo/mock/out_roles.png')
print('ok')
