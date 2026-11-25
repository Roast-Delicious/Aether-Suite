# Map quest log page: now vs 10% brighter, with the approved title colors
from PIL import Image, ImageDraw
from talent_details import F
GOLD=(255,176,0); NAVY=(19,40,74); DIM=(170,176,188); TXT=(230,236,245)
def panel(page):
    W,H=320,300; im=Image.new('RGBA',(W,H),page+(255,)); d=ImageDraw.Draw(im)
    y=10
    def head(t):
        nonlocal y
        d.rectangle([6,y,W-6,y+24],fill=NAVY); d.line([6,y+24,W-6,y+24],fill=GOLD); d.text((14,y+12),t,font=F(15,'SemiBold'),fill=GOLD,anchor='lm'); y+=32
    def quest(t,c,o):
        nonlocal y
        sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((25,y+1),t,font=F(14,'SemiBold'),fill=(0,0,0,230)); im.alpha_composite(sh)
        d.text((24,y),t,font=F(14,'SemiBold'),fill=c); d.text((34,y+18),o,font=F(12),fill=TXT); y+=42
    head("Crafting"); quest("[60] Craftsman's Writ",(255,96,88),"- Ready for turn-in")
    head("Dustwallow Marsh"); quest("[41] Marg Speaks",(255,150,84),"- 0/1 Jeweled Pendant"); quest("[38] Call to Arms",GOLD,"- 0/10 Boulderfist Brute slain"); quest("[33] Supply and Demand",(64,192,64),"- Ready for turn-in")
    return im
P=(35,75,115); P2=tuple(min(255,round(c*1.2)) for c in P); P3=tuple(min(255,round(c*1.4)) for c in P)
out=Image.new('RGBA',(1080,380),(16,18,24,255)); d=ImageDraw.Draw(out)
d.text((20,10),"Page blue: now, 20% and 40% brighter (game size)",font=F(20,'SemiBold'),fill=GOLD)
for i,(p,t) in enumerate(((P,"Now  35,75,115"),(P2,"20%% brighter  %d,%d,%d" % P2),(P3,"40%% brighter  %d,%d,%d" % P3))):
    x=20+i*360; d.text((x,46),t,font=F(14),fill=DIM); out.alpha_composite(panel(p),(x,72))
out.convert('RGB').save('out_page_bright.png'); print(P2)
