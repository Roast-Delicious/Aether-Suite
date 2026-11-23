from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, cv2, math
base=np.array(Image.open('/tmp/v4/f_057.png').convert('RGB').crop((420,990,1180,1230)))
K=1.15; H,W=base.shape[:2]
# crests: center, R (units), gem size (units), which gems (top, right, bottom, left)
crests=[((62.5,121.5-39*K),40,9,("t","r","l")),((679.5,121-39*K),40,9,("t","r","l")),((113,210.5),29,6,("t","r","b","l"))]
gems=[]
for (cx,cy),R,g,which in crests:
    d=(R-1)*K
    for w in which:
        dx,dy={"t":(0,-1),"r":(1,0),"b":(0,1),"l":(-1,0)}[w]
        gems.append((cx+dx*d, cy+dy*d, g*K))
# erase the current gems (inpaint a small diamond-sized patch at each)
m=np.zeros((H,W),np.uint8)
for x,y,s in gems:
    r=s*1.4
    cv2.circle(m,(int(round(x)),int(round(y))),int(math.ceil(r)),255,-1)
# rebuild what's under each gem by copying the same ring from 25 degrees further round
clean=base.copy().astype(np.float32)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
for (ccx,ccy),R,g,which in crests:
    rho=np.hypot(xx-ccx,yy-ccy); phi=np.arctan2(yy-ccy,xx-ccx)
    rot=math.radians(25)
    mapx=(ccx+rho*np.cos(phi+rot)).astype(np.float32); mapy=(ccy+rho*np.sin(phi+rot)).astype(np.float32)
    src=cv2.remap(base,mapx,mapy,cv2.INTER_LINEAR)
    d=(R-1)*K
    for w in which:
        dx,dy={"t":(0,-1),"r":(1,0),"b":(0,1),"l":(-1,0)}[w]
        gx,gy=ccx+dx*d,ccy+dy*d; rad=g*K*1.4
        mm=np.clip((rad-np.hypot(xx-gx,yy-gy))/2.0,0,1)[...,None]
        clean=clean*(1-mm)+src.astype(np.float32)*mm
clean=clean.clip(0,255).astype(np.uint8)
SS=8
GOLD=(255,209,0); DARK=(10,11,14)
def poly(d,pts,fill): d.polygon([(p[0],p[1]) for p in pts],fill=fill)
def diamond(cx,cy,r): return [(cx,cy-r),(cx+r,cy),(cx,cy+r),(cx-r,cy)]
def draw_gem(layer,x,y,s,style):
    d=ImageDraw.Draw(layer); cx,cy=x*SS,y*SS
    r=s/2*math.sqrt(2)*SS            # half-diagonal of the gold diamond
    rb=(s+3*K)/2*math.sqrt(2)*SS     # the dark backing, a bit bigger
    if style=="now":
        poly(d,diamond(cx,cy,rb),DARK+(255,)); poly(d,diamond(cx,cy,r),(190,150,20,255))
    elif style=="faceted":
        poly(d,diamond(cx,cy,rb),DARK+(255,))
        T,Rr,B,L=(cx,cy-r),(cx+r,cy),(cx,cy+r),(cx-r,cy); C=(cx,cy)
        poly(d,[T,Rr,C],(250,214,60,255)); poly(d,[Rr,B,C],(170,118,8,255))
        poly(d,[B,L,C],(205,155,20,255)); poly(d,[L,T,C],(255,240,150,255))
        sp=r*0.22; sx,sy=cx-r*0.35,cy-r*0.35
        d.polygon([(sx,sy-sp),(sx+sp*0.3,sy),(sx,sy+sp),(sx-sp*0.3,sy)],fill=(255,255,255,235))
        d.polygon([(sx-sp,sy),(sx,sy-sp*0.3),(sx+sp,sy),(sx,sy+sp*0.3)],fill=(255,255,255,235))
    elif style=="sapphire":
        poly(d,diamond(cx,cy,rb),DARK+(255,)); poly(d,diamond(cx,cy,r),(235,190,25,255))
        ri=r*0.58
        T,Rr,B,L=(cx,cy-ri),(cx+ri,cy),(cx,cy+ri),(cx-ri,cy); C=(cx,cy)
        poly(d,[L,T,C],(150,215,255,255)); poly(d,[T,Rr,C],(77,170,245,255))
        poly(d,[Rr,B,C],(25,85,170,255)); poly(d,[B,L,C],(45,120,210,255))
        g=ri*0.22; d.ellipse([cx-ri*0.45-g,cy-ri*0.45-g,cx-ri*0.45+g,cy-ri*0.45+g],fill=(255,255,255,230))
    elif style=="star":
        R2=r*1.55; w=r*0.38
        star=lambda RR,ww:[(cx,cy-RR),(cx+ww,cy-ww),(cx+RR,cy),(cx+ww,cy+ww),(cx,cy+RR),(cx-ww,cy+ww),(cx-RR,cy),(cx-ww,cy-ww)]
        poly(d,star(R2+2.2*SS,w+1.6*SS),DARK+(255,))
        poly(d,star(R2,w),(240,195,30,255))
        # light and dark halves of each point
        poly(d,[(cx,cy-R2),(cx-w,cy-w),(cx,cy)],(255,236,140,255)); poly(d,[(cx-R2,cy),(cx-w,cy-w),(cx,cy)],(255,236,140,255))
        poly(d,[(cx,cy+R2),(cx+w,cy+w),(cx,cy)],(175,125,10,255)); poly(d,[(cx+R2,cy),(cx+w,cy+w),(cx,cy)],(175,125,10,255))
    elif style=="glow":
        g=Image.new("RGBA",layer.size,(0,0,0,0)); gd=ImageDraw.Draw(g)
        rr=r*1.9; gd.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=(255,200,40,150))
        g=g.filter(ImageFilter.GaussianBlur(r*0.55)); layer.alpha_composite(g)
        d=ImageDraw.Draw(layer)
        poly(d,diamond(cx,cy,rb*0.92),DARK+(200,))
        # gold with a bright core
        for k,c in ((1.0,(235,180,20)),(0.7,(255,215,70)),(0.42,(255,245,190)),(0.18,(255,255,255))):
            poly(d,diamond(cx,cy,r*k),c+(255,))
def render(style):
    im=Image.fromarray(clean).convert("RGBA"); big=im.resize((W*SS,H*SS),Image.LANCZOS)
    layer=Image.new("RGBA",big.size,(0,0,0,0))
    for x,y,s in gems: draw_gem(layer,x,y,s,style)
    big.alpha_composite(layer)
    return big.resize((W,H),Image.LANCZOS).convert("RGB")
styles=[("now","Now"),("faceted","1. Faceted"),("sapphire","2. Sapphire inlay"),("star","3. Compass star"),("glow","4. Glowing jewel")]
imgs={k:render(k) for k,_ in styles}
# sheet A: actual size
lab=24; C=Image.new("RGB",(W,(lab+H)*len(styles)),(20,20,24)); d=ImageDraw.Draw(C)
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16); y=0
for k,label in styles:
    d.text((8,y+3),label,fill=(230,230,230),font=lf); C.paste(imgs[k],(0,y+lab)); y+=lab+H
C.save('/tmp/gems_actual.png')
# sheet B: close-ups of your crest (4x)
cx,cy=62.5,101.5-39*K; box=(int(cx-62),int(cy-58),int(cx+62),int(cy+58))
tiles=[(label,imgs[k].crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.LANCZOS)) for k,label in styles]
tw,th=tiles[0][1].size; cols=3; rows=2
Z=Image.new("RGB",(tw*cols+20*(cols-1),(th+30)*rows),(20,20,24)); dz=ImageDraw.Draw(Z)
for i,(label,t) in enumerate(tiles):
    x=(i%cols)*(tw+20); yy=(i//cols)*(th+30)
    dz.text((x+6,yy+4),label,fill=(230,230,230),font=lf); Z.paste(t,(x,yy+28))
Z.save('/tmp/gems_close.png'); print(C.size, Z.size)
