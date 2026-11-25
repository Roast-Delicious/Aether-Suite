# Friends list: hover vs selected (user, Nov 25 test: window too dark, hover
# and selection look the same). Cards a bit lighter in both options.
from PIL import Image, ImageDraw
from talent_details import F
GOLD = (255, 176, 0); BLUE = (77, 166, 255); TEXT = (235, 238, 245); DIM = (150, 156, 170)
BG = (10, 14, 22)
def card(d, x, y, w, h, state, opt):
    base = (30, 56, 98) if opt != 'now' else (16, 28, 48)
    off = state == 'offline'
    fill = base if not off else ((22, 34, 54) if opt != 'now' else (12, 18, 30))
    if state == 'hover':
        fill = tuple(min(255, int(c + (BLUE[i] - c) * (0.18 if opt != 'now' else 0.3))) for i, c in enumerate(base))
    if state == 'selected':
        fill = tuple(min(255, int(c + (BLUE[i] - c) * 0.3)) for i, c in enumerate(base)) if opt != 'now' else \
               tuple(min(255, int(c + (BLUE[i] - c) * 0.3)) for i, c in enumerate(base))
    d.rounded_rectangle([x, y, x + w, y + h], 4, fill=fill)
    if state == 'selected' and opt == 'A':
        d.rectangle([x, y + 4, x + 4, y + h - 4], fill=GOLD)
        d.rounded_rectangle([x, y, x + w, y + h], 4, outline=BLUE, width=2)
    if state == 'selected' and opt == 'B':
        d.rounded_rectangle([x, y, x + w, y + h], 4, outline=GOLD, width=2)
    if state == 'hover' and opt != 'now':
        d.rounded_rectangle([x, y, x + w, y + h], 4, outline=(77, 166, 255), width=1)
    name = {'normal': "Itdrtyndere", 'hover': "Itdrtyndere", 'selected': "Itdrtyndere", 'offline': "FunkyMonk"}[state]
    d.text((x + 14, y + 10), name, font=F(17, 'SemiBold'), fill=TEXT if not off else DIM)
    d.text((x + 14, y + 34), "In App" if not off else "Offline", font=F(14), fill=BLUE if not off else DIM)
OPTS = [('now', "Now"), ('A', "A  Selected: brighter, gold notch  (my pick)"), ('B', "B  Selected: gold outline")]
W, H = 1180, 450
im = Image.new('RGB', (W, H), (16, 18, 24)); d = ImageDraw.Draw(im)
for i, (o, t) in enumerate(OPTS):
    x0 = 20 + i * 390
    d.text((x0, 16), t, font=F(18, 'SemiBold'), fill=GOLD)
    d.rectangle([x0, 50, x0 + 360, 420], fill=BG, outline=(40, 70, 115))
    for j, (st, lab) in enumerate((('normal', "normal"), ('hover', "mouse over"), ('selected', "selected"), ('offline', "offline"))):
        y = 66 + j * 88
        card(d, x0 + 12, y, 336, 60, st, o)
        d.text((x0 + 348, y + 66), lab, font=F(12), fill=DIM, anchor='ra')
im.save('out_friends_sel.png'); print(im.size)
