# Mockup: AetherMeter rows, now (Blizzard-style font, thin 1 px shadow) vs the
# AetherFrames text style (Fira Sans Bold, 1 px black outline + drop shadow),
# over a bright and a dark patch of game world, on the meter's see-through panel.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
SC, PX = 4, 1.15
FIRA = '/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf'
BLIZ = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'      # stand-in for Friz Quadrata
BLIZB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
GOLD = (255, 209, 0); WHITE = (255, 255, 255); BLUE_T = (77, 166, 255)
PW, PH = 230, 104          # panel size, UI units

rows = [("1. Jay Iscariot", "4.0K", "72.6"), ("2. Steve", "1.9K", "34.1"), ("3. Thornbrew", "1.2K", "21.7")]
BGS = [Image.open('/mnt/user-data/uploads/aab9ff8c-image.png').convert('RGB').crop((280, 0, 550, 125)),
       Image.open('/tmp/v4/f_057.png').convert('RGB').crop((1180, 470, 1450, 595))]

def panel(bg, style):
    W, H = (PW + 20) * SC, (PH + 20) * SC
    img = bg.resize((W, H), Image.BICUBIC).convert('RGBA')
    over = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(over)
    x0, y0, x1, y1 = 10 * SC, 10 * SC, (10 + PW) * SC, (10 + PH) * SC
    d.rounded_rectangle([x0, y0, x1, y1], 8 * SC, fill=(13, 15, 22, 110), outline=(77, 166, 255, 200), width=SC)
    img.alpha_composite(over)
    def T(x, y, s, size, color, anchor='la', bold=False):
        L = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
        px, py = (10 + x) * SC, (10 + y) * SC
        if style == 'now':
            f = ImageFont.truetype(BLIZB if bold else BLIZ, int(size * SC))
            dd.text((px + SC, py + SC), s, font=f, fill=(0, 0, 0, 255), anchor=anchor)      # Blizzard's 1 px shadow
            dd.text((px, py), s, font=f, fill=color + (255,), anchor=anchor)
        else:
            f = ImageFont.truetype(FIRA, int(size * 1.08 * SC))
            dd.text((px + SC, py + SC), s, font=f, fill=(0, 0, 0, 255), stroke_width=SC, stroke_fill=(0, 0, 0, 255), anchor=anchor)
            dd.text((px, py), s, font=f, fill=color + (255,), stroke_width=SC, stroke_fill=(0, 0, 0, 255), anchor=anchor)
        img.alpha_composite(L)
    T(10, 8, "AETHER METER", 11, BLUE_T, bold=True)
    T(10, 26, "DPS", 10, GOLD, bold=True)
    # rows: 15-unit bars, 2 apart; class color at 85% over a 40% black backing,
    # status-bar texture approximated with a soft top-to-bottom shade
    CLASS = [((0.67, 0.83, 0.45), 1.0, True), ((0.78, 0.61, 0.43), 0.47, False), ((1.0, 0.49, 0.04), 0.30, False)]
    bl = Image.new('RGBA', img.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bl)
    for i, (col, share, me) in enumerate(CLASS):
        y = 42 + i * 17
        x0, x1 = 16 * SC, (PW + 4) * SC
        bd.rectangle([x0, (10 + y) * SC, x1, (10 + y + 15) * SC - 1], fill=(0, 0, 0, 102))
        for k in range(15 * SC):
            shade = 1.0 - 0.35 * (k / (15 * SC))
            c = tuple(int(255 * v * shade) for v in col) + (217,)
            bd.line([(x0, (10 + y) * SC + k), (x0 + int((x1 - x0) * share), (10 + y) * SC + k)], fill=c)
        if me: bd.rectangle([x0, (10 + y) * SC, x0 + 3 * SC, (10 + y + 15) * SC - 1], fill=(255, 209, 26, 255))
    img.alpha_composite(bl)
    for i, (n, a, b) in enumerate(rows):
        y = 44 + i * 17
        T(10, y, n, 10, WHITE)
        T(PW - 56, y, a, 10, WHITE, anchor='ra')
        T(PW - 10, y, b, 10, WHITE, anchor='ra')
    return img.convert('RGB')

labels = ["Now: Blizzard font, thin 1 px shadow", "Aether style: Fira Sans, outline + shadow (as AetherFrames)"]
cells = [[panel(bg, s) for s in ('now', 'aether')] for bg in BGS]
act = [[c.resize((int(c.width / SC * PX), int(c.height / SC * PX)), Image.LANCZOS) for c in r] for r in cells]
zooms = [c.crop((14 * SC, 52 * SC, (PW + 12) * SC, 92 * SC)) for c in cells[0]]
zooms = [z.resize((int(z.width / SC * PX * 2), int(z.height / SC * PX * 2)), Image.LANCZOS) for z in zooms]

pad = 18
aw, ah = act[0][0].size
cw = pad + 2 * (aw + pad) + max(z.width for z in zooms) + pad
ch = 34 + 2 * (ah + pad) + 10
out = Image.new('RGB', (max(cw, 2 * (aw + pad) + pad), 34 + 2 * (ah + pad) + 30 + 2 * zooms[0].height + 40), (18, 20, 26))
od = ImageDraw.Draw(out); lf = ImageFont.truetype(BLIZ, 13)
for j in range(2):
    od.text((pad + j * (aw + pad), 10), labels[j].split(':')[0], fill=(255, 209, 0), font=lf)
for i in range(2):
    for j in range(2):
        out.paste(act[i][j], (pad + j * (aw + pad), 34 + i * (ah + pad)))
yz = 34 + 2 * (ah + pad) + 4
od.text((pad, yz), "2x zoom, bright background (top: now, bottom: Aether style)", fill=(170, 180, 200), font=lf)
for k, z in enumerate(zooms):
    out.paste(z, (pad, yz + 22 + k * (z.height + 8)))
out = out.crop((0, 0, max(2 * (aw + pad) + pad, pad + zooms[0].width + pad), yz + 22 + 2 * (zooms[0].height + 8) + 6))
out.save(OUT)
print(out.size)
