# Point counts as words (user, Nov 25 07:05): "2 of 5", "5 of 5".
# 3c: a pill across the bottom edge of the icon; 3d: a line under the node
# (the arrow then starts below it); 3b (badge "2/5") for comparison.
from PIL import Image, ImageDraw
import talent_states as TS
from talent_details import node, arrow, F, GOLD, BLUE, GRAY

def pill_bottom(im, txt, col):
    d = ImageDraw.Draw(im); S = im.width
    f = F(max(11, int(S * 0.19)), 'Bold'); w = d.textlength(txt, font=f) + S * 0.16
    cx = S / 2; y1 = S - 2; y0 = y1 - S * 0.27
    d.rounded_rectangle([cx - w / 2, y0, cx + w / 2, y1], int(S * 0.13), fill=(8, 12, 22, 255), outline=col + (255,), width=max(1, S // 40))
    d.text((cx, (y0 + y1) / 2), txt, font=f, fill=col + (255,), anchor='mm')
    return im

def column(sheet, x, y, S, style):
    items = [(TS.CLAW, 'max', 2, 2), (TS.BEAST, 'part', 3, 5)]
    gap = int(S * (0.95 if style == 'd' else 0.75))
    for i, (ic, st, n, m) in enumerate(items):
        col = GOLD if st == 'max' else BLUE
        yy = y + i * (S + gap)
        if style == 'b':
            im = node(ic, st, S, f"{n}/{m}", 'b')
        else:
            im = node(ic, st, S)
            if style == 'c': pill_bottom(im, f"{n} of {m}", col)
        sheet.alpha_composite(im, (x, yy))
        if style == 'd':
            ImageDraw.Draw(sheet).text((x + S / 2, yy + S + 2), f"{n} of {m}", font=F(max(11, int(S * 0.2)), 'Bold'), fill=col + (255,), anchor='ma',
                                       stroke_width=2, stroke_fill=(0, 0, 0))
    off = int(S * 0.24) if style == 'd' else 0
    a = arrow(gap + 6 - off, GOLD, max(3, S // 14))
    sheet.alpha_composite(a, (x + S // 2 - a.width // 2, y + S - 7 + off))

W, H = 1080, 640
sheet = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
d.text((24, 18), "Point counts as \"2 of 5\"", font=F(28, 'SemiBold'), fill=GOLD)
d.text((24, 60), "Maxed (top) and some points (bottom).  2x zoom, then game size.", font=F(17), fill=(170, 176, 188))
for i, (st, name) in enumerate((('b', "3b  Badge \"2/5\""), ('c', "3c  Pill on the icon"), ('d', "3d  Line under the icon"))):
    x = 40 + i * 345
    d.text((x, 100), name, font=F(20, 'SemiBold'), fill=(235, 238, 245))
    column(sheet, x + 10, 150, 128, st)
    column(sheet, x + 200, 150, 64, st)
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_talent_counts.png'); print(sheet.size)
