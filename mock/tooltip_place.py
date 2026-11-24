# Mockup: where the default tooltip goes (instead of bottom right, over the meter).
from PIL import Image, ImageDraw, ImageFont
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; R='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
S=1.58  # px per UI unit in the user's screenshot
base=Image.open('/tmp/v4/f_057.png').convert('RGBA')
LINES=[("Moonsteel Broadsword",(30,255,0),B,15),("Binds when equipped",(255,255,255),R,12),
       ("Two-Hand                    Sword",(255,255,255),R,12),("71 - 107 Damage      Speed 3.40",(255,255,255),R,12),
       ("(26.2 damage per second)",(255,255,255),R,12),("+12 Strength",(255,255,255),R,12),
       ("Durability 100 / 100",(255,255,255),R,12),("Requires Level 35",(255,255,255),R,12)]
def tooltip():
    w=int(215*S); lh=[int(l[3]*S*1.25) for l in LINES]; h=int(sum(lh)+16*S)
    t=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(t)
    d.rounded_rectangle((0,0,w-1,h-1),radius=int(4*S),fill=(8,8,20,225),outline=(150,150,160,255),width=2)
    y=int(8*S)
    for (txt,col,f,sz),hh in zip(LINES,lh):
        d.text((int(9*S),y),txt,font=ImageFont.truetype(f,int(sz*S*0.82)),fill=col); y+=hh
    return t
T=tooltip()
QX=int(1620*1.15)            # quest list's left edge
OPT={'A':(QX-8-T.width,int(390*1.15)),          # left of quest list, tops aligned
     'B':(QX-8-T.width,720-T.height//2),        # left of quest list, centered mid-screen
     'C':(int(1932*1.15)-T.width,int(560*1.15))}# under the quest list, same column
def shot(k,label):
    im=base.copy(); x,y=OPT[k]; im.alpha_composite(T,(x,y))
    d=ImageDraw.Draw(im); d.rectangle((0,0,560,70),fill=(0,0,0,200))
    d.text((16,10),label,font=ImageFont.truetype(B,40),fill=(255,176,0)); return im
names={'A':'A: beside quests, top','B':'B: beside quests, middle','C':'C: under quests'}
for k in OPT:
    shot(k,names[k]).convert('RGB').resize((1152,720),Image.LANCZOS).save(f'/home/claude/tt_{k}.png')
im=shot('B',''); x,y=OPT['B']
im.crop((x-260,y-120,base.width,y+T.height+160)).convert('RGB').save('/home/claude/tt_B_actual.png')
