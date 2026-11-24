# Where else the deposit slot could go, on the user's in-game AetherPack screenshot
# (1.4.0, Fira text). The slot is lined up with the item grid; the bars get their
# full width back; the slogan is hand-lettered on one line at a steeper angle,
# with a drawn arrow into the slot.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
MEDIA = '/home/claude/aether-suite/AetherPack/Media/'
HAND = '/home/claude/aether-suite/refs/fonts/gochi-hand-400.ttf'
FIRA = '/home/claude/aether-suite/AetherHub/Media/Fonts/FiraSans-%s.ttf'
AMBER = (255, 176, 0)
src = Image.open(SRC).convert('RGB')
W, H = src.size
SLOT = 52                                  # px, like the other slots here
COL1, COL10 = 25, 553                      # item grid columns (left edges)
BG = tuple(int(v) for v in np.array(src)[897, 300])

def tex(name, size):
    return Image.open(MEDIA + name + '.tga').convert('RGBA').resize(size, Image.LANCZOS)
def tint(im, col, a=1.0):
    x = np.array(im).astype(np.float32)
    for k in range(3): x[..., k] = x[..., k] * col[k] / 255
    x[..., 3] *= a
    return Image.fromarray(x.clip(0, 255).astype(np.uint8))

def slot_img(n=SLOT, count="20"):
    S = 4; N = n * S
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    im.alpha_composite(tex('dep_well', (N, N)))
    im.alpha_composite(tint(tex('dep_glow', (N, N)), AMBER))
    im.alpha_composite(tex('dep_dark', (N, N)))
    im.alpha_composite(tint(tex('dep_rim', (N, N)), AMBER))
    ng = tint(tex('dep_numglow', (int(N * 0.76), int(N * 0.49))), AMBER, 0.55)
    im.alpha_composite(ng, ((N - ng.width) // 2, (N - ng.height) // 2))
    f = ImageFont.truetype(FIRA % 'Black', int(n * 0.30 * S))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((N / 2 + S, N / 2 + S), count, font=f, fill=(0, 0, 0, 165), anchor='mm')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S * 0.6)))
    ImageDraw.Draw(im).text((N / 2, N / 2), count, font=f, fill=(255, 199, 77, 255), anchor='mm')
    return im.resize((n, n), Image.LANCZOS)

def ink_layer(size, draw_fn, S=4):
    L = Image.new('L', (size[0] * S, size[1] * S), 0)
    draw_fn(ImageDraw.Draw(L), S)
    return L

def stroke(d, S, pts, w0, w1, wmid=None):
    n_ = len(pts)
    for i_, (x_, y_) in enumerate(pts):
        t_ = i_ / max(1, n_ - 1)
        if wmid is None: w_ = w0 + (w1 - w0) * t_
        else: w_ = (w0 + (wmid - w0) * min(1, t_ / 0.35)) * (1 - max(0, t_ - 0.75) / 0.25 * (1 - w1 / wmid))
        r = w_ * S / 2
        d.ellipse([x_ * S - r, y_ * S - r, x_ * S + r, y_ * S + r], fill=255)

def arrow(d, S, p0, p1, p2, p3, seed=3, scale=1.4):
    t = np.linspace(0, 1, 60)[:, None]
    pts = ((1 - t) ** 3) * np.array(p0) + 3 * ((1 - t) ** 2) * t * np.array(p1) + 3 * (1 - t) * t ** 2 * np.array(p2) + t ** 3 * np.array(p3)
    rng = np.random.default_rng(seed)
    tang = np.gradient(pts, axis=0); tang /= np.linalg.norm(tang, axis=1)[:, None] + 1e-9
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    pts = pts + nrm * np.convolve(rng.normal(0, 0.55, len(pts)), np.ones(9) / 9, mode='same')[:, None]
    stroke(d, S, pts, 0.9 * scale, 1.9 * scale, 2.3 * scale)
    tip = pts[-1]; dv = pts[-1] - pts[-6]; dv /= np.linalg.norm(dv)
    for side, ang, ln in ((1, 0.62, 7.0), (-1, 0.55, 6.2)):
        ca, sa = np.cos(side * ang), np.sin(side * ang)
        back = -np.array([dv[0] * ca - dv[1] * sa, dv[0] * sa + dv[1] * ca])
        seg = np.array([tip + back * ln * scale * u for u in np.linspace(0, 1, 18)])
        stroke(d, S, seg, 2.1 * scale, 1.1 * scale)

CHALK = None                       # None, 'light' or 'heavy'
def chalkify(mask, S, level, seed=11):
    """Chalk: streaks that run along each stroke (noise smeared along the stroke's
    direction), ragged broken edges, gaps where the chalk skipped, a little dust."""
    import cv2
    m = np.array(mask).astype(np.float32) / 255
    h, w = m.shape
    rng = np.random.default_rng(seed)
    # the stroke direction everywhere: across the gradient of the softened stroke
    soft = cv2.GaussianBlur(m, (0, 0), 1.6 * S)
    gx = cv2.Sobel(soft, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(soft, cv2.CV_32F, 0, 1, ksize=3)
    # structure tensor, smoothed, gives a steady direction inside the stroke
    jxx = cv2.GaussianBlur(gx * gx, (0, 0), 2.0 * S); jyy = cv2.GaussianBlur(gy * gy, (0, 0), 2.0 * S); jxy = cv2.GaussianBlur(gx * gy, (0, 0), 2.0 * S)
    theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy)            # across the stroke
    dx, dy = -np.sin(theta), np.cos(theta)                    # along the stroke
    # white noise, coarse enough to survive at actual size
    cell = max(1, int(0.55 * S))
    nz = rng.random((h // cell + 1, w // cell + 1)).astype(np.float32)
    nz = cv2.resize(nz, (w, h), interpolation=cv2.INTER_NEAREST)
    # line integral convolution: average the noise along the stroke direction
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    acc = nz.copy(); cnt = 1.0
    L = int((7 if level == 'heavy' else 6) * S)
    step = max(1.0, S * 0.7)
    for sign in (1, -1):
        px, py = xs.copy(), ys.copy()
        for _ in range(int(L / step)):
            px += sign * step * cv2.remap(dx, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            py += sign * step * cv2.remap(dy, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            acc += cv2.remap(nz, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE); cnt += 1
    streak = acc / cnt
    streak = (streak - streak.mean()) / (streak.std() + 1e-6)              # zero mean, unit spread
    # ragged edges: the stroke, softened, plus streak noise, cut at a threshold
    edge = cv2.GaussianBlur(m, (0, 0), 0.8 * S)
    k = 0.16 if level == 'light' else 0.22
    body = np.clip((edge + streak * k - 0.5) * 5, 0, 1)
    near = cv2.dilate((m > 0.05).astype(np.uint8), np.ones((int(1.4 * S) | 1, int(1.4 * S) | 1), np.uint8)).astype(np.float32)
    body *= near                                            # chalk only where a stroke is
    # inside: light and dark striations along the stroke, some skips
    fill = np.clip(0.78 + streak * (0.30 if level == 'light' else 0.42), 0.15, 1)
    out = body * fill
    # dust
    dust = cv2.GaussianBlur(m, (0, 0), 2.4 * S) * (0.08 if level == 'light' else 0.13)
    dust *= cv2.GaussianBlur(near, (0, 0), 2.0 * S)
    out = np.maximum(out, dust * np.clip(0.6 + 0.6 * streak, 0, 1.5))
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))

def put_ink(img, mask, origin, S=4, blur_sh=True):
    if CHALK: mask = chalkify(mask, S, CHALK)
    m = mask.resize((mask.width // S, mask.height // S), Image.LANCZOS)
    col = AMBER if not CHALK else (255, 200, 80)      # chalk reads a touch paler
    ink = Image.new('RGBA', m.size, col + (0,)); ink.putalpha(m)
    if not CHALK:
        sh = Image.new('RGBA', m.size, (0, 0, 0, 0)); sh.putalpha(m.point(lambda v: int(v * 0.66)))
        sh = sh.filter(ImageFilter.GaussianBlur(0.7))
        img.alpha_composite(sh, (origin[0] + 1, origin[1] + 1))
    img.alpha_composite(ink, origin)

def label_mask(text, px, tilt, S=4, font=None):
    f = ImageFont.truetype(font or HAND, int(px * S))
    bb = ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0] + 8 * S, bb[3] - bb[1] + 8 * S
    sw = int(0.35 * S) if CHALK else 0                      # chalk strokes are a little fatter
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).text((w / 2, h / 2), text, font=f, fill=255, anchor='mm', stroke_width=sw, stroke_fill=255)
    return m.rotate(tilt, resample=Image.BICUBIC, expand=True)

def rebuild(extra_row_at):
    """the window with the old block removed, bars at full width, and a free row
    of height ROW inserted at y = extra_row_at (screenshot coords)."""
    a = src.copy(); d = ImageDraw.Draw(a)
    d.rectangle([518, 900, 612, 1004], fill=BG)                     # the old deposit block
    d.rectangle([498, 900, 518, 938], fill=BG)                      # and the start of its slogan
    line1 = a.crop((255, 960, 516, 976))                            # Ammo text, first line
    d.rectangle([255, 958, 516, 996], fill=BG)                      # clear both lines
    a.paste(line1, (255, 969))                                      # back on one line, level with its bar
    d = ImageDraw.Draw(a)
    f = ImageFont.truetype(FIRA % 'Regular', 15)
    d.text((481, 977), " free", font=f, fill=(255, 255, 255), anchor='lm')
    ROW = SLOT + 14
    top = a.crop((0, 0, W, extra_row_at)); bot = a.crop((0, extra_row_at, W, H))
    fill = a.crop((0, 897, W, 898)).resize((W, ROW))
    out = Image.new('RGB', (W, H + ROW)); out.paste(top, (0, 0)); out.paste(fill, (0, extra_row_at)); out.paste(bot, (0, extra_row_at + ROW))
    return out.convert('RGBA'), ROW

TILT = 8
# --- A: its own row under the bars, in the last column; slogan to its left
A, ROW = rebuild(1000)
sy = 1000 + 6
A.alpha_composite(slot_img(), (COL10, sy))
lm = label_mask("No swaps. Just drops.", 22, TILT)
put_ink(A, lm, (COL10 - 70 - lm.width // 4, sy + 2))
ax = Image.new('L', (W * 4, (H + ROW) * 4), 0); da = ImageDraw.Draw(ax)
arrow(da, 4, (COL10 - 66, sy + 34), (COL10 - 46, sy + 50), (COL10 - 22, sy + 44), (COL10 - 5, sy + 30), seed=5)
put_ink(A, ax, (0, 0))
# --- B: under "Free slots", in the first column, where empty slots live; slogan to its right
B, ROW = rebuild(898)
sy = 898 + 4
B.alpha_composite(slot_img(), (COL1, sy))
lm = label_mask("No swaps. Just drops.", 22, TILT)
put_ink(B, lm, (COL1 + SLOT + 69, sy - 11))        # higher and a little right: the arrow starts just before the first word
bx = Image.new('L', (W * 4, (H + ROW) * 4), 0); db = ImageDraw.Draw(bx)
arrow(db, 4, (COL1 + SLOT + 70, sy + 36), (COL1 + SLOT + 50, sy + 52), (COL1 + SLOT + 26, sy + 46), (COL1 + SLOT + 6, sy + 30), seed=5)
put_ink(B, bx, (0, 0))

def make_B(font=None, px=22, text="No swaps. Just drops.", dy=0):
    B, ROW = rebuild(898)
    sy = 898 + 4
    B.alpha_composite(slot_img(), (COL1, sy))
    lm = label_mask(text, px, TILT, font=font)
    put_ink(B, lm, (COL1 + SLOT + 69, sy - 11 + dy))
    bx = Image.new('L', (W * 4, (H + ROW) * 4), 0); db = ImageDraw.Draw(bx)
    arrow(db, 4, (COL1 + SLOT + 70, sy + 36), (COL1 + SLOT + 50, sy + 52), (COL1 + SLOT + 26, sy + 46), (COL1 + SLOT + 6, sy + 30), seed=5)
    put_ink(B, bx, (0, 0))
    return B.convert('RGB').crop((16, 870, 420, 990))
import os
if os.environ.get('CHALKFONTS'):
    CHALK = 'light'
    opts = [("Amatic SC Bold (tall, narrow caps, closest to your picture)", 'amatic-sc-700.ttf', 30, "NO SWAPS. JUST DROPS.", -3),
            ("Cabin Sketch Bold (sketchy, double-drawn)", 'cabin-sketch-700.ttf', 21, "No swaps. Just drops.", 0),
            ("Covered By Your Grace (quick chalk scrawl)", 'covered-by-your-grace-400.ttf', 24, "No swaps. Just drops.", -2),
            ("Rock Salt (rough, all hand)", 'rock-salt-400.ttf', 15, "No swaps. Just drops.", 0)]
    outs = [(lab, make_B(font='/home/claude/mock-work/hfonts/' + f, px=px, text=t, dy=dy)) for lab, f, px, t, dy in opts]
    fl = ImageFont.truetype(FIRA % 'Regular', 20)
    z = 3
    im0 = outs[0][1]
    rowh = 34 + im0.height * z + 16
    cv = Image.new('RGB', (16 * 3 + im0.width * z + im0.width, 8 + len(outs) * rowh), (18, 20, 26)); cd = ImageDraw.Draw(cv)
    for i, (lab, im) in enumerate(outs):
        y = 8 + i * rowh
        cd.text((16, y), lab, fill=(255, 209, 0), font=fl)
        cv.paste(im.resize((im.width * z, im.height * z), Image.LANCZOS), (16, y + 30))
        cv.paste(im, (32 + im.width * z, y + 30))
    cv.save(OUT); print(cv.size); sys.exit(0)
if os.environ.get('CHALKS'):
    outs = []
    for lv, lab in ((None, "Now: marker"), ('light', "Chalk, light"), ('heavy', "Chalk, heavy")):
        CHALK = lv
        outs.append((lab, make_B()))
    fl = ImageFont.truetype(FIRA % 'Regular', 20)
    z = 3
    im0 = outs[0][1]
    rowh = 34 + im0.height * z + 16
    cv = Image.new('RGB', (16 * 3 + im0.width * z + im0.width, 8 + len(outs) * rowh), (18, 20, 26)); cd = ImageDraw.Draw(cv)
    for i, (lab, im) in enumerate(outs):
        y = 8 + i * rowh
        cd.text((16, y), lab + "   (3x, actual size at right)", fill=(255, 209, 0), font=fl)
        cv.paste(im.resize((im.width * z, im.height * z), Image.LANCZOS), (16, y + 30))
        cv.paste(im, (32 + im.width * z, y + 30))
    cv.save(OUT); print(cv.size); sys.exit(0)
fl = ImageFont.truetype(FIRA % 'Regular', 20)
pad = 16
crops = [("A. Its own row under the bars, in the last column", A.crop((0, 600, W, H + ROW)).convert('RGB')),
         ("B. Under Free slots, in the first column", B.crop((0, 600, W, H + ROW)).convert('RGB'))]
cv = Image.new('RGB', (pad * 3 + 2 * W, 40 + crops[0][1].height + pad), (18, 20, 26)); cd = ImageDraw.Draw(cv)
for i, (lab, im) in enumerate(crops):
    x = pad + i * (W + pad)
    cd.text((x, 8), lab, fill=(255, 209, 0), font=fl)
    cv.paste(im, (x, 40))
cv.save(OUT); print(cv.size)
