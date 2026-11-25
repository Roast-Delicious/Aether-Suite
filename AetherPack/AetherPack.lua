-- ==========================================
-- AetherPack - sectioned bags for WoW Forever
-- Everything in your carried bags in one compact window, sorted into
-- sections: Ammo, Quest items, Gear, Consumables, Trade goods, Other and
-- Junk (with its vendor value). Click a section's title to fold it. Search
-- dims what doesn't match. At a vendor, Sell junk sells every gray item.
-- Item buttons are Blizzard's own bag buttons, so right-click to use, equip,
-- drink or sell works as usual. Click one bag on the bag bar to open a
-- small window with just that bag. WoW doesn't let addons move bag buttons in
-- combat, so the layout catches up when the fight ends.
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
-- The gold capsule's numbers: SemiBold, a step bigger than window text.
if CreateFont and not AetherFontMoney then
    local f = CreateFont("AetherFontMoney")
    if GameFontHighlight then f:CopyFontObject(GameFontHighlight) end
    if not AetherSetFont(f, "SemiBold", 14.5) and GameFontHighlightLarge then f:CopyFontObject(GameFontHighlightLarge) end
    f:SetShadowColor(0, 0, 0, 1)
    f:SetShadowOffset(1, -1)
end

local PREFIX = "|cff4da6ffAetherPack:|r "

local DEFAULTS = {
    replace = true,     -- opens instead of Blizzard's bags
    backpackCount = true,   -- free bag slots shown on the backpack button
    columns = 10,
    scale = 1,
    collapsed = { empty = true },
    bagPos = {},        -- one-bag windows you've dragged: bag -> { left, top }
    deposit = true,     -- the "No swaps. Just drops." slot
    depositPulse = "item",   -- its number pulses: "item" (while you hold one), "always" or "off"
}

local db

local function IsSecret(v) return issecretvalue and issecretvalue(v) or false end

-- ==========================================
-- AETHER LOOK
-- ==========================================
local function AetherFill(button, r, g, b, a)
    local t = button:CreateTexture(nil, "BACKGROUND")
    t:SetColorTexture(r, g, b, a)
    t:SetPoint("TOPLEFT", 1, -1)
    t:SetPoint("BOTTOMRIGHT", -1, 1)
    return t
end

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
    local MEDIA, WHITE = "Interface\\AddOns\\AetherPack\\Media\\", "Interface\\Buttons\\WHITE8X8"
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
-- BAGS AND ITEMS
-- ==========================================
local C = C_Container or {}
-- Backpack, the four bag slots, and WoW Forever's fifth slot for a reagent bag
-- (crafting materials and reagents only; warlocks can put a soul bag there).
local REAGENT_BAG = Enum and Enum.BagIndex and Enum.BagIndex.ReagentBag
local BAGS = { 0, 1, 2, 3, 4 }
if REAGENT_BAG then BAGS[#BAGS + 1] = REAGENT_BAG end

local function NumSlots(bag)
    if C.GetContainerNumSlots then return C.GetContainerNumSlots(bag) or 0 end
    return GetContainerNumSlots and GetContainerNumSlots(bag) or 0
end

-- Special bags: quivers and ammo pouches (only ammo), soul bags (only shards).
local function BagType(bag)
    if bag == 0 then return 0 end
    local _, bagType
    if C.GetContainerNumFreeSlots then _, bagType = C.GetContainerNumFreeSlots(bag)
    elseif GetContainerNumFreeSlots then _, bagType = GetContainerNumFreeSlots(bag) end
    if not bagType or IsSecret(bagType) then return 0 end
    return bagType
end

local function IsAmmoBag(bag)
    local t = BagType(bag)
    return t ~= 0 and (t % 4) ~= 0          -- 1 quiver, 2 ammo pouch
end

local function IsSoulBag(bag)
    local t = BagType(bag)
    return t ~= 0 and math.floor(t / 4) % 2 == 1   -- 4 soul bag
end

-- The reagent bag slot (unless a soul bag sits there): its space is counted on its own.
local function IsReagentBag(bag)
    return REAGENT_BAG ~= nil and bag == REAGENT_BAG and not IsSoulBag(bag)
end

-- ==========================================
-- CLASS SUPPLIES
-- ==========================================
-- Each class's "ammo": the reagents its spells use up. Hunters (and anyone
-- with a bow, gun or crossbow equipped) get the ammo bar; warlocks get a soul
-- shard bar. These items also go in the first section, named for your class.
local SOUL_SHARD = 6265
local CLASS_REAGENTS = {
    WARLOCK = { 6265, 5565, 16583 },                         -- Soul Shard, Infernal Stone, Demonic Figurine
    MAGE    = { 17031, 17032, 17020, 17056 },                -- runes of Teleportation/Portals, Arcane Powder, Light Feather
    PRIEST  = { 17056, 17028, 17029 },                       -- Light Feather, Holy Candle, Sacred Candle
    SHAMAN  = { 17030, 17058, 17057 },                       -- Ankh, Fish Oil, Shiny Fish Scales
    PALADIN = { 17033, 21177 },                              -- Symbol of Divinity, Symbol of Kings
    DRUID   = { 17034, 17035, 17036, 17037, 17038, 17021, 17026 },   -- Rebirth seeds, Wild Berries, Wild Thornroot
    ROGUE   = { 5140, 5530 },                                -- Flash Powder, Blinding Powder
}
local REAGENT_NAMES = {
    [6265] = "Soul Shard", [5565] = "Infernal Stone", [16583] = "Demonic Figurine",
    [17031] = "Rune of Teleportation", [17032] = "Rune of Portals", [17020] = "Arcane Powder",
    [17056] = "Light Feather", [17028] = "Holy Candle", [17029] = "Sacred Candle",
    [17030] = "Ankh", [17058] = "Fish Oil", [17057] = "Shiny Fish Scales",
    [17033] = "Symbol of Divinity", [21177] = "Symbol of Kings",
    [17034] = "Maple Seed", [17035] = "Stranglethorn Seed", [17036] = "Ashwood Seed",
    [17037] = "Hornbeam Seed", [17038] = "Ironwood Seed", [17021] = "Wild Berries", [17026] = "Wild Thornroot",
    [5140] = "Flash Powder", [5530] = "Blinding Powder",
}

local function MyClass()
    local _, token = UnitClass("player")
    return token
end

local myReagents   -- set of item IDs for your class
local function ClassReagent(itemID)
    if not myReagents then
        myReagents = {}
        for _, id in ipairs(CLASS_REAGENTS[MyClass()] or {}) do myReagents[id] = true end
    end
    return itemID and myReagents[itemID] or false
end

-- Hunters, or anyone with a bow, gun or crossbow in the ranged slot.
local function UsesAmmo()
    if MyClass() == "HUNTER" then return true end
    local id = GetInventoryItemID and GetInventoryItemID("player", 18)
    if not id then return false end
    local instant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant
    local _, _, _, _, _, classID, subClassID = instant(id)
    return classID == 2 and (subClassID == 2 or subClassID == 3 or subClassID == 18)
end

local function FirstSectionTitle()
    if UsesAmmo() then return "Ammo" end
    if MyClass() == "WARLOCK" then return "Soul shards" end
    if CLASS_REAGENTS[MyClass()] then return "Class reagents" end
    return "Ammo"
end

local function SlotInfo(bag, slot)
    if C.GetContainerItemInfo then
        local info = C.GetContainerItemInfo(bag, slot)
        if not info then return nil end
        return info.iconFileID, info.stackCount, info.isLocked, info.quality, info.hyperlink, info.itemID
    end
    local icon, count, locked, quality, _, _, link, _, _, itemID = GetContainerItemInfo(bag, slot)
    if not icon then return nil end
    return icon, count, locked, quality, link, itemID
end

local function IsQuestItem(bag, slot)
    local get = C.GetContainerItemQuestInfo or GetContainerItemQuestInfo
    if not get then return false end
    local ok, a, b = pcall(get, bag, slot)
    if not ok then return false end
    if type(a) == "table" then return a.isQuestItem or a.questID ~= nil end
    return a or b ~= nil
end

local function ItemClass(itemID)
    local instant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant
    if not instant or not itemID then return nil end
    local _, _, _, _, _, classID, subClassID = instant(itemID)
    return classID, subClassID
end

local function SellPrice(link)
    if not link then return 0 end
    local get = (C_Item and C_Item.GetItemInfo) or GetItemInfo
    local price = select(11, get(link))
    return price or 0
end

local function ItemName(link)
    if not link then return "" end
    return link:match("%[(.-)%]") or ""
end

-- ==========================================
-- SECTIONS
-- ==========================================
local SECTIONS = {
    { key = "ammo",       title = "Ammo" },
    { key = "quest",      title = "Quest items" },
    { key = "gear",       title = "Gear" },
    { key = "consumable", title = "Consumables" },
    { key = "trade",      title = "Trade goods" },
    { key = "other",      title = "Other" },
    { key = "junk",       title = "Junk" },
    { key = "empty",      title = "Free slots" },
}

-- Item class IDs: 0 consumable, 2 weapon, 4 armor, 5 reagent, 6 projectile,
-- 7 trade goods, 9 recipe, 11 quiver, 12 quest.
local function SectionFor(bag, slot, quality, itemID)
    if IsAmmoBag(bag) or IsSoulBag(bag) or ClassReagent(itemID) then return "ammo" end
    local classID = ItemClass(itemID)
    if classID == 6 then return "ammo" end
    if classID == 12 or IsQuestItem(bag, slot) then return "quest" end
    if quality == 0 then return "junk" end
    if classID == 2 or classID == 4 then return "gear" end
    if classID == 0 then return "consumable" end
    if classID == 5 or classID == 7 or classID == 9 then return "trade" end
    return "other"
end

-- ==========================================
-- SPACE AND SUPPLY COUNTS
-- ==========================================
-- bags: regular slots; ammo: count and quiver capacity; shards: count and
-- soul bag space; reagents: your class reagents you carry.
local function Stats()
    local st = { bagUsed = 0, bagTotal = 0, ammo = 0, quiverSlots = 0, quiverFree = 0, quiverAmmo = 0, ammoStack = 200,
                 pouch = false,
                 shards = 0, soulSlots = 0, soulFree = 0, reagents = {}, rbSlots = 0, rbUsed = 0 }
    for _, bag in ipairs(BAGS) do
        local ammoBag, soulBag, reagentBag = IsAmmoBag(bag), IsSoulBag(bag), IsReagentBag(bag)
        for slot = 1, NumSlots(bag) do
            local icon, count, _, _, link, itemID = SlotInfo(bag, slot)
            if reagentBag then
                st.rbSlots = st.rbSlots + 1
                if icon then st.rbUsed = st.rbUsed + 1 end
            elseif ammoBag then
                st.quiverSlots = st.quiverSlots + 1
                if not icon then st.quiverFree = st.quiverFree + 1 end
                if icon and ItemClass(itemID) == 6 then st.quiverAmmo = st.quiverAmmo + (count or 1) end
                if BagType(bag) % 4 == 2 then st.pouch = true end
            elseif soulBag then
                st.soulSlots = st.soulSlots + 1
                if not icon then st.soulFree = st.soulFree + 1 end
            else
                st.bagTotal = st.bagTotal + 1
                if icon then st.bagUsed = st.bagUsed + 1 end
            end
            if icon then
                if ItemClass(itemID) == 6 then
                    st.ammo = st.ammo + (count or 1)
                    local get = (C_Item and C_Item.GetItemInfo) or GetItemInfo
                    local maxStack = link and select(8, get(link))
                    if maxStack and maxStack > 1 then st.ammoStack = maxStack end
                end
                if itemID == SOUL_SHARD then st.shards = st.shards + (count or 1) end
                if ClassReagent(itemID) and itemID ~= SOUL_SHARD then
                    st.reagents[itemID] = (st.reagents[itemID] or 0) + (count or 1)
                end
            end
        end
    end
    return st
end

-- Soft green with room to spare, gold in the last 25%, soft red in the last 10%.
local function FillColor(used, total)
    local left = total > 0 and (total - used) / total or 1
    if left <= 0.10 then return 0.9, 0.35, 0.3 end
    if left <= 0.25 then return 1, 0.69, 0 end   -- Aether gold: the suite's only yellow
    return 0.133, 0.902, 0.314   -- the vivid green (#22e650)
end

-- Free bag slots on the backpack button, so you can check without opening.
local backpackText
local function UpdateBackpackCount(st)
    local button = MainMenuBarBackpackButton
    if not button then return end
    if not backpackText then
        backpackText = button:CreateFontString(nil, "OVERLAY", "NumberFontNormal")
        backpackText:SetPoint("BOTTOMRIGHT", button, "BOTTOMRIGHT", -3, 3)
    end
    if not db.backpackCount then backpackText:Hide(); return end
    st = st or Stats()
    local free = st.bagTotal - st.bagUsed
    backpackText:SetText(free)
    backpackText:SetTextColor(FillColor(st.bagUsed, st.bagTotal))
    backpackText:Show()
end

-- ==========================================
-- WINDOW
-- ==========================================
local BUTTON = 37      -- Blizzard's bag button size

-- Money as text with coin icons. The game's function for this moved
-- (C_CurrencyInfo.GetCoinTextureString since 10.2.6; the old global may be gone),
-- so try the new one, then the old ones, then build it ourselves.
local function AetherCoins(amount)
    amount = math.floor(tonumber(amount) or 0)
    local fns = { C_CurrencyInfo and C_CurrencyInfo.GetCoinTextureString, GetCoinTextureString, GetMoneyString }
    for i = 1, 3 do                       -- (not ipairs: it would stop at the first missing one)
        local f = fns[i]
        if f then
            local ok, s = pcall(f, amount)
            if ok and type(s) == "string" and s ~= "" then return s end
        end
    end
    local g, s, c = math.floor(amount / 10000), math.floor(amount / 100) % 100, amount % 100
    local parts = {}
    if g > 0 then parts[#parts + 1] = g .. "|TInterface\\MoneyFrame\\UI-GoldIcon:0:0:2:0|t" end
    if s > 0 then parts[#parts + 1] = s .. "|TInterface\\MoneyFrame\\UI-SilverIcon:0:0:2:0|t" end
    if c > 0 or #parts == 0 then parts[#parts + 1] = c .. "|TInterface\\MoneyFrame\\UI-CopperIcon:0:0:2:0|t" end
    return table.concat(parts, " ")
end

local DEP_W, DEP_H = 256, 46  -- the deposit row (see DEPOSIT SLOT)
local GAP = 2
local PAD = 10

local win, holders, buttons, headers = nil, {}, {}, {}
local SpaceColor, SpaceRow

-- The gold capsule in the title strip: bigger numbers, each in its coin's
-- color, in a dark navy pill with a thin gold edge. Hovering it shows what
-- you've gained or lost since you logged in (or last reloaded).
local COIN_COLORS = { "ffce3c", "d6dce6", "e8925a" }   -- gold, silver, copper
local COIN_ICONS = { "UI-GoldIcon", "UI-SilverIcon", "UI-CopperIcon" }
local COIN_ICON = 13
local session = { money = nil, start = nil }

local function CapsuleCoins(amount)
    amount = math.max(0, math.floor(tonumber(amount) or 0))
    local v = { math.floor(amount / 10000), math.floor(amount / 100) % 100, amount % 100 }
    local parts = {}
    for i = 1, 3 do
        if v[i] > 0 or (i == 3 and #parts == 0) then
            parts[#parts + 1] = "|cff" .. COIN_COLORS[i] .. v[i] .. "|r|TInterface\\MoneyFrame\\"
                .. COIN_ICONS[i] .. ":" .. COIN_ICON .. ":" .. COIN_ICON .. ":2:0|t"
        end
    end
    return table.concat(parts, "  ")
end

local function UpdateMoney()
    if not (win and win.coins) then return end
    local money = GetMoney()
    if not session.money then session.money, session.start = money, GetTime() end
    win.coins.text:SetText(CapsuleCoins(money))
    win.coins:SetWidth(math.floor((win.coins.text:GetStringWidth() or 60) + 22 + 0.5))
end

local function ShowMoneyTooltip(self)
    GameTooltip:SetOwner(self, "ANCHOR_BOTTOMLEFT", self:GetWidth(), -4)
    GameTooltip:SetText("Gold", 1, 0.69, 0)
    local money = GetMoney()
    GameTooltip:AddDoubleLine("On hand", AetherCoins(money), 0.6, 0.62, 0.67, 1, 1, 1)
    local diff = money - (session.money or money)
    local r, g, b = 1, 1, 1
    if diff > 0 then r, g, b = 0.133, 0.902, 0.314 elseif diff < 0 then r, g, b = 1, 0.38, 0.35 end
    local sign = diff > 0 and "+" or (diff < 0 and "-" or "")
    GameTooltip:AddDoubleLine("This session", sign .. AetherCoins(math.abs(diff)), 0.6, 0.62, 0.67, r, g, b)
    local mins = (GetTime() - (session.start or GetTime())) / 60
    if mins >= 10 then
        local raw = diff / mins * 60
        local per = raw >= 0 and math.floor(raw + 0.5) or -math.floor(-raw + 0.5)
        GameTooltip:AddDoubleLine("Per hour", (per > 0 and "+" or (per < 0 and "-" or "")) .. AetherCoins(math.abs(per)),
            0.6, 0.62, 0.67, r, g, b)
    else
        GameTooltip:AddDoubleLine("Per hour", "after 10 min", 0.6, 0.62, 0.67, 0.5, 0.52, 0.57)
    end
    GameTooltip:AddLine("Counts from when you logged in or last reloaded.", 0.5, 0.52, 0.57, true)
    GameTooltip:Show()
end

local function BuildCoinCapsule(parent, anchor)
    local MEDIA, WHITE = "Interface\\AddOns\\AetherPack\\Media\\", "Interface\\Buttons\\WHITE8X8"
    local H, CAP = 22, 11
    local c = CreateFrame("Frame", nil, parent)
    c:SetSize(80, H)
    c:SetPoint("RIGHT", anchor, "LEFT", -6, 0)
    c:EnableMouse(true)
    local function Piece(file, layer, sub, r, g, b, a)
        local t = c:CreateTexture(nil, layer, nil, sub)
        t:SetTexture(file); t:SetVertexColor(r, g, b, a)
        return t
    end
    -- Fill (navy) and edge (gold): round caps from a circle, a stretched middle.
    for _, spec in ipairs({ { "pack_pill_fill", "BACKGROUND", 1, 0.03, 0.063, 0.125, 1 },
                            { "pack_pill_ring", "BORDER", 2, 1, 0.69, 0, 0.67 } }) do
        local file, layer, sub, r, g, b, a = unpack(spec)
        local l = Piece(MEDIA .. file, layer, sub, r, g, b, a)
        l:SetTexCoord(0, 0.5, 0, 1); l:SetSize(CAP, H); l:SetPoint("LEFT")
        local rt = Piece(MEDIA .. file, layer, sub, r, g, b, a)
        rt:SetTexCoord(0.5, 1, 0, 1); rt:SetSize(CAP, H); rt:SetPoint("RIGHT")
        if file == "pack_pill_fill" then
            local m = Piece(WHITE, layer, sub, r, g, b, a)
            m:SetPoint("TOPLEFT", l, "TOPRIGHT"); m:SetPoint("BOTTOMRIGHT", rt, "BOTTOMLEFT")
        else
            for _, edge in ipairs({ "TOP", "BOTTOM" }) do
                local m = Piece(WHITE, layer, sub, r, g, b, a)
                m:SetHeight(1)
                m:SetPoint(edge .. "LEFT", l, edge .. "RIGHT"); m:SetPoint(edge .. "RIGHT", rt, edge .. "LEFT")
            end
        end
    end
    c.text = c:CreateFontString(nil, "OVERLAY", "AetherFontMoney")
    c.text:SetPoint("CENTER", 1, 0)
    c:SetScript("OnEnter", ShowMoneyTooltip)
    c:SetScript("OnLeave", function() GameTooltip:Hide() end)
    return c
end
local layoutPending, searchText = false, ""

-- Blizzard's old quickslot frame (the light-gray rounded edge around each
-- slot) fades out; a thin Aether-blue frame takes its place, under the
-- quality border, which stays on top (user, Nov 25 07:26).
local function SlotFrame(b)
    local nt = b.GetNormalTexture and b:GetNormalTexture()
    if nt then nt:SetAlpha(0) end
    if b.aetherFrame then return end
    b.aetherFrame = {}
    for i, a in ipairs({ 1, 0.55 }) do
        local inset = i - 1
        for _, side in ipairs({ "TOP", "BOTTOM", "LEFT", "RIGHT" }) do
            local t = b:CreateTexture(nil, "ARTWORK", nil, 7)
            t:SetColorTexture(0.3, 0.65, 1, a)
            b.aetherFrame[#b.aetherFrame + 1] = { t, a }
            if side == "TOP" or side == "BOTTOM" then
                local dy = side == "TOP" and -inset or inset
                t:SetPoint(side .. "LEFT", b, side .. "LEFT", inset, dy); t:SetPoint(side .. "RIGHT", b, side .. "RIGHT", -inset, dy); t:SetHeight(1)
            else
                local dx = side == "LEFT" and inset or -inset
                t:SetPoint("TOP" .. side, b, "TOP" .. side, dx, -inset); t:SetPoint("BOTTOM" .. side, b, "BOTTOM" .. side, dx, inset); t:SetWidth(1)
            end
        end
    end
end

-- The frame takes the item's quality color for uncommon and up, Aether blue
-- otherwise; Blizzard's own quality border (under ours) is hidden (user,
-- Nov 25: "All frames are blue").
local function SlotQuality(b, quality, hasItem)
    local parts = type(b.aetherFrame) == "table" and b.aetherFrame
    if not parts then return end
    -- plain items silver, empty slots dim (Nov 25: plain blue looked like rare)
    local r, g, bl = 0.78, 0.8, 0.84
    if not hasItem then r, g, bl = 0.2, 0.25, 0.33 end
    if type(quality) == "number" and quality >= 2 then
        local c = (ITEM_QUALITY_COLORS and ITEM_QUALITY_COLORS[quality])
        if c and c.r then r, g, bl = c.r, c.g, c.b
        elseif C_Item and C_Item.GetItemQualityColor then
            local ok, cr, cg, cb = pcall(C_Item.GetItemQualityColor, quality)
            if ok and type(cr) == "number" then r, g, bl = cr, cg, cb end
        end
    end
    for _, p in ipairs(parts) do p[1]:SetColorTexture(r, g, bl, p[2]) end
    local ib = b.IconBorder
    if type(ib) == "table" and ib.SetAlpha then ib:SetAlpha(0) end
end

local function ButtonFor(bag, slot)
    buttons[bag] = buttons[bag] or {}
    local b = buttons[bag][slot]
    if b then return b end
    local holder = holders[bag]
    if not holder then
        holder = CreateFrame("Frame", nil, win)
        holder:SetID(bag)
        holder:SetSize(1, 1)
        holder:SetPoint("TOPLEFT")
        holders[bag] = holder
    end
    b = CreateFrame("ItemButton", "AetherPackItem" .. (bag + 1) .. "_" .. slot, holder, "ContainerFrameItemButtonTemplate")
    b:SetID(slot)
    if b.SetBagID then b:SetBagID(bag) end
    b:SetSize(BUTTON, BUTTON)
    SlotFrame(b)
    buttons[bag][slot] = b
    return b
end

local function UpdateButton(b, bag, slot, noSearch)
    local icon, count, locked, quality, link, itemID = SlotInfo(bag, slot)
    b.aetherLink = link
    pcall(SetItemButtonTexture, b, icon)
    pcall(SetItemButtonCount, b, count or 0)
    pcall(SetItemButtonDesaturated, b, locked and true or false)
    if SetItemButtonQuality then pcall(SetItemButtonQuality, b, quality, itemID) end
    SlotQuality(b, icon and quality or nil, icon ~= nil)
    if b.UpdateCooldown then pcall(b.UpdateCooldown, b, icon)
    elseif ContainerFrame_UpdateCooldown then pcall(ContainerFrame_UpdateCooldown, bag, b) end
    -- "New item" glow: only for items the game says are new (it clears
    -- when you hover them), never for everything after a reload.
    local isNew = false
    if icon and C_NewItems and C_NewItems.IsNewItem then
        local ok, v = pcall(C_NewItems.IsNewItem, bag, slot)
        isNew = ok and v and not IsSecret(v) or false
    end
    if type(b.NewItemTexture) == "table" then
        if isNew then
            local atlas = NEW_ITEM_ATLAS_BY_QUALITY and quality and NEW_ITEM_ATLAS_BY_QUALITY[quality]
            if atlas then b.NewItemTexture:SetAtlas(atlas) else b.NewItemTexture:SetAtlas("bags-glow-white") end
            b.NewItemTexture:Show()
        else
            b.NewItemTexture:Hide()
        end
    end
    if type(b.BattlepayItemTexture) == "table" then b.BattlepayItemTexture:Hide() end
    for _, anim in ipairs({ b.flashAnim, b.newitemglowAnim }) do
        if type(anim) == "table" then
            if isNew then
                if not anim:IsPlaying() then anim:Play() end
            elseif anim:IsPlaying() then
                anim:Stop()
            end
        end
    end
    -- Search: dim what doesn't match.
    local match = noSearch or searchText == "" or (link and ItemName(link):lower():find(searchText, 1, true))
    b:SetAlpha(match and 1 or 0.25)
end

-- Space colors: one green (SPACE_GREEN, easy to swap), the Aether gold and a
-- soft red. Gold is the suite's only yellow.
local SPACE_GREEN = { 0.133, 0.902, 0.314 }   -- #22e650, "vivid green"
local SPACE_GOLD  = { 1, 0.69, 0 }
local SPACE_RED   = { 0.94, 0.37, 0.33 }
local SPACE_WHITE = { 1, 1, 1 }
local AMMO_WARN = 0.5      -- Warning at half a full quiver or ammo pouch, or less
local AMMO_LOW  = 300      -- Low (pulsing) at this much ammo or less
local SHARDS_LOW = 3
local DEP_INK_W = 227      -- where the "No swaps. Just drops." ink ends in the deposit row
local SIDE_MIN_W = 135     -- room the space rows need beside the ink
local ROW_H = 15

-- Green with room to spare, gold in the last 25%, red in the last 10% (and full).
SpaceColor = function(used, total)
    local left = total > 0 and (total - used) / total or 1
    if left <= 0.10 then return SPACE_RED end
    if left <= 0.25 then return SPACE_GOLD end
    return SPACE_GREEN
end

-- One space row: a label on the left; on the right the value, with an
-- optional word in front of it ("Warning", or "Low", which pulses).
SpaceRow = function(i)
    local r = win.bars[i]
    if r then return r end
    r = CreateFrame("Frame", nil, win)
    r:SetHeight(ROW_H)
    r:EnableMouse(true)
    r.label = r:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    r.label:SetPoint("LEFT", 0, 0)
    r.label:SetTextColor(0.78, 0.8, 0.84)
    r.value = r:CreateFontString(nil, "OVERLAY", "AetherFontNormalSmall")
    r.value:SetPoint("RIGHT", 0, 0)
    r.word = r:CreateFontString(nil, "OVERLAY", "AetherFontNormalSmall")
    r.word:SetPoint("RIGHT", r.value, "LEFT", -4, 0)
    -- The Low pulse: fades to 35% and back, about once a second.
    r.pulse = r.word:CreateAnimationGroup()
    r.pulse:SetLooping("BOUNCE")
    local fade = r.pulse:CreateAnimation("Alpha")
    fade:SetFromAlpha(1); fade:SetToAlpha(0.35); fade:SetDuration(0.5)
    if fade.SetSmoothing then fade:SetSmoothing("IN_OUT") end
    r:SetScript("OnEnter", function(self)
        if not self.tip then return end
        GameTooltip:SetOwner(self, "ANCHOR_TOP")
        GameTooltip:SetText(self.label:GetText() or "", 1, 0.69, 0)
        for _, line in ipairs(self.tip) do GameTooltip:AddLine(line, 1, 1, 1, true) end
        GameTooltip:Show()
    end)
    r:SetScript("OnLeave", function() GameTooltip:Hide() end)
    win.bars[i] = r
    return r
end

local function Header(key, title)
    local h = headers[key]
    if not h then
        h = CreateFrame("Button", nil, win)
        h:SetHeight(18)
        h.text = h:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
        h.text:SetPoint("LEFT", 2, 0)
        h.line = h:CreateTexture(nil, "ARTWORK")
        h.line:SetColorTexture(0.3, 0.65, 1, 0.35)
        h.line:SetHeight(1)
        h.line:SetPoint("LEFT", h.text, "RIGHT", 8, 0)
        h.line:SetPoint("RIGHT", h, "RIGHT", 0, 0)
        h.hint = h:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")   -- what to buy (ammo heading)
        h.hint:SetPoint("RIGHT", h, "RIGHT", 0, 0)
        h.hint:Hide()
        h.show = h:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")   -- "Show" when folded
        h.show:SetPoint("RIGHT", h, "RIGHT", 0, 0)
        h.show:SetTextColor(0.43, 0.67, 1)
        h:SetScript("OnClick", function()
            db.collapsed[key] = not db.collapsed[key]
            AetherPack_Layout()
        end)
        h:SetScript("OnEnter", function(self)
            GameTooltip:SetOwner(self, "ANCHOR_TOP")
            GameTooltip:SetText("Click to " .. (db.collapsed[key] and "open" or "fold") .. " this section", 1, 1, 1)
            GameTooltip:Show()
        end)
        h:SetScript("OnLeave", function() GameTooltip:Hide() end)
        headers[key] = h
    end
    return h
end

-- The Ammo heading (user idea, Nov 25): what you shoot, how many you carry,
-- and what to buy, e.g. "Arrows: 1,240" ... "buy 9 stacks to fill".
-- Arrows with a bow or crossbow (or a quiver), bullets with a gun (or an
-- ammo pouch); warlocks see their soul shards and the room left for them.
-- Returns name, count text, hint, hint color (or nil for other classes).
local function AmmoHeading(st)
    local function Num(n) return FormatLargeNumber and FormatLargeNumber(n) or tostring(n) end
    if UsesAmmo() then
        local word = "Arrows"
        local id = GetInventoryItemID and GetInventoryItemID("player", 18)
        local instant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant
        if id and instant then
            local _, _, _, _, _, classID, subClassID = instant(id)
            if classID == 2 and subClassID == 3 then word = "Bullets" end
        elseif st.pouch then word = "Bullets" end
        if not id and st.pouch then word = "Bullets" end
        local hint, col
        local cap = st.quiverSlots * (st.ammoStack or 200)
        if cap > 0 then
            local room = math.max(0, cap - (st.quiverAmmo or 0))
            local stacks = math.floor(room / (st.ammoStack or 200))
            if stacks >= 1 then
                hint = "buy " .. stacks .. (stacks == 1 and " stack" or " stacks") .. " to fill"
                col = (st.ammo <= AMMO_LOW) and SPACE_RED or { 0.92, 0.93, 0.96 }
            else
                hint = (st.pouch and "pouch" or "quiver") .. " full"
                col = SPACE_GREEN
            end
        end
        return word, Num(st.ammo), hint, col
    end
    if MyClass() == "WARLOCK" then
        local hint, col
        if st.soulSlots > 0 then
            if st.soulFree > 0 then hint, col = "room for " .. st.soulFree .. " more", { 0.92, 0.93, 0.96 }
            else hint, col = "soul bag full", SPACE_GREEN end
        end
        return "Soul shards", Num(st.shards), hint, col
    end
    return nil
end

-- Sorts the bags into sections and lays the window out.
function AetherPack_Layout()
    if not win then return end
    if InCombatLockdown() then layoutPending = true; return end
    layoutPending = false
    local groups = {}
    for _, s in ipairs(SECTIONS) do groups[s.key] = {} end
    local free, ammoFree, soulFree, junkValue = 0, 0, 0, 0
    for _, bag in ipairs(BAGS) do
        local ammoBag, soulBag, reagentBag = IsAmmoBag(bag), IsSoulBag(bag), IsReagentBag(bag)
        for slot = 1, NumSlots(bag) do
            local b = ButtonFor(bag, slot)
            local icon, count, _, quality, link, itemID = SlotInfo(bag, slot)
            local entry = { b = b, bag = bag, slot = slot, quality = quality or -1, name = ItemName(link) }
            if icon then
                local key = SectionFor(bag, slot, quality, itemID)
                if key == "junk" then junkValue = junkValue + SellPrice(link) * (count or 1) end
                table.insert(groups[key], entry)
            else
                if reagentBag then -- reagent-only space: not counted as free bag space
                elseif ammoBag then ammoFree = ammoFree + 1
                elseif soulBag then soulFree = soulFree + 1
                else free = free + 1 end
                table.insert(groups.empty, entry)
            end
        end
    end
    -- Hide buttons for bags that got smaller or removed.
    for bag, list in pairs(buttons) do
        for slot, b in pairs(list) do
            if slot > NumSlots(bag) then b:Hide() end
        end
    end

    local cols = db.columns
    local width = PAD * 2 + cols * BUTTON + (cols - 1) * GAP
    local y = -62     -- below the title and search box
    local st0 = Stats()
    for _, s in ipairs(SECTIONS) do
        local list = groups[s.key]
        local title = s.key == "ammo" and FirstSectionTitle() or s.title
        local h = Header(s.key, title)
        if #list == 0 then
            h:Hide()
            for _, e in ipairs(list) do e.b:Hide() end
        else
            table.sort(list, function(a, b)
                if a.quality ~= b.quality then return a.quality > b.quality end
                if a.name ~= b.name then return a.name < b.name end
                if a.bag ~= b.bag then return a.bag < b.bag end
                return a.slot < b.slot
            end)
            local label = title .. "  |cff9d9d9d" .. #list .. "|r"
            if s.key == "junk" and junkValue > 0 then
                label = label .. "  " .. AetherCoins(junkValue)
            end
            if s.key == "empty" and (ammoFree > 0 or soulFree > 0) then
                label = s.title .. "  |cff9d9d9d" .. free
                    .. (ammoFree > 0 and (" (+" .. ammoFree .. " ammo)") or "")
                    .. (soulFree > 0 and (" (+" .. soulFree .. " soul bag)") or "") .. "|r"
            end
            local hint
            if s.key == "ammo" then
                local name, count, hintText, hintColor = AmmoHeading(st0)
                if name then
                    label = name .. ":  |cff9d9d9d" .. count .. "|r"
                    hint, hintColor = hintText, hintColor
                    if hint then h.hint:SetText(hint); h.hint:SetTextColor(hintColor[1], hintColor[2], hintColor[3]) end
                end
            end
            h.hint:SetShown(hint ~= nil and not db.collapsed[s.key])
            h.text:SetText(label)
            h.line:ClearAllPoints()
            h.line:SetPoint("LEFT", h.text, "RIGHT", 8, 0)
            if hint and not db.collapsed[s.key] then
                h.line:SetPoint("RIGHT", h.hint, "LEFT", -8, 0)
            elseif db.collapsed[s.key] then
                h.show:SetText(s.key == "empty" and "Show empty" or "Show")
                h.show:Show()
                h.line:SetPoint("RIGHT", h.show, "LEFT", -8, 0)
            else
                h.show:Hide()
                h.line:SetPoint("RIGHT", h, "RIGHT", 0, 0)
            end
            h:ClearAllPoints()
            h:SetPoint("TOPLEFT", win, "TOPLEFT", PAD, y)
            h:SetPoint("RIGHT", win, "RIGHT", -PAD, 0)
            h:Show()
            y = y - 20
            if db.collapsed[s.key] then
                for _, e in ipairs(list) do e.b:Hide() end
            else
                for i, e in ipairs(list) do
                    local col = (i - 1) % cols
                    local row = math.floor((i - 1) / cols)
                    e.b:ClearAllPoints()
                    e.b:SetPoint("TOPLEFT", win, "TOPLEFT", PAD + col * (BUTTON + GAP), y - row * (BUTTON + GAP))
                    UpdateButton(e.b, e.bag, e.slot)
                    e.b:Show()
                end
                y = y - math.ceil(#list / cols) * (BUTTON + GAP) - 6
            end
        end
    end
    -- Space and supply at the bottom: short colored values instead of bars
    -- (see SpaceColor), full numbers in each row's tooltip.
    local st = Stats()
    local rows = {}
    local function Num(n) return FormatLargeNumber and FormatLargeNumber(n) or tostring(n) end
    local bagFree = st.bagTotal - st.bagUsed
    rows[#rows + 1] = { label = "Bags", value = bagFree <= 0 and "Full" or (bagFree .. " free"),
        color = SpaceColor(st.bagUsed, st.bagTotal),
        tip = { st.bagUsed .. " of " .. st.bagTotal .. " slots used", bagFree .. " free" } }
    if st.rbSlots > 0 then
        local rbFree = st.rbSlots - st.rbUsed
        rows[#rows + 1] = { label = "Reagent", value = rbFree <= 0 and "Full" or (rbFree .. " free"),
            color = SpaceColor(st.rbUsed, st.rbSlots),
            tip = { "Reagent bag: " .. st.rbUsed .. " of " .. st.rbSlots .. " slots used", rbFree .. " free" } }
    end
    if UsesAmmo() then
        local cap = st.quiverSlots * st.ammoStack
        local word, wordColor, pulse
        if st.ammo <= AMMO_LOW then word, wordColor, pulse = "Low", SPACE_RED, true
        elseif cap > 0 and st.ammo <= cap * AMMO_WARN then word, wordColor = "Warning", SPACE_GOLD end
        local tip = { Num(st.ammo) .. " ammo" }
        if cap > 0 then
            tip[1] = Num(st.ammo) .. " of " .. Num(cap) .. " ammo"
            tip[2] = st.quiverFree .. " quiver slot" .. (st.quiverFree == 1 and "" or "s") .. " free"
        else
            tip[2] = "No quiver or ammo pouch"
        end
        tip[#tip + 1] = "|cff999999Warning at half a full quiver, Low at " .. AMMO_LOW .. " or less.|r"
        rows[#rows + 1] = { label = "Ammo", value = Num(st.ammo), color = SPACE_WHITE,
            word = word, wordColor = wordColor, pulse = pulse, tip = tip }
    end
    if MyClass() == "WARLOCK" then
        local low = st.shards < SHARDS_LOW
        rows[#rows + 1] = { label = "Shards", value = tostring(st.shards), color = SPACE_WHITE,
            word = low and "Low" or nil, wordColor = SPACE_RED, pulse = low,
            tip = { st.shards .. " soul shard" .. (st.shards == 1 and "" or "s")
                .. (st.soulSlots > 0 and (" (soul bag: " .. st.soulSlots .. " slots)") or "") } }
    end
    local reagents = {}
    for _, id in ipairs(CLASS_REAGENTS[MyClass()] or {}) do
        local n = st.reagents[id]
        if n then
            reagents[#reagents + 1] = (n <= 2 and "|cffe65a4d" or "|cffffffff") .. (REAGENT_NAMES[id] or id) .. " " .. n .. "|r"
        end
    end

    -- The deposit slot gets a row of its own under the last section (right
    -- under Free slots when that's folded), lined up with the item grid's
    -- first column. The space rows sit to the right of its hint when there's
    -- room; in a narrow window, under it. Class reagents go full width below.
    local depBox = win.depositBox
    local sideX = PAD + DEP_INK_W + 8
    local side = db.deposit and (width - PAD - sideX) >= SIDE_MIN_W
    local top = y
    if db.deposit then
        depBox:ClearAllPoints()
        depBox:SetPoint("TOPLEFT", win, "TOPLEFT", PAD, y + 2)
        depBox:Show()
    else
        depBox:Hide()
    end
    local x0, x1, ry
    if side then
        x0, x1 = sideX, width - PAD
        ry = top - math.max(0, math.floor((DEP_H - #rows * ROW_H) / 2))   -- centered beside the slot
    else
        if db.deposit then y = y - DEP_H end
        y = y - 4
        x0, x1 = PAD, math.min(width - PAD, PAD + 200)
        ry = y
    end
    for i, row in ipairs(rows) do
        local r = SpaceRow(i)
        r:ClearAllPoints()
        r:SetPoint("TOPLEFT", win, "TOPLEFT", x0, ry)
        r:SetWidth(x1 - x0)
        r.label:SetText(row.label)
        r.value:SetText(row.value)
        r.value:SetTextColor(row.color[1], row.color[2], row.color[3])
        r.word:SetText(row.word or "")
        if row.word then r.word:SetTextColor(row.wordColor[1], row.wordColor[2], row.wordColor[3]) end
        r.word:SetShown(row.word ~= nil)
        if row.pulse then
            if not r.pulse:IsPlaying() then r.pulse:Play() end
        else
            r.pulse:Stop(); r.word:SetAlpha(1)
        end
        r.tip = row.tip
        r:Show()
        ry = ry - ROW_H
    end
    for i = #rows + 1, #win.bars do
        local r = win.bars[i]; r.pulse:Stop(); r:Hide()
    end
    if side then
        y = math.min(top - DEP_H, ry) - 4
    else
        y = ry - 2
    end
    win.reagentLine:ClearAllPoints()
    if #reagents > 0 then
        win.reagentLine:SetPoint("TOPLEFT", win, "TOPLEFT", PAD, y)
        win.reagentLine:SetPoint("RIGHT", win, "RIGHT", -PAD, 0)
        win.reagentLine:SetText("|cffc8cdd7Reagents|r  " .. table.concat(reagents, "  "))
        win.reagentLine:Show()
        y = y - (win.reagentLine:GetStringHeight() or 12) - 4
    else
        win.reagentLine:Hide()
    end


    UpdateMoney()
    win.junkValue = junkValue
    win.sell:SetShown(win.atMerchant and junkValue > 0)
    UpdateBackpackCount(st)
    AetherPack_UpdateDeposit(st)
    win:SetSize(width, -y + (win.sell:IsShown() and 34 or 10))
end

-- Quick refresh of icons, counts and locks without moving anything (safe in combat).
local function RefreshButtons()
    for bag, list in pairs(buttons) do
        for slot, b in pairs(list) do
            if b:IsShown() then UpdateButton(b, bag, slot) end
        end
    end
end

-- ==========================================
-- DEPOSIT SLOT ("No swaps. Just drops.")
-- ==========================================
-- A drop target that never swaps: whatever you drop on it goes to a free
-- slot, through the game's own "put in bag" calls. Crafting reagents try the
-- reagent bag first; ammo, soul shards and the like try their special bag
-- first; everything else goes to your first regular bag with room.
local function FreeSlots(bag)
    local get = C.GetContainerNumFreeSlots or GetContainerNumFreeSlots
    if not get then return 0 end
    local ok, free = pcall(get, bag)
    if not ok or not free or IsSecret(free) then return 0 end
    return free
end

-- Does a quiver, ammo pouch or soul bag take this item? (bag type flags)
local function SpecialBagTakes(bag, itemID)
    local t = BagType(bag)
    if t == 0 or not itemID then return false end
    local family = (C_Item and C_Item.GetItemFamily or GetItemFamily)
    local ok, f = pcall(family, itemID)
    if not ok or type(f) ~= "number" or IsSecret(f) then return false end
    return bit and bit.band and bit.band(f, t) ~= 0 or false
end

local function IsCraftingReagent(itemID)
    local get = (C_Item and C_Item.GetItemInfo) or GetItemInfo
    if not get or not itemID then return false end
    local ok, r = pcall(function() return select(17, get(itemID)) end)
    if ok and r then return true end
    return false
end

-- The bag a dropped item should go to, or nil if there's no room for it.
local function DepositBag(itemID)
    if REAGENT_BAG and NumSlots(REAGENT_BAG) > 0 and FreeSlots(REAGENT_BAG) > 0 then
        if IsSoulBag(REAGENT_BAG) then
            if SpecialBagTakes(REAGENT_BAG, itemID) then return REAGENT_BAG end
        elseif IsCraftingReagent(itemID) then
            return REAGENT_BAG
        end
    end
    for bag = 1, 4 do      -- a quiver or soul bag that takes it
        if NumSlots(bag) > 0 and FreeSlots(bag) > 0 and SpecialBagTakes(bag, itemID) then return bag end
    end
    for bag = 0, 4 do      -- then the first regular bag with room
        if NumSlots(bag) > 0 and FreeSlots(bag) > 0 and BagType(bag) == 0 then return bag end
    end
end

local function Deposit()
    if not (CursorHasItem and CursorHasItem()) then return end
    local kind, itemID = GetCursorInfo()
    if kind ~= "item" then return end
    local bag = DepositBag(itemID)
    if not bag then
        if UIErrorsFrame then UIErrorsFrame:AddMessage("No room in your bags for that.", 1, 0.3, 0.3) end
        return
    end
    if bag == 0 then
        pcall(PutItemInBackpack)
    else
        local inv = (C.ContainerIDToInventoryID or ContainerIDToInventoryID)
        local ok, slot = pcall(inv, bag)
        if ok and slot then pcall(PutItemInBag, slot) end
    end
end

-- The deposit row (art: tools/gen_deposit_art.py for the slot, gen_deposit_ink.py
-- for the chalk lettering): 46 units tall. The slot (37) sits at its left, 3
-- units down; the ink (256 x 64 units: "NO SWAPS. JUST DROPS." and an arrow
-- curving back into the slot) has the slot's top-left at (0, 12) on it.
local DEP_SX, DEP_SY, DEP_SLOT = 0, 3, 37
local AMBER = { 1, 0.69, 0 }             -- the Aether gold
local FULL = { 0.9, 0.35, 0.3 }          -- the slot's rim and glow when your bags are full

-- Free regular slots in the slot; the rim and glow turn red when you're full.
function AetherPack_UpdateDeposit(st)
    if not win or not win.deposit then return end
    st = st or Stats()
    local free = st.bagTotal - st.bagUsed
    local d = win.deposit
    d.count:SetText(free)
    local c = free <= 0 and FULL or AMBER
    for _, t in ipairs(d.tint) do t:SetVertexColor(c[1], c[2], c[3], 1) end
    d.free = free
end

-- The number pulses (100% to 10% and back, 2.7 s): while you hold an item
-- (db.depositPulse "item", the default), all the time ("always"), or never ("off").
local function UpdatePulse()
    local d = win and win.deposit
    if not d or not d.pulse then return end
    local mode = db.depositPulse or "item"
    local want = d:IsVisible() and (mode == "always" or (mode == "item" and CursorHasItem and CursorHasItem() and true or false))
    if want and not d.pulse:IsPlaying() then d.pulse:Play()
    elseif not want and d.pulse:IsPlaying() then d.pulse:Stop() end
end
AetherPack_UpdatePulse = UpdatePulse

local function BuildDeposit()
    local MEDIA = "Interface\\AddOns\\AetherPack\\Media\\"
    local box = CreateFrame("Frame", nil, win)
    box:SetSize(DEP_W, DEP_H)
    local d = CreateFrame("Button", "AetherPackDeposit", box)
    d:SetSize(DEP_SLOT, DEP_SLOT)
    d:SetPoint("TOPLEFT", box, "TOPLEFT", DEP_SX, -DEP_SY)
    d:RegisterForClicks("LeftButtonUp")
    d.tint = {}
    local function Tex(parent, layer, sub, file, tinted, a)
        local t = parent:CreateTexture(nil, layer, nil, sub)
        t:SetTexture(MEDIA .. file)
        if tinted then
            t:SetVertexColor(AMBER[1], AMBER[2], AMBER[3], a or 1)
        end
        return t
    end
    -- the slot: dark well, soft glow and rays, darker middle, rim
    Tex(d, "BACKGROUND", 0, "dep_well"):SetAllPoints()
    local glow = Tex(d, "BORDER", 0, "dep_glow", true); glow:SetAllPoints()
    Tex(d, "BORDER", 1, "dep_dark"):SetAllPoints()
    local rim = Tex(d, "ARTWORK", 0, "dep_rim", true); rim:SetAllPoints()
    d.tint = { glow, rim }
    local hl = d:CreateTexture(nil, "HIGHLIGHT")
    hl:SetTexture("Interface\\Buttons\\WHITE8X8")
    hl:SetVertexColor(1, 0.69, 0, 0.12)
    hl:SetPoint("TOPLEFT", 3, -3); hl:SetPoint("BOTTOMRIGHT", -3, 3)

    -- the free count: Fira Sans Black in a light amber, with a soft amber glow; it pulses
    d.num = CreateFrame("Frame", nil, d)
    d.num:SetAllPoints()
    local ng = Tex(d.num, "ARTWORK", 1, "dep_numglow", true, 0.55)
    ng:SetSize(28, 18); ng:SetPoint("CENTER")
    d.count = d.num:CreateFontString(nil, "OVERLAY")
    if not AetherSetFont(d.count, "Black", 11) then d.count:SetFontObject("NumberFontNormal") end
    d.count:SetPoint("CENTER", 0, 0)
    d.count:SetTextColor(1, 0.69, 0)
    d.count:SetShadowColor(0, 0, 0, 0.65)
    d.count:SetShadowOffset(1, -1)
    if d.num.CreateAnimationGroup then
        local ok, ag = pcall(d.num.CreateAnimationGroup, d.num)
        if ok and ag then
            ag:SetLooping("BOUNCE")
            local a = ag:CreateAnimation("Alpha")
            a:SetFromAlpha(1); a:SetToAlpha(0.1)
            a:SetDuration(1.35)                  -- down and back up: 2.7 s
            a:SetSmoothing("IN_OUT")
            d.pulse = ag
        end
    end

    -- the chalk lettering and arrow, drawn on top
    local inkF = CreateFrame("Frame", nil, box)
    inkF:SetAllPoints(box)
    inkF:SetFrameLevel((d:GetFrameLevel() or 1) + 3)
    local ink = Tex(inkF, "OVERLAY", 7, "dep_ink", true)
    ink:SetSize(256, 64); ink:SetPoint("TOPLEFT", d, "TOPLEFT", 0, 12)   -- chalk: no shadow

    d:SetScript("OnReceiveDrag", Deposit)
    d:SetScript("OnClick", Deposit)
    d:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_TOP")
        GameTooltip:SetText("No swaps. Just drops.", 1, 0.69, 0)
        GameTooltip:AddLine("Drop an item here and it goes into a free slot. Nothing already in your bags gets moved or swapped.", 1, 1, 1, true)
        GameTooltip:AddLine("Crafting reagents go to your reagent bag first, ammo to your quiver.", 0.75, 0.75, 0.75, true)
        GameTooltip:AddLine((self.free or 0) .. " free in your regular bags.", 0.75, 0.75, 0.75)
        GameTooltip:Show()
    end)
    d:SetScript("OnLeave", function() GameTooltip:Hide() end)
    d:SetScript("OnShow", UpdatePulse)
    d:SetScript("OnHide", function(self) if self.pulse then self.pulse:Stop() end end)
    win.deposit = d
    win.depositBox = box
end

-- ==========================================
-- SELL JUNK
-- ==========================================
local selling = false
local function SellJunk()
    if selling then return end
    local queue = {}
    for _, bag in ipairs(BAGS) do
        for slot = 1, NumSlots(bag) do
            local icon, _, locked, quality, link = SlotInfo(bag, slot)
            if icon and quality == 0 and not locked and SellPrice(link) > 0 then
                queue[#queue + 1] = { bag, slot }
            end
        end
    end
    if #queue == 0 then return end
    selling = true
    local total = win.junkValue or 0
    local i = 0
    local function Next()
        i = i + 1
        local item = queue[i]
        if not item or not win.atMerchant then
            selling = false
            if total > 0 then print(PREFIX .. "sold junk for " .. AetherCoins(total) .. ".") end
            return
        end
        local use = C.UseContainerItem or UseContainerItem
        pcall(use, item[1], item[2])
        C_Timer.After(0.2, Next)      -- one at a time, so the vendor keeps up
    end
    Next()
end

local function BuildWindow()
    win = CreateFrame("Frame", "AetherPackFrame", UIParent, "BackdropTemplate")
    win:SetSize(400, 200)
    win:SetPoint("BOTTOMRIGHT", UIParent, "BOTTOMRIGHT", -80, 120)
    win:SetFrameStrata("HIGH")
    win:SetToplevel(true)
    win:SetClampedToScreen(true)
    win:SetMovable(true)
    win:EnableMouse(true)
    win:RegisterForDrag("LeftButton")
    win:SetScript("OnDragStart", win.StartMoving)
    win:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        local left, top = self:GetLeft(), self:GetTop()
        if left and top then db.pos = { left, top } end
    end)
    if win.SetBackdrop then
        win:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        win:SetBackdropColor(0.05, 0.06, 0.09, 0.94)
        win:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    AetherDecorate(win, 26)
    tinsert(UISpecialFrames, "AetherPackFrame")   -- Esc closes it

    local title = win:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    title:SetPoint("TOPLEFT", PAD, -9)
    title:SetText("|cff4da6ffAETHER PACK|r")

    local close = AetherButton(win, nil, true)
    close:SetSize(18, 18)
    close:SetText("x")
    close:SetPoint("TOPRIGHT", -6, -6)
    close:SetScript("OnClick", function() win:Hide() end)

    -- Search box
    local search = CreateFrame("EditBox", "AetherPackSearch", win, "BackdropTemplate")
    search:SetHeight(20)
    search:SetPoint("TOPLEFT", PAD, -30)
    search:SetPoint("RIGHT", win, "RIGHT", -PAD, 0)
    search:SetAutoFocus(false)
    search:SetFontObject("AetherFontHighlightSmall")
    search:SetTextInsets(6, 6, 0, 0)
    if search.SetBackdrop then
        search:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        search:SetBackdropColor(0.07, 0.17, 0.32, 0.6)
        search:SetBackdropBorderColor(0.3, 0.65, 1, 0.6)
    end
    local hint = search:CreateFontString(nil, "OVERLAY", "AetherFontDisableSmall")
    hint:SetPoint("LEFT", 6, 0)
    hint:SetText("Search")
    search:SetScript("OnTextChanged", function(self)
        searchText = (self:GetText() or ""):lower()
        hint:SetShown(searchText == "")
        RefreshButtons()
    end)
    search:SetScript("OnEscapePressed", function(self) self:SetText(""); self:ClearFocus() end)
    search:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)

    -- Gold next to the title; space bars and Sell junk at the bottom.
    win.bars = {}
    win.reagentLine = win:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    win.reagentLine:SetJustifyH("LEFT")
    win.reagentLine:Hide()
    win.coins = BuildCoinCapsule(win, close)
    win.sell = AetherButton(win, nil, true)
    win.sell:SetSize(76, 18)
    win.sell:SetPoint("BOTTOM", win, "BOTTOM", 0, 7)
    win.sell:SetText("Sell junk")
    win.sell:SetScript("OnClick", SellJunk)
    win.sell:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_TOP")
        GameTooltip:SetText("Sells every gray item to this vendor (nothing else).", 1, 1, 1, 1, true)
        GameTooltip:Show()
    end)
    win.sell:SetScript("OnLeave", function() GameTooltip:Hide() end)
    win.sell:Hide()
    BuildDeposit()

    win:SetScript("OnShow", function() AetherPack_Layout() end)
    win:SetScale(db.scale or 1)
    if db.pos then
        win:ClearAllPoints()
        win:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", db.pos[1], db.pos[2])
    end
    win:Hide()
end

-- ==========================================
-- ONE-BAG WINDOWS
-- ==========================================
-- Clicking one of your bags on the bag bar (the four bag slots or the reagent
-- bag) opens a small window with just that bag, in slot order. The backpack
-- button and the bag key still open the combined window. Open windows stack
-- up from the lower right; drag one and it stays where you put it.
local BAG_COLS = 4
local bagWins = {}
local bagLayoutPending = false

local function IsSingleBag(bag)
    return bag ~= nil and ((bag >= 1 and bag <= 4) or (REAGENT_BAG ~= nil and bag == REAGENT_BAG))
end

local function BagName(bag)
    local ok, name = pcall(C.GetBagName or GetBagName, bag)
    if ok and type(name) == "string" and name ~= "" and not IsSecret(name) then return name end
    return bag == REAGENT_BAG and "Reagent bag" or ("Bag " .. bag)
end

local function BagCount(w)
    local n, used = NumSlots(w.bag), 0
    for slot = 1, n do if SlotInfo(w.bag, slot) then used = used + 1 end end
    w.count:SetText(used .. "/" .. n)
    w.count:SetTextColor(FillColor(used, n))
end

-- Quick refresh of icons, counts and locks (safe in combat).
local function RefreshBagWindow(w)
    for slot, b in pairs(w.buttons) do
        if b:IsShown() then UpdateButton(b, w.bag, slot, true) end
    end
    BagCount(w)
end

local function LayoutBagWindow(w)
    if InCombatLockdown() then bagLayoutPending = true; return end
    local n = NumSlots(w.bag)
    if n == 0 then w:Hide(); return end          -- the bag was taken off
    w.title:SetText(BagName(w.bag))
    local cols = BAG_COLS
    for slot = 1, n do
        local b = w.buttons[slot]
        if not b then
            b = CreateFrame("ItemButton", "AetherPackBag" .. w.bag .. "_" .. slot, w.holder, "ContainerFrameItemButtonTemplate")
            b:SetID(slot)
            if b.SetBagID then b:SetBagID(w.bag) end
            b:SetSize(BUTTON, BUTTON)
            SlotFrame(b)
            w.buttons[slot] = b
        end
        local col, row = (slot - 1) % cols, math.floor((slot - 1) / cols)
        b:ClearAllPoints()
        b:SetPoint("TOPLEFT", w, "TOPLEFT", PAD + col * (BUTTON + GAP), -32 - row * (BUTTON + GAP))
        UpdateButton(b, w.bag, slot, true)
        b:Show()
    end
    for slot, b in pairs(w.buttons) do if slot > n then b:Hide() end end
    BagCount(w)
    local rows = math.ceil(n / cols)
    w.w = PAD * 2 + cols * BUTTON + (cols - 1) * GAP
    -- Wide enough for the whole bag name: title, count, then the x (24).
    local function Width(fs)
        local get = fs.GetUnboundedStringWidth or fs.GetStringWidth
        local ok, v = pcall(get, fs)
        return ok and type(v) == "number" and v or 0
    end
    w.w = math.max(w.w, math.ceil(PAD + Width(w.title) + 10 + Width(w.count) + 6 + 24))
    w.h = 32 + rows * (BUTTON + GAP) - GAP + PAD
    w:SetSize(w.w, w.h)
    w.laidOut = true
end

-- Windows you haven't dragged stack up from the lower right, a new column to
-- the left when one gets too tall.
local function PlaceBagWindows()
    if InCombatLockdown() then bagLayoutPending = true; return end
    local top = ((UIParent.GetHeight and UIParent:GetHeight()) or 768) - 60
    local x, y, colW = -20, 110, 0
    for _, bag in ipairs(BAGS) do
        local w = bagWins[bag]
        if w and w:IsShown() and w.h and not db.bagPos[bag] then
            if y > 110 and y + w.h > top then x, y, colW = x - colW - 14, 110, 0 end
            w:ClearAllPoints()
            w:SetPoint("BOTTOMRIGHT", UIParent, "BOTTOMRIGHT", x, y)
            y = y + w.h + 16
            colW = math.max(colW, w.w)
        end
    end
end

local function BuildBagWindow(bag)
    local name = "AetherPackBag" .. bag .. "Frame"
    local w = CreateFrame("Frame", name, UIParent, "BackdropTemplate")
    w.bag, w.buttons = bag, {}
    w:SetSize(174, 80)
    w:SetFrameStrata("HIGH")
    w:SetToplevel(true)
    w:SetClampedToScreen(true)
    w:SetMovable(true)
    w:EnableMouse(true)
    w:RegisterForDrag("LeftButton")
    w:SetScript("OnDragStart", w.StartMoving)
    w:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        local left, top = self:GetLeft(), self:GetTop()
        if left and top then db.bagPos[bag] = { left, top } end
        PlaceBagWindows()
    end)
    if w.SetBackdrop then
        w:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        w:SetBackdropColor(0.05, 0.06, 0.09, 0.94)
        w:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    AetherDecorate(w, 26)
    tinsert(UISpecialFrames, name)                -- Esc closes it

    -- The item buttons find their bag through their parent's ID.
    w.holder = CreateFrame("Frame", nil, w)
    w.holder:SetID(bag)
    w.holder:SetSize(1, 1)
    w.holder:SetPoint("TOPLEFT")

    local close = AetherButton(w, nil, true)
    close:SetSize(18, 18)
    close:SetText("x")
    close:SetPoint("TOPRIGHT", -6, -6)
    close:SetScript("OnClick", function() w:Hide() end)
    w.count = w:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    w.count:SetPoint("RIGHT", close, "LEFT", -6, 0)
    w.title = w:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    w.title:SetPoint("TOPLEFT", PAD, -9)
    w.title:SetPoint("RIGHT", w.count, "LEFT", -6, 0)
    w.title:SetJustifyH("LEFT")
    if w.title.SetWordWrap then w.title:SetWordWrap(false) end

    w:SetScript("OnShow", function(self) LayoutBagWindow(self); PlaceBagWindows() end)
    w:SetScript("OnHide", function() PlaceBagWindows() end)    -- the others close the gap
    w:SetScale(db.scale or 1)
    if db.bagPos[bag] then
        w:ClearAllPoints()
        w:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", db.bagPos[bag][1], db.bagPos[bag][2])
    end
    w:Hide()
    bagWins[bag] = w
    return w
end

local function ToggleBagWindow(bag)
    if not IsSingleBag(bag) or NumSlots(bag) == 0 then return end
    local w = bagWins[bag] or BuildBagWindow(bag)
    if w:IsShown() then w:Hide(); return end
    if InCombatLockdown() and not w.laidOut then
        -- New item buttons can't be made in combat: it opens when the fight ends.
        w.openAfterCombat = true
        print(PREFIX .. BagName(bag) .. " opens when this fight ends.")
        return
    end
    w:Show()
end

local function ForEachBagWindow(fn)
    for _, w in pairs(bagWins) do fn(w) end
end

local function HideBagWindows()
    ForEachBagWindow(function(w) w.openAfterCombat = nil; if w:IsShown() then w:Hide() end end)
end

-- ==========================================
-- OPENING AND CLOSING (instead of Blizzard's bags)
-- ==========================================
local function Show() if not win then return end; win:Show() end
local function Hide() if win then win:Hide() end; HideBagWindows() end
-- The bag key: opens the combined window; if it's already open, closes it
-- and any one-bag windows too.
local function Toggle() if not win then return end; if win:IsShown() then Hide() else win:Show() end end

-- Several bag calls can arrive at once (B opens five bags): act once per
-- moment. source: "click" (a bag slot on the bag bar was clicked), "bag"
-- (ToggleBag for one bag: a click, or a Toggle Bag 1-4 key), "call" (any
-- other bag call: the bag key, the backpack, open/close all), or nil (one of
-- Blizzard's bag windows showed up). One bag asked for, and nothing else,
-- opens that bag's own window; anything else goes to the combined window.
local HideBlizzardBags   -- below
local pendingAction, clickBag, bagRequests, otherCall, timerSet
local function Act(action, source, bag)
    if not db or not db.replace then return end
    if source == "click" then clickBag = bag
    elseif source == "bag" then bagRequests = bagRequests or {}; bagRequests[bag] = true
    elseif source == "call" then otherCall = true end
    if action and not (action == "toggle" and pendingAction == "toggle") then pendingAction = action end
    if timerSet then return end
    timerSet = true
    C_Timer.After(0, function()
        timerSet = false
        local a, click, reqs, other = pendingAction, clickBag, bagRequests, otherCall
        pendingAction, clickBag, bagRequests, otherCall = nil, nil, nil, nil
        HideBlizzardBags()        -- in case one opened after our hook ran
        local only = click
        if not only and reqs and not other then
            local n = 0
            for b in pairs(reqs) do n = n + 1; only = b end
            if n ~= 1 then only = nil end
        end
        if only then ToggleBagWindow(only)
        elseif a == "toggle" then Toggle()
        elseif a == "open" then Show()
        elseif a == "close" then Hide() end
    end)
end

-- Blizzard's bag windows stay closed while AetherPack is in charge: the
-- one-per-bag windows for your carried bags, and the newer combined backpack.
local function IsCarriedBagFrame(f)
    if f == ContainerFrameCombinedBags then return true end
    local id = f.GetID and f:GetID()
    return id and ((id >= 0 and id <= 4) or (REAGENT_BAG ~= nil and id == REAGENT_BAG))
end

HideBlizzardBags = function()
    if not db.replace then return end
    for i = 1, (NUM_CONTAINER_FRAMES or 13) do
        local f = _G["ContainerFrame" .. i]
        if f and f:IsShown() and IsCarriedBagFrame(f) then f:Hide() end
    end
    if ContainerFrameCombinedBags and ContainerFrameCombinedBags:IsShown() then ContainerFrameCombinedBags:Hide() end
end

local function HookBags()
    for name, action in pairs({ ToggleAllBags = "toggle", ToggleBackpack = "toggle", ToggleBag = "toggle",
                                OpenAllBags = "open", OpenBackpack = "open",
                                CloseAllBags = "close", CloseBackpack = "close" }) do
        if _G[name] then
            hooksecurefunc(name, function(id)
                HideBlizzardBags()
                if name == "ToggleBag" then
                    -- Your bags only (0-4 and the reagent bag); the bank and keyring stay Blizzard's.
                    if id and (id < 0 or id > 4) and id ~= REAGENT_BAG then return end
                    if IsSingleBag(id) then Act(action, "bag", id); return end
                end
                Act(action, "call")
            end)
        end
    end
    -- The bag slots on the bag bar: a plain click opens that bag's own window.
    -- (Dropping an item on a slot puts it in the bag, as before.)
    local slots = {}
    for i = 0, 3 do slots[#slots + 1] = { _G["CharacterBag" .. i .. "Slot"], i + 1 } end
    if REAGENT_BAG then slots[#slots + 1] = { _G["CharacterReagentBag0Slot"], REAGENT_BAG } end
    for _, s in ipairs(slots) do
        local button, bag = s[1], s[2]
        if button and button.HookScript then
            local wanted
            button:HookScript("PreClick", function(_, mouse)
                wanted = db.replace and (mouse == nil or mouse == "LeftButton")
                    and not (CursorHasItem and CursorHasItem()) and not (IsModifierKeyDown and IsModifierKeyDown())
            end)
            button:HookScript("PostClick", function()
                if wanted then HideBlizzardBags(); Act(nil, "click", bag) end
                wanted = nil
            end)
        end
    end
    local frames = {}
    for i = 1, (NUM_CONTAINER_FRAMES or 13) do frames[#frames + 1] = _G["ContainerFrame" .. i] end
    frames[#frames + 1] = ContainerFrameCombinedBags
    for _, f in ipairs(frames) do
        f:HookScript("OnShow", function(self)
            if db.replace and IsCarriedBagFrame(self) then
                self:Hide()
                Act("toggle")     -- whatever opened it (a key, a bag button): AetherPack opens or closes instead
            end
        end)
    end
end

-- ==========================================
-- EVENTS
-- ==========================================
local events = CreateFrame("Frame")
for _, event in ipairs({ "ADDON_LOADED", "PLAYER_LOGIN", "BAG_UPDATE_DELAYED", "ITEM_LOCK_CHANGED",
    "BAG_UPDATE_COOLDOWN", "PLAYER_MONEY", "MERCHANT_SHOW", "MERCHANT_CLOSED", "PLAYER_REGEN_ENABLED",
    "QUEST_LOG_UPDATE", "GET_ITEM_INFO_RECEIVED", "PLAYER_EQUIPMENT_CHANGED" }) do
    pcall(events.RegisterEvent, events, event)
end
-- Picking up or putting down an item starts or stops the deposit slot's pulse
-- (CURSOR_CHANGED in newer clients, CURSOR_UPDATE in older ones).
for _, event in ipairs({ "CURSOR_CHANGED", "CURSOR_UPDATE" }) do pcall(events.RegisterEvent, events, event) end

local refreshSoon = false
local function LayoutSoon()
    if refreshSoon then return end
    refreshSoon = true
    C_Timer.After(0.1, function()
        refreshSoon = false
        if win and win:IsShown() then AetherPack_Layout() end
        local moved = false
        ForEachBagWindow(function(w)
            if w:IsShown() then
                local h = w.h
                LayoutBagWindow(w)                -- a bag swapped for a bigger one, or taken off
                if w.h ~= h or not w:IsShown() then moved = true end
            end
        end)
        if moved then PlaceBagWindows() end
    end)
end

events:SetScript("OnEvent", function(_, event, arg1)
    if event == "CURSOR_CHANGED" or event == "CURSOR_UPDATE" then
        if win then UpdatePulse() end
        return
    end
    if event == "ADDON_LOADED" and arg1 == "AetherPack" then
        AetherPackDB = AetherPackDB or {}
        db = AetherPackDB
        for k, v in pairs(DEFAULTS) do
            if db[k] == nil then db[k] = type(v) == "table" and CopyTable and CopyTable(v) or v end
        end
        if type(db.collapsed) ~= "table" then db.collapsed = { empty = true } end
        if type(db.bagPos) ~= "table" then db.bagPos = {} end
    elseif event == "PLAYER_LOGIN" then
        BuildWindow()
        UpdateMoney()          -- also notes the gold you logged in with
        HookBags()
        C_Timer.After(2, function() UpdateBackpackCount() end)
    elseif not win then
        return
    elseif event == "MERCHANT_SHOW" then
        win.atMerchant = true
        if db.replace then win:Show() end
        LayoutSoon()
    elseif event == "MERCHANT_CLOSED" then
        win.atMerchant = false
        if win.sell then win.sell:Hide() end
    elseif event == "PLAYER_REGEN_ENABLED" then
        if layoutPending and win:IsShown() then AetherPack_Layout() end
        if bagLayoutPending then
            bagLayoutPending = false
            ForEachBagWindow(function(w) if w:IsShown() then LayoutBagWindow(w) end end)
            PlaceBagWindows()
        end
        ForEachBagWindow(function(w)
            if w.openAfterCombat then w.openAfterCombat = nil; w:Show() end
        end)
    elseif event == "ITEM_LOCK_CHANGED" or event == "BAG_UPDATE_COOLDOWN" then
        if win:IsShown() then RefreshButtons() end
        ForEachBagWindow(function(w) if w:IsShown() then RefreshBagWindow(w) end end)
    elseif event == "PLAYER_MONEY" then
        UpdateMoney()
    else
        if event == "BAG_UPDATE_DELAYED" then UpdateBackpackCount() end   -- even with the window closed
        LayoutSoon()
    end
end)

-- ==========================================
-- SLASH COMMANDS AND API
-- ==========================================
SLASH_AETHERPACK1 = "/pack"
SLASH_AETHERPACK2 = "/aetherpack"
SlashCmdList["AETHERPACK"] = function(msg)
    local cmd, arg = strlower(strtrim(msg or "")):match("^(%S*)%s*(.-)$")
    if cmd == "" then
        Toggle()
    elseif cmd == "replace" then
        db.replace = (arg == "on") or (arg ~= "off" and not db.replace)
        print(PREFIX .. "opens instead of Blizzard's bags: " .. (db.replace and "|cff33dd66on|r" or "|cffff5555off|r"))
    elseif cmd == "columns" and tonumber(arg) then
        db.columns = math.max(6, math.min(16, math.floor(tonumber(arg))))
        AetherPack_Layout()
    elseif cmd == "scale" and tonumber(arg) then
        db.scale = math.max(0.6, math.min(1.5, tonumber(arg)))
        if win then win:SetScale(db.scale) end
        ForEachBagWindow(function(w) w:SetScale(db.scale) end)
        PlaceBagWindows()
    elseif cmd == "deposit" then
        db.deposit = (arg == "on") or (arg ~= "off" and not db.deposit)
        AetherPack_Layout()
        print(PREFIX .. "No swaps. Just drops. slot: " .. (db.deposit and "|cff33dd66on|r" or "|cffff5555off|r"))
    elseif cmd == "pulse" and (arg == "item" or arg == "always" or arg == "off") then
        db.depositPulse = arg
        if AetherPack_UpdatePulse then AetherPack_UpdatePulse() end
        print(PREFIX .. "the deposit slot's number pulses: " .. ({ item = "while you hold an item", always = "all the time", off = "never" })[arg] .. ".")
    elseif cmd == "count" then
        db.backpackCount = (arg == "on") or (arg ~= "off" and not db.backpackCount)
        UpdateBackpackCount()
        print(PREFIX .. "free slots on the backpack button: " .. (db.backpackCount and "|cff33dd66on|r" or "|cffff5555off|r"))
    elseif cmd == "reset" then
        db.pos = nil
        if win then win:ClearAllPoints(); win:SetPoint("BOTTOMRIGHT", UIParent, "BOTTOMRIGHT", -80, 120) end
        db.bagPos = {}
        PlaceBagWindows()
        print(PREFIX .. "windows back in their starting spots.")
    else
        print(PREFIX .. "your bags, sorted into sections.")
        print("  /pack                 open or close (B opens it too)")
        print("  Click a bag on the bag bar to open just that bag.")
        print("  /pack replace on|off  open instead of Blizzard's bags")
        print("  /pack columns 6-16    icons per row")
        print("  /pack count on|off    free bag slots on the backpack button")
        print("  /pack deposit on|off  the No swaps. Just drops. slot")
        print("  /pack pulse item|always|off  when its number pulses")
        print("  /pack scale 0.6-1.5   window size")
        print("  /pack reset           windows back to their starting spots")
    end
end

AetherPack_API = {
    Toggle = Toggle,
    Layout = function() AetherPack_Layout() end,
}
