# Four page-blue windows at the current blue and 20% brighter (user 13:51)
from PIL import Image, ImageDraw
from talent_details import F
GOLD=(255,176,0); BLUE=(77,166,255); NAVY=(19,40,74); FRAME=(12,14,19); TXT=(230,236,245); DIM=(170,176,188); EDGE=(61,110,176)
def win(title, W=300, H=330):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,W-1,H-1],9,fill=FRAME,outline=BLUE,width=2)
    d.rectangle([2,2,W-3,24],fill=NAVY); d.line([2,24,W-3,24],fill=GOLD)
    d.text((W/2,13),title,font=F(12,'SemiBold'),fill=GOLD,anchor='mm'); return im,d
def gossip(P):
    im,d=win("Urtharo"); d.rectangle([8,34,291,292],fill=P,outline=EDGE)
    d.text((18,44),"So many years of battle and slavery,",font=F(11),fill=TXT); d.text((18,58),"it feels good to have a home again.",font=F(11),fill=TXT)
    d.text((18,82),"I want to browse your goods.",font=F(11),fill=GOLD); d.text((18,100),"Train me.",font=F(11),fill=GOLD)
    d.rounded_rectangle([200,300,290,320],4,fill=(30,60,105),outline=BLUE); d.text((245,310),"Goodbye",font=F(11,'SemiBold'),fill=TXT,anchor='mm'); return im
def details(P):
    im,d=win("Map & Quest Log"); d.rectangle([8,34,291,50],fill=NAVY); d.rounded_rectangle([12,36,70,48],3,fill=(30,60,105),outline=BLUE); d.text((41,42),"Back",font=F(9),fill=TXT,anchor='mm')
    d.rectangle([8,56,291,230],fill=P,outline=EDGE); d.text((18,64),"Lost Shipping Crate",font=F(14,'SemiBold'),fill=GOLD)
    for i,l in enumerate(["Deliver the Lost Shipping Crate to Friz","Frazzlespark at Powderfuse Port."]): d.text((18,86+i*14),l,font=F(10),fill=TXT)
    d.text((18,124),"Description",font=F(14,'SemiBold'),fill=GOLD)
    for i,l in enumerate(["<A handwritten label appears on","the side of the crate...>"]): d.text((18,146+i*14),l,font=F(10),fill=TXT)
    d.rectangle([8,238,291,292],fill=NAVY,outline=EDGE); d.text((150,248),"Rewards",font=F(12,'SemiBold'),fill=GOLD,anchor='mm'); d.text((18,262),"XP  290",font=F(11),fill=TXT); return im
def mounts(P):
    im,d=win("Mounts"); d.rectangle([8,34,120,320],fill=P,outline=EDGE)
    for i,n in enumerate(["Cerulean Pride.","Veteran's Comp."]):
        y=44+i*40; d.rectangle([12,y,116,y+34],fill=NAVY,outline=EDGE); d.rectangle([15,y+3,43,y+31],fill=(190,195,205)); d.text((48,y+17),n,font=F(9),fill=GOLD,anchor='lm')
    d.rectangle([126,34,291,320],fill=P,outline=EDGE); d.text((136,46),"Cerulean Prideclaw",font=F(11),fill=TXT)
    d.ellipse([170,190,260,260],fill=(80,120,200)); return im
def spellbook(P):
    im,d=win("Spellbook"); d.rectangle([8,34,291,320],fill=P,outline=EDGE); d.text((22,46),"General",font=F(16),fill=TXT)
    for i,(n,s) in enumerate([("Attack",""),("Dodge","Passive"),("Berserking","Racial"),("Parry","Passive")]):
        x=22+(i%2)*140; y=84+(i//2)*50
        d.rectangle([x,y,x+30,y+30],fill=(60,60,70),outline=BLUE); d.text((x+38,y+4),n,font=F(12),fill=TXT); d.text((x+38,y+19),s,font=F(9),fill=DIM)
    return im
P=(35,75,115); P2=tuple(round(c*1.2) for c in P)
out=Image.new('RGBA',(1290,800),(40,34,30,255)); d=ImageDraw.Draw(out)
d.text((20,10),"Page blue in four windows: now (top) vs 20% brighter (bottom), game size",font=F(18,'SemiBold'),fill=GOLD)
for r,(p,lab) in enumerate(((P,"Now 35,75,115"),(P2,"20% brighter 42,90,138"))):
    y=50+r*370; d.text((20,y),lab,font=F(13),fill=DIM)
    for i,fn in enumerate((gossip,details,mounts,spellbook)): out.alpha_composite(fn(p),(20+i*318,y+22))
out.convert('RGB').save('out_page_windows.png'); print(out.size)
