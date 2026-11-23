-- ==========================================
-- AetherPathfinder - world map filters for service NPCs (WoW Forever 1.60.x)
-- Learns where trainers, merchants, stable masters and so on stand as you
-- meet them, then shows them as colored pins you can filter on the world map.
-- ==========================================

-- ==========================================
-- AETHER TEXT
-- ==========================================
-- The Aether text style, in Fira Sans (the unit frames' font; SIL Open Font
-- License, see AetherHub\Media\Fonts\FiraSans-OFL.txt). In windows: Regular
-- for text, SemiBold for the gold headings, with a soft shadow. Over the game
-- world (AetherFontWorld...): Bold with a thin black outline and a shadow, so
-- it reads on any background, faded or not. Each copies the Blizzard font it
-- stands in for (size, color), so layouts stay the same. The files live in
-- AetherHub\Media\Fonts; if one can't load, Blizzard's font stays.
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
    local function Make(name, base, weight, world)
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
    end
    for _, d in ipairs({
        { "AetherFontNormal",           "GameFontNormal",         "SemiBold" },
        { "AetherFontNormalSmall",      "GameFontNormalSmall",    "SemiBold" },
        { "AetherFontNormalLarge",      "GameFontNormalLarge",    "SemiBold" },
        { "AetherFontNormalHuge",       "GameFontNormalHuge",     "SemiBold" },
        { "AetherFontHighlight",        "GameFontHighlight",      "Regular" },
        { "AetherFontHighlightSmall",   "GameFontHighlightSmall", "Regular" },
        { "AetherFontDisable",          "GameFontDisable",        "Regular" },
        { "AetherFontDisableSmall",     "GameFontDisableSmall",   "Regular" },
        { "AetherFontWorldNormal",      "GameFontNormal",         "Bold", true },
        { "AetherFontWorldNormalSmall", "GameFontNormalSmall",    "Bold", true },
        { "AetherFontWorld",            "GameFontHighlight",      "Bold", true },
        { "AetherFontWorldSmall",       "GameFontHighlightSmall", "Bold", true },
    }) do Make(d[1], d[2], d[3], d[4]) end
end

local ADDON_NAME = ...

-- ==========================================
-- CATEGORIES
-- ==========================================
-- Each NPC is sorted by the subtitle under its name (e.g. "Hunter Trainer").
-- Keywords are matched in lowercase; the first matching category wins,
-- except Repair, which is added on top of any merchant category.

local PROFESSIONS = {
    "alchem", "blacksmith", "armorsmith", "weaponsmith", "enchant", "engineer",
    "herbalis", "leatherwork", "mining", "miner", "skinn", "tailor",
    "cook", "fishing", "fisherman", "first aid",
}

-- Classes, in the order the class dropdown lists them. "word" is how the class
-- appears in trainer titles ("Hunter Trainer").
local CLASS_LIST = {
    { token = "WARRIOR", word = "warrior" }, { token = "PALADIN", word = "paladin" },
    { token = "HUNTER",  word = "hunter" },  { token = "ROGUE",   word = "rogue" },
    { token = "PRIEST",  word = "priest" },  { token = "SHAMAN",  word = "shaman" },
    { token = "MAGE",    word = "mage" },    { token = "WARLOCK", word = "warlock" },
    { token = "DRUID",   word = "druid" },
}

-- Classes with a trainer of their own besides the class trainer.
local CLASS_PET = {
    HUNTER  = { word = "pet trainer",    label = "Pet Trainer" },
    WARLOCK = { word = "demon trainer",  label = "Demon Trainer" },
    MAGE    = { word = "portal trainer", label = "Portal Trainer" },
}

local CATEGORIES = {
    -- The two class filters follow the class chosen in the class dropdown.
    { key = "mytrainer", label = "Class Trainer",    color = { 0.67, 0.83, 0.45 }, on = true },
    { key = "classpet",  label = "Class Pet Trainer",color = { 0.40, 0.90, 0.70 }, on = true },
    { key = "stable",  label = "Stable Master",      color = { 0.85, 0.60, 0.30 }, on = true,
      words = { "stable master" } },
    { key = "general", label = "General Goods",      color = { 1.00, 0.85, 0.20 }, on = true,
      words = { "general goods", "general supplies", "general store", "general trade",
                "trade goods", "trade supplies", "trade supplier", "tradesman" } },
    { key = "ammo",    label = "Ammo / Bows / Guns", color = { 0.95, 0.45, 0.25 }, on = true,
      words = { "bow", "gun", "arrow", "ammunition", "fletcher" } },
    { key = "food",    label = "Food & Drink",       color = { 0.95, 0.75, 0.55 }, on = false,
      words = { "food", "drink", "baker", "butcher", "fruit", "cheese", "meat", "bartender", "barmaid" } },
    { key = "inn",     label = "Innkeeper",          color = { 0.90, 0.45, 0.85 }, on = false,
      words = { "innkeeper" } },
    { key = "flight",  label = "Flight Master",      color = { 0, 0, 0 }, on = true,
      -- Black marker: a white ring keeps it visible, and its name in menus
      -- and tooltips is written in light gray so it can be read.
      ring = { 1, 1, 1 }, text = { 0.85, 0.85, 0.85 },
      words = { "flight master", "wind rider", "gryphon master", "hippogryph master", "bat handler" } },
    { key = "mail",    label = "Mailbox",            color = { 0.30, 0.55, 1.00 }, on = true },
    { key = "repair",  label = "Repair",             color = { 0.75, 0.75, 0.80 }, on = false,
      words = { "armorer", "weapon merchant", "blacksmithing supplies" } },
    { key = "prof",    label = "Profession Trainer", color = { 0.55, 0.55, 1.00 }, on = false },
    { key = "class",   label = "Other Class Trainer",color = { 0.60, 0.60, 0.60 }, on = false },
    { key = "bank",    label = "Banker",             color = { 1.00, 1.00, 1.00 }, on = false,
      words = { "banker" } },
    { key = "auction", label = "Auctioneer",         color = { 0.90, 0.30, 0.30 }, on = false,
      words = { "auctioneer" } },
    { key = "supplies",label = "Profession Supplies",color = { 0.45, 0.85, 0.95 }, on = false,
      words = { "supplies", "supplier", "reagent" } },
}

local CATEGORY_BY_KEY = {}
for i, cat in ipairs(CATEGORIES) do
    cat.order = i
    CATEGORY_BY_KEY[cat.key] = cat
end

local function ContainsAny(text, words)
    for _, w in ipairs(words) do
        if text:find(w, 1, true) then return true end
    end
    return false
end

-- Returns the main category key for a subtitle (nil if it isn't a service NPC)
-- and, for class trainers, the class they train ("HUNTER").
-- Class trainers are stored as "classtrainer" / "classpet" with their class;
-- which filter they show under depends on the class chosen in the dropdown.
local function Classify(subtitle)
    if not subtitle or subtitle == "" then return nil end
    local s = subtitle:lower()

    for _, c in ipairs(CLASS_LIST) do
        if s:find(c.word .. " trainer", 1, true) then return "classtrainer", c.token end
    end
    for token, pet in pairs(CLASS_PET) do
        if s:find(pet.word, 1, true) then return "classpet", token end
    end

    local isTrainer = s:find("trainer", 1, true)
        or s:find("^apprentice") or s:find("^journeyman") or s:find("^expert") or s:find("^artisan")
    if isTrainer and ContainsAny(s, PROFESSIONS) then return "prof" end

    for _, cat in ipairs(CATEGORIES) do
        if cat.words and ContainsAny(s, cat.words) then return cat.key end
    end
    return nil
end

-- ==========================================
-- SAVED DATA
-- ==========================================
-- WoW Forever 1.60 has been reported to save account-wide variables without
-- reading them back, so everything is kept in both an account-wide and a
-- per-character table, and the two are merged when the addon loads.

local db

local OPTION_DEFAULTS = {
    useSeed      = true,    -- show the built-in NPC locations (from QuestieDB)
    otherFaction = false,   -- also show NPCs that are only friendly to the other faction
    trainerClass = "AUTO",  -- class for the class trainer filters; "AUTO" = your character's class
    minimap      = true,    -- also show the markers on the minimap
}

local CLASS_BY_TOKEN = {}
for _, c in ipairs(CLASS_LIST) do CLASS_BY_TOKEN[c.token] = c end

-- The class the trainer filters follow right now.
local function SelectedClass()
    local choice = db and db.trainerClass
    if not choice or choice == "AUTO" or not CLASS_BY_TOKEN[choice] then
        choice = select(2, UnitClass("player"))
    end
    return choice
end

local function ClassName(token)
    local names = LOCALIZED_CLASS_NAMES_MALE
    return (names and names[token]) or (token:sub(1, 1) .. token:sub(2):lower())
end

local function HasClassPet()
    return CLASS_PET[SelectedClass()] ~= nil
end

local function LabelFor(cat)
    if cat.key == "mytrainer" then return ClassName(SelectedClass()) .. " Trainer" end
    if cat.key == "classpet" then
        local pet = CLASS_PET[SelectedClass()]
        return pet and pet.label or "Class Pet Trainer (n/a)"
    end
    return cat.label
end

-- Before the class dropdown, hunters had fixed "hunter" / "pet" filters and
-- learned NPCs were filed under "hunter", "pet" or "class".
local function MigrateClassFilters(merged)
    local f = merged.filters
    if f.hunter ~= nil and f.mytrainer == nil then f.mytrainer = f.hunter end
    if f.pet ~= nil and f.classpet == nil then f.classpet = f.pet end
    f.hunter, f.pet = nil, nil
    for _, list in pairs(merged.npcs) do
        for _, npc in pairs(list) do
            local cats = npc.cats
            if cats and (cats.hunter or cats.pet or cats.class) then
                local hadHunter, hadPet = cats.hunter, cats.pet
                cats.hunter, cats.pet, cats.class = nil, nil, nil
                local cat, forClass = Classify(npc.sub)
                if cat == "classtrainer" or cat == "classpet" then
                    cats[cat] = true
                    npc.forClass = forClass
                elseif hadHunter then
                    cats.classtrainer, npc.forClass = true, "HUNTER"
                elseif hadPet then
                    cats.classpet, npc.forClass = true, "HUNTER"
                end
            end
        end
    end
end

local function MergeInto(target, source)
    if type(source) ~= "table" then return end
    for key in pairs(OPTION_DEFAULTS) do
        if target[key] == nil and source[key] ~= nil then target[key] = source[key] end
    end
    if type(source.filters) == "table" then
        target.filters = target.filters or {}
        for k, v in pairs(source.filters) do
            if target.filters[k] == nil then target.filters[k] = v end
        end
    end
    if type(source.mailboxes) == "table" then
        target.mailboxes = target.mailboxes or {}
        for mapID, list in pairs(source.mailboxes) do
            if target.mailboxes[mapID] == nil and type(list) == "table" then target.mailboxes[mapID] = list end
        end
    end
    if type(source.knownFlights) == "table" then
        target.knownFlights = target.knownFlights or {}
        for who, list in pairs(source.knownFlights) do
            if type(list) == "table" then
                target.knownFlights[who] = target.knownFlights[who] or {}
                for id, v in pairs(list) do
                    if target.knownFlights[who][id] == nil then target.knownFlights[who][id] = v end
                end
            end
        end
    end
    if type(source.npcs) == "table" then
        target.npcs = target.npcs or {}
        for mapID, list in pairs(source.npcs) do
            target.npcs[mapID] = target.npcs[mapID] or {}
            for id, npc in pairs(list) do
                local mine = target.npcs[mapID][id]
                if not mine or (npc.exact and not mine.exact) then
                    target.npcs[mapID][id] = npc
                end
            end
        end
    end
end

local function LoadData()
    local merged = { filters = {}, npcs = {} }
    MergeInto(merged, AetherPathfinderCharDB)
    MergeInto(merged, AetherPathfinderDB)
    -- Learned NPCs and filters from before the rename (present only right after migrating).
    MergeInto(merged, PathfinderMapCharDB)
    MergeInto(merged, PathfinderMapDB)
    MigrateClassFilters(merged)
    for _, cat in ipairs(CATEGORIES) do
        if merged.filters[cat.key] == nil then merged.filters[cat.key] = cat.on end
    end
    for key, value in pairs(OPTION_DEFAULTS) do
        if merged[key] == nil then merged[key] = value end
    end
    db = merged
    -- Both saved tables point at the same data from now on.
    AetherPathfinderDB = db
    AetherPathfinderCharDB = db
    PathfinderMapDB, PathfinderMapCharDB = nil, nil
end

-- ==========================================
-- READING NPCs
-- ==========================================

local function IsSecret(v)
    return issecretvalue ~= nil and issecretvalue(v)
end

local function Readable(v)
    return v ~= nil and not IsSecret(v)
end

-- Hidden tooltip, used when C_TooltipInfo isn't available.
local scanTip = CreateFrame("GameTooltip", "AetherPathfinderScanTip", nil, "GameTooltipTemplate")

local function CleanSubtitle(text)
    if not Readable(text) then return nil end
    text = text:gsub("^<", ""):gsub(">$", "")
    -- The second line is the level line when an NPC has no subtitle.
    if text:find("^" .. (LEVEL or "Level")) then return nil end
    return text
end

local function GetSubtitle(unit)
    if C_TooltipInfo and C_TooltipInfo.GetUnit then
        local ok, data = pcall(C_TooltipInfo.GetUnit, unit)
        if ok and data and data.lines and data.lines[2] then
            local text = CleanSubtitle(data.lines[2].leftText)
            if text then return text end
        end
    end
    local ok = pcall(function()
        scanTip:SetOwner(WorldFrame, "ANCHOR_NONE")
        scanTip:SetUnit(unit)
    end)
    if not ok then return nil end
    local line = _G["AetherPathfinderScanTipTextLeft2"]
    local text = line and CleanSubtitle(line:GetText())
    scanTip:Hide()
    return text
end

-- NPC id from the unit's GUID ("Creature-0-...-<id>-..."), or nil for players/pets.
local function GetNpcID(unit)
    local guid = UnitGUID(unit)
    if not Readable(guid) then return nil end
    local kind, _, _, _, _, id = strsplit("-", guid)
    if kind ~= "Creature" then return nil end
    return tonumber(id)
end

local function GetPlayerSpot()
    local mapID = C_Map.GetBestMapForUnit("player")
    if not mapID then return nil end
    local pos = C_Map.GetPlayerMapPosition(mapID, "player")
    if not pos then return nil end          -- no position inside dungeons
    local x, y = pos:GetXY()
    if not x or (x == 0 and y == 0) then return nil end
    return mapID, x, y
end

local pinsDirty = true

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

-- ==========================================
-- DISCOVERED FLIGHT PATHS
-- ==========================================
-- Flight masters whose flight path this character hasn't discovered get a red
-- ring and blink. Discovery is learned by talking to a flight master and, more
-- completely, whenever a flight map is open (it lists every known path).

local function KnownFlights()
    if not db then return {} end
    db.knownFlights = db.knownFlights or {}
    local who = (UnitName("player") or "?") .. "-" .. ((GetRealmName and GetRealmName()) or "?")
    db.knownFlights[who] = db.knownFlights[who] or {}
    return db.knownFlights[who]
end

local function MarkFlightKnown(id)
    if id then KnownFlights()[id] = true; pinsDirty = true end
end

-- True for a flight master of a faction you can use whose path you haven't discovered.
local function NeedsDiscovery(npc)
    if not db or not db.filters.flight or not (npc.cats and npc.cats.flight) then return false end
    local group = UnitFactionGroup("player")
    local mine = (group == "Alliance" and 1) or (group == "Horde" and 2) or 3
    if npc.faction and npc.faction ~= 3 and npc.faction ~= mine then return false end
    return not (npc.id and KnownFlights()[npc.id])
end

local function SetClassChoice(choice)
    if not db then return end
    db.trainerClass = (choice and CLASS_BY_TOKEN[choice]) and choice or "AUTO"
    pinsDirty = true
end

-- Saves an NPC. exact = true when you are talking to it (you're standing next to it).
-- extraCat adds a category that comes from the window it opened (e.g. "repair").
local function RecordNPC(unit, exact, extraCat, fallbackCat)
    if not db or InCombatLockdown() then return end
    if not UnitExists(unit) or UnitIsPlayer(unit) then return end

    local id = GetNpcID(unit)
    local name = UnitName(unit)
    if not id or not Readable(name) then return end

    local subtitle = GetSubtitle(unit)
    local cat, forClass = Classify(subtitle)
    cat = cat or fallbackCat
    if not cat and not extraCat then return end

    local mapID, x, y = GetPlayerSpot()
    if not mapID then return end

    db.npcs[mapID] = db.npcs[mapID] or {}
    local npc = db.npcs[mapID][id]
    if not npc then
        npc = { id = id, name = name, sub = subtitle, cats = {} }
        db.npcs[mapID][id] = npc
    end
    npc.name = name
    npc.sub = subtitle or npc.sub
    if cat then npc.cats[cat] = true end
    if extraCat then npc.cats[extraCat] = true end
    if forClass then npc.forClass = forClass end

    -- A spot from talking to the NPC beats one from hovering over it.
    if exact or not npc.exact then
        npc.x, npc.y = x, y
        npc.exact = exact or npc.exact
    end
    pinsDirty = true
end

-- ==========================================
-- EVENTS
-- ==========================================

-- ==========================================
-- MAILBOXES
-- ==========================================
-- Built-in mailbox spots come from AetherPathfinder_Mail.lua. Opening a mailbox
-- that isn't on the map yet adds it at your spot.

local MAILBOX_SAME_YARDS = 20

local function YardsApart(mapID, x1, y1, x2, y2)
    if C_Map.GetWorldPosFromMapPos and CreateVector2D then
        local ok1, _, a = pcall(C_Map.GetWorldPosFromMapPos, mapID, CreateVector2D(x1, y1))
        local ok2, _, b = pcall(C_Map.GetWorldPosFromMapPos, mapID, CreateVector2D(x2, y2))
        if ok1 and ok2 and a and b and not IsSecret(a.x) then
            return math.sqrt((a.x - b.x) ^ 2 + (a.y - b.y) ^ 2)
        end
    end
    return math.sqrt((x1 - x2) ^ 2 + (y1 - y2) ^ 2) * 1000   -- rough: a zone is about 1000 yards
end

local function LearnMailbox()
    if not db then return end
    local mapID, x, y = GetPlayerSpot()
    if not mapID then return end
    for _, entry in ipairs((AetherPathfinder_Mailboxes or {})[mapID] or {}) do
        if YardsApart(mapID, x, y, entry[3], entry[4]) < MAILBOX_SAME_YARDS then return end
    end
    db.mailboxes = db.mailboxes or {}
    local list = db.mailboxes[mapID] or {}
    for _, spot in ipairs(list) do
        if YardsApart(mapID, x, y, spot[1], spot[2]) < MAILBOX_SAME_YARDS then return end
    end
    list[#list + 1] = { x, y }
    db.mailboxes[mapID] = list
    pinsDirty = true
end

local SetupMap         -- defined with the map pins below
local SyncFlightPaths  -- defined with the map pins below

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("UPDATE_MOUSEOVER_UNIT")
events:RegisterEvent("GOSSIP_SHOW")
events:RegisterEvent("MERCHANT_SHOW")
events:RegisterEvent("TRAINER_SHOW")
events:RegisterEvent("PET_STABLE_SHOW")
events:RegisterEvent("TAXIMAP_OPENED")
events:RegisterEvent("BANKFRAME_OPENED")
events:RegisterEvent("AUCTION_HOUSE_SHOW")
events:RegisterEvent("MAIL_SHOW")

events:SetScript("OnEvent", function(self, event, arg1)
    if event == "ADDON_LOADED" then
        if arg1 == ADDON_NAME then
            LoadData()
            SetupMap()            -- in case the world map is already loaded
        elseif arg1 == "Blizzard_WorldMap" then
            SetupMap()            -- WoW loads the world map the first time it's needed
        end
        return
    elseif event == "PLAYER_LOGIN" then
        SetupMap()
        return
    end

    if event == "UPDATE_MOUSEOVER_UNIT" then
        -- Only friendly NPCs close enough that your own spot is a good guess for theirs.
        -- Never in combat: WoW blocks addons from checking distance then, and the
        -- blocked call shows "Interface action failed because of an AddOn".
        if InCombatLockdown() then return end
        if UnitExists("mouseover") and not UnitCanAttack("player", "mouseover") then
            local ok, close = pcall(CheckInteractDistance, "mouseover", 2)
            if ok and close then RecordNPC("mouseover", false) end
        end
    elseif event == "MERCHANT_SHOW" then
        local canRepair = CanMerchantRepair and CanMerchantRepair()
        RecordNPC("npc", true, canRepair and "repair" or nil)
    elseif event == "PET_STABLE_SHOW" then
        RecordNPC("npc", true, nil, "stable")
    elseif event == "TAXIMAP_OPENED" then
        RecordNPC("npc", true, nil, "flight")
        SyncFlightPaths(GetNpcID("npc"), UnitGUID("npc"))
    elseif event == "BANKFRAME_OPENED" then
        RecordNPC("npc", true, nil, "bank")
    elseif event == "AUCTION_HOUSE_SHOW" then
        RecordNPC("npc", true, nil, "auction")
    elseif event == "MAIL_SHOW" then
        LearnMailbox()
    else -- GOSSIP_SHOW, TRAINER_SHOW
        RecordNPC("npc", true)
    end
end)

-- ==========================================
-- MAP PINS
-- ==========================================

-- Filled in by SetupMap() once WoW has loaded the world map, which it only does
-- the first time it's needed (often after this addon has loaded).
local mapFrame, scroll, canvas

local pins, usedPins = {}, 0
local rebuildIn = 0     -- seconds until the minimap re-collects nearby NPCs
local PIN_SIZE   = 13.2  -- room for an icon (the dots were 8.4)
local PIN_BORDER = 1.4
local CIRCLE_MASK = "Interface\\CharacterFrame\\TempPortraitAlphaMask"

-- Stored category -> the filter it shows under for the chosen class.
local function ResolveKey(npc, key)
    if key == "classtrainer" then
        return npc.forClass == SelectedClass() and "mytrainer" or "class"
    elseif key == "classpet" then
        return npc.forClass == SelectedClass() and "classpet" or "class"
    end
    return key
end

local function MainCategory(npc)
    local best
    for stored in pairs(npc.cats) do
        local key = ResolveKey(npc, stored)
        local cat = CATEGORY_BY_KEY[key]
        if cat and db.filters[key] and (not best or cat.order < best.order) then
            best = cat
        end
    end
    return best
end

local function ShowPinTooltip(pin)
    local npc = pin.npc
    GameTooltip:SetOwner(pin, pin.tooltipAnchor or "ANCHOR_RIGHT")
    GameTooltip:AddLine(npc.name, 1, 1, 1)
    if npc.sub then GameTooltip:AddLine(npc.sub, 0.8, 0.8, 0.8) end
    local keys, seen = {}, {}
    for stored in pairs(npc.cats) do
        local cat = CATEGORY_BY_KEY[ResolveKey(npc, stored)]
        if cat and not seen[cat] then seen[cat] = true; keys[#keys + 1] = cat end
    end
    table.sort(keys, function(a, b) return a.order < b.order end)
    for _, cat in ipairs(keys) do
        -- Other classes' trainers say which class they train.
        local text = LabelFor(cat)
        if cat.key == "class" and npc.forClass then
            text = ClassName(npc.forClass) .. " (" .. cat.label .. ")"
        end
        local c = cat.text or cat.color
        GameTooltip:AddLine(text, c[1], c[2], c[3])
    end
    GameTooltip:AddLine(string.format("%.1f, %.1f%s", npc.x * 100, npc.y * 100,
        npc.exact and "" or "  (approx.)"), 0.6, 0.6, 0.6)
    if NeedsDiscovery(npc) then
        GameTooltip:AddLine("Flight path not discovered yet", 1, 0.25, 0.25)
    end
    if npc.seed then
        GameTooltip:AddLine("Built-in location (QuestieDB)", 0.45, 0.6, 0.75)
    end
    GameTooltip:Show()
end

-- Makes a texture round by masking it with a circle the same size.
local function Round(owner, tex)
    if not owner.CreateMaskTexture then return end
    local mask = owner:CreateMaskTexture()
    mask:SetTexture(CIRCLE_MASK, "CLAMPTOBLACKADDITIVE", "CLAMPTOBLACKADDITIVE")
    mask:SetAllPoints(tex)
    tex:AddMaskTexture(mask)
end

-- A round marker: a black ring around a colored dot, with a soft glow on hover.
local function MakePin(parent)
    local pin = CreateFrame("Button", nil, parent)
    pin.isAetherPin = true
    pin:SetSize(PIN_SIZE, PIN_SIZE)

    pin.border = pin:CreateTexture(nil, "BACKGROUND")
    pin.border:SetAllPoints()
    pin.border:SetColorTexture(0, 0, 0, 0.9)
    Round(pin, pin.border)

    pin.dot = pin:CreateTexture(nil, "ARTWORK")
    pin.dot:SetPoint("TOPLEFT", PIN_BORDER, -PIN_BORDER)
    pin.dot:SetPoint("BOTTOMRIGHT", -PIN_BORDER, PIN_BORDER)
    Round(pin, pin.dot)

    pin.icon = pin:CreateTexture(nil, "ARTWORK", nil, 1)
    pin.icon:SetPoint("TOPLEFT", PIN_BORDER, -PIN_BORDER)
    pin.icon:SetPoint("BOTTOMRIGHT", -PIN_BORDER, PIN_BORDER)
    Round(pin, pin.icon)

    pin.glow = pin:CreateTexture(nil, "HIGHLIGHT")
    pin.glow:SetPoint("TOPLEFT", -PIN_BORDER, PIN_BORDER)
    pin.glow:SetPoint("BOTTOMRIGHT", PIN_BORDER, -PIN_BORDER)
    pin.glow:SetColorTexture(1, 1, 1, 0.35)
    Round(pin, pin.glow)

    pin:SetScript("OnEnter", ShowPinTooltip)
    pin:SetScript("OnLeave", function() GameTooltip:Hide() end)
    return pin
end

-- Colors a marker for its category (the ring is black unless the category says otherwise).
-- A slow blink (fade to faint and back) for a texture.
local function MakeBlink(tex)
    if not tex.CreateAnimationGroup then return nil end
    local group = tex:CreateAnimationGroup()
    group:SetLooping("BOUNCE")
    local fade = group:CreateAnimation("Alpha")
    fade:SetFromAlpha(1)
    fade:SetToAlpha(0.15)
    fade:SetDuration(0.5)
    if fade.SetSmoothing then fade:SetSmoothing("IN_OUT") end
    return group
end

local function SetBlinking(pin, on)
    if on == (pin.blinking or false) then return end
    pin.blinking = on
    if on and not pin.blinks then
        pin.blinks = { MakeBlink(pin.border), MakeBlink(pin.dot), MakeBlink(pin.icon) }
    end
    for _, group in pairs(pin.blinks or {}) do
        if on then group:Play() else group:Stop() end
    end
end

-- ==========================================
-- MARKER ICONS
-- ==========================================
-- Icons WoW already ships (the minimap's town tracking icons, class crests,
-- profession and item icons): nothing extra to load. If an icon can't be
-- found, the marker falls back to a plain colored dot.
local TRACKING = "Interface\\Minimap\\Tracking\\"
local ICONS = {
    flight   = { TRACKING .. "FlightMaster" },
    inn      = { TRACKING .. "Innkeeper" },
    bank     = { TRACKING .. "Banker" },
    auction  = { TRACKING .. "Auctioneer" },
    mail     = { TRACKING .. "Mailbox" },
    repair   = { TRACKING .. "Repair" },
    stable   = { TRACKING .. "StableMaster" },
    food     = { TRACKING .. "Food" },
    supplies = { TRACKING .. "Reagents", "Interface\\Icons\\INV_Misc_Dust_02" },
    general  = { "Interface\\Icons\\INV_Misc_Bag_10", TRACKING .. "Banker" },
    ammo     = { "Interface\\Icons\\INV_Ammo_Arrow_02", TRACKING .. "Ammunition" },
    prof     = { TRACKING .. "Profession" },
    class    = { TRACKING .. "Class" },
}
-- Profession trainers get their profession's icon (matched in their title).
local PROFESSION_ICONS = {
    { "alchem",      "Interface\\Icons\\Trade_Alchemy" },
    { "blacksmith",  "Interface\\Icons\\Trade_BlackSmithing" },
    { "enchant",     "Interface\\Icons\\Trade_Engraving" },
    { "engineer",    "Interface\\Icons\\Trade_Engineering" },
    { "leatherwork", "Interface\\Icons\\INV_Misc_ArmorKit_17" },
    { "tailor",      "Interface\\Icons\\Trade_Tailoring" },
    { "herbalis",    "Interface\\Icons\\Spell_Nature_NatureTouchGrow" },
    { "mining",      "Interface\\Icons\\Trade_Mining" },
    { "miner",       "Interface\\Icons\\Trade_Mining" },
    { "skinning",    "Interface\\Icons\\INV_Misc_Pelt_Wolf_01" },
    { "cook",        "Interface\\Icons\\INV_Misc_Food_15" },
    { "first aid",   "Interface\\Icons\\Spell_Holy_SealOfSacrifice" },
    { "fishing",     "Interface\\Icons\\Trade_Fishing" },
}
-- Class pet and demon trainers.
local PET_ICONS = {
    HUNTER  = "Interface\\Icons\\Ability_Hunter_BeastTaming",
    WARLOCK = "Interface\\Icons\\Spell_Shadow_SummonImp",
    MAGE    = "Interface\\Icons\\Spell_Arcane_PortalOrgrimmar",
}
local CLASS_CRESTS = "Interface\\TargetingFrame\\UI-Classes-Circles"

local missing = {}   -- icon paths the game didn't have

-- Tries each path; true if one loaded. Interface\Icons squares are trimmed
-- a little so their built-in frame doesn't show in the round marker.
local function TryIcon(tex, paths)
    for _, path in ipairs(paths) do
        if path and not missing[path] then
            local ok = tex:SetTexture(path)
            if ok ~= false then
                if path:find("Interface\\Icons\\", 1, true) then tex:SetTexCoord(0.08, 0.92, 0.08, 0.92)
                else tex:SetTexCoord(0, 1, 0, 1) end
                return true
            end
            missing[path] = true
        end
    end
    return false
end

local function SetIcon(pin, cat, npc)
    local tex, key = pin.icon, cat.key
    -- Class trainers: the class crest.
    if (key == "mytrainer" or key == "class") and npc and npc.forClass and CLASS_ICON_TCOORDS
            and CLASS_ICON_TCOORDS[npc.forClass] and not missing[CLASS_CRESTS] then
        if tex:SetTexture(CLASS_CRESTS) ~= false then
            local c = CLASS_ICON_TCOORDS[npc.forClass]
            tex:SetTexCoord(c[1], c[2], c[3], c[4])
            return true
        end
        missing[CLASS_CRESTS] = true
    end
    if key == "mytrainer" or key == "class" then return TryIcon(tex, ICONS.class) end
    if key == "classpet" then
        return TryIcon(tex, { npc and npc.forClass and PET_ICONS[npc.forClass], TRACKING .. "StableMaster" })
    end
    if key == "prof" then
        local sub = npc and npc.sub and npc.sub:lower() or ""
        for _, pair in ipairs(PROFESSION_ICONS) do
            if sub:find(pair[1], 1, true) then return TryIcon(tex, { pair[2], TRACKING .. "Profession" }) end
        end
    end
    return ICONS[key] and TryIcon(tex, ICONS[key]) or false
end

-- Colors a marker for its category: the ring takes the category's color (the
-- flight master's is white) around the icon. Undiscovered flight masters get
-- a red ring and blink. Without an icon it's the old colored dot.
local function Paint(pin, cat, npc)
    local c, r = cat.color, cat.ring
    local alert = npc and NeedsDiscovery(npc)
    -- Only reload the icon when the marker shows a different kind of NPC.
    local iconKey = cat.key .. "|" .. tostring(npc and npc.forClass) .. "|" .. tostring(npc and npc.sub)
    if pin.iconKey ~= iconKey then
        pin.iconKey, pin.hasIcon = iconKey, SetIcon(pin, cat, npc)
    end
    local hasIcon = pin.hasIcon
    pin.icon:SetShown(hasIcon)
    if hasIcon then
        pin.dot:SetColorTexture(0.06, 0.07, 0.1, 1)          -- dark backing behind the icon
        local ring = r or c
        if alert then pin.border:SetColorTexture(1, 0.1, 0.1, 1)
        else pin.border:SetColorTexture(ring[1], ring[2], ring[3], 1) end
    else
        pin.dot:SetColorTexture(c[1], c[2], c[3], 1)
        if alert then pin.border:SetColorTexture(1, 0.1, 0.1, 1)
        elseif r then pin.border:SetColorTexture(r[1], r[2], r[3], 0.9)
        else pin.border:SetColorTexture(0, 0, 0, 0.9) end
    end
    SetBlinking(pin, alert)
end

-- Markers under (or right next to) your character's arrow turn see-through
-- so the arrow stays easy to spot.
local UNDER_ARROW_PX, UNDER_ARROW_ALPHA = 12, 0.3

local function GetPin(i)
    local pin = pins[i]
    if pin then return pin end
    pin = MakePin(canvas)
    pins[i] = pin
    return pin
end

local lastMapID, lastScale

local function GetCanvasScale()
    if scroll.GetCanvasScale then
        local ok, s = pcall(scroll.GetCanvasScale, scroll)
        if ok and s and s > 0 then return s end
    end
    return 1
end

-- ==========================================
-- BUILT-IN NPC LOCATIONS (AetherPathfinder_Data.lua, from QuestieDB)
-- ==========================================
-- Each entry: { npcID, name, subtitle, npcFlags, faction, x, y }
-- faction: 1 = Alliance, 2 = Horde, 3 = both.

local NPC_FLAG = {
    FLIGHT = 8, INN = 128, BANK = 256, AUCTION = 4096, STABLE = 8192, REPAIR = 16384,
}
local FLAG_CATEGORY = {
    { NPC_FLAG.STABLE, "stable" }, { NPC_FLAG.FLIGHT, "flight" }, { NPC_FLAG.INN, "inn" },
    { NPC_FLAG.BANK, "bank" }, { NPC_FLAG.AUCTION, "auction" }, { NPC_FLAG.REPAIR, "repair" },
}

local seedCache = {}   -- data entry -> pin object (built the first time it's shown)
local mailCache = setmetatable({}, { __mode = "k" })   -- mailbox entry -> pin object

local function HasFlag(flags, bit)
    return flags % (bit * 2) >= bit
end

local function SeedObject(entry)
    local obj = seedCache[entry]
    if obj ~= nil then return obj or nil end
    local id, name, sub, flags, faction, x, y = unpack(entry)
    local cats = {}
    local main, forClass = Classify(sub)
    if main then cats[main] = true end
    for _, pair in ipairs(FLAG_CATEGORY) do
        if HasFlag(flags or 0, pair[1]) then cats[pair[2]] = true end
    end
    if not next(cats) then
        seedCache[entry] = false     -- a vendor we don't have a filter for
        return nil
    end
    obj = { id = id, name = name, sub = (sub ~= "" and sub or nil), cats = cats,
            x = x, y = y, exact = true, seed = true, faction = faction, forClass = forClass }
    seedCache[entry] = obj
    return obj
end

local function MyFactionCode()
    local group = UnitFactionGroup("player")
    return (group == "Alliance" and 1) or (group == "Horde" and 2) or 3
end

-- Calls fn(npc) for every NPC to show on a map: learned ones, then built-in
-- ones you haven't met yet (a learned NPC replaces its built-in copy).
local function ForEachNPC(mapID, fn)
    local learned = db and mapID and db.npcs[mapID]
    if learned then
        for id, npc in pairs(learned) do
            npc.id = npc.id or id
            fn(npc)
        end
    end
    local seed = db and db.useSeed and mapID and AetherPathfinder_Seed and AetherPathfinder_Seed[mapID]
    if seed then
        local mine = MyFactionCode()
        for _, entry in ipairs(seed) do
            local faction = entry[5]
            if not (learned and learned[entry[1]])
                    and (faction == 3 or faction == mine or db.otherFaction) then
                local obj = SeedObject(entry)
                if obj then fn(obj) end
            end
        end
    end
    -- Mailboxes: built-in ones (your faction's unless the other faction is on), then learned ones.
    if db and mapID and db.filters.mail then
        local builtIn = db.useSeed and AetherPathfinder_Mailboxes and AetherPathfinder_Mailboxes[mapID]
        if builtIn then
            local mine = MyFactionCode()
            for _, entry in ipairs(builtIn) do
                if entry[2] == 3 or entry[2] == mine or db.otherFaction then
                    local obj = mailCache[entry]
                    if not obj then
                        obj = { id = "mail" .. entry[1] .. ":" .. entry[3], name = "Mailbox", cats = { mail = true },
                                x = entry[3], y = entry[4], exact = true, seed = true, faction = entry[2] }
                        mailCache[entry] = obj
                    end
                    fn(obj)
                end
            end
        end
        for i, spot in ipairs(db.mailboxes and db.mailboxes[mapID] or {}) do
            local obj = mailCache[spot]
            if not obj then
                obj = { id = "mail:" .. mapID .. ":" .. i, name = "Mailbox", cats = { mail = true },
                        x = spot[1], y = spot[2], exact = true }
                mailCache[spot] = obj
            end
            fn(obj)
        end
    end
end

local function CountPins(mapID)
    local learned, builtIn = 0, 0
    ForEachNPC(mapID, function(npc)
        if npc.seed then builtIn = builtIn + 1 else learned = learned + 1 end
    end)
    return learned, builtIn
end

-- Markers go above everything else on the map canvas. Zone maps carry layers
-- (explored-area overlays, flight paths, quest areas) that city maps don't.
-- Is this world map pin one of Blizzard's quest markers ("!", "?", objectives)?
-- (The shaded quest areas don't count: our icons go above those.)
local function IsQuestPin(child)
    local template = child.pinTemplate
    if type(template) == "string" then
        if template:find("Blob", 1, true) then return false end
        return template:find("Quest", 1, true) or template:find("Objective", 1, true) or false
    end
    return child.questID ~= nil
end

-- Our icons sit above the map and everything else on it, but just below the
-- quest markers, so a "!" or "?" is never hidden behind an NPC icon.
local function PinLevel()
    local base, top, questFloor = canvas:GetFrameLevel(), canvas:GetFrameLevel(), nil
    for _, child in ipairs({ canvas:GetChildren() }) do
        if not child.isAetherPin then
            local level = child:GetFrameLevel()
            if level then
                if IsQuestPin(child) then
                    if not questFloor or level < questFloor then questFloor = level end
                elseif level > top then
                    top = level
                end
            end
        end
    end
    if questFloor then
        return math.max(base + 1, math.min(top + 1, questFloor - 1))
    end
    return math.min(top + 20, 9000)
end

local function LayoutPins()
    usedPins = 0
    local mapID = mapFrame:GetMapID()
    local w, h = canvas:GetWidth(), canvas:GetHeight()
    local scale = 1 / GetCanvasScale()   -- keeps pins the same size when you zoom

    if db and mapID and w > 0 and h > 0 then
        ForEachNPC(mapID, function(npc)
            local cat = npc.x and MainCategory(npc)
            if cat then
                usedPins = usedPins + 1
                local pin = GetPin(usedPins)
                pin.npc = npc
                Paint(pin, cat, npc)
                pin:SetScale(scale)
                pin:SetFrameLevel(PinLevel())
                pin:ClearAllPoints()
                pin:SetPoint("CENTER", canvas, "TOPLEFT", npc.x * w / scale, -npc.y * h / scale)
                pin:Show()
            end
        end)
    end
    for i = usedPins + 1, #pins do SetBlinking(pins[i], false); pins[i]:Hide() end
    lastMapID, lastScale, pinsDirty = mapID, GetCanvasScale(), false
end

-- Fades the world map markers your arrow is over. Runs a few times a second
-- while the map is open, since you can move with it open.
local function FadeUnderArrow()
    local mapID = mapFrame:GetMapID()
    local pos = mapID and C_Map.GetPlayerMapPosition(mapID, "player")
    local px, py
    if pos and not IsSecret(pos.x) then px, py = pos:GetXY() end
    local w, h = canvas:GetWidth(), canvas:GetHeight()
    local zoom = GetCanvasScale()
    for i = 1, usedPins do
        local pin, alpha = pins[i], 1
        local npc = pin.npc
        if px and npc and npc.x then
            -- Distance on screen: map size times zoom.
            local dx, dy = (npc.x - px) * w * zoom, (npc.y - py) * h * zoom
            if dx * dx + dy * dy < UNDER_ARROW_PX * UNDER_ARROW_PX then alpha = UNDER_ARROW_ALPHA end
        end
        pin:SetAlpha(alpha)
    end
end

-- ==========================================
-- FILTER BUTTON ON THE WORLD MAP
-- ==========================================

local function ColorText(cat)
    local c = cat.text or cat.color
    return string.format("|cff%02x%02x%02x%s|r", c[1] * 255, c[2] * 255, c[3] * 255, LabelFor(cat))
end

local function ClassChoiceText()
    local choice = db and db.trainerClass or "AUTO"
    if choice == "AUTO" or not CLASS_BY_TOKEN[choice] then
        return "Auto (" .. ClassName(SelectedClass()) .. ")"
    end
    return ClassName(choice)
end

local function SetAll(value)
    for _, cat in ipairs(CATEGORIES) do db.filters[cat.key] = value end
    pinsDirty = true
end

local function OpenFilterMenu(owner)
    if not db then return end
    MenuUtil.CreateContextMenu(owner, function(_, root)
        root:CreateTitle("Show on Map")
        local classMenu = root:CreateButton("Class: " .. ClassChoiceText())
        classMenu:CreateRadio("Auto (your character's class)",
            function() return (db.trainerClass or "AUTO") == "AUTO" end,
            function() SetClassChoice("AUTO") end)
        for _, c in ipairs(CLASS_LIST) do
            classMenu:CreateRadio(ClassName(c.token),
                function() return db.trainerClass == c.token end,
                function() SetClassChoice(c.token) end)
        end
        for _, cat in ipairs(CATEGORIES) do
            local box = root:CreateCheckbox(ColorText(cat),
                function() return db.filters[cat.key] end,
                function() db.filters[cat.key] = not db.filters[cat.key]; pinsDirty = true end)
            if cat.key == "classpet" and not HasClassPet() and box.SetEnabled then
                pcall(box.SetEnabled, box, false)
            end
        end
        root:CreateDivider()
        root:CreateButton("Show All", function() SetAll(true) end)
        root:CreateButton("Hide All", function() SetAll(false) end)
        root:CreateDivider()
        root:CreateCheckbox("Built-in NPC locations",
            function() return db.useSeed end,
            function() db.useSeed = not db.useSeed; pinsDirty = true end)
        root:CreateCheckbox("Show the other faction's NPCs",
            function() return db.otherFaction end,
            function() db.otherFaction = not db.otherFaction; pinsDirty = true end)
        root:CreateCheckbox("Show on the minimap",
            function() return db.minimap end,
            function() db.minimap = not db.minimap; rebuildIn = 0 end)
        root:CreateDivider()
        local learned, builtIn = CountPins(mapFrame:GetMapID())
        root:CreateTitle(learned .. " learned, " .. builtIn .. " built-in on this map")
    end)
end

local mapReady = false

SetupMap = function()
    if mapReady then return end
    local wm = WorldMapFrame
    local sc = wm and wm.ScrollContainer
    local child = sc and sc.Child
    if not child then return end      -- the world map isn't loaded yet; try again later
    mapFrame, scroll, canvas = wm, sc, child
    mapReady = true

    local button = AetherButton(mapFrame, "AetherPathfinderButton", true)
    button:SetSize(56, 20)
    button:SetText("NPCs")
    button:SetPoint("TOPLEFT", scroll, "TOPLEFT", 8, -8)
    button:SetFrameLevel(math.min(PinLevel() + 10, 9999))
    button:SetScript("OnClick", OpenFilterMenu)
    button:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:AddLine("AetherPathfinder", 0.3, 0.7, 1)
        GameTooltip:AddLine("Choose which NPCs to highlight.", 1, 1, 1)
        GameTooltip:AddLine("Built-in locations come from QuestieDB. NPCs you talk to "
            .. "are added too, including ones in new Forever zones.", 0.7, 0.7, 0.7, true)
        GameTooltip:Show()
    end)
    button:SetScript("OnLeave", function() GameTooltip:Hide() end)

    -- Re-place the pins when the map changes, you zoom, or a filter or NPC changes.
    local sinceCheck = 0
    mapFrame:HookScript("OnUpdate", function(_, elapsed)
        sinceCheck = sinceCheck + elapsed
        if sinceCheck < 0.1 then return end
        sinceCheck = 0
        if pinsDirty or mapFrame:GetMapID() ~= lastMapID
                or math.abs(GetCanvasScale() - (lastScale or 0)) > 0.001 then
            LayoutPins()
        end
        FadeUnderArrow()
    end)
    mapFrame:HookScript("OnShow", function() pinsDirty = true end)
end

SetupMap()   -- the world map may already be loaded

-- ==========================================
-- MINIMAP MARKERS
-- ==========================================
-- The same markers as the world map, drawn around you on the minimap. They
-- follow you as you move, turn with the minimap when "Rotate Minimap" is on,
-- scale with the minimap zoom, and are hidden past the minimap's edge.

-- Minimap diameter in yards at each zoom level (0 = most zoomed out).
local MINIMAP_YARDS = {
    outdoor = { [0] = 466 + 2/3, 400, 333 + 1/3, 266 + 2/3, 200, 133 + 1/3 },
    indoor  = { [0] = 300, 240, 180, 120, 80, 50 },
}
local NEARBY_YARDS = 1000      -- NPCs farther than this aren't considered at all

local miniPins, miniUsed = {}, 0
local nearby = {}              -- { npc, cat, wx, wy } for NPCs near you
local worldCache = setmetatable({}, { __mode = "k" })   -- npc -> { instance, x, y } or false
local function WorldPos(mapID, x, y)
    if not (C_Map.GetWorldPosFromMapPos and CreateVector2D) then return nil end
    local ok, instance, pos = pcall(C_Map.GetWorldPosFromMapPos, mapID, CreateVector2D(x, y))
    if not ok or not pos or IsSecret(pos.x) then return nil end
    return instance, pos.x, pos.y
end

local function NpcWorldPos(mapID, npc)
    local cached = worldCache[npc]
    if cached == nil then
        local instance, x, y = WorldPos(mapID, npc.x, npc.y)
        cached = instance and { instance, x, y } or false
        worldCache[npc] = cached
    end
    if cached then return cached[1], cached[2], cached[3] end
end

-- Where you are in world yards, or nil where WoW doesn't say (some instances).
local function PlayerWorldPos()
    local mapID = C_Map.GetBestMapForUnit("player")
    if not mapID then return nil end
    local pos = C_Map.GetPlayerMapPosition(mapID, "player")
    if not pos or IsSecret(pos.x) then return nil end
    local px, py = pos:GetXY()
    if not px or (px == 0 and py == 0) then return nil end
    return WorldPos(mapID, px, py)
end

local function GetMiniPin(i)
    local pin = miniPins[i]
    if pin then return pin end
    pin = MakePin(Minimap)
    pin.tooltipAnchor = "ANCHOR_LEFT"    -- the minimap sits at the right edge of the screen
    pin:SetFrameLevel(Minimap:GetFrameLevel() + 5)
    miniPins[i] = pin
    return pin
end

local function HideMiniPins(from)
    for i = from or 1, #miniPins do SetBlinking(miniPins[i], false); miniPins[i]:Hide() end
end

-- Every map that has NPCs to show (learned or built in).
local function AllMapIDs()
    local maps = {}
    for mapID in pairs(db.npcs) do maps[mapID] = true end
    if db.useSeed and AetherPathfinder_Seed then
        for mapID in pairs(AetherPathfinder_Seed) do maps[mapID] = true end
    end
    return maps
end

-- While a flight map is open, WoW lists the flight paths this character knows
-- (positions are on the flight map, usually the continent). Each one is matched
-- to the nearest flight master marker, by distance in yards.
local MATCH_YARDS = 120
local lastFlightSync = { listed = 0, placed = 0, matched = 0, mapID = nil, method = "none yet" }

-- Known flight paths on the open flight map: list of { x, y } on taxiMapID.
local function ReadTaxiNodes()
    local taxiMapID = GetTaxiMapID and GetTaxiMapID()
    if not taxiMapID or taxiMapID == 0 then
        local here = C_Map.GetBestMapForUnit("player")
        while here do                         -- fall back to the continent you're on
            local info = C_Map.GetMapInfo(here)
            if not info or info.mapType == 2 or not info.parentMapID or info.parentMapID == 0 then break end
            here = info.parentMapID
        end
        taxiMapID = here
    end
    local list, method = {}, "none"
    if taxiMapID and C_TaxiMap and C_TaxiMap.GetAllTaxiNodes then
        local ok, nodes = pcall(C_TaxiMap.GetAllTaxiNodes, taxiMapID)
        if ok and type(nodes) == "table" and #nodes > 0 then
            method = "C_TaxiMap"
            for _, node in ipairs(nodes) do   -- the flight map only lists paths you know
                local pos = node.position
                if pos and not IsSecret(pos.x) then list[#list + 1] = { pos.x, pos.y } end
            end
        end
    end
    if #list == 0 and NumTaxiNodes and TaxiNodePosition then
        method = "TaxiNode"
        for i = 1, NumTaxiNodes() or 0 do
            local kind = TaxiNodeGetType and TaxiNodeGetType(i)
            if kind ~= "NONE" then
                local x, y = TaxiNodePosition(i)
                if x and not IsSecret(x) then list[#list + 1] = { x, y } end
            end
        end
    end
    return taxiMapID, list, method
end

local function DoFlightSync()
    if not db then return end
    local taxiMapID, nodes, method = ReadTaxiNodes()
    local stats = { listed = #nodes, placed = 0, matched = 0, mapID = taxiMapID, method = method,
                    talk = lastFlightSync.talk }
    lastFlightSync = stats
    if #nodes == 0 or not taxiMapID then return end

    -- Every flight master marker with its spot in world yards.
    local masters, seen = {}, {}
    for mapID in pairs(AllMapIDs()) do
        ForEachNPC(mapID, function(npc)
            if npc.cats.flight and npc.id and npc.x and not seen[npc.id] then
                local inst, wx, wy = NpcWorldPos(mapID, npc)
                if inst then
                    seen[npc.id] = true
                    masters[#masters + 1] = { id = npc.id, inst = inst, x = wx, y = wy }
                end
            end
        end)
    end

    local known = KnownFlights()
    for _, node in ipairs(nodes) do
        local inst, wx, wy = WorldPos(taxiMapID, node[1], node[2])
        if inst then
            stats.placed = stats.placed + 1
            local best, bestDist
            for _, m in ipairs(masters) do
                if m.inst == inst then
                    local dist = (m.x - wx) ^ 2 + (m.y - wy) ^ 2
                    if not bestDist or dist < bestDist then best, bestDist = m, dist end
                end
            end
            if best and bestDist < MATCH_YARDS ^ 2 then
                known[best.id] = true
                stats.matched = stats.matched + 1
            end
        end
    end
    pinsDirty = true
    rebuildIn = 0
end

-- The flight master you're talking to is discovered. Marked by its NPC id and,
-- in case that id is hidden or differs from the built-in data, every flight
-- master marker within TALK_YARDS of where you stand.
local TALK_YARDS = 40

local function MarkTalkedTo(npcID, guid)
    local talk = { id = npcID, guidReadable = Readable(guid) and true or false }
    lastFlightSync.talk = talk
    if npcID then MarkFlightKnown(npcID) end
    local instance, px, py = PlayerWorldPos()
    talk.havePos = instance and true or false
    if not instance then return end
    local best, bestDist
    for mapID in pairs(AllMapIDs()) do
        ForEachNPC(mapID, function(npc)
            if npc.cats.flight and npc.id and npc.x then
                local inst, wx, wy = NpcWorldPos(mapID, npc)
                if inst == instance then
                    local dist = (wx - px) ^ 2 + (wy - py) ^ 2
                    -- Every marker this close is this flight master (the built-in
                    -- one and a learned copy can sit on top of each other).
                    if dist < TALK_YARDS ^ 2 then MarkFlightKnown(npc.id) end
                    if not bestDist or dist < bestDist then best, bestDist = npc, dist end
                end
            end
        end)
    end
    if best then
        talk.nearest, talk.nearestYards = best.name, math.sqrt(bestDist)
        talk.nearestID, talk.idMatches = best.id, (best.id == npcID)
    end
end

SyncFlightPaths = function(npcID, guid)
    MarkTalkedTo(npcID, guid)
    DoFlightSync()
    -- The flight map can fill in a moment after it opens; read it again shortly.
    if C_Timer and C_Timer.After then C_Timer.After(0.5, DoFlightSync) end
end

-- Collects the NPCs (from every map) within NEARBY_YARDS of you.
local function RebuildNearby()
    wipe(nearby)
    if not db or not db.minimap then return end
    local instance, px, py = PlayerWorldPos()
    if not instance then return end
    local seen = {}
    for mapID in pairs(AllMapIDs()) do
        ForEachNPC(mapID, function(npc)
            local key = npc.id or npc
            if seen[key] or not npc.x then return end
            local cat = MainCategory(npc)
            if not cat then return end
            local inst, wx, wy = NpcWorldPos(mapID, npc)
            if inst == instance and math.abs(wx - px) < NEARBY_YARDS and math.abs(wy - py) < NEARBY_YARDS then
                seen[key] = true
                nearby[#nearby + 1] = { npc = npc, cat = cat, wx = wx, wy = wy }
            end
        end)
    end
end

local function MinimapDiameter()
    if C_Minimap and C_Minimap.GetViewRadius then
        local ok, r = pcall(C_Minimap.GetViewRadius)
        if ok and r and r > 0 then return r * 2 end
    end
    local zoom = Minimap:GetZoom() or 0
    local list = (IsIndoors and IsIndoors()) and MINIMAP_YARDS.indoor or MINIMAP_YARDS.outdoor
    return list[zoom] or list[0]
end

local function LayoutMiniPins()
    miniUsed = 0
    if not db or not db.minimap or #nearby == 0 or not Minimap:IsVisible() then
        HideMiniPins(1)
        return
    end
    local instance, px, py = PlayerWorldPos()
    if not instance then HideMiniPins(1); return end

    local width = Minimap:GetWidth()
    local radius = width / 2
    local perYard = width / MinimapDiameter()
    local round = not (GetMinimapShape and GetMinimapShape() ~= "ROUND")
    local limit = radius - PIN_SIZE / 2

    local sin, cos
    if GetCVar("rotateMinimap") == "1" then
        local facing = GetPlayerFacing and GetPlayerFacing()
        if not facing or IsSecret(facing) then HideMiniPins(1); return end
        -- The minimap turns so the way you face is up.
        sin, cos = math.sin(-facing), math.cos(-facing)
    end

    for _, item in ipairs(nearby) do
        -- World x points north and world y points west.
        local east  = (py - item.wy) * perYard
        local north = (item.wx - px) * perYard
        if sin then
            east, north = east * cos - north * sin, east * sin + north * cos
        end
        local inside
        if round then
            inside = east * east + north * north <= limit * limit
        else
            inside = math.abs(east) <= limit and math.abs(north) <= limit
        end
        if inside then
            miniUsed = miniUsed + 1
            local pin = GetMiniPin(miniUsed)
            pin.npc = item.npc
            Paint(pin, item.cat, item.npc)
            pin:SetAlpha(east * east + north * north < UNDER_ARROW_PX * UNDER_ARROW_PX
                and UNDER_ARROW_ALPHA or 1)
            pin:ClearAllPoints()
            pin:SetPoint("CENTER", Minimap, "CENTER", east, north)
            pin:Show()
        end
    end
    HideMiniPins(miniUsed + 1)
end

local miniDriver = CreateFrame("Frame")
miniDriver:SetScript("OnUpdate", function(_, elapsed)
    rebuildIn = rebuildIn - elapsed
    if rebuildIn <= 0 then
        rebuildIn = 1          -- filters, zone and newly learned NPCs show up within a second
        RebuildNearby()
    end
    LayoutMiniPins()
end)
miniDriver:RegisterEvent("ZONE_CHANGED_NEW_AREA")
miniDriver:RegisterEvent("PLAYER_ENTERING_WORLD")
miniDriver:SetScript("OnEvent", function() rebuildIn = 0 end)


-- ==========================================
-- SLASH COMMANDS
-- ==========================================

SLASH_AETHERPATHFINDER1 = "/pfm"
SLASH_AETHERPATHFINDER2 = "/aetherpathfinder"

SlashCmdList["AETHERPATHFINDER"] = function(msg)
    local command = (msg:match("^(%S*)") or ""):lower()
    local prefix = "|cff4da6ffAetherPathfinder:|r "
    if not db then return end

    if command == "stats" then
        local maps, total = 0, 0
        for _, list in pairs(db.npcs) do
            maps = maps + 1
            for _ in pairs(list) do total = total + 1 end
        end
        local seedTotal, seedMaps = 0, 0
        for _, list in pairs(AetherPathfinder_Seed or {}) do
            seedMaps = seedMaps + 1
            seedTotal = seedTotal + #list
        end
        print(prefix .. total .. " NPCs learned across " .. maps .. " maps, plus "
            .. seedTotal .. " built-in locations across " .. seedMaps .. " maps"
            .. (db.useSeed and "." or " (turned off)."))
        local info = AetherPathfinder_SeedInfo or {}
        if info.source == "downloaded" then
            print(prefix .. "Built-in data: downloaded from QuestieDB, " .. tostring(info.version) .. ".")
        else
            print(prefix .. "Built-in data: the copy bundled with the addon"
                .. (info.problem and (" (download couldn't be used: " .. info.problem .. ")") or "")
                .. ". To keep it up to date automatically, run the setup command in AetherAddons-README.txt.")
        end
    elseif command == "debug" then
        -- Report what the world map is doing, to track down missing markers.
        if not mapReady then
            print(prefix .. "the world map hasn't loaded yet. Open it once (M), then try again.")
            return
        end
        local mapID = mapFrame:GetMapID()
        local info = mapID and C_Map.GetMapInfo and C_Map.GetMapInfo(mapID)
        print(prefix .. "map " .. tostring(mapID) .. " (" .. tostring(info and info.name) .. ")"
            .. ", you are " .. tostring(UnitFactionGroup("player"))
            .. ", class filters follow " .. ClassName(SelectedClass()))
        local seed = AetherPathfinder_Seed and AetherPathfinder_Seed[mapID]
        local learned = db.npcs[mapID]
        local learnedCount = 0
        for _ in pairs(learned or {}) do learnedCount = learnedCount + 1 end
        local listed, withFilter = 0, 0
        ForEachNPC(mapID, function(npc)
            listed = listed + 1
            if MainCategory(npc) then withFilter = withFilter + 1 end
        end)
        print(prefix .. "built-in for this map: " .. (seed and #seed or 0)
            .. (db.useSeed and "" or " (turned off)") .. ", learned: " .. learnedCount
            .. ", your faction's: " .. listed .. ", with a filter turned on: " .. withFilter)
        local shown, sampleLevel = 0, nil
        for i = 1, usedPins do
            if pins[i]:IsShown() then shown = shown + 1; sampleLevel = sampleLevel or pins[i]:GetFrameLevel() end
        end
        local topOther = 0
        for _, child in ipairs({ canvas:GetChildren() }) do
            if not child.isAetherPin then topOther = math.max(topOther, child:GetFrameLevel() or 0) end
        end
        print(prefix .. string.format("markers drawn: %d, marker level: %s, highest other map layer: %d, "
            .. "map size: %.0f x %.0f, zoom: %.2f", shown, tostring(sampleLevel), topOther,
            canvas:GetWidth(), canvas:GetHeight(), GetCanvasScale()))
        if shown > 0 then
            local p1 = pins[1]
            print(prefix .. string.format("first marker: %s at %.1f, %.1f",
                tostring(p1.npc and p1.npc.name), (p1.npc and p1.npc.x or 0) * 100, (p1.npc and p1.npc.y or 0) * 100))
        end
    elseif command == "flights" then
        local st = lastFlightSync
        local count = 0
        for _ in pairs(KnownFlights()) do count = count + 1 end
        print(prefix .. count .. " flight masters marked discovered on this character.")
        print(prefix .. string.format("last flight map: %d known paths listed (%s, map %s), "
            .. "%d placed on the map, %d matched to a flight master.",
            st.listed, st.method, tostring(st.mapID), st.placed, st.matched))
        local t = st.talk
        if t then
            print(prefix .. string.format("flight master you talked to: id %s (readable: %s), your position: %s, "
                .. "nearest marker: %s (id %s) %.0f yards away, ids match: %s.",
                tostring(t.id), tostring(t.guidReadable), t.havePos and "yes" or "no",
                tostring(t.nearest), tostring(t.nearestID), t.nearestYards or -1, tostring(t.idMatches)))
        else
            print(prefix .. "no flight master talked to since the last /reload.")
        end
    elseif command == "clearzone" then
        local mapID = C_Map.GetBestMapForUnit("player")
        if mapID then
            db.npcs[mapID] = nil
            if db.mailboxes then db.mailboxes[mapID] = nil end
            pinsDirty = true
            print(prefix .. "Forgot every NPC in this zone.")
        end
    elseif command == "reset" then
        db.npcs = {}
        db.mailboxes = {}
        pinsDirty = true
        print(prefix .. "Forgot every NPC.")
    else
        print(prefix .. "/pfm stats, /pfm debug, /pfm flights, /pfm clearzone, /pfm reset. Use the NPCs button on the world map to filter.")
    end
end

-- ==========================================
-- FOR AETHERHUB
-- ==========================================

AetherPathfinder_API = {
    classes        = (function()
        local list = {}
        for _, c in ipairs(CLASS_LIST) do list[#list + 1] = c.token end
        return list
    end)(),
    ClassName      = ClassName,
    SelectedClass  = SelectedClass,
    HasClassPet    = HasClassPet,
    GetClassChoice = function() return db and db.trainerClass or "AUTO" end,
    SetClassChoice = SetClassChoice,
    LabelFor       = function(key) return CATEGORY_BY_KEY[key] and LabelFor(CATEGORY_BY_KEY[key]) or key end,
    Refresh        = function() pinsDirty = true; rebuildIn = 0 end,

    -- For AetherLedger's travel directions. Positions are 0 to 1 on mapID.
    -- Flight masters your faction can use, with known = true for paths this character has.
    FlightMasters  = function()
        local list, seen = {}, {}
        if not db then return list end
        local mine = MyFactionCode()
        for mapID in pairs(AllMapIDs()) do
            ForEachNPC(mapID, function(npc)
                if npc.cats and npc.cats.flight and npc.id and npc.x and not seen[npc.id]
                        and (not npc.faction or npc.faction == 3 or npc.faction == mine) then
                    seen[npc.id] = true
                    list[#list + 1] = { id = npc.id, name = npc.name, map = mapID, x = npc.x, y = npc.y,
                                        known = KnownFlights()[npc.id] == true }
                end
            end)
        end
        return list
    end,
    -- Trainers whose title has one of words (and, if given, one of titleWords).
    Trainers       = function(words, titleWords)
        local list, seen = {}, {}
        if not db then return list end
        local mine = MyFactionCode()
        local function Has(text, set)
            for _, w in ipairs(set) do if text:find(w, 1, true) then return true end end
            return false
        end
        for mapID in pairs(AllMapIDs()) do
            ForEachNPC(mapID, function(npc)
                local sub = npc.sub and npc.sub:lower()
                if sub and npc.x and not seen[npc.id or npc] and Has(sub, words)
                        and not sub:find("suppl", 1, true)
                        and (sub:find("trainer", 1, true) or Has(sub, { "journeyman", "expert", "artisan", "master" }))
                        and (not titleWords or Has(sub, titleWords))
                        and (not npc.faction or npc.faction == 3 or npc.faction == mine) then
                    seen[npc.id or npc] = true
                    list[#list + 1] = { name = npc.name, sub = npc.sub, map = mapID, x = npc.x, y = npc.y }
                end
            end)
        end
        return list
    end,
}
