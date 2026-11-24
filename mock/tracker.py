from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, math
SS=3
FD='/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
def F(w,px): return ImageFont.truetype(FD+w+'.ttf',int(px*SS))
GOLD=(255,176,0); GOLD_L=(255,214,110); NAVY=(19,40,74); BLUE=(77,166,255); WHITE=(230,232,238); SOFT=(200,204,212)
ORANGE=(255,128,64); GREEN=(34,230,80); GRAY=(160,160,160)
Q=[(31,"Hunting in Stranglethorn",GOLD,True,["Bring Roon's Kodo Horn to Hemet","Nesingwary in Stranglethorn."],GREEN),
   (32,"Investigate the Camp",GOLD,False,["- Locate the hunters' camp"],None),
   (35,"Bloodscalp Ears",GOLD,False,["- 0/15 Bloodscalp Ear"],None),
   (35,"Singing Blue Shards",GOLD,False,["- 0/10 Singing Crystal Shard"],None),
   (35,"The Troll Witchdoctor",GOLD,True,["Take the Defiant Orc Head to","Kin'weelay in the Grom'gol Base","Camp in Stranglethorn Vale."],None),
   (35,"Tiger Mastery",GOLD,True,["Ready for turn-in"],"ready"),
   (36,"Hostile Takeover",ORANGE,False,["- 0/8 Tumbled Crystal"],None),
   (36,"Raptor Mastery",ORANGE,False,["- 0/10 Lashtail Raptor slain"],None),
   (37,"Headhunting",ORANGE,False,["- 0/20 Shrunken Head"],None),
   ("37+","The Vile Reef (Elite)",ORANGE,False,["- 0/1 Tablet Shard"],None),
   (38,"Panther Mastery",ORANGE,False,["- 0/10 Shadowmaw Panther slain"],None)]
# The first quest is "Hunting in Stranglethorn" (green in game: 3+ below you)
Q[0]=(31,"Hunting in Stranglethorn",(64,200,64),True,Q[0][4],None)
random.seed(5)
def backdrop(w,h):
    bg=Image.new('RGB',(w,h),(126,96,60)); d=ImageDraw.Draw(bg)
    for _ in range(160):
        x,y=random.randint(0,w),random.randint(0,h); r=random.randint(30,110)
        d.ellipse([x-r,y-r,x+r,y+r],fill=random.choice([(140,104,64),(116,90,56),(70,84,60),(56,70,58),(150,118,74),(90,96,66)]))
    return bg.filter(ImageFilter.GaussianBlur(18)).convert('RGBA')
def poi(im,cx,cy,r,done):
    d=ImageDraw.Draw(im); r*=SS; cx*=SS; cy*=SS
    gl=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(gl).ellipse([cx-r*1.5,cy-r*1.5,cx+r*1.5,cy+r*1.5],fill=GOLD+(70,))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(r*0.5)))
    d=ImageDraw.Draw(im)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=NAVY+(240,),outline=GOLD,width=int(1.6*SS))
    if done: d.text((cx,cy+0.5*SS),"?",font=F('Bold',15),fill=GOLD,anchor='mm')
    else:
        for k in (-1,0,1): d.ellipse([cx+k*5*SS-1.8*SS,cy-1.8*SS,cx+k*5*SS+1.8*SS,cy+1.8*SS],fill=GOLD)
def chevron(d,cx,cy,size,direction):
    # small gold chevron pointing outward (direction: 'left'/'right'/'up'/'down')
    s=size*SS; cx*=SS; cy*=SS
    if direction=='left': P=[(cx+s*0.4,cy-s),(cx-s*0.4,cy),(cx+s*0.4,cy+s)]
    elif direction=='right': P=[(cx-s*0.4,cy-s),(cx+s*0.4,cy),(cx-s*0.4,cy+s)]
    d.line(P,fill=(10,12,18),width=int(5.5*SS),joint='curve'); d.line(P,fill=GOLD,width=int(3*SS),joint='curve')
def header(im,x0,x1,y,text,big=False):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle([x0*SS,y*SS,x1*SS,(y+30)*SS],radius=6*SS,fill=NAVY+(235,))
    d.line([x0*SS,(y+30)*SS,x1*SS,(y+30)*SS],fill=GOLD,width=int(1.3*SS))
    d.text(((x0+14)*SS,(y+15)*SS),text,font=F('SemiBold',19),fill=GOLD,anchor='lm')
    # fold button: Aether style, navy square with blue edge and a gold minus
    bx=x1-26; d.rectangle([bx*SS,(y+6)*SS,(bx+18)*SS,(y+24)*SS],outline=BLUE,width=int(1.2*SS),fill=(10,20,40))
    d.line([(bx+5)*SS,(y+15)*SS,(bx+13)*SS,(y+15)*SS],fill=GOLD,width=int(2*SS))
PH=806
def tracker(variant):
    W,H=502,900
    im=backdrop(W*SS,H*SS); d=ImageDraw.Draw(im)
    x0,x1=62,470; y=30
    if variant in ('B','C'):
        # soft navy panel with Aether trim behind the list
        ph=PH
        pan=Image.new('RGBA',im.size,(0,0,0,0)); pd=ImageDraw.Draw(pan)
        pd.rounded_rectangle([(x0-8)*SS,(y-6)*SS,(x1+8)*SS,(y+ph)*SS],radius=8*SS,fill=(13,15,23,150),outline=BLUE+(200,),width=int(1.2*SS))
        gl=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(gl).rounded_rectangle([(x0-12)*SS,(y-10)*SS,(x1+12)*SS,(y+ph+4)*SS],radius=12*SS,outline=BLUE+(90,),width=int(6*SS))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(4*SS))); im.alpha_composite(pan)
        d=ImageDraw.Draw(im)
        chevron(d,x0-11,y+ph/2,9,'left'); chevron(d,x1+11,y+ph/2,9,'right')
    header(im,x0,x1,y,"Quests"); d=ImageDraw.Draw(im)
    y+=44
    tf=F('SemiBold',18.5); of=F('Regular',17.5)
    for lvl,title,col,done,lines,extra in Q:
        cy=y+11
        poi(im,x0+18,cy,12,done); d=ImageDraw.Draw(im)
        tx=x0+42
        if variant=='C':
            lv=str(lvl); w=d.textlength(lv,font=F('Bold',13))/SS+12
            d.rounded_rectangle([tx*SS,(cy-9)*SS,(tx+w)*SS,(cy+9)*SS],radius=9*SS,fill=col+(255,))
            d.text(((tx+w/2)*SS,(cy+0.5)*SS),lv,font=F('Bold',13),fill=(12,14,20),anchor='mm')
            d.text(((tx+w+7)*SS,cy*SS),title,font=tf,fill=col,anchor='lm',stroke_width=SS,stroke_fill=(0,0,0))
        else:
            d.text((tx*SS,cy*SS),f"[{lvl}] {title}",font=tf,fill=col,anchor='lm',stroke_width=SS,stroke_fill=(0,0,0))
        yy=cy+22
        for ln in lines:
            c=GREEN if extra=="ready" else SOFT
            d.text(((tx+(0 if ln.startswith('-') else 12))*SS,yy*SS),ln,font=of,fill=c,anchor='lm',stroke_width=SS,stroke_fill=(0,0,0))
            yy+=21
        y=yy+9
    return im.resize((W,H),Image.LANCZOS)
now=Image.open('/mnt/user-data/uploads/03e628c0-image.png').convert('RGBA').crop((40,60,502,880))
ims=[('Now',now),('A. Aether header, list on the map',tracker('A')),('B. Plus a soft Aether panel and chevrons',tracker('B')),('C. Plus level badges',tracker('C'))]
fl=ImageFont.truetype(FD+'SemiBold.ttf',18)
out=Image.new('RGBA',(sum(i.width for _,i in ims)+30*3,ims[1][1].height+34),(30,32,40,255)); x=0
for name,i in ims:
    ImageDraw.Draw(out).text((x+8,8),name,font=fl,fill=(255,255,255)); out.alpha_composite(i,(x,34)); x+=i.width+30
out.save('tracker_options.png'); print(out.size)
