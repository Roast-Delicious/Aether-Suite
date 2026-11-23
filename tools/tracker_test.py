import lupa.lua51 as l, sys
MODE = sys.argv[1] if len(sys.argv) > 1 else "classic"
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
OUT={}; print=function(m) OUT[#OUT+1]=tostring(m) end
local function Obj() return setmetatable({shown=false}, {__index=function(t,k)
  if k=="Show" then return function(s) s.shown=true end end
  if k=="Hide" then return function(s) s.shown=false end end
  if k=="IsShown" then return function(s) return s.shown end end
  if k=="SetShown" then return function(s,v) s.shown=v and true or false end end
  if k=="SetText" then return function(s,x) s.text=x end end
  if k=="GetStringHeight" then return function() return 14 end end
  if k=="CreateFontString" or k=="CreateTexture" then return function() return Obj() end end
  return function() end end}) end
FR={}; CreateFrame=function(_, name) local o=Obj(); FR[#FR+1]=o; if name then _G[name]=o end; o.ev={}; o.RegisterEvent=function(s,e) s.ev[e]=true end; o.SetScript=function(s,n,fn) s[n]=fn end; return o end
UIParent=Obj(); UISpecialFrames={}; tinsert=table.insert
TIMERS={}; C_Timer={After=function(t,fn) TIMERS[#TIMERS+1]=fn end}
function Fire() for _=1,3 do local t=TIMERS; TIMERS={}; for _,f in ipairs(t) do f() end end end
COMBAT=false; InCombatLockdown=function() return COMBAT end
NOW=0; GetTime=function() return NOW end
NAMES={[1454]="Orgrimmar",[1443]="Desolace",[1434]="Stranglethorn Vale",[1417]="Arathi Highlands",[1456]="Thunder Bluff",[1458]="Undercity",[1441]="Thousand Needles",[1411]="Durotar",[1414]="Kalimdor",[1415]="Eastern Kingdoms"}
PARENT={[1454]=1414,[1443]=1414,[1456]=1414,[1441]=1414,[1411]=1414,[1434]=1415,[1417]=1415,[1458]=1415}
HERE=1454
C_Map={GetBestMapForUnit=function() return HERE end, GetMapInfo=function(m) if m==1414 or m==1415 then return {name=NAMES[m],mapType=2} end return {name=NAMES[m] or ("Zone"..m), mapType=3, parentMapID=PARENT[m] or 1414} end}
ONTAXI=false; UnitOnTaxi=function() return ONTAXI end
LEVEL=32; UnitLevel=function() return LEVEL end; UnitName=function() return "Jay" end; GetRealmName=function() return "" end
''')
L.execute(open("/mnt/user-data/uploads/54619117#1--SavedVariables/AetherLedger.lua").read().replace("AetherLedgerDB","JAY",1))
L.execute(r'''
LOG={}; local lastZone
for _,q in ipairs(JAY.characters.Jay.questLog) do
  if q.zone~=lastZone then LOG[#LOG+1]={title=q.zone, header=true}; lastZone=q.zone end
  LOG[#LOG+1]={title=q.title, level=q.level, id=q.id, complete=q.complete}
end
WATCH={}   -- ordered list of log indices / ids
local function find(v) for i,x in ipairs(WATCH) do if x==v then return i end end end
''')
if MODE == "classic":
    L.execute(r'''
    GetNumQuestLogEntries=function() return #LOG end
    GetQuestLogTitle=function(i) local q=LOG[i]; return q.title,q.level,nil,q.header,nil,q.complete and 1 or nil,nil,q.id end
    IsQuestWatched=function(i) for _,x in ipairs(WATCH) do if x==i then return true end end return false end
    AddQuestWatch=function(i) WATCH[#WATCH+1]=i end
    RemoveQuestWatch=function(i) for k,x in ipairs(WATCH) do if x==i then table.remove(WATCH,k) end end end
    GetNumQuestWatches=function() return #WATCH end
    GetQuestIndexForWatch=function(n) return WATCH[n] end
    MAX_WATCHABLE_QUESTS = MAXW or 25
    function Shown() local t={} for _,i in ipairs(WATCH) do t[#t+1]="["..LOG[i].level.."] "..LOG[i].title end return t end
    function UserWatch(i, on) if on then AddQuestWatch(i) else RemoveQuestWatch(i) end end
    ''')
else:
    L.execute(r'''
    local function idx(id) for i,q in ipairs(LOG) do if q.id==id then return i end end end
    C_QuestLog={
      GetNumQuestLogEntries=function() return #LOG end,
      GetInfo=function(i) local q=LOG[i]; return {title=q.title, level=q.level, isHeader=q.header, questID=q.id} end,
      GetQuestWatchType=function(id) for _,x in ipairs(WATCH) do if x==id then return 0 end end return nil end,
      IsComplete=function(id) return LOG[idx(id)].complete end,
      AddQuestWatch=function(id) WATCH[#WATCH+1]=id; EV.OnEvent(EV,"QUEST_WATCH_LIST_CHANGED",id,true) end,
      RemoveQuestWatch=function(id) for k,x in ipairs(WATCH) do if x==id then table.remove(WATCH,k) end end; EV.OnEvent(EV,"QUEST_WATCH_LIST_CHANGED",id,false) end,
      GetNumQuestWatches=function() return #WATCH end,
      GetQuestIDForQuestWatchIndex=function(n) return WATCH[n] end,
      GetMaxNumQuestsCanWatch=function() return 25 end,
      SetSelectedQuest=function(id) SEL=id end, SetAbandonQuest=function() end,
      AbandonQuest=function() local i=idx(SEL); ABANDONED=LOG[i].title; table.remove(LOG,i) end,
    }
    function Shown() local t={} for _,id in ipairs(WATCH) do local q=LOG[idx(id)]; t[#t+1]="["..q.level.."] "..q.title end return t end
    function UserWatch(i, on) if on then C_QuestLog.AddQuestWatch(LOG[i].id) else C_QuestLog.RemoveQuestWatch(LOG[i].id) end end
    ''')
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Data.lua').read())
L.execute("""HOOKS={}; hooksecurefunc=function(name, fn) local orig=_G[name]; _G[name]=function(...) local r=orig(...); fn(...); return r end end""")
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Tracker.lua').read())
L.execute('for _,f in ipairs(FR) do if f.ev.QUEST_ACCEPTED then EV=f end end')
# Blizzard had tracked 4 quests in log order (like the screenshot)
if MODE == "classic":
    L.execute('WATCH={}; local n=0; for i,q in ipairs(LOG) do if not q.header and n<4 and q.level>=36 then WATCH[#WATCH+1]=i; n=n+1 end end')
else:
    L.execute('WATCH={}; local n=0; for i,q in ipairs(LOG) do if not q.header and n<4 and q.level>=36 then WATCH[#WATCH+1]=q.id; n=n+1 end end')
def show(label): print(label); [print("   ", x) for x in L.eval('Shown()').values()]
show("== before (Blizzard's order)")
def go(zone, label):
    L.execute('OUT={}; HERE=%d; EV.OnEvent(EV,"ZONE_CHANGED_NEW_AREA"); NOW=NOW+6; Fire()' % zone)
    show(label)
    for x in L.eval('OUT').values(): print("   chat:", x)
L.execute('NOW=0; EV.OnEvent(EV,"PLAYER_LOGIN"); NOW=11; Fire()')
show("== login in Orgrimmar (nothing here -> zone with most of your quests)")
go(1443, "== in Desolace")
go(1434, "== in Stranglethorn (incl. Hunting in Stranglethorn turn-in from the Desolace section)")
go(1417, "== in Arathi (Guile of the Raptor and Call to Arms are red at 32)")
print("== heading somewhere: travel destination Thousand Needles from Orgrimmar")
L.execute('AetherLedger_Travel={DestMap=function() return 1441 end}')
go(1454, "== in Orgrimmar with a trip to Thousand Needles")
L.execute('AetherLedger_Travel=nil')
print("== pin a Desolace quest by hand, then go to Stranglethorn")
L.execute('NOW=NOW+30; QuestLogFrame={IsVisible=function() return true end}; for i,q in ipairs(LOG) do if q.title=="Clam Bait" then UserWatch(i,true) end end; QuestLogFrame=nil')
print("== game auto-adds a red quest (no quest log open): not pinned")
L.execute('NOW=NOW+30; for i,q in ipairs(LOG) do if q.title=="Call to Arms" then UserWatch(i,true) end end; Fire()')
print("   Call to Arms tracked after re-sort:", any("Call to Arms" in x for x in L.eval('Shown()').values()))
go(1434, "== Stranglethorn with Clam Bait pinned")
print("== on a flight: no change until landing")
L.execute('ONTAXI=true')
go(1443, "== flying over Desolace")
L.execute('ONTAXI=false; EV.OnEvent(EV,"PLAYER_CONTROL_GAINED"); Fire()'); show("== landed in Desolace")

print("== /ledger tracker")
L.execute('OUT={}; AetherLedger_Tracker.Explain()')
for x in list(L.eval('OUT').values())[:8]: print("  ", x)
