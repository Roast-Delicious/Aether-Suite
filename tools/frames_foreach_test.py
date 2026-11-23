exec(open('frames_aura_test.py').read().split("def icons")[0])
L.execute(r'''
C_UnitAuras.GetUnitAuras=function(u,f) if u=="player" and f=="HELPFUL" then return { {name="Passive Regeneration", icon="Regen", duration=0, expirationTime=0, auraInstanceID=99} } end return {} end
BLIZZ = { player={ HELPFUL={ {name="Aspect of the Hawk", icon="Hawk", applications=0, duration=0, expirationTime=0, auraInstanceID=1},
                             {name="Quick Shots", icon=S("QS"), applications=S(0), duration=S(12), expirationTime=S(1012), auraInstanceID=2} }, HARMFUL={} },
          target={ HELPFUL={}, HARMFUL={ {name="Serpent Sting", icon="SS", applications=0, duration=15, expirationTime=1009, auraInstanceID=3} } } }
AuraUtil = { ForEachAura=function(u,f,n,fn,packed) for _,d in ipairs(BLIZZ[u] and BLIZZ[u][f] or {}) do if fn(d) then return end end end }
EV.scripts.OnEvent(EV,"UNIT_AURA","player"); EV.scripts.OnEvent(EV,"UNIT_AURA","target"); EV.scripts.OnUpdate(EV,0.2)
''')
def names(row):
    return L.eval('''(function(r) local t={} for _,c in ipairs(r.children) do if c.shown and c.icon then t[#t+1]=(type(c.icon.tex)=="table" and "QS(hidden)" or tostring(c.icon.tex)).."/"..tostring(c.timerWay) end end return table.concat(t,"  ") end)''')(row)
print("you:   ", names(L.eval('AetherFramesBuffs')))
print("target:", names(L.eval('AetherFramesTargetAuras')))
print("errors:", L.eval('#ERRS'))
