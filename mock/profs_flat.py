# Profession glyphs, flat Aether gold (user Nov 25 12:17), plus the
# Professions window on our three background layers.
import math
from PIL import Image, ImageDraw
from talent_details import F
import sidetabs_flat as ST
GOLD=(255,176,0); BLUE=(77,166,255); NAVY=(19,40,74); FRAME=(12,14,19); PAGE=(35,75,115); TEXT=(230,236,245); DIM=(170,176,188)
def bar(cx, cy, a, L, w, off=0):
    dx, dy = math.cos(a), math.sin(a); px, py = -dy*w, dx*w
    return [(cx-dx*L+px+dx*off, cy-dy*L+py+dy*off), (cx+dx*L+px+dx*off, cy+dy*L+py+dy*off), (cx+dx*L-px+dx*off, cy+dy*L-py+dy*off), (cx-dx*L-px+dx*off, cy-dy*L-py+dy*off)]
def glyph(d, kind, cx, cy, r, C, BG=NAVY):
    lw = max(2, int(r*.14))
    if kind == 'overview':     # crossed hammer and pick
        ST.glyph(d, 'skills', cx, cy, r, C)
    elif kind == 'leather':    # stretched hide with stitches
        pts = [(cx-r*.8,cy-r*.75),(cx-r*.2,cy-r*.55),(cx+r*.2,cy-r*.85),(cx+r*.85,cy-r*.6),(cx+r*.6,cy),(cx+r*.85,cy+r*.65),
               (cx+r*.2,cy+r*.85),(cx-r*.2,cy+r*.55),(cx-r*.85,cy+r*.75),(cx-r*.6,cy)]
        d.polygon(pts, fill=C)
        for i in range(4):
            y = cy - r*.36 + i*r*.24; d.line([(cx-r*.12,y),(cx+r*.12,y+r*.08)], fill=BG, width=max(1,int(r*.09)))
    elif kind == 'skinning':   # skinning knife
        d.polygon([(cx-r*.85,cy+r*.85),(cx-r*.5,cy+r*.5),(cx-r*.35,cy+r*.65),(cx-r*.7,cy+r*1.0)], fill=C)   # handle
        d.polygon([(cx-r*.55,cy+r*.4),(cx+r*.25,cy-r*.75),(cx+r*.9,cy-r*.9),(cx+r*.55,cy-r*.2),(cx-r*.25,cy+r*.7)], fill=C)
        d.line([(cx-r*.62,cy+r*.48),(cx-r*.32,cy+r*.75)], fill=BG, width=lw)
    elif kind == 'firstaid':   # cross
        w = r*.32
        d.rectangle([cx-w,cy-r*.9,cx+w,cy+r*.9], fill=C); d.rectangle([cx-r*.9,cy-w,cx+r*.9,cy+w], fill=C)
    elif kind == 'fishing':    # hook with line
        lw = max(3, int(r*.26))
        d.line([(cx+r*.2,cy-r*1.0),(cx+r*.2,cy+r*.25)], fill=C, width=lw)
        d.arc([cx-r*.55,cy-r*.3,cx+r*.25,cy+r*.85], 0, 180, fill=C, width=lw)
        d.polygon([(cx-r*.55,cy+r*.27),(cx-r*.75,cy-r*.05),(cx-r*.38,cy+r*.1)], fill=C)
        d.ellipse([cx+r*.05,cy-r*1.0,cx+r*.35,cy-r*.75], outline=C, width=max(1,lw//2))
    elif kind == 'cooking':    # chef's hat
        for (x,y,s) in ((-.42,-.25,.38),(0,-.48,.45),(.42,-.25,.38)):
            d.ellipse([cx+r*(x-s),cy+r*(y-s),cx+r*(x+s),cy+r*(y+s)], fill=C)
        d.rectangle([cx-r*.55,cy-r*.2,cx+r*.55,cy+r*.55], fill=C)
        d.rectangle([cx-r*.6,cy+r*.62,cx+r*.6,cy+r*.88], fill=C)
    elif kind == 'blacksmith': # hammer
        d.polygon(bar(cx, cy, math.radians(-45), r*.9, r*.1, 0), fill=C)
        hx, hy = cx+r*.45, cy-r*.45
        d.polygon(bar(hx, hy, math.radians(45), r*.5, r*.24), fill=C)
    elif kind == 'mining':     # pick
        d.polygon(bar(cx, cy, math.radians(-45), r*.9, r*.1), fill=C)
        d.arc([cx-r*.95,cy-r*1.0,cx+r*.95,cy+r*.15], 200, 340, fill=C, width=int(r*.24))
    elif kind == 'herbalism':  # leaf
        d.chord([cx-r*.9,cy-r*.9,cx+r*.5,cy+r*.5], 0, 360, fill=C)
        d.polygon([(cx-r*.9,cy+r*.9),(cx+r*.9,cy-r*.9),(cx+r*.9,cy-r*.2),(cx-r*.2,cy+r*.9)], fill=C)
        d.line([(cx-r*.85,cy+r*.85),(cx+r*.45,cy-r*.45)], fill=BG, width=max(1,int(r*.1)))
    elif kind == 'alchemy':    # flask
        d.rectangle([cx-r*.18,cy-r*.95,cx+r*.18,cy-r*.3], fill=C); d.rectangle([cx-r*.3,cy-r*.98,cx+r*.3,cy-r*.85], fill=C)
        d.polygon([(cx-r*.18,cy-r*.3),(cx+r*.18,cy-r*.3),(cx+r*.85,cy+r*.85),(cx-r*.85,cy+r*.85)], fill=C)
        d.line([(cx-r*.45,cy+r*.35),(cx+r*.45,cy+r*.35)], fill=BG, width=max(1,int(r*.1)))
    elif kind == 'tailoring':  # spool of thread with a needle
        d.rectangle([cx-r*.75,cy-r*.85,cx+r*.35,cy-r*.65], fill=C); d.rectangle([cx-r*.75,cy+r*.65,cx+r*.35,cy+r*.85], fill=C)
        d.rectangle([cx-r*.6,cy-r*.65,cx+r*.2,cy+r*.65], fill=C)
        for i in range(5):
            y = cy - r*.5 + i*r*.25; d.line([(cx-r*.6,y),(cx+r*.2,y+r*.06)], fill=BG, width=max(1,int(r*.06)))
        d.polygon(bar(cx+r*.62, cy, math.radians(-75), r*.95, r*.06), fill=C)
    elif kind == 'enchanting': # rod with star
        d.polygon(bar(cx-r*.15, cy+r*.15, math.radians(-45), r*.8, r*.08), fill=C)
        sx, sy, R = cx+r*.5, cy-r*.5, r*.45
        d.polygon([(sx+math.cos(math.radians(a))*(R if i%2==0 else R*.42), sy+math.sin(math.radians(a))*(R if i%2==0 else R*.42)) for i,a in enumerate(range(-90,270,45))], fill=C)
    elif kind == 'engineering':# gear
        for i in range(8):
            a = math.radians(i*45); d.polygon(bar(cx+math.cos(a)*r*.62, cy+math.sin(a)*r*.62, a, r*.25, r*.17), fill=C)
        d.ellipse([cx-r*.68,cy-r*.68,cx+r*.68,cy+r*.68], fill=C); d.ellipse([cx-r*.25,cy-r*.25,cx+r*.25,cy+r*.25], fill=BG)
    elif kind == 'jewel':      # gem
        d.polygon([(cx-r*.85,cy-r*.3),(cx-r*.45,cy-r*.8),(cx+r*.45,cy-r*.8),(cx+r*.85,cy-r*.3),(cx,cy+r*.9)], fill=C)
        d.line([(cx-r*.85,cy-r*.3),(cx+r*.85,cy-r*.3)], fill=BG, width=max(1,int(r*.08)))
    elif kind == 'inscription':# quill
        d.polygon([(cx-r*.85,cy+r*.9),(cx+r*.05,cy-r*.45),(cx+r*.9,cy-r*.95),(cx+r*.6,cy+r*.05),(cx-r*.05,cy+r*.5)], fill=C)
        d.line([(cx-r*.85,cy+r*.9),(cx+r*.5,cy-r*.5)], fill=BG, width=max(1,int(r*.08)))
KINDS = [('overview','Overview'),('leather','Leatherworking'),('skinning','Skinning'),('firstaid','First Aid'),('fishing','Fishing'),('cooking','Cooking'),
         ('blacksmith','Blacksmithing'),('mining','Mining'),('herbalism','Herbalism'),('alchemy','Alchemy'),('tailoring','Tailoring'),('enchanting','Enchanting'),
         ('engineering','Engineering'),('jewel','Jewelcrafting'),('inscription','Inscription')]
def tile(kind, s, sel=False, SS=6):
    n = s*SS; im = Image.new('RGBA',(n,n),(0,0,0,0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,n-1,n-1], 3*SS, fill=NAVY+(255,), outline=(GOLD if sel else BLUE)+(255,), width=(3 if sel else 1)*SS)
    glyph(d, kind, n/2, n/2, n*.32, GOLD+(255,))
    return im.resize((s,s), Image.LANCZOS)
if __name__ == '__main__':
    out = Image.new('RGBA',(1320,820),(16,18,24,255)); d = ImageDraw.Draw(out)
    d.text((20,12),"Profession glyphs, flat Aether gold on navy (game size 36px, then 2x)",font=F(20,'SemiBold'),fill=GOLD)
    for i,(k,n) in enumerate(KINDS):
        x = 30 + i*84
        out.alpha_composite(tile(k,36,sel=(k=='overview')),(x+12,56))
        out.alpha_composite(tile(k,72,sel=(k=='overview')),(x-6,104))
        d.text((x+30,186),n,font=F(11),fill=DIM,anchor='ma')
    # overview window on the tiers
    X,Y = 30,230; d.text((X,Y),"Professions window: navy cards, gold bars, blue edges",font=F(16),fill=DIM); Y+=28
    d.rounded_rectangle([X,Y,X+700,Y+560],10,fill=FRAME,outline=BLUE,width=2)
    def card(x,y,w,h,title,rows,barw,val,mx):
        d.rectangle([x,y,x+w,y+h],fill=NAVY,outline=(61,110,176))
        d.text((x+14,y+10),title,font=F(15,'SemiBold'),fill=GOLD)
        for j,(k,nm,sub) in enumerate(rows):
            yy = y+38+j*44; out.alpha_composite(tile(k,36),(int(x+14),int(yy)))
            d.text((x+58,yy+2),nm,font=F(13),fill=TEXT); d.text((x+58,yy+19),sub,font=F(11),fill=DIM)
        bx, by = (x+200, y+48) if barw>250 else (x+14, y+40)
        if barw<=250: by = y+38
        d.rounded_rectangle([bx,by,bx+barw,by+16],8,fill=(14,26,46),outline=BLUE)
        d.rounded_rectangle([bx+2,by+2,bx+2+(barw-4)*val/mx,by+14],6,fill=GOLD)
        d.text((bx+barw/2,by+8),f"{title} {val}/{mx}",font=F(11,'SemiBold'),fill=(255,255,255),anchor='mm',stroke_width=2,stroke_fill=(10,16,28))
    card(X+10,Y+12,680,120,"Leatherworking",[('leather','Leatherworking','Expert')],440,165,225)
    card(X+10,Y+142,680,150,"Skinning",[('skinning','Tanning',''),('skinning','Skinning','Artisan')],440,247,300)
    for i,(k,n,v,m,sub) in enumerate((('cooking','Cooking',99,150,'Journeyman'),('fishing','Fishing',20,75,'Apprentice'),('firstaid','First Aid',225,225,'Expert'))):
        x = X+10+i*228; card(x,Y+302,218,246,n,[],190,v,m)
        out.alpha_composite(tile(k,36),(x+14,Y+490)); d.text((x+58,Y+492),n,font=F(13),fill=TEXT); d.text((x+58,Y+509),sub,font=F(11),fill=DIM)
    # recipe page note
    X2 = 770; d.text((X2,230),"Recipe page",font=F(16),fill=DIM)
    d.rectangle([X2,258,X2+260,620],fill=NAVY,outline=(61,110,176)); d.text((X2+10,266),"Recipe list (navy)",font=F(12),fill=TEXT)
    d.rectangle([X2+6,300,X2+254,320],fill=(30,60,105)); d.line([X2+6,320,X2+254,320],fill=GOLD); d.text((X2+16,310),"Camp Tent  (picked: blue + gold line)",font=F(11),fill=TEXT,anchor='lm')
    d.rectangle([X2+270,258,X2+530,620],fill=PAGE,outline=(61,110,176)); d.text((X2+280,266),"Recipe details (page blue)",font=F(12),fill=TEXT)
    out.convert('RGB').save('out_profs_flat.png'); print(out.size)
