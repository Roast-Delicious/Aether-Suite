from PIL import Image, ImageDraw, ImageFont
import numpy as np, math
exec(open('/tmp/accents10.py').read().split("names=[")[0])   # base image, gems, draw_accent (chevron = style 2)
GOLDC=(255,209,0,255); DARKC=(10,11,14,255)
def glyph(d, cx, cy, U, kind, color, grow=0):
    """Glyph in a [-1,1] box (y down), U = px per box unit."""
    TH=0.2*U+grow; FN=0.09*U+grow
    P=lambda x,y:(cx+x*U, cy+y*U)
    def ln(pts,w): d.line([P(*p) for p in pts],fill=color,width=max(1,int(round(w))),joint="curve")
    def poly(pts): d.polygon([P(*p) for p in pts],fill=color)
    def arc(cx_,cy_,r,a0,a1,n=40): return [(cx_+r*math.cos(a),cy_+r*math.sin(a)) for a in np.linspace(a0,a1,n)]
    def disc(x,y,r): q=P(x,y); rr=r*U+grow; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],fill=color)
    if kind=="hunter":       # a drawn bow, arrow on the string pointing through it
        def circ3(p1,p2,p3):
            ax,ay=p1; bx,by=p2; cx_,cy_=p3
            dd=2*(ax*(by-cy_)+bx*(cy_-ay)+cx_*(ay-by))
            ux=((ax*ax+ay*ay)*(by-cy_)+(bx*bx+by*by)*(cy_-ay)+(cx_*cx_+cy_*cy_)*(ay-by))/dd
            uy=((ax*ax+ay*ay)*(cx_-bx)+(bx*bx+by*by)*(ax-cx_)+(cx_*cx_+cy_*cy_)*(bx-ax))/dd
            return ux,uy,math.hypot(ax-ux,ay-uy)
        t,m,b=(-0.05,-0.88),(-0.62,0),(-0.05,0.88)
        ux,uy,r=circ3(t,m,b)
        a0=math.atan2(t[1]-uy,t[0]-ux); a1=math.atan2(b[1]-uy,b[0]-ux)
        if a1<a0: a1+=2*math.pi
        pts=arc(ux,uy,r,a0,a1)
        if abs(pts[len(pts)//2][0]-m[0])>0.2: pts=arc(ux,uy,r,a1,a0+2*math.pi)
        ln(pts,TH)
        ln([t,(0.42,0),b],FN)
        ln([(0.42,0),(-0.78,0)],FN); poly([(-0.95,0),(-0.7,-0.15),(-0.7,0.15)])
        ln([(0.42,0),(0.62,-0.14)],FN); ln([(0.42,0),(0.62,0.14)],FN)
    elif kind=="mage":       # a four-point star with two small sparks
        s=0.62; w=0.16
        poly([(0,-s),(w,-w),(s,0),(w,w),(0,s),(-w,w),(-s,0),(-w,-w)])
        for x,y,k in ((0.55,-0.55,0.22),(-0.58,0.5,0.17)):
            ln([(x-k,y),(x+k,y)],FN); ln([(x,y-k),(x,y+k)],FN)
    elif kind=="warrior":    # an upright sword
        ln([(0,-0.9),(0,0.38)],TH); poly([(0,-0.98),(0.1,-0.82),(-0.1,-0.82)])
        ln([(-0.42,0.38),(0.42,0.38)],TH*0.8); ln([(0,0.38),(0,0.78)],FN*1.6); disc(0,0.85,0.09)
    elif kind=="rogue":      # a curved dagger, tip to the upper right
        base=(-0.12,0.18); tip=(0.68,-0.78)
        pts_l=[];pts_r=[]
        for t_ in np.linspace(0,1,24):
            x=base[0]+(tip[0]-base[0])*t_; y=base[1]+(tip[1]-base[1])*t_
            bend=0.18*math.sin(math.pi*t_)          # curve the blade
            nx,ny=0.77,0.64                          # perpendicular to the blade
            x+=nx*bend; y+=ny*bend
            w=0.15*(1-t_)**0.8
            pts_l.append((x-nx*w,y-ny*w)); pts_r.append((x+nx*w,y+ny*w))
        poly(pts_l+pts_r[::-1])
        ln([(-0.42,-0.1),(0.2,0.48)],TH*0.8)        # guard
        ln([(-0.12,0.18),(-0.5,0.62)],FN*1.6); disc(-0.56,0.68,0.09)
    elif kind=="priest":     # a radiant circle
        q=P(0,0); rr=0.36*U; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],outline=color,width=int(TH))
        for a in np.linspace(0,2*math.pi,9)[:-1]:
            ln([(0.52*math.cos(a),0.52*math.sin(a)),(0.82*math.cos(a),0.82*math.sin(a))],FN)
    elif kind=="paladin":    # a hammer
        poly([(-0.55,-0.75),(0.55,-0.75),(0.55,-0.3),(-0.55,-0.3)])
        ln([(0,-0.3),(0,0.85)],TH); ln([(-0.18,0.45),(0.18,0.45)],FN); ln([(-0.18,0.6),(0.18,0.6)],FN)
    elif kind=="druid":      # a leaf on a short stem
        A=(-0.62,0.62); B=(0.66,-0.66); ux,uy=(B[0]-A[0]),(B[1]-A[1]); L=math.hypot(ux,uy); ux,uy=ux/L,uy/L; nx,ny=-uy,ux
        left=[];right=[]
        for t_ in np.linspace(0,1,40):
            x=A[0]+ux*L*t_; y=A[1]+uy*L*t_; w=0.36*math.sin(math.pi*t_)**0.85
            left.append((x+nx*w,y+ny*w)); right.append((x-nx*w,y-ny*w))
        outline=left+right[::-1]
        d.line([P(*p) for p in outline+[outline[0]]],fill=color,width=int(TH),joint="curve")
        ln([A,(B[0]-ux*0.12,B[1]-uy*0.12)],FN)
        for t_,side in ((0.35,1),(0.35,-1),(0.6,1),(0.6,-1)):
            x=A[0]+ux*L*t_; y=A[1]+uy*L*t_; e=0.2
            ln([(x,y),(x+(nx*side+ux)*e,y+(ny*side+uy)*e)],FN)
        ln([A,(A[0]-0.22,A[1]+0.22)],TH*0.8)
    elif kind=="shaman":     # a lightning bolt
        poly([(0.25,-0.9),(-0.35,0.08),(0.02,0.08),(-0.25,0.9),(0.38,-0.15),(0.0,-0.15),(0.25,-0.9)])
    elif kind=="warlock":    # a flame
        out=[(0,-0.9),(0.32,-0.35),(0.48,0.15),(0.4,0.55),(0.0,0.82),(-0.4,0.55),(-0.48,0.15),(-0.25,-0.25),(-0.12,0.0)]
        d.line([P(*p) for p in out+[out[0]]],fill=color,width=int(TH),joint="curve")
        inn=[(0,-0.1),(0.16,0.25),(0.12,0.5),(0,0.58),(-0.12,0.5),(-0.16,0.25)]
        d.line([P(*p) for p in inn+[inn[0]]],fill=color,width=max(1,int(FN)),joint="curve")
def medallion(big, x, y, kind, SSf):
    D=20*K*SSf; cx,cy=x*SSf,y*SSf
    d=ImageDraw.Draw(big)
    d.ellipse([cx-D/2-1.5*SSf,cy-D/2-1.5*SSf,cx+D/2+1.5*SSf,cy+D/2+1.5*SSf],fill=DARKC)          # dark disc
    d.ellipse([cx-D/2,cy-D/2,cx+D/2,cy+D/2],outline=GOLDC,width=max(1,int(0.75*SSf)))             # fine gold rim
    glyph(d,cx,cy,D*0.33,kind,GOLDC)
def render_crests(classes):
    im=Image.fromarray(clean).convert("RGBA"); big=im.resize((W*SS,H*SS),Image.LANCZOS)
    dark=Image.new("RGBA",big.size,(0,0,0,0)); gold=Image.new("RGBA",big.size,(0,0,0,0)); med=Image.new("RGBA",big.size,(0,0,0,0))
    top_gems={}
    for gi,(x,y,s,dx,dy) in enumerate(gems):
        crest=0 if gi<3 else (1 if gi<6 else 2)
        outer = 1 if crest!=1 else -1            # 3 o'clock on yours (capsule side), mirrored on the target
        if dx==outer and dy==0 and crest in classes: top_gems[crest]=(x,y); continue
        draw_accent(dark,x,y,s,dx,dy,2,DARK,1.9*SS); draw_accent(gold,x,y,s,dx,dy,2,GOLD,0)
    big.alpha_composite(dark); big.alpha_composite(gold)
    for crest,(x,y) in top_gems.items():
        medallion(big,x,y,classes[crest],SS)
    return big.resize((W,H),Image.LANCZOS).convert("RGB")
full=render_crests({0:"hunter",1:"paladin"})
full.save('/tmp/glyph_frames.png')
# glyph sheet: each glyph in its medallion, 6x and at actual size
kinds=["hunter","mage","warrior","rogue","priest","paladin","druid","shaman","warlock"]
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)
tile=120; S2=16
sheet=Image.new("RGB",(len(kinds)*tile,tile+50+40),(20,20,24)); ds=ImageDraw.Draw(sheet)
for i,k in enumerate(kinds):
    big=Image.new("RGBA",(tile*S2,tile*S2),(43,36,24,255))
    D=20*K*4.5*S2; c=tile*S2/2
    d=ImageDraw.Draw(big)
    d.ellipse([c-D/2-1.5*4.5*S2,c-D/2-1.5*4.5*S2,c+D/2+1.5*4.5*S2,c+D/2+1.5*4.5*S2],fill=DARKC)
    d.ellipse([c-D/2,c-D/2,c+D/2,c+D/2],outline=GOLDC,width=int(0.75*4.5*S2))
    glyph(d,c,c,D*0.33,k,GOLDC)
    sheet.paste(big.resize((tile,tile),Image.LANCZOS).convert("RGB"),(i*tile,0))
    ds.text((i*tile+tile/2-ds.textlength(k.title(),font=lf)/2,tile+4),k.title(),fill=(230,230,230),font=lf)
    # actual size
    a=Image.new("RGBA",(30*S2,30*S2),(43,36,24,255)); D=20*K*S2; c=15*S2; d=ImageDraw.Draw(a)
    d.ellipse([c-D/2-1.5*S2,c-D/2-1.5*S2,c+D/2+1.5*S2,c+D/2+1.5*S2],fill=DARKC)
    d.ellipse([c-D/2,c-D/2,c+D/2,c+D/2],outline=GOLDC,width=int(0.75*S2)); glyph(d,c,c,D*0.33,k,GOLDC)
    sheet.paste(a.resize((30,30),Image.LANCZOS).convert("RGB"),(i*tile+tile//2-15,tile+28))
sheet.save('/tmp/glyph_sheet.png'); print(full.size, sheet.size)
