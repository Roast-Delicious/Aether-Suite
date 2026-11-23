import lupa.lua51 as l
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
OUT={}; print=function(m) OUT[#OUT+1]=tostring(m) end
local function Obj() return setmetatable({shown=false}, {__index=function(t,k)
  if k=="Show" then return function(s) s.shown=true end end
  if k=="Hide" then return function(s) s.shown=false end end
  if k=="IsShown" then return function(s) return s.shown end end
  if k=="SetText" then return function(s,x) s.text=x end end
  if k=="GetStringHeight" then return function() return 30 end end
  if k=="CreateFontString" then return function() return Obj() end end
  return function() end end}) end
FR={}; CreateFrame=function(_, name) local o=Obj(); FR[#FR+1]=o; if name then _G[name]=o end; o.events={}; o.RegisterEvent=function(s,e) s.events[e]=true end; o.SetScript=function(s,n,fn) s[n]=fn end; return o end
UIParent=Obj()
TIMERS={}; C_Timer={After=function(t,fn) TIMERS[#TIMERS+1]=fn end}
function Fire() local t=TIMERS; TIMERS={}; for _,f in ipairs(t) do f() end end
COMBAT=false; InCombatLockdown=function() return COMBAT end
IsInInstance=function() return false end
LEVEL=32
UnitName=function() return "Jay" end; GetRealmName=function() return "" end
UnitClass=function() return "Hunter","HUNTER",3 end; UnitRace=function() return "Troll","Troll",8 end
UnitLevel=function() return LEVEL end; UnitFactionGroup=function() return "Horde" end
GetRealZoneText=function() return "Orgrimmar" end
date=function() return "now" end
strlower=string.lower; strtrim=function(s) return (s:gsub("^%s+",""):gsub("%s+$","")) end
NAMES={[1454]="Orgrimmar",[1443]="Desolace",[1441]="Thousand Needles",[1434]="Stranglethorn Vale",[1424]="Hillsbrad Foothills",[1417]="Arathi Highlands",[1413]="The Barrens",[1445]="Dustwallow Marsh",[1435]="Swamp of Sorrows"}
CURMAP=1454
C_Map={GetMapInfo=function(m) return {name=NAMES[m] or ("Zone"..m), mapType=3, parentMapID=1414} end, GetBestMapForUnit=function() return CURMAP end}
C_QuestLog={}
SlashCmdList={}
''')
# real ledger data -> completed + quest log
L.execute(open("/mnt/user-data/uploads/54619117#1--SavedVariables/AetherLedger.lua").read().replace("AetherLedgerDB","JAY",1))
L.execute(r'''
local c = JAY.characters.Jay
GetQuestsCompleted=function() local t={} for _,q in ipairs(c.completed) do t[q.id]=true end return t end
local log={}
local lastZone
for _,q in ipairs(c.questLog) do
  if q.zone~=lastZone then log[#log+1]={q.zone,nil,nil,true}; lastZone=q.zone end
  log[#log+1]={q.title,q.level,nil,false,nil,q.complete and 1 or nil,nil,q.id}
end
GetNumQuestLogEntries=function() return #log end
GetQuestLogTitle=function(i) return unpack(log[i]) end
GetNumQuestLeaderBoards=function() return 0 end
''')
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Data.lua').read())
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger.lua').read())

L.execute('for _,f in ipairs(FR) do if f.OnEvent then EV=f end end')
def ev(*a):
    L.execute('EV.OnEvent(EV, %s)' % ",".join(repr(x) if isinstance(x,str) else str(x) for x in a))
def out():
    for x in L.eval('OUT').values(): print(x)
    L.execute('OUT={}')
print("events registered:", sorted(L.eval('EV.events').keys()))
ev("PLAYER_LOGIN"); L.execute('Fire(); Fire()')
print("notice after login in Orgrimmar:", L.eval('AetherLedgerNotice and AetherLedgerNotice.shown'), "|", L.eval('AetherLedgerNotice and AetherLedgerNotice.text.text'))
print("----- /ledger zones")
L.execute('SlashCmdList.AETHERLEDGER("zones")'); out()
print("----- zone change again, same level: no repeat")
L.execute('AetherLedgerNotice.shown=false'); ev("ZONE_CHANGED_NEW_AREA"); L.execute('Fire()')
print("shown:", L.eval('AetherLedgerNotice.shown'))
print("----- move to Desolace: nothing better")
L.execute('CURMAP=1443'); ev("ZONE_CHANGED_NEW_AREA"); L.execute('Fire()'); print("shown:", L.eval('AetherLedgerNotice.shown'))
print("----- level up to 33 in Orgrimmar, during combat")
L.execute('CURMAP=1454; COMBAT=true; LEVEL=33'); ev("PLAYER_LEVEL_UP", 33); L.execute('Fire()'); print("shown in combat:", L.eval('AetherLedgerNotice.shown'))
L.execute('COMBAT=false'); ev("PLAYER_REGEN_ENABLED"); L.execute('Fire()'); print("after combat:", L.eval('AetherLedgerNotice.shown'), "|", L.eval('AetherLedgerNotice.text.text'))
print("----- suggest off")
L.execute('AetherLedgerNotice.shown=false; SlashCmdList.AETHERLEDGER("suggest off"); LEVEL=34'); ev("PLAYER_LEVEL_UP",34); L.execute('Fire()'); print("shown:", L.eval('AetherLedgerNotice.shown')); out()
import time
L.execute('LEVEL=32; T0=os.clock(); for i=1,20 do AetherLedger_API.Check() end; T1=os.clock()')
print("check time ms:", round((L.eval('T1')-L.eval('T0'))/20*1000,2))
