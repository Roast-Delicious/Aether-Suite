import math
exec(open('frames_aura_test.py').read().split("def icons")[0])
L.execute(r'''
AetherFramesPet.shown=true
TH={}; PCT=nil
UnitThreatSituation=function(u,m) if m then return TH["T"] end return TH[u] end
UnitDetailedThreatSituation=function(u,m) return false, TH["T"], PCT, PCT, 0 end
function EFF(f) local m=0 for _,t in pairs(f.glow) do m=math.max(m,t.alpha) end return m end
function Run(sec) local mn,mx=9,-9 for i=1,math.floor(sec/0.02) do EV.scripts.OnUpdate(EV,0.02)
  local a=EFF(AetherFramesPlayer) if i*0.02>0.6 then mn=math.min(mn,a); mx=math.max(mx,a) end end return mn,mx end
''')
def case(label, setup, sec=3.2):
    L.execute(setup)
    mn,mx = L.eval('{Run(%s)}' % sec).values()
    p,pt,t = L.eval('AetherFramesPlayer'), L.eval('AetherFramesPet'), L.eval('AetherFramesTarget')
    def st(f):
        return "%-5s alpha %.2f" % (f.glowMode, L.eval('EFF')(f))
    print("%-44s you: %s (range %.2f-%.2f) | Steve: %s | target: %s" % (label, st(p), mn, mx, st(pt), st(t)))
case("out of combat", 'TH={}; PCT=nil')
case("fighting, Steve tanking, you low (40%)", 'TH={player=0, pet=3, T=0}; PCT=40')
case("you at 85% of Steve's threat", 'TH={player=0, pet=3, T=0}; PCT=85')
case("you out-threat Steve (1)", 'TH={player=1, pet=2, T=1}; PCT=110')
case("mob on you (3)", 'TH={player=3, pet=0, T=3}; PCT=100')
case("threat hidden by the game", 'TH={player=S(3), pet=S(3), T=S(3)}; PCT=S(90)')
L.execute('TH={player=3,pet=3,T=3}; SlashCmdList.AETHERFRAMES("threat off")')
case("glow turned off", '')
print("color:", list(L.eval('AetherFramesPlayer.glow.solid.vc').values())[:3], "| errors:", L.eval('#ERRS'))
# pulse periods: count peaks over 3.2 s
L.execute('SlashCmdList.AETHERFRAMES("threat on")')
for label, setup in (("slow", 'TH={player=0,T=0}; PCT=90'), ("fast", 'TH={player=1,T=1}')):
    L.execute(setup + '; SAMPLES={}; for i=1,320 do EV.scripts.OnUpdate(EV,0.01); SAMPLES[i]=EFF(AetherFramesPlayer) end')
    s=[L.eval('SAMPLES')[i] for i in range(1,321)]
    peaks=sum(1 for i in range(1,319) if s[i]>s[i-1] and s[i]>=s[i+1] and s[i]>0.5)
    print(label, "pulse: peaks in 3.2 s =", peaks)
