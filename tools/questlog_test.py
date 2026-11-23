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
C_TooltipInfo = { GetUnit = function(u) local x = UNITS[u]; if x.far then return { lines = { {leftText=x.name}, {leftText="Level 34"}, {leftText="Humanoid"} } } end; return { lines = { {leftText=x.name}, x.quest and {leftText=x.quest, type=8} or {leftText="Level 30"} } } end }
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
LOG_Q = {}
GetNumQuestLogEntries = function() return #LOG_Q end
GetQuestLogTitle = function(i) return LOG_Q[i].title, 30, 0, LOG_Q[i].header end
GetNumQuestLeaderBoards = function(i) return #(LOG_Q[i].obj or {}) end
GetQuestLogLeaderBoard = function(j, i) local o = LOG_Q[i].obj[j]; return o[1], o[2], o[3] end
wipe = function(t) for k in pairs(t) do t[k]=nil end end
function AddPlate(unit, data)
  UNITS[unit] = data
  local p = Obj("plate"); p.UnitFrame = Obj("uf"); p.UnitFrame.healthBar = Obj("bar"); p.namePlateUnitToken = unit
  PLATES[unit] = p
  EV.scripts.OnEvent(EV, "NAME_PLATE_UNIT_ADDED", unit)
end
''')
L.execute(open('/home/claude/brand/AetherMarks/AetherMarks_Unique.lua').read())
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
def name(u):
    c=L.eval('OVERLAYS[PLATES["%s"]].radarName.color'%u)
    col=tuple(round(c[i],2) for i in (1,2,3))
    return {(1.0,0.2,0.2):"RED",(0.54,0.81,0.94):"BABY BLUE",(0.64,0.21,0.93):"PURPLE"}.get(col,str(col))
def quests():
    L.execute('EV.scripts.OnEvent(EV, "QUEST_LOG_UPDATE")')
def show(l,u): print("%-45s %s"%(l,name(u)))
L.execute("""LOG_Q = {
 {title="Stranglethorn", header=true},
 {title="Panther Mastery", obj={{"Young Panther slain: 0/10","monster",false}}},
 {title="Tiger Mastery", obj={{"Young Stranglethorn Tiger slain: 7/10","monster",false}}},
 {title="Hunt for Yenniku", obj={{"Bloodscalp Tusk: 0/9","item",false}}},
 {title="Big Game", obj={{"King Bangalash slain: 0/1","monster",false}}},
}""")
quests()
for i,(id,n) in enumerate([("681","Young Panther"),("682","Stranglethorn Tiger"),("683","Young Stranglethorn Tiger"),("731","King Bangalash"),("694","Bloodscalp Axe Thrower"),("694","Bloodscalp Axe Thrower")],1):
    L.execute('AddPlate("nameplate%d", {guid="Creature-0-1-2-3-%s-%d", name="%s", far=true})'%(i,id,i,n))
for u,l in [(1,"far Young Panther (kill 0/10)"),(2,"far Stranglethorn Tiger (not the quest one)"),(3,"far Young Stranglethorn Tiger (7/10)"),(4,"far King Bangalash (0/1)"),(5,"far Axe Thrower, never seen up close"),(6,"far Axe Thrower #2")]:
    show(l,"nameplate%d"%u)
print("-- Axe Thrower #1 seen up close: tooltip shows '0/9 Bloodscalp Tusk'")
L.execute('UNITS.nameplate5.far = nil; UNITS.nameplate5.quest = "0/9 Bloodscalp Tusk"; EV.scripts.OnEvent(EV, "NAME_PLATE_UNIT_ADDED", "nameplate5")')
show("Axe Thrower #1 (tooltip read)","nameplate5")
show("far Axe Thrower #2 (learned type)","nameplate6")
L.execute('AddPlate("nameplate7", {guid="Creature-0-1-2-3-694-7", name="Bloodscalp Axe Thrower", far=true})')
show("new far Axe Thrower #3","nameplate7")
print("-- progress")
L.execute('LOG_Q[3].obj[1] = {"Young Stranglethorn Tiger slain: 10/10","monster",true}; LOG_Q[4].obj[1] = {"Bloodscalp Tusk: 9/9","item",true}'); quests()
show("Young Str. Tiger after 10/10","nameplate3")
show("far Axe Thrower #3 after 9/9 tusks","nameplate7")
show("Young Panther still 0/10","nameplate1")
print("-- modern-style text, no type")
L.execute('LOG_Q = {{title="P", obj={{"0/10 Young Panther slain"}}}}'); quests()
show("far Young Panther","nameplate1")
print("-- a later tusk quest: remembered type colors right away")
L.execute('LOG_Q = {{title="Y", obj={{"Bloodscalp Tusk: 2/9","item",false}}}}'); quests()
show("far Axe Thrower #3","nameplate7")
print("learned:", list(L.eval('AetherMarksDB.learned["694"]').keys()))

print("-- single-item objectives (0/1)")
L.execute('LOG_Q = {{title="Shared", obj={{"Bloody Bone Necklace: 0/1","item",false}}},{title="Uniq", obj={{"Bellygrub Tusk: 0/1","item",false}}}}'); quests()
L.execute('AddPlate("nameplate20", {guid="Creature-0-1-2-3-694-x", name="Bloodscalp Axe Thrower", quest="0/1 Bloody Bone Necklace"})')
L.execute('AddPlate("nameplate21", {guid="Creature-0-1-2-3-345-y", name="Bellygrub", quest="0/1 Bellygrub Tusk"})')
L.execute('AddPlate("nameplate22", {guid="Creature-0-1-2-3-694-z", name="Bloodscalp Axe Thrower", far=true})')
L.execute('AddPlate("nameplate23", {guid="Creature-0-1-2-3-345-w", name="Bellygrub", far=true})')
show("Axe Thrower, shared 0/1 item (tooltip)", "nameplate20")
show("Bellygrub, his own 0/1 item (tooltip)", "nameplate21")
show("far Axe Thrower (learned, shared item)", "nameplate22")
show("far Bellygrub (learned, unique)", "nameplate23")
L.execute('LOG_Q = {{title="K", obj={{"King Bangalash slain: 0/1","monster",false}}}}'); quests()
L.execute('AddPlate("nameplate24", {guid="Creature-0-1-2-3-731-k", name="King Bangalash", quest="King Bangalash slain: 0/1"})')
show("King Bangalash slain 0/1 (tooltip)", "nameplate24")
