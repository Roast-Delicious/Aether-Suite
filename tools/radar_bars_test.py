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
function M_SetMinMaxValues(self, a, b) self.min, self.max = a, b end
function M_SetValue(self, v) self.value = v end
function M_SetStatusBarColor(self, r, g, b) self.barColor = { r, g, b } end
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
HEALTH = { cur = 75, max = 100 }
UnitHealth = function(u) if SECRET_HEALTH then error("secret") end return HEALTH.cur end
UnitHealthMax = function(u) return HEALTH.max end
CASTING = nil; CHANNEL = nil
UnitCastingInfo = function(u) if CASTING then return CASTING[1], "", "", CASTING[2], CASTING[3] end end
UnitChannelInfo = function(u) if CHANNEL then return CHANNEL[1], "", "", CHANNEL[2], CHANNEL[3] end end
NOW = 100; GetTime = function() return NOW end
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
def bars(label, u):
    o = 'OVERLAYS[PLATES["%s"]]' % u
    hp = "hidden" if not L.eval(o+'.hp.shown') else "%s/%s color %s" % (L.eval(o+'.hp.value'), L.eval(o+'.hp.max'), tuple(round(x,2) for x in L.eval(o+'.hp.barColor').values()))
    cast = "hidden" if not L.eval(o+'.cast.shown') else "'%s' %s/%s..%s" % (L.eval(o+'.cast.text.text'), L.eval(o+'.cast.value'), L.eval(o+'.cast.min'), L.eval(o+'.cast.max'))
    print("%-40s blizzard alpha=%s | name shown=%s | health %s | cast %s" % (label, L.eval('PLATES["%s"].UnitFrame.alpha' % u), L.eval(o+'.radarName.shown'), hp, cast))
L.execute('SlashCmdList.AETHERMARKS("names 0")')
L.execute('AddPlate("nameplate1", {guid="a", name="Gnoll"}); AddPlate("nameplate2", {guid="b", name="Kobold", reaction=4})')
bars("not targeted (names 0)", "nameplate1")
L.execute('UNITS.target = UNITS.nameplate1; PLATES.target = PLATES.nameplate1; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
bars("targeted", "nameplate1")
L.execute('HEALTH.cur = 40; EV.scripts.OnEvent(EV, "UNIT_HEALTH", "target")'); bars("takes damage", "nameplate1")
L.execute('CASTING = {"Fireball", 100000, 102000}; EV.scripts.OnEvent(EV, "UNIT_SPELLCAST_START", "target"); NOW = 101; OVERLAYS[PLATES.nameplate1].cast.scripts.OnUpdate(OVERLAYS[PLATES.nameplate1].cast)')
bars("casting, halfway", "nameplate1")
L.execute('NOW = 102.5; OVERLAYS[PLATES.nameplate1].cast.scripts.OnUpdate(OVERLAYS[PLATES.nameplate1].cast)'); bars("cast finished", "nameplate1")
L.execute('CASTING = nil; CHANNEL = {"Drain Life", 103000, 108000}; NOW = 104; EV.scripts.OnEvent(EV, "UNIT_SPELLCAST_CHANNEL_START", "target"); OVERLAYS[PLATES.nameplate1].cast.scripts.OnUpdate(OVERLAYS[PLATES.nameplate1].cast)')
bars("channeling, 1s in (drains)", "nameplate1")
L.execute('CHANNEL = nil; EV.scripts.OnEvent(EV, "UNIT_SPELLCAST_CHANNEL_STOP", "target")'); bars("channel stopped", "nameplate1")
L.execute('SECRET_HEALTH = true; EV.scripts.OnEvent(EV, "UNIT_HEALTH", "target"); SECRET_HEALTH = nil'); bars("health hidden by game", "nameplate1")
L.execute('UNITS.target = UNITS.nameplate2; PLATES.target = PLATES.nameplate2; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
bars("old target after switching", "nameplate1"); bars("new target (neutral)", "nameplate2")
L.execute('AddPlate("nameplate5", {guid="e", name="Mystmane", class="rare", level=24}); UNITS.target = UNITS.nameplate5; PLATES.target = PLATES.nameplate5; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
bars("rare targeted (beacon + bars)", "nameplate5")
L.execute('SlashCmdList.AETHERMARKS("radar")'); bars("radar off", "nameplate5")
