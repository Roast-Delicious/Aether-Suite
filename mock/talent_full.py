# Full-window Talents mockup on the user's own screenshot (Nov 25, 03:12),
# with every decision so far (Nov 25 07:00-07:08):
#  spec icons gold on navy (C); maxed = gold tint + gold frame; some points
#  = blue frame; can take = light frame + medium Aether-blue glow; locked =
#  navy (1C, middle); 3D arrows gold/blue/gray by source; counts as a
#  "2 of 5" pill centered on the frame's bottom edge (3c); Aether chrome.
# The screenshot had 0 unspent points; shown here with 2, so the reachable
# empty talents show the "can take" glow.
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from skins_lib import Canvas, U, SS, GOLD, BLUE, NAVY, PANEL, WHITE, DIM, F as LF, label
from talent_details import arrow, F
import talent_states as TS, os
VIS = os.environ.get('VIS') == '1'
UNSPENT = int(os.environ.get('UNSPENT', '2')); LOCKED = os.environ.get('LOCKED', 'gray'); OUTN = os.environ.get('OUTN', 'out_talent_full.png')

SHOT = Image.open('/mnt/user-data/uploads/330e1911-image.png').convert('RGB')
FULL = np.array(SHOT).astype(float)

def icon_at(cx, cy, r=23):
    a = FULL[cy - r:cy + r, cx - r:cx + r].copy()
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = (((R > 150) & (G > 120) & (B < 110)) | ((G > 150) & (R < 140) & (B < 140))).astype(np.uint8)
    yy, xx = np.mgrid[0:2 * r, 0:2 * r]; m[(xx < r * 1.2) | (yy < r * 0.9)] = 0
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    return cv2.inpaint(a.astype(np.uint8)[..., ::-1], m * 255, 5, cv2.INPAINT_TELEA)[..., ::-1].astype(float)

def lum(a): return (a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11) / 255

# ---- the nodes (full-res centers) and their states -------------------------
H = lambda x, y: (2 * x, 2 * y)        # from the half-size grid
BM = {(117, 212): ('can', 0, 0), (162, 212): None, (207, 212): None}  # filled below
nodes = []
# Beast Mastery (from the screenshot: yellow = maxed, green = some points)
for (x, y, st, n, m) in [(162, 212, 'max', 5, 5), (207, 212, 'part', 1, 5), (117, 257, 'max', 2, 2), (162, 257, 'can', 0, 0),
                         (207, 257, 'max', 2, 2), (117, 302, 'can', 0, 0), (162, 302, 'max', 1, 1), (207, 302, 'max', 5, 5),
                         (117, 347, 'can', 0, 0), (207, 347, 'max', 5, 5), (252, 347, 'max', 1, 1), (117, 392, 'can', 0, 0),
                         (162, 392, 'max', 1, 1), (252, 392, 'max', 2, 2), (207, 437, 'part', 2, 3), (162, 482, 'lock', 0, 0)]:
    if st == 'can' and UNSPENT == 0: st = 'none'
    nodes.append((H(x, y), st, n, m))
MM = [(418, 212), (463, 212), (508, 212), (418, 257), (463, 257), (508, 257), (418, 302), (463, 302), (553, 302),
      (463, 347), (508, 347), (418, 392), (508, 392), (553, 392), (508, 437), (463, 482)]
SV = [(767, 212), (812, 212), (722, 257), (767, 257), (812, 257), (857, 257), (722, 302), (767, 302), (812, 302),
      (722, 347), (767, 347), (812, 347), (722, 392), (767, 392), (812, 392), (857, 392), (812, 437), (767, 482)]
for (x, y) in MM + SV:
    nodes.append((H(x, y), ('can' if UNSPENT else 'none') if y == 212 else 'lock', 0, 0))
ARROWS = [((162, 302), (162, 392), 'max'), ((207, 347), (207, 437), 'max'), ((162, 392), (162, 482), 'lock'),
          ((508, 257), (508, 347), 'lock'), ((418, 302), (418, 392), 'lock'), ((463, 347), (463, 482), 'lock'),
          ((812, 302), (812, 347), 'lock'), ((767, 392), (767, 482), 'lock')]
SPEC = [(H(133, 155), "27"), (H(433, 155), "0"), (H(735, 155), "0")]

# ---- 1. bronze -> blue in the tree area (the top band and spec underlines) --
def bronze_to_blue(a, box):
    x0, y0, x1, y1 = box; reg = a[y0:y1, x0:x1].astype(np.uint8)
    hsv = cv2.cvtColor(reg, cv2.COLOR_RGB2HSV).astype(float)
    warm = (hsv[..., 0] < 35) & (hsv[..., 1] > 60) & (hsv[..., 2] > 40)
    hsv[..., 0] = np.where(warm, 106, hsv[..., 0])            # OpenCV hue 0-180: 106 ~ Aether blue
    hsv[..., 1] = np.where(warm, np.minimum(hsv[..., 1] * 0.9, 200), hsv[..., 1])
    hsv[..., 2] = np.where(warm, hsv[..., 2] * 0.85, hsv[..., 2])
    a[y0:y1, x0:x1] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
work = FULL.copy()
bronze_to_blue(work, (80, 170, 1880, 250))      # header band + divider
bronze_to_blue(work, (80, 350, 1880, 395))      # spec underlines
ART = Image.fromarray(np.clip(work, 0, 255).astype(np.uint8)).crop((80, 242, 1880, 1062))

# ---- 2. chrome -------------------------------------------------------------
c = Canvas(SHOT.copy())
win = (64, 56, 1888, 1120)
c.window(win, "Talents", chevrons='tbl')
c.crest((118, 106), 46); c.text((118, 106), "T", 30, GOLD, 'Bold', 'mm')
c.close(win[2] - 30, win[1] + 20)
# Primary / Secondary tabs
for i, (t, act) in enumerate((("Primary", True), ("Secondary", False))):
    x0 = 172 + i * 228
    c.d.rounded_rectangle(c.P(x0, 130, x0 + 216, 170), int(5 * U * SS), fill=((28, 58, 104) if act else NAVY) + (255,),
                          outline=(GOLD if act else BLUE) + (255,), width=SS * (2 if act else 1))
    c.text((x0 + 108, 150), t, 19, GOLD if act else DIM, 'SemiBold', 'mm')
# search + dropdown
c.d.rounded_rectangle(c.P(1556, 122, 1838, 152), int(4 * U * SS), fill=(8, 12, 22, 255), outline=BLUE + (255,), width=SS)
c.text((1590, 137), "Search", 17, DIM, 'Regular', 'lm')
c.d.ellipse(c.P(1564, 129, 1576, 141), outline=(170, 190, 215, 255), width=2 * SS); c.d.line(c.P(1575, 140, 1581, 146), fill=(170, 190, 215, 255), width=2 * SS)
c.d.rounded_rectangle(c.P(1846, 122, 1876, 152), int(4 * U * SS), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
c.tri(1861, 138, 6, WHITE)
# tree art (kept), framed in blue
c.paste(ART, (80, 242))
L, d = c.layer(); d.rectangle(c.P(80, 242, 1880, 1062), outline=BLUE + (255,), width=SS); c.over(L)
c.d.line(c.P(80, 242, 1880, 242), fill=BLUE + (255,), width=SS)
# unspent box
c.d.rounded_rectangle(c.P(1556, 180, 1852, 232), int(5 * U * SS), fill=NAVY + (240,), outline=BLUE + (255,), width=SS)
c.text((1576, 206), "Unspent Talents", 19, WHITE, 'Regular', 'lm'); c.text((1832, 206), str(UNSPENT), 32, GOLD, 'Bold', 'rm')
# Apply Changes
c.button((852, 1072, 1100, 1106), "Apply Changes", size=18)
base = c.done().convert('RGBA')

# ---- 3. spec icons: gold on navy ------------------------------------------
NV = np.array(NAVY, float); GD = np.array(GOLD, float)
for (cx, cy), pts in SPEC:
    r = 27; ic = FULL[cy - r:cy + r, cx - r:cx + r]; g = lum(ic); g = g / max(g.max(), 1e-3)
    col = NV + g[..., None] * GD * 1.05
    S = 2 * r; disc = Image.new('L', (S, S), 0); ImageDraw.Draw(disc).ellipse([0, 0, S - 1, S - 1], fill=255)
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(disc)
    ring = Image.new('RGBA', (S + 12, S + 12), (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
    rd.ellipse([0, 0, S + 11, S + 11], fill=NAVY + (255,), outline=BLUE + (255,), width=3)
    ring.alpha_composite(im, (6, 6)); rd.ellipse([0, 0, S + 11, S + 11], outline=BLUE + (255,), width=3)
    base.alpha_composite(ring, (cx - r - 6, cy - r - 6))
    bd = ImageDraw.Draw(base); f = F(17, 'Bold')
    bd.rounded_rectangle([cx + 6, cy + 14, cx + 42, cy + 38], 5, fill=(8, 12, 22, 255), outline=BLUE + (255,), width=2)
    bd.text((cx + 24, cy + 26), pts, font=f, fill=WHITE + (255,), anchor='mm')

# ---- 4. arrows, then nodes, then pills -------------------------------------
ACOL = {'max': GOLD, 'part': BLUE, 'lock': (BLUE if LOCKED == 'blue' else ((150, 154, 164) if VIS else (110, 114, 124)))}
S = 78; half = S // 2
for (a, b, kind) in ARROWS:
    (x0, y0), (x1, y1) = H(*a), H(*b)
    ln = (y1 - half + 8) - (y0 + half - 8)
    ar = arrow(ln, ACOL[kind], 6)
    base.alpha_composite(ar, (x0 - ar.width // 2, y0 + half - 12))

def glow_layer(S, strength=1.6, spread=0.13):
    pad = int(S * 0.35); N = S + 2 * pad
    m = np.zeros((N, N), np.float32); cv2.rectangle(m, (pad + 8, pad + 8), (pad + S - 9, pad + S - 9), 1.0, -1)
    g = cv2.GaussianBlur(m, (0, 0), S * spread) * strength
    out = np.zeros((N, N, 4), np.float32); out[..., :3] = BLUE; out[..., 3] = np.clip(g, 0, 1) * 255
    return Image.fromarray(out.astype(np.uint8)), pad

DEEP = np.array([8, 18, 38.]); MID = np.array([60, 100, 160.])
pills = []
for (cx, cy), st, n, m in nodes:
    ic = icon_at(cx, cy)
    if st == 'max':
        im = TS.tile(ic, border=GOLD, fx='gold', S=S)
    elif st == 'part':
        im = TS.tile(ic, border=BLUE, S=S)
    elif st == 'can':
        g = lum(ic); g = g / max(g.max(), 1e-3)
        # empty talents in the screenshot are already gray; show them in color where we can
        im = TS.tile(ic, border=(210, 214, 222), S=S)
        gl, pad = glow_layer(S); base.alpha_composite(gl, (cx - half - pad, cy - half - pad))
    elif st == 'none':     # open, but no points left: navy
        g = lum(ic); g = g / max(g.max(), 1e-3)
        if VIS:            # lighter navy icon, lighter frame, faint navy backing
            bk = ImageDraw.Draw(base); bk.rounded_rectangle([cx - half - 4, cy - half - 4, cx + half + 4, cy + half + 4], 8, fill=(30, 58, 104, 150))
            a = np.array([24, 48, 92.]) + g[..., None] * (np.array([120, 160, 220.]) - np.array([24, 48, 92.]))
            im = TS.tile(a, border=(110, 150, 210), S=S)
        else:
            a = DEEP + g[..., None] * (MID - DEEP) * 1.15
            im = TS.tile(a, border=(60, 90, 140), S=S)
    elif LOCKED == 'blue':
        g = lum(ic); g = g / max(g.max(), 1e-3)
        a = np.array([14, 40, 80.]) + g[..., None] * (np.array([77, 166, 255.]) - np.array([14, 40, 80.])) * 0.9
        im = TS.tile(a, border=BLUE, S=S)
    else:                  # locked: gray
        g = lum(ic); g = g / max(g.max(), 1e-3)
        a = g[..., None] * np.array([150, 152, 160.]) * (0.85 if VIS else 0.55) + (25 if VIS else 0)
        im = TS.tile(a, border=((125, 129, 140) if VIS else (70, 74, 84)), S=S)
    base.alpha_composite(im, (cx - half, cy - half))
    if st in ('max', 'part'): pills.append((cx, cy + half - 8, f"{n} of {m}", GOLD if st == 'max' else BLUE))
d = ImageDraw.Draw(base)
for cx, y, txt, col in pills:
    f = F(16, 'Bold'); w = d.textlength(txt, font=f) + 14; h = 22
    d.rounded_rectangle([cx - w / 2, y - h / 2, cx + w / 2, y + h / 2], 11, fill=(8, 12, 22, 255), outline=col + (255,), width=2)
    d.text((cx, y), txt, font=f, fill=col + (255,), anchor='mm')

VIS0 = 0
TITLE = os.environ.get('TITLE', 'Talents, full window')
out = label(base.convert('RGB'), TITLE)
out.save('/home/claude/aether-repo/mock/' + OUTN); print(out.size)
