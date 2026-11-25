# Bakes AetherSkins' second-pass art (Nov 25) from the approved mockups:
#   role_tank/healer/dps/leader.tga  role glyphs (mock/roles.py), white with
#                                    alpha, tinted Aether gold in game
#   disc_plain.tga                   filled circle, white (tinted navy)
#   ring_thin.tga                    thin ring, white (blue; gold when picked)
#   glow_sq.tga                      soft square glow, white (Aether blue,
#                                    the medium strength, mock/talent_glow.py)
#   arrow_head_{gold,blue,gray}.tga  3D arrowheads, bevel lit from the
#                                    top-right like the gold accents
#   arrow_shaft_{gold,blue,gray}.tga 3D shaft: the ridge runs across the
#                                    texture's height (a Line's thickness)
import sys, os, math, numpy as np, cv2
sys.path.insert(0, '/home/claude/aether-repo/mock'); sys.path.insert(0, '/home/claude/aether-repo/tools')
from PIL import Image, ImageDraw
from gen_skins_art import write_rgba, white_alpha
import roles
from talent_details import bevel

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/aether-repo/AetherSkins/Media'
GOLD = (255, 176, 0); BLUE = (77, 166, 255); GRAY = (130, 134, 144)

def glyph_tga(kind, size=128):
    S = 8; n = size * S
    im = Image.new('RGB', (n, n), (0, 0, 0)); d = ImageDraw.Draw(im)
    roles.glyph(d, kind, n / 2, n / 2, n * 0.40, (255, 255, 255))   # the shield's rib comes out dark
    a = Image.fromarray(np.array(im)[..., 0])                        # white = glyph
    return white_alpha(a.resize((size, size), Image.LANCZOS))

def disc(size=128):
    S = 8; n = size * S; im = Image.new('L', (n, n), 0)
    ImageDraw.Draw(im).ellipse([0, 0, n - 1, n - 1], fill=255)
    return white_alpha(im.resize((size, size), Image.LANCZOS))

def ring(size=128, w=0.07):
    S = 8; n = size * S; im = Image.new('L', (n, n), 0); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, n - 1, n - 1], fill=255); k = int(n * w)
    d.ellipse([k, k, n - 1 - k, n - 1 - k], fill=0)
    return white_alpha(im.resize((size, size), Image.LANCZOS))

def glow_sq(size=128):
    # the node is the middle 64 of 128; the glow falls off outside it
    m = np.zeros((size, size), np.float32)
    cv2.rectangle(m, (34, 34), (size - 35, size - 35), 1.0, -1)
    g = np.clip(cv2.GaussianBlur(m, (0, 0), 64 * 0.13) * 1.6, 0, 1)
    g[32:size - 32, 32:size - 32] = np.minimum(g[32:size - 32, 32:size - 32], 0)   # nothing under the icon
    return white_alpha(Image.fromarray((g * 255).astype(np.uint8)))

def head(col, size=64):
    S = 4; n = size * S
    m = Image.new('L', (n, n), 0)
    ImageDraw.Draw(m).polygon([(n * 0.06, n * 0.2), (n * 0.94, n * 0.2), (n / 2, n * 0.92)], fill=255)
    m = (np.array(m) > 127).astype(np.uint8)
    out = bevel(m, col)
    dark = cv2.dilate(m * 255, np.ones((3 * S, 3 * S), np.uint8)).astype(np.float32)
    o = np.zeros((n, n, 4), np.float32); o[..., :3] = (8, 10, 14); o[..., 3] = cv2.GaussianBlur(dark, (0, 0), S) * 0.85
    a = o.copy(); fa = out[..., 3:4] / 255
    a[..., :3] = out[..., :3] * fa + o[..., :3] * (1 - fa); a[..., 3] = np.maximum(o[..., 3], out[..., 3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((size, size), Image.LANCZOS)

def shaft(col, w=8, h=32):
    """Across the height: dark edge, lit ridge (top-right light: upper half brighter)."""
    v = np.linspace(-1, 1, h)
    core = np.clip(1 - np.abs(v) / 0.72, 0, 1)
    lit = np.where(v < 0, 1.15, 0.72)                       # upper side catches the light
    k = (0.58 + 0.62 * core * lit)[:, None]
    b = np.array(col, np.float32); pale = b + (255 - b) * 0.75
    c = b[None, None, :] * np.minimum(k, 1.0)[..., None]
    s = np.clip((k - 1.0) * 1.5, 0, 0.8)[..., None]
    c = c * (1 - s) + pale * s
    edge = np.abs(v) > 0.72
    c[edge] = (8, 10, 14)
    a = np.where(np.abs(v) > 0.95, 120, 255)[:, None]
    img = np.zeros((h, w, 4), np.float32); img[..., :3] = np.repeat(c, w, axis=1); img[..., 3] = np.repeat(a, w, axis=1)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

if __name__ == '__main__':
    for k in ('tank', 'healer', 'dps', 'leader'): write_rgba(f'{OUT}/role_{k}.tga', glyph_tga(k))
    write_rgba(f'{OUT}/disc_plain.tga', disc()); write_rgba(f'{OUT}/ring_thin.tga', ring())
    write_rgba(f'{OUT}/glow_sq.tga', glow_sq())
    for name, col in (('gold', GOLD), ('blue', BLUE), ('gray', GRAY)):
        write_rgba(f'{OUT}/arrow_head_{name}.tga', head(col))
        write_rgba(f'{OUT}/arrow_shaft_{name}.tga', shaft(col))
    print('ok', OUT)
