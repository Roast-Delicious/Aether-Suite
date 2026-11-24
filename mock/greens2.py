exec(open('pack_mock.py').read().split('# B: compact')[0])
RED=(240,95,85); AG=(255,176,0)
opts=[("Now: soft green",(110,219,120)),("F. Vivid green",(34,230,80)),("G. Electric",(0,230,118)),("H. Spring",(0,255,127)),("I. Bright lime",(110,255,60)),("J. Neon",(57,255,20))]
def card(name,G):
    im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
    c=down(im); c.alpha_composite(slot,(27,38)); c.alpha_composite(ink,(87,35))
    im=up(c); d=ImageDraw.Draw(im)
    f1=F('Regular',15); f2=F('SemiBold',15)
    R=[("Bags",[("22 free",G)]),("Reagent",[("Full",RED)]),("Ammo",[("Warning",AG),("1,350",WHITE)])]
    for i,(n,parts) in enumerate(R):
        yy=48+i*19; d.text((420*S,yy*S),n,font=f1,fill=(200,205,215),anchor='lm'); x=608
        for t,col in reversed(parts):
            d.text((x*S,yy*S),t,font=f2,fill=col,anchor='rm'); x-=d.textlength(t,font=f2)/S+5
    return label(down(im).crop((0,0,648,100)),name+"   #%02x%02x%02x"%G)
stack([card(n,g) for n,g in opts]).save('greens_vivid.png')
