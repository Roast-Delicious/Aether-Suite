from lupa.lua51 import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
table.unpack = table.unpack or unpack
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New() return setmetatable({scripts={}, color={1,0.82,0}}, M) end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.HookScript(s,k,f) local o=s.scripts[k]; s.scripts[k]=function(...) if o then o(...) end f(...) end end
function M.SetTextColor(s,r,g,b) s.color={r,g,b} end
function M.GetTextColor(s) return s.color[1], s.color[2], s.color[3] end
function M.RegisterEvent(s,e) if e=="UNIT_CLASSIFICATION_CHANGED" then error("unknown event") end end
function M.UnregisterEvent() end
CreateFrame = function() local f=New(); EV = EV or f; return f end
hooksecurefunc = function(obj, name, fn) local o=obj[name]; obj[name]=function(...) local r={o(...)}; fn(...); return table.unpack(r) end end
Enum = { TooltipDataType = { Unit = 2 }, TooltipDataLineType = { QuestObjective = 8 } }
POSTCALL = nil
TooltipDataProcessor = { AddTooltipPostCall = function(t, fn) POSTCALL = fn end }
GameTooltip = New(); GameTooltipTextLeft1 = New()
function GameTooltip:GetUnit() return "Bob", "mouseover" end
TargetFrame = New(); TargetFrame.name = New()
TargetFrameToT = New(); TargetFrameToT.name = New()
UNITS = {}
UnitExists = function(u) return UNITS[u] ~= nil end
UnitCanAttack = function(_, u) return true end
UnitIsPlayer = function() return false end
UnitIsDead = function() return false end
UnitGUID = function(u) return UNITS[u] and UNITS[u].guid end
UnitName = function(u) return UNITS[u] and UNITS[u].name end
UnitClassification = function(u) return UNITS[u] and UNITS[u].class or "normal" end
C_TooltipInfo = { GetUnit = function(u) local x = UNITS[u]; return { lines = { {leftText=x.name}, x.quest and {leftText=x.quest, type=8} or {leftText="Level 30"} } } end }
C_Timer = { After = function(t, fn) fn() end }
C_NamePlate = { GetNamePlates = function() return {} end }
SOUNDS = 0; PlaySound = function() SOUNDS = SOUNDS + 1 end
print = function() end
SlashCmdList = {}
wipe = function(t) for k in pairs(t) do t[k]=nil end end
''')
L.execute(open('/home/claude/brand/AetherMarks/AetherMarks.lua').read(), 'AetherMarks')
L.execute('EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks")')
def col(expr):
    c = L.eval(expr + '.color'); t = (round(c[1],2), round(c[2],2), round(c[3],2))
    return {(0.64,0.21,0.93):"PURPLE",(1.0,0.5,0.0):"ORANGE",(1.0,0.82,0.0):"normal yellow"}.get(t, str(t))
def target(desc, code):
    L.execute(code + '; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
    print(desc.ljust(46), col('TargetFrame.name'))
def col(expr):
    c = L.eval(expr + '.color'); t = (round(c[1],2), round(c[2],2), round(c[3],2))
    return {(0.64,0.21,0.93):"PURPLE",(1.0,0.5,0.0):"ORANGE",(0.54,0.81,0.94):"BABY BLUE",(1.0,0.82,0.0):"normal"}.get(t, str(t))
target("Gnoll, 'Gnoll Paw: 2/8'", 'UNITS.target = {guid="a", name="Gnoll", quest="Gnoll Paw: 2/8"}')
target("Hogger, 'Hogger slain: 0/1'", 'UNITS.target = {guid="b", name="Hogger", quest="Hogger slain: 0/1"}')
target("Named drop, 'Fang of Hogger: 0/1'", 'UNITS.target = {guid="c", name="Hogger2", quest="Fang of Hogger: 0/1"}')
target("Hogger already done, 'Hogger slain: 1/1'", 'UNITS.target = {guid="d", name="Hogger3", quest="Hogger slain: 1/1"}')
target("Gnoll objective done, 'Gnoll Paw: 8/8'", 'UNITS.target = {guid="e", name="Gnoll2", quest="Gnoll Paw: 8/8"}')
target("Rare that is also a named quest mob", 'UNITS.target = {guid="f", name="Rare", class="rare", quest="Rare slain: 0/1"}')
target("Plain mob", 'UNITS.target = {guid="g", name="Wolf"}')
