# Mockup: highlighting the stats that matter for your class in item tooltips.
from PIL import Image, ImageDraw, ImageFont
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; R='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
S=1.58; GOLD=(255,176,0); W=(255,255,255); GRN=(30,255,0)
LINES=[("Mottled Hide Leggings",GRN,B,15,0),("Binds when equipped",W,R,12,0),
       ("Legs                          Leather",W,R,12,0),("112 Armor",W,R,12,0),
       ("+8 Agility",W,R,12,1),("+6 Stamina",W,R,12,1),("+3 Intellect",W,R,12,0),
       ("Durability 75 / 75",W,R,12,0),("Requires Level 34",W,R,12,0),
       ("Equip: +16 Attack Power.",GRN,R,12,1)]
def tip(style):
    w=int(200*S); lh=[int(l[3]*S*1.25) for l in LINES]; h=int(sum(lh)+16*S)
    t=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(t)
    d.rounded_rectangle((0,0,w-1,h-1),radius=int(4*S),fill=(8,8,20,235),outline=(150,150,160,255),width=2)
    y=int(8*S); x0=int(9*S)
    for (txt,col,f,sz,key),hh in zip(LINES,lh):
        font=ImageFont.truetype(f,int(sz*S*0.82)); c=col; x=x0
        if key:
            if style=='A': c=GOLD
            if style=='B': d.rectangle((int(3*S),y+2,int(3*S)+3,y+hh-4),fill=GOLD)
            if style=='C': d.rectangle((2,y-1,w-3,y+hh-3),fill=(255,176,0,60))
            if style=='D':
                cx,cy=x0+5,y+hh//2-2
                d.polygon([(cx,cy-5),(cx+5,cy),(cx,cy+5),(cx-5,cy)],fill=GOLD); x=x0+14
        d.text((x,y),txt,font=font,fill=c); y+=hh
    return t
names={'A':'A  gold text','B':'B  gold bar at left','C':'C  soft gold band','D':'D  gold diamond'}
tips={k:tip(k) for k in names}
bg=Image.open('/tmp/v4/f_057.png').convert('RGBA').crop((1300,500,1300+380,500+340))
# actual size row
pad=20; tw=tips['A'].width; th=tips['A'].height
row=Image.new('RGBA',(4*(bg.width+pad),bg.height+50),(20,20,24,255)); d=ImageDraw.Draw(row)
for i,k in enumerate(names):
    p=bg.copy(); p.alpha_composite(tips[k],((p.width-tw)//2,(p.height-th)//2+10))
    row.alpha_composite(p,(i*(bg.width+pad),45)); d.text((i*(bg.width+pad)+6,8),names[k],font=ImageFont.truetype(B,24),fill=GOLD)
row.convert('RGB').save('/home/claude/stat_actual.png')
zoom=Image.new('RGBA',(4*(tw*2+pad),th*2+50),(20,20,24,255)); d=ImageDraw.Draw(zoom)
for i,k in enumerate(names):
    zoom.alpha_composite(tips[k].resize((tw*2,th*2),Image.LANCZOS),(i*(tw*2+pad),45))
    d.text((i*(tw*2+pad)+6,8),names[k],font=ImageFont.truetype(B,26),fill=GOLD)
zoom.convert('RGB').save('/home/claude/stat_zoom.png')
