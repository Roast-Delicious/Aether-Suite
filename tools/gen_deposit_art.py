# Art for AetherPack's deposit slot ("No swaps. Just drops."), as chosen from the
# mockups on 2026-11-23. Everything is drawn here (no game art), white with alpha
# so the addon can tint it, except the dark well and the shadows.
#   dep_rim.tga      the slot's rim: 37 units, cut corners, lit top-left (tinted amber)
#   dep_well.tga     the dark well inside the rim (not tinted)
#   dep_glow.tga     soft glow inside the rim plus tapered rays fading toward the middle (tinted)
#   dep_dark.tga     darker middle, under the number (black)
#   dep_ink.tga      the hand-lettered slogan and the hook arrow (tinted)
#   dep_ink_sh.tga   their soft shadow (black)
#   dep_numglow.tga  soft glow behind the number (tinted)
# Usage: python3 gen_deposit_art.py <AetherPack/Media dir> <handwriting font .ttf>
import sys, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT, HAND = sys.argv[1], sys.argv[2]

def write_tga(path, rgba):
    """rgba: float array h x w x 4 in 0..1 (top row first)."""
    a = np.clip(np.round(rgba * 255), 0, 255).astype(np.uint8)
    h, w = a.shape[:2]
    rows = a[::-1]; bgra = rows[..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())

def white(alpha):
    o = np.ones(alpha.shape + (4,), np.float32); o[..., 3] = alpha; return o
def black(alpha):
    o = np.zeros(alpha.shape + (4,), np.float32); o[..., 3] = alpha; return o
def down(arr, ss):
    h, w = arr.shape[0] // ss, arr.shape[1] // ss
    return arr.reshape(h, ss, w, ss, *arr.shape[2:]).mean(axis=(1, 3))

# ---------- the slot: 37 units square, drawn at 128 px ----------
SLOT = 37.0
PX, SS = 128, 4
N = PX * SS
c = (np.arange(N) + 0.5) / N * SLOT
X, Y = np.meshgrid(c, c)                       # units from the slot's top-left
edge = np.minimum.reduce([X, SLOT - X, Y, SLOT - Y])
CUT = 2.0                                      # the cut corners, units along each edge
corner = np.minimum.reduce([X + Y, (SLOT - X) + Y, X + (SLOT - Y), (SLOT - X) + (SLOT - Y)])
inside_shape = corner >= CUT
RIM_W = 2.2                                    # rim width, units
rim = inside_shape & (edge < RIM_W) | (inside_shape & (corner < CUT + RIM_W * 1.4))
rim = rim & inside_shape
inner = inside_shape & ~rim
# rim shading: lit from the top-left, a bright outer line, darker bottom-right
light = np.clip(0.80 + 0.25 * (1 - (X + Y) / (2 * SLOT)) - 0.15 * ((X + Y) / (2 * SLOT)), 0, 1)
outer_line = edge < 0.6
gray = np.where(outer_line, np.minimum(1, light + 0.12), light)
rim_rgba = np.zeros((N, N, 4), np.float32)
rim_rgba[..., 0:3] = gray[..., None]; rim_rgba[..., 3] = rim.astype(np.float32)
write_tga(OUT + '/dep_rim.tga', down(rim_rgba, SS))

# the dark well (not tinted): near black, a touch lighter toward the rim
r_ = np.hypot(X - SLOT / 2, Y - SLOT / 2) / (SLOT / 2)
v = np.clip(8 + 14 * r_, 0, 24) / 255
well = np.zeros((N, N, 4), np.float32)
well[..., 0] = v; well[..., 1] = v; well[..., 2] = v * 1.1; well[..., 3] = (inside_shape).astype(np.float32) * 0.98
write_tga(OUT + '/dep_well.tga', down(well, SS))

# glow + rays (white, tinted amber by the addon)
IN = RIM_W                                     # the glow starts at the rim's inside edge
inside = inside_shape & (edge >= IN - 0.8)          # tucks under the rim's inner edge: no dark seam
U2PX = N / SLOT                                # supersampled px per unit
def blur(a, r_units):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.array(im.filter(ImageFilter.GaussianBlur(r_units * U2PX))).astype(np.float32) / 255
band = (~inside).astype(np.float32)
glow = np.where(inside, np.clip(1.35 * blur(band, 3.7), 0, 1), 0)
# rays: from the rim toward the middle, wide and bright at the rim, narrowing and
# fading out toward the center; random lengths (fixed seed: always the same pattern)
rays_im = Image.new('L', (N, N), 0); dr = ImageDraw.Draw(rays_im)
rng = np.random.default_rng(7)
cen = N / 2
for k in range(26):
    ang = k * 2 * np.pi / 26 + rng.uniform(-0.08, 0.08)
    r0 = N * rng.uniform(0.48, 0.70); r1 = N * rng.uniform(0.08, 0.22)
    w0 = rng.uniform(1.5, 2.3) * U2PX; w1 = 0.2 * U2PX
    strength = rng.uniform(0.55, 0.95)
    ca, sa = np.cos(ang), np.sin(ang); px_, py_ = -sa, ca
    SEG = 16
    for seg in range(SEG):
        t0, t1 = seg / SEG, (seg + 1) / SEG
        ra, rb = r0 + (r1 - r0) * t0, r0 + (r1 - r0) * t1
        wa, wb = (w0 + (w1 - w0) * t0) / 2, (w0 + (w1 - w0) * t1) / 2
        q = [(cen + ra * ca + wa * px_, cen + ra * sa + wa * py_), (cen + rb * ca + wb * px_, cen + rb * sa + wb * py_),
             (cen + rb * ca - wb * px_, cen + rb * sa - wb * py_), (cen + ra * ca - wa * px_, cen + ra * sa - wa * py_)]
        tm = (t0 + t1) / 2
        ease = min(1.0, tm / 0.38) ** 2.0
        a = strength * 0.8 * ease * (1 - tm) ** 1.3
        dr.polygon(q, fill=int(255 * a))
core = np.array(rays_im).astype(np.float32) / 255
soft = blur(core, 1.3)
rays = 1 - (1 - soft) ** 2
rays = 1 - (1 - rays) * (1 - 0.2 * core)
rays = np.where(inside, rays, 0)
glow_all = 1 - (1 - glow) * (1 - rays)          # rays under the glow, both the same color
write_tga(OUT + '/dep_glow.tga', down(white(glow_all), SS))

# darker middle
dark = np.where(inside, 0.8 * np.clip(1.08 - r_, 0, 1) ** 0.6, 0)
write_tga(OUT + '/dep_dark.tga', down(black(dark), SS))

# soft glow behind the number: 64 px, the addon sizes it to the number
n2 = 64 * SS
yy, xx = np.mgrid[0:n2, 0:n2]
u = (xx - n2 / 2) / (n2 / 2); w_ = (yy - n2 / 2) / (n2 / 2)
blob = np.clip(1 - np.sqrt(u ** 2 + w_ ** 2), 0, 1) ** 1.6
write_tga(OUT + '/dep_numglow.tga', down(white(blob), SS))

# ---------- the ink: slogan + hook arrow, on a 68 x 68 unit canvas (256 px) ----------
CAN = 68.0
IPX, ISS = 256, 4
M = IPX * ISS
K = M / CAN                                    # px per unit
SX, SY = 13.0, 23.0                            # the slot's top-left on this canvas (units)
cx = SX + SLOT / 2; ytop = SY - 18.1
ink = Image.new('L', (M, M), 0); di = ImageDraw.Draw(ink)
font = ImageFont.truetype(HAND, int(12.5 * K))
for i, line in enumerate(("No swaps.", "Just drops.")):
    di.text(((cx + (i * 2 - 1) * 0.72) * K, (ytop + i * 10.1) * K), line, font=font, fill=255, anchor='mm')
ink = ink.rotate(3, resample=Image.BICUBIC, center=(cx * K, (ytop + 5) * K))   # tilted a little, like a quick note
di = ImageDraw.Draw(ink)
def bez(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
sx1, sy0 = SX + SLOT, SY
P2U = 1 / 1.38                                 # the mockup was drawn in screen px at 1.38 px per unit
pts = bez(np.array([cx + 37 * P2U, ytop + 18 * P2U]), np.array([sx1 + 20 * P2U, ytop + 20 * P2U]),
          np.array([sx1 + 18 * P2U, sy0 + 20 * P2U]), np.array([sx1 - 7 * P2U, sy0 + 13 * P2U]))
rng = np.random.default_rng(3)
tang = np.gradient(pts, axis=0); tang /= np.linalg.norm(tang, axis=1)[:, None] + 1e-9
nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
pts = pts + nrm * np.convolve(rng.normal(0, 0.55 * P2U, len(pts)), np.ones(9) / 9, mode='same')[:, None]
def stroke(points, w0, w1, wmid=None):
    n_ = len(points)
    for i_, (x_, y_) in enumerate(points):
        t_ = i_ / max(1, n_ - 1)
        if wmid is None: w_ = w0 + (w1 - w0) * t_
        else: w_ = (w0 + (wmid - w0) * min(1, t_ / 0.35)) * (1 - max(0, t_ - 0.75) / 0.25 * (1 - w1 / wmid))
        r = w_ * K / 2
        di.ellipse([x_ * K - r, y_ * K - r, x_ * K + r, y_ * K + r], fill=255)
stroke(pts, 0.9, 1.9, 2.3)
tip = pts[-1]; dirv = pts[-1] - pts[-6]; dirv /= np.linalg.norm(dirv)
for side, ang, ln in ((1, 0.62, 7.0 * P2U), (-1, 0.55, 6.2 * P2U)):
    ca, sa = np.cos(side * ang), np.sin(side * ang)
    back = -np.array([dirv[0] * ca - dirv[1] * sa, dirv[0] * sa + dirv[1] * ca])
    seg = np.array([tip + back * ln * t_ for t_ in np.linspace(0, 1, 18)])
    seg = seg + np.stack([-back[1], back[0]])[None, :] * np.convolve(rng.normal(0, 0.35 * P2U, 18), np.ones(5) / 5, mode='same')[:, None]
    stroke(seg, 2.1, 1.1)
ink_a = np.array(ink).astype(np.float32) / 255
write_tga(OUT + '/dep_ink.tga', down(white(ink_a), ISS))
sh = np.array(ink.filter(ImageFilter.GaussianBlur(0.5 * K))).astype(np.float32) / 255 * 0.66
write_tga(OUT + '/dep_ink_sh.tga', down(black(sh), ISS))
print("slot art: 128 px for 37 units; ink: 256 px for 68 units; slot at", (SX, SY), "on the ink canvas")
