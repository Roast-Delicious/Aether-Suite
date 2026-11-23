from lupa.lua51 import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New(parent) local f = setmetatable({scripts={}, shown=true, alpha=1, scale=1, color={1,0.82,0}, parent=parent}, M); return f end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.HookScript(s,k,f) local o=s.scripts[k]; s.scripts[k]=function(...) if o then o(...) end f(...) end end
function M.SetTextColor(s,r,g,b) s.color={r,g,b} end
function M.GetTextColor(s) return s.color[1], s.color[2], s.color[3] end
function M.SetAlpha(s,a) s.alpha=a end
function M.SetScale(s,v) s.scale=v end
function M.SetText(s,t) s.text=t end
function M.Show(s) s.shown=true end
function M.Hide(s) s.shown=false end
function M.CreateFontString(s) return New(s) end
function M.CreateTexture(s) return New(s) end
function M.GetFont() return "F", 10 end
function M.SetFont(s, f, size) s.fontSize = size end
function M.GetAlpha(s) return s.alpha end
function M.IsObjectType(s, t) return s.kind == t end
function M.GetRegions(s) return unpack(s.regions or {}) end
function M.GetChildren(s) return unpack(s.children or {}) end
function M.SetHeight(s, h) s.h = h end
function M.GetScale(s) return s.scale end
function M.GetWidth(s) return s.w end
function M.SetWidth(s, w) s.w = w end
function M.GetCenter(s) error("Action[FrameMeasurement] failed because[Can't measure restricted regions]") end
function M.ClearAllPoints(s) s.points = {} end
function M.SetPoint(s, ...) s.points = s.points or {}; table.insert(s.points, {...}) end
function M.GetNumPoints(s) return #(s.points or {}) end
function M.GetPoint(s, i) return unpack(s.points[i]) end
function M.GetHeight(s) return s.h end
OVERLAYS = {}
CreateFrame = function(kind, name, parent) local f = New(parent); EV = EV or f; if parent and parent.isPlate then OVERLAYS[parent] = f end; return f end
hooksecurefunc = function(obj, name, fn) local o=obj[name]; obj[name]=function(...) local r={o(...)}; fn(...); return unpack(r) end end
Enum = { TooltipDataType = { Unit = 2 }, TooltipDataLineType = { QuestObjective = 8 } }
TooltipDataProcessor = { AddTooltipPostCall = function() end }
GameTooltip = New()
UNITS = {}
UnitExists = function(u) return UNITS[u] ~= nil end
UnitCanAttack = function(_, u) return UNITS[u] and (UNITS[u].reaction or 2) <= 4 end
UnitIsPlayer = function() return false end
UnitIsDead = function() return false end
UnitGUID = function(u) return UNITS[u] and UNITS[u].guid end
UnitName = function(u) return UNITS[u] and UNITS[u].name end
UnitReaction = function(u) return UNITS[u] and UNITS[u].reaction or 2 end
UnitIsUnit = function(a, b) return UNITS[a] ~= nil and UNITS[b] ~= nil and UNITS[a].guid == UNITS[b].guid end
UnitClassification = function(u) return UNITS[u] and UNITS[u].class or "normal" end
C_TooltipInfo = { GetUnit = function(u) local x = UNITS[u]; return { lines = { {leftText=x.name}, x.quest and {leftText=x.quest, type=8} or {leftText="Level 30"} } } end }
C_Timer = { After = function(t, fn) fn() end }
PLATES = {}
C_NamePlate = { GetNamePlates = function() local o={} for _,p in pairs(PLATES) do o[#o+1]=p end return o end,
  GetNamePlateForUnit = function(u) return PLATES[u] end }
PlaySound = function() end
CVARS = { nameplateMinScale = "0.8", nameplateMaxScale = "1", nameplateMinScaleDistance = "10", nameplateMaxScaleDistance = "10", nameplateShowEnemies = "1" }
GetCVar = function(n) return CVARS[n] end
SetCVar = function(n, v) CVARS[n] = v end
InCombatLockdown = function() return COMBAT end
function M.GetObjectType(s) return s.kind or "Frame" end
function M.IsShown(s) return s.shown end
OUT = {}; print = function(...) local t={} for i=1,select("#",...) do t[#t+1]=tostring(select(i,...)) end OUT[#OUT+1]=table.concat(t," ") end
SlashCmdList = {}
wipe = function(t) for k in pairs(t) do t[k]=nil end end
function AddPlate(unit, data)
  UNITS[unit] = data
  local p = New(); p.isPlate = true; p.UnitFrame = New(); p.namePlateUnitToken = unit
  local uf = p.UnitFrame
  uf.name = New()
  local bar = New(); uf.healthBar = bar
  bar.fill = New(); bar.fill.kind = "Texture"
  bar.bg = New(); bar.bg.kind = "Texture"
  bar.border = New(); bar.border.kind = "Frame"
  bar.power = New(); bar.power.kind = "StatusBar"
  bar.regions = { bar.fill, bar.bg }; bar.children = { bar.border, bar.power }; bar.h = 12
  function bar:GetStatusBarTexture() return self.fill end
  uf.castBar = New()
  local box = New(); box.h = 11; box.regions = {}; box.children = { bar }; uf.HealthBarsContainer = box
  uf.scale = 1; uf.cx, uf.cy = 100, 50
  box.w = 120; box.cx, box.cy = 100, 40
  box.points = { {"LEFT", uf, "LEFT", 4, -10}, {"RIGHT", uf, "RIGHT", -4, -10} }
  PLATES[unit] = p
  EV.scripts.OnEvent(EV, "NAME_PLATE_UNIT_ADDED", unit)
end
''')
L.execute(open('/home/claude/brand/AetherMarks/AetherMarks.lua').read(), 'AetherMarks')
L.execute('EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks")')
L.execute('AddPlate("nameplate1", {guid="1", name="Wolf"})')
box = 'PLATES.nameplate1.UnitFrame.HealthBarsContainer'
def pts(): return L.eval('(function() local o={} for _,p in ipairs('+box+'.points) do o[#o+1]=p[1]..(p[4] and (" "..p[4]..","..p[5]) or "") end return table.concat(o," + ") end)()')
print("clean on : width", L.eval(box+'.w'), "(Blizzard 120) | anchors", pts(), "| opacity", L.eval(box+'.alpha'))
L.execute(box+':SetPoint("TOP", PLATES.nameplate1.UnitFrame, "TOP", 0, 0)')
print("Blizzard re-anchors -> anchors", pts(), "| width", L.eval(box+'.w'))
L.execute('SlashCmdList.AETHERMARKS("width 40"); SlashCmdList.AETHERMARKS("alpha 60")')
print("/qm width 40, /qm alpha 60 -> width", L.eval(box+'.w'), "| opacity", L.eval(box+'.alpha'))
L.execute('SlashCmdList.AETHERMARKS("names")')
print("clean off: width", L.eval(box+'.w'), "| anchors", pts(), "| opacity", L.eval(box+'.alpha'))
