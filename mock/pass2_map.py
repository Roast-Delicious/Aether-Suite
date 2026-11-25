# Second-pass mockup 4: World Map + quest log, on the user's own screenshot
# (Nov 25 06:41, Desolace). The map art, pins and fog stay; the chrome, the
# breadcrumb bar and the quest log get the Aether look.
from skins_lib import *
from pass2_friends import searchbox
from PIL import Image

SHOT = Image.open('/mnt/user-data/uploads/6245b0e9-image.png').convert('RGBA')
OY = 140                                   # crop offset (top of the screenshot)

def poi(c, cx, cy, kind):
    """Quest marker in the tracker's Aether style: navy disc, blue ring,
    gold '?' for ready, white dots for in progress."""
    R = 12; c.d.ellipse(c.P(cx - R, cy - R, cx + R, cy + R), fill=NAVY + (255,), outline=BLUE + (255,), width=2 * SS)
    if kind == 'ready': c.text((cx, cy), "?", 17, GOLD, 'Bold', 'mm')
    else:
        for k in (-5, 0, 5): c.d.ellipse(c.P(cx + k - 1.6, cy - 1.6, cx + k + 1.6, cy + 1.6), fill=WHITE + (255,))

def check(c, x, y, on):
    c.d.rounded_rectangle(c.P(x, y, x + 18, y + 18), u(2), fill=(8, 12, 22, 255), outline=BLUE + (255,), width=SS)
    if on:
        c.d.line(c.P(x + 4, y + 9, x + 8, y + 13), fill=GOLD + (255,), width=3 * SS)
        c.d.line(c.P(x + 8, y + 13, x + 15, y + 4), fill=GOLD + (255,), width=3 * SS)

def pill(c, box, text, current=False, arrow=True):
    x0, y0, x1, y1 = c.P(*box)
    c.d.rounded_rectangle([x0, y0, x1, y1], (y1 - y0) // 2, fill=((28, 58, 104) if current else NAVY) + (255,),
                          outline=(GOLD if current else BLUE) + (255,), width=SS)
    c.text((box[0] + 16, (box[1] + box[3]) / 2), text, 17, GOLD if current else WHITE, 'SemiBold', 'lm')
    if arrow: c.tri(box[2] - 18, (box[1] + box[3]) / 2 + 1, 5, GOLD if current else WHITE)

def chev(c, x, y):
    c.d.line([tuple(c.P(*p)) for p in [(x, y - 8), (x + 7, y), (x, y + 8)]], fill=BLUE + (255,), width=2 * SS, joint='curve')

def worldmap():
    bg = SHOT.crop((0, OY, 1620, 985))
    c = Canvas(bg)
    box = (22, 168 - OY, 1575, 975 - OY)
    c.window(box, "Map & Quest Log")
    c.crest((64, 208 - OY), 40)
    c.text((64, 208 - OY), "M", 26, GOLD, 'Bold', 'mm')
    c.close(box[2] - 26, box[1] + 19)
    # maximize: navy box, white arrow
    cx, cy = box[2] - 58, box[1] + 19
    c.d.rounded_rectangle(c.P(cx - 11, cy - 11, cx + 11, cy + 11), u(3), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
    c.d.line(c.P(cx - 5, cy + 5, cx + 5, cy - 5), fill=WHITE + (255,), width=2 * SS)
    c.d.line(c.P(cx, cy - 5, cx + 5, cy - 5), fill=WHITE + (255,), width=2 * SS)
    c.d.line(c.P(cx + 5, cy - 5, cx + 5, cy), fill=WHITE + (255,), width=2 * SS)
    # the map itself stays (pins, fog, our coords box included)
    art = SHOT.crop((35, 268, 1072, 968)); c.paste(art, (35, 268 - OY))
    L, d = c.layer(); d.rectangle(c.P(35, 268 - OY, 1072, 968 - OY), outline=BLUE + (255,), width=SS); c.over(L)
    # breadcrumb bar: navy pills, blue chevrons, the current zone in gold
    y0, y1 = 216 - OY, 256 - OY
    L, d = c.layer(); d.rounded_rectangle(c.P(118, y0 - 4, 1000, y1 + 4), u(5), fill=(10, 18, 34, 235), outline=(60, 110, 175, 200), width=SS); c.over(L)
    pill(c, (126, y0, 226, y1), "World", arrow=False); chev(c, 238, (y0 + y1) / 2)
    pill(c, (252, y0, 392, y1), "Kalimdor"); chev(c, 404, (y0 + y1) / 2)
    pill(c, (418, y0, 560, y1), "Desolace", current=True)
    # filter + pin buttons
    for bx, kind in ((1040, 'filter'),):
        c.d.rounded_rectangle(c.P(bx - 16, 222 - OY, bx + 16, 254 - OY), u(4), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
        c.tri(bx, 238 - OY + 1, 6, WHITE)
    # quest log panel
    Q0, Q1 = 1082, 1560
    L, d = c.layer(); d.rounded_rectangle(c.P(Q0, 212 - OY, Q1, 962 - OY), u(6), fill=(10, 14, 22, 255), outline=(60, 110, 175, 220), width=SS); c.over(L)
    searchbox(c, (Q0 + 8, 218 - OY, Q0 + 300, 244 - OY), "Search Quest Log")
    c.d.rounded_rectangle(c.P(Q0 + 308, 218 - OY, Q1 - 34, 244 - OY), u(4), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
    c.text((Q1 - 44, 231 - OY), "Quests: 34/40", 15, WHITE, 'Regular', 'rm')
    gx, gy = Q1 - 17, 231 - OY
    import math
    for k in range(8):
        a = k * math.pi / 4
        c.d.line(c.P(gx + 5 * math.cos(a), gy + 5 * math.sin(a), gx + 9 * math.cos(a), gy + 9 * math.sin(a)), fill=WHITE + (255,), width=3 * SS)
    c.d.ellipse(c.P(gx - 6, gy - 6, gx + 6, gy + 6), outline=WHITE + (255,), width=3 * SS)
    y = 262 - OY; X = Q0 + 14; Xr = Q1 - 30
    rows = [("q", "ready", "[38] Lost Shipping Crate", (255, 255, 255), ["Deliver the Lost Shipping Crate to Friz", "Frazzlespark at Powderfuse Port."], True, False),
            ("q", "prog", "[40] Cherry for Your Thoughts?", ORANGE, ["0/1 Cherry Grog"], True, False),
            ("h", "Arathi Highlands", False), ("h", "Crafting", False), ("h", "Orgrimmar", False),
            ("h", "Stranglethorn Vale", True),
            ("q", "ready", "[31] Supply and Demand", GREEN, ["Ready for turn-in"], False, True),
            ("q", "prog", "[37] The Defense of Grom'gol", GOLD, ["0/10 Mosh'Ogg Brute slain", "0/5 Mosh'Ogg Witch Doctor slain"], False, False),
            ("q", "prog", "[37+] The Vile Reef  (Elite)", GOLD, ["0/1 Tablet Shard"], False, False)]
    for r in rows:
        if r[0] == "h":
            c.header((X, y, Xr, y + 36), r[1], minus=r[2])
            if not r[2]: c.text((Xr - 14, y + 17), "+", 20, GOLD, 'Bold', 'mm')
            y += 44; continue
        _, kind, title, col, obj, on, sel = r
        h = 34 + 22 * len(obj)
        if sel:
            L, d = c.layer(); x0, yy0, x1, yy1 = c.P(X, y - 4, Xr, y + h - 6)
            d.rounded_rectangle([x0, yy0, x1, yy1], u(4), fill=BLUE + (48,), outline=BLUE + (150,), width=SS)
            d.rounded_rectangle([x0 + SS, yy0 + 3 * SS, x0 + 4 * SS, yy1 - 3 * SS], SS, fill=GOLD + (255,)); c.over(L)
        poi(c, X + 18, y + 14, kind)
        c.text((X + 40, y + 14), title, 17, col if col != (255, 255, 255) else GOLD, 'Regular', 'lm')
        for i, t in enumerate(obj): c.text((X + 50, y + 38 + i * 22), "- " + t, 15, WHITE, 'Regular', 'lm')
        check(c, Xr - 26, y + 5, on)
        y += h + 6
    # scroll bar
    sx = Q1 - 14
    c.d.rounded_rectangle(c.P(sx - 3, 262 - OY, sx + 3, 950 - OY), 3 * SS, fill=(14, 28, 52, 255))
    c.d.rounded_rectangle(c.P(sx - 3, 300 - OY, sx + 3, 560 - OY), 3 * SS, fill=BLUE + (235,))
    return c.done()

if __name__ == '__main__':
    im = label(worldmap(), "4  World Map and quest log (on your screenshot, game size)")
    im.save('/home/claude/aether-repo/mock/out_p2_map.png'); print(im.size)
