from PIL import Image, ImageDraw, ImageFont
import numpy as np
src=Image.open('/tmp/v4/f_057.png').convert('RGB')
X0,X1,Y0,Y1=924,1711,1272,1282          # bar interior (x1,y1 exclusive)
EARN,REST=0.58,0.75
W=X1-X0; H=Y1-Y0
def C(*c): return np.array(c,np.float32)
NAVY=C(28,74,150); NAVY_DARK=C(18,43,82); BLUE=C(77,166,255); GOLD=C(255,209,0); BG=C(10,12,18)
def bar(earned_col, rested_col, rested_alpha=0.55, ticks=C(0,0,0), tick_a=0.55, spark=None, earned_rested_col=None):
    a=np.zeros((H,W,3),np.float32); a[:]=BG
    ex=int(W*EARN); rx=int(W*REST)
    shade=np.linspace(1.18,0.82,H)[:,None,None]      # light from above, like the other bars
    if rested_col is not None:
        a[:,ex:rx]=BG*(1-rested_alpha)+rested_col*rested_alpha
    col=earned_rested_col if earned_rested_col is not None else earned_col
    a[:,:ex]=col
    a=a*shade
    for i in range(1,20):
        x=int(round(W*i/20)); a[:,x]=a[:,x]*(1-tick_a)+ticks*tick_a
    if spark is not None: a[:,max(0,ex-1):ex+1]=spark
    return np.clip(a,0,255).astype(np.uint8)
opts=[
 ("Now (Blizzard purple)", None),
 ("A  Your idea: navy earned, bright blue rested", bar(NAVY, BLUE, rested_alpha=0.85)),
 ("B  Bright blue earned while rested, navy when not", bar(NAVY, BLUE, rested_alpha=0.35, earned_rested_col=BLUE)),
 ("C  Like A, plus gold ticks and a gold tip", bar(NAVY, BLUE, rested_alpha=0.85, ticks=GOLD, tick_a=0.35, spark=GOLD)),
 ("D  Aether blue earned, gold rested", bar(BLUE*0.85, GOLD, rested_alpha=0.45)),
]
crop=(900,1258,1730,1296)
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',12)
rows=[]
for label,b in opts:
    im=src.copy()
    if b is not None: im.paste(Image.fromarray(b),(X0,Y0))
    c=im.crop(crop)
    lab=Image.new('RGB',(c.width,18),(20,20,24)); ImageDraw.Draw(lab).text((6,2),label,font=lf,fill=(255,255,255))
    rows+=[lab,c]
Wt=crop[2]-crop[0]; Ht=sum(r.height for r in rows)
out=Image.new('RGB',(Wt,Ht)); y=0
for r in rows: out.paste(r,(0,y)); y+=r.height
out.save('/tmp/xp_actual.png')
z=out.crop((0,0,420,Ht)).resize((840,Ht*2),Image.NEAREST); z.save('/tmp/xp_zoom.png')
print(out.size)
