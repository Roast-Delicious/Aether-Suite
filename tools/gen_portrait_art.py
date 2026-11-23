# Art for 3D portraits (AetherFrames 1.9.0):
#  crest{S}_rim  - the crest's dark disc with a hole where the face shows (drawn
#                  over the 3D model, hiding its square corners)
#  portrait_glow - the backdrop glow: white, full in the middle (35% of the
#                  radius), centered a little above the middle, fading to 0 at
#                  the circle's edge. Tinted Aether blue over a navy disc.
import sys, numpy as np
from PIL import Image
import struct
def write_tga(path, alpha):          # same as gen_round_art.write_tga (importing that regenerates its art)
    h, w = alpha.shape
    a = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8); rgba[..., 0:3] = 255; rgba[..., 3] = a
    bgra = rgba[::-1][..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())
MEDIA = '/home/claude/brand/AetherFrames/Media/'
SS = 8
def grid(n):
    c = (np.arange(n * SS) + 0.5) / (n * SS)
    return np.meshgrid(c, c)            # 0..1, y down
def down(a, n): return a.reshape(n, SS, n, SS).mean(axis=(1, 3))
for S in (58, 80):
    inner = S - (14 if S > 60 else 10)
    rface = (inner - 2) / 2 - 0.25       # tuck the hole's edge under the gold ring
    dark = np.array(Image.open(MEDIA + 'crest%d_dark.tga' % S))[..., 3].astype(float) / 255
    n = dark.shape[0]
    X, Y = grid(n)
    d = np.hypot(X - 0.5, Y - 0.5) * S   # units from the center
    hole = down((d >= rface).astype(float), n)
    write_tga(MEDIA + 'crest%d_rim.tga' % S, dark * hole)
n = 128
X, Y = grid(n)
r = 0.5
d0 = np.hypot(X - 0.5, Y - 0.5)
t = np.clip(np.hypot(X - 0.5, Y - (0.5 - 0.18 * r)) / (r * 1.1), 0, 1)
t = np.clip((t - 0.35) / 0.65, 0, 1); t = t * t * (3 - 2 * t)
glow = down((1 - t) * (d0 <= r), n)
write_tga(MEDIA + 'portrait_glow.tga', glow)
print("ok")
