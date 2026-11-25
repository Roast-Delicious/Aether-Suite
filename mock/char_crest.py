# Character window crest (user Nov 25 12:40): A your face, B flat helmet
from PIL import Image, ImageDraw
from talent_details import F
GOLD=(255,176,0); BLUE=(77,166,255); NAVY=(19,40,74); DIM=(170,176,188)
shot = Image.open('/mnt/user-data/uploads/2cd4fc1e-image.png').convert('RGBA')
face = shot.crop((979, 100, 1035, 160)).resize((120,110), Image.LANCZOS)
def crest(kind, S=96, SS=4):
    n=S*SS; im=Image.new('RGBA',(n,n),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,n-1,n-1], fill=NAVY+(255,), outline=BLUE+(255,), width=3*SS)
    if kind=='face':
        f = face.resize((int(n*.95),int(n*.95)))
        m = Image.new('L', f.size, 0); ImageDraw.Draw(m).ellipse([0,0,f.size[0]-1,f.size[1]-1], fill=255)
        im.paste(f, (int(n*.025),int(n*.025)), m)
        ImageDraw.Draw(im).ellipse([0,0,n-1,n-1], outline=BLUE+(255,), width=3*SS)
    else:
        cx, cy, r = n/2, n/2, n*.3
        d.pieslice([cx-r,cy-r*1.05,cx+r,cy+r*.95], 180, 360, fill=GOLD+(255,))
        d.rectangle([cx-r,cy-r*.05,cx+r,cy+r*.75], fill=GOLD+(255,))
        d.rectangle([cx-r*.62,cy+r*.05,cx+r*.62,cy+r*.28], fill=NAVY+(255,))       # eye slit
        d.rectangle([cx-r*.1,cy+r*.28,cx+r*.1,cy+r*.75], fill=GOLD+(255,))
        d.polygon([(cx-r*.1,cy+r*.28),(cx-r*.45,cy+r*.28),(cx-r*.45,cy+r*.75),(cx-r*.1,cy+r*.75)], fill=NAVY+(255,))
        d.polygon([(cx+r*.1,cy+r*.28),(cx+r*.45,cy+r*.28),(cx+r*.45,cy+r*.75),(cx+r*.1,cy+r*.75)], fill=NAVY+(255,))
        d.rectangle([cx-r*.08,cy-r*1.3,cx+r*.08,cy-r*.9], fill=GOLD+(255,))
    return im.resize((S,S), Image.LANCZOS)
out=Image.new('RGBA',(760,330),(16,18,24,255)); d=ImageDraw.Draw(out)
d.text((20,12),"Character window crest — game size, then 2x",font=F(20,'SemiBold'),fill=GOLD)
for i,(k,t) in enumerate((('face',"A  Your character's face (recommended)"),('flat',"B  Flat helmet, like the other windows"))):
    x=20+i*380; d.text((x,50),t,font=F(15),fill=DIM)
    out.alpha_composite(crest(k,62),(x+10,100)); out.alpha_composite(crest(k,180),(x+110,90))
out.convert('RGB').save('out_char_crest.png')
