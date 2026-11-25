# Release C, mockup 1: Hub tab layout options A / B / C, drawn at in-game
# size (1.55 px per UI unit) on the reference game frame. Same AetherBars
# settings shown in each so the options compare fairly.
# Run from mock/: python3 hub_layout.py  -> out_hub_A.png, out_hub_B.png,
# out_hub_C.png, out_hub_B_zoom.png
import sys
from PIL import Image, ImageDraw, ImageEnhance
import skins_lib as K
from skins_lib import GOLD, BLUE, NAVY, PANEL, WHITE, DIM, RED, U, SS

WU, HU = 620, 525           # Hub window in UI units (WIN_W, WIN_H)
SIDE = 160
M = 34                      # px margin around the window
OX, OY = M, M

def X(ux): return OX + ux * U
def Y(uy): return OY + uy * U

def background():
    bg = Image.open('/tmp/v4/f_057.png').convert('RGB')
    w, h = int(WU * U + 2 * M), int(HU * U + 2 * M)
    bg = bg.crop((700, 200, 700 + w, 200 + h))
    return ImageEnhance.Brightness(bg).enhance(0.55)

def rect(c, ux0, uy0, ux1, uy1, fill=None, outline=None, r=4, a=255, w=1):
    x0, y0, x1, y1 = c.P(X(ux0), Y(uy0), X(ux1), Y(uy1))
    c.d.rounded_rectangle([x0, y0, x1, y1], int(r * U * SS),
                          fill=(fill + (a,)) if fill else None,
                          outline=(outline + (255,)) if outline else None, width=w * SS)

def T(c, ux, uy, s, size, color, w='Regular', anchor='la'):
    c.text((X(ux), Y(uy)), s, size, color, w, anchor)

# ---------- sidebar ----------
def side_frame(c):
    rect(c, 10, 34, 10 + SIDE, HU - 40, fill=(8, 9, 12), outline=(46, 104, 160), r=5, a=200)

def section(c, uy, label, arrow=None):
    x = 20
    if arrow:
        c.tri(X(x + 3), Y(uy + 6), 3.2, BLUE, arrow); x += 10
    T(c, x, uy, label, 13, BLUE, 'SemiBold')
    tw = c.d.textlength(label, font=K.F(13, 'SemiBold')) / SS / U
    L, d = c.layer()
    d.line(c.P(X(x + tw + 6), Y(uy + 7), X(SIDE), Y(uy + 7)), fill=BLUE + (90,), width=SS)
    c.over(L)

def tab(c, uy, label, right='', selected=False, h=24, sub=None, indent=0):
    x0, x1 = 16 + indent, SIDE + 4
    if selected:
        L, d = c.layer()
        d.rounded_rectangle(c.P(X(x0), Y(uy), X(x1), Y(uy + h)), int(3 * U * SS), fill=(77, 179, 255, 64))
        c.over(L)
        rect(c, x0, uy + 3, x0 + 2, uy + h - 3, fill=GOLD, r=1)          # gold notch
    col = GOLD if selected else (217, 217, 217)
    if sub:
        T(c, x0 + 8, uy + 4, label, 15.5, col, 'SemiBold' if selected else 'Regular')
        T(c, x0 + 8, uy + 20, sub, 12.5, (140, 146, 160))
    else:
        T(c, x0 + 8, uy + h / 2, label, 15.5, col, 'SemiBold' if selected else 'Regular', 'lm')
    if right:
        T(c, x1 - 6, uy + h / 2, right, 12.5, (140, 140, 140), 'Regular', 'rm')

# ---------- page controls (cursor in UI units) ----------
PX = SIDE + 24              # page left
PR = WU - 30                # page right
PB = HU - 44                # page bottom (scroll area)

class Page:
    def __init__(self, c, top=40):
        self.c, self.y, self.full = c, top, False
    def room(self, h):
        if self.y + h > PB: self.full = True
        return not self.full
    def title(self, s, sub):
        T(self.c, PX, self.y, s, 21, GOLD, 'SemiBold')
        tw = self.c.d.textlength(s, font=K.F(21, 'SemiBold')) / SS / U
        T(self.c, PX + tw + 8, self.y + 5, sub, 13.5, (150, 150, 150))
        self.y += 30
    def header(self, s):
        if not self.room(22): return
        T(self.c, PX, self.y, s, 16.5, GOLD, 'SemiBold'); self.y += 22
    def band(self, s, addons=''):
        if not self.room(26): return
        self.c.header((X(PX - 4), Y(self.y), X(PR), Y(self.y + 20)), s, minus=False)
        if addons: T(self.c, PR - 4, self.y + 10, addons, 12.5, (150, 156, 170), 'Regular', 'rm')
        self.y += 27
    def check(self, s, on=True, ux=0, row_end=True):
        if not self.room(26): return
        x, y = PX + 4 + ux, self.y + 4
        rect(self.c, x, y, x + 16, y + 16, fill=(18, 43, 82), outline=GOLD if on else BLUE, r=2)
        if on: rect(self.c, x + 4, y + 4, x + 12, y + 12, fill=GOLD, r=1)
        T(self.c, x + 22, y + 8, s, 15.5, WHITE if on else (215, 218, 225), 'Regular', 'lm')
        if row_end: self.y += 26
    def slider(self, s, frac, val):
        if not self.room(52): return
        T(self.c, PX + 4, self.y, s, 15.5, WHITE); self.y += 20
        x0, x1, yy = PX + 8, PX + 248, self.y + 8
        rect(self.c, x0, yy - 2, x1, yy + 2, fill=(31, 71, 128), r=1)
        tx = x0 + (x1 - x0) * frac
        rect(self.c, tx - 4, yy - 8, tx + 4, yy + 8, fill=GOLD, r=1)
        rect(self.c, x1 + 12, yy - 10, x1 + 66, yy + 10, fill=(8, 12, 22), outline=BLUE, r=3)
        T(self.c, x1 + 39, yy, val, 15, WHITE, 'Regular', 'mm')
        self.y += 32
    def choice(self, s, opts, sel):
        if not self.room(48): return
        T(self.c, PX + 4, self.y, s, 15.5, WHITE); self.y += 20
        x = PX + 6
        for o in opts:
            w = max(80, self.c.d.textlength(o, font=K.F(15, 'SemiBold')) / SS / U + 20)
            on = o == sel
            rect(self.c, x, self.y, x + w, self.y + 20, fill=NAVY, outline=GOLD if on else BLUE, r=5)
            T(self.c, x + w / 2, self.y + 10, o, 15, GOLD if on else WHITE, 'SemiBold', 'mm')
            x += w + 4
        self.y += 28
    def buttons(self, labels):
        if not self.room(30): return
        x = PX + 4
        for s in labels:
            danger = s.startswith('!'); s = s.lstrip('!')
            w = self.c.d.textlength(s, font=K.F(15, 'SemiBold')) / SS / U + 28
            rect(self.c, x, self.y, x + w, self.y + 22, fill=NAVY, outline=(200, 70, 60) if danger else BLUE, r=5)
            T(self.c, x + w / 2, self.y + 11, s, 15, WHITE, 'SemiBold', 'mm')
            x += w + 8
        self.y += 30
    def gap(self, h=6): self.y += h
    def scrollbar(self, frac_shown=0.55):
        x = PR + 8; top, bot = 40, PB
        rect(self.c, x, top, x + 4, bot, fill=(31, 71, 128), r=2, a=150)
        rect(self.c, x, top, x + 4, top + (bot - top) * frac_shown, fill=GOLD, r=2, a=230)

# ---------- the window ----------
def window(c, footer_moves=False):
    c.window((X(0), Y(0), X(WU), Y(HU)), None, strip=30, chev3d=True)
    T(c, 14, 15, 'AETHER HUB', 16.5, BLUE, 'SemiBold', 'lm')
    c.close(X(WU - 18), Y(15))
    side_frame(c)
    # footer
    fy = HU - 23
    if footer_moves:
        for s, x0, w in (('Unlock to Move', 14, 112), ('Reset Positions...', 132, 128)):
            rect(c, x0, fy - 11, x0 + w, fy + 11, fill=NAVY, outline=BLUE, r=5)
            T(c, x0 + w / 2, fy, s, 15, WHITE, 'SemiBold', 'mm')
    else:
        T(c, 16, fy, 'Changes apply right away. Hover anything for help.', 13, (150, 150, 150), 'Regular', 'lm')
    x = WU - 24 - 100 - 150
    rect(c, x, fy - 8, x + 16, fy + 8, fill=(18, 43, 82), outline=GOLD, r=2)
    rect(c, x + 4, fy - 4, x + 12, fy + 4, fill=GOLD, r=1)
    T(c, x + 22, fy, 'Minimap button', 15.5, WHITE, 'Regular', 'lm')
    rect(c, WU - 124, fy - 11, WU - 24, fy + 11, fill=NAVY, outline=BLUE, r=5)
    T(c, WU - 74, fy, 'Reload UI', 15, WHITE, 'SemiBold', 'mm')

# ---------- AetherBars, every setting in one place (A and C) ----------
def bars_page(p):
    p.title('AetherBars', 'Clean action bars and XP bar')
    p.header('Look')
    p.check('Aether panel behind each bar')
    p.slider('Icon edge darkness', 0.85, '85%')
    p.check('Cooldown glow (red after use, green when ready)')
    p.check('Macro names on buttons')
    p.check('Hide Blizzard\'s bar art')
    p.header('Fading')
    p.slider('Bars when idle', 0.6, '60%')
    p.check('Solid in combat', ux=0, row_end=False); p.check('Solid under your mouse', ux=210)
    p.header('Size')
    p.choice('Match button size to Action Bar 1', ['Bar 2', 'All Bars', 'Off'], 'Bar 2')
    p.header('Layout')
    p.check('Center the bars when aligning')
    p.buttons(['Align Bars...', 'Undo Last Align'])
    p.buttons(['!Restore AetherBars Defaults...'])

ADDON_TABS = ['AetherMeter', 'AetherBars', 'AetherCoords', 'AetherPathfinder', 'AetherMarks',
              'AetherItemID', 'AetherLedger', 'AetherPack', 'AetherChat', 'AetherFrames', 'AetherSkins']

def option_A():
    c = K.Canvas(background()); window(c)
    y = 43; section(c, y, 'GENERAL'); y += 16
    for s in ('Your Character', 'Move & Reset', 'Help & Debug'):
        tab(c, y, s, '60' if s == 'Your Character' else ''); y += 25
    y += 6; section(c, y, 'ADDONS'); y += 16
    for s in ADDON_TABS:
        tab(c, y, s, selected=(s == 'AetherBars')); y += 25
    p = Page(c); bars_page(p); p.scrollbar(0.72)
    return c.done()

GROUPS = [('Your Character', 'Level, professions'),
          ('Action Bar Area', 'Bars, Chat, Meter, XP bar'),
          ('Unit Frames', 'Frames'),
          ('Map & Waypoints', 'Coords, Pathfinder'),
          ('Quests & Mobs', 'Ledger, Marks'),
          ('Bags & Items', 'Pack, ItemID'),
          ('Window Look', 'Skins, minimap'),
          ('Help & Debug', 'Versions, reports')]

def option_B():
    c = K.Canvas(background()); window(c, footer_moves=True)
    y = 42
    for name, sub in GROUPS:
        tab(c, y, name, selected=(name == 'Action Bar Area'), h=36, sub=sub); y += 39
    p = Page(c)
    p.title('Action Bar Area', 'Your bars, chat, meter and XP bar')
    p.band('Action bars', 'AetherBars')
    p.check('Aether panel behind each bar')
    p.slider('Bars when idle', 0.6, '60%')
    p.check('Solid in combat', ux=0, row_end=False); p.check('Solid under your mouse', ux=210)
    p.check('Cooldown glow (red after use, green when ready)')
    p.check('Macro names on buttons', ux=0, row_end=False); p.check('Hide Blizzard\'s bar art', ux=210)
    p.choice('Match button size to Action Bar 1', ['Bar 2', 'All Bars', 'Off'], 'Bar 2')
    p.buttons(['Align Bars...', 'Undo Last Align'])
    p.gap(2)
    p.band('Chat', 'AetherChat')
    p.check('Aether panel behind chat')
    p.check('Chat fits left of your bars')
    p.scrollbar(0.34)
    return c.done()

def option_C():
    c = K.Canvas(background()); window(c)
    y = 42
    tab(c, y, 'Your Character', '60'); y += 27
    section(c, y, 'ACTION BAR AREA', 'down'); y += 16
    for s in ('AetherBars', 'AetherChat', 'AetherMeter'):
        tab(c, y, s, selected=(s == 'AetherBars'), indent=8); y += 25
    y += 4
    for g in ('UNIT FRAMES', 'MAP & WAYPOINTS', 'QUESTS & MOBS', 'BAGS & ITEMS', 'WINDOW LOOK'):
        section(c, y, g, 'right'); y += 22
    y += 4
    tab(c, y, 'Move & Reset'); y += 25
    tab(c, y, 'Help & Debug')
    p = Page(c); bars_page(p); p.scrollbar(0.72)
    return c.done()

if __name__ == '__main__':
    out = {}
    for k, fn in (('A', option_A), ('B', option_B), ('C', option_C)):
        im = fn(); im.save(f'out_hub_{k}.png'); out[k] = im
    b = out['B']
    z = b.crop((0, 0, int(X(PR + 20)), int(Y(250)))).resize(
        (int(X(PR + 20)) * 2, int(Y(250)) * 2), Image.LANCZOS)
    z.save('out_hub_B_zoom.png')
    print('ok', b.size)
