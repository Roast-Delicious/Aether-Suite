-- ==========================================
-- AetherItemID - hover an item in your bags or bank for a moment and a small
-- window shows what it's good for: the quests that need it (or that it's safe
-- to discard), which professions craft with it, whether it's soulbound, how
-- many you have and what a vendor pays for it.
-- ==========================================

local ADDON = ...
local PREFIX = "|cff4da6ffAetherItemID:|r "

local defaults = {
    enabled = true,
    delay   = 1,       -- seconds to hover before the window opens
}
local db

-- Colors
local GOLD    = { 1, 0.82, 0 }
local WHITE   = { 1, 1, 1 }
local GRAY    = { 0.6, 0.6, 0.6 }
local GREEN   = { 0.35, 1, 0.35 }
local RED     = { 1, 0.25, 0.25 }
local ORANGE  = { 1, 0.55, 0.1 }
local YELLOW  = { 1, 1, 0.35 }

local PROFESSIONS = {
    [1] = "First Aid", [2] = "Blacksmithing", [3] = "Leatherworking", [4] = "Alchemy",
    [5] = "Herbalism", [6] = "Cooking", [7] = "Mining", [8] = "Tailoring",
    [9] = "Engineering", [10] = "Enchanting", [11] = "Fishing", [12] = "Skinning",
    [13] = "Poisons",
}

local MAX_RECIPES_SHOWN = 5   -- per profession you have; other professions show a count

local function CharKey()
    return (UnitName("player") or "?") .. "-" .. ((GetRealmName and GetRealmName()) or "?")
end

-- ==========================================
-- GAME LOOKUPS (newer and older API names)
-- ==========================================

local function SpellName(spellID)
    if C_Spell and C_Spell.GetSpellName then return C_Spell.GetSpellName(spellID) end
    return GetSpellInfo and (GetSpellInfo(spellID))
end

local function ItemInfo(item)
    if C_Item and C_Item.GetItemInfo then return C_Item.GetItemInfo(item) end
    return GetItemInfo(item)
end

local function ItemClass(itemID)
    local getInstant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant
    if not getInstant then return nil end
    local _, _, _, _, _, classID = getInstant(itemID)
    return classID
end

local function ItemCount(itemID, includeBank)
    if C_Item and C_Item.GetItemCount then return C_Item.GetItemCount(itemID, includeBank) end
    return GetItemCount(itemID, includeBank)
end

-- itemID, stack count, hyperlink and whether it's bound, for a bag slot.
local function SlotInfo(bag, slot)
    if C_Container and C_Container.GetContainerItemInfo then
        local info = C_Container.GetContainerItemInfo(bag, slot)
        if not info then return nil end
        local bound = info.isBound
        if bound == nil and C_Item and C_Item.IsBound and ItemLocation then
            local ok, b = pcall(C_Item.IsBound, ItemLocation:CreateFromBagAndSlot(bag, slot))
            if ok then bound = b end
        end
        return info.itemID, info.stackCount or 1, info.hyperlink, bound
    end
    local _, count, _, _, _, _, link, _, _, itemID = GetContainerItemInfo(bag, slot)
    return itemID, count or 1, link, nil
end

local function QuestCompleted(questID)
    if C_QuestLog and C_QuestLog.IsQuestFlaggedCompleted then
        return C_QuestLog.IsQuestFlaggedCompleted(questID)
    end
    return IsQuestFlaggedCompleted and IsQuestFlaggedCompleted(questID)
end

local function QuestName(questID)
    local name = AetherItemID_QuestNames and AetherItemID_QuestNames[questID]
    if not name and C_QuestLog and C_QuestLog.GetTitleForQuestID then
        name = C_QuestLog.GetTitleForQuestID(questID)
    end
    return name or ("quest " .. questID)
end

-- Every quest in your log: { id, title, objectives = { {text, done}, ... } }
local function QuestLog()
    local out = {}
    if C_QuestLog and C_QuestLog.GetNumQuestLogEntries and C_QuestLog.GetInfo then
        for i = 1, C_QuestLog.GetNumQuestLogEntries() do
            local info = C_QuestLog.GetInfo(i)
            if info and not info.isHeader and info.questID then
                local q = { id = info.questID, title = info.title, objectives = {} }
                for _, o in ipairs(C_QuestLog.GetQuestObjectives(info.questID) or {}) do
                    q.objectives[#q.objectives + 1] = { o.text or "", o.finished }
                end
                out[#out + 1] = q
            end
        end
    elseif GetNumQuestLogEntries then
        for i = 1, GetNumQuestLogEntries() do
            local title, _, _, isHeader, _, _, _, questID = GetQuestLogTitle(i)
            if title and not isHeader then
                local q = { id = questID, title = title, objectives = {} }
                for o = 1, (GetNumQuestLeaderBoards(i) or 0) do
                    local text, _, done = GetQuestLogLeaderBoard(o, i)
                    q.objectives[#q.objectives + 1] = { text or "", done }
                end
                out[#out + 1] = q
            end
        end
    end
    return out
end

-- Your professions: { ["Tailoring"] = skill, ... }
local function MyProfessions()
    local out = {}
    if GetProfessions and GetProfessionInfo then
        for _, index in pairs({ GetProfessions() }) do
            if index then
                local name, _, skill = GetProfessionInfo(index)
                if name then out[name] = skill or 0 end
            end
        end
    end
    if next(out) == nil and GetNumSkillLines and GetSkillLineInfo then
        local known = {}
        for _, name in pairs(PROFESSIONS) do known[name] = true end
        for i = 1, GetNumSkillLines() do
            local name, isHeader, _, rank = GetSkillLineInfo(i)
            if name and not isHeader and known[name] then out[name] = rank or 0 end
        end
    end
    return out
end

-- ==========================================
-- LEARNING YOUR RECIPES
-- ==========================================
-- The built-in recipe list is Classic's. When you open a profession window,
-- the recipes you know are read from the game, so recipes WoW Forever added
-- show up too, and the ones you know are marked.

local function ItemIDFromLink(link)
    return link and tonumber(link:match("item:(%d+)"))
end

local function Remember(profession, recipe, reagentIDs)
    if not db or not profession or not recipe then return end
    db.learned = db.learned or {}
    db.known = db.known or {}
    local who = CharKey()
    db.known[who] = db.known[who] or {}
    db.known[who][recipe] = true
    for _, itemID in ipairs(reagentIDs) do
        db.learned[itemID] = db.learned[itemID] or {}
        db.learned[itemID][recipe] = profession
    end
end

local function ScanTradeSkills()
    -- Newer profession window
    if C_TradeSkillUI and C_TradeSkillUI.GetAllRecipeIDs and C_TradeSkillUI.GetRecipeSchematic then
        local profession
        if C_TradeSkillUI.GetBaseProfessionInfo then
            local info = C_TradeSkillUI.GetBaseProfessionInfo()
            profession = info and info.professionName
        end
        profession = profession or (GetTradeSkillLine and GetTradeSkillLine())
        for _, recipeID in ipairs(C_TradeSkillUI.GetAllRecipeIDs() or {}) do
            local info = C_TradeSkillUI.GetRecipeInfo(recipeID)
            if info and info.learned then
                local reagents = {}
                local schematic = C_TradeSkillUI.GetRecipeSchematic(recipeID, false)
                for _, slotInfo in ipairs(schematic and schematic.reagentSlotSchematics or {}) do
                    local r = slotInfo.reagents and slotInfo.reagents[1]
                    if r and r.itemID then reagents[#reagents + 1] = r.itemID end
                end
                Remember(profession, info.name, reagents)
            end
        end
        return
    end
    -- Classic profession window
    if GetNumTradeSkills and GetTradeSkillLine then
        local profession = GetTradeSkillLine()
        for i = 1, GetNumTradeSkills() do
            local name, kind = GetTradeSkillInfo(i)
            if name and kind ~= "header" then
                local reagents = {}
                for r = 1, (GetTradeSkillNumReagents(i) or 0) do
                    local id = ItemIDFromLink(GetTradeSkillReagentItemLink(i, r))
                    if id then reagents[#reagents + 1] = id end
                end
                Remember(profession, name, reagents)
            end
        end
    end
end

local function ScanCrafts()   -- Classic Enchanting uses its own window
    if not (GetNumCrafts and GetCraftDisplaySkillLine) then return end
    local profession = GetCraftDisplaySkillLine()
    for i = 1, GetNumCrafts() do
        local name, _, kind = GetCraftInfo(i)
        if name and kind ~= "header" then
            local reagents = {}
            for r = 1, (GetCraftNumReagents(i) or 0) do
                local id = ItemIDFromLink(GetCraftReagentItemLink(i, r))
                if id then reagents[#reagents + 1] = id end
            end
            Remember(profession, name, reagents)
        end
    end
end

-- ==========================================
-- WHAT TO SHOW
-- ==========================================

-- Builds the window's lines for an item: list of { text, color, indent }.
local function Describe(itemID, count, link, bound)
    local lines = {}
    local function Add(text, color, indent) lines[#lines + 1] = { text, color or WHITE, indent or 0 } end

    local name, _, quality, _, _, _, _, _, _, _, sellPrice = ItemInfo(link or itemID)
    local qr, qg, qb = 1, 1, 1
    if quality and GetItemQualityColor then qr, qg, qb = GetItemQualityColor(quality) end
    Add(name or ("item " .. itemID), { qr, qg, qb })

    -- Soulbound
    if bound ~= nil then
        Add(bound and "Soulbound" or "Not soulbound", ORANGE)
    end

    -- How many you have
    local inBags = ItemCount(itemID, false) or count
    local total = ItemCount(itemID, true) or inBags
    local inBank = math.max(0, total - inBags)
    Add(string.format("You have %d  (bags %d, bank %d)", total, inBags, inBank))

    -- Vendor price
    if sellPrice and sellPrice > 0 and GetCoinTextureString then
        local each = GetCoinTextureString(sellPrice)
        if count and count > 1 then
            Add("Vendor price: " .. each .. " each, " .. GetCoinTextureString(sellPrice * count) .. " for this stack")
        else
            Add("Vendor price: " .. each)
        end
    elseif sellPrice == 0 then
        Add("Vendors won't buy this", GRAY)
    end

    -- Quests
    local questLines = {}
    local function QAdd(text, color, indent) questLines[#questLines + 1] = { text, color, indent } end
    local log = QuestLog()
    local inLog = {}
    for _, q in ipairs(log) do inLog[q.id] = q end

    local neededNow = false
    local wanted = {}
    for _, qid in ipairs(AetherItemID_QuestNeeds and AetherItemID_QuestNeeds[itemID] or {}) do wanted[qid] = true end
    for _, q in ipairs(log) do
        local progress
        for _, o in ipairs(q.objectives) do
            if name and o[1]:find(name, 1, true) then progress = o[1] end
        end
        if progress or wanted[q.id] then
            neededNow = true
            QAdd("Needed for: " .. (q.title or QuestName(q.id)), GREEN)
            if progress then QAdd(progress, WHITE, 1) end
        end
    end

    local starts = AetherItemID_StartsQuest and AetherItemID_StartsQuest[itemID]
    if starts then
        if QuestCompleted(starts) then
            QAdd("Starts \"" .. QuestName(starts) .. "\", which you've already done: safe to discard", RED)
        elseif inLog[starts] then
            QAdd("Starts \"" .. QuestName(starts) .. "\" (already in your quest log)", YELLOW)
        else
            QAdd("Starts a quest: " .. QuestName(starts), YELLOW)
            neededNow = true
        end
    end

    local isQuestItem = ItemClass(itemID) == 12      -- 12 = Quest
    if isQuestItem and not neededNow and not starts then
        QAdd("Not needed by any quest in your log: safe to discard", RED)
        local others = {}
        for qid in pairs(wanted) do
            if not QuestCompleted(qid) then others[#others + 1] = QuestName(qid) end
        end
        table.sort(others)
        if #others > 0 then
            QAdd("(Used by " .. table.concat(others, ", ", 1, math.min(#others, 3))
                .. (#others > 3 and ", ..." or "") .. ", which you don't have)", GRAY, 1)
        end
    end
    if #questLines > 0 then
        Add(" ")
        Add("Quests", GOLD)
        for _, l in ipairs(questLines) do lines[#lines + 1] = l end
    end

    -- Crafting
    local byProf, seen = {}, {}
    local function Use(profName, recipe, skill)
        if not profName or not recipe or seen[profName .. recipe] then return end
        seen[profName .. recipe] = true
        byProf[profName] = byProf[profName] or {}
        table.insert(byProf[profName], { recipe, skill })
    end
    for _, use in ipairs(AetherItemID_Uses and AetherItemID_Uses[itemID] or {}) do
        Use(PROFESSIONS[use[2]], SpellName(use[1]), use[3])
    end
    for recipe, profName in pairs(db.learned and db.learned[itemID] or {}) do Use(profName, recipe) end

    if next(byProf) then
        Add(" ")
        Add("Used in crafting", GOLD)
        local mine = MyProfessions()
        local known = db.known and db.known[CharKey()] or {}
        local names = {}
        for profName in pairs(byProf) do names[#names + 1] = profName end
        table.sort(names, function(a, b)
            if (mine[a] ~= nil) ~= (mine[b] ~= nil) then return mine[a] ~= nil end
            return a < b
        end)
        for _, profName in ipairs(names) do
            local list = byProf[profName]
            local mySkill = mine[profName]
            if mySkill then
                -- Recipes you know first, then the ones nearest your skill:
                -- those you can make (highest first), then the next ones up.
                local function Rank(r)
                    if known[r[1]] then return 0, -(r[2] or 0) end
                    local skill = r[2] or mySkill
                    if skill <= mySkill then return 1, -skill end
                    return 2, skill
                end
                table.sort(list, function(a, b)
                    local ga, ka = Rank(a)
                    local gb, kb = Rank(b)
                    if ga ~= gb then return ga < gb end
                    if ka ~= kb then return ka < kb end
                    return a[1] < b[1]
                end)
            else
                table.sort(list, function(a, b) return (a[2] or 999) < (b[2] or 999) end)
            end
            local plural = #list == 1 and "1 recipe" or (#list .. " recipes")
            if mine[profName] then
                Add(profName .. " (yours, skill " .. mine[profName] .. "): " .. plural, YELLOW)
                for i = 1, math.min(#list, MAX_RECIPES_SHOWN) do
                    local recipe, skill = list[i][1], list[i][2]
                    Add(recipe .. (skill and (" (" .. skill .. ")") or ""),
                        known[recipe] and GREEN or WHITE, 1)
                end
                if #list > MAX_RECIPES_SHOWN then Add("and " .. (#list - MAX_RECIPES_SHOWN) .. " more", GRAY, 1) end
            else
                Add(profName .. ": " .. plural, GRAY)
            end
        end
    end
    return lines
end

-- ==========================================
-- THE WINDOW
-- ==========================================

-- The Aether window look (same as AetherHub): soft blue halo, inner frame line,
-- title strip with a gold underline, gold corner brackets and a gold gem.
local function AetherDecorate(frame, titleHeight)
    if frame.aetherTrim then return end
    frame.aetherTrim = true
    -- The Aether window look: rounded corners, a blue edge with a fine inner
    -- line, a soft blue glow, a navy title strip with a gold underline, and
    -- gold chevrons at 12, 3, 6 and 9. Smooth images (Media\win_*), so it
    -- stays crisp at any UI scale.
    local MEDIA, WHITE = "Interface\\AddOns\\AetherItemID\\Media\\", "Interface\\Buttons\\WHITE8X8"
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
        local line = Tex("BORDER", 2, WHITE, { 1, 0.82, 0, 0.7 })
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
        for _, g in ipairs({ { "dark", { 0.04, 0.05, 0.07, 1 }, 6 }, { "gold", { 1, 0.82, 0, 1 }, 7 } }) do
            local ch = Tex("OVERLAY", g[3], MEDIA .. "win_chev_" .. g[1], g[2])
            ch:SetSize(c[6], c[6])
            ch:SetPoint("CENTER", frame, c[2], c[3], c[4])
            if c[5] ~= 0 and ch.SetRotation then ch:SetRotation(c[5]) end   -- positive turns counter-clockwise
            set[#set + 1] = ch
        end
        frame.aetherChevrons[c[1]] = set
    end
end

local window = CreateFrame("Frame", "AetherItemIDFrame", UIParent, "BackdropTemplate")
window:SetFrameStrata("TOOLTIP")
window:SetClampedToScreen(true)
window:Hide()
if window.SetBackdrop then
    window:SetBackdrop({
        bgFile = "Interface\\Buttons\\WHITE8X8", edgeFile = "Interface\\Buttons\\WHITE8X8", edgeSize = 1,
    })
    window:SetBackdropColor(0.05, 0.05, 0.08, 0.92)
    window:SetBackdropBorderColor(0.3, 0.7, 1, 0.8)
end
AetherDecorate(window, 0)

-- Text is 10% larger than the game's standard small tooltip text.
local TEXT_SCALE = 1.1
local WIDTH, PAD = math.floor(280 * TEXT_SCALE), 8

local function ScaledFont(name, base)
    local font = CreateFont(name)
    font:CopyFontObject(base)
    local file, size, flags = font:GetFont()
    if file and size then font:SetFont(file, size * TEXT_SCALE, flags or "") end
    return font
end
local TITLE_FONT = ScaledFont("AetherItemIDTitleFont", GameFontNormal)
local TEXT_FONT = ScaledFont("AetherItemIDTextFont", GameFontHighlightSmall)
local rows = {}
local function Row(i)
    if rows[i] then return rows[i] end
    local fs = window:CreateFontString(nil, "OVERLAY")
    fs:SetFontObject(TEXT_FONT)
    fs:SetJustifyH("LEFT")
    fs:SetWordWrap(true)
    rows[i] = fs
    return fs
end

local function Fill(lines)
    local y = -PAD
    for i, line in ipairs(lines) do
        local fs = Row(i)
        local indent = (line[3] or 0) * 12
        fs:ClearAllPoints()
        fs:SetPoint("TOPLEFT", window, "TOPLEFT", PAD + indent, y)
        fs:SetWidth(WIDTH - PAD * 2 - indent)
        fs:SetFontObject(i == 1 and TITLE_FONT or TEXT_FONT)
        fs:SetText(line[1])
        fs:SetTextColor(line[2][1], line[2][2], line[2][3])
        fs:Show()
        y = y - (fs:GetStringHeight() or 12) - 2
    end
    for i = #lines + 1, #rows do rows[i]:Hide() end
    window:SetSize(WIDTH, -y + PAD - 2)
end

-- Next to the item tooltip, wherever it fits on screen without covering your
-- mouse cursor or the tooltip: right of the tooltip, then left, above, below.
local CURSOR_MARGIN = 24   -- keep at least this far from the cursor
local GAP = 4

local function CursorXY()
    local x, y = GetCursorPosition()
    local scale = UIParent:GetEffectiveScale()
    return x / scale, y / scale
end

-- The tooltip's edges in UIParent's coordinates.
local function TooltipEdges()
    local l, r, t, b = GameTooltip:GetLeft(), GameTooltip:GetRight(), GameTooltip:GetTop(), GameTooltip:GetBottom()
    if not (l and r and t and b) then return nil end
    local k = GameTooltip:GetEffectiveScale() / UIParent:GetEffectiveScale()
    return l * k, r * k, t * k, b * k
end

local function CoversCursor(x, y, w, h)   -- x, y: the window's top-left corner
    local cx, cy = CursorXY()
    return cx > x - CURSOR_MARGIN and cx < x + w + CURSOR_MARGIN
        and cy < y + CURSOR_MARGIN and cy > y - h - CURSOR_MARGIN
end

local function Place()
    local w, h = window:GetWidth(), window:GetHeight()
    local screenW, screenH = UIParent:GetWidth(), UIParent:GetHeight()
    local l, r, t, b = TooltipEdges()
    window:ClearAllPoints()
    if not l then
        window:SetPoint("TOPLEFT", GameTooltip, "TOPRIGHT", GAP, 0)
        return
    end
    local spots = {
        { r + GAP, t },          -- right of the tooltip
        { l - GAP - w, t },      -- left of it
        { l, t + GAP + h },      -- above it
        { l, b - GAP },          -- below it
    }
    local chosen
    for _, spot in ipairs(spots) do
        -- Keep it on screen.
        local x = math.max(0, math.min(spot[1], screenW - w))
        local y = math.min(screenH, math.max(spot[2], h))
        local overTooltip = x < r and x + w > l and y > b and y - h < t
        if not overTooltip and not CoversCursor(x, y, w, h) then chosen = { x, y }; break end
        chosen = chosen or { x, y }
    end
    window:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", chosen[1], chosen[2])
end

-- ==========================================
-- HOVERING
-- ==========================================

local pending       -- { owner, bag, slot, timer }
local debugging = false

local function Debug(msg)
    if debugging then print(PREFIX .. msg) end
end

local function Stop()
    if pending and pending.timer then pending.timer:Cancel() end
    pending = nil
    window:Hide()
end

-- Still hovering the same item? (Tooltips refresh, and may hide for a moment
-- while they do, so this is checked when it matters rather than on every hide.)
local function StillOver(entry)
    return GameTooltip:IsShown() and GameTooltip:GetOwner() == entry.owner
end

local reported = false
local function Open(bag, slot)
    local itemID, count, link, bound = SlotInfo(bag, slot)
    if not itemID then Debug("no item found in bag " .. tostring(bag) .. " slot " .. tostring(slot)); return end
    local ok, lines = pcall(Describe, itemID, count, link, bound)
    if not ok then
        if not reported or debugging then print(PREFIX .. "error: " .. tostring(lines)) end
        reported = true
        return
    end
    Fill(lines)
    Place()
    window:Show()
end

local function Hovering(tooltip, bag, slot)
    if not db or not db.enabled or tooltip ~= GameTooltip then return end
    local owner = tooltip:GetOwner()
    -- Same item as before and still waiting (or already open): keep going.
    if pending and pending.owner == owner and pending.bag == bag and pending.slot == slot
        and (pending.timer or window:IsShown()) then
        return
    end
    Stop()
    Debug("hovering bag " .. tostring(bag) .. " slot " .. tostring(slot))
    local entry = { owner = owner, bag = bag, slot = slot }
    entry.timer = C_Timer.NewTimer(db.delay or 1, function()
        entry.timer = nil
        if pending ~= entry then return end
        if StillOver(entry) then
            Open(bag, slot)
        else
            Debug("moved away before it opened")
            pending = nil
        end
    end)
    pending = entry
end

-- Which bag and slot a tooltip's owner (the item button) is, if it's one.
local BANK_CONTAINER = (Enum and Enum.BagIndex and Enum.BagIndex.Bank) or BANK_CONTAINER or -1
local function BagSlotOf(owner)
    if not owner or (owner.IsForbidden and owner:IsForbidden()) then return nil end
    -- Bank tab buttons (newer bank)
    if owner.GetBankTabID and owner.GetContainerSlotID then
        local ok, bag, slot = pcall(function() return owner:GetBankTabID(), owner:GetContainerSlotID() end)
        if ok and bag and slot then return bag, slot end
    end
    -- Bag buttons (newer bags, including the combined backpack)
    if owner.GetBagID and owner.GetID then
        local ok, bag = pcall(owner.GetBagID, owner)
        if ok and bag then return bag, owner:GetID() end
    end
    -- Bank slots on the older bank window
    local parent = owner.GetParent and owner:GetParent()
    while parent do
        if parent == BankFrame then return BANK_CONTAINER, owner:GetID() end
        parent = parent.GetParent and parent:GetParent()
    end
    return nil
end

-- Newer tooltips report every item tooltip here, however it was built.
if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall and Enum and Enum.TooltipDataType then
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, function(tooltip)
        if tooltip ~= GameTooltip then return end
        local bag, slot = BagSlotOf(tooltip:GetOwner())
        if bag and slot then Hovering(tooltip, bag, slot) end
    end)
end
-- Older bag and bank windows.
hooksecurefunc(GameTooltip, "SetBagItem", Hovering)
hooksecurefunc(GameTooltip, "SetInventoryItem", function(tooltip)
    local bag, slot = BagSlotOf(tooltip:GetOwner())
    if bag == BANK_CONTAINER then Hovering(tooltip, bag, slot) end
end)

-- Close once you've really moved off the item.
window:SetScript("OnUpdate", function()
    if not pending or not StillOver(pending) then Stop(); return end
    -- If the cursor has drifted onto the window, move it out of the way.
    local left, top = window:GetLeft(), window:GetTop()
    if left and top and CoversCursor(left, top, window:GetWidth(), window:GetHeight()) then Place() end
end)

-- ==========================================
-- SETTINGS AND EVENTS
-- ==========================================

local events = CreateFrame("Frame")
-- Events this game version doesn't have are skipped (registering an unknown
-- event is an error that would stop the addon from loading).
for _, event in ipairs({ "ADDON_LOADED", "TRADE_SKILL_SHOW", "TRADE_SKILL_LIST_UPDATE", "TRADE_SKILL_UPDATE", "CRAFT_SHOW", "CRAFT_UPDATE" }) do
    pcall(events.RegisterEvent, events, event)
end
events:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" then
        if arg1 ~= ADDON then return end
        -- The per-character copy first (WoW Forever may not load account-wide
        -- settings back), then the account-wide one.
        local saved
        -- AetherLensDB / AetherLensCharDB hold settings and learned recipes from
        -- before the rename (AetherLens); they're used once and then cleared.
        local sources = { AetherItemIDCharDB, AetherItemIDDB, AetherLensCharDB, AetherLensDB }
        for i = 1, 4 do
            local source = sources[i]
            if type(source) == "table" and next(source) then saved = source; break end
        end
        saved = saved or {}
        for k, v in pairs(defaults) do
            if saved[k] == nil then saved[k] = v end
        end
        db = saved
        AetherItemIDDB, AetherItemIDCharDB = db, db
        AetherLensDB, AetherLensCharDB = nil, nil
    elseif not db then
        return
    elseif event == "CRAFT_SHOW" or event == "CRAFT_UPDATE" then
        pcall(ScanCrafts)
    else
        pcall(ScanTradeSkills)
    end
end)

SLASH_AETHERITEMID1, SLASH_AETHERITEMID2 = "/itemid", "/aetheritemid"
SlashCmdList.AETHERITEMID = function(input)
    local cmd, val = strsplit(" ", strlower(strtrim(input or "")), 2)
    if cmd == "on" or cmd == "off" then
        db.enabled = (cmd == "on")
        if not db.enabled then Stop() end
        print(PREFIX .. "item window " .. (db.enabled and "on" or "off") .. ".")
    elseif cmd == "delay" and tonumber(val) then
        db.delay = math.max(0, math.min(5, tonumber(val)))
        print(PREFIX .. "opens after hovering " .. db.delay .. " seconds.")
    elseif cmd == "debug" then
        debugging = not debugging
        print(PREFIX .. "debug messages " .. (debugging and "on: hover an item in your bags." or "off."))
    elseif cmd == "reset" and val == "recipes" then
        db.learned, db.known = {}, {}
        print(PREFIX .. "learned recipes forgotten. Open your profession windows to learn them again.")
    elseif cmd == "reset" then
        for k, v in pairs(defaults) do
            if k ~= "learned" and k ~= "known" then db[k] = v end
        end
        print(PREFIX .. "settings back to their defaults (learned recipes kept).")
    else
        print(PREFIX .. "hover an item in your bags or bank for " .. (db.delay or 1) .. " second(s).")
        print("  /itemid on|off    turn the item window on or off (now " .. (db.enabled and "on" or "off") .. ")")
        print("  /itemid delay 1   seconds to hover before it opens")
        print("  /itemid reset     default settings (keeps learned recipes)")
        print("  /itemid reset recipes   forget learned recipes")
        print("  /itemid debug     show in chat what it detects while you hover")
    end
end

