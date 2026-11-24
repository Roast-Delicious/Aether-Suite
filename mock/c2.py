exec(open('pack_mock.py').read().split('# B: compact')[0])
def rows(d,x,y,lw,bw,vx,sp,fs=14):
    R=[("Bags",28/50,(110,200,120),"22 free",WHITE),("Reagent",1.0,AMBER,"Full",AMBER),("Ammo",2612/2800,(110,200,120),"2,612",WHITE)]
    for i,(n,fr,c,v,vc) in enumerate(R):
        yy=y+i*sp
        d.text((x*S,yy*S),n,font=F('Regular',fs),fill=(200,205,215),anchor='lm')
        bx=x+lw; d.rounded_rectangle([bx*S,(yy-2.5)*S,(bx+bw)*S,(yy+2.5)*S],radius=3*S,fill=(28,40,64))
        d.rounded_rectangle([bx*S,(yy-2.5)*S,(bx+bw*fr)*S,(yy+2.5)*S],radius=3*S,fill=c)
        d.text((vx*S,yy*S),v,font=F('SemiBold',fs),fill=vc,anchor='rm')
# C1: bars beside the ink
im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
c=down(im); c.alpha_composite(slot,(27,38)); c.alpha_composite(ink,(87,35))
im=up(c); d=ImageDraw.Draw(im); rows(d,384,48,62,92,608,19)
C1=label(down(im).crop((0,0,648,108)),"C1. Bars beside the ink (one row, shortest)")
# C2: ink kept, bars underneath but short, values right after each bar, all on the left half
im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
c=down(im); c.alpha_composite(slot,(27,38)); c.alpha_composite(ink,(87,35))
im=up(c); d=ImageDraw.Draw(im)
R=[("Bags",28/50,(110,200,120),"22 free",WHITE),("Reagent",1.0,AMBER,"Full",AMBER),("Ammo",2612/2800,(110,200,120),"2,612",WHITE)]
for i,(n,fr,col,v,vc) in enumerate(R):
    x=30+i*196; y=118
    d.text((x*S,y*S),n,font=F('Regular',14),fill=(200,205,215),anchor='lm')
    d.text(((x+176)*S,y*S),v,font=F('SemiBold',14),fill=vc,anchor='rm')
    d.rounded_rectangle([x*S,(y+12)*S,(x+176)*S,(y+17)*S],radius=3*S,fill=(28,40,64))
    d.rounded_rectangle([x*S,(y+12)*S,(x+176*fr)*S,(y+17)*S],radius=3*S,fill=col)
C2=label(down(im).crop((0,0,648,148)),"C2. Bars side by side under the ink")
foot=stack([nowf,C1,C2]); foot.save('freeC_actual.png')
foot.resize((foot.width*2,foot.height*2),Image.LANCZOS).save('freeC_zoom.png')
