# 1) Scroll and page arrows as our 3D gold chevron accents: gold when you
#    can click, gray when you can't; page arrows inside a navy square.
# 2) Vendor buttons gray when there's nothing to repair.
import numpy as np
from PIL import Image, ImageDraw
from talent_details import F
import vendor as VD
MED = '/home/claude/aether-repo/AetherSkins/Media/'
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74); DIM = (170, 176, 188)
def chev(name, size, gray=False):
    im = Image.open(MED + 'chev3d_' + name + '.tga').convert('RGBA').resize((size, size), Image.LANCZOS)
    if gray:
        a = np.array(im).astype(float); l = a[..., :3].mean(axis=2, keepdims=True)
        a[..., :3] = l * np.array([0.52, 0.55, 0.62]) * 1.1; im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im
def square(d, x, y, s, on):
    d.rounded_rectangle([x, y, x + s, y + s], 5, fill=NAVY + (255,), outline=(BLUE if on else (60, 70, 90)) + (255,), width=2)
W, H = 1180, 600
im = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(im)
d.text((20, 16), "1  Arrows as our gold chevron accents (2x game size)", font=F(22, 'SemiBold'), fill=GOLD)
# scroll bar now vs new
for i, (title, new) in enumerate((("Scroll bar now", False), ("Scroll bar, new", True))):
    x = 40 + i * 200; d.text((x, 60), title, font=F(16), fill=DIM)
    d.rounded_rectangle([x + 40, 120, x + 52, 400], 6, fill=(26, 46, 82, 255))
    d.rounded_rectangle([x + 40, 140, x + 52, 260], 6, fill=GOLD + (255,))
    if new:
        im.alpha_composite(chev('up', 40, gray=True), (x + 26, 76)); im.alpha_composite(chev('down', 40), (x + 26, 404))
        d.text((x + 70, 92), "top: gray", font=F(13), fill=DIM); d.text((x + 70, 420), "can scroll", font=F(13), fill=DIM)
    else:
        d.polygon([(x + 38, 104), (x + 54, 104), (x + 46, 92)], fill=(200, 205, 215, 255))
        d.polygon([(x + 38, 416), (x + 54, 416), (x + 46, 428)], fill=(200, 205, 215, 255))
# page buttons
x0 = 480
d.text((x0, 60), "Page buttons (vendor, Spellbook): now", font=F(16), fill=DIM)
for j, on in enumerate((False, True)):
    xx = x0 + j * 90; square(d, xx, 96, 64, on)
    c = (200, 205, 215) if on else (90, 96, 108)
    if j == 0: d.polygon([(xx + 40, 110), (xx + 40, 146), (xx + 20, 128)], fill=c + (255,))
    else: d.polygon([(xx + 24, 110), (xx + 24, 146), (xx + 44, 128)], fill=c + (255,))
d.text((x0, 200), "new: gold chevron when you can click, gray when you can't", font=F(16), fill=DIM)
for j, on in enumerate((False, True)):
    xx = x0 + j * 90; square(d, xx, 236, 64, on)
    im.alpha_composite(chev('left' if j == 0 else 'right', 52, gray=not on), (xx + 6, 242))
d.text((x0, 316), "Page 1 of 3  (first page: back arrow gray)", font=F(15), fill=DIM)
# vendor
d.text((20, 440), "2  Vendor buttons: gold when usable, gray when there's nothing to repair", font=F(22, 'SemiBold'), fill=GOLD)
for j, (k, n, on) in enumerate((('repairall', "Repair all", False), ('repair', "Repair item", False), ('guild', "Guild repair", False), ('junk', "Sell junk", True))):
    xx = 40 + j * 160; s = 84
    d.rounded_rectangle([xx, 480, xx + s, 480 + s], 8, fill=NAVY + (255,), outline=BLUE + (255,), width=2)
    g = VD.glyph_img(k, 62, (GOLD if on else (115, 120, 133)) + (255,))
    a = np.array(g); m = (a[..., 0] < 40) & (a[..., 2] > 60); a[m, 3] = 0; g = Image.fromarray(a)
    im.alpha_composite(g, (xx + 11, 491))
    d.text((xx + s / 2, 572), n + ("" if on else " (gray)"), font=F(14), fill=DIM, anchor='ma')
im.convert('RGB').save('out_arrows_vendor.png'); print(im.size)
