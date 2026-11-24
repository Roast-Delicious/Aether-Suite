# Mockup: Friends and Progress Track windows in the Aether look (style A, Clean).
import sys; sys.path.insert(0, '/home/claude/mock')
from skins_lib import *
from PIL import Image, ImageDraw
WORLD = Image.open('/tmp/v4/f_057.png').convert('RGBA')
FR = Image.open('/mnt/user-data/uploads/05d4c094-image.png').convert('RGBA')
PT = Image.open('/mnt/user-data/uploads/ac51d26c-image.png').convert('RGBA')

def side_tabs(c, x, ys, icons, selected=0, size=64):
    for i, (y, ic) in enumerate(zip(ys, icons)):
        sel = i == selected
        Lr, d = c.layer()
        d.rounded_rectangle(c.P(x, y, x + size, y + size), u(6), fill=NAVY + (250,),
                            outline=(GOLD if sel else BLUE) + (255,), width=(2 if sel else 1) * SS)
        c.over(Lr)
        c.paste(c.recolor_icon(ic, GOLD if sel else WHITE), (x + 10, y + 10), (size - 20, size - 20))

def friends():
    bg = WORLD.crop((900, 150, 900 + 800, 150 + 1180)); c = Canvas(bg)
    box = (40, 60, 660, 1120)
    tabs = [FR.crop((648, 256, 700, 308)), FR.crop((648, 342, 700, 394)), FR.crop((648, 428, 700, 480)), FR.crop((648, 514, 700, 566))]
    side_tabs(c, 672, [250, 330, 410, 490], tabs, 0)
    c.window(box, "Friends")
    c.crest((86, 106), 40, FR.crop((27, 52, 85, 110)))
    c.close(634, 79)
    # Battletag bar: status dropdown + name + menu
    Lr, d = c.layer()
    d.rounded_rectangle(c.P(135, 102, 600, 142), u(5), fill=(10, 20, 38, 255), outline=(50, 95, 160, 255), width=SS)
    c.over(Lr)
    c.d.ellipse(c.P(150, 114, 166, 130), fill=(80, 200, 110, 255))
    c.tri(182, 122, 6, WHITE, 'down')
    c.text((388, 122), "Soup", 19, SKY, 'Regular', 'rm'); c.text((388, 122), "#1552", 19, DIM, 'Regular', 'lm')
    c.button((606, 104, 642, 140), "", 18); c.menu(624, 122)
    # search + filter
    Lr, d = c.layer()
    d.rounded_rectangle(c.P(66, 168, 400, 200), u(4), fill=(6, 9, 15, 255), outline=(50, 95, 160, 255), width=SS)
    c.over(Lr)
    c.text((82, 184), "Search for keywords", 16, DIM, 'Regular', 'lm')
    c.button((430, 164, 630, 204), "Filter", 17); c.tri(600, 184, 7, GOLD, 'right')
    # list header
    c.header((66, 236, 630, 270), "Friends List 1/2")
    # friends
    Lr, d = c.layer()
    d.rounded_rectangle(c.P(66, 286, 610, 386), u(5), fill=BLUE + (45,), outline=BLUE + (150,), width=SS)
    d.rounded_rectangle(c.P(66, 396, 610, 496), u(5), fill=(20, 24, 32, 230))
    c.over(Lr)
    c.d.ellipse(c.P(74, 294, 86, 306), fill=(80, 200, 110, 255))
    c.d.ellipse(c.P(74, 404, 86, 416), fill=(110, 115, 125, 255))
    c.text((92, 322), "Itdrtyndere", 21, SKY, 'Regular', 'lm'); c.text((92, 352), "In App", 17, DIM, 'Regular', 'lm')
    c.text((92, 432), "FunkyMonk", 21, (140, 145, 155), 'Regular', 'lm'); c.text((92, 462), "Offline", 17, (110, 115, 125), 'Regular', 'lm')
    c.paste(c.recolor_icon(FR.crop((488, 336, 524, 372)), SKY), (500, 318), (34, 34))
    for y in (318, 428):
        c.button((548, y, 590, y + 40), "", 10)
        c.paste(c.recolor_icon(FR.crop((536, 342, 572, 378)), WHITE), (552, y + 3), (34, 34))
    # scrollbar
    Lr, d = c.layer(); d.rounded_rectangle(c.P(620, 290, 626, 1010), u(3), fill=(30, 45, 70, 255)); c.over(Lr)
    c.button((230, 1044, 470, 1084), "Add New Friend", 18)
    return c.done()

def progress():
    bg = WORLD.crop((300, 200, 300 + 1580, 200 + 1060)); c = Canvas(bg)
    box = (40, 60, 1440, 960)
    tabs = [PT.crop((1404, 126, 1462, 184)), PT.crop((1404, 212, 1462, 270)), PT.crop((1404, 296, 1462, 354))]
    side_tabs(c, 1452, [150, 232, 314], tabs, 0)
    c.window(box, "Progress Track")
    c.crest((86, 106), 40, PT.crop((18, 20, 86, 88)))
    c.close(1414, 79)
    # the points medal: round crest, white number, gold chevrons
    c.crest((740, 260), 78)
    c.text((740, 258), "2", 64, WHITE, 'Bold', 'mm', outline=True)
    c.text((740, 384), "Legacy Points", 26, WHITE, 'SemiBold', 'mm')
    # progress pill with gold milestone marks
    x0, x1 = 110, 1370; y0, y1 = 456, 476
    c.bar((x0, y0, x1, y1), (262 - 110) * 2 / 15 / (1370 - 110), BLUE, None, pill=True)
    centers = [262, 579, 896, 1213]
    for m, cx in zip((15, 25, 40, 55), centers):
        mx = cx
        Lr, d = c.layer(); d.line(c.P(mx, y0 - 4, mx, y1 + 4), fill=GOLD + (255,), width=2 * SS); c.over(Lr)
    # reward cards
    names = [("Holstered Replica", "Ironforge Air Rifle"), ("Spectral Bear", "Cub"), ("Spectral Bear", "Tabard"), ("Reins of the", "Spectral Bear")]
    icons = [PT.crop((180, 560, 278, 658)), PT.crop((496, 560, 594, 658)), PT.crop((812, 560, 910, 658)), PT.crop((1129, 560, 1227, 658))]
    for cx, m, nm, ic in zip(centers, (15, 25, 40, 55), names, icons):
        bx = (cx - 145, 520, cx + 145, 860)
        Lr, d = c.layer()
        d.rounded_rectangle(c.P(*bx), u(6), fill=(16, 22, 34, 255), outline=(55, 100, 165, 255), width=SS)
        d.rounded_rectangle(c.P(bx[0] + 4, bx[1] + 4, bx[2] - 4, bx[3] - 4), u(5), outline=(55, 100, 165, 70), width=SS)
        c.over(Lr)
        # milestone diamond: navy with a gold rim, white number
        Lr, d = c.layer(); X, Y = c.P(cx, 520); r = 26 * SS
        d.polygon([(X, Y - r), (X + r, Y), (X, Y + r), (X - r, Y)], fill=NAVY + (255,), outline=GOLD + (255,), width=2 * SS)
        c.over(Lr)
        c.text((cx, 520), str(m), 18, WHITE, 'SemiBold', 'mm')
        # icon well with a blue rim
        Lr, d = c.layer(); d.rounded_rectangle(c.P(cx - 52, 586, cx + 52, 690), u(5), fill=(5, 7, 12, 255), outline=BLUE + (200,), width=SS); c.over(Lr)
        c.paste(ic, (cx - 47, 591), (94, 94))
        c.text((cx, 728), nm[0], 20, DIM, 'Regular', 'mm'); c.text((cx, 754), nm[1], 20, DIM, 'Regular', 'mm')
    return c.done()

if __name__ == '__main__':
    friends().save('/tmp/sk/friends_A.png'); progress().save('/tmp/sk/progress_A.png'); print('ok')
