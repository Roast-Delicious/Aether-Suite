# Renders AetherSkins' minimap from the baked textures at the positions and
# sizes AetherSkins.lua uses, on the user's screenshot (the mockup's minimap).
import sys; sys.path.insert(0, '/home/claude/mock')
from PIL import Image, ImageDraw
import numpy as np, skin_minimap as MM
MED = '/home/claude/brand/AetherSkins/Media/'
def tga(n): return Image.open(MED + n + '.tga').convert('RGBA')
def tint(im, c):
    a = np.array(im).astype(np.float32); a[..., :3] *= np.array(c, np.float32)[None, None, :]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))
K, R = 1.2821, MM.RM
base = Image.fromarray(MM.CLEAN.copy()); base.paste(Image.fromarray(MM.A), (0, 0), Image.fromarray(MM.disk))
im = base.convert('RGBA'); cx, cy = MM.CX, MM.CY
def put(img, x, y, size, rot=0):
    s = int(round(size)); t = img.resize((s, s), Image.LANCZOS)
    if rot: t = t.rotate(rot, resample=Image.BICUBIC)
    im.alpha_composite(t, (int(round(x - s / 2)), int(round(y - s / 2))))
night = len(sys.argv) > 1 and sys.argv[1] == 'night'
put(tga('ring_plain'), cx, cy, 2 * K * R); put(tga('ring_night' if night else 'ring_day'), cx, cy, 2 * K * R)
for dx, dy, rot, name in ((0, 1, 0, 'up'), (1, 0, -90, 'right'), (0, -1, 180, 'down'), (-1, 0, 90, 'left')):
    x, y = cx + dx * 1.094 * R, cy - dy * 1.094 * R
    put(tint(tga('win_chev_dark'), (0.04, 0.045, 0.055)), x, y, 0.343 * R, rot)
    put(tga('chev3d_' + name), x, y, 0.343 * R)
sx, sy = cx + 0.718 * R, cy - 0.735 * R
put(tga('btn_disc'), sx, sy, 0.29 * R)
put(tint(tga('ico_moon' if night else 'ico_sun'), (0.88, 0.91, 0.96) if night else (1, 0.69, 0)), sx, sy, 0.29 * R * 0.75)
# layout 3 (AetherSkins 1.1.0): magnifier on the ring across from the sun,
# coordinates pill just under the bottom chevron, zone + clock pill under it
mx, my = cx - 0.718 * R, cy - 0.735 * R
put(tga('btn_disc'), mx, my, 0.29 * R)
put(tint(tga('ico_track'), (0.3, 0.65, 1)), mx, my, 0.29 * R * 0.68)
from PIL import ImageFont
U = R / 99.0                                    # px per UI unit (Forever's minimap is 198 wide)
FONT = '/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
def pill(x0, y0, w, h, parts):
    S = 4; lay = Image.new('RGBA', (im.width * 1, im.height), (0, 0, 0, 0))
    big = Image.new('RGBA', (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * S, h * S], radius=h * S / 2, fill=(77, 166, 255, 255))
    d.rounded_rectangle([1.2 * S * U, 1.2 * S * U, w * S - 1.2 * S * U, h * S - 1.2 * S * U], radius=h * S / 2 - 1.2 * S * U, fill=(19, 40, 74, 240))
    big = big.resize((big.width // S, big.height // S), Image.LANCZOS); im.alpha_composite(big, (int(x0), int(y0)))
    d = ImageDraw.Draw(im)
    for text, col, weight, x in parts:
        f = ImageFont.truetype(FONT + weight + '.ttf', int(12 * U)); d.text((x, y0 + h / 2), text, font=f, fill=col, anchor='lm')
d = ImageDraw.Draw(im)
f12 = ImageFont.truetype(FONT + 'Bold.ttf', int(12 * U))
ctext = '32.9, 20.2'; tw = d.textlength(ctext, font=f12) / U
ch = 20; cw = tw + 12 + ch / 2
ctop = cy + R + (0.223 * 99 + 2) * U
pill(cx - cw * U / 2, ctop, cw * U, ch * U, [(ctext, (235, 238, 245), 'Bold', cx - tw * U / 2)])
zt, ct = 'Stranglethorn Vale', '15:00'
fz = ImageFont.truetype(FONT + 'SemiBold.ttf', int(12 * U))
zw = d.textlength(zt, font=fz) / U; cwid = d.textlength(ct, font=fz) / U
W = 10 + zw + 10 + 12 + cwid; ztop = ctop + (ch + 5) * U
pill(cx - W * U / 2, ztop, W * U, 20 * U, [(zt, (255, 176, 0), 'SemiBold', cx - W * U / 2 + 10 * U), (ct, (235, 238, 245), 'SemiBold', cx + W * U / 2 - (10 + cwid) * U)])
MM.Y1 = max(MM.Y1, int(ztop + 24 * U) + 6)
im.crop((MM.X0, MM.Y0, MM.X1, MM.Y1)).convert('RGB').save('/tmp/sk/ingame_%s.png' % ('night' if night else 'day'))
print('ok')
