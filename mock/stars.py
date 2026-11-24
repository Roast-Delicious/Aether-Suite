from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, random
K=1.5; SS=8           # px per UI unit on the user's screen (from their screenshots), supersampling
GOLD=(255,176,0); GOLD_L=(255,214,110); GOLD_D=(196,118,0); NAVY=(19,40,74); DARK=(10,12,18)
FD='/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
def star_pts(cx,cy,R,r,n=5,rot=-90,):
    pts=[]
    for i in range(2*n):
        a=math.radians(rot+i*180/n); rad=R if i%2==0 else r
        pts.append((cx+rad*math.cos(a), cy+rad*math.sin(a)))
    return pts
def glow(size,color,radius,alpha):
    g=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(g)
    c=size/2; d.ellipse([c-radius,c-radius,c+radius,c+radius],fill=color+(alpha,))
    return g.filter(ImageFilter.GaussianBlur(radius*0.45))
def pin(kind, units, glow_on=True):
    s=int(units*2.6*K*SS); im=Image.new('RGBA',(s,s),(0,0,0,0)); c=s/2; u=K*SS
    if glow_on: im.alpha_composite(glow(s,GOLD,units*0.62*u,150))
    d=ImageDraw.Draw(im)
    R=units/2*u
    if kind=='now':      # approximation of the current pin: big star on a dark disc
        d.ellipse([c-R-2*u,c-R-2*u,c+R+2*u,c+R+2*u],fill=(0,0,0,165))
        d.polygon(star_pts(c,c+R*0.06,R*0.98,R*0.42),fill=(255,226,60),outline=(120,90,0),width=int(u))
    elif kind=='A':      # solid gold star, thin dark outline, small dark disc
        d.ellipse([c-R,c-R,c+R,c+R],fill=DARK+(170,))
        d.polygon(star_pts(c,c+R*0.06,R*1.02,R*0.44),fill=GOLD,outline=(40,24,0),width=int(1.1*u))
    elif kind=='B':      # faceted gem star: light and dark halves per point
        d.ellipse([c-R,c-R,c+R,c+R],fill=DARK+(170,))
        P=star_pts(c,c+R*0.06,R*1.02,R*0.45); cc=(c,c+R*0.06)
        for i in range(10):
            a,b=P[i],P[(i+1)%10]
            col=GOLD_L if (i%2==0) else GOLD_D
            d.polygon([cc,a,b],fill=col)
        d.polygon(P,outline=(40,24,0),width=int(1.0*u))
    elif kind=='C':      # star in a ring: navy disc, thin gold ring, gold star (like the crests)
        d.ellipse([c-R,c-R,c+R,c+R],fill=NAVY+(235,),outline=GOLD,width=int(1.4*u))
        d.polygon(star_pts(c,c+R*0.05,R*0.72,R*0.31),fill=GOLD)
    elif kind=='D':      # four-point Aether spark with a small diamond core
        d.ellipse([c-R*0.72,c-R*0.72,c+R*0.72,c+R*0.72],fill=DARK+(160,))
        d.polygon(star_pts(c,c,R*1.15,R*0.34,n=4,rot=-90),fill=GOLD,outline=(40,24,0),width=int(0.9*u))
        d.polygon(star_pts(c,c,R*0.62,R*0.22,n=4,rot=-45),fill=GOLD_L)
    elif kind=='E':      # rounded five-point star, no disc, dark outline only (most compact)
        P=star_pts(c,c+R*0.06,R*1.05,R*0.47)
        m=Image.new('L',im.size,0); ImageDraw.Draw(m).polygon(P,fill=255)
        m=m.filter(ImageFilter.GaussianBlur(0.45*u)).point(lambda v:255 if v>110 else 0)
        o=m.filter(ImageFilter.MaxFilter(int(2.4*u)//2*2+1))
        im.paste((30,18,0,255),(0,0),o); im.paste(GOLD+(255,),(0,0),m)
        hl=Image.new('L',im.size,0); ImageDraw.Draw(hl).polygon(star_pts(c,c+R*0.05,R*0.98,R*0.46),fill=0)
    return im.resize((s//SS,s//SS),Image.LANCZOS)
# a plain map-like backdrop (generic terrain colors, not Blizzard art)
random.seed(3)
def backdrop(w,h):
    bg=Image.new('RGB',(w,h),(118,104,72)); d=ImageDraw.Draw(bg)
    for _ in range(140):
        x,y=random.randint(0,w),random.randint(0,h); r=random.randint(20,90)
        col=random.choice([(98,112,70),(132,116,80),(110,96,64),(84,98,74),(140,128,92)])
        d.ellipse([x-r,y-r,x+r,y+r],fill=col)
    bg=bg.filter(ImageFilter.GaussianBlur(14))
    d=ImageDraw.Draw(bg)
    for _ in range(2):
        pts=[(random.randint(0,w),random.randint(0,h)) for _ in range(4)]
        d.line(pts,fill=(86,104,118),width=2)
    return bg.convert('RGBA')
opts=[('now','Now (approx.)',24),('A','A. Solid star',18),('B','B. Faceted gem star',18),('C','C. Star in a ring',18),('D','D. Aether spark',18),('E','E. Outline only',16)]
cell=150; W=cell*len(opts); H=210
bg=backdrop(W,H); f=ImageFont.truetype(FD+'SemiBold.ttf',13); f2=ImageFont.truetype(FD+'Regular.ttf',11)
d=ImageDraw.Draw(bg)
for i,(k,name,u) in enumerate(opts):
    cx=i*cell+cell//2
    d.rectangle([i*cell+6,4,i*cell+cell-6,24],fill=(10,12,18,200))
    d.text((cx,14),name,font=f,fill=(255,255,255),anchor='mm')
    p=pin(k,u); bg.alpha_composite(p,(int(cx-p.width/2),int(80-p.height/2)))
    mp=pin(k,u*14/18 if k!='now' else 18); bg.alpha_composite(mp,(int(cx-mp.width/2),int(160-mp.height/2)))
    d.text((cx,118),"world map",font=f2,fill=(240,240,240),anchor='mm',stroke_width=2,stroke_fill=(0,0,0))
    d.text((cx,196),"minimap",font=f2,fill=(240,240,240),anchor='mm',stroke_width=2,stroke_fill=(0,0,0))
bg.save('stars_actual.png')
big=Image.new('RGBA',(W,190),(24,26,34,255)); d=ImageDraw.Draw(big)
for i,(k,name,u) in enumerate(opts):
    p=pin(k,u); p=p.resize((p.width*3,p.height*3),Image.LANCZOS)
    cx=i*cell+cell//2; big.alpha_composite(p,(int(cx-p.width/2),int(100-p.height/2)))
    d.text((cx,12),name,font=f,fill=(255,255,255),anchor='mm')
big.save('stars_zoom.png')
