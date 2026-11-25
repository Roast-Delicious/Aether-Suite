# Second-pass mockup 2: Friends (SocialUIFrame), 410x675 units at 1.55 px/unit.
from skins_lib import *
from pass2_rep import backdrop, sidetab, scrollbar, sel_row, icon

def searchbox(c, box, hint):
    x0, y0, x1, y1 = c.P(*box)
    c.d.rounded_rectangle([x0, y0, x1, y1], u(4), fill=(8, 12, 22, 255), outline=BLUE + (255,), width=SS)
    cx, cy = box[0] + 14, (box[1] + box[3]) / 2
    c.d.ellipse(c.P(cx - 6, cy - 7, cx + 4, cy + 3), outline=(170, 190, 215, 255), width=2 * SS)
    c.d.line(c.P(cx + 3, cy + 2, cx + 8, cy + 7), fill=(170, 190, 215, 255), width=2 * SS)
    c.text((box[0] + 28, cy), hint, 15, DIM, 'Regular', 'lm')

def dropdown(c, box, text):
    x0, y0, x1, y1 = c.P(*box)
    c.d.rounded_rectangle([x0, y0, x1, y1], u(4), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
    c.text((box[0] + 12, (box[1] + box[3]) / 2), text, 15, WHITE, 'Regular', 'lm')
    c.tri(box[2] - 14, (box[1] + box[3]) / 2 + 1, 5, WHITE)

def iconbtn(c, cx, cy, s, kind):
    x0, y0, x1, y1 = c.P(cx - s, cy - s, cx + s, cy + s)
    c.d.rounded_rectangle([x0, y0, x1, y1], u(4), fill=NAVY + (255,), outline=BLUE + (255,), width=SS)
    if kind == 'menu': c.menu(cx, cy)
    elif kind == 'invite':
        c.d.text(tuple(c.P(cx, cy - 1)), "+", font=F(20, 'Bold'), fill=WHITE + (255,), anchor='mm')

def card(c, box, name, where, online, selected=False):
    x0, y0, x1, y1 = c.P(*box)
    L, d = c.layer()
    fill = (22, 46, 84) if online else (16, 24, 38)
    d.rounded_rectangle([x0, y0, x1, y1], u(6), fill=fill + (245,),
                        outline=(BLUE + (255,)) if selected else ((60, 110, 175, 200) if online else (50, 64, 86, 200)), width=SS * (2 if selected else 1))
    c.over(L)
    dot = GREEN if online else (110, 116, 128)
    c.d.ellipse(c.P(box[0] + 14, box[1] + 17, box[0] + 26, box[1] + 29), fill=dot + (255,))
    c.text((box[0] + 36, box[1] + 23), name, 17, (115, 191, 255) if online else DIM, 'SemiBold', 'lm')
    c.text((box[0] + 36, box[1] + 50), where, 14, WHITE if online else (120, 126, 138), 'Regular', 'lm')
    iconbtn(c, box[2] - 32, (box[1] + box[3]) / 2, 20, 'invite')

def friends():
    W, H = 840, 1150
    c = Canvas(backdrop(W, H))
    box = (60, 50, 60 + 635, 50 + 1046)
    c.window(box, "Friends List", chevrons='tbl')
    c.crest((106, 96), 40); icon(c, 'char', 106, 100, 20, GOLD)
    c.close(box[2] - 26, box[1] + 19)
    for i, (g, s) in enumerate([('char', True), ('stats', False), ('pvp', False), ('skill', False)]):
        sidetab(c, box[2] + 4, box[1] + 70 + i * 92, g, selected=s)
    # Battle.net bar: navy strip, battletag, status dropdown, menu button
    y = box[1] + 72
    c.header((box[0] + 20, y, box[2] - 20, y + 50), "", minus=False)
    dropdown(c, (box[0] + 30, y + 10, box[0] + 112, y + 40), "On")
    c.text((box[0] + 130, y + 25), "Jay#1234", 17, (115, 191, 255), 'SemiBold', 'lm')
    iconbtn(c, box[2] - 46, y + 25, 17, 'menu')
    # filter bar
    y += 70
    dropdown(c, (box[0] + 22, y, box[0] + 222, y + 36), "All Friends")
    searchbox(c, (box[0] + 236, y + 2, box[2] - 22, y + 34), "Search")
    c.d.line(c.P(box[0] + 22, y + 52, box[2] - 22, y + 52), fill=BLUE + (120,), width=SS)
    # list
    y += 66; L0, L1 = box[0] + 22, box[2] - 40
    c.header((L0, y, L1, y + 36), "Online  (2)"); y += 46
    card(c, (L0, y, L1, y + 72), "Zulkaro", "Desolace  ·  Level 37 Hunter", True, selected=True); y += 82
    card(c, (L0, y, L1, y + 72), "Brightfen", "Booty Bay  ·  Level 41 Mage", True); y += 82
    c.header((L0, y, L1, y + 36), "Offline  (3)"); y += 46
    for n, w in (("Grimtusk", "Last online 2 days ago"), ("Kaelix", "Last online 5 days ago"), ("Rogmar", "Last online 3 weeks ago")):
        card(c, (L0, y, L1, y + 72), n, w, False); y += 82
    scrollbar(c, box[2] - 26, box[1] + 230, box[3] - 100, box[1] + 230, box[1] + 520)
    c.d.line(c.P(box[0] + 22, box[3] - 84, box[2] - 22, box[3] - 84), fill=BLUE + (120,), width=SS)
    c.button(((box[0] + box[2]) / 2 - 125, box[3] - 66, (box[0] + box[2]) / 2 + 125, box[3] - 22), "Add Friend")
    return c.done()

if __name__ == '__main__':
    im = label(friends(), "2  Friends (game size)")
    im.save('/home/claude/aether-repo/mock/out_p2_friends.png'); print(im.size)
