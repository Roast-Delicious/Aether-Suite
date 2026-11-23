exec(open('badges_w.py').read().split('rows=[')[0])
def qq(border_px, RD=23):
    # same outer size as every badge (23 units); the black ring grows inward
    total=RD*K
    S=int(total*SS); im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,S-1,S-1],fill=(10,10,12,255))
    o=int(border_px*SS); d.ellipse([o,o,S-1-o,S-1-o],fill=C((1,0.13,0.13))+(255,))
    f=ImageFont.truetype(FIRA,int(9*K*SS))
    d.text((S/2,S/2+0.3*K*SS),"??",font=f,fill=(255,255,255,255),anchor='mm',stroke_width=int(K*SS),stroke_fill=(10,10,12,255))
    return im.resize((max(1,round(total)),max(1,round(total))),Image.LANCZOS)
opts=[("Now (A+)",None),("3px",3),("4px",4),("5px",5),("6px",6)]
W=360; H=110
bg=Image.open('/tmp/v4/f_057.png').convert('RGBA').crop((1350,560,1350+W,560+H)); d=ImageDraw.Draw(bg)
lf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',10)
x=10
for label,bp in opts:
    b=badge('W','red','??',(1,0.13,0.13)) if bp is None else qq(bp)
    d.text((x,8),label,font=lf,fill=(255,255,255),stroke_width=1,stroke_fill=(0,0,0))
    bg.alpha_composite(b,(x,60-b.height//2))
    x+=max(60,b.width+16)
bg=bg.convert('RGB'); bg.save('/tmp/qq2_actual.png'); bg.resize((W*3,H*3),Image.LANCZOS).save('/tmp/qq2_3x.png')
