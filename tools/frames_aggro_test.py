# Aggro fading: in combat only the target, the target of target and whoever has
# aggro go solid; switches with aggro; hidden (secret) threat levels via curves.
import sys
exec(open('/home/claude/tools/frames_test.py').read().split("for name in")[0])
L.execute(r'''
SM = { __lt=function() error("compared a secret") end, __le=function() error("compared a secret") end,
       __eq=function() error("compared a secret") end, __add=function() error("math on a secret") end,
       __mul=function() error("math on a secret") end }
function S(v) return setmetatable({v=v}, SM) end
issecretvalue=function(v) return getmetatable(v)==SM end
C_CurveUtil={CreateCurve=function() local c={pts={}}
  function c:AddPoint(x,y) self.pts[#self.pts+1]={x,y} end
  function c:ClearPoints() self.pts={} end
  function c:Evaluate(x) if getmetatable(x)==SM then x=x.v end
    local y=self.pts[1][2] for _,p in ipairs(self.pts) do if x>=p[1] then y=p[2] end end return y end
  return c end}
TH={}
UnitThreatSituation=function(u, m) if m ~= "target" then return 99 end return TH[u] end
UNITS.targettarget = UNITS.player
for _, n in ipairs({"AetherFramesPlayer","AetherFramesPet","AetherFramesTarget","AetherFramesTargetTarget"}) do _G[n].shown = true end
function Ring(f) for _,t in ipairs(f.soft) do if (t.baseAlpha or 1) == 1 and not t.isBar then return t.alpha end end end
function Bar(f) for _,t in ipairs(f.soft) do if t.isBar then return t.alpha end end end
function Tick() EV.scripts.OnUpdate(EV, 0.2) end
''')
fails = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m)
    if not c: fails.append(m)
A = lambda n: L.eval('Ring(%s)' % n)
fade = L.eval('AetherFramesDB.alpha'); cfade = L.eval('AetherFramesDB.combatAlpha')
def state(): return {k: A(n) for k, n in [("you", "AetherFramesPlayer"), ("pet", "AetherFramesPet"), ("target", "AetherFramesTarget"), ("tot", "AetherFramesTargetTarget")]}
L.execute('Tick()'); s0 = state()
check(all(v == fade for v in s0.values()), "out of combat: all faded %s" % s0)
L.execute('EV.scripts.OnEvent(EV, "PLAYER_REGEN_DISABLED"); TH={pet=3, player=0}; Tick()'); s = state()
check(s == {"you": cfade, "pet": 1, "target": 1, "tot": 1}, "combat, Steve tanking: pet, target, tot solid; you cfaded %s" % s)
L.execute('TH={pet=0, player=3}; Tick()'); s = state()
check(s["you"] == 1 and s["pet"] == cfade, "you pull aggro: you go solid, Steve cfades %s" % s)
L.execute('TH={pet=2, player=1}; Tick()'); s = state()
check(s["pet"] == 1 and s["you"] == cfade, "insecure aggro (2) counts as aggro; about to pull (1) doesn't %s" % s)
L.execute('TH={}; Tick()'); s = state()
check(s["you"] == cfade and s["pet"] == cfade and s["target"] == 1, "nobody on the target's threat list: only target and tot solid %s" % s)
L.execute('TH={pet=3}; UNITS.target = nil; Tick(); UNITS.target = {name="Bloodfen Raptor",lvl=37,hp=612,hpm=1275,pw=0,pwm=0,pt=1,tok="RAGE",enemy=true}')
check(A("AetherFramesPet") == cfade, "no target: aggro doesn't light anyone up")
# hidden levels
L.execute('TH={pet=S(3), player=S(0)}; Tick()'); s = state()
check(s["pet"] == 1 and s["you"] == cfade, "hidden levels work through curves %s" % s)
L.execute('TH={pet=S(0), player=S(2)}; Tick()'); s = state()
check(s["pet"] == cfade and s["you"] == 1, "hidden levels switch %s" % s)
bases = L.eval('(function() local t={} for _,x in ipairs(AetherFramesPet.soft) do if not x.isBar then t[#t+1]=(x.baseAlpha or 1)..":"..x.alpha end end return table.concat(t," ") end)()')
check(all(abs(float(b) * cfade - float(a)) < 1e-9 for b, a in (p.split(":") for p in bases.split())), "faded textures keep their own base brightness")
# mouse over still solid
L.execute('AetherFramesPet.IsMouseOver = function() return true end; Tick()')
check(A("AetherFramesPet") == 1, "mouse over: solid")
L.execute('AetherFramesPet.IsMouseOver = nil')
# off: old behavior
L.execute('SlashCmdList.AETHERFRAMES("aggro off"); TH={pet=3, player=0}; Tick()'); s = state()
check(all(v == 1 for v in s.values()), "/af aggro off: everything solid in combat %s" % s)
L.execute('SlashCmdList.AETHERFRAMES("aggro on"); Tick()'); s = state()
check(s["you"] == cfade and s["pet"] == 1, "/af aggro on again %s" % s)
# can't read threat: solid
L.execute('UnitThreatSituation = function() error("blocked") end; Tick()')
check(A("AetherFramesPlayer") == 1, "threat can't be read: solid (safe side)")
L.execute('EV.scripts.OnEvent(EV, "PLAYER_REGEN_ENABLED"); Tick()'); s = state()
check(all(v == fade for v in s.values()), "combat over: all faded again %s" % s)
# in combat without aggro: face and bars too
L.execute('EV.scripts.OnEvent(EV, "PLAYER_REGEN_DISABLED"); UnitThreatSituation=function(u, m) if m ~= "target" then return 99 end return TH[u] end; TH={pet=3, player=0}; Tick()')
P = L.eval('AetherFramesPlayer'); PT = L.eval('AetherFramesPet')
check(P.face.alpha == cfade and L.eval('Bar(AetherFramesPlayer)') == 0.45, "no aggro: face to %.0f%%, bars to 45%%" % (cfade * 100))
check(PT.face.alpha == 1 and L.eval('Bar(AetherFramesPet)') == 1, "with aggro: face and bars solid")
check(P.faceBacking is not None and P.faceBacking.shown, "a dark disc sits behind the face")
L.execute('TH={pet=S(3), player=S(0)}; Tick()')
check(P.face.alpha == cfade and L.eval('Bar(AetherFramesPlayer)') == 0.45 and PT.face.alpha == 1, "hidden levels: face and bars too")
L.execute('EV.scripts.OnEvent(EV, "PLAYER_REGEN_ENABLED"); TH={}; Tick()')
check(P.face.alpha == 1 and L.eval('Bar(AetherFramesPlayer)') == fade, "out of combat: face solid, bars at the usual fade")
# whoever the target attacks counts at once, before the threat level catches up
L.execute('UnitThreatSituation=function(u, m) if m ~= "target" then return 99 end return TH[u] end')
L.execute('EV.scripts.OnEvent(EV, "PLAYER_REGEN_DISABLED"); TH={pet=0, player=0}; UNITS.targettarget = UNITS.pet; UnitIsUnit = function(a, b) return UNITS[a] ~= nil and UNITS[a] == UNITS[b] end; Tick()')
check(A("AetherFramesPet") == 1 and A("AetherFramesPlayer") == cfade, "target attacking Steve: his frame lights at once")
L.execute('UnitIsUnit = function() return S(true) end; Tick()')
check(A("AetherFramesPet") == cfade, "hidden answer: falls back to the threat level")
L.execute('UnitIsUnit = nil; UNITS.targettarget = UNITS.player')
# hits
L.execute('NOW = 1000; GetTime = function() return NOW end; EV.scripts.OnEvent(EV, "PLAYER_REGEN_DISABLED")')
G = lambda n: L.eval(n + '.hitGlow.alpha')
L.execute('EV.scripts.OnEvent(EV, "UNIT_COMBAT", "pet", "WOUND", "", 120, 1); EV.scripts.OnUpdate(EV, 0.001)')
check(G('AetherFramesPet') == 1 and G('AetherFramesPlayer') == 0, "Steve hit: his crest flashes red at full")
ringc = lambda n: tuple(round(v, 3) for v in L.eval('{%s.crestBlue.vc[1], %s.crestBlue.vc[2], %s.crestBlue.vc[3]}' % (n, n, n)).values())
check(ringc('AetherFramesPet') == (1.0, 0.16, 0.1), "the blue ring turns red too")
L.execute('NOW = NOW + 0.09; EV.scripts.OnUpdate(EV, 0.09)')
check(G('AetherFramesPet') == 1, "still full red at 0.09 s")
L.execute('NOW = NOW + 0.135; EV.scripts.OnUpdate(EV, 0.135)')
check(0.6 < G('AetherFramesPet') < 0.85, "fading at 0.225 s (%.2f)" % G('AetherFramesPet'))
L.execute('NOW = NOW + 0.13; EV.scripts.OnUpdate(EV, 0.13)')
check(G('AetherFramesPet') == 0 and ringc('AetherFramesPet') == (0.3, 0.7, 1.0), "gone by 0.35 s, ring blue again")
L.execute('EV.scripts.OnEvent(EV, "PLAYER_REGEN_ENABLED"); EV.scripts.OnUpdate(EV, 0.2); EV.scripts.OnEvent(EV, "UNIT_COMBAT", "pet", "WOUND", "", 9, 1); NOW = NOW + 0.5; EV.scripts.OnUpdate(EV, 0.2)')
check(L.eval('AetherFramesPet.crestBlue.alpha') == fade, "a flash on a faded frame leaves its ring faded")
L.execute('EV.scripts.OnEvent(EV, "PLAYER_REGEN_DISABLED")')
check(L.eval('AetherFramesTarget.hitGlow') is None and L.eval('AetherFramesTargetTarget.hitGlow') is None, "target and target of target have no hit flash")
L.execute('EV.scripts.OnEvent(EV, "UNIT_COMBAT", "target", "WOUND", "", 50, 1); EV.scripts.OnEvent(EV, "UNIT_COMBAT", "player", "DODGE", "", 0, 1); EV.scripts.OnUpdate(EV, 0.001)')
check(G('AetherFramesPlayer') == 0, "a dodge doesn't flash; hits on the target are ignored")
L.execute('EV.scripts.OnEvent(EV, "UNIT_COMBAT", "player", S("WOUND"), S(""), S(77), 1); EV.scripts.OnUpdate(EV, 0.001)')
check(G('AetherFramesPlayer') == 1, "hidden hit details still flash")
check(L.eval('AetherFramesPlayer.hitNumber.alpha') == 0, "numbers off by default")
L.execute('SlashCmdList.AETHERFRAMES("hitnumbers on"); EV.scripts.OnEvent(EV, "UNIT_COMBAT", "player", "WOUND", "CRITICAL", 345, 1); EV.scripts.OnUpdate(EV, 0.001)')
n = L.eval('AetherFramesPlayer.hitNumber')
check(n.text == 345 and n.alpha == 1, "number shows (%s)" % n.text)
L.execute('EV.scripts.OnEvent(EV, "UNIT_COMBAT", "pet", "WOUND", "", S(88), 1); EV.scripts.OnUpdate(EV, 0.001)')
check(L.eval('getmetatable(AetherFramesPet.hitNumber.text) ~= nil'), "a hidden amount is handed to the game to show")
L.execute('NOW = NOW + 0.9; EV.scripts.OnUpdate(EV, 0.9)')
check(L.eval('AetherFramesPlayer.hitNumber.alpha') == 0, "number gone after 0.8 s")
L.execute('SlashCmdList.AETHERFRAMES("hits off"); EV.scripts.OnEvent(EV, "UNIT_COMBAT", "pet", "WOUND", "", 5, 1); EV.scripts.OnUpdate(EV, 0.001)')
check(G('AetherFramesPet') == 0, "/af hits off: no flash")
print("FAILURES:", fails) if fails else print("all good")
sys.exit(1 if fails else 0)
