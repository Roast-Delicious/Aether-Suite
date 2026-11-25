# Red (far above your level) quest names on the map log's blue page
from PIL import Image, ImageDraw, ImageFilter
from talent_details import F
GOLD=(255,176,0); PAGE=(35,75,115); NAVY=(19,40,74); DIM=(170,176,188); TXT=(230,236,245)
RED=(255,32,32); ORG=(255,128,64); YEL=(255,210,0); GRN=(64,192,64)
def panel(mode):
    W,H=330,170; im=Image.new('RGBA',(W,H),PAGE+(255,)); d=ImageDraw.Draw(im)
    rows=[("[60] Craftsman's Writ",RED),("[41] Marg Speaks",ORG),("[38] Call to Arms",YEL),("[33] Supply and Demand",GRN)]
    for i,(t,c) in enumerate(rows):
        y=14+i*38; col=c
        if mode=='B' and c==RED: col=(255,112,104)
        if mode=='B' and c==ORG: col=(255,160,96)
        if mode in('A','C'):
            sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
            sd.text((20+1,y+1),t,font=F(15,'SemiBold'),fill=(0,0,0,230))
            if mode=='C': sd.text((20,y),t,font=F(15,'SemiBold'),fill=(0,0,0,255),stroke_width=2,stroke_fill=(8,14,26,255))
            im.alpha_composite(sh)
        d.text((20,y),t,font=F(15,'SemiBold'),fill=col)
        d.text((30,y+19),"- Ready for turn-in",font=F(12),fill=TXT)
    return im
out=Image.new('RGBA',(1100,300),(16,18,24,255)); d=ImageDraw.Draw(out)
d.text((20,10),"Red quest names on the blue map log (game size)",font=F(20,'SemiBold'),fill=GOLD)
for i,(m,t) in enumerate((('N',"Now"),('A',"A  Drop shadow"),('B',"B  Lighter red/orange (recommended)"),)):
    x=20+i*360; d.text((x,46),t,font=F(14),fill=DIM); out.alpha_composite(panel(m),(x,76))
out.convert('RGB').save('out_maplog_red.png')
