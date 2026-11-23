from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import math
SC=6; K=1.15; M=10   # hi-res scale, px per unit at actual size, renderer margin (hi-res px)
FW,FH,PORT,BADGE=eval(open('/tmp/pp_meta.txt').read())
src=Image.open('/tmp/glyph_frames.png').convert('RGBA')
def portrait(cx,cy,mirror=False,gray=False):
    r=36.5
    p=src.crop((round(cx-r),round(cy-r),round(cx+r),round(cy+r))).resize((276,276),Image.LANCZOS)
    if mirror: p=ImageOps.mirror(p)
    if gray: p=ImageEnhance.Brightness(ImageOps.grayscale(p).convert('RGBA')).enhance(0.6)
    m=Image.new('L',(276*4,276*4),0); ImageDraw.Draw(m).ellipse([0,0,276*4-1,276*4-1],fill=255)
    p.putalpha(m.resize((276,276),Image.LANCZOS)); return p
JAY=(62.5,76.65); THY=(679.5,76.15)
FIRA='/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf'
NUM='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
nameF=ImageFont.truetype(FIRA,int(11*SC)); numF=ImageFont.truetype(NUM,int(10.5*SC)); badgeF=ImageFont.truetype(FIRA,int(11*SC))
timF=ImageFont.truetype(NUM,int(9.5*SC))
GOLD=(255,209,0); WHITE=(255,255,255); GRAY=(150,150,150)
def text(d,x,y,s,font,col,anchor,stroke=True):
    d.text((M+x*SC,M+y*SC),s,font=font,fill=col,anchor=anchor,stroke_width=SC if stroke else 0,stroke_fill=(0,0,0))
members=[
 dict(i=1,name="Thyme",port=(THY,False,False),hp=("100%","1,762"),pw=("100%","1,445")),
 dict(i=2,name="Brannoc",port=(JAY,True,False),hp=("64%","1,410"),pw=("35%","35"),debuffs=[(0,(0.6,0,1),"12s"),(2,(0,0.6,0),"8s")]),
 dict(i=3,name="Lyssa",port=(THY,True,False),hp=("74%","880"),pw=("82%","1,350"),fade=0.45),
 dict(i=4,name="Vexmire",port=(JAY,False,True),hp=("Offline",""),pw=("",""),offline=True),
]
lvls={1:"35",2:"33",3:"34",4:"32"}
frames=[]
for m in members:
    out='/tmp/pp%d.png'%m['i']; im=Image.open(out).convert('RGBA')
    full=Image.new('RGBA',(im.width+int(64*SC),im.height),(0,0,0,0))
    l,t,w,h=PORT[out]; (pc,mir,gr)=m['port']
    full.alpha_composite(portrait(*pc,mirror=mir,gray=gr),(int(l),int(t)))
    full.alpha_composite(im)
    d=ImageDraw.Draw(full)
    text(d,80,19,m['name'],nameF,GRAY if m.get('offline') else GOLD,'lm')
    for (a,b),y in ((m['hp'],36),(m['pw'],50)):
        if a: text(d,82,y,a,numF,WHITE,'lm')
        if b: text(d,194,y,b,numF,WHITE,'rm')
    bx,by=BADGE[out]; d.text((bx,by-0.6*SC),lvls[m['i']],font=badgeF,fill=(18,18,23),anchor='mm')
    for k,(idx,col,tm) in enumerate(m.get('debuffs',[])):
        x0=int((FW+4+k*24)*SC+M); y0=int(26*SC+M); s=20*SC
        ix=259.3+idx*38.5
        ic=src.crop((round(ix+2),123,round(ix+25),146)).resize((s-4*SC,s-4*SC),Image.LANCZOS)
        d.rectangle([x0,y0,x0+s,y0+s],fill=(10,10,12,255))
        d.rectangle([x0+SC,y0+SC,x0+s-SC,y0+s-SC],fill=tuple(int(c*255) for c in col)+(255,))
        full.alpha_composite(ic,(x0+2*SC,y0+2*SC))
        d.text((x0+s/2,y0+s+6*SC),tm,font=timF,fill=WHITE,anchor='mm',stroke_width=SC,stroke_fill=(0,0,0))
    if m.get('fade'):
        a=full.split()[3].point(lambda v:int(v*m['fade'])); full.putalpha(a)
    frames.append(full)
# actual size: units -> K px
STRIDE=84
tw=frames[0].width/SC*K; th=(STRIDE*3+FH+14)*K
W_,H_=int(tw)+24,int(th)+24
bg=Image.open('/tmp/v4/f_057.png').convert('RGBA').crop((40,520,40+W_,520+H_))
hi=Image.new('RGBA',(int(W_/K*SC),int(H_/K*SC)),(0,0,0,0))
for n,fimg in enumerate(frames):
    hi.alpha_composite(fimg,(int(12/K*SC),int((12/K+n*STRIDE)*SC)))
small=hi.resize((W_,H_),Image.LANCZOS)
canvas=bg.copy(); canvas.alpha_composite(small.crop((0,0,W_,H_)))
canvas=canvas.convert('RGB'); canvas.save('/tmp/party_actual.png')
canvas.resize((canvas.width*2,canvas.height*2),Image.LANCZOS).save('/tmp/party_2x.png')
print(canvas.size)
