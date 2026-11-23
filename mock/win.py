from PIL import Image, ImageDraw, ImageFont
import numpy as np
SS=4
bgsrc=Image.open('/tmp/v4/f_057.png').convert('RGBA')
CH=Image.open('/home/claude/brand/AetherHub/Media/win_chev_gold.tga').convert('RGBA')
CD=Image.open('/home/claude/brand/AetherHub/Media/win_chev_dark.tga').convert('RGBA')
GOLD=(255,209,0); BLUE=(77,166,255); NAVY=(18,43,82); PANEL=(13,13,13); DARK=(10,11,14)
FT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',11*SS)
FB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',10*SS)
def tint(img,c):
    out=Image.new('RGBA',img.size,c+(255,)); out.putalpha(img.split()[3]); return out
def window(w,h,radius,brackets,chev_mid,chev_side,push=3,title="AETHER PACK",keys=("12","3","6","9")):
    M=40; W,H=(w+2*M)*SS,(h+2*M)*SS; L=Image.new('RGBA',(W,H),(0,0,0,0))
    x0,y0,x1,y1=M*SS,M*SS,(M+w)*SS,(M+h)*SS; R=radius*SS
    # soft glow, 10 px, brightest at the edge
    g=np.zeros((H,W),np.float32)
    yy,xx=np.mgrid[0:H,0:W]
    dx=np.maximum(np.maximum(x0+R-xx,xx-(x1-R)),0); dy=np.maximum(np.maximum(y0+R-yy,yy-(y1-R)),0)
    d=np.hypot(dx,dy)-R; d=d/SS
    al=np.where((d>0)&(d<10),0.42*(1-d/10)**2,0)
    glow=np.zeros((H,W,4),np.uint8); glow[...,0:3]=BLUE; glow[...,3]=(al*255).astype(np.uint8)
    L.alpha_composite(Image.fromarray(glow))
    dr=ImageDraw.Draw(L)
    dr.rounded_rectangle([x0,y0,x1,y1],R,fill=PANEL+(240,),outline=BLUE+(255,),width=SS)
    i=3*SS; dr.rounded_rectangle([x0+i,y0+i,x1-i,y1-i],max(0,R-i),outline=BLUE+(80,),width=SS)
    # title strip with gold underline
    t=26*SS
    strip=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(strip)
    sd.rounded_rectangle([x0+SS,y0+SS,x1-SS,y0+t+R],max(0,R-SS),fill=NAVY+(255,))
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).rectangle([0,0,W,y0+t],fill=255)
    L.paste(strip,(0,0),Image.composite(strip.split()[3],Image.new('L',(W,H),0),m))
    dr.line([x0+4*SS,y0+t,x1-4*SS,y0+t],fill=GOLD+(200,),width=SS)
    dr.text((x0+10*SS,y0+7*SS),title,font=FT,fill=BLUE+(255,))
    dr.rectangle([x1-22*SS,y0+6*SS,x1-8*SS,y0+20*SS],outline=BLUE+(255,),width=SS); dr.text((x1-18*SS,y0+6*SS),"x",font=FB,fill=(255,255,255,255))
    for k in range(4):
        dr.text((x0+14*SS,y0+(40+k*22)*SS),["Quest items","Gear","Consumables","Trade goods"][k],font=FB,fill=(230,230,230,255))
        for j in range(6):
            bx=x0+(120+j*28)*SS; by=y0+(36+k*22)*SS
            dr.rectangle([bx,by,bx+22*SS,by+18*SS],fill=(40,45,55,255),outline=(60,110,170,255),width=SS)
    # gold corner brackets (thick, plus a fine echo)
    if brackets=="square":
        O=3*SS; Ln=12*SS
        for sx,sy,cx,cy in ((-1,-1,x0,y0),(1,-1,x1,y0),(-1,1,x0,y1),(1,1,x1,y1)):
            px,py=cx+sx*O,cy+sy*O
            dr.rectangle(sorted([px,px-sx*Ln])+[0,0][:0] and [min(px,px-sx*Ln),min(py,py-sy*2*SS),max(px,px-sx*Ln),max(py,py-sy*2*SS)],fill=GOLD+(255,))
            dr.rectangle([min(px,px-sx*2*SS),min(py,py-sy*Ln),max(px,px-sx*2*SS),max(py,py-sy*Ln)],fill=GOLD+(255,))
            fx,fy=cx,cy
            dr.rectangle([min(fx,fx-sx*7*SS),min(fy,fy-sy*SS),max(fx,fx-sx*7*SS),max(fy,fy-sy*SS)],fill=GOLD+(230,))
            dr.rectangle([min(fx,fx-sx*SS),min(fy,fy-sy*7*SS),max(fx,fx-sx*SS),max(fy,fy-sy*7*SS)],fill=GOLD+(230,))
    elif brackets=="arc":
        O=3*SS; RR=R+O
        for (cx,cy,a0) in ((x0+R,y0+R,180),(x1-R,y0+R,270),(x1-R,y1-R,0),(x0+R,y1-R,90)):
            dr.arc([cx-RR,cy-RR,cx+RR,cy+RR],a0,a0+90,fill=GOLD+(255,),width=2*SS)
            rf=R-SS; dr.arc([cx-rf,cy-rf,cx+rf,cy+rf],a0+15,a0+75,fill=GOLD+(200,),width=SS)
    # chevrons at 12, 3, 6, 9 (outward, pushed out)
    P=push*SS
    cx,cy=(x0+x1)//2,(y0+y1)//2
    for key,(x,y,rot) in {"12":(cx,y0-P,0),"6":(cx,y1+P,180),"3":(x1+P,cy,-90),"9":(x0-P,cy,90)}.items():
        if key not in keys: continue
        size=chev_mid if key in("12","6") else chev_side
        if not size: continue
        k=int(size*SS)
        for img,col in ((CD,DARK),(CH,GOLD)):
            tt=tint(img.resize((k,k),Image.LANCZOS),col).rotate(rot,resample=Image.BICUBIC)
            L.alpha_composite(tt,(x-k//2,y-k//2))
    return L.resize((W//SS,H//SS),Image.LANCZOS)
opts=[("Now","square",0,26,0,0),
      ("1  Square + brackets + 4 chevrons","square",0,26,34,3),
      ("2  Rounded + 4 chevrons","None",8,26,34,3),
      ("3  Rounded + gold arcs + 4 chevrons","arc",8,26,34,3)]
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
tiles=[]
for i,(label,br,rad,cm,cs,push) in enumerate(opts):
    win=window(300,140,rad,br,cm,cs if cs else 0,push if push else 3)
    bg=bgsrc.crop((1250+ (i%2)*20,520+i*10,1250+(i%2)*20+win.width,520+i*10+win.height)).copy()
    if br=="square" and cs==0:   # "now": top chevron only, sitting on the edge
        win=window(300,140,0,"square",26,0,-3,keys=("12",))
    bg.alpha_composite(win)
    lab=Image.new('RGBA',(bg.width,20),(20,20,24,255)); ImageDraw.Draw(lab).text((6,3),label,font=lf,fill=(255,255,255))
    t=Image.new('RGBA',(bg.width,bg.height+20)); t.paste(lab,(0,0)); t.paste(bg,(0,20)); tiles.append(t)
out=Image.new('RGB',(tiles[0].width*2,tiles[0].height*2))
for i,t in enumerate(tiles): out.paste(t.convert('RGB'),((i%2)*t.width,(i//2)*t.height))
out.save('/tmp/win_options.png'); print(out.size)
