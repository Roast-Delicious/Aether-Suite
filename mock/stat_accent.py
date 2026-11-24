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
def tip(icon_units):
    w=int(205*S); lh=[int(l[3]*S*1.25) for l in LINES]; h=int(sum(lh)+16*S)
    t=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(t)
    d.rounded_rectangle((0,0,w-1,h-1),radius=int(4*S),fill=(8,8,20,235),outline=(150,150,160,255),width=2)
    px=int(icon_units*S); dark=tint('chev58_right_dark.tga',px,(0,0,0)); gold=tint('chev58_right_gold.tga',px,GOLD)
    y=int(8*S); x0=int(4*S)
    for (txt,col,f,sz,key),hh in zip(LINES,lh):
        font=ImageFont.truetype(f,int(sz*S*0.82)); x=x0+int(px*1.0)
        if key:
            cy=y+hh//2-px//2-2; t.alpha_composite(dark,(x0,cy)); t.alpha_composite(gold,(x0,cy))
        d.text((x,y),txt,font=font,fill=col); y+=hh
    return t
t=tip(17)
bg=Image.open('/tmp/v4/f_057.png').convert('RGBA').crop((1300,500,1300+400,500+340))
p=bg.copy(); p.alpha_composite(t,((p.width-t.width)//2,(p.height-t.height)//2)); 
z=t.resize((t.width*2,t.height*2),Image.LANCZOS)
out=Image.new('RGBA',(p.width+z.width+30,max(p.height,z.height)),(20,20,24,255))
out.alpha_composite(p,(0,0)); out.alpha_composite(z,(p.width+30,0))
out.convert('RGB').save('/home/claude/stat_accent.png')
