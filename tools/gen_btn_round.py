# Rounded buttons, Release C (user 15:36: "apply the Hub mockup button shape
# across the board" = soft corners, choice C of 05:31): corner pieces for a
# radius of 5 UI units (buttons, tabs, boxes) and 3 (checkboxes). White with
# alpha, drawn as the top-left corner (flipped for the others), like
# win_round_*. Run from tools/.
import numpy as np, struct
def write_tga(path, alpha):        # same writer as gen_round_art.py
    h, w = alpha.shape
    a = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8); rgba[..., 0:3] = 255; rgba[..., 3] = a
    rows = rgba[::-1]; bgra = rows[..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())
PX, SS = 64, 8
def raster(box, fn):
    n = PX * SS
    c = (np.arange(n) + 0.5) / n * box
    X, Y = np.meshgrid(c, c)
    return fn(X, Y).reshape(PX, SS, PX, SS).mean(axis=(1, 3))
art = {}
for R in (5, 4, 3):   # 4: the inner gold ring of an open side tab (user 16:49)
    d = lambda X, Y, R=R: np.hypot(X - R, Y - R)
    art[f"btn_round{R}_fill"] = raster(R, lambda X, Y, R=R: (d(X, Y) <= R).astype(float))
    art[f"btn_round{R}_line"] = raster(R, lambda X, Y, R=R: ((d(X, Y) >= R - 1) & (d(X, Y) <= R)).astype(float))
for addon in ["AetherHub", "AetherSkins"]:
    for name, a in art.items():
        write_tga(f"/home/claude/brand/{addon}/Media/{name}.tga", a)
print("ok", sorted(art))
