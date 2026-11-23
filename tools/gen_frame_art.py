# Generates AetherFrames' anti-aliased art (white shapes with alpha, tinted in
# game). Geometry mirrors AetherFrames.lua's Build() exactly; keep in sync.
import numpy as np, os, math, struct, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/brand/AetherFrames/Media'
os.makedirs(OUT, exist_ok=True)
SCALE, SS = 2, 4          # canvas px per UI unit (before POT), supersamples per axis

def pot(n):
    p = 8
    while p < n: p *= 2
    return p

def write_tga(path, alpha):
    h, w = alpha.shape
    a = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 0:3] = 255
    rgba[..., 3] = a
    rows = rgba[::-1]                         # bottom-left origin
    bgra = rows[..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh:
        fh.write(hdr); fh.write(bgra.tobytes())

def render(name, x0, y0, w, h, pred, mirror=False):
    """Rasterize pred(x, y) over the rect [x0, x0+w] x [y0, y0+h] (UI units,
    y down) onto a power-of-two canvas that is stretched back onto the rect."""
    W, H = pot(math.ceil(w * SCALE)), pot(math.ceil(h * SCALE))
    off = (np.arange(SS) + 0.5) / SS
    xs = (np.arange(W)[:, None] + off[None, :]).ravel() / W * w + x0
    ys = (np.arange(H)[:, None] + off[None, :]).ravel() / H * h + y0
    X, Y = np.meshgrid(xs, ys)
    m = pred(X, Y).astype(np.float32)
    m = m.reshape(H, SS, W, SS).mean(axis=(1, 3))
    if mirror: m = m[:, ::-1]
    write_tga(os.path.join(OUT, name + '.tga'), m)
    return W, H

def circle_x(cx, r, dy):
    return cx + math.sqrt(r * r - dy * dy) if abs(dy) < r else cx

# Frame specs (same numbers as AetherFrames.lua)
SPECS = {
    'player': dict(S=80, capW=40 + 184, padTop=3, nameH=16, padBottom=4, bars=[(13, 3), (13, 3)]),
    'pet4':   dict(S=58, capW=29 + 151, padTop=2, nameH=14, padBottom=3, bars=[(12, 3), (4, 2)]),
    'pet12':  dict(S=58, capW=29 + 151, padTop=2, nameH=14, padBottom=3, bars=[(12, 3), (12, 2)]),
}

def geometry(sp):
    S = sp['S']; R = S / 2
    capH = sp['padTop'] + sp['nameH'] + sum(g + h for h, g in sp['bars']) + sp['padBottom']
    fh = max(S, capH) + 12
    cx, cy = R + 6, fh / 2
    capTop = (fh - capH) / 2
    rr = capH / 2
    xc = cx + sp['capW'] - rr
    return dict(S=S, R=R, capH=capH, fh=fh, cx=cx, cy=cy, capTop=capTop, rr=rr, xc=xc, gapR=R + 3)

manifest = []
def crest(S):
    R = S / 2
    inner = S - (14 if S > 60 else 10)
    c = S / 2
    d = lambda X, Y: np.hypot(X - c, Y - c)
    render('crest%d_blue' % S, 0, 0, S, S, lambda X, Y: (d(X, Y) <= R) & (d(X, Y) >= R - 2))
    render('crest%d_dark' % S, 0, 0, S, S, lambda X, Y: d(X, Y) <= R - 1.25)
    ci = inner / 2
    di = lambda X, Y: np.hypot(X - ci, Y - ci)
    render('crest%d_gold' % S, 0, 0, inner, inner, lambda X, Y: (di(X, Y) <= ci) & (di(X, Y) >= ci - 1))
    # threat halo: soft glow from the ring outward (smooth falloff)
    # a wide glow (16 units past the ring), bright at the ring and fading slowly
    HS = S + 34; hc = HS / 2
    def halo(X, Y):
        r = np.hypot(X - hc, Y - hc)
        t = np.clip((r - (R - 1)) / 16.0, 0, 1)
        a = np.where(r < R - 1, 0.0, (1 - t) ** 1.4)
        return a
    render('halo%d' % S, 0, 0, HS, HS, halo)

def capsule(key, sp, mirror_masks):
    G = geometry(sp)
    cx, cy, R, rr, xc, capTop, capH = G['cx'], G['cy'], G['R'], G['rr'], G['xc'], G['capTop'], G['capH']
    x0, w = cx, sp['capW']
    def in_cap(X, Y):
        inside_y = (Y >= capTop) & (Y <= capTop + capH)
        end = (X <= xc) | (np.hypot(X - xc, Y - cy) <= rr)
        return inside_y & end & (np.hypot(X - cx, Y - cy) >= R) & (X >= cx)
    render('cap_%s_fill' % key, x0, capTop, w, capH, in_cap)
    def edge(X, Y):
        band = (Y < capTop + 1) | (Y > capTop + capH - 1) | ((X > xc) & (np.hypot(X - xc, Y - cy) > rr - 1))
        return in_cap(X, Y) & band
    render('cap_%s_edge' % key, x0, capTop, w, capH, edge)
    # bars
    y = capTop + sp['padTop'] + sp['nameH']
    gapR = G['gapR']
    for i, (h, gap) in enumerate(sp['bars'], 1):
        y += gap
        y0 = y
        def shape(X, Y, y0=y0, h=h):
            return ((Y >= y0) & (Y <= y0 + h) & (X >= cx) & (np.hypot(X - cx, Y - cy) >= gapR)
                    & ((X <= xc) | (np.hypot(X - xc, Y - cy) <= rr - 4)))
        def inner(X, Y, y0=y0, h=h):
            return ((Y >= y0 + 1) & (Y <= y0 + h - 1) & (X >= cx) & (np.hypot(X - cx, Y - cy) >= gapR + 1)
                    & ((X <= xc - 1) | (np.hypot(X - xc, Y - cy) <= rr - 5)))
        render('bar_%s_%d_bg' % (key, i), x0, y0, w, h, shape)
        render('bar_%s_%d_edge' % (key, i), x0, y0, w, h, lambda X, Y, s=shape, n=inner: s(X, Y) & ~n(X, Y))
        # the fill's own rect: the inner shape's left- and rightmost points
        P0 = min(circle_x(cx, gapR + 1, (y0 + 1) - cy), circle_x(cx, gapR + 1, (y0 + h - 1) - cy))
        lo, hi = (y0 + 1) - cy, (y0 + h - 1) - cy
        dmin = 0 if lo <= 0 <= hi else min(abs(lo), abs(hi))
        P1 = max(xc - 1, xc + math.sqrt(max(0, (rr - 5) ** 2 - dmin ** 2)) if dmin < rr - 5 else xc - 1)
        render('bar_%s_%d_mask' % (key, i), P0, y0 + 1, P1 - P0, h - 2, inner)
        if mirror_masks:
            render('bar_%s_%d_maskm' % (key, i), P0, y0 + 1, P1 - P0, h - 2, inner, mirror=True)
        manifest.append((key, i, round(P0, 3), round(P1, 3)))
        y += h

crest(80); crest(58)
capsule('player', SPECS['player'], True)
capsule('pet4', SPECS['pet4'], False)
capsule('pet12', SPECS['pet12'], False)
# Badges (level and pet happiness): a disc, a dark rim just outside it, and
# three faces drawn in the disc's 20-unit box.
D = 20
render('badge_disc', 0, 0, D, D, lambda X, Y: np.hypot(X - D / 2, Y - D / 2) <= D / 2)
RD = D + 3
render('badge_rim', 0, 0, RD, RD, lambda X, Y: np.hypot(X - RD / 2, Y - RD / 2) <= RD / 2)
def face(mouth):
    def f(X, Y):
        x, y = X - D / 2, Y - D / 2
        eyes = (np.hypot(x + 3.4, y + 2.6) <= 1.55) | (np.hypot(x - 3.4, y + 2.6) <= 1.55)
        return eyes | mouth(x, y)
    return f
T = 1.7
smile = lambda x, y: (np.abs(np.hypot(x, y + 0.6) - 5.4) <= T / 2) & (y > 1.2)
flat  = lambda x, y: (np.abs(y - 3.6) <= T / 2) & (np.abs(x) <= 3.8)
frown = lambda x, y: (np.abs(np.hypot(x, y - 8.6) - 5.0) <= T / 2) & (y < 5.2)
render('face_happy', 0, 0, D, D, face(smile))
render('face_neutral', 0, 0, D, D, face(flat))
render('face_sad', 0, 0, D, D, face(frown))
print("fill rects (key, bar, P0, P1):", manifest)
print("files:", len(os.listdir(OUT)), "bytes:", sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)))
