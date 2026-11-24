# The chalk lettering for AetherPack's deposit slot (chosen 2026-11-23):
# "NO SWAPS. JUST DROPS." in Amatic SC Bold, tilted 8 degrees, and a hand-drawn
# arrow curving back into the slot, both with a chalk texture (streaks that run
# along each stroke, ragged edges, a little dust). White with alpha: the addon
# tints it the Aether gold.
#   dep_ink.tga: 1024 x 256 px = 256 x 64 UI units. The slot (37 units) has its
#   top-left at (0, 12) units on this canvas.
# Usage: python3 gen_deposit_ink.py <AetherPack/Media dir> <AmaticSC-Bold .ttf>
import sys, struct
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

OUT, FONT = sys.argv[1], sys.argv[2]
UNITS_W, UNITS_H = 256, 64
PXU = 52 / 37            # drawn at the mockup's scale (px per UI unit), as approved
S = 4                    # supersampling
CW, CH = int(UNITS_W * PXU), int(UNITS_H * PXU)
SLOT = 52                # the slot, px at that scale
OX, OY = 0, 12 * PXU     # the slot's top-left on the canvas, px
TILT = 8

def write_tga(path, alpha):
    a = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    h, w = a.shape
    rgba = np.zeros((h, w, 4), np.uint8); rgba[..., 0:3] = 255; rgba[..., 3] = a
    rows = rgba[::-1]; bgra = rows[..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())

mask = Image.new('L', (CW * S, CH * S), 0)
d = ImageDraw.Draw(mask)

# the slogan, tilted, placed as in the approved mockup (right of the slot, a bit above it)
f = ImageFont.truetype(FONT, int(30 * S))
text = "NO SWAPS. JUST DROPS."
bb = d.textbbox((0, 0), text, font=f)
w, h = bb[2] - bb[0] + 8 * S, bb[3] - bb[1] + 8 * S
lab = Image.new('L', (w, h), 0)
ImageDraw.Draw(lab).text((w / 2, h / 2), text, font=f, fill=255, anchor='mm', stroke_width=int(0.35 * S), stroke_fill=255)
lab = lab.rotate(TILT, resample=Image.BICUBIC, expand=True)
mask.paste(255, (int((OX + SLOT + 69) * S), int((OY - 14) * S)), lab)

# the arrow: a quick marker-like curve from the slogan back into the slot
def stroke(pts, w0, w1, wmid=None):
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / max(1, n - 1)
        if wmid is None: ww = w0 + (w1 - w0) * t
        else: ww = (w0 + (wmid - w0) * min(1, t / 0.35)) * (1 - max(0, t - 0.75) / 0.25 * (1 - w1 / wmid))
        r = ww * S / 2
        d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], fill=255)
def P(x, y): return np.array([OX + x, OY + y])
t = np.linspace(0, 1, 60)[:, None]
p0, p1, p2, p3 = P(SLOT + 70, 36), P(SLOT + 50, 52), P(SLOT + 26, 46), P(SLOT + 6, 30)
pts = ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
rng = np.random.default_rng(5)
tang = np.gradient(pts, axis=0); tang /= np.linalg.norm(tang, axis=1)[:, None] + 1e-9
nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
pts = pts + nrm * np.convolve(rng.normal(0, 0.55, len(pts)), np.ones(9) / 9, mode='same')[:, None]
sc = 1.4
stroke(pts, 0.9 * sc, 1.9 * sc, 2.3 * sc)
tip = pts[-1]; dv = pts[-1] - pts[-6]; dv /= np.linalg.norm(dv)
for side, ang, ln in ((1, 0.62, 7.0), (-1, 0.55, 6.2)):
    ca, sa = np.cos(side * ang), np.sin(side * ang)
    back = -np.array([dv[0] * ca - dv[1] * sa, dv[0] * sa + dv[1] * ca])
    seg = np.array([tip + back * ln * sc * u for u in np.linspace(0, 1, 18)])
    stroke(seg, 2.1 * sc, 1.1 * sc)

# chalk
m = np.array(mask).astype(np.float32) / 255
H, W = m.shape
rng = np.random.default_rng(11)
soft = cv2.GaussianBlur(m, (0, 0), 1.6 * S)
gx = cv2.Sobel(soft, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(soft, cv2.CV_32F, 0, 1, ksize=3)
jxx = cv2.GaussianBlur(gx * gx, (0, 0), 2.0 * S); jyy = cv2.GaussianBlur(gy * gy, (0, 0), 2.0 * S); jxy = cv2.GaussianBlur(gx * gy, (0, 0), 2.0 * S)
theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy)
dx, dy = -np.sin(theta), np.cos(theta)
cell = max(1, int(0.55 * S))
nz = rng.random((H // cell + 1, W // cell + 1)).astype(np.float32)
nz = cv2.resize(nz, (W, H), interpolation=cv2.INTER_NEAREST)
ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
acc = nz.copy(); cnt = 1.0
L = int(6 * S); step = max(1.0, S * 0.7)
for sign in (1, -1):
    px, py = xs.copy(), ys.copy()
    for _ in range(int(L / step)):
        px += sign * step * cv2.remap(dx, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        py += sign * step * cv2.remap(dy, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        acc += cv2.remap(nz, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE); cnt += 1
streak = acc / cnt
streak = (streak - streak.mean()) / (streak.std() + 1e-6)
edge = cv2.GaussianBlur(m, (0, 0), 0.8 * S)
body = np.clip((edge + streak * 0.16 - 0.5) * 5, 0, 1)
near = cv2.dilate((m > 0.05).astype(np.uint8), np.ones((int(1.4 * S) | 1, int(1.4 * S) | 1), np.uint8)).astype(np.float32)
body *= near
fill = np.clip(0.78 + streak * 0.30, 0.15, 1)
out = body * fill
dust = cv2.GaussianBlur(m, (0, 0), 2.4 * S) * 0.08 * cv2.GaussianBlur(near, (0, 0), 2.0 * S)
out = np.maximum(out, dust * np.clip(0.6 + 0.6 * streak, 0, 1.5))

img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).resize((UNITS_W * 4, UNITS_H * 4), Image.LANCZOS)
write_tga(OUT + '/dep_ink.tga', np.array(img).astype(np.float32) / 255)
print("dep_ink.tga", img.size, "= 256 x 64 units; slot top-left at (0, 12) units")
