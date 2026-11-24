# Mockup on the user's real screenshot: the text in the blue Aether windows (Hub,
# Pack) redrawn in Fira Sans with a soft drop shadow, at the same spots and colors.
# Each element: a rough box in screen px, the string, and its style. The original
# text inside the box is found by color, erased (inpainted), and redrawn.
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
WEIGHT = sys.argv[3] if len(sys.argv) > 3 else 'Medium'
FD = '/usr/share/fonts/truetype/google-fonts/ofl/firasans/FiraSans-%s.ttf'
im = np.array(Image.open(SRC).convert('RGB'))
H, W, _ = im.shape

# (x0, y0, x1, y1, text, group); one size per group, measured from the original
E = [
    (64, 70, 188, 96, "AETHER HUB", "title"), (192, 70, 268, 96, "v1.13.2", "title"),
    (72, 117, 152, 139, "GENERAL", "caps"), (70, 297, 148, 319, "ADDONS", "caps"),
    (78, 145, 218, 171, "Your character", "body"), (258, 145, 286, 171, "34", "small"),
    (78, 183, 196, 209, "Appearance", "body"), (78, 221, 146, 247, "Fading", "body"),
    (78, 259, 148, 285, "Layout", "body"),
    (77, 326, 200, 352, "AetherMeter", "body"), (222, 328, 282, 350, "v1.13.6", "small"),
    (77, 364, 182, 390, "AetherBars", "body"), (222, 366, 282, 388, "v1.14.0", "small"),
    (77, 401, 208, 427, "AetherCoords", "body"), (228, 403, 282, 425, "v1.3.6", "small"),
    (320, 112, 408, 145, "Layout", "page"), (415, 118, 695, 142, "Moving, docking and lining things up", "sub"),
    (320, 158, 440, 184, "Move things", "head"),
    (324, 194, 1066, 213, "Unlock to Move unlocks your unit frames, the meter and the XP bar at once: drag", "body"),
    (324, 213, 1066, 231, "them, then click Lock (or Done on any of them). Action bars move in Blizzard's Edit", "body"),
    (324, 231, 392, 249, "Mode.", "body"),
    (342, 264, 494, 290, "Unlock to Move", "button"), (560, 264, 610, 290, "Lock", "button"), (676, 264, 832, 290, "Open Edit Mode", "button"),
    (342, 309, 486, 335, "Line Up Frames", "button"), (525, 309, 772, 335, "Line Up and Center Frames", "button"),
    (320, 346, 542, 372, "Around your action bars", "head"),
    (356, 388, 736, 414, "Chat fits the space to the left of your bars", "body"),
    (1177, 246, 1308, 270, "AETHER PACK", "title"),
    (1185, 286, 1242, 306, "Search", "sub"),
    (1179, 330, 1246, 354, "Ammo", "head"), (1251, 330, 1278, 354, "14", "head"),
    (1179, 486, 1296, 511, "Quest items", "head"), (1299, 486, 1326, 511, "12", "head"),
]

def text_mask(x0, y0, x1, y1):
    box = im[y0:y1, x0:x1].astype(int)
    border = np.concatenate([box[0], box[-1], box[:, 0], box[:, -1]])
    bg = np.median(border, 0)
    diff = np.abs(box - bg).sum(2)
    m = diff > 70
    return m, bg

out = im.copy()
mask_all = np.zeros((H, W), np.uint8)
draws = []
for (x0, y0, x1, y1, s, wt) in E:  # wt = group
    m, bg = text_mask(x0, y0, x1, y1)
    ys, xs = np.where(m)
    if len(xs) == 0: continue
    box = im[y0:y1, x0:x1].astype(int)
    lum = box.sum(2)
    vals = box[m]
    # text color: the brightest third of the text pixels (skip the dark shadow)
    l = vals.sum(1); col = np.median(vals[l >= np.percentile(l, 66)], 0)
    tx0, tx1, ty0, ty1 = xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0
    mm = np.zeros((H, W), np.uint8)
    mm[y0:y1, x0:x1][m] = 255
    mask_all |= cv2.dilate(mm, np.ones((5, 5), np.uint8))
    rows_ = m.sum(1); mx = rows_.max()
    base = y0 + max(i for i, v in enumerate(rows_) if v > 0.3 * mx) - 1      # minus the 1 px shadow
    top = y0 + min(i for i, v in enumerate(rows_) if v > 0)
    draws.append(((tx0 + tx1) / 2 if wt == "button" else tx0, base, base - top + 1, s, wt, tuple(int(c) for c in col)))
out = cv2.inpaint(out, mask_all, 3, cv2.INPAINT_TELEA)

SS = 4
big = Image.fromarray(out).resize((W * SS, H * SS), Image.BICUBIC).convert('RGBA')
layer = Image.new('RGBA', big.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
groups = {}
for (_, _, cap, s_, g, _) in draws:
    if not any(c in s_ for c in "ldkbhtf"):  # caps/digit height, not ascenders
        groups.setdefault(g, []).append(cap)
for (_, _, cap, s_, g, _) in draws:
    groups.setdefault(g, []).append(cap)
groups['button'] = groups.get('body', []) + groups.get('button', [])
CAP = {g: float(np.median(v[:max(1, len(v))])) for g, v in groups.items()}
print("cap heights px:", CAP)
for (tx0, base, cap, s, g, col) in draws:
    size = CAP[g] / 0.689          # Fira Sans cap height is 0.689 em
    wt = 'SemiBold' if g in ('page', 'title', 'head', 'caps') else WEIGHT
    f = ImageFont.truetype(FD % wt, int(round(size * SS)))
    px, py = tx0 * SS, (base + 1) * SS
    an = 'ms' if g == 'button' else 'ls'
    d.text((px + 1.4 * SS, py + 1.4 * SS), s, font=f, fill=(0, 0, 0, 200), anchor=an)     # soft shadow, 1 unit
    d.text((px, py), s, font=f, fill=col + (255,), anchor=an)
big.alpha_composite(layer)
new = big.resize((W, H), Image.LANCZOS).convert('RGB')

orig = Image.fromarray(im)
regions = [(50, 60, 1120, 430), (1165, 236, 1780, 560)]
pad = 16
tiles = []
for (a, b, c, e) in regions:
    tiles.append((orig.crop((a, b, c, e)), new.crop((a, b, c, e))))
cw = pad + max(t[0].width for t in tiles) * 1 + pad
rows_h = sum(t[0].height * 2 + 60 for t in tiles)
canvas = Image.new('RGB', (cw, rows_h + pad), (18, 20, 26))
cd = ImageDraw.Draw(canvas); lf = ImageFont.truetype(FD % 'Regular', 20)
y = 10
for i, (o, n) in enumerate(tiles):
    cd.text((pad, y), "Now (in game, Friz Quadrata)", fill=(255, 209, 0), font=lf); y += 28
    canvas.paste(o, (pad, y)); y += o.height + 8
    cd.text((pad, y), "Aether style (Fira Sans %s + soft shadow)" % WEIGHT, fill=(255, 209, 0), font=lf); y += 28
    canvas.paste(n, (pad, y)); y += n.height + 14
canvas = canvas.crop((0, 0, cw, y))
canvas.save(OUT)
print(canvas.size, len(draws))
