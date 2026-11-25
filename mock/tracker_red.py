# On-screen quest tracker: Blizzard red vs our lighter red (user 14:30)
from PIL import Image, ImageDraw
from talent_details import F
GOLD=(255,176,0); TXT=(230,236,245); DIM=(170,176,188); NAVY=(19,40,74)
bg=Image.open('/mnt/user-data/uploads/8e49307c-image.png').convert('RGBA').crop((1040,420,1153,834)).resize((360,520))
def panel(red):
    im=bg.copy(); d=ImageDraw.Draw(im); y=16
    def q(t,c,o):
        nonlocal y
        d.ellipse([10,y,26,y+16],fill=NAVY+(240,),outline=GOLD,width=2)
        sh=Image.new('RGBA',im.size,(0,0,0,0)); sd=ImageDraw.Draw(sh)
        for dx,dy in ((1,1),(-1,1),(1,-1),(-1,-1)): sd.text((34+dx,y+dy),t,font=F(14,'SemiBold'),fill=(0,0,0,255))
        for dx,dy in ((1,1),(-1,1),(1,-1),(-1,-1)): sd.text((44+dx,y+19+dy),o,font=F(12),fill=(0,0,0,255))
        im.alpha_composite(sh); d.text((34,y),t,font=F(14,'SemiBold'),fill=c); d.text((44,y+19),o,font=F(12),fill=TXT); y+=46
    q("[60] Craftsman's Writ",red,"- Ready for turn-in")
    q("[41] Marg Speaks",(255,150,84),"- 0/1 Jeweled Pendant")
    q("[38] Call to Arms",GOLD,"- 0/10 Boulderfist Brute slain")
    q("[44] Horde Trauma",red,"- 0/1 Hammerfall reached")
    q("[33] Supply and Demand",(64,192,64),"- Ready for turn-in")
    return im
out=Image.new('RGBA',(780,600),(16,18,24,255)); d=ImageDraw.Draw(out)
d.text((20,10),"Quest tracker over the game world (game size)",font=F(20,'SemiBold'),fill=GOLD)
for i,(c,t) in enumerate((((255,26,26),"Blizzard default red"),((255,96,88),"Our lighter red"))):
    x=20+i*390; d.text((x,46),t,font=F(14),fill=DIM); out.alpha_composite(panel(c),(x,72))
out.convert('RGB').save('out_tracker_red.png')
