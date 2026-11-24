# Mockup: the world map (windowed with the quest log, and full screen) in the
# Aether look: style A (Clean), capsule bars, only the window's four chevrons.
# The map art itself is Blizzard's and stays; only the frame around it changes.
import sys; sys.path.insert(0, '/home/claude/mock')
from skins_lib import *
from PIL import Image, ImageDraw
import numpy as np
import cv2
def clean(path, boxes):
    """Paint out overlays that sit on top of the map art in the screenshot
    (coordinate boxes, the help button, the 'Screen Captured' message)."""
    a = np.array(Image.open(path).convert('RGB'))
    m = np.zeros(a.shape[:2], np.uint8)
    for b in boxes: cv2.rectangle(m, (b[0], b[1]), (b[2], b[3]), 255, -1)
    out = cv2.inpaint(a[..., ::-1], m, 7, cv2.INPAINT_TELEA)[..., ::-1]
    return Image.fromarray(out).convert('RGBA')
WIN = clean('/mnt/user-data/uploads/6a4f91f7-image.png', [(898, 136, 1050, 170), (104, 796, 242, 820), (1004, 772, 1056, 824)])
_S = 2560 / 2419
FS = clean('/mnt/user-data/uploads/28bf8c1d-image.png', [tuple(int(v * _S) for v in b) for b in
           [(2118, 103, 2254, 137), (236, 1482, 368, 1506)]])
# "Screen Captured": cover it with the strip of map just above it (same terrain band)
_b = tuple(int(v * _S) for v in (1108, 738, 1310, 774)); _h = _b[3] - _b[1]
_patch = FS.crop((_b[0], _b[1] - _h - 4, _b[2], _b[1] - 4))
_m = Image.new('L', _patch.size, 0); ImageDraw.Draw(_m).rounded_rectangle([0, 0, _patch.width - 1, _patch.height - 1], 10, fill=255)
FS.paste(_patch, (_b[0], _b[1]), _m.filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(4)))
WORLD = Image.open('/tmp/v4/f_057.png').convert('RGBA')
QGREEN = (64, 191, 64); QORANGE = (255, 128, 64); QRED = (255, 40, 40)

def map_inset(c, crop, box, src):
    """Blizzard's map art, framed by a fine blue edge with rounded corners."""
    x0, y0, x1, y1 = box
    art = src.crop(crop).resize((int((x1 - x0) * SS), int((y1 - y0) * SS)), Image.LANCZOS)
    m = Image.new('L', art.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, art.width - 1, art.height - 1], u(6), fill=255)
    art.putalpha(m); c.over(art, (x0, y0))
    Lr, d = c.layer()
    d.rounded_rectangle(c.P(x0, y0, x1, y1), u(6), outline=BLUE + (255,), width=SS)
    d.rounded_rectangle(c.P(x0 + 3, y0 + 3, x1 - 3, y1 - 3), u(5), outline=BLUE + (70,), width=SS)
    c.over(Lr)

def breadcrumbs(c, x, y, h, items):
    """World > Eastern Kingdoms > Stranglethorn Vale: navy capsules, blue
    separators, white dropdown arrows, the current zone in Aether gold."""
    for i, (label_, dropdown) in enumerate(items):
        cur = i == len(items) - 1
        w = int(F(17).getlength(label_) / SS) + (58 if dropdown else 36)
        Lr, d = c.layer()
        d.rounded_rectangle(c.P(x, y, x + w, y + h), int(h * SS / 2), fill=NAVY + (255,),
                            outline=BLUE + (255,) if cur else (50, 95, 160, 255), width=SS)
        c.over(Lr)
        c.text((x + 18, y + h / 2), label_, 17, GOLD if cur else WHITE, 'SemiBold' if cur else 'Regular', 'lm')
        if dropdown: c.tri(x + w - 20, y + h / 2 + 1, 6, WHITE, 'down')
        x += w + 8
        if i < len(items) - 1:
            Lr, d = c.layer()
            d.line(c.P(x - 2, y + h / 2 - 6, x + 3, y + h / 2), fill=BLUE + (255,), width=2 * SS)
            d.line(c.P(x + 3, y + h / 2, x - 2, y + h / 2 + 6), fill=BLUE + (255,), width=2 * SS)
            c.over(Lr); x += 12

def quest_icon(c, cx, cy, done, r=13):
    Lr, d = c.layer(); X, Y = c.P(cx, cy); R = r * SS
    d.ellipse([X - R, Y - R, X + R, Y + R], fill=NAVY + (245,), outline=GOLD + (255,), width=int(1.5 * SS)); c.over(Lr)
    if done: c.text((cx + 0.5, cy), "?", 17, GOLD, 'Bold', 'mm')
    else:
        for k in (-5, 0, 5): c.d.ellipse(c.P(cx + k - 1.7, cy - 1.7, cx + k + 1.7, cy + 1.7), fill=GOLD + (255,))

QUESTS = [  # icon done?, title, color, elite, objective lines, tracked
    (False, "[31] Supply and Demand", QGREEN, False, ["- 0/2 Large River Crocolisk Skin"], True),
    (False, "[37] The Defense of Grom'gol", GOLD, False, ["- 0/10 Mosh'Ogg Brute slain", "- 0/5 Mosh'Ogg Witch Doctor slain"], True),
    (False, "[37+] The Vile Reef", GOLD, True, ["- 0/1 Tablet Shard"], True),
    (True, "[37] Tiger Mastery", GOLD, False, ["READY"], True),
    (True, "[37] Trollbane", GOLD, False, ["- Travel to Hammerfall in the Arathi", "  Highlands and speak with Zengu."], False),
    (True, "[38] Report to Rog'mar", QORANGE, False, ["- Report to Krom'rosh at the", "  Rog'mar outpost in the", "  Riverglades."], True),
    (False, "[40] Chapter IV", QORANGE, False, ["- 0/1 Green Hills of Stranglethorn -", "  Page 26"], True),
    (False, "[40+] Panther Mastery", QORANGE, True, ["- 0/1 Fang of Bhag'thera"], True),
    (False, "[40] The Green Hills of Stranglethorn", QORANGE, False, ["- 0/1 Green Hills of Stranglethorn -", "  Chapter IV"], True),
    (False, "[41] Bloodscalp Clan Heads", QRED, False, [], False),
]

def quest_log(c, x0, y0, x1, y1):
    # search box + quest count
    Lr, d = c.layer()
    d.rounded_rectangle(c.P(x0 + 4, y0, x0 + 300, y0 + 30), u(4), fill=(6, 9, 15, 255), outline=(50, 95, 160, 255), width=SS)
    d.rounded_rectangle(c.P(x0 + 308, y0, x1 - 30, y0 + 30), u(4), fill=NAVY + (255,), outline=(50, 95, 160, 255), width=SS)
    c.over(Lr)
    c.d.ellipse(c.P(x0 + 14, y0 + 9, x0 + 24, y0 + 19), outline=DIM + (255,), width=2 * SS)
    c.d.line(c.P(x0 + 23, y0 + 18, x0 + 28, y0 + 23), fill=DIM + (255,), width=2 * SS)
    c.text((x0 + 34, y0 + 15), "Search Quest Log", 16, DIM, 'Regular', 'lm')
    c.text(((x0 + 308 + x1 - 30) / 2, y0 + 15), "Quests: 34/40", 16, WHITE, 'Regular', 'mm')
    c.button((x1 - 24, y0, x1 + 4, y0 + 30), "", 10)        # settings
    c.d.ellipse(c.P(x1 - 16, y0 + 9, x1 - 4, y0 + 21), outline=WHITE + (255,), width=2 * SS)
    # zone header like the tracker
    c.header((x0 + 14, y0 + 50, x1 - 30, y0 + 82), "Stranglethorn Vale")
    y = y0 + 96
    for done, title, col, elite, lines, tracked in QUESTS:
        if y > y1 - 22: break
        quest_icon(c, x0 + 28, y + 11, done)
        c.text((x0 + 50, y + 11), title, 18, col, 'Regular', 'lm')
        if elite: c.text((x1 - 72, y + 11), "(Elite)", 17, col, 'Regular', 'rm')
        if tracked is not None and title != "[41] Bloodscalp Clan Heads":
            c.check((x1 - 60, y + 1), "", tracked)
        y += 24
        for ln in lines:
            if ln == "READY": c.text((x0 + 62, y + 9), "- Ready for turn-in", 17, SKY, 'Regular', 'lm')
            else: c.text((x0 + 62, y + 9), ln, 17, (205, 210, 220), 'Regular', 'lm')
            y += 21
        y += 14
    # fade the last row out at the bottom edge, like a scrolling list
    Lr, d = c.layer(); W = int((x1 - x0) * SS); Hh = int(40 * SS)
    a = np.linspace(0, 1, Hh)[:, None] * np.ones((1, W))
    fade = np.zeros((Hh, W, 4), np.uint8); fade[..., :3] = PANEL; fade[..., 3] = (a * 255).astype(np.uint8)
    c.over(Image.fromarray(fade), (x0, y1 - 40))
    # scrollbar
    Lr, d = c.layer()
    d.rounded_rectangle(c.P(x1 + 8, y0 + 50, x1 + 14, y1), u(3), fill=(30, 45, 70, 255))
    d.rounded_rectangle(c.P(x1 + 7, y0 + 54, x1 + 15, y0 + 380), u(3), fill=BLUE + (200,))
    c.over(Lr)

def coords_pill(c, x1, y, text):
    w = F(16, 'SemiBold').getlength(text) / SS + 28
    Lr, d = c.layer(); d.rounded_rectangle(c.P(x1 - w, y, x1, y + 28), u(14), fill=NAVY + (235,), outline=BLUE + (255,), width=SS); c.over(Lr)
    c.text((x1 - w / 2, y + 14), text, 16, WHITE, 'SemiBold', 'mm')

def small_btn(c, cx, cy, kind):
    s = 14; c.button((cx - s, cy - s, cx + s, cy + s), "", 10)
    if kind == 'expand':
        c.d.line(c.P(cx - 6, cy + 6, cx + 6, cy - 6), fill=WHITE + (255,), width=2 * SS)
        c.d.line(c.P(cx, cy - 6, cx + 6, cy - 6), fill=WHITE + (255,), width=2 * SS)
        c.d.line(c.P(cx + 6, cy - 6, cx + 6, cy), fill=WHITE + (255,), width=2 * SS)
    elif kind == 'shrink':
        c.d.line(c.P(cx - 6, cy + 6, cx + 6, cy - 6), fill=WHITE + (255,), width=2 * SS)
        c.d.line(c.P(cx - 6, cy, cx - 6, cy + 6), fill=WHITE + (255,), width=2 * SS)
        c.d.line(c.P(cx - 6, cy + 6, cx, cy + 6), fill=WHITE + (255,), width=2 * SS)
    elif kind == 'filter': c.tri(cx, cy + 1, 7, WHITE, 'down')
    elif kind == 'help': c.text((cx, cy), "?", 18, WHITE, 'Bold', 'mm')

def windowed():
    ox, oy = 40, 50
    bg = WORLD.crop((200, 120, 200 + 1573 + 2 * ox, 120 + 835 + 2 * oy)); c = Canvas(bg)
    c.window((ox + 6, oy + 18, ox + 1564, oy + 830), "Map & Quest Log")
    c.crest((ox + 50, oy + 60), 40, WIN.crop((14, 14, 84, 84)))
    small_btn(c, ox + 1500, oy + 37, 'expand'); c.close(ox + 1540, oy + 37)
    breadcrumbs(c, ox + 104, oy + 70, 34, [("World", False), ("Eastern Kingdoms", True), ("Stranglethorn Vale", True)])
    small_btn(c, ox + 1024, oy + 88, 'filter')
    map_inset(c, (16, 124, 1056, 824), (ox + 18, oy + 122, ox + 1056, oy + 818), WIN)
    # the PCs toggle (ours) stays; "You:" box becomes an Aether pill
    c.paste(WIN.crop((20, 130, 108, 170)), (ox + 22, oy + 128))
    coords_pill(c, ox + 1044, oy + 136, "You: 27.2, 77.5")
    c.text((ox + 110, oy + 806), "Player: 27.2, 77.5", 15, WHITE, 'Regular', 'lm', outline=True)
    small_btn(c, ox + 1030, oy + 796, 'help')
    Lr, d = c.layer(); d.line(c.P(ox + 1064, oy + 66, ox + 1064, oy + 818), fill=BLUE + (90,), width=SS); c.over(Lr)
    quest_log(c, ox + 1066, oy + 66, ox + 1525, oy + 818)
    return c.done()

def fullscreen():
    S = FS.width / 2419            # the screenshot is 2560 wide; the user's preview was 2419
    c = Canvas(Image.new('RGBA', FS.size, (0, 0, 0, 255)))
    L, R = int(150 * S), int(2270 * S)
    c.window((L, 22, R, FS.height - 14), "Map")
    small_btn(c, R - 76, 41, 'shrink'); c.close(R - 36, 41)
    breadcrumbs(c, L + 18, 70, 36, [("World", False), ("Eastern Kingdoms", True), ("Stranglethorn Vale", True)])
    small_btn(c, R - 36, 88, 'filter')
    map_inset(c, (int(160 * S), int(100 * S), int(2264 * S), int(1500 * S)), (L + 14, 120, R - 14, FS.height - 30), FS)
    c.paste(FS.crop((int(158 * S), int(103 * S), int(240 * S), int(135 * S))), (L + 20, 128))
    coords_pill(c, R - 26, 132, "You: 27.2, 77.5")
    c.text((L + 90, FS.height - 50), "Player: 27.2, 77.5", 16, WHITE, 'Regular', 'lm', outline=True)
    return c.done()

if __name__ == '__main__':
    windowed().save('/tmp/sk/wm_window.png'); fullscreen().save('/tmp/sk/wm_full.png'); print('ok')
