# 1C with the locked talent in navy blue instead of the gold-on-navy look
# (user, Nov 25 07:05). Locked = the grayscale icon mapped from deep navy
# to a muted blue: no gold, so gold only ever means "maxed".
import numpy as np
from PIL import Image, ImageDraw
import talent_states as TS
from talent_details import F, GOLD, BLUE

DEEP = np.array([8, 18, 38.]); MID = np.array([60, 100, 160.])
def navy_icon(ic, lift):
    g = TS.lum(ic)[..., None]
    return DEEP + g * (MID - DEEP) * lift

def tile_navy(ic, S, lift, border):
    a = navy_icon(ic, lift)
    im = TS.tile(a, border=border, S=S)
    return im

W, H = 1000, 560
sheet = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
d.text((24, 18), "1C with navy blue for locked talents", font=F(28, 'SemiBold'), fill=GOLD)
d.text((24, 60), "Locked talents (right) in three navy strengths. Can take and not taken as in 1C.  2x zoom, then game size.", font=F(17), fill=(170, 176, 188))
can = TS.tile(TS.BOW, border=(140, 175, 215), glow=BLUE, S=112); can_s = TS.tile(TS.BOW, border=(140, 175, 215), glow=BLUE, S=64)
nt = TS.tile(TS.LION, border=(90, 110, 140), fx='gray', dim=0.2, S=112); nt_s = TS.tile(TS.LION, border=(90, 110, 140), fx='gray', dim=0.2, S=64)
d.text((40, 110), "Can take", font=F(18, 'SemiBold'), fill=(235, 238, 245)); sheet.alpha_composite(can, (40, 140)); sheet.alpha_composite(can_s, (170, 164))
d.text((40, 290), "Not taken", font=F(18, 'SemiBold'), fill=(235, 238, 245)); sheet.alpha_composite(nt, (40, 320)); sheet.alpha_composite(nt_s, (170, 344))
for i, (lift, name) in enumerate(((0.8, "Dark navy"), (1.15, "Navy (my pick)"), (1.6, "Lighter navy"))):
    x = 330 + i * 225
    d.text((x, 110), name, font=F(17, 'SemiBold'), fill=(235, 238, 245))
    b = (40, 60, 92)
    big = tile_navy(TS.LOCK, 112, lift, b); sm = tile_navy(TS.LOCK, 64, lift, b)
    sheet.alpha_composite(big, (x, 140)); sheet.alpha_composite(sm, (x + 128, 164))
d.text((330, 300), "Gold now only means maxed; blue frames and glows mean\nsome points or ready to spend; navy means out of reach.",
       font=F(17), fill=(170, 176, 188))
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_talent_1c.png'); print(sheet.size)
