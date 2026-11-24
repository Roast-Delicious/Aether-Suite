# Bakes the 3D (bevel ridge) gold chevrons for every Aether addon, lit from
# the top-right like AetherSkins' minimap ring. One texture per direction
# (the light must stay put, so the gold is never rotated in game).
#   python3 gen_chev3d.py           all addons
#   python3 gen_chev3d.py --check   compare with AetherSkins' approved art
# Shape sources: win_chev_gold (windows, bars, XP bar, meter, minimap) and
# AetherFrames' chev58_up_gold / chev80_up_gold (unit frame crests).
import sys, os, struct
sys.path.insert(0, '/home/claude/mock')
import numpy as np
from PIL import Image
import skin_chevron3d as C3

BRAND = '/home/claude/brand/'
DIRS = (('up', 0), ('right', -90), ('down', 180), ('left', 90))   # PIL rotate: + = counter-clockwise

def write_rgba_tga(path, im):
    a = np.array(im.convert('RGBA'))
    h, w = a.shape[:2]
    bgra = a[::-1][..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())

def bake(src, size=128):
    """{dir: RGBA image} from a white+alpha chevron pointing up (src path)."""
    old = C3.SRC; C3.SRC = os.path.dirname(src) + '/'
    name = os.path.basename(src)[:-4]
    try:
        shape0 = C3.shape
        def shape(n=512):
            import cv2
            a = Image.open(src).split()[3].resize((n, n), Image.BICUBIC)
            a = cv2.GaussianBlur(np.array(a).astype(np.float32), (0, 0), n / 160)
            m = (a > 120).astype(np.uint8)
            alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), n / 400)
            return m, alpha
        C3.shape = shape
        out = {}
        for d, rot in DIRS:
            im = C3.chevron3d('bevel', rot)
            if rot: im = im.rotate(rot, resample=Image.BICUBIC)
            out[d] = im.resize((size, size), Image.LANCZOS)
        return out
    finally:
        C3.shape = shape0; C3.SRC = old

def bake_as_is(src, size=128):
    """One already-oriented chevron, lit from the top-right of the screen."""
    import cv2
    shape0 = C3.shape
    def shape(n=512):
        a = Image.open(src).split()[3].resize((n, n), Image.BICUBIC)
        a = cv2.GaussianBlur(np.array(a).astype(np.float32), (0, 0), n / 160)
        m = (a > 120).astype(np.uint8)
        return m, cv2.GaussianBlur(m.astype(np.float32), (0, 0), n / 400)
    C3.shape = shape
    try:
        return C3.chevron3d('bevel', 0).resize((size, size), Image.LANCZOS)
    finally:
        C3.shape = shape0

WINDOW_ADDONS = ['AetherBars', 'AetherCoords', 'AetherFrames', 'AetherHub', 'AetherItemID',
                 'AetherLedger', 'AetherMeter', 'AetherPack', 'AetherSkins']

if __name__ == '__main__':
    win = bake(BRAND + 'AetherHub/Media/win_chev_gold.tga')
    if '--check' in sys.argv:
        for d, _ in DIRS:
            a = np.array(win[d]).astype(int); b = np.array(Image.open(BRAND + 'AetherSkins/Media/chev3d_%s.tga' % d).convert('RGBA')).astype(int)
            print(d, 'max diff', np.abs(a - b).max(), 'mean', round(np.abs(a - b).mean(), 3))
        sys.exit()
    for addon in WINDOW_ADDONS:
        for d, _ in DIRS:
            write_rgba_tga(BRAND + addon + '/Media/chev3d_%s.tga' % d, win[d])
    # Unit frame crests: each direction has its own flat art (pixel-placed),
    # so bake each one as drawn, with the light already in screen space.
    for S in (58, 80):
        for d, _ in DIRS:
            art = bake_as_is(BRAND + 'AetherFrames/Media/chev%d_%s_gold.tga' % (S, d), 128)
            write_rgba_tga(BRAND + 'AetherFrames/Media/chev%d_%s_gold3d.tga' % (S, d), art)
    print('baked')
