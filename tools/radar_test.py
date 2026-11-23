from lupa.lua51 import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
LOG = {}
local function Obj(kind)
  local o = { kind = kind, shown = true, alpha = 1, hooks = {} }
  return setmetatable(o, { __index = function(t, k)
    local f = rawget(_G, "M_" .. k)
    if f then return f end
    if type(k) == "string" and k:match("^%u") then return function() return nil end end
    return nil
  end })
end
function M_Show(self) self.shown = true end
function M_Hide(self) self.shown = false end
function M_IsShown(self) return self.shown end
function M_SetAlpha(self, a) self.alpha = a; for _, h in ipairs(self.hooks.SetAlpha or {}) do h(self, a) end end
function M_GetAlpha(self) return self.alpha end
function M_SetText(self, t) self.text = t end
function M_SetTextColor(self, r, g, b) self.color = { r, g, b } end
function M_GetTextColor(self) return 1, 0.82, 0 end
function M_GetFont(self) return "F", 10 end
function M_CreateTexture(self) return Obj("tex") end
function M_CreateFontString(self) return Obj("fs") end
function M_CreateAnimationGroup(self)
  local g = Obj("anim"); g.playing = false
  function g:Play() self.playing = true end
  function g:Stop() self.playing = false end
  function g:IsPlaying() return self.playing end
  function g:CreateAnimation() return Obj("a") end
  return g
end
function M_IsForbidden() return false end
function M_SetIgnoreParentAlpha(self, v) self.ignoreParentAlpha = v end
function M_SetIgnoreParentScale(self, v) self.ignoreParentScale = v end
function M_SetScale(self, v) self.scale = v end
function M_GetEffectiveScale(self) return 0.71 end
FRAMES = {}
function CreateFrame(kind)
  local f = Obj(kind); f.scripts = {}
  function f:SetScript(n, fn) self.scripts[n] = fn end
  FRAMES[#FRAMES + 1] = f
  return f
end
function hooksecurefunc(obj, name, fn)
  if type(obj) ~= "table" then return end
  obj.hooks = obj.hooks or {}
  obj.hooks[name] = obj.hooks[name] or {}
  table.insert(obj.hooks[name], fn)
end
UIParent = Obj("UIParent")
Enum = { TooltipDataLineType = { QuestObjective = 8 }, TooltipDataType = { Unit = 1 } }
TooltipDataProcessor = { AddTooltipPostCall = function() end }
GameTooltip = Obj("tt")
UNITS = {}
UnitExists = function(u) return UNITS[u] ~= nil end
UnitCanAttack = function(_, u) return UNITS[u] and not UNITS[u].friend end
UnitIsPlayer = function() return false end
UnitIsDead = function() return false end
UnitGUID = function(u) return UNITS[u] and UNITS[u].guid end
UnitName = function(u) return UNITS[u] and UNITS[u].name end
UnitLevel = function(u) return UNITS[u] and UNITS[u].level or 30 end
UnitReaction = function(u) return UNITS[u] and UNITS[u].reaction or 2 end
UnitIsUnit = function(a, b) return UNITS[a] ~= nil and UNITS[b] ~= nil and UNITS[a].guid == UNITS[b].guid end
UnitClassification = function(u) return UNITS[u] and UNITS[u].class or "normal" end
FACTION_BAR_COLORS = { [2] = { r = 1, g = 0, b = 0 }, [4] = { r = 1, g = 1, b = 0 } }
C_TooltipInfo = { GetUnit = function(u) local x = UNITS[u]; return { lines = { {leftText=x.name}, x.quest and {leftText=x.quest, type=8} or {leftText="Level 30"} } } end }
C_Timer = { After = function(t, fn) fn() end }
PLATES = {}
C_NamePlate = { GetNamePlates = function() local o={} for _,p in pairs(PLATES) do o[#o+1]=p end return o end,
  GetNamePlateForUnit = function(u) return PLATES[u] end }
PlaySound = function() LOG[#LOG+1] = "sound" end
RaidNotice_AddMessage = function(_, m) LOG[#LOG+1] = "notice: " .. m end
RaidWarningFrame = {}
MARKS = {}
SetRaidTarget = function(u, i) MARKS[UNITS[u].guid] = i; LOG[#LOG+1] = "skull on " .. UNITS[u].name end
GetRaidTargetIndex = function(u) return MARKS[UNITS[u].guid] end
CVARS = { nameplateMaxDistance = "20", nameplateShowEnemies = "1" }
GetCVar = function(n) return CVARS[n] end
SetCVar = function(n, v) CVARS[n] = v end
COMBAT = false
InCombatLockdown = function() return COMBAT end
print = function(m) LOG[#LOG+1] = "print: " .. tostring(m) end
SlashCmdList = {}
wipe = function(t) for k in pairs(t) do t[k]=nil end end
function AddPlate(unit, data)
  UNITS[unit] = data
  local p = Obj("plate"); p.UnitFrame = Obj("uf"); p.UnitFrame.healthBar = Obj("bar"); p.namePlateUnitToken = unit
  PLATES[unit] = p
  EV.scripts.OnEvent(EV, "NAME_PLATE_UNIT_ADDED", unit)
end
''')
src = open('/home/claude/brand/AetherMarks/AetherMarks.lua').read().replace('local overlays   = {}', 'OVERLAYS = {}; local overlays = OVERLAYS')
L.execute(src, 'AetherMarks')
L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then EV = f end end')
L.execute('EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks"); EV.scripts.OnEvent(EV, "PLAYER_LOGIN")')
L.execute('''
function Describe(u)
  local p = PLATES[u]
  local o = OVERLAYS[p]
  local s = "blizzard plate alpha=" .. tostring(p.UnitFrame.alpha)
  if not o or not o.shown then return s .. " | no overlay" end
  if o.beacon.shown then
    s = s .. " | BEACON '" .. tostring(o.beacon.name.text) .. "' / " .. tostring(o.beacon.sub.text) .. " pulse=" .. tostring(o.beacon.pulse.playing)
  end
  if o.radarName.shown then
    local c = o.radarName.color
    s = s .. string.format(" | name '%s' rgb(%.2f,%.2f,%.2f) alpha=%.2f", o.radarName.text, c[1], c[2], c[3], o.radarName.alpha)
  end
  if o.box.shown then s = s .. " | outline label '" .. tostring(o.label.text) .. "'" end
  return s
end''')
def show(desc, u): print(desc.ljust(42), L.eval(f'Describe("{u}")'))
def log():
    out = list(L.eval('LOG').values()); L.execute('LOG = {}')
    if out: print("   events:", "; ".join(out))
print("range after login:", L.eval('CVARS.nameplateMaxDistance'), "| old value saved:", L.eval('AetherMarksDB.radarDistance')); log()
L.execute('AddPlate("nameplate1", {guid="a", name="Gnoll"})'); show("ordinary hostile", "nameplate1")
L.execute('AddPlate("nameplate2", {guid="b", name="Kobold", reaction=4})'); show("ordinary neutral", "nameplate2")
L.execute('AddPlate("nameplate3", {guid="c", name="Gnoll Brute", quest="Gnoll Paw: 2/8"})'); show("quest mob", "nameplate3")
L.execute('AddPlate("nameplate4", {guid="d", name="Hogger", quest="Hogger slain: 0/1"})'); show("named quest mob", "nameplate4")
L.execute('AddPlate("nameplate5", {guid="e", name="Mystmane", class="rare", level=24})'); show("rare", "nameplate5"); log()
L.execute('AddPlate("nameplate6", {guid="f", name="Takk the Leaper", class="rareelite", level=19, quest="Takk slain: 0/1"})'); show("rare elite, also quest", "nameplate6"); log()
L.execute('PLATES.nameplate1.UnitFrame:SetAlpha(0.6)'); show("Blizzard tries to re-show a hidden plate", "nameplate1")
L.execute('UNITS.target = UNITS.nameplate1; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")'); show("ordinary mob becomes target", "nameplate1")
L.execute('UNITS.target = nil; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")'); show("target cleared", "nameplate1")
L.execute('EV.scripts.OnEvent(EV, "NAME_PLATE_UNIT_REMOVED", "nameplate5"); AddPlate("nameplate5", {guid="e", name="Mystmane", class="rare", level=24})'); show("same rare back in range", "nameplate5"); log()
L.execute('SlashCmdList.AETHERMARKS("names 50")'); show("/qm names 50: ordinary", "nameplate1"); show("/qm names 50: quest mob", "nameplate3")
L.execute('SlashCmdList.AETHERMARKS("names 0")'); show("/qm names 0: ordinary", "nameplate1"); log()
L.execute('SlashCmdList.AETHERMARKS("radar")'); show("/qm radar off: ordinary", "nameplate1"); show("/qm radar off: rare", "nameplate5"); show("/qm radar off: quest", "nameplate3")
print("range after radar off:", L.eval('CVARS.nameplateMaxDistance'), "| saved:", L.eval('AetherMarksDB.radarDistance')); log()
L.execute('COMBAT = true; SlashCmdList.AETHERMARKS("radar")'); print("radar on in combat -> range", L.eval('CVARS.nameplateMaxDistance'))
L.execute('COMBAT = false; EV.scripts.OnEvent(EV, "PLAYER_REGEN_ENABLED")'); print("after combat -> range", L.eval('CVARS.nameplateMaxDistance')); log()
L.execute('MARKS = {}; SlashCmdList.AETHERMARKS("skull"); AddPlate("nameplate7", {guid="g", name="Other Rare", class="rare"})'); print("skull off, new rare marked:", L.eval('MARKS.g')); log()
L.execute('CVARS.nameplateShowEnemies = "0"; LOG = {}; EV.scripts.OnEvent(EV, "PLAYER_LOGIN")'); log()
