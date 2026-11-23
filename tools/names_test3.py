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
GetCVar = function() return "1" end
print = function() end
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
  uf.castBar = New(); uf.HealthBarsContainer = false
  PLATES[unit] = p
  EV.scripts.OnEvent(EV, "NAME_PLATE_UNIT_ADDED", unit)
end
''')
L.execute(open('/home/claude/brand/AetherMarks/AetherMarks.lua').read(), 'AetherMarks')
L.execute('EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks")')
L.execute('AddPlate("nameplate1", {guid="1", name="Wolf"})')
b = 'PLATES.nameplate1.UnitFrame.healthBar'
print("clean: bar height", L.eval(b+'.h'), "(Blizzard 12) | background", L.eval(b+'.bg.alpha'), "| border", L.eval(b+'.border.alpha'), "| resource bar", L.eval(b+'.power.alpha'), "| fill", L.eval(b+'.fill.alpha'))
L.execute(b+':SetHeight(14)')
print("Blizzard sets 14 -> bar height", L.eval(b+'.h'))
L.execute('SlashCmdList.AETHERMARKS("bar 30")')
print("/qm bar 30 -> bar height", round(L.eval(b+'.h'),1))
L.execute('SlashCmdList.AETHERMARKS("names")')
print("clean mode off -> bar height", L.eval(b+'.h'), "| background", L.eval(b+'.bg.alpha'))
