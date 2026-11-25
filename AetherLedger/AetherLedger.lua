-- ==========================================
-- AetherLedger - quest log export for WoW Forever
-- Records each character's current quest log (with objectives and progress)
-- and the IDs of the quests they've completed into
-- WTF\Account\<ACCOUNT>\SavedVariables\AetherLedger.lua.
-- WoW writes that file when you log out or type /reload.
-- Read-only: it never accepts, abandons or changes quests.
--
-- Zone suggestions: using quest data from QuestieDB (AetherLedger_Data.lua),
-- it works out which quests you could pick up right now (your level, race,
-- class and faction, prerequisites done, not already done or in your log),
-- scores each zone by how many of them suit your level (chains that keep
-- going past your level count extra), and suggests moving when another zone
-- is clearly better than the one you're in. It rechecks only when something
-- changes: you level up, accept or turn in a quest, or change zones.
-- ==========================================

-- ==========================================
-- AETHER TEXT
-- ==========================================
-- The Aether text style, in Fira Sans (the unit frames' font; SIL Open Font
-- License, see AetherHub\Media\Fonts\FiraSans-OFL.txt). In windows: Regular
-- for text, SemiBold for the gold headings, with a soft shadow. Over the game
-- world (AetherFontWorld...): Bold with a thin black outline and a shadow, so
-- it reads on any background, faded or not. Each copies the Blizzard font it
-- stands in for (size, color), so layouts stay the same, except that the gold
-- ones use the Aether gold (a warm amber, 1, 0.69, 0) instead of Blizzard's
-- yellow. The files live in AetherHub\Media\Fonts; if one can't load,
-- Blizzard's font stays.
AETHER_FONT_DIR = AETHER_FONT_DIR or "Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-"
local function AetherFontFile(weight) return AETHER_FONT_DIR .. weight .. ".ttf" end

-- Sets a Fira font on a font object or font string; false if it didn't load.
local function AetherSetFont(obj, weight, size, outline)
    local ok, set = pcall(obj.SetFont, obj, AetherFontFile(weight), size, outline and "OUTLINE" or "")
    return ok and set ~= false
end

if CreateFont and not AetherFontHighlight then
    -- Fira's capitals are a little shorter than Friz Quadrata's at the same size.
    local SCALE = 1.05
    local function Make(name, base, weight, world, gold)
        local f = CreateFont(name)
        local src = _G[base]
        if src then f:CopyFontObject(src) end
        local file, size, flags = f:GetFont()
        size = size or 12
        if not AetherSetFont(f, weight, size * SCALE, world) and file then
            f:SetFont(file, size, flags or "")
        end
        f:SetShadowColor(0, 0, 0, world and 1 or 0.8)
        f:SetShadowOffset(1, -1)
        if gold then f:SetTextColor(1, 0.69, 0) end
    end
    for _, d in ipairs({
        { "AetherFontNormal",           "GameFontNormal",         "SemiBold", false, true },
        { "AetherFontNormalSmall",      "GameFontNormalSmall",    "SemiBold", false, true },
        { "AetherFontNormalLarge",      "GameFontNormalLarge",    "SemiBold", false, true },
        { "AetherFontNormalHuge",       "GameFontNormalHuge",     "SemiBold", false, true },
        { "AetherFontHighlight",        "GameFontHighlight",      "Regular" },
        { "AetherFontHighlightSmall",   "GameFontHighlightSmall", "Regular" },
        { "AetherFontDisable",          "GameFontDisable",        "Regular" },
        { "AetherFontDisableSmall",     "GameFontDisableSmall",   "Regular" },
        { "AetherFontWorldNormal",      "GameFontNormal",         "Bold", true, true },
        { "AetherFontWorldNormalSmall", "GameFontNormalSmall",    "Bold", true, true },
        { "AetherFontWorld",            "GameFontHighlight",      "Bold", true },
        { "AetherFontWorldSmall",       "GameFontHighlightSmall", "Bold", true },
    }) do Make(d[1], d[2], d[3], d[4], d[5]) end
end

local PREFIX = "|cff4da6ffAetherLedger:|r "

local function CharKey()
    local name = UnitName("player") or "Unknown"
    local realm = (GetRealmName and GetRealmName()) or ""
    if realm ~= "" then
        return name .. "-" .. realm
    end
    return name
end

local function TitleForID(id)
    if C_QuestLog and C_QuestLog.GetTitleForQuestID then
        local ok, title = pcall(C_QuestLog.GetTitleForQuestID, id)
        if ok then return title end
    end
    return nil
end

-- ==========================================
-- COMPLETED QUESTS
-- ==========================================

local function CollectCompleted()
    local ids = {}
    if C_QuestLog and C_QuestLog.GetAllCompletedQuestIDs then
        local ok, list = pcall(C_QuestLog.GetAllCompletedQuestIDs)
        if ok and type(list) == "table" then
            for _, id in ipairs(list) do ids[#ids + 1] = id end
        end
    end
    if #ids == 0 and GetQuestsCompleted then
        local ok, t = pcall(GetQuestsCompleted)
        if ok and type(t) == "table" then
            for id in pairs(t) do ids[#ids + 1] = id end
        end
    end
    table.sort(ids)

    local out = {}
    for _, id in ipairs(ids) do
        out[#out + 1] = { id = id, title = TitleForID(id) }
    end
    return out
end

-- ==========================================
-- QUEST LOG
-- ==========================================

-- Collapsed zone headers hide their quests from addons, so open them all.
local function ExpandAllHeaders()
    if ExpandQuestHeader then
        pcall(ExpandQuestHeader, 0)
    end
end

local function GetObjectives(logIndex, questID)
    local objs = {}
    if questID and C_QuestLog and C_QuestLog.GetQuestObjectives then
        local ok, list = pcall(C_QuestLog.GetQuestObjectives, questID)
        if ok and type(list) == "table" and #list > 0 then
            for _, o in ipairs(list) do
                objs[#objs + 1] = { text = o.text, done = o.finished and true or false }
            end
            return objs
        end
    end
    if GetNumQuestLeaderBoards and GetQuestLogLeaderBoard then
        local ok, n = pcall(GetNumQuestLeaderBoards, logIndex)
        if ok and n then
            for j = 1, n do
                local ok2, text, _, finished = pcall(GetQuestLogLeaderBoard, j, logIndex)
                if ok2 and text then
                    objs[#objs + 1] = { text = text, done = finished and true or false }
                end
            end
        end
    end
    return objs
end

local function CollectQuestLog(keepHeaders)
    if not keepHeaders then ExpandAllHeaders() end
    local quests = {}
    local currentHeader = nil

    local n = 0
    if C_QuestLog and C_QuestLog.GetNumQuestLogEntries then
        n = C_QuestLog.GetNumQuestLogEntries() or 0
    elseif GetNumQuestLogEntries then
        n = GetNumQuestLogEntries() or 0
    end

    for i = 1, n do
        local title, level, isHeader, isComplete, questID, suggestedGroup

        if C_QuestLog and C_QuestLog.GetInfo then
            local info = C_QuestLog.GetInfo(i)
            if info then
                title = info.title
                level = info.level
                isHeader = info.isHeader
                questID = info.questID
                suggestedGroup = info.suggestedGroup
                if questID and C_QuestLog.IsComplete then
                    isComplete = C_QuestLog.IsComplete(questID)
                end
            end
        elseif GetQuestLogTitle then
            local t, lvl, grp, hdr, _, complete, _, id = GetQuestLogTitle(i)
            title, level, suggestedGroup, isHeader, isComplete, questID = t, lvl, grp, hdr, complete, id
        end

        if title then
            if isHeader then
                currentHeader = title
            else
                quests[#quests + 1] = {
                    title = title,
                    id = questID,
                    level = level,
                    zone = currentHeader,
                    group = (suggestedGroup and suggestedGroup > 0) and suggestedGroup or nil,
                    -- true = ready to turn in, "failed" = failed
                    complete = (isComplete == 1 or isComplete == true) and true
                        or (isComplete == -1 and "failed") or false,
                    objectives = GetObjectives(i, questID),
                }
            end
        end
    end
    return quests
end

-- ==========================================
-- SNAPSHOT
-- ==========================================

local function Snapshot()
    AetherLedgerDB = AetherLedgerDB or {}
    AetherLedgerDB.characters = AetherLedgerDB.characters or {}
    local _, class = UnitClass("player")
    local _, race = UnitRace("player")
    local entry = {
        exported = date("%Y-%m-%d %H:%M"),
        level = UnitLevel("player"),
        class = class,
        race = race,
        faction = UnitFactionGroup("player"),
        zone = GetRealZoneText and GetRealZoneText() or nil,
        questLog = CollectQuestLog(),
        completed = CollectCompleted(),
    }
    AetherLedgerDB.characters[CharKey()] = entry
    return entry
end

-- One line about this character's last recording (used by AetherHub too).
local function Status()
    local entry = AetherLedgerDB and AetherLedgerDB.characters and AetherLedgerDB.characters[CharKey()]
    if not entry then return "Nothing recorded yet for this character." end
    return string.format("Last recorded %s: %d quests in your log, %d completed.",
        entry.exported or "?", #(entry.questLog or {}), #(entry.completed or {}))
end

-- ==========================================
-- ZONE SUGGESTIONS
-- ==========================================

local DATA = AetherLedger_Data or {}

-- Field positions in AetherLedger_Data entries.
local NAME, REQ, LEVEL, MAP, X, Y, GIVER, SIDE, RACES, CLASSES, TOP, LEN, PRE_ANY, PRE_ALL, NOT_WITH =
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
local KIND, SKILL, SKILL_MIN = 16, 17, 18      -- "c" class quest / "p" profession quest
local SPECIAL_LOW = 10                         -- class/profession quests up to 10 levels below you still count

-- Quest givers who walk a route (AetherLedger_Routes, from QuestieDB): their
-- one spot in DATA is only somewhere on the way, so say they're on the move.
-- (Below the field names: above them GIVER was still nil, Nov 25 error.)
local function Moving(id) return AetherLedger_Routes and id and AetherLedger_Routes[id] ~= nil end
local function GiverText(id)
    local d = DATA[id]
    return tostring(d and d[GIVER] or "?") .. (Moving(id) and " (on the move)" or "")
end
AetherLedger_Moving = Moving


local BAND_LOW, BAND_HIGH = 2, 3      -- quests from your level -2 to +3 count
local MIN_SCORE = 4                   -- a zone needs at least this much to be suggested

local completed      -- set of completed quest IDs
local lastReport     -- result of the last check, for /ledger zones and AetherHub
local RankUpText     -- below

local function Settings()
    AetherLedgerDB = AetherLedgerDB or {}
    if AetherLedgerDB.suggest == nil then AetherLedgerDB.suggest = true end
    AetherLedgerDB.shown = AetherLedgerDB.shown or {}
    return AetherLedgerDB
end

-- Is bit number id (1 = first) set in mask? 0 or nil means "anyone".
-- (Masks go past 32 bits, so plain arithmetic instead of bit.band.)
local function HasBit(mask, id)
    if not mask or mask == 0 or not id then return true end
    return math.floor(mask / 2 ^ (id - 1)) % 2 == 1
end

local function LoadCompleted()
    completed = {}
    for _, q in ipairs(CollectCompleted()) do completed[q.id] = true end
end

local function MapName(map)
    local info = C_Map and C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    return info and info.name or ("map " .. tostring(map))
end

-- The zone you're in (towns, caves and buildings roll up to their zone).
local function CurrentZone()
    if not (C_Map and C_Map.GetBestMapForUnit) then return nil end
    local map = C_Map.GetBestMapForUnit("player")
    for _ = 1, 5 do
        local info = map and C_Map.GetMapInfo(map)
        if not info or not info.mapType or info.mapType <= 3 or not info.parentMapID or info.parentMapID == 0 then break end
        map = info.parentMapID
    end
    return map
end

local zoneByName   -- zone name -> map, for quest log headers
local function ZoneByName(name)
    if not zoneByName then
        zoneByName = {}
        for _, d in pairs(DATA) do
            if not zoneByName[d[MAP]] then zoneByName[MapName(d[MAP])] = d[MAP] end
        end
    end
    return name and zoneByName[name]
end

-- Quests in your log right now: id -> zone map (if known).
local function LogQuests()
    local log = {}
    pcall(function()
        for _, q in ipairs(CollectQuestLog(true)) do   -- leave your collapsed zones alone
            if q.id then
                local d = DATA[q.id]
                log[q.id] = { map = (d and d[MAP]) or ZoneByName(q.zone), level = q.level, done = q.complete == true }
            end
        end
    end)
    return log
end

local function Me()
    local _, _, raceID = UnitRace("player")
    local _, _, classID = UnitClass("player")
    local faction = UnitFactionGroup("player")
    return raceID, classID, faction == "Horde" and "H" or (faction == "Alliance" and "A" or nil)
end

local function AnyDone(list)
    for _, id in ipairs(list) do if completed[id] then return true end end
    return false
end

local function AllDone(list)
    for _, id in ipairs(list) do if not completed[id] then return false end end
    return true
end

local IsOnQuest = C_QuestLog and C_QuestLog.IsOnQuest

-- Can you pick this quest up right now? low/high: quest level window around yours.
local function Available(id, d, level, raceID, classID, side, log, low, high)
    if completed[id] or log[id] then return false end
    if d[REQ] > level or d[LEVEL] < level - (low or BAND_LOW) or d[LEVEL] > level + (high or BAND_HIGH) then return false end
    if side and d[SIDE] ~= "" and not d[SIDE]:find(side, 1, true) then return false end
    if not HasBit(d[RACES], raceID) or not HasBit(d[CLASSES], classID) then return false end
    if d[PRE_ANY] and not AnyDone(d[PRE_ANY]) then return false end
    if d[PRE_ALL] and not AllDone(d[PRE_ALL]) then return false end
    if d[NOT_WITH] then
        for _, other in ipairs(d[NOT_WITH]) do
            if completed[other] or log[other] then return false end
        end
    end
    -- Quests under a collapsed zone header aren't listed, so ask directly.
    if IsOnQuest then
        local ok, on = pcall(IsOnQuest, id)
        if ok and on then return false end
    end
    return true
end

local function Profile()
    return AetherHub_Profile and AetherHub_Profile.Get and AetherHub_Profile.Get()
end

local function Wants(key)
    return not (AetherHub_Profile and AetherHub_Profile.Interest) or AetherHub_Profile.Interest(key)
end

-- Skill by profession skill ID, from AetherHub's profile.
local function SkillRanks(profile)
    local ranks = {}
    for _, prof in ipairs(profile and profile.professions or {}) do ranks[prof.id] = prof.rank end
    return ranks
end

-- Profession rank-ups due: { prof, next } for each profession near its cap.
local function RankUps(profile)
    local list = {}
    if not (profile and AetherHub_Profile.NextRank) or not Wants("rankUps") then return list end
    for _, prof in ipairs(profile.professions) do
        local nextRank = AetherHub_Profile.NextRank(prof)
        if nextRank then list[#list + 1] = { prof = prof, next = nextRank } end
    end
    return list
end

-- Where to skin for skill-ups. Mobs you can skin go up to level skill/10+10
-- (below 100 skill) or skill/5; the ones near that limit give skill-ups.
local function SkinningSpots(profile, level)
    if not (AetherLedger_Skinning and Wants("skinning")) then return nil end
    local skinning
    for _, prof in ipairs(profile and profile.professions or {}) do
        if prof.key == "skinning" then skinning = prof end
    end
    if not skinning or skinning.rank >= 300 then return nil end
    local maxMob = skinning.rank < 100 and (math.floor(skinning.rank / 10) + 10) or math.floor(skinning.rank / 5)
    local low, high = maxMob - 5, math.min(maxMob, level + 2)
    local zones = {}
    for map, mobs in pairs(AetherLedger_Skinning) do
        local hits = {}
        for _, mob in ipairs(mobs) do
            if mob[2] >= low and mob[1] <= high then hits[#hits + 1] = mob end
        end
        if #hits > 0 then zones[#zones + 1] = { map = map, mobs = hits } end
    end
    table.sort(zones, function(a, b) return #a.mobs > #b.mobs end)
    return { rank = skinning.rank, max = skinning.max, maxMob = maxMob, zones = zones }
end

-- Scores every zone. Returns a report: { level, current, zones = { sorted by score } }.
local function Check(level)
    level = level or UnitLevel("player")
    if not completed then LoadCompleted() end
    local raceID, classID, side = Me()
    local log = LogQuests()
    local profile = Profile()
    local skills = SkillRanks(profile)
    local wantClass, wantProf = Wants("classQuests"), Wants("profQuests")
    local special = {}
    local zones = {}
    local function Zone(map)
        local z = zones[map]
        if not z then
            z = { map = map, score = 0, quests = {}, inLog = 0, chains = 0 }
            zones[map] = z
        end
        return z
    end

    for id, d in pairs(DATA) do
        local kind = d[KIND]
        if kind then
            -- Class and profession quests: listed on their own, not counted toward zones.
            local wanted = (kind == "c" and wantClass and d[CLASSES] ~= 0)
                or (kind == "p" and wantProf and skills[d[SKILL]] and skills[d[SKILL]] >= (d[SKILL_MIN] or 0))
            if wanted and Available(id, d, level, raceID, classID, side, log, SPECIAL_LOW, 5) then
                special[#special + 1] = id
            end
        elseif Available(id, d, level, raceID, classID, side, log) then
            local z = Zone(d[MAP])
            local weight = (d[LEVEL] >= level - 1 and d[LEVEL] <= level + 2) and 1 or 0.6
            local chain = d[LEN] > 1 and d[TOP] >= level + 4
            if chain then
                weight = weight + 0.5
                z.chains = z.chains + 1
            end
            z.score = z.score + weight
            z.quests[#z.quests + 1] = id
            z.lo = math.min(z.lo or 99, d[LEVEL])
            z.hi = math.max(z.hi or 0, d[LEVEL])
        end
    end
    -- Unfinished quests already in your log that suit your level pull toward their zone too.
    for _, q in pairs(log) do
        if q.map and not q.done and (q.level or 0) <= level + BAND_HIGH then
            local z = Zone(q.map)
            z.score = z.score + 0.5
            z.inLog = z.inLog + 1
        end
    end

    local list = {}
    for _, z in pairs(zones) do
        table.sort(z.quests, function(a, b)
            if DATA[a][LEVEL] ~= DATA[b][LEVEL] then return DATA[a][LEVEL] < DATA[b][LEVEL] end
            return DATA[a][NAME] < DATA[b][NAME]
        end)
        list[#list + 1] = z
    end
    table.sort(list, function(a, b) return a.score > b.score end)

    table.sort(special, function(a, b) return DATA[a][LEVEL] < DATA[b][LEVEL] end)
    local current = CurrentZone()
    local report = { level = level, current = current, zones = list, here = zones[current], special = special,
                     rankUps = RankUps(profile), skinning = SkinningSpots(profile, level) }
    local best = list[1]
    local hereScore = report.here and report.here.score or 0
    if best and best.map ~= current and best.score >= MIN_SCORE and best.score >= hereScore * 1.5 + 2 then
        report.suggest = best
    end
    lastReport = report
    return report
end

local function ZoneLine(z)
    local parts = { #z.quests .. " quest" .. (#z.quests == 1 and "" or "s") }
    if z.lo then parts[1] = parts[1] .. " (" .. (z.lo == z.hi and z.lo or (z.lo .. "-" .. z.hi)) .. ")" end
    if z.chains > 0 then parts[#parts + 1] = z.chains .. (z.chains == 1 and " chain that grows" or " chains that grow") .. " with you" end
    if z.inLog > 0 then parts[#parts + 1] = z.inLog .. " already in your log" end
    return MapName(z.map) .. ": " .. table.concat(parts, ", ")
end

-- Short version for buttons: "Desolace: 7 quests (33-35), 2 chains, 2 in your log"
local function ZoneShort(z)
    local text = MapName(z.map) .. ": " .. #z.quests .. (#z.quests == 1 and " quest" or " quests")
    if z.lo then text = text .. " (" .. (z.lo == z.hi and z.lo or (z.lo .. "-" .. z.hi)) .. ")" end
    if z.chains > 0 then text = text .. ", " .. z.chains .. (z.chains == 1 and " chain" or " chains") end
    if z.inLog > 0 then text = text .. ", " .. z.inLog .. " in your log" end
    return text
end

local function QuestLine(id)
    local d = DATA[id]
    local line = string.format("[%d] %s - %s (%.0f, %.0f)", d[LEVEL], d[NAME], GiverText(id), d[X], d[Y])
    if d[LEN] > 1 and d[TOP] > d[LEVEL] then line = line .. ", chain to " .. d[TOP] end
    return line
end

-- Nearest trainer that teaches the next rank (from AetherPathfinder's NPC data).
local function NearestTrainer(nextRank)
    if not (AetherPathfinder_API and AetherPathfinder_API.Trainers and nextRank.trainerWords) then return nil end
    local list = AetherPathfinder_API.Trainers(nextRank.trainerWords, nextRank.titleWords)
    local here = CurrentZone()
    local hereInfo = here and C_Map.GetMapInfo(here)
    local best, bestScore
    for _, t in ipairs(list) do
        -- Same zone first, then same continent, then anything.
        local info = C_Map.GetMapInfo(t.map)
        local score = (t.map == here and 0) or ((info and hereInfo and info.parentMapID == hereInfo.parentMapID) and 1) or 2
        if not bestScore or score < bestScore then best, bestScore = t, score end
    end
    return best
end

RankUpText = function(item, level)
    local prof, nextRank = item.prof, item.next
    local text = string.format("%s %d/%d: train %s", prof.name, prof.rank, prof.max, nextRank.name)
    if level < nextRank.level then text = text .. " once you're level " .. nextRank.level end
    if nextRank.fromBook then
        return text .. ". For " .. prof.name .. ", " .. nextRank.name .. " comes from a book or quest, not a trainer."
    end
    local trainer = NearestTrainer(nextRank)
    if trainer then
        text = text .. string.format(". Nearest: %s, %s in %s (%.0f, %.0f)", trainer.name, trainer.sub or "trainer",
            MapName(trainer.map), trainer.x * 100, trainer.y * 100)
    elseif nextRank.titleWords then
        text = text .. " (only some trainers teach it)"
    end
    return text .. "."
end

-- Text for AetherHub and /ledger zones.
-- The zones to choose from: the best three for you.
local selected = 1
local function Options()
    local list = {}
    local r = lastReport
    for i = 1, math.min(3, r and #r.zones or 0) do list[i] = r.zones[i] end
    if selected > #list then selected = 1 end
    return list
end

-- hub: leave out the zone list (AetherHub shows it as buttons).
local function Report(hub)
    if not lastReport then pcall(Check) end
    local r = lastReport
    if not r then return "Not checked yet." end
    local lines = {}
    local here = r.here
    lines[#lines + 1] = string.format("Level %d in %s: %s.", r.level, r.current and MapName(r.current) or "?",
        here and (#here.quests .. (#here.quests == 1 and " quest" or " quests") .. " to pick up here") or "nothing to pick up here")
    if not hub then
        lines[#lines + 1] = " "
        lines[#lines + 1] = "Best zones for you now:"
        for i = 1, math.min(3, #r.zones) do
            lines[#lines + 1] = "  " .. i .. ". " .. ZoneLine(r.zones[i])
        end
    end
    local top = Options()[selected] or r.zones[1]
    if top and #top.quests > 0 then
        lines[#lines + 1] = " "
        lines[#lines + 1] = "To pick up in " .. MapName(top.map) .. ":"
        for i = 1, math.min(10, #top.quests) do
            lines[#lines + 1] = "  " .. QuestLine(top.quests[i])
        end
        if #top.quests > 10 then lines[#lines + 1] = "  ...and " .. (#top.quests - 10) .. " more" end
    end
    for _, item in ipairs(r.rankUps or {}) do
        if #lines > 0 then lines[#lines + 1] = " " end
        lines[#lines + 1] = RankUpText(item, r.level)
    end
    if r.special and #r.special > 0 then
        lines[#lines + 1] = " "
        lines[#lines + 1] = "Class and profession quests:"
        for i = 1, math.min(8, #r.special) do
            local d = DATA[r.special[i]]
            lines[#lines + 1] = "  " .. QuestLine(r.special[i]) .. " in " .. MapName(d[MAP])
        end
        if #r.special > 8 then lines[#lines + 1] = "  ...and " .. (#r.special - 8) .. " more" end
    end
    local sk = r.skinning
    if sk then
        lines[#lines + 1] = " "
        lines[#lines + 1] = string.format("Skinning %d/%d: you can skin mobs up to level %d.", sk.rank, sk.max, sk.maxMob)
        if #sk.zones == 0 then
            lines[#lines + 1] = "  No known spot near your level; beasts close to level " .. sk.maxMob .. " give skill-ups."
        end
        for i = 1, math.min(3, #sk.zones) do
            local z, names = sk.zones[i], {}
            for j = 1, math.min(3, #z.mobs) do
                local mob = z.mobs[j]
                names[#names + 1] = mob[3] .. " (" .. (mob[1] == mob[2] and mob[1] or (mob[1] .. "-" .. mob[2])) .. ")"
            end
            lines[#lines + 1] = "  " .. MapName(z.map) .. ": " .. table.concat(names, ", ")
        end
    end
    return table.concat(lines, "\n")
end

-- ==========================================
-- AETHER LOOK
-- ==========================================
-- Navy buttons with a blue edge, so Aether windows are easy to tell apart from
-- Blizzard's. Plain colored textures only: nothing to load, nothing running.
local function AetherFill(button, r, g, b, a)
    local t = button:CreateTexture(nil, "BACKGROUND")
    t:SetColorTexture(r, g, b, a)
    t:SetPoint("TOPLEFT", 1, -1)
    t:SetPoint("BOTTOMRIGHT", -1, 1)
    return t
end

-- A button (use SetText/SetSize/SetScript as usual). small: smaller text.
local function AetherButton(parent, name, small)
    local b = CreateFrame("Button", name, parent, "BackdropTemplate")
    b:SetSize(100, 22)
    if b.SetBackdrop then
        b:SetBackdrop({ edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        b:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    b:SetNormalTexture(AetherFill(b, 0.07, 0.17, 0.32, 0.95))
    b:SetPushedTexture(AetherFill(b, 0.03, 0.09, 0.19, 0.95))
    b:SetDisabledTexture(AetherFill(b, 0.13, 0.13, 0.15, 0.9))
    local hl = AetherFill(b, 0.3, 0.65, 1, 0.3)
    hl:SetBlendMode("ADD")
    b:SetHighlightTexture(hl)
    b:SetNormalFontObject(small and "AetherFontHighlightSmall" or "AetherFontHighlight")
    b:SetHighlightFontObject(small and "AetherFontHighlightSmall" or "AetherFontHighlight")
    b:SetDisabledFontObject(small and "AetherFontDisableSmall" or "AetherFontDisable")
    b:SetText(" ")
    return b
end

-- A small square close button that hides its parent (set OnClick to change that).
local function AetherClose(parent)
    local b = AetherButton(parent, nil, true)
    b:SetSize(18, 18)
    b:SetText("x")
    b:SetPoint("TOPRIGHT", parent, "TOPRIGHT", -6, -6)
    b:SetScript("OnClick", function() parent:Hide() end)
    return b
end

-- Aether window trim: a double blue frame with a soft halo, gold corner
-- brackets, a title strip with a gold underline, and a small gold gem at the
-- top center. Plain colored textures only. titleHeight 0 = no title strip.
local function AetherDecorate(frame, titleHeight)
    if frame.aetherTrim then return end
    frame.aetherTrim = true
    -- The Aether window look: rounded corners, a blue edge with a fine inner
    -- line, a soft blue glow, a navy title strip with a gold underline, and
    -- gold chevrons at 12, 3, 6 and 9. Smooth images (Media\win_*), so it
    -- stays crisp at any UI scale.
    local MEDIA, WHITE = "Interface\\AddOns\\AetherLedger\\Media\\", "Interface\\Buttons\\WHITE8X8"
    local R, IN, GLOW = 8, 3, 6.7          -- corner radius, inner line inset, glow width
    local function Tex(layer, sub, file, c)
        local t = frame:CreateTexture(nil, layer, nil, sub)
        t:SetTexture(file)
        t:SetVertexColor(c[1], c[2], c[3], c[4] or 1)
        if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false); t:SetTexelSnappingBias(0) end
        return t
    end
    -- corner images are drawn as the top-left corner; flip them for the others
    local FLIP = { TOPLEFT = { 0, 1, 0, 1 }, TOPRIGHT = { 1, 0, 0, 1 }, BOTTOMLEFT = { 0, 1, 1, 0 }, BOTTOMRIGHT = { 1, 0, 1, 0 } }
    local CORNERS = { "TOPLEFT", "TOPRIGHT", "BOTTOMLEFT", "BOTTOMRIGHT" }
    -- A rounded shape: a corner image at each corner, plus straight pieces.
    -- line = thickness for an outline (nil: a solid fill); inset = distance in.
    local function Shape(layer, sub, file, color, inset, line)
        local parts = {}
        local function Add(t) parts[#parts + 1] = t; return t end
        for _, c in ipairs(CORNERS) do
            local t = Add(Tex(layer, sub, MEDIA .. file, color))
            local f = FLIP[c]
            t:SetTexCoord(f[1], f[2], f[3], f[4])
            t:SetSize(R, R)
            t:SetPoint(c, frame, c, 0, 0)
        end
        if line then
            local t = Add(Tex(layer, sub, WHITE, color))       -- top
            t:SetPoint("TOPLEFT", frame, "TOPLEFT", R, -inset); t:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -R, -inset); t:SetHeight(line)
            t = Add(Tex(layer, sub, WHITE, color))             -- bottom
            t:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", R, inset); t:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -R, inset); t:SetHeight(line)
            t = Add(Tex(layer, sub, WHITE, color))             -- left
            t:SetPoint("TOPLEFT", frame, "TOPLEFT", inset, -R); t:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", inset, R); t:SetWidth(line)
            t = Add(Tex(layer, sub, WHITE, color))             -- right
            t:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -inset, -R); t:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -inset, R); t:SetWidth(line)
        else
            local t = Add(Tex(layer, sub, WHITE, color))       -- middle, full height
            t:SetPoint("TOPLEFT", frame, "TOPLEFT", R, 0); t:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -R, 0)
            t = Add(Tex(layer, sub, WHITE, color))             -- left side, between the corners
            t:SetPoint("TOPLEFT", frame, "TOPLEFT", 0, -R); t:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", 0, R); t:SetWidth(R)
            t = Add(Tex(layer, sub, WHITE, color))             -- right side
            t:SetPoint("TOPRIGHT", frame, "TOPRIGHT", 0, -R); t:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 0, R); t:SetWidth(R)
        end
        return parts
    end

    -- The window's own (square) backdrop becomes the rounded fill and edge, in
    -- the same colors; later color changes go to the rounded pieces.
    local bg, edge = { 0.05, 0.05, 0.05, 0.95 }, { 0.3, 0.7, 1, 1 }
    if frame.GetBackdrop and frame:GetBackdrop() then
        local r, g, b, a = frame:GetBackdropColor()
        if r then bg = { r, g, b, a or 1 } end
        r, g, b, a = frame:GetBackdropBorderColor()
        if r then edge = { r, g, b, a or 1 } end
        frame:SetBackdrop(nil)
    end
    local fill = Shape("BACKGROUND", -7, "win_round_fill", bg, 0, nil)
    local outline = Shape("BORDER", 3, "win_round_line", edge, 0, 1)
    Shape("BORDER", 1, "win_round_inner", { 0.3, 0.65, 1, 0.3 }, IN, 1)
    local function Paint(parts, r, g, b, a) for _, t in ipairs(parts) do t:SetVertexColor(r, g, b, a or 1) end end
    frame.SetBackdropColor = function(_, r, g, b, a) bg = { r, g, b, a or 1 }; Paint(fill, r, g, b, a) end
    frame.SetBackdropBorderColor = function(_, r, g, b, a) edge = { r, g, b, a or 1 }; Paint(outline, r, g, b, a) end
    frame.GetBackdropColor = function() return bg[1], bg[2], bg[3], bg[4] end
    frame.GetBackdropBorderColor = function() return edge[1], edge[2], edge[3], edge[4] end

    -- Soft blue glow just outside, brightest at the edge, following the corners.
    local BLUE = { 0.3, 0.65, 1, 0.42 }
    local function Glow(file, l, r, t, b)
        local g = Tex("BACKGROUND", -8, MEDIA .. file, BLUE)
        g:SetTexCoord(l, r, t, b)
        return g
    end
    local t = Glow("win_glow_v", 0, 1, 1, 0)          -- top
    t:SetPoint("BOTTOMLEFT", frame, "TOPLEFT", R, 0); t:SetPoint("BOTTOMRIGHT", frame, "TOPRIGHT", -R, 0); t:SetHeight(GLOW)
    t = Glow("win_glow_v", 0, 1, 0, 1)                -- bottom
    t:SetPoint("TOPLEFT", frame, "BOTTOMLEFT", R, 0); t:SetPoint("TOPRIGHT", frame, "BOTTOMRIGHT", -R, 0); t:SetHeight(GLOW)
    t = Glow("win_glow_h", 1, 0, 0, 1)                -- left
    t:SetPoint("TOPRIGHT", frame, "TOPLEFT", 0, -R); t:SetPoint("BOTTOMRIGHT", frame, "BOTTOMLEFT", 0, R); t:SetWidth(GLOW)
    t = Glow("win_glow_h", 0, 1, 0, 1)                -- right
    t:SetPoint("TOPLEFT", frame, "TOPRIGHT", 0, -R); t:SetPoint("BOTTOMLEFT", frame, "BOTTOMRIGHT", 0, R); t:SetWidth(GLOW)
    for _, c in ipairs(CORNERS) do
        local f = FLIP[c]
        t = Glow("win_rglow_c", f[1], f[2], f[3], f[4])
        t:SetSize(GLOW + R, GLOW + R)
        t:SetPoint(c, frame, c, c:find("LEFT") and -GLOW or GLOW, c:find("TOP") and GLOW or -GLOW)
    end

    -- Title strip (navy, rounded at the top) with a gold underline.
    if titleHeight and titleHeight > R then
        local NAVY = { 0.075, 0.157, 0.29, 1 }
        local S = IN + 1
        for _, c in ipairs({ "TOPLEFT", "TOPRIGHT" }) do
            local f = FLIP[c]
            t = Tex("BORDER", 0, MEDIA .. "win_round_strip", NAVY)
            t:SetTexCoord(f[1], f[2], f[3], f[4]); t:SetSize(R, R); t:SetPoint(c, frame, c, 0, 0)
        end
        t = Tex("BORDER", 0, WHITE, NAVY)                 -- top band between the rounded corners
        t:SetPoint("TOPLEFT", frame, "TOPLEFT", R, -S); t:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -R, -S); t:SetHeight(R - S)
        t = Tex("BORDER", 0, WHITE, NAVY)                 -- the rest, full width
        t:SetPoint("TOPLEFT", frame, "TOPLEFT", S, -R); t:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -S, -R); t:SetHeight(titleHeight - R)
        local line = Tex("BORDER", 2, WHITE, { 1, 0.69, 0, 0.7 })
        line:SetPoint("TOPLEFT", frame, "TOPLEFT", S, -titleHeight); line:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -S, -titleHeight)
        line:SetHeight(1)
    end

    -- Gold chevrons at 12, 3, 6 and 9, pointing outward, 3 px off the edge;
    -- the side ones a little larger. frame.aetherChevrons.left / .right let a
    -- docked window hide the sides.
    frame.aetherChevrons = {}
    for _, c in ipairs({ { "top", "TOP", 0, 3, 0, 26 }, { "bottom", "BOTTOM", 0, -3, math.pi, 26 },
                         { "left", "LEFT", -3, 0, math.pi / 2, 34 }, { "right", "RIGHT", 3, 0, -math.pi / 2, 34 } }) do
        local set = {}
        for _, g in ipairs({ { "dark", { 0.04, 0.05, 0.07, 1 }, 6 }, { "gold", { 1, 0.69, 0, 1 }, 7 } }) do
            -- the gold is the 3D bevel, baked per direction and lit from the
            -- top-right, so it's never rotated; the dark backing still turns
            local gold3d = g[1] == "gold"
            local ch = Tex("OVERLAY", g[3], MEDIA .. (gold3d and ("chev3d_" .. ({ top = "up", bottom = "down", left = "left", right = "right" })[c[1]]) or ("win_chev_" .. g[1])),
                gold3d and { 1, 1, 1, 1 } or g[2])
            ch:SetSize(c[6], c[6])
            ch:SetPoint("CENTER", frame, c[2], c[3], c[4])
            if not gold3d and c[5] ~= 0 and ch.SetRotation then ch:SetRotation(c[5]) end   -- positive turns counter-clockwise
            set[#set + 1] = ch
        end
        frame.aetherChevrons[c[1]] = set
    end
end

-- ==========================================
-- SUGGESTION WINDOW
-- ==========================================

local notice
local GoTo, GoToQuest   -- below
local function ShowQuests()
    if notice then notice:Hide() end
    if AetherHub_Toggle then
        AetherHub_Toggle("AetherLedger")      -- opens AetherHub on this tab (never closes it)
    else
        for line in Report():gmatch("[^\n]+") do print(line) end
    end
end

local function BuildNotice()
    notice = CreateFrame("Frame", "AetherLedgerNotice", UIParent, "BackdropTemplate")
    notice:SetSize(360, 110)
    notice:SetPoint("TOP", UIParent, "TOP", 0, -140)
    notice:SetFrameStrata("FULLSCREEN_DIALOG")   -- above AetherHub
    notice:SetMovable(true)
    notice:SetClampedToScreen(true)
    notice:EnableMouse(true)
    notice:RegisterForDrag("LeftButton")
    notice:SetScript("OnDragStart", notice.StartMoving)
    notice:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        AetherLedger_SavePos(self, "notice")
    end)
    if notice.SetBackdrop then
        notice:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        notice:SetBackdropColor(0.05, 0.06, 0.09, 0.92)
        notice:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    AetherDecorate(notice, 28)
    local title = notice:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    title:SetPoint("TOPLEFT", 12, -10)
    title:SetText("|cff4da6ffAetherLedger|r")
    notice.text = notice:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
    notice.text:SetPoint("TOPLEFT", title, "BOTTOMLEFT", 0, -8)
    notice.text:SetPoint("RIGHT", notice, "RIGHT", -12, 0)
    notice.text:SetJustifyH("LEFT")
    local show = AetherButton(notice)
    show:SetSize(110, 22)
    show:SetPoint("BOTTOMRIGHT", notice, "BOTTOMRIGHT", -12, 10)
    show:SetText("Show quests")
    show:SetScript("OnClick", ShowQuests)
    local go = AetherButton(notice)
    go:SetSize(110, 22)
    go:SetPoint("RIGHT", show, "LEFT", -6, 0)
    go:SetText("Clean up")
    go:SetScript("OnClick", function()
        notice:Hide()
        if AetherLedger_Tracker then AetherLedger_Tracker.ShowCleanup() end
    end)
    notice.go = go
    -- One row per zone to choose from: its summary and a Go button.
    notice.rows = {}
    for i = 1, 3 do
        local row = CreateFrame("Frame", nil, notice)
        row:SetHeight(24)
        row:SetPoint("LEFT", notice, "LEFT", 12, 0)
        row:SetPoint("RIGHT", notice, "RIGHT", -12, 0)
        row.go = AetherButton(row, nil, true)
        row.go:SetSize(46, 20)
        row.go:SetPoint("RIGHT", row, "RIGHT", 0, 0)
        row.go:SetText("Go")
        row.go:SetScript("OnClick", function()
            notice:Hide()
            if row.action then row.action() end
        end)
        row.text = row:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
        row.text:SetPoint("LEFT", row, "LEFT", 0, 0)
        row.text:SetPoint("RIGHT", row.go, "LEFT", -6, 0)
        row.text:SetJustifyH("LEFT")
        notice.rows[i] = row
    end
    local later = AetherButton(notice)
    later:SetSize(80, 22)
    later:SetPoint("BOTTOMLEFT", notice, "BOTTOMLEFT", 12, 10)
    later:SetText("Not now")
    later:SetScript("OnClick", function() notice:Hide() end)
    notice:Hide()
end

-- The quest giver to head for in a zone: the one with the most of your quests.
local function Destination(z)
    local byGiver, best = {}, nil
    for _, id in ipairs(z.quests) do
        local d = DATA[id]
        local key = d[GIVER] .. "@" .. d[MAP]
        local g = byGiver[key]
        if not g then
            g = { name = d[GIVER], map = d[MAP], x = d[X] / 100, y = d[Y] / 100, count = 0, level = d[LEVEL], quests = {}, qid = id }
            byGiver[key] = g
        end
        g.count = g.count + 1
        g.quests[#g.quests + 1] = d[NAME]
        if not best or g.count > best.count or (g.count == best.count and g.level < best.level) then best = g end
    end
    return best
end

-- Sends you to the best zone: waypoint on its main quest giver, plus travel directions.
GoTo = function(z)
    local dest = z and Destination(z)
    if not dest then return end
    local db = Settings()
    if AetherCoords_API then
        if db.waypoint then AetherCoords_API.RemoveWaypoint(db.waypoint) end
        db.waypoint = AetherCoords_API.AddWaypoint(dest.map, dest.x, dest.y, "Quests: " .. dest.name)
    end
    if AetherLedger_Travel and AetherLedger_Travel.Start then
        AetherLedger_Travel.Start(dest)
    else
        print(PREFIX .. string.format("head to %s in %s (%.0f, %.0f).", dest.name, MapName(dest.map), dest.x * 100, dest.y * 100))
    end
end

-- lines: messages; rows: { text, action } choices, each with a Go button.
-- Directions to the giver of one quest (class and profession quests).
GoToQuest = function(id)
    local d = DATA[id]
    if not d then return end
    local db = Settings()
    local dest = { name = d[GIVER], map = d[MAP], x = d[X] / 100, y = d[Y] / 100, qid = id }
    if AetherCoords_API then
        if db.waypoint then AetherCoords_API.RemoveWaypoint(db.waypoint) end
        db.waypoint = AetherCoords_API.AddWaypoint(dest.map, dest.x, dest.y, d[NAME] .. ": " .. d[GIVER])
    end
    if AetherLedger_Travel and AetherLedger_Travel.Start then AetherLedger_Travel.Start(dest) end
end

-- Ledger's windows remember where you drag them (top-left corner, per window).
function AetherLedger_SavePos(frame, key)
    local db = Settings()
    db.windowPos = db.windowPos or {}
    local left, top = frame:GetLeft(), frame:GetTop()
    if left and top then db.windowPos[key] = { left, top } end
end

local function SavedPos(frame, key)
    local pos = key and Settings().windowPos and Settings().windowPos[key]
    if not pos then return false end
    frame:ClearAllPoints()
    frame:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", pos[1], pos[2])
    return true
end
AetherLedger_SavedPos = SavedPos

-- Where you last dragged it; if you never have, beside AetherHub when that's
-- showing (so neither covers the other), or else its usual spot.
function AetherLedger_PlaceBeside(frame, defaultPoint, key)
    if SavedPos(frame, key) then return end
    frame:ClearAllPoints()
    local hubFrame = AetherHubFrame
    if hubFrame and hubFrame:IsShown() then
        local right = (UIParent:GetRight() or 0) - (hubFrame:GetRight() or 0)
        if right > frame:GetWidth() + 16 then
            frame:SetPoint("TOPLEFT", hubFrame, "TOPRIGHT", 8, 0)
        else
            frame:SetPoint("TOPRIGHT", hubFrame, "TOPLEFT", -8, 0)
        end
    else
        frame:SetPoint(unpack(defaultPoint))
    end
end

local function LayoutNotice()
    local y = -36 - notice.text:GetStringHeight() - 10
    for _, row in ipairs(notice.rows) do
        if row.action then
            row:ClearAllPoints()
            row:SetPoint("TOPLEFT", notice, "TOPLEFT", 12, y)
            row:SetPoint("RIGHT", notice, "RIGHT", -12, 0)
            y = y - 28
        end
    end
    notice:SetHeight(-y + 46)              -- room for the buttons at the bottom
end

local function ShowNotice(lines, rows, cleanup)
    if not notice then BuildNotice() end
    notice.go:SetShown(cleanup and true or false)
    notice.text:SetText(table.concat(lines, "\n\n"))
    local y = -36 - notice.text:GetStringHeight() - 8
    for i, row in ipairs(notice.rows) do
        local z = rows and rows[i]
        row.action = z and z.action
        if z then
            row:ClearAllPoints()
            row:SetPoint("TOPLEFT", notice, "TOPLEFT", 12, y)
            row:SetPoint("RIGHT", notice, "RIGHT", -12, 0)
            row.text:SetText(z.text)
            row:Show()
            y = y - 28
        else
            row:Hide()
        end
    end
    AetherLedger_PlaceBeside(notice, { "TOP", UIParent, "TOP", 0, -140 }, "notice")
    notice:Show()
    LayoutNotice()
    C_Timer.After(0, LayoutNotice)       -- again once the text has wrapped to its real height
end

-- Runs a check and shows the window when there's something new to say:
-- a better zone (once per zone and level), a profession ready for its next
-- rank, or class/profession quests you haven't been told about.
-- force: say it even if it was already said.
local function Suggest(force, level)
    local db = Settings()
    if not force and db.suggest == false then return end
    if not force and IsInInstance and IsInInstance() then return end
    local ok, report = pcall(Check, level)
    if not ok then
        if force then print(PREFIX .. "couldn't check zones: " .. tostring(report)) end
        return
    end
    local key = CharKey()
    db.told = db.told or {}
    local firstTime = db.told[key] == nil
    local told = db.told[key] or {}
    db.told[key] = told
    local lines = {}

    local rows, zoneHeader, newQuestRow = {}, nil, nil
    local function ZoneRows(minScore)
        for _, option in ipairs(Options()) do
            if option.map ~= report.current and option.score >= minScore and #rows < 3 then
                rows[#rows + 1] = { text = ZoneShort(option), action = function() GoTo(option) end }
            end
        end
    end
    local z = report.suggest
    if z then
        local last = db.shown[key]
        if force or not (last and last.map == z.map and last.level == report.level) then
            db.shown[key] = { map = z.map, level = report.level }
            ZoneRows(MIN_SCORE / 2)
            zoneHeader = "Better questing for your level. Pick a zone:"
        end
    elseif force then
        -- You asked: list your best zones even if none is clearly better than here.
        ZoneRows(0.1)
        local here = report.here
        zoneHeader = (here and #here.quests > 0)
            and ("You're in a good spot (" .. #here.quests .. " quests here). Other zones for your level:")
            or "Zones with quests for your level:"
        if #rows == 0 then zoneHeader = "No other zone has quests for your level right now." end
    end
    for _, item in ipairs(report.rankUps or {}) do
        local tag = "rank:" .. item.prof.key .. ":" .. item.prof.max
        if force or not told[tag] then
            told[tag] = true
            lines[#lines + 1] = RankUpText(item, report.level)
        end
    end
    local new = {}
    for _, id in ipairs(report.special or {}) do
        if not told["q:" .. id] then new[#new + 1] = id end
        told["q:" .. id] = true
    end
    if #new == 1 then
        local d = DATA[new[1]]
        lines[#lines + 1] = string.format("New %s quest: %s, from %s in %s.",
            d[KIND] == "c" and "class" or "profession", d[NAME], GiverText(new[1]), MapName(d[MAP]))
        newQuestRow = { text = "[" .. d[LEVEL] .. "] " .. d[NAME] .. " (" .. MapName(d[MAP]) .. ")",
            action = function() GoToQuest(new[1]) end }
    elseif #new > 1 then
        lines[#lines + 1] = #new .. (firstTime and " class and profession quests are" or " new class and profession quests are")
            .. " available. Show quests lists them."
    end

    -- Quests in your log that turned gray: mention each one once.
    local gray = {}
    if AetherLedger_Tracker and Wants("manageTracker") then
        for _, q in ipairs(AetherLedger_Tracker.Gray()) do
            if force or not told["gray:" .. tostring(q.id)] then gray[#gray + 1] = q.title end
            told["gray:" .. tostring(q.id)] = true
        end
    end
    if #gray > 0 then
        lines[#lines + 1] = (#gray == 1 and ("\"" .. gray[1] .. "\" has turned gray")
            or (#gray .. " quests have turned gray")) .. " (little XP now). Clean up lets you drop them."
    end

    if zoneHeader then lines[#lines + 1] = zoneHeader end
    if newQuestRow then           -- the new class/profession quest gets the last Go row
        while #rows > 2 do table.remove(rows) end
        rows[#rows + 1] = newQuestRow
    end
    if #lines == 0 then return end
    ShowNotice(lines, #rows > 0 and rows or nil, #gray > 0)
end

-- ==========================================
-- EVENTS
-- ==========================================

local f = CreateFrame("Frame")
local checkPending, checkLevel = false, nil
local waitingForCombat = false

local function CheckSoon(delay, level)
    if level then checkLevel = level end
    if checkPending then return end
    checkPending = true
    C_Timer.After(delay or 3, function()
        checkPending = false
        if InCombatLockdown() then waitingForCombat = true; return end
        local lvl = checkLevel
        checkLevel = nil
        Suggest(false, lvl)
    end)
end

for _, event in ipairs({ "PLAYER_LOGIN", "PLAYER_LOGOUT", "PLAYER_LEVEL_UP", "QUEST_TURNED_IN",
    "QUEST_ACCEPTED", "ZONE_CHANGED_NEW_AREA", "PLAYER_REGEN_ENABLED", "SKILL_LINES_CHANGED" }) do
    pcall(f.RegisterEvent, f, event)   -- an event this version doesn't know is skipped, not an error
end

f:SetScript("OnEvent", function(_, event, arg1)
    if event == "PLAYER_LOGIN" then
        Settings()
        -- Give the server a moment to send quest data, then take a snapshot.
        C_Timer.After(10, function()
            pcall(Snapshot)
            LoadCompleted()
            CheckSoon(1)
        end)
    elseif event == "PLAYER_LOGOUT" then
        pcall(Snapshot)
    elseif event == "QUEST_TURNED_IN" then
        if completed and arg1 then completed[arg1] = true end
        CheckSoon(3)
    elseif event == "PLAYER_LEVEL_UP" then
        CheckSoon(3, arg1)   -- UnitLevel can lag behind the event
    elseif event == "PLAYER_REGEN_ENABLED" then
        if waitingForCombat then
            waitingForCombat = false
            CheckSoon(2)
        end
    elseif completed then   -- quest accepted, new zone
        CheckSoon(3)
    end
end)

-- ==========================================
-- SLASH COMMANDS
-- ==========================================

SLASH_AETHERLEDGER1 = "/ledger"
SLASH_AETHERLEDGER2 = "/aetherledger"
SlashCmdList["AETHERLEDGER"] = function(msg)
    local cmd = strlower(strtrim(msg or ""))
    if cmd == "" or cmd == "export" then
        local ok, data = pcall(Snapshot)
        if ok and data then
            print(PREFIX .. string.format("%d quests in your log, %d completed quests recorded.",
                #data.questLog, #data.completed))
            print("  Type /reload or log out to write the file:")
            print("  WTF\\Account\\<account>\\SavedVariables\\AetherLedger.lua")
        else
            print(PREFIX .. "export failed: " .. tostring(data))
        end
    elseif cmd == "status" then
        print(PREFIX .. Status())
    elseif cmd == "zones" then
        pcall(Check)
        for line in Report():gmatch("[^\n]+") do print(line) end
    elseif cmd == "check" then
        Suggest(true)
    elseif cmd == "cleanup" then
        if AetherLedger_Tracker then AetherLedger_Tracker.ShowCleanup() end
    elseif cmd == "tracker" then
        if AetherLedger_Tracker then AetherLedger_Tracker.Explain() end
    elseif cmd == "sort" then
        if AetherLedger_Tracker then AetherLedger_Tracker.Apply() end
    elseif cmd == "tooltip" then
        if AetherLedger_TooltipSpot then
            local on = AetherLedger_TooltipSpot.Toggle()
            print(PREFIX .. (on and "tooltips go beside the quest tracker |cff33dd66on|r"
                or "tooltips go beside the quest tracker |cffff5555off|r (the game's usual spot)"))
        end
    elseif cmd == "resetwindows" then
        Settings().windowPos = nil
        print(PREFIX .. "Ledger's windows will open in their usual spots again.")
    elseif cmd == "go" then
        AetherLedger_API.GoBest()
    elseif cmd == "stop" then
        if AetherLedger_Travel then AetherLedger_Travel.Stop() end
    elseif cmd == "suggest" or cmd == "suggest on" or cmd == "suggest off" then
        local db = Settings()
        if cmd == "suggest" then db.suggest = not db.suggest else db.suggest = (cmd == "suggest on") end
        print(PREFIX .. "zone suggestions " .. (db.suggest and "|cff33dd66on|r" or "|cffff5555off|r"))
    else
        print(PREFIX .. "records your quest log and completed quests.")
        print("  /ledger           record now (then /reload or log out to save the file)")
        print("  /ledger status    when this character was last recorded")
        print("  /ledger zones     the best zones for you right now, and their quests")
        print("  /ledger check     check now and show the suggestion window")
        print("  /ledger go        directions to the best zone's main quest giver (/ledger stop ends them)")
        print("  /ledger suggest   turn zone suggestions on or off")
        print("  /ledger cleanup   gray quests you could drop; /ledger sort re-sorts the quest tracker")
        print("  /ledger tracker   why each quest is or isn't on the tracker")
        print("  /ledger tooltip   tooltips beside the quest tracker, or back in the corner")
        print("  /ledger resetwindows   put Ledger's windows back in their usual spots")
    end
end

AetherLedger_API = {
    Snapshot = function() return Snapshot() end,
    Status = Status,
    Report = Report,
    HubReport = function() return Report(true) end,
    Cleanup = function() if AetherLedger_Tracker then AetherLedger_Tracker.ShowCleanup() end end,
    SortTracker = function() if AetherLedger_Tracker then AetherLedger_Tracker.Apply() end end,
    Check = function() Suggest(true) end,
    Refresh = function() pcall(Check) end,
    Options = function()
        if not lastReport then pcall(Check) end
        local list = {}
        for i, z in ipairs(Options()) do
            list[i] = { label = ZoneShort(z), here = (lastReport and z.map == lastReport.current) }
        end
        return list
    end,
    Selected = function() return selected end,
    Select = function(i) selected = i end,
    GoOption = function(i)
        local z = Options()[i]
        if z then GoTo(z) end
    end,
    GoBest = function()
        if not lastReport then pcall(Check) end
        local z = lastReport and (lastReport.suggest or lastReport.zones[1])
        if z then GoTo(z) else print(PREFIX .. "no zone to go to right now.") end
    end,
    Suggesting = function() return Settings().suggest ~= false end,
}
