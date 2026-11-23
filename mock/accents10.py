from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2, math
exec(open('/tmp/gems.py').read().split("SS=8")[0])      # base, clean image, gem positions
gems=[]
for (cx,cy),R,g,which in crests:
    d=(R-1)*K
    for w in which:
        dx,dy={"t":(0,-1),"r":(1,0),"b":(0,1),"l":(-1,0)}[w]
        gems.append((cx+dx*d, cy+dy*d, g*K, dx, dy))
SS=8
GOLD=(255,209,0,255); DARK=(10,11,14,255)
def draw_accent(img, x, y, s, dx, dy, style, color, grow):
    """Draw in local units: u = outward from the crest, v = along the ring.
    r = the old gem's half-diagonal. `grow` widens everything for the dark backing."""
    d=ImageDraw.Draw(img); r=s/2*math.sqrt(2)
    cx,cy=x*SS,y*SS
    def P(u,v): return (cx+(u*dx-v*dy)*r*SS, cy+(u*dy+v*dx)*r*SS)
    TH=1.6*SS+grow; FN=0.75*SS+grow
    def line(a,b,w): d.line([P(*a),P(*b)],fill=color,width=max(1,int(round(w))),joint="curve")
    def outline(pts,w): d.line([P(*p) for p in pts+[pts[0]]],fill=color,width=max(1,int(round(w))),joint="curve")
    def fill(pts):
        d.polygon([P(*p) for p in pts],fill=color)
        if grow: d.line([P(*p) for p in pts+[pts[0]]],fill=color,width=int(grow*2),joint="curve")
    def dot(u,v,rad):
        q=P(u,v); rr=rad*r*SS+grow; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],fill=color)
    def circle(u,v,rad,w):
        q=P(u,v); rr=rad*r*SS; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],outline=color,width=max(1,int(round(w))))
    def arcpts(cu,cv,rad,a0,a1,n=24): return [(cu+rad*math.cos(a),cv+rad*math.sin(a)) for a in np.linspace(a0,a1,n)]
    if style==1:   # kite + spine
        k=[(1.45,0),(0,0.55),(-0.85,0),(0,-0.55)]
        outline(k,TH); line((-0.6,0),(1.2,0),FN)
    elif style==2: # chevron + fine echo
        line((-0.2,-0.85),(0.55,0),TH); line((0.55,0),(-0.2,0.85),TH)
        line((0.35,-0.75),(1.1,0),FN); line((1.1,0),(0.35,0.75),FN)
    elif style==3: # lens along the ring + fine diamond
        top=arcpts(0.7,0,1.2,math.pi*0.73,math.pi*1.27); bot=arcpts(-0.7,0,1.2,-math.pi*0.27,math.pi*0.27)
        outline(top+bot,TH); fill([(0.22,0),(0,0.22),(-0.22,0),(0,-0.22)])
    elif style==4: # bowtie + fine bar
        outline([(0,0),(0.55,-0.85),(-0.55,-0.85)],TH); outline([(0,0),(0.55,0.85),(-0.55,0.85)],TH)
        line((-0.9,0),(0.9,0),FN)
    elif style==5: # fine diamond around a thick square
        outline([(1.05,0),(0,1.05),(-1.05,0),(0,-1.05)],FN)
        q=0.4; outline([(q,q),(q,-q),(-q,-q),(-q,q)],TH)
    elif style==6: # fine circle + solid diamond
        circle(0,0,0.95,FN); fill([(0.5,0),(0,0.5),(-0.5,0),(0,-0.5)])
    elif style==7: # rune: thick bar along the ring, fine bars, fine spine
        line((0,-0.75),(0,0.75),TH); line((0.5,-0.45),(0.5,0.45),FN); line((-0.5,-0.45),(-0.5,0.45),FN)
        line((-0.75,0),(0.85,0),FN)
    elif style==8: # bead: solid diamond, fine dots either side along the ring
        fill([(0.55,0),(0,0.45),(-0.55,0),(0,-0.45)]); dot(0,0.9,0.16); dot(0,-0.9,0.16)
        line((0,-0.62),(0,0.62),FN)
    elif style==9: # arrow: thick shaft, fine head, fine tail bar
        line((-0.8,0),(1.0,0),TH); line((0.55,-0.45),(1.15,0),FN); line((1.15,0),(0.55,0.45),FN)
        line((-0.8,-0.4),(-0.8,0.4),FN)
    elif style==10: # hex + fine inner hex
        hexp=lambda k:[(k*math.cos(a),k*0.85*math.sin(a)) for a in np.linspace(0,2*math.pi,7)[:-1]]
        outline(hexp(0.95),TH); outline(hexp(0.5),FN)
def render(style):
    im=Image.fromarray(clean).convert("RGBA"); big=im.resize((W*SS,H*SS),Image.LANCZOS)
    dark=Image.new("RGBA",big.size,(0,0,0,0)); gold=Image.new("RGBA",big.size,(0,0,0,0))
    for x,y,s,dx,dy in gems:
        if style=="now":
            dd=ImageDraw.Draw(dark); r=s/2*math.sqrt(2)*SS; rb=(s+3*K)/2*math.sqrt(2)*SS; c=(x*SS,y*SS)
            dd.polygon([(c[0],c[1]-rb),(c[0]+rb,c[1]),(c[0],c[1]+rb),(c[0]-rb,c[1])],fill=DARK)
            gg=ImageDraw.Draw(gold); gg.polygon([(c[0],c[1]-r),(c[0]+r,c[1]),(c[0],c[1]+r),(c[0]-r,c[1])],fill=(190,150,20,255))
        else:
            draw_accent(dark,x,y,s,dx,dy,style,DARK,1.9*SS)
            draw_accent(gold,x,y,s,dx,dy,style,GOLD,0)
    big.alpha_composite(dark); big.alpha_composite(gold)
    return big.resize((W,H),Image.LANCZOS).convert("RGB")
names=["Now","1. Kite","2. Chevron","3. Lens","4. Bowtie","5. Square in diamond","6. Ring & diamond","7. Rune","8. Bead","9. Arrow","10. Hex"]
keys=["now"]+list(range(1,11))
imgs=[render(k) for k in keys]
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)
cx,cy=62.5,101.5-39*K
# close-ups (3x) of your crest
box=(int(cx-60),int(cy-56),int(cx+60),int(cy+56)); tw,th=(box[2]-box[0])*3,(box[3]-box[1])*3
cols=4; rows=3
Z=Image.new("RGB",(cols*tw+(cols-1)*12,rows*(th+26)),(20,20,24)); dz=ImageDraw.Draw(Z)
for i,(im,nm) in enumerate(zip(imgs,names)):
    x=(i%cols)*(tw+12); y=(i//cols)*(th+26)
    dz.text((x+4,y+4),nm,fill=(230,230,230),font=lf); Z.paste(im.crop(box).resize((tw,th),Image.LANCZOS),(x,y+24))
Z.save('/tmp/acc_close.png')
# actual size: your crest + Steve's, 1:1, in a grid
box2=(int(cx-58),int(cy-52),int(cx+86),int(cy+62)); w2,h2=box2[2]-box2[0],box2[3]-box2[1]
cols=6; rows=2
A=Image.new("RGB",(cols*w2+(cols-1)*8,rows*(h2+22)),(20,20,24)); da=ImageDraw.Draw(A)
sf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',11)
for i,(im,nm) in enumerate(zip(imgs,names)):
    x=(i%cols)*(w2+8); y=(i//cols)*(h2+22)
    da.text((x+3,y+4),nm,fill=(230,230,230),font=sf); A.paste(im.crop(box2),(x,y+20))
A.save('/tmp/acc_actual.png'); print(Z.size, A.size)
