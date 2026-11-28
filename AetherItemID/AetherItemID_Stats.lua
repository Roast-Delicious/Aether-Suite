-- ==========================================
-- AetherItemID: key stats in item tooltips
-- The stats that matter to your class show in Aether gold with two small
-- gold chevrons after them, pointing back at the stat. Equip lines keep
-- Blizzard's green and get the chevrons (user Nov 27, option B of
-- mock/stat_gold.py). Item tooltips only. Each class starts with a list;
-- tick stats on or off per character on AetherHub's Bags & Items page.
-- ==========================================

local MEDIA = "Interface\\AddOns\\AetherItemID\\Media\\"
local GOLD = { 1, 0.69, 0 }

-- key, label, words to find (lowercase, plain text)
local STATS = {
    { "str",  "Strength",        { "strength" } },
    { "agi",  "Agility",         { "agility" } },
    { "sta",  "Stamina",         { "stamina" } },
    { "int",  "Intellect",       { "intellect" } },
    { "spi",  "Spirit",          { "spirit" } },
    { "ap",   "Attack Power",    { "attack power" } },
    { "crit", "Critical strike", { "critical strike" } },
    { "hit",  "Hit chance",      { "chance to hit", "hit rating" } },
    { "sp",   "Spell power",     { "spell power", "damage and healing done by magical spells", "damage done by" } },
    { "heal", "Healing",         { "healing done by", "increases healing" } },
    { "mp5",  "Mana per 5 sec",  { "mana per 5", "mana every 5" } },
    { "def",  "Defense",         { "defense" } },
}
local BY_KEY = {}
for _, s in ipairs(STATS) do BY_KEY[s[1]] = s end

local CLASS = {
    HUNTER  = { agi = true, sta = true, ap = true, crit = true, hit = true },
    ROGUE   = { agi = true, sta = true, ap = true, crit = true, hit = true },
    WARRIOR = { str = true, sta = true, agi = true, ap = true, crit = true, hit = true, def = true },
    PALADIN = { str = true, sta = true, int = true, crit = true, heal = true },
    SHAMAN  = { int = true, sta = true, agi = true, str = true, sp = true, heal = true, mp5 = true },
    DRUID   = { int = true, sta = true, agi = true, spi = true, heal = true, sp = true },
    PRIEST  = { int = true, spi = true, sta = true, heal = true, sp = true, mp5 = true },
    MAGE    = { int = true, sta = true, spi = true, sp = true, crit = true, hit = true },
    WARLOCK = { int = true, sta = true, sp = true, crit = true, hit = true },
}

local function DB() AetherItemIDDB = AetherItemIDDB or {}; return AetherItemIDDB end
local function CharKey() return (UnitName("player") or "?") .. "-" .. ((GetRealmName and GetRealmName()) or "?") end
local function Picks()
    local db = DB()
    db.statPicks = db.statPicks or {}
    db.statPicks[CharKey()] = db.statPicks[CharKey()] or {}
    return db.statPicks[CharKey()]
end
local function ClassDefault(key)
    local _, cls = UnitClass("player")
    local d = CLASS[cls or ""]
    return d and d[key] or false
end
local function IsOn(key)
    local v = Picks()[key]
    if v == nil then return ClassDefault(key) end
    return v
end
local function Enabled() return DB().keyStats ~= false end

-- Which picked stat a tooltip line names, if any.
local function Match(text)
    local low = text:lower()
    for _, s in ipairs(STATS) do
        if IsOn(s[1]) then
            for _, w in ipairs(s[3]) do
                if low:find(w, 1, true) then return s[1] end
            end
        end
    end
end

-- Chevrons: a pool per tooltip, hidden before each tooltip is filled.
local pools = setmetatable({}, { __mode = "k" })
local function Chevrons(tip, i)
    local pool = pools[tip]
    if not pool then pool = {}; pools[tip] = pool end
    local c = pool[i]
    if not c then
        c = {}
        for k = 1, 2 do
            local dark = tip:CreateTexture(nil, "ARTWORK", nil, 6)
            dark:SetTexture(MEDIA .. "chev58_left_dark"); dark:SetVertexColor(0, 0, 0, 1)
            local gold = tip:CreateTexture(nil, "ARTWORK", nil, 7)
            -- the 3D bevel art, already gold, untinted (the suite's chevrons
            -- are all the 3D kind; tools/chev3d_test.py)
            gold:SetTexture(MEDIA .. "chev58_left_gold3d"); gold:SetVertexColor(1, 1, 1, 1)
            c[#c + 1] = dark; c[#c + 1] = gold
        end
        pool[i] = c
    end
    return c
end
local function HideAll(tip)
    for _, c in pairs(pools[tip] or {}) do for _, t in ipairs(c) do t:Hide() end end
end

local function Mark(tip)
    HideAll(tip)
    if not Enabled() then return end
    local name = tip.GetName and tip:GetName()
    if not name or not tip.NumLines then return end
    for i = 2, tip:NumLines() do
        local fs = _G[name .. "TextLeft" .. i]
        local ok, text = pcall(function() return fs and fs:IsShown() and fs:GetText() end)
        local plain = ok and type(text) == "string" and not (issecretvalue and issecretvalue(text))
            and text:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", "") or nil
        -- only real stat lines ("+8 Agility") and Equip/Use lines; flavor
        -- text that mentions a stat is left alone
        local statLine = plain and plain:find("^[%+%-]%d")
        local equip = plain and (plain:find("^Equip:") or plain:find("^Use:") or plain:find("^Chance on hit:"))
        if (statLine or equip) and Match(plain) then
            if statLine and fs.SetTextColor then fs:SetTextColor(GOLD[1], GOLD[2], GOLD[3]) end
            local h = select(2, fs:GetFont()) or 12
            local size = math.floor(h * 1.25 + 0.5)
            local w = fs:GetStringWidth() or 0
            local c = Chevrons(tip, i)
            for k = 1, 2 do
                local x = w + 3 + (k - 1) * size * 0.38
                for j = 0, 1 do
                    local t = c[(k - 1) * 2 + 1 + j]
                    t:SetSize(size, size); t:ClearAllPoints()
                    t:SetPoint("LEFT", fs, "LEFT", x, 0); t:Show()
                end
            end
        end
    end
end
AetherItemID_MarkStats = Mark      -- for tests

if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall and Enum and Enum.TooltipDataType then
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, function(tip) pcall(Mark, tip) end)
else
    for _, n in ipairs({ "GameTooltip", "ItemRefTooltip", "ShoppingTooltip1", "ShoppingTooltip2" }) do
        local t = _G[n]
        if t and t.HookScript then pcall(t.HookScript, t, "OnTooltipSetItem", function(self) pcall(Mark, self) end) end
    end
end
for _, n in ipairs({ "GameTooltip", "ItemRefTooltip", "ShoppingTooltip1", "ShoppingTooltip2" }) do
    local t = _G[n]
    if t and t.HookScript then pcall(t.HookScript, t, "OnTooltipCleared", function(self) HideAll(self) end) end
end

-- For AetherHub's Bags & Items page.
AetherItemID_Stats = {
    List = function() local l = {}; for i, s in ipairs(STATS) do l[i] = { key = s[1], label = s[2] } end; return l end,
    IsOn = IsOn,
    Set = function(key, on) if BY_KEY[key] then Picks()[key] = on and true or false end end,
    Enabled = Enabled,
    SetEnabled = function(on) DB().keyStats = on and true or false end,
    ClassDefaults = function() wipe(Picks()) end,
}
