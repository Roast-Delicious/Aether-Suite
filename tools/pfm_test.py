import lupa, sys, math
from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
unpack = table.unpack; loadstring = load
wipe = function(t) for k in pairs(t) do t[k]=nil end return t end
issecretvalue = function() return false end
frames = {}
local Tex = {}
Tex.__index = function(t,k) return Tex[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function Tex.SetColorTexture(self,r,g,b,a) self.color={r,g,b,a} end
function Tex.AddMaskTexture(self,m) self.mask=m end
MISSING = {}
function Tex.SetTexture(self,p) if MISSING[p] then return false end self.path=p; return true end
function Tex.SetTexCoord(self,...) self.coords={...} end
function Tex.SetShown(self,v) self.shown=v end
local F = {}
F.__index = function(t,k) return F[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function NewFrame(kind, name, parent)
  local f = setmetatable({scripts={}, events={}, shown=true, w=0,h=0, level=1, parent=parent, kids={}}, F)
  if parent and parent.kids then table.insert(parent.kids, f) end
  frames[#frames+1]=f; if name then _G[name]=f end
  return f
end
function F.SetScript(s,k,fn) s.scripts[k]=fn end
function F.HookScript(s,k,fn) local o=s.scripts[k]; s.scripts[k]=function(...) if o then o(...) end fn(...) end end
function F.GetScript(s,k) return s.scripts[k] end
function F.RegisterEvent(s,e) s.events[e]=true end
function F.SetSize(s,w,h) s.w,s.h=w,h end
function F.GetWidth(s) return s.w end
function F.GetHeight(s) return s.h end
function F.Show(s) s.shown=true end
function F.Hide(s) s.shown=false end
function F.IsShown(s) return s.shown end
function F.IsVisible(s) return s.shown end
function F.SetAlpha(s,a) s.alpha=a end
function F.SetFrameLevel(s,l) s.level=l end
function F.GetFrameLevel(s) return s.level end
function F.GetChildren(s) return unpack(s.kids) end
function F.SetPoint(s,...) s.point={...} end
function F.ClearAllPoints(s) s.point=nil end
function F.CreateTexture(s) return setmetatable({},Tex) end
function F.CreateMaskTexture(s) return setmetatable({mask=true},Tex) end
CreateFrame = NewFrame
Minimap = NewFrame("Frame"); Minimap:SetSize(140,140); Minimap.zoom=0
function Minimap:GetZoom() return self.zoom end
IsIndoors = function() return false end
CVARS = { rotateMinimap = "0" }
GetCVar = function(k) return CVARS[k] end
FACING = 0
GetPlayerFacing = function() return FACING end
InCombatLockdown = function() return false end
UnitFactionGroup = function() return "Horde" end
UnitClass = function() return "Hunter","HUNTER" end
CLASS_ICON_TCOORDS = { HUNTER = {0,0.25,0.25,0.5} }
GameTooltip = NewFrame("GameTooltip")
C_Timer = { After = function() end }
-- one test map 100: 2000 x 2000 yards, world x = north, y = west
PLAYER = { map = 100, x = 0.5, y = 0.5 }
CreateVector2D = function(x,y) return { x=x, y=y, GetXY=function(v) return v.x, v.y end } end
C_Map = {
  GetBestMapForUnit = function() return PLAYER.map end,
  GetPlayerMapPosition = function(m) return CreateVector2D(PLAYER.x, PLAYER.y) end,
  GetWorldPosFromMapPos = function(m, v)
    if m ~= 100 then return 9, CreateVector2D(0,0) end
    return 1, CreateVector2D(1000 - v.y*2000, 1000 - v.x*2000)
  end,
}
SlashCmdList = {}
UnitName = function() return "Tester" end
GetRealmName = function() return "Forever" end
strsplit = function(sep, str) local o={} for p in string.gmatch(str,"([^"..sep.."]+)") do o[#o+1]=p end return table.unpack(o) end
UnitExists = function() return true end
UnitIsPlayer = function() return false end
NPC_GUID = nil
UnitGUID = function() return NPC_GUID end
TAXI = {}
C_TaxiMap = { GetAllTaxiNodes = function(m) return TAXI[m] or {} end }
function Tex.CreateAnimationGroup(tex)
  local g = {playing=false}
  function g:SetLooping(m) self.loop=m end
  function g:CreateAnimation() return setmetatable({}, {__index=function() return function() end end}) end
  function g:Play() self.playing=true end
  function g:Stop() self.playing=false end
  tex.group = g; return g
end
print = function(...) end
''')
d = '/home/claude/brand/AetherPathfinder/'
L.execute("AetherPathfinder_Seed = nil")
L.execute(open(d+'AetherPathfinder_Raw.lua').read())
L.execute(open(d+'AetherPathfinder_Build.lua').read())
# Replace seed with a controlled set on map 100
L.execute('''AetherPathfinder_Seed = { [100] = {
 {1,"North Guy","Stable Master",8192,2,0.5,0.45},    -- 100 yd north
 {2,"East Guy","Flight Master",8,2,0.55,0.5},        -- 100 yd east
 {3,"Far Guy","Stable Master",8192,2,0.9,0.5},       -- 800 yd east (off minimap)
 {4,"Alliance Guy","Stable Master",8192,1,0.5,0.52}, -- other faction
 {5,"Hunt Trainer","Hunter Trainer",16,2,0.5,0.55},
 {6,"Skin Trainer","Skinning Trainer",16,2,0.48,0.5},
 {7,"Pet Guy","Pet Trainer",16,2,0.52,0.52},
 {8,"Mail",nil,0,2,0.5,0.5},
}}''')
L.execute(open(d+'AetherPathfinder.lua').read(), 'AetherPathfinder')
L.execute('''for _,f in ipairs(frames) do if f.events.ADDON_LOADED and f.scripts.OnEvent then f.scripts.OnEvent(f,"ADDON_LOADED","AetherPathfinder"); f.scripts.OnEvent(f,"PLAYER_LOGIN") end end''')
L.execute('''
function tick(dt) for _,f in ipairs(frames) do local u=f.scripts.OnUpdate; if u and rawget(f,"parent")==nil and f~=Minimap then u(f, dt or 0.02) end end end
function shownPins()
  local out = {}
  for _,p in ipairs(Minimap.kids) do if p.isAetherPin and p.shown then out[#out+1]=string.format("%s@%.1f,%.1f", p.npc.name, p.point[4], p.point[5]) end end
  table.sort(out); return table.concat(out," ")
end''')
def run(label):
    L.execute('tick(2)'); print(label.ljust(40), L.eval('shownPins()'))
run("zoom 0 (466yd), facing north")
L.execute('Minimap.zoom=5'); run("zoom 5 (133yd)")
L.execute('Minimap.zoom=0; CVARS.rotateMinimap="1"; FACING=math.pi/2'); run("rotating, facing west")
L.execute('FACING=math.pi'); run("rotating, facing south")
L.execute('CVARS.rotateMinimap="0"; AetherPathfinderDB.filters.flight=false; AetherPathfinder_API.Refresh()'); run("flight filter off")
L.execute('AetherPathfinderDB.filters.flight=true; AetherPathfinderDB.minimap=false'); run("minimap option off")
L.execute('AetherPathfinderDB.minimap=true; PLAYER.x=0.85'); run("walk east to x=0.85")
L.execute('PLAYER.map=200'); run("other continent")
# pin looks
print("mask on dot:", L.eval('Minimap.kids[1].dot.mask ~= nil'), "size:", L.eval('Minimap.kids[1].w'))
# globals leak check
print("leaked globals:", [k for k in ['rebuildIn','nearby','miniPins','MakePin','Round','pinsDirty','db'] if L.eval(f'rawget(_G,"{k}")') is not None])

L.execute('PLAYER.map=100; PLAYER.x=0.5; AetherPathfinderDB.filters.prof=true; AetherPathfinder_API.Refresh(); tick(2)')
L.execute("""ICONS={} for _,p in ipairs(Minimap.kids) do if p.isAetherPin and p.shown then ICONS[#ICONS+1]=p.npc.name.." -> "..tostring(p.icon.shown and p.icon.path or "DOT").." ring="..table.concat(p.border.color,",",1,3) end end""")
for x in sorted(L.eval('ICONS').values()): print("  ", x)
L.execute("MISSING[ [[Interface\\Minimap\\Tracking\\StableMaster]] ]=true; for _,p in ipairs(Minimap.kids) do p.iconKey=nil end; AetherPathfinder_API.Refresh(); tick(2)")
L.execute("""ICONS={} for _,p in ipairs(Minimap.kids) do if p.isAetherPin and p.shown and p.npc.name=="North Guy" then ICONS[1]=tostring(p.icon.shown).." dot="..table.concat(p.dot.color,",",1,3) end end""")
print("missing stable icon ->", L.eval('ICONS[1]'))
