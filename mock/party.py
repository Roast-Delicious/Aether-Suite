import os, math
os.chdir('/home/claude/tools')
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageEnhance, ImageFilter
SC_HI=6
src=open('frames_render.py').read()
src=src.replace("exec(open('frames_test.py').read()","exec(open('/tmp/ft_party.py').read()",1)
src=src.replace("SC=3","SC=%d"%SC_HI,1)
# transparent canvas, no scenery
src=src.replace("img=Image.new(\"RGBA\",(int(W*SC)+20,int(H*SC)+20),bg+(255,))","img=Image.new(\"RGBA\",(int(W*SC)+20,int(H*SC)+20),(0,0,0,0))")
src=src.replace("d0.ellipse([0,10,W*SC*0.6,H*SC*0.9],fill=(79,107,46,255)); d0.ellipse([W*SC*0.4,-40,W*SC*1.1,H*SC*0.6],fill=(110,90,58,255))","pass")
# record instead of drawing text / portraits
src=src.replace("""            if o.text:
                col=(255,209,0) if (o.font is None) else (255,255,255)
                d.text((l*SC+2,t*SC+2),str(o.text),fill=(255,255,255,255))
            continue""","            continue")
src=src.replace("""            d.ellipse([l*SC,t*SC,(l+w)*SC,(t+h)*SC],fill=(122,74,58,255)); continue""","""            PORT[out]=(l*SC,t*SC,w*SC,h*SC); continue""")
src=src.replace("""        if o.tex and isinstance(o.tex,str) and "AetherFrames" in o.tex:""","""        if o.tex and isinstance(o.tex,str) and o.tex.endswith("badge_disc"): BADGE[out]=((l+w/2)*SC,(t+h/2)*SC)
        if o.tex and isinstance(o.tex,str) and "AetherFrames" in o.tex:""")
src=src.replace("""        if o.kind=="FontString": lv=5
        return (lv, o.sub or 0)""","""        if o.kind=="FontString": lv=5
        if SAME(o.parent, F.badge) or SAME(o.parent, F.classMedal): lv+=10
        return (lv, o.sub or 0)""")
src=src.split('render("AetherFramesPlayer","/tmp/af_player.png")')[0]
PORT={}; BADGE={}
exec(src)
L.execute('''
PowerBarColor={MANA={r=0,g=0,b=1},RAGE={r=1,g=0,b=0},ENERGY={r=1,g=1,b=0},FOCUS={r=1,g=0.5,b=0.25}}
UnitIsPlayer=function(u) return u~="pet" end
local C={party1={"Paladin","PALADIN"},party2={"Warrior","WARRIOR"},party3={"Priest","PRIEST"},party4={"Mage","MAGE"}}
UnitClass=function(u) local c=C[u] or {"Hunter","HUNTER"}; return c[1],c[2] end
UNITS.party1={name="Thyme",lvl=35,hp=1762,hpm=1762,pw=1445,pwm=1445,pt=0,tok="MANA"}
UNITS.party2={name="Brannoc",lvl=33,hp=1410,hpm=2210,pw=35,pwm=100,pt=1,tok="RAGE"}
UNITS.party3={name="Lyssa",lvl=34,hp=880,hpm=1190,pw=1350,pwm=1640,pt=0,tok="MANA"}
UNITS.party4={name="Vexmire",lvl=32,hp=1080,hpm=1080,pw=1320,pwm=1320,pt=0,tok="MANA"}
for i=1,4 do local f=_G["AetherFramesParty"..i]; f.shown=true; f.scripts.OnShow(f) end
for i=1,12 do EV.scripts.OnUpdate(EV,0.1) end
-- class medallion scaled to the smaller crest
for i=1,4 do local m=_G["AetherFramesParty"..i].classMedal
  for _,o in ipairs(ALL) do if o.parent==m and o.w then o.w=o.w*0.74; o.h=o.h*0.74 end end end
-- offline: gray bars
local f4=_G["AetherFramesParty4"]
for _,o in ipairs(ALL) do if o.kind=="StatusBar" then local p=o.parent; while p do if p==f4 then o.sbc={0.45,0.45,0.45} break end p=p.parent end end end
''')
for i in range(1,5): render("AetherFramesParty%d"%i,"/tmp/pp%d.png"%i)
f=L.eval("AetherFramesParty1"); FW,FH=f.w,f.h
print("frame units",FW,FH, PORT["/tmp/pp1.png"], BADGE.get("/tmp/pp1.png"))
open('/tmp/pp_meta.txt','w').write(repr((FW,FH,PORT,BADGE)))
