# Collections tab glyphs (user Nov 25 12:19), same style as the profession set
import math
from PIL import Image, ImageDraw
from talent_details import F
import profs_flat as PF
GOLD=PF.GOLD; NAVY=PF.NAVY; BLUE=PF.BLUE; DIM=PF.DIM
def glyph(d, kind, cx, cy, r, C, BG=NAVY):
    if kind == 'mount':      # horseshoe
        w = int(r*.32)
        d.arc([cx-r*.8,cy-r*.85,cx+r*.8,cy+r*.75], 140, 400, fill=C, width=w)
        for s in (-1,1):
            d.rectangle([cx+s*r*.62-r*.2,cy+r*.45,cx+s*r*.62+r*.2,cy+r*.8], fill=C)
        for a in (200,240,300,340):
            x = cx+math.cos(math.radians(a))*r*.64; y = cy-r*.05+math.sin(math.radians(a))*r*.64
            d.ellipse([x-r*.06,y-r*.06,x+r*.06,y+r*.06], fill=BG)
    elif kind == 'pet':      # paw print
        d.ellipse([cx-r*.5,cy-r*.05,cx+r*.5,cy+r*.8], fill=C)
        for x,y in ((-.72,-.2),(-.3,-.72),(.3,-.72),(.72,-.2)):
            d.ellipse([cx+r*(x-.2),cy+r*(y-.24),cx+r*(x+.2),cy+r*(y+.24)], fill=C)
    elif kind == 'toy':      # gift box
        d.rectangle([cx-r*.85,cy-r*.3,cx+r*.85,cy+r*.05], fill=C)
        d.rectangle([cx-r*.7,cy+r*.12,cx+r*.7,cy+r*.9], fill=C)
        d.rectangle([cx-r*.1,cy-r*.3,cx+r*.1,cy+r*.9], fill=BG)
        for s in (-1,1):
            d.ellipse([cx+s*r*.35-r*.3,cy-r*.85,cx+s*r*.35+r*.3,cy-r*.35], outline=C, width=max(2,int(r*.14)))
    elif kind == 'heirloom': # crown
        d.polygon([(cx-r*.85,cy+r*.55),(cx-r*.85,cy-r*.5),(cx-r*.42,cy),(cx,cy-r*.8),(cx+r*.42,cy),(cx+r*.85,cy-r*.5),(cx+r*.85,cy+r*.55)], fill=C)
        d.rectangle([cx-r*.85,cy+r*.65,cx+r*.85,cy+r*.85], fill=C)
    elif kind == 'appearance': # tunic on a hanger
        d.arc([cx-r*.2,cy-r*1.0,cx+r*.2,cy-r*.6], 180, 360, fill=C, width=max(2,int(r*.1)))
        d.polygon([(cx-r*.35,cy-r*.65),(cx+r*.35,cy-r*.65),(cx+r*.95,cy-r*.25),(cx+r*.7,cy+r*.1),(cx+r*.5,cy-r*.05),(cx+r*.5,cy+r*.9),
                   (cx-r*.5,cy+r*.9),(cx-r*.5,cy-r*.05),(cx-r*.7,cy+r*.1),(cx-r*.95,cy-r*.25)], fill=C)
        d.polygon([(cx-r*.2,cy-r*.65),(cx+r*.2,cy-r*.65),(cx,cy-r*.35)], fill=BG)
KINDS=[('mount','Mounts'),('pet','Pets'),('toy','Toys'),('heirloom','Heirlooms'),('appearance','Appearances')]
def tile(kind, s, sel=False, SS=6):
    n=s*SS; im=Image.new('RGBA',(n,n),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,n-1,n-1],3*SS,fill=NAVY+(255,),outline=(GOLD if sel else BLUE)+(255,),width=(3 if sel else 1)*SS)
    glyph(d,kind,n/2,n/2,n*.32,GOLD+(255,)); return im.resize((s,s),Image.LANCZOS)
if __name__=='__main__':
    pf = Image.open('out_profs_flat.png').convert('RGBA').crop((0,0,1320,205))
    out=Image.new('RGBA',(1320,330),(16,18,24,255)); out.alpha_composite(pf,(0,0)); d=ImageDraw.Draw(out)
    d.text((20,214),"Collections tabs, same style",font=F(20,'SemiBold'),fill=GOLD)
    for i,(k,n) in enumerate(KINDS):
        x=30+i*84; out.alpha_composite(tile(k,36,sel=(k=='appearance')),(x+12,248)); out.alpha_composite(tile(k,72,sel=(k=='appearance')),(x+110*0+430+i*0,0)) if False else None
        out.alpha_composite(tile(k,72,sel=(k=='appearance')),(500+i*84,240))
        d.text((x+30,292),n,font=F(11),fill=DIM,anchor='ma')
    out.convert('RGB').save('out_glyphs_all.png'); print(out.size)
