# Map quest DETAILS page: A = parchment-free Aether page (like the NPC quest
# window), B = flat Aether blue (like the quest list behind it)
from PIL import Image, ImageDraw
from talent_details import F
MED = '/home/claude/aether-repo/AetherSkins/Media/'
GOLD=(255,176,0); BLUE=(77,166,255); NAVY=(19,40,74); TEXT=(230,236,245); DIM=(170,176,188)
def panel(kind):
    W,H=308,502; im=Image.new('RGBA',(W,H),(14,20,32,255)); d=ImageDraw.Draw(im)
    # back strip
    d.rectangle([0,0,W,40],fill=NAVY+(255,)); d.line([0,40,W,40],fill=BLUE,width=1)
    d.rounded_rectangle([10,9,100,31],4,fill=(30,60,105,255),outline=BLUE); d.text((55,20),"Back",font=F(12,'SemiBold'),fill=TEXT,anchor='mm')
    # page
    if kind=='A':
        pg=Image.open(MED+'page_aether.tga').convert('RGBA').resize((W-8,330)); im.alpha_composite(pg,(4,46))
    else:
        d.rectangle([4,46,W-4,376],fill=(35,75,115,255))
    d.rectangle([4,46,W-4,376],outline=(61,110,176),width=1)
    y=56; d.text((14,y),"Lost Shipping Crate",font=F(15,'SemiBold'),fill=GOLD); y+=22
    for l in ["Deliver the Lost Shipping Crate to Friz","Frazzlespark at Powderfuse Port in the","Riverglades."]:
        d.text((14,y),l,font=F(11),fill=TEXT); y+=14
    y+=10; d.text((14,y),"Description",font=F(15,'SemiBold'),fill=GOLD); y+=22
    for l in ["<A handwritten label appears on the side","of the crate. On the right side is a map","with a large red circle along a southeast-","ern shoreline north of a poorly drawn","temple surrounded by water...>","","PROPERTY OF FRIZ FRAZZLESPARK","POWDERFUSE PORT"]:
        d.text((14,y),l,font=F(11),fill=TEXT); y+=14
    # scroll bar
    d.rounded_rectangle([W-12,52,W-8,370],2,fill=(26,46,82,255)); d.rounded_rectangle([W-12,60,W-8,250],2,fill=GOLD)
    # rewards
    d.rectangle([4,384,W-4,458],fill=NAVY+(255,)); d.rectangle([4,384,W-4,458],outline=(61,110,176))
    d.text((W/2,396),"Rewards",font=F(14,'SemiBold'),fill=GOLD,anchor='mm')
    d.text((14,410),"You will receive:",font=F(11),fill=DIM)
    d.rounded_rectangle([14,426,140,452],4,fill=(14,26,46,255),outline=BLUE)
    d.rounded_rectangle([16,428,40,450],3,fill=(60,40,110,255)); d.text((28,439),"XP",font=F(11,'Bold'),fill=TEXT,anchor='mm')
    d.text((48,439),"290",font=F(12),fill=TEXT,anchor='lm')
    # buttons
    for i,(n,on) in enumerate((("Abandon",1),("Share",0),("Untrack",1))):
        x=4+i*101; d.rounded_rectangle([x,468,x+98,492],4,fill=(30,60,105,255) if on else (22,32,50,255),outline=BLUE if on else (60,70,90))
        d.text((x+49,480),n,font=F(12,'SemiBold'),fill=TEXT if on else (110,116,128),anchor='mm')
    return im
pa,pb=panel('A'),panel('B')
out=Image.new('RGBA',(1360,1150),(16,18,24,255)); d=ImageDraw.Draw(out)
d.text((20,12),"Map quest details page — game size, then 2x",font=F(22,'SemiBold'),fill=GOLD)
for i,(p,t) in enumerate(((pa,"A  Aether page (like the NPC quest window)"),(pb,"B  Aether blue (like the quest list behind it)  — recommended"))):
    x=20+i*680; d.text((x,48),t,font=F(15),fill=DIM)
    out.alpha_composite(p,(x,80)); out.alpha_composite(p.resize((616,1004*0+1004//2*2)).crop((0,0,616,1004)).resize((308*2,502*2)).crop((0,0,616,1004)) if False else p.resize((616,1004)).crop((0,0,616,560)),(x,590))
out.convert('RGB').save('out_maplog_details.png'); print(out.size)
