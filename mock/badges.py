from PIL import Image, ImageDraw, ImageFont, ImageFilter
K=1.15; SS=8                      # px per unit at actual size; supersampling
MED='/home/claude/brand/AetherFrames/Media/'
FIRA=MED+'FiraSans-Bold.ttf'
rim=Image.open(MED+'badge_rim.tga').convert('RGBA'); disc=Image.open(MED+'badge_disc.tga').convert('RGBA')
DIFF=[("red","37",(1,0.13,0.13)),("orange","36",(1,0.5,0.13)),("yellow","34",(1,0.82,0)),
      ("green","30",(0.25,0.75,0.25)),("gray","22",(0.55,0.55,0.55)),("red","??",(1,0.13,0.13))]
DARKN=(0.07,0.07,0.09); DARKD=(0.043,0.051,0.071)
CORAL=(1,0.45,0.40)
def tint(img,c,size):
    im=img.resize((size,size),Image.LANCZOS); a=im.split()[3]
    out=Image.new('RGBA',im.size,tuple(int(v*255) for v in c)+(255,)); out.putalpha(a); return out
def C(c): return tuple(int(v*255) for v in c)
def badge(opt, name, txt, col):
    BD,RD=20,23
    S=int(RD*K*SS); im=Image.new('RGBA',(S,S),(0,0,0,0))
    im.alpha_composite(tint(rim,(0.04,0.04,0.055),S))
    d_px=int(BD*K*SS); off=(S-d_px)//2
    numc=DARKN; stroke=0
    if opt=="B":
        im.alpha_composite(tint(disc,col,d_px),(off,off))
        inner=int((BD-4)*K*SS); o2=(S-inner)//2
        im.alpha_composite(tint(disc,DARKD,inner),(o2,o2))
        numc=col
    else:
        c=col
        if opt=="C" and name=="red": c=CORAL
        im.alpha_composite(tint(disc,c,d_px),(off,off))
        if opt=="A" and name in ("red","orange"): numc=(1,1,1); stroke=1
    size=11 if len(txt)<=2 else 9
    f=ImageFont.truetype(FIRA,int(size*K*SS))
    d=ImageDraw.Draw(im)
    d.text((S/2,S/2+0.3*K*SS),txt,font=f,fill=C(numc)+(255,),anchor='mm',
           stroke_width=int(stroke*K*SS),stroke_fill=(10,10,12,255))
    return im.resize((int(RD*K),int(RD*K)),Image.LANCZOS)
rows=[("Now","now"),("A  White number on red and orange","A"),("B  Dark badge, colored ring and number","B"),("C  Lighter red","C")]
# actual-size sheet on in-game ground
cellW,cellH=44,40; left=8; labelH=16
W=left+cellW*6+8; H=len(rows)*(cellH+labelH)+10
bg=Image.open('/tmp/v4/f_057.png').convert('RGBA').crop((1350,560,1350+W,560+H))
sheet=bg.copy(); d=ImageDraw.Draw(sheet)
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',10)
for r,(label,opt) in enumerate(rows):
    y=6+r*(cellH+labelH)
    d.text((left,y),label,font=lf,fill=(255,255,255),stroke_width=1,stroke_fill=(0,0,0))
    for i,(name,txt,col) in enumerate(DIFF):
        b=badge(opt,name,txt,col)
        sheet.alpha_composite(b,(left+i*cellW+(cellW-b.width)//2, y+labelH+4))
sheet=sheet.convert('RGB'); sheet.save('/tmp/badges_actual.png')
sheet.resize((W*3,H*3),Image.LANCZOS).save('/tmp/badges_3x.png')
print(sheet.size)
