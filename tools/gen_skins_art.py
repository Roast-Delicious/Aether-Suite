# Bakes AetherSkins' minimap art from the approved mockup code
# (mock/skin_minimap.py ring_ref, _sun('B'), _moon()), so the game shows
# exactly what was approved.
#   ring_plain.tga  navy bevel ring, no light (shown while day <-> night changes)
#   ring_day.tga    same as ring_plain (no light, user Nov 24 16:11)
#   ring_night.tga  same as ring_plain
#   btn_disc.tga    navy button with a blue rim (sun/moon, AetherHub)
#   ico_sun.tga     12-ray sun, white with alpha (tinted Aether gold in game)
#   ico_moon.tga    crescent, white with alpha (tinted pale in game)
#   ico_track.tga   flat magnifier (tracking button), white with alpha (tinted Aether Blue)
#   pill_cap.tga    half disc for the zone and coordinate pills (white)
#   pill_capline.tga half-ring outline for the pills (white)
# Ring textures span +-K map radii around the minimap's center (K below);
# the Lua uses the same K. TGA: bottom-left origin.
import sys, struct, math, os
sys.path.insert(0, '/home/claude/mock')
import numpy as np
from PIL import Image, ImageDraw
import skins_lib as SL
import skin_minimap as MM

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/brand/AetherSkins/Media'
os.makedirs(OUT, exist_ok=True)
RM = MM.RM                 # map radius in mockup px (117)
HALF = 150                 # canvas half-size in mockup px
K = HALF / RM              # texture half-size in map radii (~1.282)

def write_rgba(path, im):
    a = np.array(im.convert('RGBA'))
    h, w = a.shape[:2]
    bgra = a[::-1][..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())

def white_alpha(alpha_im):
    a = np.array(alpha_im.convert('L'))
    out = np.zeros(a.shape + (4,), np.uint8); out[..., :3] = 255; out[..., 3] = a
    return Image.fromarray(out)

def ring(kind, size=512):
    c = SL.Canvas(Image.new('RGBA', (2 * HALF, 2 * HALF), (0, 0, 0, 0)))
    W, H = c.im.size; X, Y = c.P(HALF, HALF); R = (RM + 1) * SL.SS; width = 11
    c.over(SL.glow(W, H, (X, Y, X, Y), R + width * SL.SS, SL.u(10), SL.BLUE, 0.4))
    # User, Nov 24 16:11: the whole ring plain navy, no light source. Day and
    # night get the plain ring too, so the Lua's day/night swap changes nothing.
    if kind in ('plain', 'day', 'night'):
        MM.ring_ref(c, HALF, HALF, RM - 2, width, navy=True, spread=1e-4, glint=False)
    else:
        night = kind == 'night'
        # day: ring light B (user, Nov 24): the same glow, lighter, a soft gold-cream
        light = {} if night else dict(gain=0.85, peak=0.3, halo_amt=0.2)
        MM.ring_ref(c, HALF, HALF, RM - 2, width, hl=(SL.WHITE if night else SL.GOLD), night=night, navy=True, **light)
    return c.im.resize((size, size), Image.LANCZOS)

def disc(size=64):
    S = 8; n = size * S; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rim = int(n * 0.034) + 1          # about 1 UI unit on a ~22-unit button
    d.ellipse([0, 0, n - 1, n - 1], fill=SL.BLUE + (255,))
    d.ellipse([rim, rim, n - 1 - rim, n - 1 - rim], fill=SL.NAVY + (255,))
    return im.resize((size, size), Image.LANCZOS)

def sun(size=128):
    N = 176 * 4; im = Image.new('L', (N, N), 0); d = ImageDraw.Draw(im); c0 = N / 2; s = 4
    d.ellipse([c0 - 36 * s, c0 - 36 * s, c0 + 36 * s, c0 + 36 * s], fill=255)
    for k in range(12):
        a = math.radians(k * 30); w = math.radians(7)
        d.polygon([(c0 + 48 * s * math.cos(a - w), c0 + 48 * s * math.sin(a - w)),
                   (c0 + 82 * s * math.cos(a), c0 + 82 * s * math.sin(a)),
                   (c0 + 48 * s * math.cos(a + w), c0 + 48 * s * math.sin(a + w))], fill=255)
    return white_alpha(im.resize((size, size), Image.LANCZOS))

def moon(size=128):
    N = 176 * 4; im = Image.new('L', (N, N), 0); d = ImageDraw.Draw(im); s = 4
    d.ellipse([28 * s, 28 * s, 148 * s, 148 * s], fill=255); d.ellipse([60 * s, 14 * s, 176 * s, 130 * s], fill=0)
    return white_alpha(im.resize((size, size), Image.LANCZOS))

def magnifier(size=128, ring_w=17, lens=38, handle_w=21, cx=72, cy=72, reach=56):
    """Flat magnifier like the sun and moon: a bold lens ring and a handle to
    the bottom-right (mock/skin_magnifier.py, the approved proportions)."""
    N = 176 * 4; s = 4; im = Image.new('L', (N, N), 0); d = ImageDraw.Draw(im)
    X, Y = cx * s, cy * s; r = lens * s; hw0 = ring_w * s / 2
    d.ellipse([X - r - hw0, Y - r - hw0, X + r + hw0, Y + r + hw0], fill=255)
    d.ellipse([X - r + hw0, Y - r + hw0, X + r - hw0, Y + r - hw0], fill=0)
    a = math.radians(45)
    x0, y0 = X + (r + hw0) * math.cos(a), Y + (r + hw0) * math.sin(a)
    x1, y1 = X + (r + reach * s) * math.cos(a), Y + (r + reach * s) * math.sin(a)
    d.line([x0, y0, x1, y1], fill=255, width=int(handle_w * s)); hw = handle_w * s / 2
    d.ellipse([x1 - hw, y1 - hw, x1 + hw, y1 + hw], fill=255)
    return white_alpha(im.resize((size, size), Image.LANCZOS))

def pill_cap(size=64, line=False):
    """Left half of a pill: a half disc (or its 1-unit outline), right edge flat."""
    S = 8; n = size * S; im = Image.new('L', (n // 2, n), 0); d = ImageDraw.Draw(im)
    if line:
        lw = int(n / 20) + 1          # ~1 UI unit on a 20-unit-tall pill
        d.ellipse([0, 0, n - 1, n - 1], fill=255); d.ellipse([lw, lw, n - 1 - lw, n - 1 - lw], fill=0)
    else:
        d.ellipse([0, 0, n - 1, n - 1], fill=255)
    return white_alpha(im.resize((size // 2, size), Image.LANCZOS))

if __name__ == '__main__':
    for k in ('plain', 'day', 'night'): write_rgba(f'{OUT}/ring_{k}.tga', ring(k))
    write_rgba(f'{OUT}/btn_disc.tga', disc())
    write_rgba(f'{OUT}/ico_sun.tga', sun()); write_rgba(f'{OUT}/ico_moon.tga', moon())
    write_rgba(f'{OUT}/ico_track.tga', magnifier())
    write_rgba(f'{OUT}/pill_cap.tga', pill_cap()); write_rgba(f'{OUT}/pill_capline.tga', pill_cap(line=True))
    print('K =', round(K, 4), 'written to', OUT)
