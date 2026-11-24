exec(open('tracker.py').read().split("now=Image.open")[0])
import numpy as np
def taper_line(im,x0,x1,y,thick,color,fade_ends=True,center_bright=False):
    # a line thickest in the middle, tapering to points at both ends
    W=im.width; L=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(L)
    x0*=SS;x1*=SS;y*=SS;t=thick*SS/2
    d.polygon([(x0,y),( (x0+x1)/2,y-t),(x1,y),((x0+x1)/2,y+t)],fill=color+(255,))
    if fade_ends:
        a=np.array(L); xs=np.arange(W); mid=(x0+x1)/2; half=(x1-x0)/2
        f=np.clip(1-np.abs(xs-mid)/half,0,1)**0.6
        a[...,3]=(a[...,3]*f[None,:]).astype(np.uint8); L=Image.fromarray(a)
    im.alpha_composite(L)
def band(im,x0,x1,y0,y1,color,alpha,mode):
    W=im.width; xs=np.arange(W)/SS
    ramp=np.clip((xs-x0)/24,0,1)                       # soft start over 24 units
    if mode=='left': f=ramp*np.clip(1-(xs-x0)/(x1-x0),0,1)**0.9
    else: f=ramp*np.clip((x1-xs)/40,0,1)                 # even, soft at both ends
    f[(xs<x0)|(xs>x1)]=0
    a=np.zeros((im.height,W,4),np.uint8); a[...,0:3]=color
    rows=slice(int(y0*SS),int(y1*SS)); a[rows,:,3]=(alpha*f*255)[None,:]
    L=Image.fromarray(a).filter(ImageFilter.GaussianBlur(2*SS)); im.alpha_composite(L)
def chev_cap(d,x,y,direction,size=5):
    s=size*SS; x*=SS; y*=SS
    P=[(x-s*0.5,y-s),(x+s*0.5,y),(x-s*0.5,y+s)] if direction=='right' else [(x+s*0.5,y-s),(x-s*0.5,y),(x+s*0.5,y+s)]
    d.line(P,fill=(10,12,18),width=int(3.6*SS),joint='curve'); d.line(P,fill=GOLD,width=int(2*SS),joint='curve')
def hdr(im,variant,x0,x1,y):
    d=ImageDraw.Draw(im)
    if variant=='H1':   # navy band fading to the right, tapered gold line
        band(im,x0-4,x1+10,y+2,y+30,NAVY,0.9,'left')
        taper_line(im,x0-6,x1+6,y+31,3.4,GOLD)
    elif variant=='H2': # no band: tapered gold line with Aether chevron caps
        taper_line(im,x0+6,x1-6,y+31,3.2,GOLD,fade_ends=False)
        d=ImageDraw.Draw(im); chev_cap(d,x0,y+31,'left',7); chev_cap(d,x1,y+31,'right',7)
    elif variant=='H3': # navy band darkest in the middle, blue line with a gold center
        band(im,x0-6,x1+6,y+2,y+30,NAVY,0.72,'even')
        taper_line(im,x0-6,x1+6,y+31,3.0,BLUE,fade_ends=False)
        taper_line(im,x0+60,x1-60,y+31,3.4,GOLD)
    d=ImageDraw.Draw(im)
    d.text(((x0+12)*SS,(y+16)*SS),"Quests",font=F('SemiBold',21),fill=GOLD,anchor='lm',stroke_width=SS,stroke_fill=(0,0,0))
    # plain gold minus, like Blizzard's (no box)
    d.line([(x1-26)*SS,(y+16)*SS,(x1-12)*SS,(y+16)*SS],fill=(10,12,18),width=int(5*SS))
    d.line([(x1-26)*SS,(y+16)*SS,(x1-12)*SS,(y+16)*SS],fill=GOLD,width=int(3*SS))
def panel(variant):
    W,H=502,300
    im=backdrop(W*SS,H*SS); x0,x1=62,470; y=20
    hdr(im,variant,x0,x1,y); d=ImageDraw.Draw(im)
    y+=46; tf=F('SemiBold',18.5); of=F('Regular',17.5)
    for lvl,title,col,done,lines,extra in Q[:4]:
        cy=y+11; poi(im,x0+18,cy,12,done); d=ImageDraw.Draw(im); tx=x0+42
        d.text((tx*SS,cy*SS),f"[{lvl}] {title}",font=tf,fill=col,anchor='lm',stroke_width=SS,stroke_fill=(0,0,0))
        yy=cy+22
        for ln in lines:
            d.text(((tx+(0 if ln.startswith('-') else 12))*SS,yy*SS),ln,font=of,fill=SOFT,anchor='lm',stroke_width=SS,stroke_fill=(0,0,0)); yy+=21
        y=yy+9
    return im.resize((W,H),Image.LANCZOS)
now=Image.open('/mnt/user-data/uploads/03e628c0-image.png').convert('RGBA').crop((40,110,502,410))
opts=[("Now (Blizzard's Quests bar)",now),("H1. Navy fade + gold line",panel('H1')),("H2. Gold line + chevron caps",panel('H2')),("H3. Navy fade + blue/gold line",panel('H3'))]
fl=ImageFont.truetype(FD+'SemiBold.ttf',18)
out=Image.new('RGBA',(sum(i.width for _,i in opts)+30*3,300+34),(30,32,40,255)); x=0
for name,i in opts:
    ImageDraw.Draw(out).text((x+8,8),name,font=fl,fill=(255,255,255)); out.alpha_composite(i,(x,34)); x+=i.width+30
out.save('headers.png')
z=Image.new('RGBA',(3*500+60,130),(30,32,40,255)); x=0
for name,i in opts[1:]:
    c=i.crop((50,12,480,62)); c=c.resize((c.width*1.15.__int__() if False else 500,int(c.height*500/c.width)),Image.LANCZOS)
    z.alpha_composite(c,(x,20)); ImageDraw.Draw(z).text((x+4,2),name.split('.')[0],font=fl,fill=(255,255,255)); x+=530
z.save('headers_zoom.png'); print('ok')
