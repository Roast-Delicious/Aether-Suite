exec(open('frames_test.py').read().split("for name in [")[0])
L.execute('''
OUT={}; print=function(s) OUT[#OUT+1]=s end
SlashCmdList.AETHERFRAMES("alpha 0.3"); SlashCmdList.AETHERFRAMES("faces on")
local f=AetherFramesPlayer; f.shown=true; EV.scripts.OnUpdate(EV,0.2)
A1=f.face.alpha
SlashCmdList.AETHERFRAMES("unlock")
EV.scripts.OnUpdate(EV,0.2); A2=f.curAlpha
SlashCmdList.AETHERFRAMES("lock")
EV.scripts.OnUpdate(EV,0.2); A3=f.curAlpha
issecretvalue=function(v) return type(v)=="number" end
UnitHealthPercent=function(u) return 87 end
f.scripts.OnShow(f)
''')
f=L.eval('AetherFramesPlayer')
print("faces fade:", L.eval('A1'), "| unlocked alpha:", L.eval('A2'), "| locked alpha:", L.eval('A3'))
holder_texts=L.eval('''(function() local t={} for _,o in ipairs(ALL) do if o.kind=="FontString" and o.text and o.parent and o.parent.kind=="Frame" and o.parent.parent==AetherFramesPlayer then t[#t+1]=tostring(o.text) end end return table.concat(t," | ") end)()''')
print("bar texts with secret numbers:", holder_texts)
print("chat:", [L.eval('OUT')[i] for i in range(1,len(L.eval('OUT'))+1)][:4])
L.execute('''
SlashCmdList.AETHERFRAMES("unlock")
local n=0; for _,o in ipairs(ALL) do if o.kind=="Button" and o.scripts.OnClick and o.parent and o.parent.kind=="Frame" and o.parent.scripts.OnDragStart then n=n+1; DONE=o end end
MOVERS=n
DONE.scripts.OnClick(DONE)
LOCKED=AetherFramesDB.locked; PETW=AetherFramesPet.watched
CurveConstants={ScaleTo100={}}; UnitHealthPercent=function(u,p,c) return c and 87 or 0.87 end
issecretvalue=function(v) return type(v)=="number" end
AetherFramesPlayer.scripts.OnShow(AetherFramesPlayer)
''')
print("Done buttons:", L.eval('MOVERS'), "| after Done locked:", L.eval('LOCKED'), "pet watched again:", L.eval('PETW'))
print("bar texts with curve:", L.eval('''(function() local t={} for _,o in ipairs(ALL) do if o.kind=="FontString" and o.text and o.parent and o.parent.kind=="Frame" and o.parent.parent==AetherFramesPlayer then t[#t+1]=tostring(o.text) end end return table.concat(t," | ") end)()'''))
