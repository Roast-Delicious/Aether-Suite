-- ==========================================
-- AetherMarks - quest and rare mob highlights for WoW Forever (1.60.x)
-- Mobs you still need for a quest get a baby blue name, named quest mobs (unique
-- ones a quest asks for just one of, like "Hogger slain: 0/1") a purple one (the
-- epic item color) and rare mobs an orange one (the legendary color), on your target frame,
-- target-of-target, focus frame and the mouseover tooltip. A sound plays when
-- a rare shows up.
--
-- Rare Radar (with enemy nameplates on, V): every mob near you is checked as
-- soon as its nameplate appears, without targeting it. Rares get a beacon over
-- their heads (pulsing glow, skull icon, big orange name), an orange pulse
-- around the screen edge and a sound. (Placing the skull raid marker is
-- reserved for Blizzard's own UI in WoW Forever, so the skull is drawn by us.)
-- Ordinary mobs' Blizzard plates are hidden and replaced by a plain name (or a
-- faded one, or nothing: db.others), quest mobs keep their colored name, and
-- your target gets a slim health bar (and a slim cast bar while it casts)
-- under its name. The nameplate range is raised to the maximum while Rare
-- Radar is on, and put back when it's turned off.
-- ==========================================

local ADDON_NAME = ...

local DEFAULTS = {
    quest      = true,    -- highlight quest mobs
    rare       = true,    -- highlight rare mobs
    rareSound  = true,    -- play a sound + message when a rare shows up
    radar      = true,    -- Rare Radar (needs enemy nameplates on)
    others     = 1,       -- Rare Radar: opacity of ordinary mobs' names (0 hides them)
}

local RADAR_DISTANCE = 41   -- nameplate range while Rare Radar is on (the game caps it)

-- Settings from the "clean nameplates" version (1.4.x), no longer used.
local RETIRED = { "namesOnly", "barScale", "farScale", "plateScale", "barWidth", "barAlpha", "skull" }

local COLORS = {
    quest = { 0.54, 0.81, 0.94 },   -- baby blue
    named = { 0.64, 0.21, 0.93 },   -- purple, like epic items
    rare  = { 1.00, 0.50, 0.00 },   -- orange, like legendary items
}

local db
local overlays   = {}   -- nameplate -> our overlay frame
local questCache = {}   -- GUID -> true/false, kept for when tooltips are hidden in combat
local rareSeen   = {}   -- GUID -> true, so each rare only alerts once per session

-- What the last quest check saw, for /qm debug.
local lastWhy = {}

local function IsSecret(v)
    return issecretvalue ~= nil and issecretvalue(v)
end

local function Readable(v)
    return v ~= nil and not IsSecret(v)
end

-- A yes/no answer from the game, or nil when it's hidden from addons (a
-- hidden answer can't even be tested, so it must never reach an "if").
local function Flag(fn, ...)
    if not fn then return nil end
    local ok, v = pcall(fn, ...)
    if not ok or IsSecret(v) then return nil end
    return v and true or false
end

-- ==========================================
-- SAVED SETTINGS (account + character, merged)
-- ==========================================
-- WoW Forever 1.60 has been reported not to read account-wide saved variables
-- back, so settings are stored in both tables.

local function LoadSettings()
    local merged = {}
    -- QuarryMarks* hold settings from before the rename (present only right after migrating).
    local sources = { QuarryMarksCharDB, QuarryMarksDB, AetherMarksCharDB, AetherMarksDB }
    for i = 1, 4 do              -- not ipairs: it stops at the first nil
        local source = sources[i]
        if type(source) == "table" then
            for k, v in pairs(source) do
                if merged[k] == nil then merged[k] = v end
            end
        end
    end
    for k, v in pairs(DEFAULTS) do
        if merged[k] == nil then merged[k] = v end
    end
    db = merged
    AetherMarksDB = db
    AetherMarksCharDB = db
    QuarryMarksDB, QuarryMarksCharDB = nil, nil
end

-- ==========================================
-- WHAT KIND OF MOB IS THIS?
-- ==========================================

-- Returns true for rares, plus true again for rare elites.
local function IsRare(unit)
    local ok, class = pcall(UnitClassification, unit)
    if not ok or not Readable(class) then return false end
    return class == "rare" or class == "rareelite", class == "rareelite"
end

local OBJECTIVE_TYPE = Enum.TooltipDataLineType and Enum.TooltipDataLineType.QuestObjective

-- "3/8" style progress in a line of text: true if not finished yet (nil if
-- there's no count), and the number needed.
local function UnfinishedCount(text)
    local have, need = text:match("(%d+)%s*/%s*(%d+)")
    if have then return tonumber(have) < tonumber(need), tonumber(need) end
    return nil
end

-- "0/9 Bloodscalp Tusk", "- Bloodscalp Tusk: 0/9" -> "Bloodscalp Tusk"
local function ObjectiveName(text)
    local t = text:gsub("^%s*%-%s*", ""):gsub("%d+%s*/%s*%d+", "")
    t = t:gsub("^%s+", ""):gsub("%s+$", ""):gsub("^:%s*", ""):gsub("%s*:$", "")
    return t
end

-- Returns needed (true / false, or nil when the game won't tell us right now)
-- and named: true when an unfinished objective for this mob needs just one
-- (a unique, named quest target).
-- Purple is for one-of-a-kind quest targets: a "slain: 0/1" objective naming
-- this mob, or a single item that only this named mob drops. A "0/1" item that
-- ordinary mobs drop keeps them baby blue.
local function IsUnique(objective, name, key)
    if name and objective then
        local target = objective:gsub("%s+[Ss]lain$", "")
        if target == name then return true end
    end
    local id = key and tonumber(key)
    return id and AetherMarks_Unique and AetherMarks_Unique[id] and true or false
end

local function NeedsForQuest(unit, name, key)
    if not (C_TooltipInfo and C_TooltipInfo.GetUnit) then return nil end
    local ok, data = pcall(C_TooltipInfo.GetUnit, unit)
    if not ok or not data or not data.lines then return nil end
    lastWhy.lines = #data.lines

    local needed, named, seen = false, false, {}
    for i = 2, #data.lines do
        local line = data.lines[i]
        local text = line.leftText
        if not Readable(text) then return nil end

        local unfinished, count
        if OBJECTIVE_TYPE and line.type == OBJECTIVE_TYPE then
            unfinished, count = UnfinishedCount(text)
            if unfinished == nil and Readable(line.completed) then unfinished = (line.completed == false) end
        elseif text:find("^%s*%-") then
            -- Objective lines start with " - " on older-style tooltips.
            unfinished, count = UnfinishedCount(text)
        end
        if unfinished ~= nil or count then seen[#seen + 1] = ObjectiveName(text) end
        if unfinished then
            needed = true
            if count == 1 and IsUnique(ObjectiveName(text), name, key) then named = true end
        end
    end
    -- No unfinished objective in the tooltip means you don't need this mob
    -- (WoW drops an objective's line once it's done). The quest log isn't
    -- asked instead: it says "related to a quest" until you turn the quest
    -- in, which kept finished mobs colored.
    return needed, named, seen
end

-- ==========================================
-- QUEST LOG MATCHING (works at any distance)
-- ==========================================
-- Far-away mobs' tooltips come without their quest lines, so the quest log is
-- read too:
--  * kill objectives ("Young Panther slain: 0/10"): any mob whose name is an
--    exact match is needed until the objective is done;
--  * item objectives ("Bloodscalp Tusk: 0/9"): the log doesn't say who drops
--    them, so each mob type is learned the first time its tooltip shows the
--    item (mouse-over, target, or up close), and remembered in db.learned.
-- The log is read again only when it changes, not per plate.
local questIndex = { kills = {}, items = {} }
local questDirty = true
local OnLearned   -- set further down: recolors plates when a new mob type is learned

local function AddObjective(kills, items, text, kind, finished, required)
    if not Readable(text) or text == "" then return end
    local have, need = text:match("(%d+)%s*/%s*(%d+)")
    required = tonumber(required) or tonumber(need) or 0
    if finished == nil and have then finished = tonumber(have) >= tonumber(need) end
    if finished then return end
    local name = ObjectiveName(text)
    if name == "" then return end
    if kind == "monster" or (kind == nil and name:find("%s[Ss]lain$")) then
        name = name:gsub("%s+[Ss]lain$", "")
        kills[name] = required
    elseif kind == "item" then
        items[name] = required
    end
end

local function BuildQuestIndex()
    questDirty = false
    local kills, items = {}, {}
    -- Classic-style quest log
    pcall(function()
        for i = 1, GetNumQuestLogEntries() or 0 do
            local _, _, _, isHeader = GetQuestLogTitle(i)
            if not isHeader then
                for j = 1, GetNumQuestLeaderBoards(i) or 0 do
                    local text, kind, finished = GetQuestLogLeaderBoard(j, i)
                    AddObjective(kills, items, text, kind, finished)
                end
            end
        end
    end)
    -- Newer quest log API, when the game has it
    pcall(function()
        for i = 1, C_QuestLog.GetNumQuestLogEntries() or 0 do
            local info = C_QuestLog.GetInfo(i)
            if info and not info.isHeader and info.questID then
                for _, o in ipairs(C_QuestLog.GetQuestObjectives(info.questID) or {}) do
                    AddObjective(kills, items, o.text, o.type, o.finished, o.numRequired)
                end
            end
        end
    end)
    questIndex.kills, questIndex.items = kills, items
end

-- "Creature-0-1-2-3-1234-5678" -> "1234" (the mob type); the name if the GUID is hidden.
local function MobKey(guid, name)
    if guid then
        local id = guid:match("^%a+%-%d+%-%d+%-%d+%-%d+%-(%d+)")
        if id then return id end
    end
    return name and ("n:" .. name)
end

-- needed, named from the quest log for this mob.
local function NeedsFromLog(name, key)
    if questDirty then BuildQuestIndex() end
    local needed, named = false, false
    local req = name and questIndex.kills[name]
    if req then needed = true; named = (req == 1) end      -- "Hogger slain: 0/1"
    -- A mob type is remembered by its creature ID and by its name, so it still
    -- matches when the game hides one of them (in combat, far away).
    for _, k in ipairs({ key or false, name and ("n:" .. name) or false }) do
        local drops = k and db.learned and db.learned[k]
        if drops then
            for item in pairs(drops) do
                local r = questIndex.items[item]
                if r then
                    needed = true
                    if r == 1 and IsUnique(nil, nil, k) then named = true end   -- only if no one else drops it
                end
            end
        end
    end
    return needed, named
end

-- Remember which quest items this mob type showed on its tooltip.
local function Learn(key, seen)
    if not key or not seen or #seen == 0 then return end
    if questDirty then BuildQuestIndex() end
    for _, item in ipairs(seen) do
        if item ~= "" and not questIndex.kills[item:gsub("%s+[Ss]lain$", "")] then
            db.learned = db.learned or {}
            db.learned[key] = db.learned[key] or {}
            if not db.learned[key][item] then
                db.learned[key][item] = true
                if OnLearned then OnLearned() end   -- other plates of this type, even far ones
            end
        end
    end
end

-- ==========================================
-- OVERLAY ON A NAMEPLATE
-- ==========================================

local FONT = STANDARD_TEXT_FONT or "Fonts\\FRIZQT__.TTF"

local TARGET_BAR_WIDTH = 70
local NAME_SIZE = 13         -- Rare Radar names of ordinary and quest mobs

local function MakeSlimBar(parent, width, height)
    local bar = CreateFrame("StatusBar", nil, parent)
    bar:SetSize(width, height)
    bar:SetStatusBarTexture("Interface\\Buttons\\WHITE8X8")
    local bg = bar:CreateTexture(nil, "BACKGROUND")
    bg:SetAllPoints()
    bg:SetColorTexture(0, 0, 0, 0.55)
    bar:SetMinMaxValues(0, 1)
    bar:SetValue(1)
    bar:Hide()
    return bar
end

local function MakeEdge(parent)
    local t = parent:CreateTexture(nil, "OVERLAY")
    t:SetColorTexture(1, 1, 1, 1)
    return t
end

local function HealthBarOf(plate)
    local uf = plate.UnitFrame
    return uf and (uf.healthBar or (uf.HealthBarsContainer and uf.HealthBarsContainer.healthBar))
end

local function GetOverlay(plate)
    local o = overlays[plate]
    if o then return o end

    o = CreateFrame("Frame", nil, plate)
    o:SetFrameStrata("HIGH")
    -- WoW fades nameplates that aren't your target or that are behind
    -- something, and draws them smaller with distance. Our names and beacons
    -- ignore both, so every mob's name has the same color and a steady,
    -- readable size (the same scale as the rest of your interface).
    if o.SetIgnoreParentAlpha then o:SetIgnoreParentAlpha(true) end
    if o.SetIgnoreParentScale then
        o:SetIgnoreParentScale(true)
        o:SetScale(UIParent:GetEffectiveScale())
    end

    -- Outline around the health bar if we can find it, otherwise the middle of the plate.
    local bar = HealthBarOf(plate)
    o.box = CreateFrame("Frame", nil, o)
    if bar then
        o.box:SetPoint("TOPLEFT", bar, "TOPLEFT", -2, 2)
        o.box:SetPoint("BOTTOMRIGHT", bar, "BOTTOMRIGHT", 2, -2)
    else
        o.box:SetSize(120, 14)
        o.box:SetPoint("CENTER", plate, "CENTER", 0, 0)
    end

    o.top, o.bottom, o.left, o.right = MakeEdge(o.box), MakeEdge(o.box), MakeEdge(o.box), MakeEdge(o.box)
    o.top:SetPoint("TOPLEFT");        o.top:SetPoint("TOPRIGHT");        o.top:SetHeight(2)
    o.bottom:SetPoint("BOTTOMLEFT");  o.bottom:SetPoint("BOTTOMRIGHT");  o.bottom:SetHeight(2)
    o.left:SetPoint("TOPLEFT");       o.left:SetPoint("BOTTOMLEFT");     o.left:SetWidth(2)
    o.right:SetPoint("TOPRIGHT");     o.right:SetPoint("BOTTOMRIGHT");   o.right:SetWidth(2)

    -- Soft tint behind the bar so the highlight shows at a glance.
    o.tint = o.box:CreateTexture(nil, "BACKGROUND")
    o.tint:SetPoint("TOPLEFT", -3, 3)
    o.tint:SetPoint("BOTTOMRIGHT", 3, -3)
    o.tint:SetColorTexture(1, 1, 1, 0.18)

    o.label = o:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    o.label:SetPoint("BOTTOM", o.box, "TOP", 0, 14)
    local font, size = o.label:GetFont()
    if font then o.label:SetFont(font, size or 10, "OUTLINE") end

    -- Rare Radar: a plain name in place of Blizzard's plate for ordinary mobs.
    o.radarName = o:CreateFontString(nil, "OVERLAY")
    o.radarName:SetFont(FONT, NAME_SIZE, "OUTLINE")
    o.radarName:SetPoint("CENTER", plate, "CENTER", 0, 0)
    o.radarName:Hide()

    -- Rare Radar: the beacon over a rare (glow, skull, big name, RARE line).
    local b = CreateFrame("Frame", nil, o)
    b:SetSize(1, 1)
    b:SetPoint("CENTER", plate, "CENTER", 0, 8)
    b.glow = b:CreateTexture(nil, "BACKGROUND")
    b.glow:SetTexture("Interface\\Cooldown\\star4")
    b.glow:SetBlendMode("ADD")
    b.glow:SetSize(150, 150)
    b.glow:SetPoint("CENTER", b, "CENTER", 0, 4)
    b.glow:SetVertexColor(1, 0.5, 0, 1)
    b.name = b:CreateFontString(nil, "OVERLAY")
    b.name:SetFont(FONT, 18, "OUTLINE")
    b.name:SetPoint("CENTER", b, "CENTER", 0, 0)
    b.name:SetTextColor(COLORS.rare[1], COLORS.rare[2], COLORS.rare[3])
    b.skull = b:CreateTexture(nil, "OVERLAY")
    b.skull:SetTexture("Interface\\TargetingFrame\\UI-RaidTargetingIcon_8")
    b.skull:SetSize(30, 30)
    b.skull:SetPoint("BOTTOM", b.name, "TOP", 0, 4)
    b.sub = b:CreateFontString(nil, "OVERLAY")
    b.sub:SetFont(FONT, 11, "OUTLINE")
    b.sub:SetPoint("TOP", b.name, "BOTTOM", 0, -3)
    local pulse = b:CreateAnimationGroup()
    pulse:SetLooping("BOUNCE")
    local fade = pulse:CreateAnimation("Alpha")
    fade:SetFromAlpha(1)
    fade:SetToAlpha(0.3)
    fade:SetDuration(0.6)
    if fade.SetTarget then fade:SetTarget(b.glow) end
    b.pulse = pulse
    b:Hide()
    o.beacon = b

    -- Rare Radar, your target: slim health bar, and a slim cast bar while it casts.
    o.hp = MakeSlimBar(o, TARGET_BAR_WIDTH, 4)
    o.cast = MakeSlimBar(o, TARGET_BAR_WIDTH, 3)
    o.cast:SetPoint("TOP", o.hp, "BOTTOM", 0, -2)
    o.cast.text = o.cast:CreateFontString(nil, "OVERLAY")
    o.cast.text:SetFont(FONT, 8, "OUTLINE")
    o.cast.text:SetPoint("TOP", o.cast, "BOTTOM", 0, -1)

    overlays[plate] = o
    return o
end

-- Rare Radar hides Blizzard's own plate (health bar, name and all) by making it
-- fully transparent; the mob can still be clicked. If Blizzard changes its
-- transparency while it's hidden, it's put back to hidden, and the value
-- Blizzard wanted is kept for when it's shown again.
local hiddenPlates = {}   -- Blizzard plate unit frame -> true while hidden
local blizzardAlpha = {}  -- Blizzard plate unit frame -> the transparency Blizzard last set
local settingAlpha = false

local function HideBlizzardPlate(plate, hide)
    local uf = plate.UnitFrame
    if not uf or (uf.IsForbidden and uf:IsForbidden()) then return end
    if hiddenPlates[uf] == nil then
        if not hide then return end
        blizzardAlpha[uf] = uf:GetAlpha() or 1
        hooksecurefunc(uf, "SetAlpha", function(self, alpha)
            if settingAlpha then return end
            blizzardAlpha[self] = alpha
            if hiddenPlates[self] and alpha ~= 0 then
                settingAlpha = true
                self:SetAlpha(0)
                settingAlpha = false
            end
        end)
    end
    if (hiddenPlates[uf] or false) == hide then return end
    hiddenPlates[uf] = hide
    settingAlpha = true
    uf:SetAlpha(hide and 0 or (blizzardAlpha[uf] or 1))
    settingAlpha = false
end

-- Name color for a mob that isn't a quest mob or rare: bright red if hostile,
-- yellow if neutral, green if friendly. Always these exact colors (not WoW's
-- duller reaction colors), so every hostile mob's name is the same red even
-- when the game won't say how a mob feels about you.
local REACTION = {
    hostile  = { 1, 0.2, 0.2 },
    neutral  = { 1, 0.69, 0 },   -- Aether gold: the suite's only yellow
    friendly = { 0.2, 1, 0.2 },
}
local function ReactionColor(unit)
    local ok, r = pcall(UnitReaction, unit, "player")
    if ok and Readable(r) then
        if r == 4 then return REACTION.neutral end
        if r >= 5 then return REACTION.friendly end
    end
    return REACTION.hostile
end

local function Paint(o, color, text)
    for _, edge in ipairs({ o.top, o.bottom, o.left, o.right }) do
        edge:SetVertexColor(color[1], color[2], color[3], 1)
    end
    o.tint:SetVertexColor(color[1], color[2], color[3], 0.18)
    o.label:SetText(text)
    o.label:SetTextColor(color[1], color[2], color[3])
    o:Show()
end

-- An orange glow around the edges of the screen that pulses twice.
local edgePulse
local function PulseScreenEdge()
    if not edgePulse then
        edgePulse = CreateFrame("Frame", nil, UIParent)
        edgePulse:SetAllPoints(UIParent)
        edgePulse:SetFrameStrata("BACKGROUND")
        local t = edgePulse:CreateTexture(nil, "BACKGROUND")
        t:SetAllPoints()
        t:SetTexture("Interface\\FullScreenTextures\\LowHealth")
        t:SetBlendMode("ADD")
        t:SetVertexColor(1, 0.5, 0, 1)
        edgePulse:SetAlpha(0)
        local anim = edgePulse:CreateAnimationGroup()
        for i = 1, 4 do
            local a = anim:CreateAnimation("Alpha")
            a:SetFromAlpha(i % 2 == 1 and 0 or 1)
            a:SetToAlpha(i % 2 == 1 and 1 or 0)
            a:SetDuration(0.4)
            a:SetOrder(i)
        end
        anim:SetScript("OnFinished", function() edgePulse:SetAlpha(0) end)
        edgePulse.anim = anim
    end
    edgePulse.anim:Stop()
    edgePulse.anim:Play()
end

local function AlertRare(unit, guid)
    if not db.rareSound or not guid or rareSeen[guid] then return end
    rareSeen[guid] = true
    PulseScreenEdge()
    local name = UnitName(unit)
    if not Readable(name) then name = "A rare" end
    PlaySound(SOUNDKIT and SOUNDKIT.RAID_WARNING or 8959, "Master")
    if RaidNotice_AddMessage and RaidWarningFrame then
        RaidNotice_AddMessage(RaidWarningFrame, "RARE: " .. name, { r = 1, g = 0.5, b = 0 })
    end
    print("|cffff8000AetherMarks:|r rare spotted - " .. name)
end

-- Is this a quest mob and/or a rare? Returns rare, quest, named, rare elite
-- (and alerts for rares).
-- Only enemies (and neutral mobs you can attack); not players.
local function Classify(unit)
    -- Unknown (hidden) answers count as "go ahead": nameplates are mostly mobs.
    if not db or Flag(UnitExists, unit) == false or Flag(UnitCanAttack, "player", unit) == false
        or Flag(UnitIsPlayer, unit) or Flag(UnitIsDead, unit) then
        return false, false, false
    end
    local guid = UnitGUID(unit)
    if not Readable(guid) then guid = nil end

    local rare, elite = false, false
    if db.rare then rare, elite = IsRare(unit) end
    local quest, named = false, false
    wipe(lastWhy)
    if db.quest then
        local okName, name = pcall(UnitName, unit)
        if not okName or not Readable(name) then name = nil end
        local key = MobKey(guid, name)
        local needed, isNamed, seen = NeedsForQuest(unit, name, key)
        if needed == nil and guid and questCache[guid] then
            needed, isNamed = questCache[guid][1], questCache[guid][2]   -- hidden right now: keep what we knew
        elseif needed ~= nil and guid then
            questCache[guid] = { needed, isNamed }
        end
        Learn(key, seen)
        if name and key ~= ("n:" .. name) then
            Learn("n:" .. name, seen)
            -- Mob types learned by ID only (before 1.6.12): add the name too.
            local byId = db.learned and db.learned[key]
            if byId then
                db.learned["n:" .. name] = db.learned["n:" .. name] or {}
                for item in pairs(byId) do db.learned["n:" .. name][item] = true end
            end
        end
        local logNeeded, logNamed = NeedsFromLog(name, key)
        lastWhy.name, lastWhy.guid, lastWhy.key = name, guid, key
        lastWhy.tip, lastWhy.log = needed, logNeeded
        quest = (needed or logNeeded) and true or false
        named = quest and (isNamed or logNamed) and true or false
    end

    if rare then AlertRare(unit, guid) end
    return rare, quest, named, elite
end

-- The color for a unit's name, or nil to leave it as it is. Rare wins, then named.
local function NameColor(unit)
    local rare, quest, named = Classify(unit)
    return (rare and COLORS.rare) or (named and COLORS.named) or (quest and COLORS.quest) or nil
end

local function IsTarget(unit)
    local ok, same = pcall(UnitIsUnit, unit, "target")
    return ok and Readable(same) and same or false
end

-- Your target's slim bars. WoW Forever may hide exact numbers from addons;
-- the bars accept them anyway, and anything that can't be read falls back to a
-- full bar rather than an error.
local function UpdateTargetHealth(o)
    local ok = pcall(function()
        o.hp:SetMinMaxValues(0, UnitHealthMax("target"))
        o.hp:SetValue(UnitHealth("target"))
    end)
    if not ok then o.hp:SetMinMaxValues(0, 1); o.hp:SetValue(1) end
end

local function StopCast(o)
    o.cast:SetScript("OnUpdate", nil)
    o.cast:Hide()
end

-- Progress for the cast bar. WoW Forever hides cast timings from addons, so
-- the bar is driven without reading them, trying in order:
--   1. a sealed cast timer from the game (UnitCastingDuration), played by the bar
--   2. copying the fill of Blizzard's own target cast bar every frame (hidden
--      values can be passed from one bar to another without being read)
--   3. the cast's start and end times, when the game does share them
local TIMER_ELAPSED = Enum and Enum.StatusBarTimerDirection and Enum.StatusBarTimerDirection.ElapsedTime
local TIMER_REMAINING = Enum and Enum.StatusBarTimerDirection and Enum.StatusBarTimerDirection.RemainingTime
local TIMER_SMOOTH = Enum and Enum.StatusBarInterpolation and Enum.StatusBarInterpolation.Immediate

local function DriveBySealedTimer(o, channel)
    local getter = channel and UnitChannelDuration or UnitCastingDuration
    if not (getter and o.cast.SetTimerDuration) then return false end
    local ok = pcall(function()
        local duration = getter("target")
        if not duration then error("no timer") end
        o.cast:SetTimerDuration(duration, TIMER_SMOOTH, channel and TIMER_REMAINING or TIMER_ELAPSED)
    end)
    return ok
end

local function DriveByBlizzardBar(o)
    local blizz = TargetFrameSpellBar
    if not (blizz and blizz.GetValue and blizz.GetMinMaxValues) then return false end
    local function Copy()
        o.cast:SetMinMaxValues(blizz:GetMinMaxValues())
        o.cast:SetValue(blizz:GetValue())
    end
    if not pcall(Copy) then return false end
    o.cast:SetScript("OnUpdate", function()
        if not blizz:IsShown() or not pcall(Copy) then StopCast(o) end
    end)
    return true
end

local function DriveByTimes(o, startMS, endMS, channel)
    if not (Readable(startMS) and Readable(endMS) and endMS > startMS) then return false end
    o.cast:SetMinMaxValues(startMS, endMS)
    o.cast:SetScript("OnUpdate", function(self)
        local now = GetTime() * 1000
        if now >= endMS then StopCast(o); return end
        -- Casts fill up; channels drain.
        self:SetValue(channel and (startMS + endMS - now) or now)
    end)
    return true
end

local function UpdateTargetCast(o)
    local name, _, _, startMS, endMS = UnitCastingInfo("target")
    local channel = false
    if not name and UnitChannelInfo then
        name, _, _, startMS, endMS = UnitChannelInfo("target")
        channel = name ~= nil
    end
    if not name then StopCast(o); return end
    o.cast.text:SetText(name)
    if channel then o.cast:SetStatusBarColor(0.3, 1, 0.3) else o.cast:SetStatusBarColor(1, 0.69, 0) end
    o.cast:SetScript("OnUpdate", nil)
    o.cast:Show()
    o.castMethod = (DriveBySealedTimer(o, channel) and "timer")
        or (DriveByBlizzardBar(o) and "blizzard")
        or (DriveByTimes(o, startMS, endMS, channel) and "times")
        or "none"
    if o.castMethod == "none" then
        o.cast:SetMinMaxValues(0, 1)
        o.cast:SetValue(1)
    end
end

-- Shows (or hides) the target bars, under the given text.
local function TargetBars(o, unit, under, color)
    if not under then
        o.hp:Hide()
        StopCast(o)
        return
    end
    o.hp:ClearAllPoints()
    o.hp:SetPoint("TOP", under, "BOTTOM", 0, -2)
    o.hp:SetStatusBarColor(color[1], color[2], color[3])
    o.hp:Show()
    UpdateTargetHealth(o)
    UpdateTargetCast(o)
end

-- Rare Radar look for one plate. Returns false when the plate should keep the
-- normal look instead (players, friendly NPCs).
local function RadarPlate(plate, o, unit, rare, quest, named, elite)
    local b = o.beacon
    if not db.radar or Flag(UnitCanAttack, "player", unit) == false or Flag(UnitIsPlayer, unit) then
        return false
    end
    o.box:Hide()
    o.label:Hide()
    if rare then
        HideBlizzardPlate(plate, true)
        o.radarName:Hide()
        local name = UnitName(unit)
        b.name:SetText(Readable(name) and name or "Rare")
        local level = UnitLevel(unit)
        local lvl = (Readable(level) and level and level > 0) and ("  " .. level) or "  ??"
        b.sub:SetText((elite and "RARE ELITE" or "RARE") .. lvl
            .. (quest and "  |cff8acff0QUEST|r" or ""))
        b.sub:SetTextColor(elite and 1 or 0.85, elite and 0.25 or 0.85, elite and 0.2 or 0.85)
        b:Show()
        if not b.pulse:IsPlaying() then b.pulse:Play() end
        TargetBars(o, unit, IsTarget(unit) and b.sub or nil, COLORS.rare)
        o:Show()
        return true
    end
    b.pulse:Stop()
    b:Hide()
    HideBlizzardPlate(plate, true)
    local target = IsTarget(unit)
    local color = (named and COLORS.named) or (quest and COLORS.quest) or ReactionColor(unit)
    local alpha = (quest or target) and 1 or (db.others or 1)   -- your target's name always shows
    local name = UnitName(unit)
    if alpha <= 0 or not Readable(name) then
        o.radarName:Hide()
    else
        o.radarName:SetText(name)
        o.radarName:SetTextColor(color[1], color[2], color[3])
        o.radarName:SetAlpha(alpha)
        o.radarName:Show()
    end
    TargetBars(o, unit, target and o.radarName or nil, ReactionColor(unit))
    o:Show()
    return true
end

local function UpdatePlate(unit)
    local plate = C_NamePlate.GetNamePlateForUnit(unit)
    if not plate or (plate.IsForbidden and plate:IsForbidden()) then return end
    local o = GetOverlay(plate)
    o.dbgTime = GetTime()
    local rare, quest, named, elite = Classify(unit)
    o.dbgWhy = { rare = rare, quest = quest, named = named, lines = lastWhy.lines, tip = lastWhy.tip,
        log = lastWhy.log, name = lastWhy.name, guid = lastWhy.guid ~= nil, key = lastWhy.key }
    if RadarPlate(plate, o, unit, rare, quest, named, elite) then return end

    -- Normal look: Blizzard's plate, with an outline on quest mobs and rares.
    HideBlizzardPlate(plate, false)
    TargetBars(o, unit, nil)
    o.radarName:Hide()
    o.beacon.pulse:Stop()
    o.beacon:Hide()
    o.box:Show()
    o.label:Show()
    if rare and quest then
        Paint(o, COLORS.rare, "RARE  |cff8acff0QUEST|r")
    elseif rare then
        Paint(o, COLORS.rare, "RARE")
    elseif named then
        Paint(o, COLORS.named, "QUEST")
    elseif quest then
        Paint(o, COLORS.quest, "QUEST")
    else
        o:Hide()
    end
end

-- ==========================================
-- NAMES ON UNIT FRAMES AND THE TOOLTIP
-- ==========================================

-- The name text on each unit frame (names differ between WoW versions).
local function Content(frame)
    local c = frame and frame.TargetFrameContent
    return c and c.TargetFrameContentMain
end
local NAME_TEXT = {
    target = function()
        return (TargetFrame and (TargetFrame.name or (Content(TargetFrame) and Content(TargetFrame).Name)))
            or _G.TargetFrameTextureFrameName
    end,
    targettarget = function()
        return (TargetFrameToT and (TargetFrameToT.name or TargetFrameToT.Name)) or _G.TargetFrameToTTextureFrameName
    end,
    focus = function()
        return (FocusFrame and (FocusFrame.name or (Content(FocusFrame) and Content(FocusFrame).Name)))
            or _G.FocusFrameTextureFrameName
    end,
}

local blizzardColor = {}   -- name text -> the color Blizzard last gave it
local painting = false
local ColorName

local function SetColor(text, color)
    painting = true
    text:SetTextColor(color[1], color[2], color[3])
    painting = false
end

ColorName = function(unit)
    local text = NAME_TEXT[unit] and NAME_TEXT[unit]()
    if not text or not text.SetTextColor then return end
    if not blizzardColor[text] then
        blizzardColor[text] = { text:GetTextColor() }
        -- If Blizzard recolors the name later, remember that and put ours back on top.
        hooksecurefunc(text, "SetTextColor", function(self, r, g, b)
            if painting then return end
            blizzardColor[self] = { r, g, b }
            ColorName(unit)
        end)
    end
    SetColor(text, NameColor(unit) or blizzardColor[text])
end

local function ColorAllNames()
    for unit in pairs(NAME_TEXT) do ColorName(unit) end
end

-- Mouseover tooltip: recolor the name on its first line.
local function ColorTooltip(tooltip)
    if tooltip ~= GameTooltip or not db then return end
    local _, unit = tooltip:GetUnit()
    if not Readable(unit) then return end
    local color = NameColor(unit)
    local line = _G.GameTooltipTextLeft1
    if color and line then line:SetTextColor(color[1], color[2], color[3]) end
end

if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall and Enum.TooltipDataType then
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Unit, ColorTooltip)
else
    GameTooltip:HookScript("OnTooltipSetUnit", ColorTooltip)
end

local lastPlateError   -- for /qm debug
local function UpdateAllPlates()
    if not db then return end
    for _, plate in ipairs(C_NamePlate.GetNamePlates() or {}) do
        local unit = plate.namePlateUnitToken or (plate.UnitFrame and plate.UnitFrame.unit)
        -- One plate going wrong must not stop the rest from being updated.
        if unit then
            local ok, err = pcall(UpdatePlate, unit)
            if not ok then lastPlateError = tostring(unit) .. ": " .. tostring(err) end
        end
    end
end

-- ==========================================
-- ONE-TIME CLEANUP FROM THE CLEAN NAMEPLATES VERSION
-- ==========================================
-- Version 1.4.x changed four of WoW's nameplate size settings (CVars) and kept
-- your original values in db.savedCVars. Put them back once, then forget them.
-- They can't be changed in combat, so this waits until combat ends if needed.
local function RestoreOldSettings()
    if not db.savedCVars then return true end
    if InCombatLockdown() then return false end
    local set = (C_CVar and C_CVar.SetCVar) or SetCVar
    if set then
        for name, value in pairs(db.savedCVars) do pcall(set, name, tostring(value)) end
    end
    db.savedCVars = nil
    return true
end

-- ==========================================
-- RARE RADAR RANGE
-- ==========================================
-- While Rare Radar is on, the nameplate range is raised to the most the game
-- allows, so rares are found from farther away. Your old value is kept in
-- db.radarDistance and put back when Rare Radar is turned off. WoW doesn't
-- allow this in combat, so a change then waits until combat ends.
local function GetSetting(name)
    local get = (C_CVar and C_CVar.GetCVar) or GetCVar
    if not get then return nil end
    local ok, v = pcall(get, name)
    return ok and v or nil
end

local function SetSetting(name, value)
    local set = (C_CVar and C_CVar.SetCVar) or SetCVar
    if set then pcall(set, name, tostring(value)) end
end

local function ApplyRadarRange()
    if InCombatLockdown() then return false end
    if db.radar then
        if db.radarDistance == nil then
            db.radarDistance = GetSetting("nameplateMaxDistance") or false
        end
        SetSetting("nameplateMaxDistance", RADAR_DISTANCE)
    elseif db.radarDistance ~= nil then
        if db.radarDistance then SetSetting("nameplateMaxDistance", db.radarDistance) end
        db.radarDistance = nil
    end
    return true
end

local function NameplatesOn()
    return GetSetting("nameplateShowEnemies") == "1"
end

-- ==========================================
-- EVENTS
-- ==========================================

local events = CreateFrame("Frame")
-- Events this game version doesn't have are skipped (registering an unknown
-- event is an error that would stop the addon from loading).
for _, event in ipairs({ "ADDON_LOADED", "PLAYER_LOGIN", "NAME_PLATE_UNIT_ADDED", "NAME_PLATE_UNIT_REMOVED", "QUEST_LOG_UPDATE", "UNIT_QUEST_LOG_CHANGED", "PLAYER_REGEN_ENABLED", "PLAYER_TARGET_CHANGED", "PLAYER_FOCUS_CHANGED", "UNIT_TARGET", "UNIT_NAME_UPDATE", "UNIT_CLASSIFICATION_CHANGED", "UNIT_HEALTH", "UNIT_MAXHEALTH", "UNIT_SPELLCAST_START", "UNIT_SPELLCAST_STOP", "UNIT_SPELLCAST_FAILED", "UNIT_SPELLCAST_INTERRUPTED", "UNIT_SPELLCAST_DELAYED", "UNIT_SPELLCAST_CHANNEL_START", "UNIT_SPELLCAST_CHANNEL_UPDATE", "UNIT_SPELLCAST_CHANNEL_STOP" }) do
    pcall(events.RegisterEvent, events, event)
end

local refreshPending = false
local restorePending = false
local rangePending = false
local function RefreshSoon()
    if refreshPending then return end
    refreshPending = true
    C_Timer.After(0.3, function()
        refreshPending = false
        UpdateAllPlates()
        ColorAllNames()
    end)
end

OnLearned = RefreshSoon

-- Every 2 seconds, go over the plates again: a plate that couldn't be read
-- the moment it appeared (or whose mob changed) gets fixed instead of
-- keeping Blizzard's look.
local sweep = CreateFrame("Frame")
local sweepTime = 0
sweep:SetScript("OnUpdate", function(_, dt)
    sweepTime = sweepTime + dt
    if sweepTime < 2 then return end
    sweepTime = 0
    if not db or not db.radar then return end
    for _, plate in ipairs(C_NamePlate.GetNamePlates() or {}) do
        local unit = plate.namePlateUnitToken or (plate.UnitFrame and plate.UnitFrame.unit)
        if unit then
            local ok, err = pcall(UpdatePlate, unit)
            if not ok then lastPlateError = tostring(unit) .. ": " .. tostring(err) end
        end
    end
end)

events:SetScript("OnEvent", function(self, event, arg1)
    if event == "ADDON_LOADED" then
        if arg1 == ADDON_NAME then
            LoadSettings()
            self:UnregisterEvent("ADDON_LOADED")
            for _, key in ipairs(RETIRED) do db[key] = nil end
            restorePending = not RestoreOldSettings()
            rangePending = not ApplyRadarRange()
        end
    elseif event == "PLAYER_LOGIN" then
        if db and db.radar and not NameplatesOn() then
            print("|cffff8000AetherMarks:|r Rare Radar needs enemy nameplates. Press V to turn them on.")
        end
    elseif not db then
        return
    elseif event == "NAME_PLATE_UNIT_ADDED" then
        local ok, err = pcall(UpdatePlate, arg1)
        if not ok then
            lastPlateError = arg1 .. ": " .. tostring(err)
            geterrorhandler()(err)
        end
    elseif event == "NAME_PLATE_UNIT_REMOVED" then
        local plate = C_NamePlate.GetNamePlateForUnit(arg1)
        if plate and overlays[plate] then
            overlays[plate].beacon.pulse:Stop()
            overlays[plate]:Hide()
        end
        if plate then HideBlizzardPlate(plate, false) end   -- plates are reused for other mobs
    elseif event == "PLAYER_TARGET_CHANGED" then
        ColorName("target"); ColorName("targettarget")
        if db.radar then UpdateAllPlates() end   -- your target gets its slim bars
    elseif event == "PLAYER_FOCUS_CHANGED" then
        ColorName("focus")
    elseif event == "UNIT_TARGET" then
        if arg1 == "target" then ColorName("targettarget") end
    elseif event == "UNIT_HEALTH" or event == "UNIT_MAXHEALTH" or event:find("^UNIT_SPELLCAST") then
        if arg1 ~= "target" then return end
        local plate = C_NamePlate.GetNamePlateForUnit("target")
        local o = plate and overlays[plate]
        if o and o.hp:IsShown() then
            if event:find("^UNIT_SPELLCAST") then UpdateTargetCast(o) else UpdateTargetHealth(o) end
        end
    elseif event == "UNIT_NAME_UPDATE" or event == "UNIT_CLASSIFICATION_CHANGED" then
        if NAME_TEXT[arg1] then ColorName(arg1) end
    else
        -- Quest progress changed, or combat ended and tooltips are readable again.
        if event == "PLAYER_REGEN_ENABLED" and restorePending then restorePending = not RestoreOldSettings() end
        if event == "PLAYER_REGEN_ENABLED" and rangePending then rangePending = not ApplyRadarRange() end
        wipe(questCache); questDirty = true
        RefreshSoon()
    end
end)

-- ==========================================
-- SLASH COMMANDS
-- ==========================================

SLASH_AETHERMARKS1 = "/qm"
SLASH_AETHERMARKS2 = "/aethermarks"

local function OnOff(v) return v and "|cff33dd66on|r" or "|cffff5555off|r" end

SlashCmdList["AETHERMARKS"] = function(msg)
    if not db then return end
    local command = (msg:match("^(%S*)") or ""):lower()
    local prefix = "|cffff8000AetherMarks:|r "

    if command == "quest" or command == "rare" or command == "sound" or command == "radar" then
        local key = (command == "sound") and "rareSound" or command
        db[key] = not db[key]
        print(prefix .. command .. " " .. OnOff(db[key]))
        if command == "radar" then
            rangePending = not ApplyRadarRange()
            if rangePending then print(prefix .. "the nameplate range changes when combat ends.") end
            if db.radar and not NameplatesOn() then
                print(prefix .. "Rare Radar needs enemy nameplates. Press V to turn them on.")
            end
        end
        wipe(questCache); questDirty = true
        UpdateAllPlates()
        ColorAllNames()
    elseif command == "defaults" then
        for k, v in pairs(DEFAULTS) do db[k] = v end
        rangePending = not ApplyRadarRange()
        wipe(questCache); questDirty = true
        UpdateAllPlates()
        ColorAllNames()
        print(prefix .. "settings back to their defaults.")
    elseif command == "debug" then
        local function yn(v) return v == nil and "?" or (v and "yes" or "no") end
        local plates = C_NamePlate.GetNamePlates() or {}
        print(prefix .. "debug: " .. #plates .. " nameplates, radar " .. OnOff(db.radar)
            .. ", range " .. tostring(((C_CVar and C_CVar.GetCVar) or GetCVar)("nameplateMaxDistance"))
            .. ", in combat " .. yn(InCombatLockdown()))
        if questDirty then BuildQuestIndex() end
        local kills, items = {}, {}
        for k, n in pairs(questIndex.kills) do kills[#kills + 1] = k .. " (" .. n .. ")" end
        for k, n in pairs(questIndex.items) do items[#items + 1] = k .. " (" .. n .. ")" end
        print("  quest log kills: " .. (#kills > 0 and table.concat(kills, ", ") or "none"))
        print("  quest log items: " .. (#items > 0 and table.concat(items, ", ") or "none"))
        for i, plate in ipairs(plates) do
            local unit = plate.namePlateUnitToken or (plate.UnitFrame and plate.UnitFrame.unit)
            local o = overlays[plate]
            local uf = plate.UnitFrame
            local line = "  " .. i .. ". " .. tostring(unit)
            if plate.IsForbidden and plate:IsForbidden() then
                line = line .. " FORBIDDEN (Blizzard-only plate)"
            elseif not o then
                line = line .. " no AetherMarks label yet"
            else
                local w = o.dbgWhy or {}
                local okN, liveName = pcall(UnitName, unit or "none")
                liveName = (okN and Readable(liveName)) and liveName or "hidden"
                line = line .. " '" .. liveName .. "'"
                    .. " | label " .. (o:IsShown() and (o.radarName:IsShown() and "name" or (o.beacon:IsShown() and "beacon" or "empty")) or "off")
                    .. " | color " .. (w.rare and "orange" or w.named and "purple" or w.quest and "blue" or "default")
                    .. " (tooltip " .. yn(w.tip) .. " " .. tostring(w.lines or "?") .. " lines, log " .. yn(w.log)
                    .. ", name " .. (w.name and "ok" or "hidden") .. ", id " .. (w.guid and "ok" or "hidden") .. ")"
                    .. " | checked " .. (o.dbgTime and string.format("%.0fs ago", GetTime() - o.dbgTime) or "never")
            end
            if uf then
                local okA, a = pcall(uf.GetAlpha, uf)
                line = line .. " | Blizzard plate " .. ((uf.IsForbidden and uf:IsForbidden()) and "forbidden"
                    or ("alpha " .. ((okA and Readable(a)) and string.format("%.1f", a) or "?")))
            else
                line = line .. " | no Blizzard UnitFrame"
            end
            print(line)
        end
        if lastPlateError then print("  last plate error: " .. lastPlateError) end
    elseif command == "names" then
        local pct = tonumber(msg:match("^%S+%s+(%d+)"))
        if pct then
            db.others = math.max(0, math.min(100, pct)) / 100
            print(prefix .. "other mobs' names at " .. math.floor(db.others * 100 + 0.5) .. "% (0 hides them).")
            UpdateAllPlates()
        else
            print(prefix .. "/qm names 50 sets how visible ordinary mobs' names are with Rare Radar"
                .. " (0 hides them, 100 is full; now " .. math.floor((db.others or 1) * 100 + 0.5) .. ").")
        end
    else
        print(prefix .. "quest " .. OnOff(db.quest) .. ", rare " .. OnOff(db.rare)
            .. ", sound " .. OnOff(db.rareSound) .. ", radar " .. OnOff(db.radar)
            .. ", names " .. math.floor((db.others or 1) * 100 + 0.5) .. "%")
        print(prefix .. "/qm quest, /qm rare, /qm sound, /qm radar turn each one on or off;"
            .. " /qm names 0-100 sets ordinary mobs' names with Rare Radar.")
    end
end
