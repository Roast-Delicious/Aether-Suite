# Character window side tabs (user, Nov 25 08:32): flat gold icons on navy
# for the non-character tabs (the Character tab keeps your portrait), and
# three ways to show the open tab. Shown beside the window edge, game size
# and 2x.
import math, numpy as np
from PIL import Image, ImageDraw
from talent_details import F
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74); DIM = (170, 176, 188)
SHOT = Image.open('/tmp/claude-tool-results/c68e43ba-f1eb-558c-a4cf-5ec92b504533/mcp-Claude_Docs-blob-1795620771324-rzxpix-cac35786.png').convert('RGBA')
PORTRAIT = SHOT.crop((972, 94, 1046, 164))

def glyph(d, kind, cx, cy, r, col):
    C = col
    if kind == 'rep':        # a banner on a pole (standing with a faction)
        d.rectangle([cx - r * .75, cy - r * .95, cx - r * .6, cy + r * .95], fill=C)
        d.polygon([(cx - r * .6, cy - r * .85), (cx + r * .85, cy - r * .85), (cx + r * .55, cy - r * .35),
                   (cx + r * .85, cy + r * .15), (cx - r * .6, cy + r * .15)], fill=C)
    elif kind == 'skills':   # crossed hammer and pick
        def bar(a, L, w):
            dx, dy = math.cos(a), math.sin(a)
            px, py = -dy * w, dx * w
            return [(cx - dx * L + px, cy - dy * L + py), (cx + dx * L + px, cy + dy * L + py), (cx + dx * L - px, cy + dy * L - py), (cx - dx * L - px, cy - dy * L - py)]
        d.polygon(bar(math.radians(45), r * .95, r * .09), fill=C); d.polygon(bar(math.radians(-45), r * .95, r * .09), fill=C)
        hx, hy = cx + r * .62, cy - r * .62
        d.polygon([(hx - r * .38, hy - r * .02), (hx - r * .02, hy - r * .38), (hx + r * .22, hy - r * .14), (hx - r * .14, hy + r * .22)], fill=C)
        px_, py_ = cx - r * .62, cy - r * .62
        d.polygon([(px_ - r * .42, py_ + r * .12), (px_ + r * .12, py_ - r * .42), (px_ + r * .05, py_ - r * .05)], fill=C)
    elif kind == 'pvp':      # shield with crossed blades
        w, h = r * .75, r * .9
        d.polygon([(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h * .15), (cx, cy + h), (cx - w, cy + h * .15)], fill=C)
        for s in (-1, 1):
            d.line([(cx - s * w * .55, cy - h * .6), (cx + s * w * .55, cy + h * .4)], fill=NAVY, width=max(2, int(r * .14)))
    elif kind == 'coin':     # stack of coins
        for i in range(3):
            y = cy + r * .5 - i * r * .38
            d.ellipse([cx - r * .75, y - r * .22, cx + r * .75, y + r * .22], fill=C, outline=NAVY, width=max(1, int(r * .08)))
    elif kind == 'stats':    # bar chart
        for i, hgt in enumerate((.5, .95, .7, 1.25)):
            x = cx - r * .8 + i * r * .44
            d.rectangle([x, cy + r * .75 - r * hgt, x + r * .3, cy + r * .75], fill=C)

TABS = [('portrait', 'Character'), ('rep', 'Reputation'), ('skills', 'Skills'), ('pvp', 'PvP'), ('coin', 'Currency'), ('stats', 'Statistics')]

def tab(kind, sel, style, S=72):
    pad = 14; im = Image.new('RGBA', (S + pad * 2, S + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = pad, pad, pad + S, pad + S
    if sel and style in ('B', 'C'):      # soft gold glow
        for k in range(12, 0, -1):
            d.rounded_rectangle([x0 - k, y0 - k, x1 + k, y1 + k], 10 + k, outline=GOLD + (int(60 * (13 - k) / 12),), width=2)
    fill = (28, 58, 104) if sel else NAVY
    d.rounded_rectangle([x0, y0, x1, y1], 9, fill=fill + (255,))
    if kind == 'portrait':
        p = PORTRAIT.resize((S - 10, S - 10)); m = Image.new('L', p.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, p.width - 1, p.height - 1], 7, fill=255)
        p.putalpha(m); im.alpha_composite(p, (x0 + 5, y0 + 5)); d = ImageDraw.Draw(im)
    else:
        gc = GOLD if (sel or style != 'C') else (190, 140, 40)
        glyph(d, kind, (x0 + x1) / 2, (y0 + y1) / 2, S * .3, gc + (255,))
    w = 3 if sel else 1
    col = GOLD if sel else BLUE
    d.rounded_rectangle([x0, y0, x1, y1], 9, outline=col + (255,), width=w)
    if sel:
        d.rectangle([x0 - 2, y0 + 12, x0 + 3, y1 - 12], fill=GOLD + (255,))
    if not sel and style == 'C':
        L = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(L).rounded_rectangle([x0, y0, x1, y1], 9, fill=(0, 0, 0, 80)); im.alpha_composite(L)
    return im

STY = [('A', "A  Thick gold frame + notch"), ('B', "B  A + soft gold glow  (my pick)"), ('C', "C  B + other tabs dimmed")]
SEL = 1    # Reputation open
cols = []
for st, name in STY:
    col = Image.new('RGBA', (330, 760), (16, 18, 24, 255)); d = ImageDraw.Draw(col)
    d.text((10, 8), name, font=F(18, 'SemiBold'), fill=GOLD + (255,))
    # window edge
    d.rounded_rectangle([-20, 50, 40, 740], 8, fill=(12, 14, 19, 255), outline=BLUE + (255,), width=2)
    for i, (k, lab) in enumerate(TABS):
        t = tab(k, i == SEL, st, 56); col.alpha_composite(t, (40, 60 + i * 76))
        big = tab(k, i == SEL, st, 112) if i in (0, 1, 2) else None
        if big: col.alpha_composite(big, (150, 60 + i * 150))
    d.text((150 + 70, 520), "2x", font=F(15), fill=DIM + (255,), anchor='ma')
    cols.append(col)
W = sum(c.width for c in cols) + 40
sheet = Image.new('RGBA', (W, 780), (16, 18, 24, 255)); x = 10
for c in cols: sheet.alpha_composite(c, (x, 10)); x += c.width + 10
dd = ImageDraw.Draw(sheet)
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_sidetabs.png'); print(sheet.size)
