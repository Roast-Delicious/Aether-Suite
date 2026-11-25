# Talent icons: the user's own Beast Mastery screenshot (Nov 25, 03:12), in
# three treatments, each done the way the game can do it:
#  A  real icons; Blizzard's yellow borders and counts -> Aether gold
#  B  gold tint: icon:SetDesaturated(true) + SetVertexColor(gold)  (multiply)
#  C  gold on navy: navy square behind, the grayscale icon added on top in
#     gold (SetBlendMode("ADD") + SetVertexColor(gold))
import numpy as np, colorsys
from PIL import Image, ImageDraw, ImageFont
GOLD = np.array([255, 176, 0], float); NAVY = np.array([19, 40, 74], float)
FD = '/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
src = Image.open('/mnt/user-data/uploads/330e1911-image.png').convert('RGB').crop((60, 240, 680, 1060))
base = np.array(src).astype(float)

def hsv(a):
    r, g, b = [a[..., i] / 255 for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return mx, s

def yellow_mask(a):
    """Blizzard's yellow (borders, point counts): R and G high, B low."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 150) & (g > 120) & (b < 90) & (np.abs(r - g) < 80)

def green_mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (g > 150) & (r < 120) & (b < 120)

def to_gold(a):
    """Yellow -> Aether gold, keeping the shading."""
    out = a.copy(); m = yellow_mask(a)
    lum = (a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11) / 230
    out[m] = (GOLD[None, :] * np.clip(lum[m], 0, 1.1)[:, None]).clip(0, 255)
    return out

ICONS = [(265, 185), (355, 185), (175, 275), (265, 275), (355, 275), (175, 365), (265, 365), (355, 365),
         (175, 455), (355, 455), (445, 455), (175, 545), (265, 545), (445, 545), (355, 635), (265, 725)]
SPEC = (208, 68)

def treat(mode):
    a = to_gold(base)
    if mode == 'A': return a
    keep = yellow_mask(base) | green_mask(base)       # borders and counts stay
    lum = (base[..., 0] * .3 + base[..., 1] * .59 + base[..., 2] * .11) / 255
    for cx, cy in ICONS + [SPEC]:
        r = 24 if (cx, cy) != SPEC else 22
        ys, xs = slice(cy - r, cy + r), slice(cx - r, cx + r)
        g = lum[ys, xs][..., None]
        if mode == 'B': new = g * GOLD
        else:          new = np.clip(NAVY + g * GOLD * 1.15, 0, 255)
        k = keep[ys, xs].copy()
        yy, xx = np.mgrid[-r:r, -r:r]
        k &= (xx > 2) & (yy > 0)          # only the point count (bottom-right) keeps its color
        blk = a[ys, xs]
        if (cx, cy) == SPEC:
            yy, xx = np.mgrid[-r:r, -r:r]; circ = (xx ** 2 + yy ** 2) < r * r
            sel = circ & ~k
        else:
            sel = ~k
        blk[sel] = new[sel]
        a[ys, xs] = blk
    return a

def panel(mode, title, sub):
    im = Image.fromarray(treat(mode).astype(np.uint8))
    im = im.crop((110, 20, 520, 790))
    out = Image.new('RGB', (im.width, im.height + 70), (16, 18, 24)); d = ImageDraw.Draw(out)
    d.text((10, 8), title, font=ImageFont.truetype(FD + 'SemiBold.ttf', 24), fill=(255, 176, 0))
    d.text((10, 40), sub, font=ImageFont.truetype(FD + 'Regular.ttf', 16), fill=(170, 176, 188))
    out.paste(im, (0, 70)); return out

ps = [panel('A', "A  Real icons", "Blizzard's art, gold borders  (recommended)"),
      panel('B', "B  Gold tint", "grayscale icon x gold"),
      panel('C', "C  Gold on navy", "navy square + gold glow of the icon")]
W = sum(p.width for p in ps) + 40; H = ps[0].height + 20
sheet = Image.new('RGB', (W, H), (16, 18, 24)); x = 10
for p in ps: sheet.paste(p, (x, 10)); x += p.width + 10
sheet.save('/home/claude/aether-repo/mock/out_talent_tint.png'); print(sheet.size)
