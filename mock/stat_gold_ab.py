# Mockup: option D with the Aether chevron accent instead of a diamond.
import numpy as np
from PIL import Image, ImageDraw, ImageFont
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; R='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
MED='/home/claude/brand/AetherFrames/Media/'
S=1.58; GOLD=(255,176,0); W=(255,255,255); GRN=(30,255,0)
def tint(name,px,col):
    a=np.array(Image.open(MED+name).convert('RGBA').resize((px,px),Image.LANCZOS))[...,3]
    im=np.zeros((px,px,4),np.uint8); im[...,:3]=col; im[...,3]=a; return Image.fromarray(im)
LINES=[("Mottled Hide Leggings",GRN,B,15,0),("Binds when equipped",W,R,12,0),
       ("Legs                          Leather",W,R,12,0),("112 Armor",W,R,12,0),
       ("+8 Agility",W,R,12,1),("+6 Stamina",W,R,12,1),("+3 Intellect",W,R,12,0),
       ("Durability 75 / 75",W,R,12,0),("Requires Level 34",W,R,12,0),
       ("Equip: +16 Attack Power.",GRN,R,12,1)]
def tip(icon_units, art='chev58_right', n=1, step=0.55, gold_equip=True):
    w=int(225*S); lh=[int(l[3]*S*1.25) for l in LINES]; h=int(sum(lh)+16*S)
    t=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(t)
    d.rounded_rectangle((0,0,w-1,h-1),radius=int(4*S),fill=(8,8,20,235),outline=(150,150,160,255),width=2)
    px=int(icon_units*S); dark=tint(art+'_dark.tga',px,(0,0,0)); gold=tint(art+'_gold.tga',px,GOLD)
    y=int(8*S); x0=int(9*S)
    for (txt,col,f,sz,key),hh in zip(LINES,lh):
        font=ImageFont.truetype(f,int(sz*S*0.82)); x=x0
        if key and (col==W or gold_equip): col=GOLD
        if key:
            cy=y+hh//2-px//2-2; ex=x0+int(d.textlength(txt,font=font))+int(px*0.05); 
            for k in range(n): t.alpha_composite(dark,(ex+int(k*px*step),cy))
            for k in range(n): t.alpha_composite(gold,(ex+int(k*px*step),cy))
        d.text((x,y),txt,font=font,fill=col); y+=hh
    return t

bg=Image.open('/mnt/user-data/uploads/25ea1451-image.png').convert('RGBA').resize((564,811)).crop((0,300,400,640))
F=ImageFont.truetype(B,24)
cols=[]
for ge,lab in ((True,'A  all marked lines gold'),(False,'B  Equip lines stay green')):
    t=tip(20,'chev58_left',2,0.38,ge); p=bg.copy(); p.alpha_composite(t,((p.width-t.width)//2,(p.height-t.height)//2))
    z=t.resize((t.width*2,t.height*2),Image.LANCZOS)
    c=Image.new('RGBA',(z.width,40+p.height+20+z.height),(20,20,24,255))
    ImageDraw.Draw(c).text((4,6),lab,font=F,fill=GOLD); c.alpha_composite(p,(0,40)); c.alpha_composite(z,(0,60+p.height)); cols.append(c)
out=Image.new('RGBA',(cols[0].width*2+30,cols[0].height),(20,20,24,255))
for i,c in enumerate(cols): out.alpha_composite(c,(i*(c.width+30),0))
out.convert('RGB').save('/tmp/stat_gold.png')
