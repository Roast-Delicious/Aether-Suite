# Scroll slider in gold, flat vs 3D (bevel lit from the top-right like the
# gold accents), on the Reputation list at game size, plus a 4x zoom.
import numpy as np, cv2
from PIL import Image, ImageDraw
from talent_details import bevel, F
GOLD = (255, 176, 0); BLUE = (77, 166, 255)
SHOT = '/tmp/claude-tool-results/c68e43ba-f1eb-558c-a4cf-5ec92b504533/mcp-Claude_Docs-blob-1795620771324-rzxpix-cac35786.png'

def thumb(w, h, kind, S=4):
    W, H = w * S, h * S
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, H - 1], W // 2, fill=255)
    m = (np.array(m) > 127).astype(np.uint8)
    if kind == 'flat':
        out = np.zeros((H, W, 4), np.float32); out[..., :3] = GOLD; out[..., 3] = m * 255
    else:
        # a rounded bar lit from the top-right: shading runs across the width
        # (darker left, bright ridge right of center), like the gold accents
        xs = np.linspace(-1, 1, W)
        nz = np.sqrt(np.clip(1 - xs ** 2, 0, 1)); nx = xs
        L = np.array([0.62, 0.62]); L = L / np.linalg.norm(L)
        diff = np.clip(nx * L[0] + nz * L[1], 0, 1)
        spec = np.clip(nx * 0.38 + nz * 0.92, 0, 1) ** 30
        k = (0.58 + 0.62 * diff)[None, :, None]
        g = np.array(GOLD, np.float32); pale = g + (255 - g) * 0.75
        col = g * np.minimum(k, 1.0)
        sp = np.clip(spec * 0.9 + np.clip(k[..., 0] - 1, 0, 1) * 1.5, 0, 0.8)[..., None]
        col = np.repeat(col * (1 - sp) + pale * sp, H, axis=0)
        out = np.zeros((H, W, 4), np.float32); out[..., :3] = col; out[..., 3] = m * 255
        if kind == 'rim':      # thin dark outline around the 3D thumb
            d = cv2.dilate(m, np.ones((2 * S + 1, 2 * S + 1), np.uint8)) - m
            out[d > 0, :3] = (8, 10, 14); out[d > 0, 3] = 230
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    return im.resize((w + (2 if kind == 'rim' else 0), h + (2 if kind == 'rim' else 0)), Image.LANCZOS) if kind == 'rim' else im.resize((w, h), Image.LANCZOS)

def track(img, x, y0, y1, kind, ty0, ty1, w=8):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - w // 2, y0, x + w // 2, y1], w // 2, fill=(14, 28, 52, 255))
    t = thumb(w, ty1 - ty0, kind); img.alpha_composite(t, (x - t.width // 2, ty0))
    for yy, up in ((y0 - 14, True), (y1 + 6, False)):
        pts = [(x - 6, yy + 8), (x + 6, yy + 8), (x, yy)] if up else [(x - 6, yy), (x + 6, yy), (x, yy + 8)]
        d.polygon(pts, fill=GOLD + (255,))

base = Image.open(SHOT).convert('RGBA').crop((40, 130, 620, 720))
opts = [('flat', "A  Flat gold"), ('bevel', "B  3D gold"), ('rim', "C  3D gold, dark rim  (my pick)")]
panels = []
for kind, name in opts:
    im = base.copy()
    ImageDraw.Draw(im).rectangle([544, 0, 580, 590], fill=(12, 14, 19, 255))   # cover the old bar
    track(im, 555, 30, 560, kind, 40, 300)
    z = Image.new('RGBA', (120, 590), (16, 18, 24, 255))
    zt = thumb(32, 240, kind); z.alpha_composite(zt, (60 - zt.width // 2, 40))
    ImageDraw.Draw(z).text((60, 300), "4x", font=F(16), fill=(170, 176, 188, 255), anchor='ma')
    p = Image.new('RGBA', (im.width + z.width + 10, im.height + 50), (16, 18, 24, 255))
    ImageDraw.Draw(p).text((8, 12), name, font=F(20, 'SemiBold'), fill=GOLD + (255,))
    p.alpha_composite(im, (0, 50)); p.alpha_composite(z, (im.width + 10, 50))
    panels.append(p)
W = sum(p.width for p in panels) + 40
sheet = Image.new('RGBA', (W, panels[0].height + 20), (16, 18, 24, 255)); x = 10
for p in panels: sheet.alpha_composite(p, (x, 10)); x += p.width + 10
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_slider.png'); print(sheet.size)
