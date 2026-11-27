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

# Nov 27: zone list stuck on the same three zones. It was worked out only
# for the popup; with suggestions off it never refreshed.
L.execute(r"""
GetQuestsCompleted=function() return {} end
GetNumQuestLogEntries=function() return 0 end
GetQuestLogTitle=function() return nil end
GetNumQuestLeaderBoards=function() return 0 end
hooksecurefunc=function() end
AetherLedgerDB = { suggest = false }
""")
for f in ['AetherLedger/AetherLedger_Data.lua','AetherLedger/AetherLedger.lua']:
    L.execute(open('/home/claude/brand/'+f).read())
L.execute('for _,f in ipairs(FR) do if rawget(f,"ev") and f.ev.ZONE_CHANGED_NEW_AREA and f.ev.SKILL_LINES_CHANGED then EV=f end end')
ok = True
def expect(name, got, want):
    global ok
    good = got == want
    ok = ok and good
    print(("ok   " if good else "FAIL ") + name + ("" if good else "  got %r want %r" % (got, want)))
L.execute('EV.OnEvent(EV, "PLAYER_LOGIN"); Fire()')
expect("suggestions off: the zone list is still worked out at login", L.eval('AetherLedger_API.Report(true):match("^Level (%d+)")'), "32")
L.execute('LEVEL = 40; EV.OnEvent(EV, "PLAYER_LEVEL_UP", 40); Fire()')
expect("level-up with suggestions off: list follows the new level", L.eval('AetherLedger_API.Report(true):match("^Level (%d+)")'), "40")
L.execute('LEVEL = 41')
L.execute('OPTS = AetherLedger_API.Options()')
expect("Hub opened after a level-up the events missed: rechecked", L.eval('AetherLedger_API.Report(true):match("^Level (%d+)")'), "41")
L.execute('PLAYER.map = 1443')
L.execute('OPTS = AetherLedger_API.Options()')
expect("Hub opened in a new zone: rechecked for that zone", L.eval('AetherLedger_API.Report(true):match("^Level %d+ in ([^:]+)")'), "Desolace")
expect("no popup while suggestions are off", L.eval('(function() for _, t in ipairs(ALLTEXT or {}) do if tostring(t):find("Pick a zone") then return true end end return false end)()'), False)
print("ALL OK" if ok else "FAILED")
