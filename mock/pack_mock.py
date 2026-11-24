from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC=Image.open('/mnt/user-data/uploads/85c1416a-image.png').convert('RGBA')
FD='/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
S=4
def F(w,px): return ImageFont.truetype(FD+w+'.ttf',int(px*S))
AMBER=(255,176,0); GOLDC=(255,206,60); SILV=(214,220,230); COPP=(232,146,90)
WHITE=(235,238,245); GRAY=(150,156,170); NAVY=(19,40,74); BG=(13,15,23)

def up(im): return im.resize((im.width*S,im.height*S),Image.LANCZOS)
def down(im): return im.resize((im.width//S,im.height//S),Image.LANCZOS)

def coin(d,cx,cy,r,base):
    r*=S; cx*=S; cy*=S
    dk=tuple(int(c*0.55) for c in base); lt=tuple(min(255,int(c*1.15+30)) for c in base)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=dk)
    d.ellipse([cx-r*0.82,cy-r*0.82,cx+r*0.82,cy+r*0.82],fill=base)
    d.ellipse([cx-r*0.55,cy-r*0.65,cx+r*0.05,cy-r*0.1],fill=lt)

def money(d,xr,cy,font,px,r,colored=True,gap=7):
    # right-aligned at xr; returns left x
    parts=[("14",GOLDC),("45",SILV),("19",COPP)]
    widths=[d.textlength(t,font=font)/S for t,_ in parts]
    total=sum(widths)+len(parts)*(3+2*r)+(len(parts)-1)*gap
    x=xr-total; left=x
    for (t,c),w in zip(parts,widths):
        d.text((x*S,cy*S),t,font=font,fill=c if colored else WHITE,anchor='lm',stroke_width=S//2,stroke_fill=(0,0,0))
        x+=w+3; coin(d,x+r,cy+0.5,r,c); x+=2*r+gap
    return left,total

def title_strip():
    # clean copy of the title strip area with the old money text removed
    im=SRC.crop((0,0,648,110)).copy()
    ImageDraw.Draw(im).rectangle([440,27,583,54],fill=NAVY+(255,))
    return im

def label(im,txt):
    out=Image.new('RGBA',(im.width,im.height+26),(30,32,40,255))
    out.alpha_composite(im,(0,26))
    ImageDraw.Draw(out).text((10,5),txt,font=ImageFont.truetype(FD+'SemiBold.ttf',15),fill=(255,255,255))
    return out

def stack(ims,pad=10,bg=(30,32,40,255)):
    w=max(i.width for i in ims); h=sum(i.height for i in ims)+pad*(len(ims)-1)
    out=Image.new('RGBA',(w,h),bg); y=0
    for i in ims: out.alpha_composite(i,(0,y)); y+=i.height+pad
    return out

# ---------- gold options ----------
now=label(SRC.crop((0,0,648,110)),"Now")

im=up(title_strip()); d=ImageDraw.Draw(im)
money(d,578,41,F('SemiBold',19),19,7.5)
opt1=label(down(im),"1. Bigger, coin-colored numbers")

im=up(title_strip()); d=ImageDraw.Draw(im)
f=F('SemiBold',19); left,total=money(d,568,41,f,19,7.5)
x0,x1,y0,y1=left-10,580,28,54
cap=Image.new('RGBA',im.size,(0,0,0,0)); cd=ImageDraw.Draw(cap)
cd.rounded_rectangle([x0*S,y0*S,x1*S,y1*S],radius=12*S,fill=(8,16,32,255),outline=AMBER+(170,),width=S)
im2=up(title_strip()); im2.alpha_composite(cap); d=ImageDraw.Draw(im2)
money(d,568,41,f,19,7.5)
opt2img=down(im2)
opt2=label(opt2img,"2. Same, in a coin capsule")

# option 4: tooltip under the capsule
base=SRC.crop((0,0,648,250)).copy()
base.alpha_composite(opt2img,(0,0))
im=up(base); d=ImageDraw.Draw(im)
tx0,ty0,tx1,ty1=350,58,620,170
d.rounded_rectangle([tx0*S,ty0*S,tx1*S,ty1*S],radius=6*S,fill=(10,14,24,245),outline=(70,130,220),width=S)
def row(y,a,b,cb,fa=F('Regular',14),fb=F('SemiBold',14)):
    d.text(((tx0+12)*S,y*S),a,font=fa,fill=GRAY,anchor='lm')
    d.text(((tx1-12)*S,y*S),b,font=fb,fill=cb,anchor='rm')
d.text(((tx0+12)*S,(ty0+16)*S),"Gold",font=F('SemiBold',15),fill=AMBER,anchor='lm')
row(ty0+40,"On hand","14g 45s 19c",WHITE)
row(ty0+62,"This session","+2g 13s 40c",(110,220,120))
row(ty0+84,"Per hour","+1g 78s",(110,220,120))
opt4=label(down(im),"4. Hover the gold: session gain or loss")

gold=stack([now,opt1,opt2,opt4])
gold.save('gold_actual.png')
gold.resize((gold.width*2,gold.height*2),Image.LANCZOS).crop((560,0,1296,gold.height*2)).save('gold_zoom.png')

# ---------- free slots section ----------
Y0=868; H=200
nowf=label(SRC.crop((0,Y0,648,Y0+H)),"Now")
slot=SRC.crop((26,901,84,960))
ink=SRC.crop((86,898,370,962))
def clean():
    im=SRC.crop((0,Y0,648,Y0+H)).copy()
    ImageDraw.Draw(im).rectangle([22,0,616,H-12],fill=BG+(255,))
    return im
def header(d,y,show=True):
    f=F('SemiBold',17); d.text((30*S,y*S),"Free slots",font=f,fill=AMBER,anchor='lm')
    w=d.textlength("Free slots",font=f)/S
    d.text(((30+w+8)*S,y*S),"22",font=f,fill=GRAY,anchor='lm')
    rx=30+w+8+d.textlength("22",font=f)/S+10
    if show:
        sf=F('Regular',14); sw=d.textlength("Show empty",font=sf)/S
        d.text((608*S,y*S),"Show empty",font=sf,fill=(110,170,255),anchor='rm')
        d.line([rx*S,y*S,(608-sw-10)*S,y*S],fill=(40,70,120),width=S)
def bars(d,x,y,lw,bw,vx,rowsp=24):
    rows=[("Bags",28/50,(110,200,120),"22 free",WHITE),
          ("Reagent",1.0,AMBER,"Full",AMBER),
          ("Ammo",2612/2800,(110,200,120),"2,612",WHITE)]
    for i,(n,fr,c,v,vc) in enumerate(rows):
        yy=y+i*rowsp
        d.text((x*S,yy*S),n,font=F('Regular',15),fill=(200,205,215),anchor='lm')
        bx=x+lw; d.rounded_rectangle([bx*S,(yy-3)*S,(bx+bw)*S,(yy+3)*S],radius=3*S,fill=(28,40,64))
        d.rounded_rectangle([bx*S,(yy-3)*S,(bx+bw*fr)*S,(yy+3)*S],radius=3*S,fill=c)
        d.text((vx*S,yy*S),v,font=F('SemiBold',15),fill=vc,anchor='rm')

# B: compact, slot left, rows right, ink only in the tooltip
im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
b=down(im); b.alpha_composite(slot,(27,38))
im=up(b); d=ImageDraw.Draw(im); bars(d,104,44,74,330,608)
B=label(down(im).crop((0,0,648,120)),"B. Compact: slot beside the bars, the hint moves to its tooltip")

# C: keep the ink, simpler rows
im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
c=down(im); c.alpha_composite(slot,(27,38)); c.alpha_composite(ink,(87,35))
im=up(c); d=ImageDraw.Draw(im); bars(d,30,122,80,420,608)
C=label(down(im).crop((0,0,648,H-8)),"C. Keep the ink, simpler rows")

foot=stack([nowf,B,C]); foot.save('free_actual.png')
foot.resize((foot.width*2,foot.height*2),Image.LANCZOS).save('free_zoom.png')
print(gold.size,foot.size)
