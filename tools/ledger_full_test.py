import lupa.lua51 as l
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
OUT={}; print=function(m) OUT[#OUT+1]=tostring(m) end
local function Obj() return setmetatable({shown=false, w=20, h=20}, {__index=function(t,k)
  if k=="Show" then return function(s) s.shown=true end end
  if k=="Hide" then return function(s) s.shown=false end end
  if k=="IsShown" then return function(s) return s.shown end end
  if k=="SetShown" then return function(s,v) s.shown=v and true or false end end
  if k=="SetText" then return function(s,x) s.text=x; ALLTEXT=ALLTEXT or {}; ALLTEXT[#ALLTEXT+1]=x end end
  if k=="GetText" then return function(s) return s.text end end
  if k=="GetStringHeight" then return function() return 30 end end
  if k=="SetAlpha" then return function(s,a) s.alpha=a end end
  if k=="GetRight" then return function(s) return s.right or 500 end end
  if k=="GetLeft" then return function(s) return s.left or 100 end end
  if k=="GetTop" then return function(s) return s.top or 700 end end
  if k=="SetPoint" then return function(s,a,b,c,d,e) s.anchor=b; s.pt={a,c,d,e} end end
  if k=="GetVerticalScroll" then return function(s) return s.vs or 0 end end
  if k=="SetVerticalScroll" then return function(s,v) s.vs=v end end
  if k=="SetHeight" then return function(s,v) s.h=v end end
  if k=="SetSize" then return function(s,w,h) s.w=w; s.h=h end end
  if k=="GetValue" then return function(s) return s.val or 0 end end
  if k=="SetValue" then return function(s,v) s.val=v; local f=rawget(s,"OnValueChanged"); if f then f(s,v) end end end
  if k=="HookScript" then return function(s,n,fn) local o=rawget(s,n); s[n]=function(...) if o then o(...) end fn(...) end end end
  if k=="IsEnabled" then return function() return true end end
  if k=="GetChecked" then return function(s) return s.checked end end
  if k=="SetChecked" then return function(s,v) s.checked=v end end
  if k=="SetBackdropBorderColor" then return function(s,r,g,b) s.edge={r,g,b} end end
  if k=="GetStringWidth" then return function() return 100 end end
  if k=="GetFontString" then return function() return Obj() end end
  if k=="GetWidth" then return function(s) return s.w end end
  if k=="GetHeight" then return function(s) return s.h end end
  if k=="CreateFontString" or k=="CreateTexture" or k=="CreateMaskTexture" or k=="CreateAnimationGroup" or k=="CreateAnimation" then return function() return Obj() end end
  if k=="Play" then return function(s) s.playing=true end end
  if k=="Stop" then return function(s) s.playing=false end end
  if type(k)=="string" and k:match("^%u") then return function() end end
  return nil end}) end
FR={}; CreateFrame=function(_, name) local o=Obj(); FR[#FR+1]=o; if name then _G[name]=o end; o.ev={}; o.RegisterEvent=function(s,e) s.ev[e]=true end; o.SetScript=function(s,n,fn) s[n]=fn end; o.GetScript=function(s,n) return rawget(s,n) or function() end end; return o end
UIParent=Obj()
TIMERS={}; C_Timer={After=function(t,fn) TIMERS[#TIMERS+1]=fn end}
function Fire() for _=1,3 do local t=TIMERS; TIMERS={}; for _,f in ipairs(t) do f() end end end
COMBAT=false; InCombatLockdown=function() return COMBAT end
IsInInstance=function() return false end
NOW=0; GetTime=function() return NOW end
LEVEL=32
UnitName=function() return "Jay" end; GetRealmName=function() return "" end
UnitClass=function() return "Hunter","HUNTER",3 end; UnitRace=function() return "Troll","Troll",8 end
UnitLevel=function() return LEVEL end; UnitFactionGroup=function() return "Horde" end
GetRealZoneText=function() return "Orgrimmar" end
date=function() return "now" end
strlower=string.lower; strtrim=function(s) return (s:gsub("^%s+",""):gsub("%s+$","")) end
-- fake world: map -> continent instance, origin and size (yards)
WORLD={[1454]={1,0,0,800},[1411]={1,-1500,-1500,3000},[1443]={1,-9000,6000,5000},[1441]={1,-14000,-2000,5000},
       [1413]={1,-8000,-2000,6000},[1456]={1,-6000,4000,800},[1420]={0,4000,-4000,4000},[1434]={0,-12000,0,6000},[1458]={0,4500,-3000,800}}
NAMES={[1454]="Orgrimmar",[1443]="Desolace",[1441]="Thousand Needles",[1434]="Stranglethorn Vale",[1424]="Hillsbrad Foothills",[1411]="Durotar",[1420]="Tirisfal Glades",[1413]="The Barrens",[1456]="Thunder Bluff",[1458]="Undercity"}
CreateVector2D=function(x,y) return {x=x,y=y,GetXY=function(s) return s.x,s.y end} end
PLAYER={map=1454,x=0.5,y=0.5}
C_Map={GetMapInfo=function(m) return {name=NAMES[m] or ("Zone"..m), mapType=3, parentMapID=(WORLD[m] and WORLD[m][1]==0) and 1415 or 1414} end,
  GetBestMapForUnit=function() return PLAYER.map end,
  GetPlayerMapPosition=function(m) return CreateVector2D(PLAYER.x,PLAYER.y) end,
  GetWorldPosFromMapPos=function(m,v) local w=WORLD[m]; if not w then return nil end
     -- world x = north: map y down = south, map x right = east (world y = west)
     return w[1], {x=w[2]-v.y*w[4], y=w[3]-v.x*w[4]} end}
ONTAXI=false; UnitOnTaxi=function() return ONTAXI end
C_QuestLog={}
SlashCmdList={}
-- skills
SKILLS={{"Professions",true},{"Leatherworking",false,nil,148,nil,nil,150},{"Skinning",false,nil,147,nil,nil,150},{"Secondary Skills",true},{"First Aid",false,nil,225,nil,nil,225}}
GetNumSkillLines=function() return #SKILLS end
GetSkillLineInfo=function(i) return unpack(SKILLS[i]) end
-- pathfinder + coords
AetherPathfinder_API={classes={'HUNTER'}, ClassName=function(t) return 'Hunter' end, SelectedClass=function() return 'HUNTER' end, GetClassChoice=function() return 'AUTO' end, SetClassChoice=function() end, LabelFor=function(k) return k end, HasClassPet=function() return true end, Refresh=function() end,

 FlightMasters=function() return {
   {id=1,name="Doras",map=1454,x=0.45,y=0.64,known=true},
   {id=2,name="Nataka? Shadowprey FM",map=1443,x=0.21,y=0.74,known=true},
   {id=3,name="Tal",map=1456,x=0.47,y=0.50,known=true},
   {id=4,name="Unknown FM",map=1443,x=0.60,y=0.60,known=false},
   {id=5,name="Michael Garrett",map=1458,x=0.63,y=0.48,known=true},
   {id=6,name="Thysta",map=1434,x=0.32,y=0.29,known=true}} end,
 Trainers=function(words,titles)
   local all={{name="Una",sub="Artisan Leatherworker",map=1456,x=0.415,y=0.4257},{name="Thuwd",sub="Skinning Trainer",map=1454,x=0.63,y=0.45},{name="Hahrana Ironhide",sub="Master Leatherworker",map=1444,x=0.74,y=0.43}}
   local r={} for _,t in ipairs(all) do local s=t.sub:lower(); local ok=false
     for _,w in ipairs(words) do if s:find(w,1,true) then ok=true end end
     if ok and titles then ok=false; for _,w in ipairs(titles) do if s:find(w,1,true) then ok=true end end end
     if ok then r[#r+1]=t end end return r end}
WAYPOINTS={}
AetherCoords_API={AddWaypoint=function(m,x,y,n) local w={map=m,x=x,y=y,note=n}; WAYPOINTS[#WAYPOINTS+1]=w; return w end,
  RemoveWaypoint=function(w) for i,x in ipairs(WAYPOINTS) do if x==w then table.remove(WAYPOINTS,i) end end end}
''')
L.execute(open("/mnt/user-data/uploads/54619117#1--SavedVariables/AetherLedger.lua").read().replace("AetherLedgerDB","JAY",1))
L.execute(r'''
local c = JAY.characters.Jay
GetQuestsCompleted=function() local t={} for _,q in ipairs(c.completed) do t[q.id]=true end return t end
local log={}; local lastZone
for _,q in ipairs(c.questLog) do
  if q.zone~=lastZone then log[#log+1]={q.zone,nil,nil,true}; lastZone=q.zone end
  log[#log+1]={q.title,q.level,nil,false,nil,q.complete and 1 or nil,nil,q.id}
end
GetNumQuestLogEntries=function() return #log end
GetQuestLogTitle=function(i) return unpack(log[i]) end
GetNumQuestLeaderBoards=function() return 0 end
''')
L.execute('hooksecurefunc=function() end')
for f in ['AetherHub/AetherHub.lua','AetherLedger/AetherLedger_Data.lua','AetherLedger/AetherLedger.lua','AetherLedger/AetherLedger_Travel.lua','AetherLedger/AetherLedger_Tracker.lua']:
    L.execute(open('/home/claude/brand/'+f).read().replace('local ADDON_NAME = ...','local ADDON_NAME = "AetherHub"'))
L.execute('for _,f in ipairs(FR) do if rawget(f,"ev") and f.ev.ZONE_CHANGED_NEW_AREA and f.ev.SKILL_LINES_CHANGED then EV=f end; if rawget(f,"ev") and f.ev.SKILL_LINES_CHANGED and not f.ev.QUEST_TURNED_IN then HUBEV=f end end')
L.execute('HUBEV.OnEvent(HUBEV,"ADDON_LOADED","AetherHub")')
def out():
    for x in L.eval('OUT').values(): print(x)
    L.execute('OUT={}')
print("== profile"); p=L.eval('AetherHub_Profile.Get()'); print(p.level, p.raceName, p.className, [(x.name,x.rank,x.max) for x in p.professions.values()])
print("== login notice")
L.execute('EV.OnEvent(EV,"PLAYER_LOGIN"); Fire()')
print(L.eval('AetherLedgerNotice.text.text'))
for i in (1,2,3):
    print("  row", i, L.eval('AetherLedgerNotice.rows[%d].shown' % i), L.eval('AetherLedgerNotice.rows[%d].text.text' % i))
print("== report"); print(L.eval('AetherLedger_API.Report()'))
print("== Take me there (from Orgrimmar)")
L.execute('AetherLedgerNotice.rows[1].go.OnClick()')
out(); print("waypoints:", [(w.map, round(w.x,3), round(w.y,3), w.note) for w in L.eval('WAYPOINTS').values()])
print(L.eval('AetherLedgerTravel.title.text')); print(L.eval('AetherLedgerTravel.body.text'))
print("== walk to flight master")
L.execute('PLAYER={map=1454,x=0.45,y=0.64}; AetherLedger_Travel.Update()'); print(L.eval('AetherLedgerTravel.body.text'))
print("== flight map opens")
L.execute('GetTaxiMapID=function() return 1413 end; NODES={{0.1,0.2,"Orgrimmar"},{0.5,0.5,"Shadowprey Village"}}')
# compute taxi node positions in Barrens map coordinates that match FMs
L.execute('''local function inv(map, wx, wy) local w=WORLD[map]; return (w[3]-wy)/w[4], (w[2]-wx)/w[4] end
  local _,p1 = C_Map.GetWorldPosFromMapPos(1454, CreateVector2D(0.45,0.64)); local _,p2 = C_Map.GetWorldPosFromMapPos(1443, CreateVector2D(0.21,0.74))
  local a,b = inv(1413,p1.x,p1.y); NODES[1]={a,b,"Orgrimmar, Durotar"}; a,b = inv(1413,p2.x,p2.y); NODES[2]={a,b,"Shadowprey Village, Desolace"}
  NumTaxiNodes=function() return #NODES end; TaxiNodePosition=function(i) return NODES[i][1],NODES[i][2] end; TaxiNodeName=function(i) return NODES[i][3] end
  TaxiButton2=CreateFrame("Button")''')
L.execute('for _,f in ipairs(FR) do if rawget(f,"ev") and f.ev.TAXIMAP_OPENED then TEV=f end end; TEV.OnEvent(TEV,"TAXIMAP_OPENED"); Fire()')
out(); L.execute('for _,f in ipairs(FR) do if rawget(f,"anchor")==TaxiButton2 then GLOWED=true end end'); print("glow on Shadowprey button:", L.eval('GLOWED'))
print("== in flight, then landing")
L.execute('ONTAXI=true; PLAYER={map=1413,x=0.3,y=0.5}; AetherLedger_Travel.Update()'); print(L.eval('AetherLedgerTravel.body.text').split("\n")[-1])
L.execute('ONTAXI=false; PLAYER={map=1443,x=0.21,y=0.74}; AetherLedger_Travel.Update()'); print(L.eval('AetherLedgerTravel.body.text'))
L.execute('local w=WAYPOINTS[1]; PLAYER={map=w.map,x=w.x,y=w.y+0.001}; AetherLedger_Travel.Update()'); print(L.eval('AetherLedgerTravel.body.text').split("\n")[-1])
L.execute('NOW=20; AetherLedger_Travel.Update()'); print("window after 8s:", L.eval('AetherLedgerTravel.shown'))
print("== from Undercity (other continent)")
L.execute('PLAYER={map=1458,x=0.5,y=0.5}; AetherLedger_API.GoBest()'); print(L.eval('AetherLedgerTravel.body.text'))
L.execute('PLAYER={map=1420,x=0.607,y=0.588}; AetherLedger_Travel.Update()'); print("--at tower:\n"+L.eval('AetherLedgerTravel.body.text'))
L.execute('PLAYER={map=1411,x=0.509,y=0.138}; AetherLedger_Travel.Update()'); print("--landed in Durotar:\n"+L.eval('AetherLedgerTravel.body.text'))
print("== skinning level up 150->151 no repeat; rank-up told once")
L.execute('AetherLedgerNotice.shown=false; EV.OnEvent(EV,"SKILL_LINES_CHANGED"); Fire()'); print("notice again:", L.eval('AetherLedgerNotice.shown'))
L.execute('SKILLS[3]={"Skinning",false,nil,150,nil,nil,225}; HUBEV.OnEvent(HUBEV,"SKILL_LINES_CHANGED"); EV.OnEvent(EV,"SKILL_LINES_CHANGED"); Fire()'); print("after training (150/225):", L.eval('AetherLedgerNotice.shown'))
print(L.eval('AetherLedger_API.Report()').split("Skinning 150")[1] if "Skinning 150" in L.eval('AetherLedger_API.Report()') else L.eval('AetherLedger_API.Report()')[-400:])
print("== interests off")
L.execute('AetherHub_Profile.SetInterest("skinning", false); AetherHub_Profile.SetInterest("classQuests", false); AetherLedger_API.Refresh()')
r=L.eval('AetherLedger_API.Report()'); print("skinning in report:", "Skinning" in r, "| class section:", "Class and profession" in r)
out()
print("== pick option 2 (Thousand Needles) and go")
L.execute('AetherLedger_Travel.Stop(); PLAYER={map=1454,x=0.5,y=0.5}; AetherLedger_API.Select(2); AetherLedger_API.GoOption(2)')
print([w.note for w in L.eval('WAYPOINTS').values()], "|", L.eval('AetherLedgerTravel.title.text'))
print(L.eval('AetherLedger_API.HubReport()')[:300])
print("== hub window")
L.execute('Minimap=CreateFrame("Frame"); Minimap.w=140; GetCursorPosition=function() return 0,0 end; GameTooltip=CreateFrame("Frame"); C_Timer.NewTimer=function(t,fn) TIMERS[#TIMERS+1]=fn; return {Cancel=function() end} end; ReloadUI=function() RELOADED=true end')
L.execute('tinsert=table.insert; UISpecialFrames={}; C_AddOns={IsAddOnLoaded=function(n) return true end, GetAddOnMetadata=function() return "1.0" end}')
L.execute('SlashCmdList.AETHERHUB("me"); SlashCmdList.AETHERHUB("ledger")')
L.execute('HUBTEXTS=ALLTEXT')
for t in L.eval('HUBTEXTS').values():
    if any(k in t for k in ("level 32","Leatherworking","Remind","Suggest","Your character","Go","Check zones","Professions","1. ","2. ","3. ","Pick")): print(" ", t.replace("\n"," | ")[:160])
print("== checkbox edges")
L.execute('EDGES={} for _,f in ipairs(FR) do if rawget(f,"UpdateEdge") then EDGES[#EDGES+1]=(f.checked and "on " or "off ")..table.concat(f.edge,",") end end')
print(sorted(set(L.eval('EDGES').values())))
print("== travel window fading")
L.execute('AetherMeterDB={opacityInCombat=0.7, opacityOutCombat=0.25}; NOW=100; PLAYER={map=1454,x=0.5,y=0.5}; AetherLedger_API.GoOption(1)')
print("just opened:", L.eval('AetherLedgerTravel.alpha'))
L.execute('NOW=111; AetherLedgerTravel.OnUpdate(AetherLedgerTravel, 1)'); print("11s later, idle:", L.eval('AetherLedgerTravel.alpha'))
L.execute('COMBAT=true; NOW=112; AetherLedgerTravel.OnUpdate(AetherLedgerTravel, 1)'); print("in combat:", L.eval('AetherLedgerTravel.alpha'))
L.execute('COMBAT=false; AetherLedgerTravel.OnMouseDown(); '); print("clicked:", L.eval('AetherLedgerTravel.alpha'))
L.execute('NOW=125; AetherLedgerTravel.OnUpdate(AetherLedgerTravel, 1)'); print("idle again:", L.eval('AetherLedgerTravel.alpha'))
L.execute('PLAYER={map=1454,x=0.45,y=0.64}; NOW=126; AetherLedgerTravel.OnUpdate(AetherLedgerTravel, 1)'); print("step done (reached flight master):", L.eval('AetherLedgerTravel.alpha'))
print("== hub has new controls:", "Keep my quest tracker on my zone, sorted by level" in L.eval('ALLTEXT').values(), "Clean up quest log" in L.eval('ALLTEXT').values())

print("== minimap button")
L.execute('HUBEV.OnEvent(HUBEV,"PLAYER_LOGIN")')
print("button exists:", L.eval('AetherHubMinimapButton ~= nil'), "shown:", L.eval('AetherHubMinimapButton and AetherHubMinimapButton.shown'))
L.execute('SlashCmdList.AETHERHUB("minimap")'); print("after /hub minimap:", L.eval('AetherHubMinimapButton.shown'))
L.execute('SlashCmdList.AETHERHUB("minimap")'); print("again:", L.eval('AetherHubMinimapButton.shown'))
L.execute('AetherHubMinimapButton.OnClick(AetherHubMinimapButton,"LeftButton")'); print("left-click toggles hub:", L.eval('AetherHubFrame.shown'))
print("keybinding global:", L.eval('type(AetherHub_Toggle)'), L.eval('BINDING_NAME_AETHERHUB_TOGGLE'))
print("== pages with scroll")
for page in ["Character","AetherMeter","AetherBars","AetherCoords","AetherPathfinder","AetherMarks","AetherItemID","AetherLedger"]:
    L.execute('SlashCmdList.AETHERHUB("%s")' % {"Character":"me","AetherMeter":"meter","AetherBars":"bars","AetherCoords":"coords","AetherPathfinder":"map","AetherMarks":"marks","AetherItemID":"itemid","AetherLedger":"ledger"}[page])
print("tooltips hooked:", L.eval('(function() local n=0 for _,f in ipairs(FR) do if rawget(f,"OnEnter") then n=n+1 end end return n end)()'))
print("reload hint before:", L.eval('AetherHubFrame.reload.text'))
L.execute("""for _,f in ipairs(FR) do local l=rawget(f,"label"); if l and l.text=="Hide the default bar art" then f.checked=false; f.OnClick(f) end end""")
print("reload hint after unchecking bar art:", L.eval('AetherHubFrame.reload.text'))
print("== Check zones now while already in the best zone (Desolace)")
L.execute('PLAYER={map=1443,x=0.5,y=0.5}; AetherLedgerNotice.shown=false; AetherLedger_API.Check()')
print(L.eval('AetherLedgerNotice.text.text'))
for i in (1,2,3): print("  row", i, L.eval('AetherLedgerNotice.rows[%d].shown' % i), L.eval('AetherLedgerNotice.rows[%d].text.text' % i))
print("== Show quests opens AetherHub on the Ledger tab (hub already open)")
L.execute('AetherHubFrame.shown=true; for _,f in ipairs(FR) do if rawget(f,"text")=="Show quests" then f.OnClick(f) end end')
print("hub shown:", L.eval('AetherHubFrame.shown'), "| notice shown:", L.eval('AetherLedgerNotice.shown'))
print("== a new profession quest appears (Leatherworking 225)")
L.execute('SKILLS[2]={"Leatherworking",false,nil,225,nil,nil,300}; HUBEV.OnEvent(HUBEV,"SKILL_LINES_CHANGED"); LEVEL=40; AetherLedgerNotice.shown=false; AetherLedger_API.Check()')
print(L.eval('AetherLedgerNotice.text.text'))
for i in (1,2,3): print("  row", i, L.eval('AetherLedgerNotice.rows[%d].shown' % i), L.eval('AetherLedgerNotice.rows[%d].text.text' % i))
print("== /hub version")
L.execute('OUT={}; SlashCmdList.AETHERHUB("version")')
for x in L.eval('OUT').values(): print("  ", x)
L.execute('SlashCmdList.AETHERHUB("me")')
print([t for t in L.eval('ALLTEXT').values() if isinstance(t,str) and t.startswith("AetherHub  |cff")][-1].replace("\n"," | "))
print([t for t in L.eval('ALLTEXT').values() if isinstance(t,str) and "AETHER HUB" in t][-1])
print("== drag the suggestion window, then it opens there")
L.execute('AetherLedgerNotice.left=900; AetherLedgerNotice.top=420; AetherLedgerNotice.OnDragStop(AetherLedgerNotice)')
print("saved:", list(L.eval('AetherLedgerDB.windowPos.notice').values()))
L.execute('AetherLedgerNotice.shown=false; AetherLedger_API.Check()')
print("opens at:", list(L.eval('AetherLedgerNotice.pt').values()), "shown:", L.eval('AetherLedgerNotice.shown'))
L.execute('SlashCmdList.AETHERLEDGER("resetwindows"); AetherLedger_API.Check()')
print("after reset:", list(L.eval('AetherLedgerNotice.pt').values()))
print("== click the quest giver: You're there, waypoint removed, fade, close")
L.execute('AetherLedger_Travel.Stop(); NOW=500; PLAYER={map=1454,x=0.5,y=0.5}; AetherLedger_API.GoOption(1)')
print("waypoints before:", [w.note for w in L.eval('WAYPOINTS').values()])
dest = L.eval('AetherLedgerTravel.title.text'); print(dest)
L.execute('local n = AetherLedgerTravel.title.text:match("^To (.-) %("); UnitName=function(u) if u=="target" then return n end return "Jay" end')
L.execute('for _,f in ipairs(FR) do if rawget(f,"ev") and f.ev.PLAYER_TARGET_CHANGED then f.OnEvent(f,"PLAYER_TARGET_CHANGED") end end')
print("flash:", L.eval('AetherLedgerFlash.title.text'), "/", L.eval('AetherLedgerFlash.sub.text'), "| waypoints after:", len(L.eval('WAYPOINTS')), "| directions window shown:", L.eval('AetherLedgerTravel.shown'))
for t in (0.1, 1, 2.5, 3.0, 3.3):
    L.execute('NOW=%s; AetherLedgerFlash.OnUpdate(AetherLedgerFlash, 0.1)' % (500+t))
    print("  flash %.1fs: alpha %.2f shown %s" % (t, L.eval('AetherLedgerFlash.alpha') or 0, L.eval('AetherLedgerFlash.shown')))
