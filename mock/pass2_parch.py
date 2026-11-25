# Quest parchment: recolored or new art (user, Nov 25 07:43), on the user's
# own video frame. In game the text keeps the quest fonts, recolored.
#  1 Light blue paper: the parchment's grain, tinted pale blue; navy text
#  2 Navy paper: the parchment's grain, tinted deep navy; light text, gold headers
#  3 New Aether page: our own navy art (soft gradient, fine grain, thin
#    blue edge); light text, gold headers
import numpy as np, cv2
from PIL import Image, ImageDraw
import pass2_quest as Q
from pass2_quest import F
SRC = Q.SRC
a = np.array(SRC.convert('RGB')).astype(float)
x0, y0, x1, y1 = 29, 124, 437, 676
reg = a[y0:y1, x0:x1].astype(np.uint8)
lum8 = cv2.cvtColor(reg, cv2.COLOR_RGB2GRAY)
textm = (lum8 < 110).astype(np.uint8)
textm = cv2.dilate(textm, np.ones((5, 5), np.uint8))
textm[452 - y0:520 - y0, :] = 1                       # reward plaques too
clean = cv2.inpaint(lum8, textm * 255, 7, cv2.INPAINT_TELEA).astype(float) / 255
clean = (clean - clean.min()) / max(clean.max() - clean.min(), 1e-3)
h, w = clean.shape

def page(kind):
    if kind == 1: lo, hi = np.array([96, 130, 180.]), np.array([205, 225, 246.]); g = clean
    elif kind == 2: lo, hi = np.array([8, 16, 32.]), np.array([44, 74, 124.]); g = clean
    else:
        yy, xx = np.mgrid[0:h, 0:w]
        g = (1 - 0.35 * yy / h) * (1 - 0.22 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2))
        rng = np.random.default_rng(3)
        g = g + cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.8) * 0.03
        lo, hi = np.array([6, 12, 24.]), np.array([22, 42, 76.])
    return lo + g[..., None] * (hi - lo)

def build(kind):
    out = a.copy(); out[y0:y1, x0:x1] = page(kind)
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
    if kind == 3:
        d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], 6, outline=(60, 110, 175, 230), width=1)
    d.rectangle([438, 125, 466, 672], fill=(12, 14, 19, 255))
    body_c = (14, 26, 48) if kind == 1 else (232, 236, 244)
    head_c = (14, 26, 48) if kind == 1 else Q.GOLD
    dim_c = (40, 60, 95) if kind == 1 else (170, 176, 188)
    line_c = (40, 80, 140, 200) if kind == 1 else Q.BLUE + (170,)
    x = 46; y = 140
    d.text((x, y + 14), "Alliance Relations", font=F(22, 'SemiBold'), fill=head_c + (255,), anchor='lm')
    d.line([(x, y + 32), (424, y + 32)], fill=line_c, width=1)
    body = ["You have returned from Desolace more", "than successful, Jay. Thank you.", "",
            "Thank you for your efforts, your time, and", "your understanding to my plea. Thrall",
            "understands and desires peace between", "the Horde and Alliance, and by taking",
            "measures to insure our appearance is", "acceptable, we will not provoke any further",
            "threats of unnecessary violence.", "", "I am indebted to you."]
    yy = y + 46
    for line in body:
        if line: d.text((x, yy), line, font=F(16), fill=body_c + (255,))
        yy += 20
    d.text((x, 452), "Rewards", font=F(20, 'SemiBold'), fill=head_c + (255,), anchor='lm')
    d.line([(x, 466), (424, 466)], fill=line_c, width=1)
    d.text((x, 482), "Choose your reward:", font=F(16), fill=dim_c + (255,), anchor='lm')
    Q.tiles(im, d, True, dy=40)
    d.text((x, 574), "You will also receive:", font=F(16), fill=dim_c + (255,), anchor='lm')
    d.text((x, 600), "Experience:", font=F(16), fill=body_c + (255,), anchor='lm')
    d.text((x + 120, 600), "2,650", font=F(16, 'SemiBold'), fill=((14, 26, 48) if kind == 1 else Q.GOLD) + (255,), anchor='lm')
    Q.scrollbar(d)
    return im

labs = [Q.lab(build(1), "1  Light blue paper", "Parchment's grain, tinted pale blue; navy text"),
        Q.lab(build(2), "2  Navy paper", "Parchment's grain, tinted navy; light text"),
        Q.lab(build(3), "3  New Aether page  (my pick)", "Our own navy art; light text, gold headers")]
W = sum(l.width for l in labs) + 40
out = Image.new('RGBA', (W, labs[0].height + 20), (16, 18, 24, 255)); xx = 10
for l in labs: out.alpha_composite(l, (xx, 10)); xx += l.width + 10
out.convert('RGB').save('/home/claude/aether-repo/mock/out_parch.png'); print(out.size)
