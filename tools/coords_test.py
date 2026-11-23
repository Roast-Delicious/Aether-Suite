from lupa.lua51 import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
table.unpack = table.unpack or unpack
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
FRAMES = {}
function New(parent) local f = setmetatable({scripts={}, shown=true, kids={}, alpha=1, scale=1, level=1, w=0, h=0, parent=parent}, M); if parent and parent.kids then table.insert(parent.kids, f) end; FRAMES[#FRAMES+1]=f; return f end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.HookScript(s,k,f) local o=s.scripts[k]; s.scripts[k]=function(...) if o then o(...) end f(...) end end
function M.Show(s) s.shown=true end
function M.Hide(s) s.shown=false end
function M.IsShown(s) return s.shown end
function M.IsVisible(s) return s.shown end
function M.SetShown(s,v) s.shown=v end
function M.SetSize(s,w,h) s.w,s.h=w,h end
function M.GetWidth(s) return s.w end
function M.GetHeight(s) return s.h end
function M.SetPoint(s,...) s.point={...} end
function M.ClearAllPoints(s) s.point=nil end
function M.SetAlpha(s,a) s.alpha=a end
function M.SetScale(s,v) s.scale=v end
function M.SetFrameLevel(s,l) s.level=l end
function M.GetFrameLevel(s) return s.level end
function M.GetChildren(s) return unpack(s.kids) end
function M.CreateTexture(s) return New() end
function M.CreateMaskTexture(s) return New() end
function M.CreateAnimationGroup(s) local g = New(); function g:CreateAnimation() return New() end; function g:Play() PULSES = (PULSES or 0) + 1 end; return g end
function M.CreateFontString(s) local fs = New(); function fs:GetStringWidth() return 50 end; function fs:SetText(t) self.text=t end; return fs end
CreateFrame = function(kind, name, parent) local f = New(parent); if name then _G[name] = f end; return f end
UIParent = New()
Minimap = New(); Minimap:SetSize(140,140); function Minimap:GetZoom() return 0 end
IsIndoors = function() return false end
GetCVar = function() return "0" end
GameTooltip = New(); LINES = {}
function GameTooltip:AddLine(t) LINES[#LINES+1]=t end
function GameTooltip:Hide() LINES = {} end
NOW = 100; GetTime = function() return NOW end
PLAYER = { map = 100, x = 0.5, y = 0.5 }
CreateVector2D = function(x,y) return { x=x, y=y, GetXY=function(v) return v.x, v.y end } end
-- zone 100: 2000 yd square; continent 50: 8000 yd square containing it
local function toWorld(m, v) if m == 100 then return 1, CreateVector2D(1000 - v.y*2000, 1000 - v.x*2000) end if m == 50 then return 1, CreateVector2D(4000 - v.y*8000, 4000 - v.x*8000) end end
C_Map = {
  GetBestMapForUnit = function() return PLAYER.map end,
  GetPlayerMapPosition = function(m) if m == 100 then return CreateVector2D(PLAYER.x, PLAYER.y) end end,
  GetWorldPosFromMapPos = toWorld,
  GetMapPosFromWorldPos = function(inst, w, m)
    if m == 50 then return 50, CreateVector2D((4000 - w.y)/8000, (4000 - w.x)/8000) end
    if m == 100 then return 100, CreateVector2D((1000 - w.y)/2000, (1000 - w.x)/2000) end end,
  GetMapInfo = function(m) return ({[100]={name="Thousand Needles", parentMapID=50}, [50]={name="Kalimdor", parentMapID=0}})[m] end,
  GetMapChildrenInfo = function(root) return { {mapID=100, name="Thousand Needles"} } end,
}
WorldMapFrame = New(); WorldMapFrame.ScrollContainer = New(WorldMapFrame); WorldMapFrame.ScrollContainer.Child = New(WorldMapFrame.ScrollContainer)
WorldMapFrame.ScrollContainer.Child:SetSize(1000, 700); SHOWNMAP = 100
function WorldMapFrame:GetMapID() return SHOWNMAP end
function WorldMapFrame.ScrollContainer:IsMouseOver() return true end
CURSOR = {0.3, 0.4}
function WorldMapFrame.ScrollContainer:GetNormalizedCursorPosition() return CURSOR[1], CURSOR[2] end
POPUP = nil
StaticPopup_Show = function(name, text, _, data) POPUP = { name = name, text = text, data = data } end
OUT = {}
GetCursorPosition = function() return 500, 400 end
function M.GetEffectiveScale() return 1 end
print = function(...) local t={} for i=1,select("#",...) do t[#t+1]=tostring(select(i,...)) end OUT[#OUT+1]=table.concat(t," ") end
SlashCmdList = {}
strsplit = function(sep, str) local o={} for p in string.gmatch(str,"([^"..sep.."]+)") do o[#o+1]=p end return unpack(o) end
strlower, strtrim = string.lower, function(s) return (s:gsub("^%s+",""):gsub("%s+$","")) end
format = string.format
wipe = function(t) for k in pairs(t) do t[k]=nil end return t end
''')
L.execute(open('/home/claude/brand/AetherCoords/AetherCoords.lua').read(), 'AetherCoords')
L.execute('''
for _,f in ipairs(FRAMES) do if f.scripts.OnEvent then EV = f end end
EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherCoords"); EV.scripts.OnEvent(EV, "PLAYER_LOGIN")
function Tick() for _,f in ipairs(FRAMES) do if f.scripts.OnUpdate then f.scripts.OnUpdate(f, 1) end end end
function Pins(parent) local o = {} for _,p in ipairs(parent.kids) do if rawget(p,"isAetherPin") and p.shown then
  o[#o+1] = string.format("%s @ %.0f,%.0f%s", p.wp.note ~= "" and p.wp.note or "(no note)", p.point[4], p.point[5], p.alpha < 1 and " (on rim, faded)" or "") end end
  table.sort(o) return table.concat(o, " | ") end
function Out() local s = table.concat(OUT, "\\n"); OUT = {}; return s end
''')
def run(label, code):
    L.execute(code); out = L.eval('Out()')
    print("== " + label); 
    if out: print("   " + out.replace("\n","\n   "))
WM = 'WorldMapFrame.ScrollContainer.Child'
L.execute('WorldMapFrame:Hide()')
run("/way 26 42 Rok'Alim (map closed: your zone)", 'SlashCmdList.AETHERWAY("26 42 Rok\'Alim")')
run("/way 54,41.5 Dorn", 'SlashCmdList.AETHERWAY("54,41.5 Dorn")')
run("/way Thousand Needles 90 90 far camp", 'SlashCmdList.AETHERWAY("Thousand Needles 90 90 far camp")')
run("/way list", 'SlashCmdList.AETHERWAY("list")')
L.execute('WorldMapFrame:Show(); Tick()')
print("== world map (zone):", L.eval(f'Pins({WM})'))
L.execute('SHOWNMAP = 50; Tick()')
print("== world map (continent):", L.eval(f'Pins({WM})'))
L.execute('SHOWNMAP = 100; Tick()')
print("== minimap (you at 50,50):", L.eval('Pins(Minimap)'))
L.execute('local sc = WorldMapFrame.ScrollContainer; sc.scripts.OnMouseUp(sc, "LeftButton"); NOW = NOW + 1; sc.scripts.OnMouseUp(sc, "LeftButton")')
print("== two slow clicks: note box shown =", L.eval('AetherCoordsNoteBox ~= nil and AetherCoordsNoteBox.shown'))
L.execute('local sc = WorldMapFrame.ScrollContainer; NOW = NOW + 5; sc.scripts.OnMouseUp(sc, "LeftButton"); NOW = NOW + 0.2; sc.scripts.OnMouseUp(sc, "LeftButton")')
print("== double-click: note box shown =", L.eval('AetherCoordsNoteBox.shown'), "|", L.eval('AetherCoordsNoteBox.title.text'))
run("type a note and press Enter", 'local b = AetherCoordsNoteBox.box; function b:GetText() return "Herb spot" end; b.scripts.OnEnterPressed(b); Tick()')
print("   note box closed:", not L.eval('AetherCoordsNoteBox.shown'))
print("   world map now:", L.eval(f'Pins({WM})'))
L.execute(f'for _,p in ipairs({WM}.kids) do if rawget(p,"isAetherPin") and p.shown and p.wp.note=="Dorn" then p.scripts.OnEnter(p); DORN = p end end')
print("== hover Dorn pin tooltip:", L.eval('table.concat(LINES, " / ")'))
run("right-click Dorn pin", 'DORN.scripts.OnClick(DORN, "RightButton"); Tick()')
print("   world map now:", L.eval(f'Pins({WM})'))
run("/way remove 1, then /way clear", 'SlashCmdList.AETHERWAY("remove 1"); SlashCmdList.AETHERWAY("clear"); Tick()')
print("   world map now:", repr(L.eval(f'Pins({WM})')), " minimap:", repr(L.eval('Pins(Minimap)')))
