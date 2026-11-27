import lupa.lua51 as l, sys
MODE = "modern"
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

# Nov 27 (new Alliance hunter): new quests vanished from the tracker.
# 1) a quest we can't place (no zone data, header not a zone) is shown
# 2) a quest you just accepted stays even if it belongs to another zone
L.execute(r"""
NAMES[1429]="Elwynn Forest"; NAMES[1436]="Westfall"; PARENT[1429]=1415; PARENT[1436]=1415
LEVEL=8; HERE=1429
LOG={
 {title="Elwynn Forest", header=true},
 {title="Wolves Across the Border", level=6, id=33},
 {title="Riverpaw Gnoll Bounty", level=10, id=11},
 {title="Somewhere New", header=true},
 {title="A Forever Quest", level=8, id=990001},
 {title="Westfall", header=true},
 {title="The Forgotten Heirloom", level=9, id=64},
}
WATCH={}
local function find(v) for i,x in ipairs(WATCH) do if x==v then return i end end end
AetherLedger_Zones = AetherLedger_Zones or {}
AetherLedger_Zones[33]={1429,1429}; AetherLedger_Zones[11]={1429,1429}; AetherLedger_Zones[64]={1436,1436}
AetherLedger_Zones[990001]=nil
""")
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
L.execute("""AetherLedger_Zones[33]={1429,1429}; AetherLedger_Zones[11]={1429,1429}; AetherLedger_Zones[64]={1436,1436}; AetherLedger_Zones[990001]=nil""")
L.execute("""HOOKS={}; hooksecurefunc=function(name, fn) local orig=_G[name]; _G[name]=function(...) local r=orig(...); fn(...); return r end end""")
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Tracker.lua').read())
L.execute('for _,f in ipairs(FR) do if f.ev.QUEST_ACCEPTED then EV=f end end')
ok=True
def expect(name, got, want):
    global ok
    g = got == want; ok = ok and g
    print(("ok   " if g else "FAIL ") + name + ("" if g else "  got %r want %r" % (got, want)))
def shown(): return list(L.eval('Shown()').values())
L.execute('NOW=0; EV.OnEvent(EV,"PLAYER_LOGIN"); NOW=11; Fire()')
s = shown()
expect("Elwynn quests on the tracker in Elwynn", "[6] Wolves Across the Border" in s and "[10] Riverpaw Gnoll Bounty" in s, True)
expect("a quest we can't place is shown, not hidden", "[8] A Forever Quest" in s, True)
expect("a Westfall quest is left off while in Elwynn", "[9] The Forgotten Heirloom" in s, False)
# accept a new Westfall quest: the game tracks it, we keep it
L.execute('table.insert(LOG, {title="Westfall Stew", level=8, id=36}); AetherLedger_Zones[36]={1436,1436}; NOW=NOW+10; EV.OnEvent(EV,"QUEST_ACCEPTED",36); C_QuestLog.AddQuestWatch(36); NOW=NOW+10; Fire()')
expect("a quest you just took stays on the tracker (another zone)", "[8] Westfall Stew" in shown(), True)
L.execute('NOW=NOW+10; EV.OnEvent(EV,"ZONE_CHANGED_NEW_AREA"); Fire()')
expect("...and stays after the next sort", "[8] Westfall Stew" in shown(), True)
# a red quest you just took still goes
L.execute('table.insert(LOG, {title="Too Hard", level=16, id=37}); AetherLedger_Zones[37]={1429,1429}; NOW=NOW+10; EV.OnEvent(EV,"QUEST_ACCEPTED",37); C_QuestLog.AddQuestWatch(37); NOW=NOW+10; Fire()')
expect("a red quest you just took still leaves", "[16] Too Hard" in shown(), False)
# reload: the tracker is sorted while the loading screen is up, not 1.5 s later
L.execute('WATCH={}; TIMERS={}; NOW=100; EV.OnEvent(EV,"PLAYER_LOGIN"); EV.OnEvent(EV,"PLAYER_ENTERING_WORLD")')
expect("reload: sorted at PLAYER_ENTERING_WORLD, before any timer runs", "[6] Wolves Across the Border" in shown(), True)
print("ALL OK" if ok else "FAILED")
