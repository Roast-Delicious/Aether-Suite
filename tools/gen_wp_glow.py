# Round, soft glow behind the Coords waypoint star (replaces the square
# action-button border art). White with alpha; tinted Aether gold in game.
# The texture spans GLOW_SCALE x the pin size; the pin's disc fills the
# middle, so the glow is brightest at the disc's edge and fades to nothing.
import sys, struct, numpy as np

def write_tga(path, alpha):     # white + alpha, bottom-left origin
    h, w = alpha.shape
    rgba = np.zeros((h, w, 4), np.uint8); rgba[..., 0:3] = 255
    rgba[..., 3] = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    bgra = rgba[::-1][..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())
GLOW_SCALE = 2.4            # must match AetherCoords.lua
N, SS = 64, 8
c = (np.arange(N * SS) + 0.5) / (N * SS) * 2 - 1
X, Y = np.meshgrid(c, c)
r = np.sqrt(X * X + Y * Y)
edge = 1 / GLOW_SCALE       # disc radius, in texture half-widths
t = np.clip((r - edge) / (1 - edge), 0, 1)
a = np.where(r < edge, 1.0, (1 - t) ** 2.2)   # soft falloff, zero at the rim
a = a.reshape(N, SS, N, SS).mean(axis=(1, 3))
write_tga(sys.argv[1] if len(sys.argv) > 1 else
          '/home/claude/brand/AetherCoords/Media/wp_glow.tga', a)
