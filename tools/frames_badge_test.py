exec(open('frames_aura_test.py').read().split("def icons")[0])
L.execute(r'''
AetherFramesPet.shown=true
C_CurveUtil={CreateCurve=function() local c={pts={}}
  function c:AddPoint(x,y) self.pts[#self.pts+1]={x,y} end
  function c:ClearPoints() self.pts={} end
  function c:Evaluate(x) if getmetatable(x)==SM then x=x.v end
    local p=self.pts; if x<=p[1][1] then return p[1][2] end
    for i=2,#p do if x<=p[i][1] then local a,b=p[i-1],p[i]; return a[2]+(b[2]-a[2])*(x-a[1])/(b[1]-a[1]) end end
    return p[#p][2] end
  return c end}
UnitClassification=function(u) return UNITS[u] and UNITS[u].class or "normal" end
''')
def badge(unit):
    b=L.eval('AetherFrames%s.badge' % unit)
    c=b.disc.vc
    names={(1,0.82,0):"gold/yellow",(1,0.13,0.13):"red",(1,0.5,0.13):"orange",(0.25,0.75,0.25):"green",(0.55,0.55,0.55):"gray"}
    warn=" + RED RING" if b.warnRing.shown else ""
    tc=b.text.tc if hasattr(b.text,'tc') else None
    return "%s on %s%s" % (b.text.text, names.get((round(c[1],2),round(c[2],2),round(c[3],2)),str(c)), warn)
L.execute('UNITS.player.lvl=34')
for lvl,cls,label in ((40,None,"+6"),(37,None,"+3"),(36,None,"+2"),(32,None,"-2"),(28,None,"-6"),(25,None,"-9"),(36,"elite","elite"),(-1,None,"boss/unknown")):
    L.execute('UNITS.target={name="Mob",lvl=%d,hp=1,hpm=1,pw=0,pwm=0,pt=0,tok="MANA",enemy=true,class=%s}; AetherFramesTarget.shown=true; EV.scripts.OnEvent(EV,"PLAYER_TARGET_CHANGED")' % (lvl, '"%s"'%cls if cls else 'nil'))
    print("target level %3d (%-12s) -> badge %s" % (lvl, label, badge("Target")))
L.execute('AetherFramesPlayer.scripts.OnShow(AetherFramesPlayer)')
print("your badge ->", badge("Player"), "| your name-row level text:", repr(L.eval('AetherFramesPlayer.levelFS.text')))
def mood():
    b=L.eval('AetherFramesPet.happyMedal')
    al=[round(b.layers[i][1].alpha,2) for i in (1,2,3)]
    return "shown" if b.shown else "hidden", dict(zip(("sad","content","happy"),al))
for h,label in ((3,"happy"),(2,"content"),(1,"unhappy"),(None,"no happiness (not a hunter pet)"),("S(3)","hidden value, happy"),("S(1)","hidden value, unhappy")):
    L.execute('GetPetHappiness=function() return %s end; for i=1,10 do EV.scripts.OnUpdate(EV,0.1) end' % ('nil' if h is None else h))
    print("happiness %-32s -> %s" % (label, mood()))
L.execute('TH={}; UnitThreatSituation=function(u,m) if m then return TH.T end return TH[u] end; UnitDetailedThreatSituation=function() return false, TH.T, PCT, PCT, 0 end')
def glow(f):
    g=L.eval('AetherFrames%s.glow'%f)
    return L.eval('AetherFrames%s.glowMode'%f)+" "+",".join("%s=%.2f"%(k,g[k].alpha) for k in ("solid","fast","slow","dim"))
for setup,label in (('TH={player=3,pet=0,T=3}','readable: mob on you'),('TH={player=0,pet=3,T=0}; PCT=90','readable: Steve tanks, you at 90%'),
                    ('TH={player=S(1),pet=S(2),T=S(1)}','hidden: you at 1, Steve at 2'),('TH={player=S(3),pet=S(3),T=S(3)}','hidden: on you, Steve 3')):
    L.execute(setup+'; for i=1,3 do EV.scripts.OnUpdate(EV,0.05) end')
    print("%-36s you: %s | Steve: %s" % (label, glow("Player"), glow("Pet")))
print("errors:", L.eval('#ERRS'))
