# Talent details (user, Nov 25 07:03): 2 arrows thicker and 3D (same bevel
# lighting as the gold accents: light from the top-right), 3 point counts in
# the frame color, 4 the "can spend here" glow in blue instead of green.
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import talent_states as TS
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74); GRAY = (130, 134, 144)
FD = '/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
def F(n, w='Regular'): return ImageFont.truetype(FD + w + '.ttf', n)

def bevel(mask, base, light=(0.62, -0.62)):
    """3D bevel ridge on a mask, lit from the top-right; the color only
    darkens, or lifts toward a pale tint of itself at the brightest spot."""
    n = mask.shape[0]
    d = cv2.distanceTransform(mask, cv2.DIST_L2, 5).astype(np.float32)
    w = max(float(d.max()), 1); hgt = cv2.GaussianBlur(d / w, (0, 0), 2)
    gy, gx = np.gradient(hgt * w * 0.9)
    nx, ny, nz = -gx, -gy, np.ones_like(gx); ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    L = np.array([light[0], light[1], 0.62]); L /= np.linalg.norm(L)
    diff = np.clip((nx * L[0] + ny * L[1] + nz * L[2]) / ln, 0, 1)
    H = L + np.array([0, 0, 1]); H /= np.linalg.norm(H)
    spec = np.clip((nx * H[0] + ny * H[1] + nz * H[2]) / ln, 0, 1) ** 30
    k = (0.58 + 0.62 * diff)[..., None]
    b = np.array(base, np.float32); pale = b + (255 - b) * 0.75
    col = b * np.minimum(k, 1.0)
    s = np.clip(spec * 0.9 + np.clip(k[..., 0] - 1, 0, 1) * 1.5, 0, 0.8)[..., None]
    col = col * (1 - s) + pale * s
    alpha = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.2)
    out = np.zeros(mask.shape + (4,), np.float32); out[..., :3] = col; out[..., 3] = alpha * 255
    return out

def arrow(length, base, thick, S=4, flat=False):
    """Vertical arrow pointing down: a dark outline, then the bevel on top."""
    W = int((thick * 4.2 + 8) * S); H = int((length + 8) * S)
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); cx = W / 2
    t, hh, hw = thick * S, thick * 2.6 * S, thick * 2.0 * S
    d.rectangle([cx - t / 2, 4 * S, cx + t / 2, H - 4 * S - hh + 2], fill=255)
    d.polygon([(cx - hw, H - 4 * S - hh), (cx + hw, H - 4 * S - hh), (cx, H - 4 * S)], fill=255)
    m = np.array(m)
    if flat:
        out = np.zeros(m.shape + (4,), np.float32); out[..., :3] = base; out[..., 3] = m
    else:
        out = bevel((m > 127).astype(np.uint8), base)
    dark = cv2.dilate(m, np.ones((2 * S + 1, 2 * S + 1), np.uint8)).astype(np.float32)
    o = np.zeros(m.shape + (4,), np.float32); o[..., :3] = (8, 10, 14); o[..., 3] = cv2.GaussianBlur(dark, (0, 0), S * 0.6) * 0.85
    im = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8))
    im.alpha_composite(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))
    return im.resize((W // S, H // S), Image.LANCZOS)

def count_badge(im, txt, col, style):
    """3a: digits in the frame color with a dark outline; 3b: small navy
    badge with a colored edge (as in mockup 3)."""
    d = ImageDraw.Draw(im); S = im.width
    if style == 'a':
        f = F(int(S * 0.27), 'Bold')
        d.text((S - S * 0.15, S - S * 0.13), txt, font=f, fill=col + (255,), anchor='rb', stroke_width=max(2, S // 28), stroke_fill=(0, 0, 0))
    else:
        f = F(int(S * 0.19), 'Bold'); w = d.textlength(txt, font=f) + S * 0.12
        x1, y1 = S - S * 0.05, S - S * 0.05; x0, y0 = x1 - w, y1 - S * 0.27
        d.rounded_rectangle([x0, y0, x1, y1], int(S * 0.06), fill=(8, 12, 22, 255), outline=col + (255,), width=max(1, S // 40))
        d.text(((x0 + x1) / 2, (y0 + y1) / 2), txt, font=f, fill=col + (255,), anchor='mm')
    return im

def node(ic, state, S, count=None, cstyle='a', glow=None):
    kw = {'max': dict(border=GOLD, fx='gold'), 'part': dict(border=BLUE), 'can': dict(border=(210, 214, 222)),
          'lock': dict(border=(60, 64, 74), fx='gray', dim=0.62)}[state]
    im = TS.tile(ic, S=S, glow=glow, **kw)
    if count: count_badge(im, count, {'max': GOLD, 'part': BLUE}[state], cstyle)
    return im

def column(sheet, x, y, S, aether):
    """maxed -> part -> can take -> locked, linked by arrows."""
    seq = [(TS.CLAW, 'max', '2/2'), (TS.BEAST, 'part', '3/5'), (TS.BOW, 'can', None), (TS.LOCK, 'lock', None)]
    cols = [GOLD, BLUE, GRAY]
    gap = int(S * 0.75)
    for i, (ic, st, cnt) in enumerate(seq):
        if aether:
            im = node(ic, st, S, cnt, 'b', glow=(BLUE if st == 'can' else None))
        else:   # Blizzard today: yellow/green/gray frames, green glow, yellow digits
            b = {'max': (240, 200, 40), 'part': (40, 220, 70), 'can': (150, 152, 160), 'lock': (70, 72, 80)}[st]
            im = TS.tile(ic, border=b, S=S, glow=((34, 230, 80) if st == 'can' else None),
                         fx=('gray' if st == 'lock' else None), dim=(0.5 if st == 'lock' else 0))
            if cnt:
                dd = ImageDraw.Draw(im); f = F(int(S * 0.27), 'Bold')
                dd.text((S - S * 0.15, S - S * 0.13), cnt.split('/')[0], font=f, fill=b + (255,), anchor='rb', stroke_width=2, stroke_fill=(0, 0, 0))
        yy = y + i * (S + gap)
        sheet.alpha_composite(im, (x, yy))
    for i in range(3):
        yy = y + i * (S + gap)
        if True:
            if aether: a = arrow(gap + 6, cols[i], max(3, S // 14))
            else:      a = arrow(gap + 6, [(240, 200, 40), (40, 220, 70), (120, 122, 130)][i], max(1, S // 40), flat=True)
            sheet.alpha_composite(a, (x + S // 2 - a.width // 2, yy + S - 7))

W, H = 1240, 1060
sheet = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
d.text((24, 18), "Talents: arrows (2), point counts (3), glow (4)", font=F(28, 'SemiBold'), fill=GOLD)
d.text((24, 60), "Each column runs: maxed  >  some points  >  can take  >  locked.  2x zoom.", font=F(17), fill=(170, 176, 188))
for i, (t, ae) in enumerate((("Blizzard today", False), ("Aether", True))):
    x = 60 + i * 260
    d.text((x + 64, 100), t, font=F(20, 'SemiBold'), fill=(235, 238, 245), anchor='ma')
    column(sheet, x, 140, 128, ae)
# game-size column
d.text((660, 100), "Aether, game size", font=F(20, 'SemiBold'), fill=(235, 238, 245), anchor='ma')
column(sheet, 628, 140, 64, True)
# 3: count styles
X3 = 800
d.text((X3, 100), "3  Point counts", font=F(22, 'SemiBold'), fill=GOLD)
for j, (st, name) in enumerate((('a', "3a  Digits in the frame color"), ('b', "3b  Small badge  (recommended)"))):
    y = 150 + j * 190
    d.text((X3, y), name, font=F(17), fill=(235, 238, 245))
    for k, (ic, s, c) in enumerate(((TS.CLAW, 'max', '2/2'), (TS.BEAST, 'part', '3/5'))):
        im = node(ic, s, 128, c, st); sheet.alpha_composite(im, (X3 + k * 150, y + 30))
# 4: glow
y4 = 560
d.text((X3, y4), "4  'You can spend a point here' glow", font=F(22, 'SemiBold'), fill=GOLD)
for k, (g, name) in enumerate((((34, 230, 80), "Green (today)"), (BLUE, "Blue  (recommended)"))):
    im = TS.tile(TS.BOW, border=(210, 214, 222), S=150, glow=g)
    # stronger, wider glow so it reads at a glance
    gl = Image.new('RGBA', (190, 190), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    for r in range(18, 0, -1):
        gd.rounded_rectangle([20 - r, 20 - r, 170 + r, 170 + r], 14 + r, outline=g + (int(10 * (19 - r) / 6),), width=2)
    sheet.alpha_composite(gl, (X3 + k * 200 - 20, y4 + 40))
    sheet.alpha_composite(im, (X3 + k * 200, y4 + 60))
    d.text((X3 + k * 200 + 75, y4 + 230), name, font=F(16), fill=(170, 176, 188), anchor='ma')
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_talent_details.png'); print(sheet.size)
