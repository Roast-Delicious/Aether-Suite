from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
exec(open('marks_test.py').read().split("L.execute(open('/home/claude/brand")[0].split("L = LuaRuntime")[1].join(["L = LuaRuntime",""]) if False else "")
pre = open('marks_test.py').read().split("L.execute(open('/home/claude/brand")[0]
exec(pre)
L.execute(open("/mnt/user-data/uploads/54619117#1--SavedVariables/AetherMarks.lua").read())
L.execute(r'''
SM = {}; function S(v) return setmetatable({v=v}, SM) end
issecretvalue = function(v) return getmetatable(v) == SM end
geterrorhandler = function() return function() end end
UnitReaction = function() return 2 end
UnitIsUnit = function() return false end
UnitLevel = function() return 35 end
C_QuestLog = { GetNumQuestLogEntries=function() return 1 end,
  GetInfo=function() return {questID=905, isHeader=false} end,
  GetQuestObjectives=function() return { {text="Unpopped Darkmist Eye: 5/40", type="item", finished=false, numRequired=40} } end }
UIParent = New(); WorldFrame = New(); GetTime = function() return 100 end
PLATES = {}
for i = 1, 5 do
  local p = New(); p.namePlateUnitToken = "nameplate"..i; p.UnitFrame = New(); p.UnitFrame.alpha = 1; p.UnitFrame.healthBar = New(); p.UnitFrame.HealthBarsContainer = false
  function p.UnitFrame:SetAlpha(a) self.alpha = a end
  function p.UnitFrame:GetAlpha() return self.alpha end
  PLATES[i] = p
  UNITS["nameplate"..i] = { guid = "Creature-0-1-2-3-4376-00000"..i, name = "Darkmist Recluse" }
end
UNITS.nameplate3.guid = nil                        -- ID hidden
UNITS.nameplate4.deadSecret = true                 -- "is it dead?" hidden
UNITS.nameplate5.boom = true                       -- something on this plate errors
UnitIsDead = function(u) if UNITS[u] and UNITS[u].deadSecret then return S(false) end return false end
local oldName = UnitName
UnitName = function(u) if UNITS[u] and UNITS[u].boom then error("hidden name") end return oldName(u) end
C_NamePlate = { GetNamePlates=function() return PLATES end, GetNamePlateForUnit=function(u) for _,p in ipairs(PLATES) do if p.namePlateUnitToken==u then return p end end end }
''')
src = open('/home/claude/brand/AetherMarks/AetherMarks.lua').read()
L.execute(src, 'AetherMarks')
L.execute('EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks"); AetherMarksDB.learned["4376"]={["Unpopped Darkmist Eye"]=true}; AetherMarksDB.learned["n:Darkmist Recluse"]={["Unpopped Darkmist Eye"]=true}')
L.execute('EV.scripts.OnEvent(EV, "QUEST_LOG_UPDATE")')   # refresh all plates
def state(i):
    return L.eval('(function(p) return string.format("Blizzard plate %s, our name %s", p.UnitFrame.alpha==0 and "hidden" or "SHOWN", (function() for pl,o in pairs({}) do end return "" end)()) end)')(L.eval('PLATES[%d]'%i))
for i in range(1,6):
    p = L.eval('PLATES[%d]'%i)
    o = L.eval('(function(p) for k,v in pairs(_G) do end return nil end)')
    blizz = "hidden" if p.UnitFrame.alpha == 0 else "SHOWN"
    print("spider", i, ["normal","normal","ID hidden","dead? hidden","errors"][i-1].ljust(13), "Blizzard plate:", blizz)
print("last plate error recorded:", L.eval('(function() local f; return true end)()'))
L.execute('OUT={}; print=function(...) local t={} for i=1,select("#",...) do t[#t+1]=tostring((select(i,...))) end OUT[#OUT+1]=table.concat(t," ") end')
L.execute('for k,f in pairs(SlashCmdList) do DBG=f end; DBG("debug")')
out=L.eval('OUT'); print("\n".join(out[i] for i in range(1,len(out)+1)))
