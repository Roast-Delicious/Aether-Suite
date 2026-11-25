# Quest dialog (QuestFrame), on the user's own video frame (Nov 25 07:39):
#  A  keep the parchment, restyle the reward tiles and the scroll bar
#  B  navy page like the Spellbook: gold title and headers, light text,
#     navy reward tiles with blue icon frames  (recommended)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
GOLD = (255, 176, 0); BLUE = (77, 166, 255); NAVY = (19, 40, 74); WHITE = (235, 238, 245); DIM = (170, 176, 188)
FD = '/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
def F(n, w='Regular'): return ImageFont.truetype(FD + w + '.ttf', n)
SRC = Image.open('/tmp/v7/quest.png').convert('RGBA')
PAGE = (30, 122, 436, 676)          # the parchment area in the crop

def tiles(im, d, navy_text, dy=0):
    items = [((42, 458, 96, 512), "Gloves of", "Kapelan"), ((242, 458, 296, 512), "Swiftrunner", "Cape")]
    for (x0, y0, x1, y1), a, b in items:
        icon = SRC.crop((x0 + 2, y0 + 2, x1 - 2, y1 - 2)); y0 += dy; y1 += dy
        d.rounded_rectangle([x0 - 2, y0 - 2, x0 + 190, y1 + 2], 7, fill=NAVY + (235,), outline=(60, 110, 175, 255), width=1)
        im.alpha_composite(icon, (x0 + 2, y0 + 2))
        d.rounded_rectangle([x0, y0, x1, y1], 4, outline=BLUE + (255,), width=2)
        d.text((x1 + 8, y0 + 16), a, font=F(16, 'SemiBold'), fill=WHITE + (255,), anchor='lm')
        d.text((x1 + 8, y0 + 36), b, font=F(16, 'SemiBold'), fill=WHITE + (255,), anchor='lm')

def scrollbar(d, x=452, y0=140, y1=660):
    d.rounded_rectangle([x - 3, y0, x + 3, y1], 3, fill=(14, 28, 52, 255))
    d.polygon([(x - 6, y0 - 4), (x + 6, y0 - 4), (x, y0 - 12)], fill=BLUE + (255,))
    d.polygon([(x - 6, y1 + 4), (x + 6, y1 + 4), (x, y1 + 12)], fill=BLUE + (255,))

def variant(kind):
    im = SRC.copy(); d = ImageDraw.Draw(im)
    # cover the old scroll arrows column
    d.rectangle([438, 125, 466, 672], fill=(12, 14, 19, 255))
    if kind == 'A':
        # parchment stays; the brown plaques behind the rewards are replaced
        tiles(im, d, False)
    else:
        d.rounded_rectangle(PAGE, 6, fill=(12, 16, 26, 255), outline=(60, 110, 175, 200), width=1)
        x = 44; y = 140
        d.text((x, y + 14), "Alliance Relations", font=F(22, 'SemiBold'), fill=GOLD + (255,), anchor='lm')
        d.line([(x, y + 32), (420, y + 32)], fill=BLUE + (170,), width=1)
        body = ["You have returned from Desolace more", "than successful, Jay. Thank you.", "",
                "Thank you for your efforts, your time, and", "your understanding to my plea. Thrall",
                "understands and desires peace between", "the Horde and Alliance, and by taking",
                "measures to insure our appearance is", "acceptable, we will not provoke any further",
                "threats of unnecessary violence.", "", "I am indebted to you."]
        yy = y + 46
        for line in body:
            if line: d.text((x, yy), line, font=F(16), fill=WHITE + (255,))
            yy += 20
        d.text((x, 452), "Rewards", font=F(20, 'SemiBold'), fill=GOLD + (255,), anchor='lm')
        d.line([(x, 466), (420, 466)], fill=BLUE + (170,), width=1)
        d.text((x, 482), "Choose your reward:", font=F(16), fill=DIM + (255,), anchor='lm')
        tiles(im, d, True, dy=40)
        d.text((x, 574), "You will also receive:", font=F(16), fill=DIM + (255,), anchor='lm')
        d.text((x, 600), "Experience:", font=F(16), fill=WHITE + (255,), anchor='lm')
        d.text((x + 120, 600), "2,650", font=F(16, 'SemiBold'), fill=GOLD + (255,), anchor='lm')
    scrollbar(d)
    return im

def lab(im, t, sub):
    out = Image.new('RGBA', (im.width, im.height + 64), (16, 18, 24, 255)); d = ImageDraw.Draw(out)
    d.text((10, 8), t, font=F(22, 'SemiBold'), fill=GOLD + (255,)); d.text((10, 38), sub, font=F(15), fill=DIM + (255,))
    out.alpha_composite(im, (0, 64)); return out

a = lab(variant('A'), "A  Keep the parchment", "Reward tiles navy, scroll bar ours")
b = lab(variant('B'), "B  Navy page  (my pick)", "Like the Spellbook: gold headers, light text")
sheet = Image.new('RGBA', (a.width + b.width + 30, a.height + 20), (16, 18, 24, 255))
sheet.alpha_composite(a, (10, 10)); sheet.alpha_composite(b, (a.width + 20, 10))
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_quest.png'); print(sheet.size)
