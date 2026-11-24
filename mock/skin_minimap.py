# Mockup: the minimap in the Aether look, four options, on the user's screenshot.
import sys; sys.path.insert(0, '/home/claude/mock')
from skins_lib import *
from PIL import Image, ImageDraw
import numpy as np, cv2
FULL = Image.open('/tmp/v4/f_057.png').convert('RGB')
A = np.array(FULL)
CX, CY, RM = 2131, 206, 117            # Blizzard minimap: center and map radius (px)
X0, Y0, X1, Y1 = 1900, 0, 2304, 440    # region shown

# 1) world with Blizzard's ring, zone box, coords box and buttons painted out
mask = np.zeros(A.shape[:2], np.uint8)
cv2.circle(mask, (CX, CY), 152, 255, -1); cv2.circle(mask, (CX, CY), RM - 1, 0, -1)
cv2.rectangle(mask, (2015, 0), (2275, 34), 255, -1)      # zone + clock strip
cv2.rectangle(mask, (2070, 345), (2190, 386), 255, -1)   # coords box
cv2.circle(mask, (2203, 95), 26, 255, -1); cv2.circle(mask, (2014, 292), 24, 255, -1)
cv2.rectangle(mask, (1998, 0), (2030, 30), 255, -1); cv2.rectangle(mask, (2232, 30), (2262, 58), 255, -1)
CLEAN = cv2.inpaint(A[..., ::-1], mask, 9, cv2.INPAINT_TELEA)[..., ::-1]
# 2) map content: the disk, and a square version with the corners filled in
disk = np.zeros(A.shape[:2], np.uint8); cv2.circle(disk, (CX, CY), RM - 2, 255, -1)
sq = np.zeros(A.shape[:2], np.uint8); cv2.rectangle(sq, (CX - 132, CY - 132), (CX + 132, CY + 132), 255, -1)
MAPSQ = cv2.inpaint(A[..., ::-1], cv2.bitwise_and(sq, cv2.bitwise_not(disk)), 15, cv2.INPAINT_TELEA)[..., ::-1]
SUN = FULL.crop((2181, 73, 2225, 117)); GEM = FULL.crop((1993, 271, 2035, 313))

def base(square, half=126):
    im = CLEAN.copy()
    if square:
        m = np.zeros(A.shape[:2], np.uint8)
        cv2.rectangle(m, (CX - half, CY - half), (CX + half, CY + half), 255, -1)
        im[m > 0] = MAPSQ[m > 0]
    else:
        im[disk > 0] = A[disk > 0]
    return Canvas(Image.fromarray(im).crop((X0, Y0, X1, Y1)))

def chevs(c, cx, cy, rx, ry, top=26, side=26):
    for x, y, rot, sz in ((cx, cy - ry, 0, top), (cx, cy + ry, 180, side), (cx + rx, cy, -90, side), (cx - rx, cy, 90, side)):
        k = u(sz); X, Y = c.P(x, y)
        for name, col in (('win_chev_dark', (10, 11, 14)), ('win_chev_gold', GOLD)):
            c.im.alpha_composite(tga(name, col, (k, k)).rotate(rot, resample=Image.BICUBIC), (X - k // 2, Y - k // 2))
    c.d = ImageDraw.Draw(c.im)

def pill(c, box, text, size=15, color=WHITE, gold_line=False, right=None):
    x0, y0, x1, y1 = c.P(*box)
    Lr, d = c.layer()
    d.rounded_rectangle([x0, y0, x1, y1], (y1 - y0) // 2, fill=NAVY + (235,), outline=BLUE + (255,), width=SS)
    if gold_line: d.line([x0 + 3 * (y1 - y0) // 4, y1 - 3 * SS, x1 - 3 * (y1 - y0) // 4, y1 - 3 * SS], fill=GOLD + (220,), width=SS)
    c.over(Lr)
    if right:
        c.text((box[0] + 16, (box[1] + box[3]) / 2), text, size, color, 'SemiBold', 'lm')
        c.text((box[2] - 14, (box[1] + box[3]) / 2), right, size, WHITE, 'Regular', 'rm')
    else:
        c.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), text, size, color, 'SemiBold', 'mm')

def button(c, xy, icon, r=17):
    x, y = xy; Lr, d = c.layer(); X, Y = c.P(x, y); R = r * SS
    d.ellipse([X - R, Y - R, X + R, Y + R], fill=NAVY + (255,), outline=BLUE + (255,), width=SS); c.over(Lr)
    k = int(r * 1.5); c.paste(icon, (x - k / 2, y - k / 2), (k, k))

def opt_round(ring, width=2):
    c = base(False); cx, cy = CX - X0, CY - Y0
    W, H = c.im.size; X, Y = c.P(cx, cy); R = (RM + 1) * SS
    c.over(glow(W, H, (X, Y, X, Y), R, u(10), BLUE, 0.45))
    Lr, d = c.layer()
    col = GOLD if ring == 'gold' else BLUE
    Ro = R + (width // 2) * SS   # a thicker ring grows outward; the map stays the same size
    d.ellipse([X - Ro, Y - Ro, X + Ro, Y + Ro], outline=col + (255,), width=width * SS)
    i = u(3); d.ellipse([X - R + i, Y - R + i, X + R - i, Y + R - i], outline=BLUE + (90,), width=SS)
    c.over(Lr)
    if ring != 'gold': chevs(c, cx, cy, RM + 6 + width // 2, RM + 6 + width // 2)
    pill(c, (cx - 118, 6, cx + 118, 34), "Dustwallow Marsh", 15, GOLD, right="05:52")
    pill(c, (cx - 52, cy + RM + 16, cx + 52, cy + RM + 42), "62.5, 44.4", 15, WHITE)
    button(c, (cx + 84, cy - 86), SUN); button(c, (cx - 86, cy + 84), GEM)
    return c.done()

def opt_square(style):
    half = 126; c = base(True, half); cx, cy = CX - X0, CY - Y0
    box = (cx - half, cy - half, cx + half, cy + half)
    W, H = c.im.size; x0, y0, x1, y1 = c.P(*box); R = u(8)
    if style == 'window':
        top = box[1] - 30
        c.over(glow(W, H, (x0, c.P(0, top)[1], x1, y1 + u(28)), R, u(10), BLUE, 0.42))
        Lr, d = c.layer()
        # title strip above the map, coords strip under it, one rounded frame around all
        d.rounded_rectangle(c.P(box[0], top, box[2], box[1]), R, fill=NAVY + (255,))
        d.rectangle(c.P(box[0], top + 10, box[2], box[1]), fill=NAVY + (255,))
        d.rectangle(c.P(box[0], box[3], box[2], box[3] + 18), fill=PANEL + (240,))
        d.rounded_rectangle(c.P(box[0], box[3], box[2], box[3] + 28), R, fill=PANEL + (240,))
        d.line(c.P(box[0] + 4, box[1], box[2] - 4, box[1]), fill=GOLD + (220,), width=SS)
        d.rounded_rectangle(c.P(box[0], top, box[2], box[3] + 28), R, outline=BLUE + (255,), width=SS)
        i = 3; d.rounded_rectangle(c.P(box[0] + i, top + i, box[2] - i, box[3] + 28 - i), R - u(3), outline=BLUE + (85,), width=SS)
        c.over(Lr)
        c.text((box[0] + 12, top + 15), "Dustwallow Marsh", 15, GOLD, 'SemiBold', 'lm')
        c.text((box[2] - 12, top + 15), "05:52", 15, WHITE, 'Regular', 'rm')
        c.text((cx, box[3] + 14), "62.5, 44.4", 15, WHITE, 'SemiBold', 'mm')
        chevs(c, cx, (top + box[3] + 28) / 2, half + 5, (box[3] + 28 - top) / 2 + 5, 26, 26)
        button(c, (box[2] - 22, box[1] + 22), SUN, 15); button(c, (box[0] + 22, box[3] - 22), GEM, 15)
    else:   # minimal
        c.over(glow(W, H, (x0, y0, x1, y1), R, u(6), BLUE, 0.3))
        Lr, d = c.layer()
        # round the map's corners: paint the world back outside the rounded square
        d.rounded_rectangle([x0, y0, x1, y1], R, outline=BLUE + (255,), width=SS)
        c.over(Lr)
        c.text((cx, box[1] + 14), "Dustwallow Marsh", 15, GOLD, 'SemiBold', 'mm', outline=True)
        c.text((box[2] - 8, box[3] - 12), "62.5, 44.4", 14, WHITE, 'SemiBold', 'rm', outline=True)
        c.text((box[0] + 8, box[3] - 12), "05:52", 14, WHITE, 'Regular', 'lm', outline=True)
        button(c, (box[2] - 20, box[1] + 36), SUN, 14); button(c, (box[0] + 20, box[1] + 36), GEM, 14)
    return c.done()

if __name__ == '__main__':
    opts = [("Last time (2 px)", opt_round('blue', 2)),
            ("1  Medium (4 px)", opt_round('blue', 4)),
            ("2  Thick (6 px)", opt_round('blue', 6)),
            ("3  Heavy (8 px)", opt_round('blue', 8))]
    tiles = [label(im, name, 20) for name, im in opts]
    for (name, im), k in zip(opts, "0123"): im.save('/tmp/sk/mm_%s.png' % k)
    W = sum(t.width for t in tiles); sheet = Image.new('RGB', (W, tiles[0].height)); x = 0
    for t in tiles: sheet.paste(t, (x, 0)); x += t.width
    sheet.save('/tmp/sk/mm_sheet.png'); print(sheet.size)
