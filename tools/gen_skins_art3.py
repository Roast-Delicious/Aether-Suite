# Bakes AetherSkins' Build 2 art (Nov 25) from the approved mockups:
#   tab_*.tga, gl_*.tga        flat glyphs (mock/sidetabs_flat.py,
#                              mock/crests_flat.py), white with alpha,
#                              tinted Aether gold in game
#   btn_*.tga                  vendor buttons (mock/vendor.py glyph_img)
#   role_newcomer.tga          New Player Friendly sprout (mock/npf.py)
#   gl_check.tga               check mark (tracker hand-ins, mock/trk_check.py)
#   sb_thumb_{top,mid,bot}.tga beveled gold scroll thumb (mock/slider3d.py
#                              'bev'): ridge down the middle, dark left
#                              facet, lit right facet, thin dark rim
#   page_aether.tga            the Aether page (mock/pass2_parch.py option 3):
#                              navy gradient with a fine grain
# Run from mock/ (it imports the mock modules): python3 ../tools/gen_skins_art3.py
import sys, os, math, numpy as np, cv2
sys.path.insert(0, '/home/claude/aether-repo/mock'); sys.path.insert(0, '/home/claude/aether-repo/tools')
from PIL import Image, ImageDraw
from gen_skins_art import write_rgba, white_alpha
import sidetabs_flat as ST
import crests_flat as CR
import vendor as VD
import npf

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/aether-repo/AetherSkins/Media'
GOLD = (255, 176, 0)

def mono(draw_fn, size=128, S=8):
    """Draw in white on black (navy cut-outs come out dark), alpha = red."""
    n = size * S
    im = Image.new('RGB', (n, n), (0, 0, 0)); d = ImageDraw.Draw(im)
    draw_fn(d, n)
    a = np.array(im)[..., 0]
    return white_alpha(Image.fromarray(a).resize((size, size), Image.LANCZOS))

W = (255, 255, 255)
def tab(kind):
    return mono(lambda d, n: ST.glyph(d, kind, n / 2, n / 2, n * 0.40, W))
def crest(kind):
    return mono(lambda d, n: CR.g(d, kind, n / 2, n / 2, n * 0.40, W + (255,)))

def btn(kind, size=128):
    im = VD.glyph_img(kind, size, (255, 255, 255, 255))     # navy cut-outs stay navy
    a = np.array(im).astype(np.float32)
    alpha = a[..., 3] * np.clip((a[..., 0] - 19) / (255 - 19), 0, 1)
    return white_alpha(Image.fromarray(alpha.astype(np.uint8)))

def sprout():
    return mono(lambda d, n: npf.sprout(d, n / 2, n / 2 - n * 0.02, n * 0.42, W))

def check():
    def f(d, n):
        d.line([(n * .2, n * .52), (n * .42, n * .74), (n * .8, n * .28)], fill=W, width=int(n * .14), joint='curve')
    return mono(f)

def thumb_parts(w=32):
    """Beveled gold thumb, sliced: round top cap, a middle strip, round bottom cap."""
    S = 4; Wd = w * S; H = Wd * 3
    m = Image.new('L', (Wd, H), 0); ImageDraw.Draw(m).rounded_rectangle([S, 0, Wd - 1 - S, H - 1], (Wd - 2 * S) // 2, fill=255)
    m = (np.array(m) > 127).astype(np.uint8)
    xs = np.linspace(-1, 1, Wd)
    k = np.where(xs < 0, 0.6, 1.08) * (0.8 + 0.2 * (1 - np.abs(xs)))
    ridge = np.exp(-(xs / 0.09) ** 2) * 0.75
    g = np.array(GOLD, np.float32); pale = g + (255 - g) * 0.75
    col = g * np.minimum(k, 1.0)[:, None]
    sp = np.clip(ridge + np.clip(k - 1, 0, 1) * 1.2, 0, 0.8)[:, None]
    col = col * (1 - sp) + pale * sp
    edge = np.abs(xs) > 0.8; col[edge] = col[edge] * 0.55
    out = np.zeros((H, Wd, 4), np.float32); out[..., :3] = np.repeat(col[None], H, axis=0); out[..., 3] = m * 255
    rim = cv2.dilate(m, np.ones((2 * S + 1, 2 * S + 1), np.uint8)) - m
    out[rim > 0, :3] = (8, 10, 14); out[rim > 0, 3] = 230
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    top = im.crop((0, 0, Wd, Wd)).resize((w, w), Image.LANCZOS)
    mid = im.crop((0, H // 2 - S, Wd, H // 2 + S)).resize((w, 8), Image.LANCZOS)
    bot = im.crop((0, H - Wd, Wd, H)).resize((w, w), Image.LANCZOS)
    return top, mid, bot

def page(w=256, h=512):
    yy, xx = np.mgrid[0:h, 0:w]
    g = (1 - 0.35 * yy / h) * (1 - 0.22 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2))
    rng = np.random.default_rng(3)
    g = g + cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.8) * 0.03
    lo, hi = np.array([6, 12, 24.]), np.array([22, 42, 76.])
    c = lo + g[..., None] * (hi - lo)
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = np.clip(c, 0, 255); out[..., 3] = 245
    return Image.fromarray(out)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k in ('rep', 'skills', 'pvp', 'coin', 'stats'):
        write_rgba(os.path.join(OUT, 'tab_%s.tga' % k), tab(k))
    for k in ('map', 'book', 'talents', 'eyeball', 'eye', 'friends', 'people', 'clock', 'request', 'track'):
        write_rgba(os.path.join(OUT, 'gl_%s.tga' % k), crest(k))
    for k in ('repairall', 'repair', 'guild', 'junk'):
        write_rgba(os.path.join(OUT, 'btn_%s.tga' % k), btn(k))
    write_rgba(os.path.join(OUT, 'role_newcomer.tga'), sprout())
    write_rgba(os.path.join(OUT, 'gl_check.tga'), check())
    t, m, b = thumb_parts()
    write_rgba(os.path.join(OUT, 'sb_thumb_top.tga'), t); write_rgba(os.path.join(OUT, 'sb_thumb_mid.tga'), m)
    write_rgba(os.path.join(OUT, 'sb_thumb_bot.tga'), b)
    write_rgba(os.path.join(OUT, 'page_aether.tga'), page())
    print("ok")
