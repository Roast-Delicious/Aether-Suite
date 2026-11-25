# Normalize backgrounds: three layers, one color each
from PIL import Image, ImageDraw
from talent_details import F
MED='/home/claude/aether-repo/AetherSkins/Media/'
GOLD=(255,176,0); BLUE=(77,166,255); NAVY=(19,40,74); FRAME=(12,14,19); PAGE=(35,75,115); TEXT=(230,236,245); DIM=(170,176,188)
def win(page):
    W,H=340,300; im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,W-1,H-1],10,fill=FRAME+(255,),outline=BLUE,width=2)
    d.text((W/2,16),"Quest window",font=F(13,'SemiBold'),fill=GOLD,anchor='mm')
    d.rectangle([12,32,W-12,58],fill=NAVY+(255,)); d.line([12,58,W-12,58],fill=GOLD)
    d.text((20,45),"Header strip (navy)",font=F(11),fill=GOLD,anchor='lm')
    if page=='tex': im.alpha_composite(Image.open(MED+'page_aether.tga').convert('RGBA').resize((W-24,170)),(12,66))
    else: d.rectangle([12,66,W-12,236],fill=PAGE+(255,))
    d.rectangle([12,66,W-12,236],outline=(61,110,176))
    d.text((22,76),"Reading page",font=F(13,'SemiBold'),fill=GOLD)
    for i,l in enumerate(["Quest text, gossip, map quest list","and details: all the same page."]): d.text((22,98+i*15),l,font=F(11),fill=TEXT)
    d.rectangle([12,244,W-12,288],fill=NAVY+(255,)); d.rectangle([12,244,W-12,288],outline=(61,110,176))
    d.text((22,258),"Panel / box (navy): rewards, lists",font=F(11),fill=TEXT)
    return im
out=Image.new('RGBA',(1100,440),(30,34,44,255)); d=ImageDraw.Draw(out)
d.text((20,12),"One look everywhere: 3 layers, one color each",font=F(20,'SemiBold'),fill=GOLD)
for i,(c,n) in enumerate(((FRAME,"Frame  12,14,19"),(NAVY,"Panel  19,40,74"),(PAGE,"Page  35,75,115"))):
    d.rounded_rectangle([20+i*180,44,48+i*180,68],4,fill=c,outline=BLUE); d.text((56+i*180,56),n,font=F(13),fill=DIM,anchor='lm')
for i,(p,t) in enumerate((('flat',"A  Flat Aether blue page everywhere (recommended)"),('tex',"B  Textured Aether page everywhere"))):
    x=20+i*560; d.text((x,90),t,font=F(15),fill=DIM); out.alpha_composite(win(p),(x,120))
out.convert('RGB').save('out_bg_tiers.png')
