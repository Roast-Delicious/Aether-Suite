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
  local p = New(); p.isPlate = true; p.UnitFrame = New(); p.UnitFrame.healthBar = New(); p.namePlateUnitToken = unit
  PLATES[unit] = p
  EV.scripts.OnEvent(EV, "NAME_PLATE_UNIT_ADDED", unit)
end
''')
L.execute(open('/home/claude/brand/AetherMarks/AetherMarks.lua').read(), 'AetherMarks')
L.execute('EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks")')
C = {(0.54,0.81,0.94):"BABY BLUE",(0.64,0.21,0.93):"PURPLE",(1.0,0.5,0.0):"ORANGE",(1.0,0.25,0.2):"RED",(1.0,0.9,0.1):"YELLOW"}
def show(unit):
    o = f'OVERLAYS[PLATES["{unit}"]]'
    c = L.eval(o + '.name.color'); col = C.get((round(c[1],2), round(c[2],2), round(c[3],2)), str(tuple(c.values())))
    alpha = L.eval('PLATES["' + unit + '"].UnitFrame.alpha')
    return 'name "%s" %s, shown=%s, size x%s, Blizzard plate alpha=%s, outline shown=%s' % (L.eval(o+".name.text"), col, L.eval(o+".name.shown"), L.eval(o+".name.scale"), alpha, L.eval(o+".box.shown"))
L.execute('''
AddPlate("nameplate1", {guid="1", name="Wolf"})
AddPlate("nameplate2", {guid="2", name="Gnoll", quest="Gnoll Paw: 2/8"})
AddPlate("nameplate3", {guid="3", name="Hogger", quest="Hogger slain: 0/1"})
AddPlate("nameplate4", {guid="4", name="Rare Guy", class="rare"})
AddPlate("nameplate5", {guid="5", name="Kodo", reaction=4})
AddPlate("nameplate6", {guid="6", name="Friendly Guard", reaction=5})
''')
for i, label in enumerate(["hostile mob","quest mob","named quest mob","rare","neutral mob"],1):
    print(label.ljust(16), show(f"nameplate{i}"))
print("friendly guard".ljust(16), "Blizzard plate alpha =", L.eval('PLATES.nameplate6.UnitFrame.alpha'), "(left alone)")
L.execute('UNITS.target = UNITS.nameplate2; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
print("target the Gnoll:", show("nameplate2"))
L.execute('PLATES.nameplate1.UnitFrame:SetAlpha(1)')
print("Blizzard re-shows Wolf plate -> alpha", L.eval('PLATES.nameplate1.UnitFrame.alpha'))
L.execute('SlashCmdList.AETHERMARKS("names")')
print("/qm names (off) Gnoll:", show("nameplate2"))
print("/qm names (off) Wolf: Blizzard alpha", L.eval('PLATES.nameplate1.UnitFrame.alpha'), "overlay shown", L.eval('OVERLAYS[PLATES.nameplate1].shown'))
