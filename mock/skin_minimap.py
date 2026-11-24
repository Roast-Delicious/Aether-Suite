# Mockup: the minimap in the Aether look, four options, on the user's screenshot.
import sys; sys.path.insert(0, '/home/claude/mock')
from skins_lib import *
from PIL import Image, ImageDraw
import numpy as np, cv2
FULL = Image.open('/tmp/v4/f_057.png').convert('RGB')
A = np.array(FULL)
CX, CY, RM = 2131, 206, 117            # Blizzard minimap: center and map radius (px)
X0, Y0, X1, Y1 = 1900, 0, 2304, 440    # region shown

# 1) world with Blizzard's ring, zone box, coords box and buttons painted out
mask = np.zeros(A.shape[:2], np.uint8)
cv2.circle(mask, (CX, CY), 152, 255, -1); cv2.circle(mask, (CX, CY), RM - 1, 0, -1)
cv2.rectangle(mask, (2015, 0), (2275, 34), 255, -1)      # zone + clock strip
cv2.rectangle(mask, (2070, 345), (2190, 386), 255, -1)   # coords box
cv2.circle(mask, (2203, 95), 26, 255, -1); cv2.circle(mask, (2014, 292), 24, 255, -1)
cv2.rectangle(mask, (1998, 0), (2030, 30), 255, -1); cv2.rectangle(mask, (2232, 30), (2262, 58), 255, -1)
CLEAN = cv2.inpaint(A[..., ::-1], mask, 9, cv2.INPAINT_TELEA)[..., ::-1]
# 2) map content: the disk, and a square version with the corners filled in
disk = np.zeros(A.shape[:2], np.uint8); cv2.circle(disk, (CX, CY), RM - 2, 255, -1)
sq = np.zeros(A.shape[:2], np.uint8); cv2.rectangle(sq, (CX - 132, CY - 132), (CX + 132, CY + 132), 255, -1)
MAPSQ = cv2.inpaint(A[..., ::-1], cv2.bitwise_and(sq, cv2.bitwise_not(disk)), 15, cv2.INPAINT_TELEA)[..., ::-1]
SUN = FULL.crop((2181, 73, 2225, 117)); GEM = FULL.crop((1993, 271, 2035, 313))
def _moon():   # a simple pale crescent for the mockup (the game shows its own moon icon)
    im = Image.new('RGBA', (176, 176), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([28, 28, 148, 148], fill=(225, 232, 245, 255)); d.ellipse([60, 14, 176, 130], fill=(0, 0, 0, 0))
    return im.resize((44, 44), Image.LANCZOS)
MOON = _moon()

def _sun(style):
    """Original flat sun icons to pair with the moon stand-in (Aether gold)."""
    import math
    N = 176; im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c0 = N / 2
    G = GOLD + (255,)
    if style == 'A':      # disc + 8 short rounded rays
        d.ellipse([c0 - 40, c0 - 40, c0 + 40, c0 + 40], fill=G)
        for k in range(8):
            a = math.radians(k * 45); r0, r1 = 54, 78
            d.line([(c0 + r0 * math.cos(a), c0 + r0 * math.sin(a)), (c0 + r1 * math.cos(a), c0 + r1 * math.sin(a))], fill=G, width=13)
            for rr in (r0, r1):
                d.ellipse([c0 + rr * math.cos(a) - 6.5, c0 + rr * math.sin(a) - 6.5, c0 + rr * math.cos(a) + 6.5, c0 + rr * math.sin(a) + 6.5], fill=G)
    elif style == 'B':    # disc + 12 thin tapered rays
        d.ellipse([c0 - 36, c0 - 36, c0 + 36, c0 + 36], fill=G)
        for k in range(12):
            a = math.radians(k * 30); w = math.radians(7)
            pts = [(c0 + 48 * math.cos(a - w), c0 + 48 * math.sin(a - w)), (c0 + 82 * math.cos(a), c0 + 82 * math.sin(a)),
                   (c0 + 48 * math.cos(a + w), c0 + 48 * math.sin(a + w))]
            d.polygon(pts, fill=G)
    else:                 # disc + a thin halo ring
        d.ellipse([c0 - 44, c0 - 44, c0 + 44, c0 + 44], fill=G)
        d.ellipse([c0 - 70, c0 - 70, c0 + 70, c0 + 70], outline=G, width=9)
    return im.resize((44, 44), Image.LANCZOS)
SUNS = {k: _sun(k) for k in 'ABC'}


def base(square, half=126):
    im = CLEAN.copy()
    if square:
        m = np.zeros(A.shape[:2], np.uint8)
        cv2.rectangle(m, (CX - half, CY - half), (CX + half, CY + half), 255, -1)
        im[m > 0] = MAPSQ[m > 0]
    else:
        im[disk > 0] = A[disk > 0]
    return Canvas(Image.fromarray(im).crop((X0, Y0, X1, Y1)))

def chevs(c, cx, cy, rx, ry, top=26, side=26):
    for x, y, rot, sz in ((cx, cy - ry, 0, top), (cx, cy + ry, 180, side), (cx + rx, cy, -90, side), (cx - rx, cy, 90, side)):
        k = u(sz); X, Y = c.P(x, y)
        for name, col in (('win_chev_dark', (10, 11, 14)), ('win_chev_gold', GOLD)):
            c.im.alpha_composite(tga(name, col, (k, k)).rotate(rot, resample=Image.BICUBIC), (X - k // 2, Y - k // 2))
    c.d = ImageDraw.Draw(c.im)

def pill(c, box, text, size=15, color=WHITE, gold_line=False, right=None):
    x0, y0, x1, y1 = c.P(*box)
    Lr, d = c.layer()
    d.rounded_rectangle([x0, y0, x1, y1], (y1 - y0) // 2, fill=NAVY + (235,), outline=BLUE + (255,), width=SS)
    if gold_line: d.line([x0 + 3 * (y1 - y0) // 4, y1 - 3 * SS, x1 - 3 * (y1 - y0) // 4, y1 - 3 * SS], fill=GOLD + (220,), width=SS)
    c.over(Lr)
    if right:
        c.text((box[0] + 16, (box[1] + box[3]) / 2), text, size, color, 'SemiBold', 'lm')
        c.text((box[2] - 14, (box[1] + box[3]) / 2), right, size, WHITE, 'Regular', 'rm')
    else:
        c.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), text, size, color, 'SemiBold', 'mm')

def button(c, xy, icon, r=17):
    x, y = xy; Lr, d = c.layer(); X, Y = c.P(x, y); R = r * SS
    d.ellipse([X - R, Y - R, X + R, Y + R], fill=NAVY + (255,), outline=BLUE + (255,), width=SS); c.over(Lr)
    k = int(r * 1.5); c.paste(icon, (x - k / 2, y - k / 2), (k, k))

def opt_round(ring, width=2):
    c = base(False); cx, cy = CX - X0, CY - Y0
    W, H = c.im.size; X, Y = c.P(cx, cy); R = (RM + 1) * SS
    c.over(glow(W, H, (X, Y, X, Y), R, u(10), BLUE, 0.45))
    Lr, d = c.layer()
    col = GOLD if ring == 'gold' else BLUE
    Ro = R + (width // 2) * SS   # a thicker ring grows outward; the map stays the same size
    d.ellipse([X - Ro, Y - Ro, X + Ro, Y + Ro], outline=col + (255,), width=width * SS)
    i = u(3); d.ellipse([X - R + i, Y - R + i, X + R - i, Y + R - i], outline=BLUE + (90,), width=SS)
    c.over(Lr)
    if ring != 'gold': chevs(c, cx, cy, RM + 6 + width // 2, RM + 6 + width // 2)
    pill(c, (cx - 118, 6, cx + 118, 34), "Dustwallow Marsh", 15, GOLD, right="05:52")
    pill(c, (cx - 52, cy + RM + 16, cx + 52, cy + RM + 42), "62.5, 44.4", 15, WHITE)
    button(c, (cx + 84, cy - 86), SUN); button(c, (cx - 86, cy + 84), GEM)
    return c.done()

def opt_square(style):
    half = 126; c = base(True, half); cx, cy = CX - X0, CY - Y0
    box = (cx - half, cy - half, cx + half, cy + half)
    W, H = c.im.size; x0, y0, x1, y1 = c.P(*box); R = u(8)
    if style == 'window':
        top = box[1] - 30
        c.over(glow(W, H, (x0, c.P(0, top)[1], x1, y1 + u(28)), R, u(10), BLUE, 0.42))
        Lr, d = c.layer()
        # title strip above the map, coords strip under it, one rounded frame around all
        d.rounded_rectangle(c.P(box[0], top, box[2], box[1]), R, fill=NAVY + (255,))
        d.rectangle(c.P(box[0], top + 10, box[2], box[1]), fill=NAVY + (255,))
        d.rectangle(c.P(box[0], box[3], box[2], box[3] + 18), fill=PANEL + (240,))
        d.rounded_rectangle(c.P(box[0], box[3], box[2], box[3] + 28), R, fill=PANEL + (240,))
        d.line(c.P(box[0] + 4, box[1], box[2] - 4, box[1]), fill=GOLD + (220,), width=SS)
        d.rounded_rectangle(c.P(box[0], top, box[2], box[3] + 28), R, outline=BLUE + (255,), width=SS)
        i = 3; d.rounded_rectangle(c.P(box[0] + i, top + i, box[2] - i, box[3] + 28 - i), R - u(3), outline=BLUE + (85,), width=SS)
        c.over(Lr)
        c.text((box[0] + 12, top + 15), "Dustwallow Marsh", 15, GOLD, 'SemiBold', 'lm')
        c.text((box[2] - 12, top + 15), "05:52", 15, WHITE, 'Regular', 'rm')
        c.text((cx, box[3] + 14), "62.5, 44.4", 15, WHITE, 'SemiBold', 'mm')
        chevs(c, cx, (top + box[3] + 28) / 2, half + 5, (box[3] + 28 - top) / 2 + 5, 26, 26)
        button(c, (box[2] - 22, box[1] + 22), SUN, 15); button(c, (box[0] + 22, box[3] - 22), GEM, 15)
    else:   # minimal
        c.over(glow(W, H, (x0, y0, x1, y1), R, u(6), BLUE, 0.3))
        Lr, d = c.layer()
        # round the map's corners: paint the world back outside the rounded square
        d.rounded_rectangle([x0, y0, x1, y1], R, outline=BLUE + (255,), width=SS)
        c.over(Lr)
        c.text((cx, box[1] + 14), "Dustwallow Marsh", 15, GOLD, 'SemiBold', 'mm', outline=True)
        c.text((box[2] - 8, box[3] - 12), "62.5, 44.4", 14, WHITE, 'SemiBold', 'rm', outline=True)
        c.text((box[0] + 8, box[3] - 12), "05:52", 14, WHITE, 'Regular', 'lm', outline=True)
        button(c, (box[2] - 20, box[1] + 36), SUN, 14); button(c, (box[0] + 20, box[1] + 36), GEM, 14)
    return c.done()

def ring3d(c, cx, cy, r_in, width, style, light=(-0.55, -0.65), hl=(255, 255, 255), tint=0.0):
    """A blue ring drawn with light from the top-left: 'tube' (round, glossy),
    'bevel' (flatter, lit top half, shaded bottom half), 'sunk' (tube plus
    a soft shadow cast onto the map edge, so the map sits below it)."""
    W, H = c.im.size; X, Y = c.P(cx, cy)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - X, yy - Y; r = np.hypot(dx, dy) / SS
    t = (r - r_in) / width                      # 0 inner edge .. 1 outer edge
    cover = np.clip(np.minimum(t * width + 0.5, (1 - t) * width + 0.5), 0, 1)   # anti-aliased band
    ux, uy = dx / np.maximum(r * SS, 1e-3), dy / np.maximum(r * SS, 1e-3)
    L = np.array([light[0], light[1], 0.52]); L = L / np.linalg.norm(L)    # light direction, a bit in front
    tc = np.clip(t, 0, 1)
    if style == 'bevel':
        nr = np.where(tc < 0.5, -0.7, 0.7); nz = np.full_like(tc, 0.72)
    else:
        nr = 2 * tc - 1; nz = np.sqrt(np.clip(1 - nr ** 2, 0, 1))
    nx, ny = nr * ux, nr * uy
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    # specular: reflect the view (0,0,1) about the normal
    hx, hy, hz = L[0], L[1], L[2] + 1; hn = np.sqrt(hx * hx + hy * hy + hz * hz)
    spec = np.clip((nx * hx + ny * hy + nz * hz) / hn, 0, 1) ** (40 if style != 'bevel' else 18)
    base = np.array(BLUE, np.float32)
    lit_b = (0.12 + 1.1 * diff ** 1.4)[..., None]
    blue = base[None, None, :] * np.minimum(lit_b, 1.15)
    # the shine: where the light is strongest, blend toward the highlight color
    # (blending, not adding, so gold stays exactly Aether gold)
    a = np.clip((lit_b[..., 0] - 0.95) * 2.2 + spec + tint * diff ** 2, 0, 1)[..., None]
    col = blue * (1 - a) + np.array(hl, np.float32)[None, None, :] * a
    edge = np.clip(1 - np.minimum(t, 1 - t) * width / 0.8, 0, 1) * 0.55     # thin dark rim at both edges
    col = col * (1 - edge[..., None])
    out = np.zeros((H, W, 4), np.float32); out[..., :3] = np.clip(col, 0, 255); out[..., 3] = cover * 255
    d_out = r - (r_in + width)
    lit = np.clip(ux * L[0] + uy * L[1], -1, 1)          # -1 = side facing away from the light
    sh_o = np.where((d_out > -1) & (d_out < 7), (1 - np.clip(d_out, 0, 7) / 7) ** 2, 0) * np.clip(-lit * 0.9 + 0.2, 0, 1)
    so = np.zeros((H, W, 4), np.float32); so[..., 3] = sh_o * 220
    c.over(Image.fromarray(so.astype(np.uint8)))
    if style == 'sunk':     # soft shadow on the map, just inside the ring, heavier at the bottom-right
        d_in = r_in - r
        sh = np.where((d_in > -1) & (d_in < 16), (1 - np.clip(d_in, 0, 16) / 16) ** 1.4, 0) * (0.55 + 0.45 * np.clip(-lit, 0, 1) + 0.3 * np.clip(lit, 0, 1))
        shadow = np.zeros((H, W, 4), np.float32); shadow[..., 3] = np.clip(sh, 0, 1) * 250
        c.over(Image.fromarray(shadow.astype(np.uint8)))
    c.over(Image.fromarray(out.astype(np.uint8)))

def opt_3d(style, width=11, **kw):
    c = base(False); cx, cy = CX - X0, CY - Y0
    W, H = c.im.size; X, Y = c.P(cx, cy); R = (RM + 1) * SS
    c.over(glow(W, H, (X, Y, X, Y), R + width * SS, u(10), BLUE, 0.4))
    ring3d(c, cx, cy, RM - 2, width, style, **kw)
    chevs(c, cx, cy, RM + 6 + width // 2, RM + 6 + width // 2)
    pill(c, (cx - 118, 6, cx + 118, 34), "Dustwallow Marsh", 15, GOLD, right="05:52")
    pill(c, (cx - 52, cy + RM + 16, cx + 52, cy + RM + 42), "62.5, 44.4", 15, WHITE)
    button(c, (cx + 84, cy - 86), SUN); button(c, (cx - 86, cy + 84), GEM)
    return c.done()

def ring_cone(c, cx, cy, r_in, width, gold=0.3, hl=GOLD, night=False, src=(84, -86), height=90, cone=(25, 120), reach=170):
    """Bevel (ridge) ring lit by a wide cone of light shining down from the
    sun/moon button. src = the light's spot over the screen (px from the
    ring's center), height = how far in front of the screen it is, cone =
    full-strength and fade-out angles (degrees) around the cone's axis, which
    points from the light at the ring's center. gold = how far the lit
    faces go toward Aether gold. Blue and gold are never mixed half and half
    (that makes a pale gray-white): the change happens over a short step and
    the in-between is kept dark."""
    W, H = c.im.size; X, Y = c.P(cx, cy)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = (xx - X) / SS, (yy - Y) / SS; r = np.hypot(dx, dy)
    t = (r - r_in) / width
    cover = np.clip(np.minimum(t * width + 0.5, (1 - t) * width + 0.5), 0, 1)
    ux, uy = dx / np.maximum(r, 1e-3), dy / np.maximum(r, 1e-3)
    tc = np.clip(t, 0, 1)
    nr = np.where(tc < 0.5, -0.7, 0.7); nz = 0.72
    nx, ny = nr * ux, nr * uy
    # light: from the sun's side and from in front ("coming down"), in a wide cone
    # centered on the sun: full strength within cone[0] degrees around the ring
    # from the sun, fading to nothing at cone[1] degrees.
    sx, sy = src[0] / np.hypot(*src), src[1] / np.hypot(*src)
    lx, ly, lz = sx * 0.8, sy * 0.8, 0.6
    ang = np.degrees(np.arccos(np.clip(ux * sx + uy * sy, -1, 1)))
    spot = np.clip((cone[1] - ang) / (cone[1] - cone[0]), 0, 1); spot = spot * spot * (3 - 2 * spot)
    spot = 0.18 + 0.82 * spot          # a little light still reaches the far side
    diff = np.clip(nx * lx + ny * ly + nz * lz, 0, 1) * spot
    hx, hy, hz = lx, ly, lz + 1; hn = np.sqrt(hx * hx + hy * hy + hz * hz)
    spec = (np.clip((nx * hx + ny * hy + nz * hz) / hn, 0, 1) ** 18) * spot
    base = np.array(BLUE, np.float32)
    lit = ((0.34 if night else 0.42) + 0.75 * diff ** 1.2)[..., None]
    blue = base[None, None, :] * np.minimum(lit, 1.0)
    g = np.array(hl, np.float32)[None, None, :]
    # how gold: only the most strongly lit part; 'gold' lowers the threshold
    dn = diff / max(float(diff.max()), 1e-3)
    thr = 0.97 - gold
    a = np.clip((np.maximum(dn, spec * 1.2) - thr) / 0.08, 0, 1); a = a * a * (3 - 2 * a)
    goldc = g * np.clip(0.55 + 0.6 * diff, 0, 1)[..., None]                # gold dims with the light, stays gold
    col = blue * (1 - a[..., None]) + goldc * a[..., None]
    if not night: col *= (1 - 0.45 * np.sin(np.pi * a))[..., None]        # gold: keep the in-between dark, never pale
    else: col *= (1 - 0.12 * np.sin(np.pi * a))[..., None]                 # white: blue->white is a clean ramp
    edge = np.clip(1 - np.minimum(t, 1 - t) * width / 0.8, 0, 1) * 0.55
    col = col * (1 - edge[..., None])
    out = np.zeros((H, W, 4), np.float32); out[..., :3] = np.clip(col, 0, 255); out[..., 3] = cover * 255
    # shadow cast away from the light, just outside the ring
    d_out = r - (r_in + width)
    away = np.clip(-(ux * src[0] + uy * src[1]) / np.hypot(*src), 0, 1)
    sh = np.where((d_out > -1) & (d_out < 7), (1 - np.clip(d_out, 0, 7) / 7) ** 2, 0) * (0.25 + 0.6 * away)
    so = np.zeros((H, W, 4), np.float32); so[..., 3] = sh * 220
    c.over(Image.fromarray(so.astype(np.uint8)))
    c.over(Image.fromarray(out.astype(np.uint8)))

def opt_cone(gold, width=11, night=False):
    c = base(False); cx, cy = CX - X0, CY - Y0
    W, H = c.im.size; X, Y = c.P(cx, cy); R = (RM + 1) * SS
    c.over(glow(W, H, (X, Y, X, Y), R + width * SS, u(10), BLUE, 0.4))
    ring_cone(c, cx, cy, RM - 2, width, gold, hl=(WHITE if night else GOLD), night=night)
    chevs(c, cx, cy, RM + 6 + width // 2, RM + 6 + width // 2)
    pill(c, (cx - 118, 6, cx + 118, 34), "Dustwallow Marsh", 15, GOLD, right="05:52")
    pill(c, (cx - 52, cy + RM + 16, cx + 52, cy + RM + 42), "62.5, 44.4", 15, WHITE)
    button(c, (cx + 84, cy - 86), MOON if night else SUN); button(c, (cx - 86, cy + 84), GEM)
    return c.done()

def ring_spot(c, cx, cy, r_in, width, gold=0.22, hl=GOLD, night=False,
              sun=(84, -86), tip=20, height=28, cone=(8, 78), reach=260):
    """Bevel ring lit by a cone of light whose tip sits just off the
    sun/moon's bottom-left edge (tip px from the icon's center, toward the
    map's center), shining down-left across the map. Only ring slopes that
    face the tip and fall inside the cone catch the light; the cone fades
    from full (cone[0] deg off its axis) to nothing (cone[1] deg)."""
    W, H = c.im.size; X, Y = c.P(cx, cy)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = (xx - X) / SS, (yy - Y) / SS; r = np.hypot(dx, dy)
    t = (r - r_in) / width
    cover = np.clip(np.minimum(t * width + 0.5, (1 - t) * width + 0.5), 0, 1)
    ux, uy = dx / np.maximum(r, 1e-3), dy / np.maximum(r, 1e-3)
    tc = np.clip(t, 0, 1)
    nr = np.where(tc < 0.5, -0.7, 0.7); nz = 0.72
    nx, ny = nr * ux, nr * uy
    sl = np.hypot(*sun); axx, axy = -sun[0] / sl, -sun[1] / sl          # axis: toward the map's center
    px, py = sun[0] + axx * tip, sun[1] + axy * tip                     # the cone's tip
    vx, vy, vz = dx - px, dy - py, -np.full_like(dx, height)            # tip -> point
    vl = np.sqrt(vx * vx + vy * vy + vz * vz)
    ang = np.degrees(np.arccos(np.clip((vx * axx + vy * axy) / np.maximum(np.hypot(vx, vy), 1e-3), -1, 1)))
    spot = np.clip((cone[1] - ang) / (cone[1] - cone[0]), 0, 1); spot = spot * spot * (3 - 2 * spot)
    spot = spot / (1 + (vl / reach) ** 2)
    lx, ly, lz = -vx / vl, -vy / vl, -vz / vl                           # point -> tip
    diff = np.clip(nx * lx + ny * ly + nz * lz, 0, 1) * spot
    hx, hy, hz = lx, ly, lz + 1; hn = np.sqrt(hx * hx + hy * hy + hz * hz)
    spec = (np.clip((nx * hx + ny * hy + nz * hz) / hn, 0, 1) ** 18) * spot * (cover > 0)
    base = np.array(BLUE, np.float32)
    diff = diff * (cover > 0)
    dmax = max(float(diff.max()), 1e-3)          # brightest point ON THE RING
    lit = ((0.34 if night else 0.42) + 0.9 * diff / dmax * 0.85)[..., None]
    blue = base[None, None, :] * np.minimum(lit, 1.0)
    dn = diff / dmax
    thr = 0.97 - gold
    a = np.clip((np.maximum(dn, spec * 1.2) - thr) / 0.08, 0, 1); a = a * a * (3 - 2 * a)
    g = np.array(hl, np.float32)[None, None, :]
    goldc = g * np.clip(0.55 + 0.45 * dn, 0, 1)[..., None]
    col = blue * (1 - a[..., None]) + goldc * a[..., None]
    col *= (1 - (0.12 if night else 0.45) * np.sin(np.pi * a))[..., None]
    edge = np.clip(1 - np.minimum(t, 1 - t) * width / 0.8, 0, 1) * 0.55
    col = col * (1 - edge[..., None])
    out = np.zeros((H, W, 4), np.float32); out[..., :3] = np.clip(col, 0, 255); out[..., 3] = cover * 255
    # shadow: the ring's lit inner slope throws a little shade outward, away from the tip
    d_out = r - (r_in + width)
    sh = np.where((d_out > -1) & (d_out < 7), (1 - np.clip(d_out, 0, 7) / 7) ** 2, 0) * (0.25 + 0.5 * np.clip(spot / max(float(spot.max()), 1e-3), 0, 1))
    so = np.zeros((H, W, 4), np.float32); so[..., 3] = sh * 220
    c.over(Image.fromarray(so.astype(np.uint8)))
    c.over(Image.fromarray(out.astype(np.uint8)))
    return (px, py)

def opt_spot(gold=0.22, night=False, width=11, show_tip=False, **kw):
    c = base(False); cx, cy = CX - X0, CY - Y0
    W, H = c.im.size; X, Y = c.P(cx, cy); R = (RM + 1) * SS
    c.over(glow(W, H, (X, Y, X, Y), R + width * SS, u(10), BLUE, 0.4))
    tipxy = ring_spot(c, cx, cy, RM - 2, width, gold, hl=(WHITE if night else GOLD), night=night, **kw)
    chevs(c, cx, cy, RM + 6 + width // 2, RM + 6 + width // 2)
    pill(c, (cx - 118, 6, cx + 118, 34), "Dustwallow Marsh", 15, GOLD, right="05:52")
    pill(c, (cx - 52, cy + RM + 16, cx + 52, cy + RM + 42), "62.5, 44.4", 15, WHITE)
    button(c, (cx + 84, cy - 86), MOON if night else SUN); button(c, (cx - 86, cy + 84), GEM)
    if show_tip:   # guide only: where the cone starts and its edges
        Lr, d = c.layer(); px, py = cx + tipxy[0], cy + tipxy[1]
        import math
        for deg in (-kw.get('cone', (8, 78))[1], 0, kw.get('cone', (8, 78))[1]):
            a0 = math.atan2(86, -84) + math.radians(deg)
            d.line(c.P(px, py, px + 230 * math.cos(a0), py + 230 * math.sin(a0)), fill=(255, 255, 255, 90 if deg else 140), width=SS)
        d.ellipse(c.P(px - 3, py - 3, px + 3, py + 3), fill=(255, 255, 255, 230)); c.over(Lr)
    return c.done()

def ring_ref(c, cx, cy, r_in, width, hl=GOLD, night=False, sun=(84, -86), spread=48, pool=0.0, glint=True, border_blue=False, navy=False, edges=False,
             gain=1.0, peak=1.0, halo_amt=0.55):
    """Lit like the user's reference image: light from beyond the sun/moon
    (top-right). Gold glows on the INNER wall across from it, with a long,
    soft fade back to blue through a light warm cream (no gray, no hard
    edge). A small glint on the outer edge nearest the light. pool = warm
    light spilling onto the map next to the lit wall (0 = none)."""
    W, H = c.im.size; X, Y = c.P(cx, cy)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = (xx - X) / SS, (yy - Y) / SS; r = np.hypot(dx, dy)
    t = (r - r_in) / width
    cover = np.clip(np.minimum(t * width + 0.5, (1 - t) * width + 0.5), 0, 1)
    ux, uy = dx / np.maximum(r, 1e-3), dy / np.maximum(r, 1e-3)
    sl = np.hypot(*sun); sx, sy = sun[0] / sl, sun[1] / sl
    tc = np.clip(t, 0, 1)
    # base blue bevel: ridge, gently lit from the sun's side
    nr = np.where(tc < 0.5, -0.7, 0.7)                 # the two slopes of the ridge
    L = np.array([sx * 0.8, sy * 0.8, 0.6]); L /= np.linalg.norm(L)
    diff = np.clip(nr * ux * L[0] + nr * uy * L[1] + 0.72 * L[2], 0, 1)
    crest = np.exp(-((tc - 0.5) / 0.07) ** 2)           # a fine bright line along the ridge top
    if navy:
        # header navy (#13284A): the lit slope a lighter navy, the shaded slope deeper
        face = 0.75 + 0.95 * diff ** 1.1 + 0.55 * crest
    elif border_blue:
        # keep the ring's overall color at the window-border blue (#4DA6FF):
        # the shaded slope a little darker, the lit slope a little lighter
        face = 0.86 + 0.42 * diff ** 1.1 + 0.16 * crest
    else:
        face = (0.30 + 0.95 * diff ** 1.3) + 0.25 * crest   # strong light/dark split between the slopes
    base = np.array(NAVY if navy else BLUE, np.float32)
    col = base[None, None, :] * np.minimum(face, 2.2 if navy else 1.15)[..., None]
    # inner-wall glow: centered straight across from the light, long soft fade
    opp = np.degrees(np.arccos(np.clip(-(ux * sx + uy * sy), -1, 1)))     # 0 = directly across from the sun
    along = np.exp(-(opp / spread) ** 2)
    # only the INNER slope faces the light; the gold stops at the crest. The
    # outer slope on this side faces away from the light and stays shaded blue.
    across = np.clip((0.5 - tc) / 0.06, 0, 1)
    I = np.clip(along * across * 1.15 * gain, 0, 1)[..., None]
    g = np.array(hl, np.float32)[None, None, :]
    cream = (np.array((255, 236, 196), np.float32) if not night else np.array((236, 244, 255), np.float32))[None, None, :]
    # blue -> cream -> gold: the middle of the fade is light and warm, like the reference
    m1 = np.clip(I / 0.5, 0, 1); m2 = np.clip((I - 0.5) / 0.5, 0, 1) * peak
    warm = col * (1 - m1) + cream * m1
    warm = warm * (1 - m2) + g * m2
    w = np.clip(I * 1.6, 0, 1) ** 1.2
    fshade = (face - 0.75) / 1.5 + 0.5 if navy else face
    warm = warm * np.clip(0.62 + 0.45 * fshade, 0, 1.08)[..., None]   # the gold keeps the bevel's light and shade
    col = col * (1 - w) + warm * w
    # glint: a small hot spot on the outer edge nearest the light
    if glint:
        near = np.degrees(np.arccos(np.clip(ux * sx + uy * sy, -1, 1)))
        gl = np.exp(-(near / 16) ** 2) * np.clip((tc - 0.55) / 0.3, 0, 1) * np.clip((1 - tc) / 0.25, 0, 1)
        col = col * (1 - gl[..., None] * 0.85) + (g * 0.6 + cream * 0.4) * gl[..., None] * 0.85
    edge = np.clip(1 - np.minimum(t, 1 - t) * width / 0.8, 0, 1) * (0.22 if border_blue else 0.5)
    col = col * (1 - edge[..., None])
    # warm light around the lit wall: a soft halo inside the ring (and a pool on the map if asked)
    d_in = r_in - r
    halo = np.where(d_in > -1, np.exp(-np.clip(d_in, 0, None) / 9), 0) * along * halo_amt
    if pool: halo = halo + np.where(d_in > 0, np.exp(-d_in / 45), 0) * along * pool
    hl_img = np.zeros((H, W, 4), np.float32); hl_img[..., :3] = hl; hl_img[..., 3] = np.clip(halo, 0, 1) * 200 * (cover < 1)
    c.over(Image.fromarray(hl_img.astype(np.uint8)))
    # soft shadow outside, away from the light
    d_out = r - (r_in + width); away = np.clip(-(ux * sx + uy * sy), 0, 1)
    sh = np.where((d_out > -1) & (d_out < 7), (1 - np.clip(d_out, 0, 7) / 7) ** 2, 0) * (0.2 + 0.6 * away)
    so = np.zeros((H, W, 4), np.float32); so[..., 3] = sh * 220
    c.over(Image.fromarray(so.astype(np.uint8)))
    if edges:
        ln = np.exp(-((r - r_in - 0.6) / 0.7) ** 2) + np.exp(-((r - r_in - width + 0.6) / 0.7) ** 2)
        ln = np.clip(ln, 0, 1)[..., None] * 0.9
        col = col * (1 - ln) + np.array(BLUE, np.float32)[None, None, :] * ln
    out = np.zeros((H, W, 4), np.float32); out[..., :3] = np.clip(col, 0, 255); out[..., 3] = cover * 255
    c.over(Image.fromarray(out.astype(np.uint8)))

def opt_ref(night=False, width=11, sun_icon=None, **kw):
    c = base(False); cx, cy = CX - X0, CY - Y0
    W, H = c.im.size; X, Y = c.P(cx, cy); R = (RM + 1) * SS
    c.over(glow(W, H, (X, Y, X, Y), R + width * SS, u(10), BLUE, 0.4))
    ring_ref(c, cx, cy, RM - 2, width, hl=(WHITE if night else GOLD), night=night, **kw)
    chevs(c, cx, cy, RM + 6 + width // 2, RM + 6 + width // 2)
    pill(c, (cx - 118, 6, cx + 118, 34), "Dustwallow Marsh", 15, GOLD, right="05:52")
    pill(c, (cx - 52, cy + RM + 16, cx + 52, cy + RM + 42), "62.5, 44.4", 15, WHITE)
    button(c, (cx + 84, cy - 86), MOON if night else (sun_icon or SUN)); button(c, (cx - 86, cy + 84), GEM)
    return c.done()

if __name__ == '__main__':
    opts = [("A  Short round rays", opt_ref(navy=True, sun_icon=SUNS['A'])),
            ("B  Thin pointed rays", opt_ref(navy=True, sun_icon=SUNS['B'])),
            ("C  Halo ring", opt_ref(navy=True, sun_icon=SUNS['C'])),
            ("Moon (for comparison)", opt_ref(navy=True, night=True))]
    tiles = [label(im, name, 20) for name, im in opts]
    for (name, im), k in zip(opts, "01234"): im.save('/tmp/sk/mm_%s.png' % k)
    W = sum(t.width for t in tiles); sheet = Image.new('RGB', (W, tiles[0].height)); x = 0
    for t in tiles: sheet.paste(t, (x, 0)); x += t.width
    sheet.save('/tmp/sk/mm_sheet.png'); print(sheet.size)
