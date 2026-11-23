# Rounded Aether window art: corner pieces (white with alpha, tinted in game).
# Each corner image is the TOP-LEFT corner; the game flips it for the others.
import numpy as np, struct, os
def write_tga(path, alpha):
    h, w = alpha.shape
    a = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8); rgba[..., 0:3] = 255; rgba[..., 3] = a
    rows = rgba[::-1]; bgra = rows[..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())
R, IN, G = 8.0, 3.0, 6.7          # corner radius, inner line inset, glow width (UI units)
PX, SS = 64, 8
def raster(box, fn):
    """box: size in units; fn(x, y) -> alpha in 0..1, x/y in units from the top-left."""
    n = PX * SS
    c = (np.arange(n) + 0.5) / n * box
    X, Y = np.meshgrid(c, c)
    a = fn(X, Y)
    return a.reshape(PX, SS, PX, SS).mean(axis=(1, 3))
def dist(X, Y, cx, cy): return np.hypot(X - cx, Y - cy)
ring = lambda r0, r1: (lambda X, Y: ((dist(X, Y, R, R) >= r0) & (dist(X, Y, R, R) <= r1)).astype(float))
art = {
    "win_round_fill":  raster(R, lambda X, Y: (dist(X, Y, R, R) <= R).astype(float)),
    "win_round_line":  raster(R, ring(R - 1, R)),
    "win_round_inner": raster(R, ring(R - IN - 1, R - IN)),
    "win_round_strip": raster(R, lambda X, Y: (dist(X, Y, R, R) <= R - IN - 1).astype(float)),
    # glow around the rounded corner: the box reaches G past the window's corner
    "win_rglow_c":     raster(G + R, lambda X, Y: np.where(dist(X, Y, G + R, G + R) > R,
                               np.clip(1 - (dist(X, Y, G + R, G + R) - R) / G, 0, 1) ** 2, 0)),
}
for addon in ["AetherHub", "AetherMeter", "AetherCoords", "AetherItemID", "AetherLedger", "AetherPack"]:
    for name, a in art.items():
        write_tga(f"/home/claude/brand/{addon}/Media/{name}.tga", a)
print("ok", {k: round(float(v.max()), 2) for k, v in art.items()})
