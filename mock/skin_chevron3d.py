# Mockup: the gold chevron accents in 3D, lit like the minimap ring (light
# from the sun/moon at the top-right). Shading only darkens Aether gold or
# lifts it toward the ring's warm cream at the very brightest spots, so no
# second yellow appears.
import sys; sys.path.insert(0, '/home/claude/mock')
import numpy as np, cv2, math
from PIL import Image
import skins_lib as SL, skin_minimap as MM

GOLD = np.array(SL.GOLD, np.float32); CREAM = np.array((255, 236, 196), np.float32)
SRC = '/home/claude/brand/AetherSkins/Media/'

def shape(n=512):
    a = Image.open(SRC + 'win_chev_gold.tga').split()[3].resize((n, n), Image.BICUBIC)
    a = cv2.GaussianBlur(np.array(a).astype(np.float32), (0, 0), n / 160)
    m = (a > 120).astype(np.uint8)
    alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), n / 400)
    return m, alpha

def chevron3d(style, rot=0, n=512, light=(0.62, -0.62)):
    """RGBA chevron, n px, pointing up before rot (degrees, CCW). light: x right, y down."""
    m, alpha = shape(n)
    d = cv2.distanceTransform(m, cv2.DIST_L2, 5).astype(np.float32)
    w = max(float(d.max()), 1)
    if style == 'bevel':      # sharp ridge down the middle of each arm
        hgt = d / w
    elif style == 'round':    # rounded, like a tube
        hgt = np.sqrt(np.clip(1 - (1 - d / w) ** 2, 0, 1))
    else:                     # 'chamfer': flat top with angled edges
        hgt = np.clip(d / (w * 0.45), 0, 1)
    hgt = cv2.GaussianBlur(hgt, (0, 0), n / 110)
    gy, gx = np.gradient(hgt * w * 0.9)
    nx, ny, nz = -gx, -gy, np.ones_like(gx)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz); nx, ny, nz = nx / ln, ny / ln, nz / ln
    # the light comes from the top-right, in the art's own frame before rotation
    a = math.radians(rot); lx0, ly0 = light
    lx = lx0 * math.cos(a) - ly0 * math.sin(a) * -1; ly = lx0 * math.sin(a) * -1 + ly0 * math.cos(a)
    L = np.array([lx, ly, 0.62]); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    H = L + np.array([0, 0, 1]); H /= np.linalg.norm(H)
    spec = np.clip(nx * H[0] + ny * H[1] + nz * H[2], 0, 1) ** 30
    k = (0.58 + 0.62 * diff)[..., None]
    col = GOLD[None, None, :] * np.minimum(k, 1.0)
    s = np.clip(spec * 0.9 + np.clip(k[..., 0] - 1.0, 0, 1) * 1.5, 0, 0.8)[..., None]
    col = col * (1 - s) + CREAM[None, None, :] * s
    out = np.zeros((n, n, 4), np.float32); out[..., :3] = col; out[..., 3] = alpha * 255
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    return im

def dark(n=512):
    a = Image.open(SRC + 'win_chev_dark.tga').split()[3].resize((n, n), Image.LANCZOS)
    out = np.zeros((n, n, 4), np.uint8); out[..., :3] = (10, 11, 14); out[..., 3] = np.array(a)
    return Image.fromarray(out)

def on_minimap(style):
    """The approved navy minimap (day) with these chevrons."""
    import skins_lib
    c = MM.base(False); cx, cy = MM.CX - MM.X0, MM.CY - MM.Y0
    W, H = c.im.size; X, Y = c.P(cx, cy); R = (MM.RM + 1) * SL.SS; width = 11
    c.over(SL.glow(W, H, (X, Y, X, Y), R + width * SL.SS, SL.u(10), SL.BLUE, 0.4))
    MM.ring_ref(c, cx, cy, MM.RM - 2, width, navy=True)
    r = MM.RM + 6 + width // 2
    for x, y, rot in ((cx, cy - r, 0), (cx, cy + r, 180), (cx + r, cy, -90), (cx - r, cy, 90)):
        k = SL.u(26)
        X, Y = c.P(x, y)
        g = chevron3d(style, rot) if style else None
        for img in ((dark(), g) if style else (dark(), None)):
            if img is None:   # flat gold, as now
                img = SL.tga('win_chev_gold', SL.GOLD, (512, 512))
            t = img.resize((k, k), Image.LANCZOS).rotate(rot, resample=Image.BICUBIC)
            c.im.alpha_composite(t, (X - k // 2, Y - k // 2))
    c.d = __import__('PIL.ImageDraw', fromlist=['x']).Draw(c.im)
    MM.pill(c, (cx - 118, 6, cx + 118, 34), "Booty Bay", 15, SL.GOLD, right="12:46")
    MM.pill(c, (cx - 52, cy + MM.RM + 34, cx + 52, cy + MM.RM + 60), "27.6, 76.9", 15, SL.WHITE)
    MM.button(c, (cx + 84, cy - 86), MM._sun('B'))
    return c.done()

if __name__ == '__main__':
    tiles = []
    for style, name in ((None, "Flat (now)"), ('bevel', "A  Bevel ridge"), ('round', "B  Rounded"), ('chamfer', "C  Chamfered")):
        im = on_minimap(style); im.save('/tmp/sk/chev_%s.png' % (style or 'flat'))
        tiles.append(SL.label(im, name, 20))
    W = sum(t.width for t in tiles); sh = Image.new('RGB', (W, tiles[0].height)); x = 0
    for t in tiles: sh.paste(t, (x, 0)); x += t.width
    sh.save('/tmp/sk/chev_sheet.png')
    # big close-ups of one chevron each, on navy
    big = []
    for style, name in (('bevel', "A"), ('round', "B"), ('chamfer', "C")):
        bg = Image.new('RGBA', (300, 300), SL.NAVY + (255,)); g = chevron3d(style, 0).resize((240, 240), Image.LANCZOS)
        bg.alpha_composite(dark().resize((240, 240), Image.LANCZOS), (30, 30)); bg.alpha_composite(g, (30, 30))
        big.append(SL.label(bg.convert('RGB'), name, 20))
    bg = Image.new('RGBA', (300, 300), SL.NAVY + (255,))
    bg.alpha_composite(dark().resize((240, 240), Image.LANCZOS), (30, 30))
    bg.alpha_composite(SL.tga('win_chev_gold', SL.GOLD, (240, 240)), (30, 30))
    big.insert(0, SL.label(bg.convert('RGB'), "Flat", 20))
    out = Image.new('RGB', (1200, big[0].height)); [out.paste(b, (i * 300, 0)) for i, b in enumerate(big)]
    out.save('/tmp/sk/chev_close.png'); print('ok')
