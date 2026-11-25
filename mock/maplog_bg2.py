# Map quest log background: navy instead of near-black (user, Nov 25).
import numpy as np, cv2
from PIL import Image, ImageDraw
from talent_details import F
SRC = Image.open('/mnt/user-data/uploads/ccef87ac-image.png').convert('RGB')
x0, y0, x1, y1 = 1074, 112, 1532, 828
def recolor(kind):
    a = np.array(SRC).astype(float); reg = a[y0:y1, x0:x1]
    lum = reg.mean(axis=2)
    h, w = lum.shape
    if kind == 'page':
        yy, xx = np.mgrid[0:h, 0:w]
        g = (1 - 0.35 * yy / h) * (1 - 0.22 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2))
        lo, hi = np.array([6, 12, 24.]), np.array([22, 42, 76.]); bg = lo + g[..., None] * (hi - lo)
    elif kind == 'blue':
        bg = np.zeros((h, w, 3)) + np.array([77, 166, 255.])
    elif kind == 'blue45':
        bg = np.zeros((h, w, 3)) + np.array([77, 166, 255.]) * 0.45
    else:
        bg = np.zeros((h, w, 3)) + np.array([14, 28, 52.])
    k = np.clip((40 - lum) / 25, 0, 1)[..., None]      # only the near-black background
    reg[:] = reg * (1 - k) + bg * k
    out = a.copy(); out[y0:y1, x0:x1] = reg
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).crop((1060, 60, 1560, 840))
A = SRC.crop((1060, 60, 1560, 840)); B = recolor('blue'); C = recolor('blue45')
W = A.width * 3 + 80
sh = Image.new('RGB', (W, A.height + 60), (16, 18, 24)); d = ImageDraw.Draw(sh)
for i, (im, t) in enumerate(((A, "Now"), (B, "A  Aether blue"), (C, "B  Aether blue, darker  (my pick)"))):
    x = 20 + i * (A.width + 20); d.text((x, 14), t, font=F(20, 'SemiBold'), fill=(255, 176, 0)); sh.paste(im, (x, 48))
sh.save('out_maplog_bg2.png'); print(sh.size)
