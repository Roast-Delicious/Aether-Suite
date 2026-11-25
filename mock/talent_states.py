# Talent node states, user's scheme (Nov 25 07:00) on their own Beast
# Mastery screenshot: spec icon gold on navy (C); maxed = gold tint + gold
# border; some points = blue border; then three options for the states
# with no points: "can take" (you have points to spend) vs "locked".
import numpy as np
from PIL import Image, ImageDraw, ImageFont
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74)
FD = '/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
def F(n, w='Regular'): return ImageFont.truetype(FD + w + '.ttf', n)
SRC = np.array(Image.open('/mnt/user-data/uploads/330e1911-image.png').convert('RGB').crop((60, 240, 680, 1060))).astype(float)
G = np.array(GOLD, float); NV = np.array(NAVY, float)

def lum(a): return (a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11) / 255
import cv2
def icon_at(cx, cy, r=23, clean=True):
    """Icon pixels from the screenshot, with Blizzard's point count (the
    yellow/green digit, bottom-right) painted out so ours can go there."""
    a = SRC[cy - r:cy + r, cx - r:cx + r].copy()
    if not clean: return a
    R, Gc, B = a[..., 0], a[..., 1], a[..., 2]
    m = (((R > 150) & (Gc > 120) & (B < 110)) | ((Gc > 150) & (R < 140) & (B < 140))).astype(np.uint8)
    yy, xx = np.mgrid[0:2 * r, 0:2 * r]; m[(xx < r * 1.2) | (yy < r * 0.9)] = 0
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    out = cv2.inpaint(a.astype(np.uint8)[..., ::-1], m * 255, 5, cv2.INPAINT_TELEA)[..., ::-1]
    return out.astype(float)

def tile(ic, border, fx=None, glow=None, dim=0.0, count=None, ccol=None, S=64):
    """Draw one node at S px: icon (46 px) inside a 3 px rounded border."""
    a = ic.copy()
    if fx == 'gold': a = lum(a)[..., None] * G * 1.05
    if fx == 'gray': a = lum(a)[..., None] * np.array([200, 200, 205.])
    if fx == 'navy': a = NV + lum(a)[..., None] * G * 1.15
    a = a * (1 - dim)
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if glow:
        for k in range(8, 0, -1):
            d.rounded_rectangle([8 - k - 4, 8 - k - 4, S - 9 + k + 4, S - 9 + k + 4], 10, outline=glow + (int(26 * (9 - k) / 8),), width=2)
    icn = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((S - 18, S - 18), Image.LANCZOS)
    im.paste(icn, (9, 9))
    d.rounded_rectangle([7, 7, S - 8, S - 8], 5, outline=border + (255,), width=3)
    if count:
        f = F(15, 'Bold'); d.text((S - 11, S - 10), count, font=f, fill=(0, 0, 0, 255), anchor='rb', stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((S - 11, S - 10), count, font=f, fill=ccol + (255,), anchor='rb')
    return im

# icons from the screenshot (colored ones, so "can take" shows real art)
BOW = icon_at(445, 455); CLAW = icon_at(445, 545); LION = icon_at(175, 365); BEAST = icon_at(355, 365)
FIST = icon_at(265, 275); LOCK = icon_at(265, 275); WOLF = icon_at(175, 545)

OPTS = [
    ("1A  As Blizzard does it",
     dict(can=dict(border=(150, 152, 160), glow=(34, 230, 80)), none=dict(border=(120, 122, 130), fx='gray'),
          lock=dict(border=(70, 72, 80), fx='gray', dim=0.5))),
    ("1B  Light gray frame, locked dimmed  (recommended)",
     dict(can=dict(border=(210, 214, 222), glow=BLUE), none=dict(border=(150, 154, 164), fx='gray', dim=0.15),
          lock=dict(border=(60, 64, 74), fx='gray', dim=0.62))),
    ("1C  Blue-gray frame, locked dark navy",
     dict(can=dict(border=(140, 175, 215), glow=BLUE), none=dict(border=(90, 110, 140), fx='gray', dim=0.2),
          lock=dict(border=(40, 52, 72), fx='navy', dim=0.65))),
]
ROWS = [("can", "Can take\n(points to spend)", BOW), ("none", "Not taken\n(no points left)", LION), ("lock", "Locked\n(needs another\ntalent first)", LOCK)]

W, H = 1180, 820
sheet = Image.new('RGB', (W, H), (16, 18, 24)); d = ImageDraw.Draw(sheet)
d.text((24, 18), "Talent states: your scheme, plus options for 1", font=F(28, 'SemiBold'), fill=GOLD)
# your scheme row
d.text((24, 74), "Your scheme", font=F(20, 'SemiBold'), fill=(235, 238, 245))
x = 24
spec = icon_at(208, 68, 21, clean=False)
for img, cap in ((tile(spec, BLUE, fx='navy', S=96), "Spec icon\ngold on navy"),
                 (tile(CLAW, GOLD, fx='gold', count="5", ccol=GOLD, S=96), "Maxed\ngold tint + gold frame"),
                 (tile(BEAST, BLUE, count="3", ccol=BLUE, S=96), "Some points\nblue frame"),
                 (tile(FIST, (130, 132, 140), fx='gray', S=96), "Unavailable\ngray (as is)")):
    sheet.paste(img, (x, 104), img)
    for i, t in enumerate(cap.split("\n")): d.text((x + 48, 206 + i * 20), t, font=F(15), fill=(170, 176, 188), anchor='ma')
    x += 190
d.line([(24, 270), (W - 24, 270)], fill=(40, 60, 90))
# options grid: rows = states, cols = options
d.text((24, 286), "Option 1: the three no-points states", font=F(20, 'SemiBold'), fill=(235, 238, 245))
cx0 = 230
for j, (name, o) in enumerate(OPTS):
    d.text((cx0 + j * 315 + 128, 330), name.split("  ")[0], font=F(22, 'SemiBold'), fill=GOLD, anchor='ma')
    sub = name.split("  ", 1)[1]
    d.text((cx0 + j * 315 + 128, 360), sub, font=F(14), fill=(170, 176, 188), anchor='ma')
for i, (key, cap, ic) in enumerate(ROWS):
    y = 400 + i * 135
    for k, t in enumerate(cap.split("\n")): d.text((24, y + 30 + k * 22), t, font=F(17), fill=(235, 238, 245))
    for j, (name, o) in enumerate(OPTS):
        big = tile(ic, S=112, **o[key]); small = tile(ic, S=64, **o[key])
        bx = cx0 + j * 315 + 40
        sheet.paste(big, (bx, y), big); sheet.paste(small, (bx + 140, y + 24), small)
d.text((W - 24, H - 20), "big = 2x zoom, small = game size", font=F(14), fill=(120, 126, 138), anchor='rb')
sheet.save('/home/claude/aether-repo/mock/out_talent_states.png'); print(sheet.size)
