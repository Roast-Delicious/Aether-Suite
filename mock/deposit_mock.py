# Deposit slot, round 3, on the user's real AetherPack screenshot:
# two-line label centered above the slot, a stack of five chevrons dropping into
# it, the gold slot (one of the user's real slots, rim recolored), soft inner
# glow, and the free count shaded darker toward the middle of each stroke.
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUTDIR = sys.argv[1], sys.argv[2]
U = 51 / 37; SS = 4
GOLD = (255, 209, 0); ORANGE = (255, 120, 0)
FIRA = '/usr/share/fonts/truetype/google-fonts/ofl/firasans/FiraSans-%s.ttf'
BG = (14, 16, 22)

# ---------- the window, stretched down to make room ----------
src = Image.open(SRC).convert('RGB')
WX0, WX1 = 1150, 1800
EXTRA = 16                      # px added below the bars
cut = 1206                      # below the last bar row, above the bottom edge
top = src.crop((WX0, 225, WX1, cut)); bot = src.crop((WX0, cut, WX1, 1245))
filler = src.crop((WX0, cut - 1, WX1, cut)).resize((WX1 - WX0, EXTRA))
base = Image.new('RGB', (WX1 - WX0, top.height + EXTRA + bot.height))
base.paste(top, (0, 0)); base.paste(filler, (0, top.height)); base.paste(bot, (0, top.height + EXTRA))
OX, OY = WX0, 225                # screenshot coords -> base coords: (x - OX, y - OY)

# ---------- the real slot, emptied ----------
A = np.array(src).astype(np.float32)
X0, Y0, X1, Y1 = 1176, 1018, 1240, 1082
c = A[Y0:Y1, X0:X1].copy()
sat = c.max(2) - c.min(2); lum = c.mean(2)
gray = (sat < 22) & (lum > 60)
colc, rowc = gray.sum(0), gray.sum(1)
cols_ = np.where(colc > 0.6 * colc.max())[0]; rows_ = np.where(rowc > 0.6 * rowc.max())[0]
bx0, bx1, by0, by1 = cols_.min(), cols_.max(), rows_.min(), rows_.max()
yy, xx = np.mgrid[0:c.shape[0], 0:c.shape[1]]
edge_d = np.minimum.reduce([xx - bx0, bx1 - xx, yy - by0, by1 - yy])
RIM = (edge_d >= -1) & (edge_d <= 1)            # the rim: 3 px, like the other slots
# the slot's cut corners: leave them out
cx0_, cy0_ = xx - (bx0 - 1), yy - (by0 - 1); cx1_, cy1_ = (bx1 + 1) - xx, (by1 + 1) - yy
CORNER = (cx0_ + cy0_ < 3) | (cx1_ + cy0_ < 3) | (cx0_ + cy1_ < 3) | (cx1_ + cy1_ < 3)
RIM = RIM & ~CORNER
INNER = edge_d > 1
RIML = np.clip(lum / max(1, lum[RIM & (lum > 35)].max()), 0.55, 1) ** 0.9
dd = np.hypot(xx - (bx0 + bx1) / 2, yy - (by0 + by1) / 2) / ((bx1 - bx0) / 2)
WELL = (8 + 14 * dd).clip(0, 24)
def slot_img(col):
    s = c.copy()
    for k in range(3):
        s[..., k] = np.where(INNER, WELL * (1.1 if k == 2 else 1.0), s[..., k])
        s[..., k] = np.where(RIM, (col[k] * (0.35 + 0.85 * RIML)).clip(0, 255), s[..., k])
    alpha = np.where((edge_d >= -1) & ~CORNER, 255, 0).astype(np.uint8)   # nothing outside the rim or in the cut corners
    rgba = np.dstack([s.clip(0, 255).astype(np.uint8), alpha])
    return Image.fromarray(rgba).crop((bx0 - 1, by0 - 1, bx1 + 2, by1 + 2))
SW = bx1 - bx0 + 3
IN_PX = 3          # px from the slot image's edge to the inside of the rim

CHEV = Image.open('/home/claude/brand/AetherPack/Media/win_chev_gold.tga').convert('RGBA')
CHEVD = Image.open('/home/claude/brand/AetherPack/Media/win_chev_dark.tga').convert('RGBA')
def chev(size, ang, col, alpha=1.0):
    n = int(size * U * SS)
    out = Image.new('RGBA', (int(n * 1.5), int(n * 1.5)), (0, 0, 0, 0))
    for img, cc in ((CHEVD, (10, 12, 18)), (CHEV, col)):
        a = np.array(img.resize((n, n), Image.LANCZOS))[..., 3].astype(np.float32) * alpha
        o = np.zeros(a.shape + (4,), np.uint8); o[..., 0], o[..., 1], o[..., 2] = cc; o[..., 3] = a.clip(0, 255)
        o = Image.fromarray(o).rotate(ang, resample=Image.BICUBIC, expand=True)
        out.alpha_composite(o, ((out.width - o.width) // 2, (out.height - o.height) // 2))
    return out

def mix(a, b, t): return tuple(int(round(a[k] * (1 - t) + b[k] * t)) for k in range(3))

def shaded_number(text, size_u, edge, center, outline=True):
    """digits bright at their edges and darker toward the middle of each stroke"""
    f = ImageFont.truetype(FIRA % 'Bold', int(size_u * U * SS))
    W_, H_ = int(size_u * U * SS * 2.2), int(size_u * U * SS * 1.6)
    m = Image.new('L', (W_, H_), 0); ImageDraw.Draw(m).text((W_ / 2, H_ / 2), text, font=f, fill=255, anchor='mm')
    M = np.array(m)
    dist = cv2.distanceTransform((M > 127).astype(np.uint8), cv2.DIST_L2, 5)
    t = np.clip(dist / max(1, dist.max()), 0, 1) ** 0.8
    img = np.zeros((H_, W_, 4), np.float32)
    for k in range(3): img[..., k] = edge[k] * (1 - t) + center[k] * t
    img[..., 3] = M
    out = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    if outline:
        o = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        ImageDraw.Draw(o).text((W_ / 2, H_ / 2), text, font=f, fill=(0, 0, 0, 255), anchor='mm', stroke_width=int(1.1 * U * SS), stroke_fill=(0, 0, 0, 255))
        out.alpha_composite(o.filter(ImageFilter.GaussianBlur(0.6 * SS)))
    out.alpha_composite(Image.fromarray(img.clip(0, 255).astype(np.uint8)))
    return out

def render(col=GOLD, stack_fade=False, num=('gold',), label_col=None, count="20", n_stack=5, ch_size=12.5, step=7, glow_r=5.5, glow_k=1.25, dark_mid=0.0, num_center=None, dark_r=0.0, chev_sizes=None, interior=None, num_size=15, num_blur=0.0, label_glow=False, num_alpha=1.0, ytop=1100, erase_line=True, slot_right=1745, arrow=None, arrow_col=(255, 214, 40), hand_font=None, hand_size=12, hand_tilt=-3.0, hand_lines=16, hand_col=None):
    label_col = label_col or col
    # patch in screenshot coords, drawn at SS
    PX0, PY0, PX1, PY1 = 1560, ytop - 12, 1772, ytop + 160
    patch = base.crop((PX0 - OX, PY0 - OY, PX1 - OX, PY1 - OY)).resize(((PX1 - PX0) * SS, (PY1 - PY0) * SS), Image.NEAREST).convert('RGBA')
    def P(x, y): return ((x - PX0) * SS, (y - PY0) * SS)
    d = ImageDraw.Draw(patch)
    sx1 = slot_right; sx0 = sx1 - SW; cx = (sx0 + sx1) / 2
    # the Free slots line stops before the label column
    if erase_line: d.rectangle([P(sx0 - 30, 1102), P(1765, 1105)], fill=BG + (255,))
    # two-line label, centered over the slot
    lf = ImageFont.truetype(FIRA % 'SemiBold', int(10.5 * U * SS))
    if label_glow:
        hl = Image.new('RGBA', patch.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
        for i, line in enumerate(("No swaps.", "Just drops.")):
            hd.text(P(cx, ytop + i * 16), line, font=lf, fill=label_col + (255,), anchor='mm', stroke_width=int(0.6 * U * SS), stroke_fill=label_col + (255,))
        hb = hl.filter(ImageFilter.GaussianBlur(2.2 * SS))
        hb = Image.fromarray((np.array(hb).astype(np.float32) * [1, 1, 1, 0.8]).clip(0, 255).astype(np.uint8))
        patch.alpha_composite(hb)
        d = ImageDraw.Draw(patch)
    if hand_font:
        # hand-lettered: the arrow's yellow, a soft shadow, tilted a little like a quick note
        hf = ImageFont.truetype(hand_font, int(hand_size * U * SS))
        Lh = Image.new('RGBA', patch.size, (0, 0, 0, 0)); dh = ImageDraw.Draw(Lh)
        Sh_ = Image.new('RGBA', patch.size, (0, 0, 0, 0)); dsh = ImageDraw.Draw(Sh_)
        for i, line in enumerate(("No swaps.", "Just drops.")):
            q = P(cx + (i * 2 - 1), ytop + i * hand_lines)
            dsh.text((q[0] + SS, q[1] + SS), line, font=hf, fill=(0, 0, 0, 170), anchor='mm')
            dh.text(q, line, font=hf, fill=(hand_col or arrow_col) + (255,), anchor='mm')
        ctr = P(cx, ytop + hand_lines / 2)
        Sh_ = Sh_.filter(ImageFilter.GaussianBlur(0.7 * SS)).rotate(-hand_tilt, resample=Image.BICUBIC, center=ctr)
        Lh = Lh.rotate(-hand_tilt, resample=Image.BICUBIC, center=ctr)
        patch.alpha_composite(Sh_); patch.alpha_composite(Lh)
        d = ImageDraw.Draw(patch)
    else:
        for i, line in enumerate(("No swaps.", "Just drops.")):
            y = ytop + i * 16
            if not label_glow:
                d.text((P(cx, y)[0] + SS, P(cx, y)[1] + SS), line, font=lf, fill=(0, 0, 0, 200), anchor='mm')
            d.text(P(cx, y), line, font=lf, fill=(mix(label_col, (255, 255, 255), 0.2) if label_glow else label_col) + (255,), anchor='mm')
    arrow_layers = None
    if arrow:
        # a hand-drawn arrow instead of chevrons
        if arrow == 'swoosh':                     # under the label, an S-curve dropping into the slot
            sy0 = ytop + 46
        else:                                     # 'hook': from the end of the label, around the right and into the slot
            sy0 = ytop + 25
        sy1 = sy0 + SW; cy = (sy0 + sy1) / 2
        rng_ = np.random.default_rng(3)
        def bez(p0, p1, p2, p3, n=60):
            t = np.linspace(0, 1, n)[:, None]
            return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
        if arrow == 'swoosh':
            pts = bez(np.array([cx - 16, ytop + 25.]), np.array([cx + 14, ytop + 27.]), np.array([cx - 12, ytop + 38.]), np.array([cx + 1, sy0 - 1.]))
        else:
            pts = bez(np.array([cx + 37, ytop + 18.]), np.array([sx1 + 20, ytop + 20.]), np.array([sx1 + 18, sy0 + 20.]), np.array([sx1 - 7, sy0 + 13.]))
        # wobble across the stroke, like a quick marker line
        tang = np.gradient(pts, axis=0); tang /= np.linalg.norm(tang, axis=1)[:, None] + 1e-9
        nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
        wob = np.convolve(rng_.normal(0, 0.55, len(pts)), np.ones(9) / 9, mode='same')
        pts = pts + nrm * wob[:, None]
        L_ = Image.new('RGBA', patch.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(L_)
        Sh = Image.new('RGBA', patch.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(Sh)
        def stroke(points, w0, w1, wmid=None):
            n_ = len(points)
            for i_, (x_, y_) in enumerate(points):
                t_ = i_ / max(1, n_ - 1)
                w_ = (w0 + (w1 - w0) * t_) if wmid is None else (w0 + (wmid - w0) * min(1, t_ / 0.35)) * (1 - max(0, t_ - 0.75) / 0.25 * (1 - w1 / max(wmid, 1e-6)))
                r_ = w_ * U * SS / 2
                q_ = P(x_, y_)
                ds.ellipse([q_[0] - r_ + SS, q_[1] - r_ + SS, q_[0] + r_ + SS, q_[1] + r_ + SS], fill=(0, 0, 0, 150))
                dl.ellipse([q_[0] - r_, q_[1] - r_, q_[0] + r_, q_[1] + r_], fill=arrow_col + (255,))
        stroke(pts, 0.9, 1.9, 2.3)                # thin tail, fuller body
        # arrowhead: two short strokes back from the tip, a little uneven
        tip = pts[-1]; dirv = pts[-1] - pts[-6]; dirv /= np.linalg.norm(dirv)
        for side, ang, ln in ((1, 0.62, 7.0), (-1, 0.55, 6.2)):
            ca, sa = np.cos(side * ang), np.sin(side * ang)
            back = -np.array([dirv[0] * ca - dirv[1] * sa, dirv[0] * sa + dirv[1] * ca])
            seg = np.array([tip + back * ln * t_ for t_ in np.linspace(0, 1, 18)])
            seg = seg + np.stack([-back[1], back[0]])[None, :] * np.convolve(rng_.normal(0, 0.35, 18), np.ones(5) / 5, mode='same')[:, None]
            stroke(seg, 2.1, 1.1)
        arrow_layers = (Sh.filter(ImageFilter.GaussianBlur(0.8 * SS)), L_)     # drawn last, on top of the slot
    else:
        # stack of five chevrons dropping into the slot
        y0 = ytop + 31
        sizes = chev_sizes or [ch_size] * n_stack
        yc = y0 + 2
        for i, sz in enumerate(sizes):
            a = (0.35 + 0.65 * i / max(1, len(sizes) - 1)) if stack_fade else 1.0
            ch = chev(sz, 180, col, a)
            p = P(cx, yc)
            patch.alpha_composite(ch, (int(p[0] - ch.width / 2), int(p[1] - ch.height / 2)))
            if i < len(sizes) - 1: yc += step * (sz + sizes[i + 1]) / (2 * ch_size)
        sy0 = yc + sizes[-1] * U * 0.5 + 6; sy1 = sy0 + SW; cy = (sy0 + sy1) / 2
    # the slot
    patch.alpha_composite(slot_img(col).resize((SW * SS, SW * SS), Image.NEAREST).convert('RGBA'), tuple(int(v) for v in P(sx0, sy0)))
    def draw_interior():
        if interior:
            n = SW * SS; i0 = IN_PX * SS; L_ = Image.new('RGBA', (n, n), (0, 0, 0, 0)); dl = ImageDraw.Draw(L_)
            cen = n / 2
            if interior == 'shaft':       # looking down a square shaft: four walls to a small floor
                fr = 0.40; f0, f1 = cen - n * fr / 2, cen + n * fr / 2
                o0, o1 = i0, n - i0
                walls = [([(o0, o0), (o1, o0), (f1, f0), (f0, f0)], 0.34),   # top wall, catches the most light
                         ([(o0, o0), (f0, f0), (f0, f1), (o0, o1)], 0.22),   # left
                         ([(o1, o0), (o1, o1), (f1, f1), (f1, f0)], 0.16),   # right
                         ([(o0, o1), (f0, f1), (f1, f1), (o1, o1)], 0.08)]   # bottom, in shadow
                for poly, k in walls:
                    # each wall darkens toward the floor: draw it in bands
                    for b in range(12):
                        t0, t1 = b / 12, (b + 1) / 12
                        def lerp(pa, pb, t): return (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)
                        outer = (poly[0], poly[1]); inner = (poly[3], poly[2])
                        q = [lerp(outer[0], inner[0], t0), lerp(outer[1], inner[1], t0), lerp(outer[1], inner[1], t1), lerp(outer[0], inner[0], t1)]
                        kk = k * (1 - 0.85 * (t0 + t1) / 2)
                        dl.polygon(q, fill=tuple(int(col[c_] * kk) for c_ in range(3)) + (235,))
                dl.rectangle([f0, f0, f1, f1], fill=(4, 4, 6, 255))
                for a_, b_ in [((o0, o0), (f0, f0)), ((o1, o0), (f1, f0)), ((o0, o1), (f0, f1)), ((o1, o1), (f1, f1))]:
                    dl.line([a_, b_], fill=col + (110,), width=max(1, int(0.6 * SS)))
                dl.rectangle([f0, f0, f1, f1], outline=col + (90,), width=max(1, int(0.6 * SS)))
            elif interior == 'tunnel':    # rings stepping down into the dark
                for k, (inset, al) in enumerate([(7, 0.55), (12, 0.34), (16, 0.2), (19, 0.1)]):
                    q = inset * SS
                    dl.rectangle([q, q, n - q, n - q], outline=col + (int(255 * al),), width=max(1, int((1.3 - 0.25 * k) * SS)))
            elif interior == 'vortex':    # a black hole in the middle
                yy2, xx2 = np.mgrid[0:n, 0:n]; r2 = np.hypot(xx2 - cen, yy2 - cen) / (n / 2 - i0)
                a2 = np.clip(1.15 - r2, 0, 1) ** 0.7
                arr = np.zeros((n, n, 4), np.uint8); arr[..., 3] = (a2 * 255 * 0.95).clip(0, 255)
                L_ = Image.fromarray(arr)
            elif interior == 'glowstreaks':   # soft streaks of light rushing toward the middle
                # each streak fades in from the rim (so its outer end melts into the rim glow),
                # is brightest partway in, then thins out toward the dark middle
                rng = np.random.default_rng(7)              # fixed seed: the same "random" pattern every time
                for k in range(26):
                    ang = k * 2 * np.pi / 26 + rng.uniform(-0.08, 0.08)
                    r0 = n * rng.uniform(0.48, 0.70)            # outer end, out in the rim glow (clipped to the inside)
                    r1 = n * rng.uniform(0.08, 0.22)            # inner end: fades to nothing toward the middle
                    w0 = rng.uniform(2.2, 3.4) * SS             # wide near the rim...
                    w1 = 0.3 * SS                               # ...to a point near the middle
                    strength = rng.uniform(0.55, 0.95)
                    ca, sa = np.cos(ang), np.sin(ang); px_, py_ = -sa, ca     # along the ray, and across it
                    SEG = 16
                    for seg in range(SEG):
                        t0, t1 = seg / SEG, (seg + 1) / SEG                   # 0 = outer end, 1 = inner end
                        ra, rb = r0 + (r1 - r0) * t0, r0 + (r1 - r0) * t1
                        wa, wb = (w0 + (w1 - w0) * t0) / 2, (w0 + (w1 - w0) * t1) / 2
                        q = [(cen + ra * ca + wa * px_, cen + ra * sa + wa * py_), (cen + rb * ca + wb * px_, cen + rb * sa + wb * py_),
                             (cen + rb * ca - wb * px_, cen + rb * sa - wb * py_), (cen + ra * ca - wa * px_, cen + ra * sa - wa * py_)]
                        tm_ = (t0 + t1) / 2
                        ease = min(1.0, tm_ / 0.38) ** 2.0                         # eases in where it meets the rim glow
                        a_ = strength * 0.8 * ease * (1 - tm_) ** 1.3                 # bright near the rim, gone toward the center
                        dl.polygon(q, fill=col + (int(255 * a_),))
                m_ = Image.new('L', (n, n), 0); ImageDraw.Draw(m_).rectangle([i0, i0, n - i0, n - i0], fill=255)
                soft = L_.filter(ImageFilter.GaussianBlur(1.9 * SS))
                glow_ = Image.new('RGBA', (n, n), (0, 0, 0, 0)); glow_.alpha_composite(soft); glow_.alpha_composite(soft)
                core = np.array(L_).astype(np.float32); core[..., 3] *= 0.2
                glow_.alpha_composite(Image.fromarray(core.clip(0, 255).astype(np.uint8)))
                L_ = glow_
                L_.putalpha(Image.fromarray(np.minimum(np.array(L_)[..., 3], np.array(m_))))
            elif interior == 'streaks':   # gold streaks rushing toward the middle
                for k in range(24):
                    ang = k * np.pi / 12 + 0.13
                    r0, r1 = n * 0.62, n * 0.18
                    x0_, y0_ = cen + r0 * np.cos(ang), cen + r0 * np.sin(ang)
                    x1_, y1_ = cen + r1 * np.cos(ang), cen + r1 * np.sin(ang)
                    for seg in range(6):
                        t0, t1 = seg / 6, (seg + 1) / 6
                        dl.line([(x0_ + (x1_ - x0_) * t0, y0_ + (y1_ - y0_) * t0), (x0_ + (x1_ - x0_) * t1, y0_ + (y1_ - y0_) * t1)],
                                fill=col + (int(120 * (1 - t0)),), width=max(1, int((1.0 - 0.12 * seg) * SS)))
                m_ = Image.new('L', (n, n), 0); ImageDraw.Draw(m_).rectangle([i0, i0, n - i0, n - i0], fill=255)
                L_.putalpha(Image.fromarray(np.minimum(np.array(L_)[..., 3], np.array(m_))))
            patch.alpha_composite(L_, tuple(int(v) for v in P(sx0, sy0)))

    if interior == 'glowstreaks': draw_interior()     # under the rim glow, so the glow hides the rays' wide bases
    # soft glow inside (A)
    n = SW * SS
    yy_, xx_ = np.mgrid[0:n, 0:n]
    inside = np.minimum.reduce([xx_, n - 1 - xx_, yy_, n - 1 - yy_]) / SS >= IN_PX
    bl = np.array(Image.fromarray(((~inside) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(glow_r * SS))) / 255
    a = np.where(inside, glow_k * bl, 0)
    g = np.zeros((n, n, 4), np.uint8); g[..., 0], g[..., 1], g[..., 2] = mix(col, (255, 190, 0), 0.0) if col == GOLD else col; g[..., 3] = (a * 255).clip(0, 255)
    patch.alpha_composite(Image.fromarray(g), tuple(int(v) for v in P(sx0, sy0)))
    if dark_mid:                 # a darker middle: black, strongest at the center, under the number
        r_ = np.hypot(xx_ - n / 2, yy_ - n / 2) / (n / 2)
        dm = np.where(inside, dark_mid * np.clip(1 - r_, 0, 1) ** 0.8, 0)
        k_ = np.zeros((n, n, 4), np.uint8); k_[..., 3] = (dm * 255).clip(0, 255)
        patch.alpha_composite(Image.fromarray(k_), tuple(int(v) for v in P(sx0, sy0)))
    if interior and interior != 'glowstreaks': draw_interior()
    # the count
    kind = num[0]
    if kind == 'glow':            # the number in the frame's color, glowing
        f = ImageFont.truetype(FIRA % 'Black', int(num_size * U * SS))
        W_, H_ = int(13 * U * SS * 2.6), int(13 * U * SS * 1.8)
        img = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        halo = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        # the glow comes from the plain digits (no thickening), so the inside of the 0
        # and the gap between digits stay dark
        ImageDraw.Draw(halo).text((W_ / 2, H_ / 2), count, font=f, fill=col + (255,), anchor='mm')
        h1 = halo.filter(ImageFilter.GaussianBlur(1.6 * SS))
        h1 = Image.fromarray((np.array(h1).astype(np.float32) * [1, 1, 1, 0.75]).clip(0, 255).astype(np.uint8))
        img.alpha_composite(h1)
        edge_ = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))     # a faint dark edge keeps the digits crisp
        ImageDraw.Draw(edge_).text((W_ / 2, H_ / 2), count, font=f, fill=(0, 0, 0, 0), anchor='mm', stroke_width=int(0.5 * U * SS), stroke_fill=(20, 8, 0, 140))
        img.alpha_composite(edge_)
        core = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        ImageDraw.Draw(core).text((W_ / 2, H_ / 2), count, font=f, fill=mix(col, (255, 255, 255), 0.3) + (255,), anchor='mm')
        img.alpha_composite(core)
    elif kind == 'radial':          # graded across the whole number: bright at its outer edges, dark in the middle
        f = ImageFont.truetype(FIRA % 'Black', int(num_size * U * SS))
        W_, H_ = int(13 * U * SS * 2.6), int(13 * U * SS * 1.8)
        m = Image.new('L', (W_, H_), 0); ImageDraw.Draw(m).text((W_ / 2, H_ / 2), count, font=f, fill=255, anchor='mm')
        M = np.array(m); ys_, xs_ = np.where(M > 0)
        x0_, x1_, y0_, y1_ = xs_.min(), xs_.max(), ys_.min(), ys_.max()
        gy, gx = np.mgrid[0:H_, 0:W_]
        u_ = (gx - (x0_ + x1_) / 2) / ((x1_ - x0_) / 2); v_ = (gy - (y0_ + y1_) / 2) / ((y1_ - y0_) / 2)
        r_n = np.sqrt(u_ ** 2 + v_ ** 2)
        t = np.clip((r_n - dark_r) / (1.0 - dark_r), 0, 1) ** 1.3     # dark_r: the fully dark core, as a share of the number's size
        edge, center = (mix(col, (255, 255, 255), 0.55), mix(col, (25, 8, 0), 0.85)) if num_center is None else ((255, 255, 255), num_center)
        im_ = np.zeros((H_, W_, 4), np.float32)
        for k in range(3): im_[..., k] = center[k] * (1 - t) + edge[k] * t
        im_[..., 3] = M
        img = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        o = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        ImageDraw.Draw(o).text((W_ / 2, H_ / 2), count, font=f, fill=(0, 0, 0, 255), anchor='mm', stroke_width=int(1.1 * U * SS), stroke_fill=(0, 0, 0, 255))
        img.alpha_composite(o.filter(ImageFilter.GaussianBlur(0.6 * SS)))
        img.alpha_composite(Image.fromarray(im_.clip(0, 255).astype(np.uint8)))
        if num_blur: img = img.filter(ImageFilter.GaussianBlur(num_blur * SS))
    elif kind == 'gold':
        img = shaded_number(count, 13, mix(col, (255, 255, 255), 0.4), mix(col, (40, 18, 0), 0.72))
    elif kind == 'white':
        img = shaded_number(count, 13, (255, 255, 255), (115, 100, 78))
    elif kind == 'goldsoft':
        img = shaded_number(count, 13, mix(col, (255, 255, 255), 0.4), mix(col, (40, 18, 0), 0.72), outline=False)
        halo = Image.new('RGBA', img.size, (0, 0, 0, 0)); hm = np.array(img)[..., 3]
        hh = Image.fromarray(np.dstack([np.zeros_like(hm)] * 3 + [hm])).filter(ImageFilter.GaussianBlur(2.2 * SS))
        halo.alpha_composite(hh); halo.alpha_composite(hh); halo.alpha_composite(img); img = halo
    else:
        f = ImageFont.truetype(FIRA % 'Bold', int(13 * U * SS))
        img = Image.new('RGBA', (int(13 * U * SS * 2.2), int(13 * U * SS * 1.6)), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((img.width / 2, img.height / 2), count, font=f, fill=(255, 255, 255, 255), anchor='mm', stroke_width=SS, stroke_fill=(0, 0, 0, 255))
    if num_alpha < 1:
        arr = np.array(img).astype(np.float32); arr[..., 3] *= num_alpha
        img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    p = P(cx, cy)
    patch.alpha_composite(img, (int(p[0] - img.width / 2), int(p[1] - img.height / 2)))
    if arrow_layers:
        for lay in arrow_layers: patch.alpha_composite(lay)
    out = base.copy()
    out.paste(patch.resize((PX1 - PX0, PY1 - PY0), Image.LANCZOS).convert('RGB'), (PX0 - OX, PY0 - OY))
    return out, (sx0, sy0, sx1, sy1, cx)

fl = ImageFont.truetype(FIRA % 'Regular', 18); fs = ImageFont.truetype(FIRA % 'Regular', 14)
def sheet(items, path, note, zoom_box, z=3):
    tiles = []
    for label, img in items:
        act = img.crop((1440 - OX, 1080 - OY, 1785 - OX, 1206 + EXTRA + 14 - OY))
        zb = [zoom_box[0] - OX, zoom_box[1] - OY, zoom_box[2] - OX, zoom_box[3] - OY]
        zoom = img.crop(zb).resize(((zb[2] - zb[0]) * z, (zb[3] - zb[1]) * z), Image.LANCZOS)
        tiles.append((label, act, zoom))
    pad = 14
    cw = pad + tiles[0][1].width + pad + tiles[0][2].width + pad
    ch = 30 + max(tiles[0][1].height, tiles[0][2].height) + pad
    canvas = Image.new('RGB', (cw, 28 + ch * len(tiles)), (18, 20, 26)); cd = ImageDraw.Draw(canvas)
    cd.text((pad, 5), note, fill=(140, 150, 170), font=fs)
    for i, (label, act, zoom) in enumerate(tiles):
        y = 28 + i * ch
        cd.text((pad, y), label, fill=(255, 209, 0), font=fl)
        canvas.paste(act, (pad, y + 30)); canvas.paste(zoom, (pad * 2 + act.width, y + 30))
    canvas.save(path); print(path, canvas.size)

ZB = (1662, 1090, 1772, 1206 + EXTRA + 10)
if os.environ.get('GLOW'):
    O37 = mix(GOLD, ORANGE, 0.37)
    g_ = dict(col=O37, n_stack=3, ch_size=16, chev_sizes=[17, 13.5, 10], step=6.5, glow_r=6.6, glow_k=1.6, dark_mid=0.6,
              interior='glowstreaks', num=('glow',), num_size=11.5)
    if os.environ.get('WINDOW'):
        img_, box = render(**g_)[:2]
        win_ = img_.crop((1162 - OX, 230 - OY, 1782 - OX, 1206 + EXTRA + 18 - OY))      # the whole AetherPack window
        zb = (1162 - OX, 1040 - OY, 1782 - OX, 1206 + EXTRA + 18 - OY)
        zoom = img_.crop(zb).resize(((zb[2] - zb[0]) * 2, (zb[3] - zb[1]) * 2), Image.LANCZOS)
        fnt = ImageFont.truetype(FIRA % 'Regular', 18)
        pad = 16
        cv = Image.new('RGB', (pad * 3 + win_.width + zoom.width, 40 + max(win_.height, zoom.height) + pad), (18, 20, 26))
        cdd = ImageDraw.Draw(cv)
        cdd.text((pad, 10), "Your AetherPack window, actual size", fill=(255, 209, 0), font=fnt)
        cdd.text((pad * 2 + win_.width, 10), "2x: the bottom of the window", fill=(255, 209, 0), font=fnt)
        cv.paste(win_, (pad, 40)); cv.paste(zoom, (pad * 2 + win_.width, 40))
        cv.save(OUTDIR + '/deposit_in_window.png'); print(cv.size)
        sys.exit(0)
    if os.environ.get('PULSE'):
        r1, box = render(**{**g_, 'num_alpha': 1.0})[:2]
        r0, _ = render(**{**g_, 'num_alpha': 0.0})[:2]
        bx0_, by0_, bx1_, by1_, cx_ = box
        q = (int(cx_ - 40) - OX, 1092 - OY, int(cx_ + 40) - OX, int(by1_ + 6) - OY)
        A1, A0 = r1.crop(q), r0.crop(q)
        Z = 3
        frames = []
        N, MS = 27, 100                          # 27 frames x 100 ms = 2.7 s per pulse
        LOW = 0.10                               # dims to 10%, never fully gone
        fnt = ImageFont.truetype(FIRA % 'Regular', 16)
        for i in range(N):
            ph = (1 + np.cos(2 * np.pi * i / N)) / 2            # 1 -> 0 -> 1, eased
            img_ = Image.blend(A0, A1, LOW + (1 - LOW) * ph)
            fr = Image.new('RGB', (A1.width * Z + 20, A1.height * Z + 40), (18, 20, 26))
            ImageDraw.Draw(fr).text((10, 8), "100% to 10%, 2.7 s per pulse", fill=(255, 209, 0), font=fnt)
            fr.paste(img_.resize((A1.width * Z, A1.height * Z), Image.LANCZOS), (10, 34))
            frames.append(fr.convert('P', palette=Image.ADAPTIVE, colors=200))
        frames[0].save(OUTDIR + '/deposit_pulse_27.gif', save_all=True, append_images=frames[1:], duration=[MS] * N, loop=0, disposal=2)
        print('gif', frames[0].size)
        sys.exit(0)
    if os.environ.get('ALPHAS'):
        imgs = [(a_,) + render(**{**g_, 'num_alpha': a_}) for a_ in (1.0, 0.85, 0.7, 0.55)]
        zs = []
        for a_, im, (bx0_, by0_, bx1_, by1_, cx_) in imgs:
            q = (int(bx0_ - 3) - OX, int(by0_ - 3) - OY, int(bx0_ - 3) - OX + 62, int(by0_ - 3) - OY + 62)
            z = im.crop(q).resize((62 * 5, 62 * 5), Image.LANCZOS)
            act = im.crop((int(cx_ - 36) - OX, 1092 - OY, int(cx_ + 36) - OX, int(by1_ + 6) - OY))
            zs.append((a_, z, act))
        pad = 18
        cv = Image.new('RGB', (pad + 4 * (310 + pad), 40 + 310 + 16 + 140 + 16), (18, 20, 26)); cdd = ImageDraw.Draw(cv)
        cdd.text((pad, 8), "The number at different opacities (5x zoom; actual size below)", fill=(140, 150, 170), font=fs)
        for i, (a_, z, act) in enumerate(zs):
            x = pad + i * (310 + pad)
            cv.paste(z, (x, 36)); cv.paste(act, (x + 120, 36 + 310 + 12))
            cdd.text((x, 36 + 310 + 60), "%d%%" % round(a_ * 100), fill=(255, 209, 0), font=fl)
        cv.save(OUTDIR + '/deposit_v4_alpha2.png'); print(cv.size)
        sys.exit(0)
    sheet([("Rays: wide and bright at the rim, narrowing and fading toward the center", render(**g_)[0])],
          OUTDIR + '/deposit_v4_glow10.png', "Actual size at left, 3x zoom at right. 37% orange.", ZB)
    sys.exit(0)
if os.environ.get('FALL'):
    O37 = mix(GOLD, ORANGE, 0.37)
    base_ = dict(col=O37, n_stack=3, ch_size=16, step=6.2, glow_r=4.3, glow_k=1.3, dark_mid=0.4, num=('radial',), num_center=(48, 48, 52), dark_r=0.35)
    shrink = dict(chev_sizes=[17, 13.5, 10], step=6.5)
    sheet([("1. Chevrons shrink as they fall in", render(**{**base_, **shrink})[0]),
           ("2. + a shaft: four walls down to a small dark floor, number at the bottom", render(**{**base_, **shrink, 'interior': 'shaft', 'num_size': 9.5, 'dark_mid': 0.15})[0]),
           ("3. + rings stepping down into the dark", render(**{**base_, **shrink, 'interior': 'tunnel', 'num_size': 11})[0]),
           ("4. + a black hole in the middle, number small and soft", render(**{**base_, **shrink, 'interior': 'vortex', 'num_size': 10.5, 'num_blur': 0.25, 'num_center': (70, 70, 74)})[0]),
           ("5. + gold streaks rushing toward the middle", render(**{**base_, **shrink, 'interior': 'streaks', 'num_size': 11, 'dark_mid': 0.6})[0])],
          OUTDIR + '/deposit_v4_falling.png', "Ideas for a falling-in feeling. Actual size at left, 3x zoom at right. 37% orange.", ZB)
    sys.exit(0)
if os.environ.get('THREE'):
    O37 = mix(GOLD, ORANGE, 0.37)
    common = dict(col=O37, n_stack=3, ch_size=16, step=6.2, glow_r=4.3, glow_k=1.3, dark_mid=0.4, num=('radial',))
    sheet([("Last time", render(num_center=(78, 78, 82), **common)[0]),
           ("Darker middle, wider dark area", render(num_center=(48, 48, 52), dark_r=0.35, **common)[0]),
           ("Darker still, wider again", render(num_center=(38, 38, 42), dark_r=0.5, **common)[0])],
          OUTDIR + '/deposit_v3_white2.png', "Actual size at left, 3x zoom at right.", ZB)
    sys.exit(0)
# 1. the layout: even stack vs fading in
sheet([("Stack of five, all the same", render()[0]),
       ("Stack of five, fading in from the top", render(stack_fade=True)[0])],
      OUTDIR + '/deposit_v3_layout.png', "Actual size at left (window stretched down a little to fit), 3x zoom at right.", ZB)
# 2. the number, darker toward the middle of each stroke
sheet([("1. Gold, darker toward the middle (like the glow)", render(num=('gold',))[0]),
       ("2. White, darker toward the middle", render(num=('white',))[0]),
       ("3. Gold, darker toward the middle, soft shadow instead of an outline", render(num=('goldsoft',))[0])],
      OUTDIR + '/deposit_v3_numbers.png', "The count, shaded inside each stroke. 5x zoom at right.", (1684, 1163, 1754, 1232), z=5)
# 3. more and more orange mixed into the gold (rim, glow, chevrons, label and number)
row = []
import os
TS = [float(v) for v in os.environ.get('ORANGE_TS', '0,0.25,0.5,0.75,1').split(',')]
for t in TS:
    col = mix(GOLD, ORANGE, t)
    img, (sx0, sy0, sx1, sy1, cx) = render(col=col)
    row.append((t, col, img.crop((int(sx0 - 22) - OX, 1092 - OY, int(sx1 + 22) - OX, int(sy1 + 8) - OY))))
z = 3; pad = 18
tw = row[0][2].width * z
canvas = Image.new('RGB', (pad + len(row) * (tw + pad), 34 + row[0][2].height * (z + 1) + 24), (18, 20, 26)); cd = ImageDraw.Draw(canvas)
cd.text((pad, 8), "More orange mixed into the gold, left to right (3x zoom; actual size under each)", fill=(140, 150, 170), font=fs)
for i, (t, col, img) in enumerate(row):
    x = pad + i * (tw + pad)
    canvas.paste(img.resize((tw, img.height * z), Image.LANCZOS), (x, 34))
    canvas.paste(img, (x, 34 + img.height * z + 8))
    cd.text((x + img.width + 10, 34 + img.height * z + 14), "%d%% orange" % round(t * 100), fill=col, font=fl)
canvas.save(OUTDIR + '/' + os.environ.get('ORANGE_OUT', 'deposit_v3_orange.png')); print('orange', canvas.size)
