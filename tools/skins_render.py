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
im.crop((MM.X0, MM.Y0, MM.X1, MM.Y1)).convert('RGB').save('/tmp/sk/ingame_%s.png' % ('night' if night else 'day'))
print('ok')
