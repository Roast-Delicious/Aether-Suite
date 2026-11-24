exec(open('pack_mock.py').read().split('# B: compact')[0])
GREEN=(110,210,120); RED=(240,95,85)
def textrows(d,x,vx,y,sp,R,fs=15):
    for i,(n,v,col) in enumerate(R):
        yy=y+i*sp
        d.text((x*S,yy*S),n,font=F('Regular',fs),fill=(200,205,215),anchor='lm')
        d.text((vx*S,yy*S),v,font=F('SemiBold',fs),fill=col,anchor='rm')
def build(R,lab,x=420,vx=608):
    im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
    c=down(im); c.alpha_composite(slot,(27,38)); c.alpha_composite(ink,(87,35))
    im=up(c); d=ImageDraw.Draw(im); textrows(d,x,vx,48,19,R)
    return label(down(im).crop((0,0,648,108)),lab)
A=build([("Bags","22 free",GREEN),("Reagent","Full",RED),("Ammo","2,612",GREEN)],"C1, text only")
B=build([("Bags","22 of 50 free",GREEN),("Reagent","Full (6 of 6)",RED),("Ammo","2,612 of 2,800",GREEN)],"C1, text only, with totals",x=400)
im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
c=down(im); c.alpha_composite(slot,(27,38)); c.alpha_composite(ink,(87,35))
im=up(c); d=ImageDraw.Draw(im); textrows(d,420,608,48,19,[("Bags","3 free",(255,209,0)),("Reagent","Full",RED),("Ammo","Low: 180",RED)])
W=label(down(im).crop((0,0,648,108)),"Same, when things get tight")
foot=stack([nowf,A,B,W]); foot.save('freeC1_text.png')
