# Second-pass mockup 5: Progress Track (LegacySystemFrame, 920x575 units,
# shown cropped) and a vendor (MerchantFrame, 336x444 units), game size.
from skins_lib import *
from pass2_rep import backdrop, sidetab, icon
from pass2_spells import spell_icon
from PIL import Image

def rcard(c, box, lvl, name, earned, hue):
    x0, y0, x1, y1 = c.P(*box)
    L, d = c.layer()
    d.rounded_rectangle([x0, y0, x1, y1], u(8), fill=(22, 46, 84, 245) if earned else (14, 22, 38, 235),
                        outline=(BLUE + (255,)) if earned else (50, 70, 100, 230), width=SS)
    c.over(L)
    cx = (box[0] + box[2]) / 2
    # level badge: gold when earned, navy otherwise
    by = box[1] + 4
    c.d.rounded_rectangle(c.P(cx - 26, by - 18, cx + 26, by + 18), u(5), fill=(GOLD if earned else NAVY) + (255,),
                          outline=(GOLD if earned else BLUE) + (255,), width=SS)
    c.text((cx, by), str(lvl), 18, (10, 14, 22) if earned else WHITE, 'Bold', 'mm')
    iy = box[1] + 60
    spell_icon(c, (cx - 46, iy, cx + 46, iy + 92), hue)
    c.d.rounded_rectangle(c.P(cx - 50, iy - 4, cx + 50, iy + 96), u(5), outline=BLUE + (255,), width=2 * SS)
    if not earned:
        L, d = c.layer(); d.rectangle(c.P(cx - 46, iy, cx + 46, iy + 92), fill=(0, 0, 0, 110)); c.over(L)
    else:
        c.d.ellipse(c.P(cx + 30, iy + 74, cx + 58, iy + 102), fill=NAVY + (255,), outline=GOLD + (255,), width=SS)
        c.d.line(c.P(cx + 37, iy + 88, cx + 42, iy + 93), fill=GOLD + (255,), width=3 * SS)
        c.d.line(c.P(cx + 42, iy + 93, cx + 51, iy + 82), fill=GOLD + (255,), width=3 * SS)
    for i, t in enumerate(name): c.text((cx, box[1] + 190 + i * 22), t, 16, WHITE if earned else DIM, 'SemiBold', 'mm')

def track():
    W, H = 1200, 700
    c = Canvas(backdrop(W, H))
    box = (40, 46, 40 + 1080, 46 + 600)
    c.window(box, "Progress Track", chevrons='tbl')
    c.crest((86, 92), 40); icon(c, 'skill', 86, 92, 22, GOLD)
    c.close(box[2] - 26, box[1] + 19)
    for i, (g, s) in enumerate([('stats', True), ('pvp', False), ('skill', False)]):
        sidetab(c, box[2] + 4, box[1] + 70 + i * 92, g, selected=s)
    c.text((box[0] + 150, box[1] + 90), "12", 40, GOLD, 'Bold', 'lm')
    c.text((box[0] + 200, box[1] + 96), "Progress points", 17, WHITE, 'Regular', 'lm')
    c.bar((box[0] + 40, box[1] + 140, box[2] - 40, box[1] + 158), .34, GOLD, "", pill=True)
    cards = [(5, ["Traveler's", "Satchel"], True, 1), (10, ["Swift", "Mount Whistle"], True, 2),
             (15, ["Hearthstone", "Cooldown"], False, 3), (20, ["Tabard of", "the Long Road"], False, 4)]
    for i, (lv, nm, e, h) in enumerate(cards):
        x = box[0] + 60 + i * 250
        rcard(c, (x, box[1] + 210, x + 220, box[1] + 480), lv, nm, e, h)
    for k, x in ((0, box[0] + 18), (1, box[2] - 52)):
        c.d.rounded_rectangle(c.P(x, box[1] + 320, x + 34, box[1] + 370), u(4), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
        m = x + 17; my = box[1] + 345
        pts = [(m + 4, my - 9), (m - 5, my), (m + 4, my + 9)] if k == 0 else [(m - 4, my - 9), (m + 5, my), (m - 4, my + 9)]
        c.d.line([tuple(c.P(*p)) for p in pts], fill=GOLD + (255,), width=3 * SS, joint='curve')
    return c.done()

def coins(c, x, y, g, s, cp):
    for val, col in ((g, GOLD), (s, (200, 205, 215)), (cp, (205, 125, 70))):
        if val is None: continue
        c.text((x, y), str(val), 15, WHITE, 'Regular', 'rm')
        c.d.ellipse(c.P(x + 3, y - 6, x + 15, y + 6), fill=col + (255,)); x += 44

def vendor():
    W, H = 640, 780
    c = Canvas(backdrop(W, H))
    box = (40, 40, 40 + 521, 40 + 688)
    c.window(box, "Innkeeper Sikewa", chevrons='tbrl')
    c.crest((86, 86), 40); icon(c, 'char', 86, 90, 20, GOLD)
    c.close(box[2] - 26, box[1] + 19)
    items = [("Moonberry Juice", 1, 1, None, 1), ("Sweet Nectar", 2, None, 40, None), ("Ice Cold Milk", 3, None, 25, None),
             ("Haunch of Meat", 4, None, 25, None), ("Mutton Chop", 0, None, 4, 50), ("Wild Hog Shank", 1, None, 25, None),
             ("Refreshing Spring Water", 2, None, None, 25), ("Melon Juice", 3, None, 5, None)]
    for i, (n, h, g, s, cp) in enumerate(items):
        col, row = i % 2, i // 2
        x, y = box[0] + 16 + col * 248, box[1] + 100 + row * 96
        L, d = c.layer(); d.rounded_rectangle(c.P(x, y, x + 236, y + 84), u(6), fill=NAVY + (200,), outline=(60, 110, 175, 220), width=SS); c.over(L)
        spell_icon(c, (x + 10, y + 13, x + 68, y + 71), h)
        c.d.rounded_rectangle(c.P(x + 8, y + 11, x + 70, y + 73), u(3), outline=BLUE + (255,), width=2 * SS)
        words = n.split(); l1 = " ".join(words[:2]); l2 = " ".join(words[2:])
        c.text((x + 80, y + 22), l1, 15, WHITE, 'SemiBold', 'lm')
        if l2: c.text((x + 80, y + 40), l2, 15, WHITE, 'SemiBold', 'lm')
        coins(c, x + 120 if g else x + 120, y + 64, g, s, cp)
    # bottom: blue line, repair / junk buttons, money
    yb = box[3] - 120
    c.d.line(c.P(box[0] + 16, yb, box[2] - 16, yb), fill=BLUE + (160,), width=SS)
    for i, k in enumerate(("junk", "repair", "repair1")):
        bx = box[0] + 22 + i * 62
        c.d.rounded_rectangle(c.P(bx, yb + 16, bx + 52, yb + 68), u(5), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
        spell_icon(c, (bx + 8, yb + 24, bx + 44, yb + 60), 7 + i)
    c.d.rounded_rectangle(c.P(box[2] - 220, yb + 26, box[2] - 22, yb + 58), u(4), fill=(8, 12, 22, 255), outline=BLUE + (255,), width=SS)
    coins(c, box[2] - 190, yb + 42, 24, 17, 82)
    # tabs: Merchant / Buyback (already styled, shown for context)
    for i, t in enumerate(("Merchant", "Buyback")):
        tx = box[0] + 20 + i * 120; act = i == 0
        c.d.rounded_rectangle(c.P(tx, box[3] + 2, tx + 110, box[3] + 34), u(5), fill=NAVY + (255,), outline=(GOLD if act else BLUE) + (255,), width=SS)
        c.text((tx + 55, box[3] + 18), t, 15, GOLD if act else WHITE, 'SemiBold', 'mm')
    return c.done()

if __name__ == '__main__':
    a = label(track(), "5a  Progress Track (game size)")
    b = label(vendor(), "5b  Vendor (game size)")
    out = Image.new('RGB', (a.width, a.height + b.height), (16, 18, 24)); out.paste(a, (0, 0)); out.paste(b, (0, a.height))
    out.save('/home/claude/aether-repo/mock/out_p2_track.png'); print(out.size)
