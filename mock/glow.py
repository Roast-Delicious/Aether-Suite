from PIL import Image, ImageDraw, ImageFont
import numpy as np
src=Image.open('/mnt/user-data/uploads/3e26aa29-image.png').convert('RGB')
a=np.array(src).astype(np.float32)
H,W=a.shape[:2]
x0,x1,y0=126,1197,56          # window's outer edge (right edge exclusive at 1198)
gold=(a[...,0]>180)&(a[...,1]>130)&(a[...,2]<90)
b=a.copy()
# 1) take out today's flat band (6 px) by copying the ground just beyond it
for y in range(y0-6,H):
    for x in range(x0-6,x0):
        if not gold[y,x]: b[y,x]=a[y,x-6]
    for x in range(x1+1,x1+7):
        if x+6<W and not gold[y,x]: b[y,x]=a[y,x+6]
for x in range(x0-6,x1+7):
    for y in range(y0-6,y0):
        if not gold[y,x]: b[y,x]=a[y-6,x]
# 2) a real glow: strongest at the edge, fading out over ~15 px (10 units at this UI scale)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
dx=np.maximum(np.maximum(x0-0.5-xx, xx-(x1+0.5)),0); dy=np.maximum(y0-0.5-yy,0)
d=np.hypot(dx,dy); outside=(xx<x0)|(xx>x1)|(yy<y0)
R=10.0
al=np.where(outside&(d<=R), 0.42*(1-d/R)**2, 0)[...,None]
blue=np.array([77,166,255],np.float32)
b=b*(1-al)+blue*al
b[gold]=a[gold]                 # gold corners stay on top
B=Image.fromarray(b.clip(0,255).astype(np.uint8))
crop=(40,20,760,394)
A1=src.crop(crop); B1=B.crop(crop)
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
def lab(im,t):
    d=ImageDraw.Draw(im); d.text((10,6),t,font=lf,fill=(255,255,255),stroke_width=2,stroke_fill=(0,0,0)); return im
out=Image.new('RGB',(A1.width,A1.height*2+8),(0,0,0))
out.paste(lab(A1,"Now: flat 4-unit band"),(0,0)); out.paste(lab(B1,"Option 2: soft glow, 10 px"),(0,A1.height+8))
out.save('/tmp/glow10_compare.png')
zc=(80,10,330,200)
z=Image.new('RGB',((zc[2]-zc[0])*3*2+12,(zc[3]-zc[1])*3),(0,0,0))
z.paste(src.crop(zc).resize(((zc[2]-zc[0])*3,(zc[3]-zc[1])*3),Image.NEAREST),(0,0))
z.paste(B.crop(zc).resize(((zc[2]-zc[0])*3,(zc[3]-zc[1])*3),Image.NEAREST),((zc[2]-zc[0])*3+12,0))
z.save('/tmp/glow10_zoom.png')
