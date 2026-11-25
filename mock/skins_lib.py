# Mockup kit for AetherSkins: draws the decided Aether window look at the
# user's screenshot scale (about 1.55 px per UI unit). Rounded corners
# (radius 8), blue edge + fine inner line, 10-unit soft glow, navy title
# strip with a gold underline, gold chevrons at 12/3/6/9 (26 / 34 units,
# 3 out). Aether gold (255,176,0) is the only yellow.
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
U = 1.55                      # px per UI unit
SS = 3                        # supersampling
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74)
PANEL = (12, 14, 19); WHITE = (235, 238, 245); DIM = (150, 156, 170)
GREEN = (34, 230, 80); RED = (230, 60, 50); ORANGE = (240, 128, 40)
SKY = (115, 191, 255)
FD = '/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
MED = '/home/claude/brand/AetherHub/Media/'
def F(size, w='Regular'): return ImageFont.truetype(FD + w + '.ttf', int(size * SS))
def u(x): return int(round(x * U * SS))

def tga(name, color, size):
    im = Image.open(MED + name + '.tga').convert('RGBA').resize(size, Image.LANCZOS)
    out = Image.new('RGBA', im.size, color + (255,)); out.putalpha(im.split()[3]); return out

def glow(W, H, box, radius, width, color, strength):
    x0, y0, x1, y1 = box; R = radius
    yy, xx = np.mgrid[0:H, 0:W]
    dx = np.maximum(np.maximum(x0 + R - xx, xx - (x1 - R)), 0)
    dy = np.maximum(np.maximum(y0 + R - yy, yy - (y1 - R)), 0)
    d = np.hypot(dx, dy) - R
    al = np.where((d > 0) & (d < width), strength * (1 - d / width) ** 2, 0)
    g = np.zeros((H, W, 4), np.uint8); g[..., :3] = color; g[..., 3] = (al * 255).astype(np.uint8)
    return Image.fromarray(g)

class Canvas:
    """Draws in screen px (x SS internally) on top of a background crop."""
    def __init__(self, bg):
        self.bg = bg.convert('RGBA')
        self.im = self.bg.resize((bg.width * SS, bg.height * SS), Image.LANCZOS)
        self.d = ImageDraw.Draw(self.im)
    def P(self, *v): return [int(round(a * SS)) for a in v]
    def over(self, layer, xy=(0, 0)):
        self.im.alpha_composite(layer, (int(xy[0] * SS), int(xy[1] * SS)))
        self.d = ImageDraw.Draw(self.im)
    def layer(self):
        L = Image.new('RGBA', self.im.size, (0, 0, 0, 0)); return L, ImageDraw.Draw(L)
    def text(self, xy, s, size, color, w='Regular', anchor='la', outline=False):
        f = F(size, w); x, y = self.P(*xy)
        if outline:
            for ox in (-SS, 0, SS):
                for oy in (-SS, 0, SS):
                    self.d.text((x + ox, y + oy), s, font=f, fill=(0, 0, 0, 255), anchor=anchor)
        else:
            self.d.text((x + SS, y + SS), s, font=f, fill=(0, 0, 0, 200), anchor=anchor)
        self.d.text((x, y), s, font=f, fill=color + (255,), anchor=anchor)
    def window(self, box, title, alpha=242, chevrons=True, strip=24, chev3d=False):
        x0, y0, x1, y1 = self.P(*box); R = u(8); W, H = self.im.size
        self.over(glow(W, H, (x0, y0, x1, y1), R, u(10), BLUE, 0.42))
        L, d = self.layer()
        d.rounded_rectangle([x0, y0, x1, y1], R, fill=PANEL + (alpha,))
        # navy title strip, clipped to the rounded top
        t = u(strip)
        m = Image.new('L', L.size, 0); ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], R, fill=255)
        band = Image.new('L', L.size, 0); ImageDraw.Draw(band).rectangle([x0, y0, x1, y0 + t], fill=255)
        navy = Image.new('RGBA', L.size, NAVY + (255,))
        L.paste(navy, (0, 0), Image.fromarray(np.minimum(np.array(m), np.array(band))))
        d.line([x0 + u(5), y0 + t, x1 - u(5), y0 + t], fill=GOLD + (220,), width=SS)
        d.rounded_rectangle([x0, y0, x1, y1], R, outline=BLUE + (255,), width=SS)
        i = u(3); d.rounded_rectangle([x0 + i, y0 + i, x1 - i, y1 - i], R - i, outline=BLUE + (85,), width=SS)
        self.over(L)
        if title: self.text(((box[0] + box[2]) / 2, box[1] + strip * U / 2), title, 17, GOLD, 'SemiBold', 'mm')
        if chevrons:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2; Pp = u(3)
            sides = chevrons if isinstance(chevrons, str) else 'tbrl'
            for side, x, y, rot, sz in (('t', cx, y0 - Pp, 0, 26), ('b', cx, y1 + Pp, 180, 26), ('r', x1 + Pp, cy, -90, 34), ('l', x0 - Pp, cy, 90, 34)):
                if side not in sides: continue
                k = u(sz)
                c = tga('win_chev_dark', (10, 11, 14), (k, k)).rotate(rot, resample=Image.BICUBIC)
                self.im.alpha_composite(c, (x - k // 2, y - k // 2))
                if chev3d:     # the 3D (bevel ridge) chevron, lit from the top-right
                    import skin_chevron3d as C3
                    c = C3.chevron3d('bevel', rot).rotate(rot, resample=Image.BICUBIC).resize((k, k), Image.LANCZOS)
                else:
                    c = tga('win_chev_gold', GOLD, (k, k)).rotate(rot, resample=Image.BICUBIC)
                self.im.alpha_composite(c, (x - k // 2, y - k // 2))
            self.d = ImageDraw.Draw(self.im)
    def close(self, cx, cy):
        s = 11; x0, y0, x1, y1 = self.P(cx - s, cy - s, cx + s, cy + s)
        self.d.rounded_rectangle([x0, y0, x1, y1], u(3), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
        k = 5 * SS; X, Y = self.P(cx, cy)
        self.d.line([X - k, Y - k, X + k, Y + k], fill=WHITE + (255,), width=2 * SS)
        self.d.line([X - k, Y + k, X + k, Y - k], fill=WHITE + (255,), width=2 * SS)
    def button(self, box, label, size=16, danger=False):
        x0, y0, x1, y1 = self.P(*box)
        self.d.rounded_rectangle([x0, y0, x1, y1], u(4), fill=NAVY + (255,),
                                 outline=(RED if danger else BLUE) + (255,), width=SS)
        self.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), label, size, WHITE, 'SemiBold', 'mm')
    def header(self, box, label, minus=True):
        """Tracker-style section header: navy band fading right, gold text, tapered gold line."""
        x0, y0, x1, y1 = self.P(*box); w = x1 - x0; h = y1 - y0
        a = np.clip(1.25 - np.linspace(0, 1, w) * 1.1, 0, 1) * 0.95
        band = np.zeros((h, w, 4), np.uint8); band[..., :3] = NAVY; band[..., 3] = (a * 255).astype(np.uint8)[None, :]
        self.im.alpha_composite(Image.fromarray(band), (x0, y0))
        t = np.sin(np.linspace(0, np.pi, w)) ** 0.6
        line = np.zeros((2 * SS, w, 4), np.uint8); line[..., :3] = GOLD; line[..., 3] = (t * 255).astype(np.uint8)[None, :]
        self.im.alpha_composite(Image.fromarray(line), (x0, y1 - 2 * SS))
        self.d = ImageDraw.Draw(self.im)
        self.text((box[0] + 12, (box[1] + box[3]) / 2), label, 17, GOLD, 'SemiBold', 'lm')
        if minus: self.text((box[2] - 14, (box[1] + box[3]) / 2 - 1), "–", 20, GOLD, 'Bold', 'mm')
    def bar(self, box, frac, color, label, pill=False):
        x0, y0, x1, y1 = self.P(*box); r = (y1 - y0) // 2 if pill else u(3)
        self.d.rounded_rectangle([x0, y0, x1, y1], r, fill=(8, 12, 22, 255), outline=(60, 110, 175, 255), width=SS)
        fx = x0 + SS + int((x1 - x0 - 2 * SS) * frac)
        if frac > 0:
            L, d = self.layer()
            d.rounded_rectangle([x0 + SS, y0 + SS, max(fx, x0 + 2 * r), y1 - SS], max(1, r - SS), fill=color + (215,))
            self.over(L)
            L, d = self.layer()
            d.rounded_rectangle([x0 + SS, y0 + SS, max(fx, x0 + 2 * r), y0 + (y1 - y0) // 2], max(1, r - SS), fill=(255, 255, 255, 30))
            self.over(L)
        if label: self.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), label, 15, WHITE, 'Regular', 'mm', outline=True)
    def check(self, xy, label, on=False):
        x, y = xy; x0, y0, x1, y1 = self.P(x, y, x + 20, y + 20)
        self.d.rounded_rectangle([x0, y0, x1, y1], u(2), fill=(8, 12, 22, 255), outline=BLUE + (255,), width=SS)
        if on:
            self.d.line(self.P(x + 5, y + 10, x + 9, y + 15), fill=GOLD + (255,), width=3 * SS)
            self.d.line(self.P(x + 9, y + 15, x + 16, y + 5), fill=GOLD + (255,), width=3 * SS)
        self.text((x + 30, y + 10), label, 16, WHITE if on else DIM, 'Regular', 'lm')
    def crest(self, c, r, icon=None):
        """Round crest like AetherFrames: navy disc, blue rim, gold chevron on top."""
        cx, cy = c; L, d = self.layer(); X, Y = self.P(cx, cy); R = int(r * SS)
        W, H = self.im.size
        g = glow(W, H, (X, Y, X, Y), R, u(8), BLUE, 0.45); L.alpha_composite(g)
        d.ellipse([X - R, Y - R, X + R, Y + R], fill=NAVY + (255,), outline=BLUE + (255,), width=2 * SS)
        if icon is not None:
            k = int(R * 1.5); ic = icon.convert('RGBA').resize((k, k), Image.LANCZOS)
            mk = Image.new('L', (k, k), 0); ImageDraw.Draw(mk).ellipse([0, 0, k - 1, k - 1], fill=255)
            ic.putalpha(Image.fromarray(np.minimum(np.array(ic.split()[3]), np.array(mk))))
            L.alpha_composite(ic, (X - k // 2, Y - k // 2))
        i = 4 * SS; d.ellipse([X - R + i, Y - R + i, X + R - i, Y + R - i], outline=BLUE + (90,), width=SS)
        self.over(L)
    def recolor_icon(self, im, color):
        """Blizzard's yellow UI glyphs -> one color (Aether gold is the only yellow)."""
        a = np.array(im.convert('RGBA')).astype(np.float32)
        lum = a[..., :3].max(axis=2) / 255
        out = np.zeros_like(a); out[..., :3] = color; out[..., 3] = a[..., 3] * np.clip(lum * 1.4, 0, 1)
        return Image.fromarray(out.astype(np.uint8))
    def paste(self, im, xy, size=None):
        im = im.convert('RGBA')
        if size: im = im.resize((int(size[0] * SS), int(size[1] * SS)), Image.LANCZOS)
        else: im = im.resize((im.width * SS, im.height * SS), Image.LANCZOS)
        self.over(im, xy)
    def tri(self, cx, cy, s, color, d='down'):
        pts = {'down': [(cx - s, cy - s / 2), (cx + s, cy - s / 2), (cx, cy + s / 2)],
               'right': [(cx - s / 2, cy - s), (cx - s / 2, cy + s), (cx + s / 2, cy)]}[d]
        self.d.polygon([tuple(self.P(*p)) for p in pts], fill=color + (255,))
    def menu(self, cx, cy, color=WHITE):
        for k in (-6, 0, 6): self.d.line(self.P(cx - 8, cy + k, cx + 8, cy + k), fill=color + (255,), width=2 * SS)
    def done(self): return self.im.resize((self.im.width // SS, self.im.height // SS), Image.LANCZOS).convert('RGB')

def label(img, text, size=26):
    bar = Image.new('RGB', (img.width, size + 18), (16, 18, 24)); d = ImageDraw.Draw(bar)
    d.text((12, 8), text, font=ImageFont.truetype(FD + 'SemiBold.ttf', size), fill=GOLD)
    out = Image.new('RGB', (img.width, img.height + bar.height)); out.paste(bar, (0, 0)); out.paste(img, (0, bar.height)); return out
