from PIL import Image, ImageDraw, ImageFont, ImageChops
import numpy as np, cv2
src=Image.open('/tmp/v4/f_057.png').convert('RGB')
# erase today's bar so each option is drawn on the bare panel
a=np.array(src); m=np.zeros(a.shape[:2],np.uint8); m[1264:1290,916:1720]=255
clean=Image.fromarray(cv2.inpaint(a,m,6,cv2.INPAINT_TELEA)).convert('RGBA')
SS=8
CH=Image.open('/home/claude/brand/AetherHub/Media/win_chev_gold.tga').convert('RGBA')
CD=Image.open('/home/claude/brand/AetherHub/Media/win_chev_dark.tga').convert('RGBA')
def tint(img,c):
    out=Image.new('RGBA',img.size,c+(255,)); out.putalpha(img.split()[3]); return out
GOLD=(255,209,0); DARK=(10,11,14); BLUE=(77,166,255); NAVY=(28,74,150); BG=(10,12,18); EDGE=(77,166,255)
def draw_bar(canvas, x0,y0,w,h, radius, accents, chev_k=0.85, earn=0.58, rest=0.75, push=0):
    """x0,y0,w,h: outer box (screen px). radius in px. chevrons sized chev_k*h."""
    W,H=int(w*SS),int(h*SS); R=int(radius*SS)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    # outer blue edge, then dark gap, then the fill area (all following the rounded shape)
    d.rounded_rectangle([0,0,W-1,H-1],R,fill=EDGE+(255,))
    e=int(1*SS); d.rounded_rectangle([e,e,W-1-e,H-1-e],max(0,R-e),fill=(6,8,12,255))
    g=int(3*SS); inner=[g,g,W-1-g,H-1-g]; ri=max(0,R-g)
    mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).rounded_rectangle(inner,ri,fill=255)
    fill=Image.new('RGBA',(W,H),BG+(255,)); fd=ImageDraw.Draw(fill)
    iw=inner[2]-inner[0]; ex=inner[0]+int(iw*earn); rx=inner[0]+int(iw*rest)
    fd.rectangle([ex,0,rx,H],fill=tuple(int(BG[i]*0.15+BLUE[i]*0.85) for i in range(3))+(255,))
    fd.rectangle([0,0,ex,H],fill=NAVY+(255,))
    # soft top light
    sh=np.linspace(1.18,0.82,H)[:,None,None]; fa=np.array(fill).astype(np.float32); fa[...,:3]*=sh; fill=Image.fromarray(np.clip(fa,0,255).astype(np.uint8))
    fd=ImageDraw.Draw(fill)
    for i in range(1,20):
        x=inner[0]+int(iw*i/20); fd.line([x,0,x,H],fill=GOLD+(90,),width=max(1,SS//1))
    fd.rectangle([ex-SS,0,ex+SS,H],fill=GOLD+(255,))
    lay.paste(fill,(0,0),mask)
    # accents: chevrons pointing outward, centered on the edge, sized from the bar height
    cs=int(chev_k*h*SS)
    big=Image.new('RGBA',(W+cs*2,H+cs*2),(0,0,0,0)); big.alpha_composite(lay,(cs,cs))
    P=int(push*SS)
    pos={"12":(cs+W//2,cs-P,0),"6":(cs+W//2,cs+H+P,180),"3":(cs+W+P,cs+H//2,-90),"9":(cs-P,cs+H//2,90)}
    for k in accents:
        x,y,rot=pos[k]
        for img,col in ((CD,DARK),(CH,GOLD)):
            t=tint(img.resize((cs,cs),Image.LANCZOS),col).rotate(rot,resample=Image.BICUBIC)
            big.alpha_composite(t,(x-cs//2,y-cs//2))
    small=big.resize((round(big.width/SS),round(big.height/SS)),Image.LANCZOS)
    canvas.alpha_composite(small,(round(x0-cs/SS),round(y0-cs/SS)))

crop=(885,1232,1750,1322)
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',12)
opts=[("110% of bar height, 3 px out",1.10,3),
      ("130% of bar height, 3 px out",1.30,3),
      ("175% of bar height, 3 px out",1.75,3)]
rows=[]
for label,k,push in opts:
    im=clean.copy(); draw_bar(im,922,1268,790,18,9,["12","3","6","9"],chev_k=k,push=push)
    c=im.crop(crop).convert('RGB')
    lab=Image.new('RGB',(c.width,18),(20,20,24)); ImageDraw.Draw(lab).text((6,2),label,font=lf,fill=(255,255,255))
    rows+=[lab,c]
out=Image.new('RGB',(rows[0].width,sum(r.height for r in rows))); y=0
for r in rows: out.paste(r,(0,y)); y+=r.height
out.save('/tmp/xp175_actual.png')
z=[]
for i in range(3):
    y=i*108+18
    a=out.crop((0,y,250,y+90)).resize((750,270),Image.LANCZOS)
    b=out.crop((300,y,550,y+90)).resize((750,270),Image.LANCZOS)
    lab=Image.new('RGB',(750,26),(20,20,24)); ImageDraw.Draw(lab).text((6,3),opts[i][0],font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16),fill=(255,255,255))
    z+=[lab,a,b]
zo=Image.new('RGB',(750,sum(r.height for r in z))); y=0
for r in z: zo.paste(r,(0,y)); y+=r.height
zo.save('/tmp/xp175_zoom.png')
