exec(open('frames_aura_test.py').read().split("def icons")[0])
P=L.eval('AetherFramesPlayer'); T=L.eval('AetherFramesTarget')
print("capsule height: you", P.capBottom-P.capTop, "| target", T.capBottom-T.capTop, "| frame heights", P.h, T.h)
# GetUnitAuras path, secret in combat
L.execute(r'''
C_UnitAuras.GetUnitAuras=function(u,f,max) local t={} for i,d in ipairs(AURAS[u] and AURAS[u][f] or {}) do t[i]=d end return t end
AURAS.player.HELPFUL={ {name="Aspect of the Hawk", icon="Hawk", applications=0, duration=0, expirationTime=0, auraInstanceID=1},
  {name=S("Quick Shots"), icon=S("QS"), applications=S(0), duration=S(12), expirationTime=S(1012), auraInstanceID=2} }
AURAS.target.HARMFUL={ {name="Serpent Sting", icon="SS", applications=0, duration=15, expirationTime=1009, auraInstanceID=3} }
EV.scripts.OnEvent(EV,"UNIT_AURA","player"); EV.scripts.OnEvent(EV,"UNIT_AURA","target")
EV.scripts.OnUpdate(EV,0.2)
OUT={}; print=function(s) OUT[#OUT+1]=s end
SlashCmdList.AETHERFRAMES("auras")
''')
out=L.eval('OUT'); print("\n".join(str(out[i]) for i in range(1,len(out)+1)))
print("errors:", L.eval('#ERRS'))
