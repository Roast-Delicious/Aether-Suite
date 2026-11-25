# Red quest names on the near-black page: Blizzard's default red vs ours (user 14:28)
from PIL import Image, ImageDraw
from talent_details import F
GOLD=(255,176,0); NAVY=(19,40,74); DIM=(170,176,188); TXT=(230,236,245); PAGE=(10,11,14)
def panel(red):
    W,H=330,250; im=Image.new('RGBA',(W,H),PAGE+(255,)); d=ImageDraw.Draw(im); y=10
    def h(t):
        nonlocal y
        d.rectangle([6,y,W-6,y+24],fill=NAVY); d.line([6,y+24,W-6,y+24],fill=GOLD); d.text((14,y+12),t,font=F(15,'SemiBold'),fill=GOLD,anchor='lm'); y+=32
    def q(t,c,o):
        nonlocal y
        sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((25,y+1),t,font=F(14,'SemiBold'),fill=(0,0,0,230)); im.alpha_composite(sh)
        d.text((24,y),t,font=F(14,'SemiBold'),fill=c); d.text((34,y+18),o,font=F(12),fill=TXT); y+=42
    h("Crafting"); q("[60] Craftsman's Writ",red,"- Ready for turn-in")
    h("Dustwallow Marsh"); q("[41] Marg Speaks",(255,150,84),"- 0/1 Jeweled Pendant"); q("[38] Call to Arms",GOLD,"- 0/10 Boulderfist Brute slain")
    return im
out=Image.new('RGBA',(720,330),(16,18,24,255)); d=ImageDraw.Draw(out)
d.text((20,10),"Red quest names on the near-black page (game size)",font=F(20,'SemiBold'),fill=GOLD)
for i,(c,t) in enumerate((((255,96,88),"Now: our lighter red"),((255,26,26),"Blizzard default red"))):
    x=20+i*360; d.text((x,46),t,font=F(14),fill=DIM); out.alpha_composite(panel(c),(x,72))
out.convert('RGB').save('out_red_default.png')
