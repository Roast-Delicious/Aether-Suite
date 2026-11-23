exec(open('frames_test.py').read().split("for name in [")[0])
L.execute(r'''
SM = { __lt=function() error("compared a secret") end, __le=function() error("compared a secret") end,
       __eq=function() error("compared a secret") end, __add=function() error("math on a secret") end,
       __sub=function() error("math on a secret") end, __concat=function() error("joined a secret") end }
function S(v) return setmetatable({v=v}, SM) end
issecretvalue=function(v) return getmetatable(v)==SM end
AURAS = { player={HELPFUL={}, HARMFUL={}}, target={HELPFUL={}, HARMFUL={}} }
C_UnitAuras = {
  GetAuraDataByIndex=function(u,i,f) return AURAS[u] and AURAS[u][f or "HELPFUL"][i] end,
  GetAuraApplicationDisplayCount=function(u,id,mn,mx) return S("stack") end,
  GetAuraDuration=function(u,id) if id==nil then error("bad id") end return {durationObject=id} end,
}
AetherFramesPlayer.shown=true; AetherFramesTarget.shown=true; AetherFramesDB.myBuffs=true
ERRS={}; geterrorhandler=function() return function(e) ERRS[#ERRS+1]=e end end
''')
def icons(row):
    return L.eval('''(function(r) local t={} for _,c in ipairs(r.children) do if c.shown and c.icon then
      t[#t+1]=string.format("%s[%s edge=%s timer='%s' countdown=%s]", tostring(c.icon.tex and (type(c.icon.tex)=="table" and "secret-icon" or c.icon.tex)), c.harmful and "debuff" or "buff",
        c.edge.color and (c.edge.color[1]>0.5 and "red" or "blue") or "?", c.timer.text or "", tostring(c.cd and c.cd.shown)) end end
      return table.concat(t,"  ") end)''')(row)
def step(label, code):
    L.execute(code)
    L.execute('EV.scripts.OnUpdate(EV, 0.2)')   # timer tick
    print(label); print("   you:   ", icons(L.eval('AetherFramesBuffs')) or "(none)")
    print("   target:", icons(L.eval('AetherFramesTargetAuras')) or "(none)", "| row shown:", L.eval('AetherFramesTargetAuras.shown'))
step("1) out of combat, Aspect of the Hawk (no duration):", '''
AURAS.player.HELPFUL = { {icon="Hawk", applications=0, duration=0, expirationTime=0, auraInstanceID=11} }
EV.scripts.OnEvent(EV,"UNIT_AURA","player")''')
step("2) in combat: Quick Shots procs (all numbers secret) + a debuff on you:", '''
AURAS.player.HELPFUL = { {icon=S("Hawk"), applications=S(0), duration=S(0), expirationTime=S(0), auraInstanceID=11},
                         {icon=S("QuickShots"), applications=S(0), duration=S(12), expirationTime=S(1012), auraInstanceID=12} }
AURAS.player.HARMFUL = { {icon=S("Poison"), applications=S(2), duration=S(15), expirationTime=S(1015), auraInstanceID=13} }
EV.scripts.OnEvent(EV,"UNIT_AURA","player")''')
step("3) your Serpent Sting and Hunter's Mark land on the target (secret):", '''
AURAS.target.HARMFUL = { {icon=S("SerpentSting"), applications=S(0), duration=S(15), expirationTime=S(1015), auraInstanceID=21},
                         {icon=S("HuntersMark"), applications=S(0), duration=S(120), expirationTime=S(1120), auraInstanceID=22} }
EV.scripts.OnEvent(EV,"UNIT_AURA","target")''')
step("4) Quick Shots ends, out of combat again (readable numbers):", '''
AURAS.player.HELPFUL = { {icon="Hawk", applications=0, duration=0, expirationTime=0, auraInstanceID=11} }
AURAS.player.HARMFUL = { {icon="Poison", applications=2, duration=15, expirationTime=1010, auraInstanceID=13} }
EV.scripts.OnEvent(EV,"UNIT_AURA","player")''')
step("5) target cleared:", '''UNITS.target=nil; AetherFramesTarget.shown=false; EV.scripts.OnEvent(EV,"PLAYER_TARGET_CHANGED")''')
step("6) 12 buffs + 3 debuffs on you (debuffs keep their room):", '''
AURAS.player.HELPFUL={}; for i=1,12 do AURAS.player.HELPFUL[i]={icon="B"..i, applications=0, duration=0, expirationTime=0, auraInstanceID=100+i} end
AURAS.player.HARMFUL={}; for i=1,3 do AURAS.player.HARMFUL[i]={icon="D"..i, applications=0, duration=0, expirationTime=0, auraInstanceID=200+i} end
EV.scripts.OnEvent(EV,"UNIT_AURA","player")''')
print("errors:", L.eval('#ERRS'))
print("target row anchor:", list(L.eval('AetherFramesTargetAuras.pts[1]').values())[:1], "x", L.eval('AetherFramesTargetAuras.pts[1][4]'), "| target w", L.eval('AetherFramesTarget.w'), "cx", L.eval('AetherFramesTarget.cx'))
