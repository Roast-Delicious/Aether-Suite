exec(open('pack_mock.py').read().split('# B: compact')[0])
GREEN=(110,210,120); RED=(240,95,85); AG=(255,176,0); DIMRED=(120,50,48)
def build(R,lab):
    im=up(clean()); d=ImageDraw.Draw(im); header(d,17)
    c=down(im); c.alpha_composite(slot,(27,38)); c.alpha_composite(ink,(87,35))
    im=up(c); d=ImageDraw.Draw(im)
    f1=F('Regular',15); f2=F('SemiBold',15)
    for i,(n,parts) in enumerate(R):
        yy=48+i*19; d.text((420*S,yy*S),n,font=f1,fill=(200,205,215),anchor='lm')
        x=608
        for t,col in reversed(parts):
            d.text((x*S,yy*S),t,font=f2,fill=col,anchor='rm'); x-=d.textlength(t,font=f2)/S+5
    return label(down(im).crop((0,0,648,108)),lab)
bags=("Bags",[("22 free",GREEN)]); reag=("Reagent",[("Full",RED)])
a=build([bags,reag,("Ammo",[("2,612",WHITE)])],"Ammo above half: white count only")
b=build([bags,reag,("Ammo",[("Warning",AG),("1,350",WHITE)])],"Half or less (1,400 of a 2,800 quiver): Warning in Aether gold")
c=build([bags,reag,("Ammo",[("Low",RED),("280",WHITE)])],"300 or less: Low, pulsing (bright)")
d_=build([bags,reag,("Ammo",[("Low",DIMRED),("280",WHITE)])],"... (dim), about once a second")
stack([a,b,c,d_]).save('ammo_states.png')
