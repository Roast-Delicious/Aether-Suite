-- ==========================================
-- AetherHub - one options window for our WoW Forever addons
-- AetherMeter, AetherBars, AetherCoords, AetherPathfinder, AetherMarks, AetherItemID, AetherLedger and AetherPack.
--
-- It changes settings through each addon's own slash commands, so every
-- change applies right away.
--
-- It also keeps a backup of the settings of the addons that only save
-- account-wide (WoW Forever 1.60 has been reported not to load those back)
-- and puts the backup in place if their settings come back empty.
-- They list AetherHub as an optional dependency, so it loads before them.
-- ==========================================

local ADDON_NAME = ...
local PREFIX = "|cff4da6ffAetherHub:|r "

local hubDB   -- merged account + character settings for the hub itself

-- Addons whose settings the hub backs up, and the saved table each one uses.
local BACKUP = {
    AetherMeter  = "AetherMeterDB",
    AetherBars   = "AetherBarsDB",
    AetherCoords = "AetherCoordsDB",
}

-- Names these addons had before the Aether rename; an old backup still counts.
local OLD_NAMES = {
    AetherBars   = "CleanBars",
    AetherCoords = "MapCoords",
}

-- ==========================================
-- HELPERS
-- ==========================================

local function IsLoaded(name)
    if C_AddOns and C_AddOns.IsAddOnLoaded then return C_AddOns.IsAddOnLoaded(name) end
    return IsAddOnLoaded and IsAddOnLoaded(name)
end

local function Version(name)
    local get = (C_AddOns and C_AddOns.GetAddOnMetadata) or GetAddOnMetadata
    return get and get(name, "Version") or "?"
end

local function DeepCopy(v)
    if type(v) ~= "table" then return v end
    local out = {}
    for k, x in pairs(v) do out[k] = DeepCopy(x) end
    return out
end

-- Runs another addon's slash command (it prints its usual one-line confirmation).
local function Run(slashKey, input)
    local handler = SlashCmdList[slashKey]
    if not handler then return end
    local ok, err = pcall(handler, input or "")
    if not ok then geterrorhandler()(err) end
end

local function Pct(v) return math.floor((v or 0) * 100 + 0.5) end

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
    b:SetNormalFontObject(small and "GameFontHighlightSmall" or "GameFontHighlight")
    b:SetHighlightFontObject(small and "GameFontHighlightSmall" or "GameFontHighlight")
    b:SetDisabledFontObject(small and "GameFontDisableSmall" or "GameFontDisable")
    b:SetText(" ")
    b.aetherSmall = small
    return b
end

-- Mark a choice button as selected: highlighted, lettering in Aether yellow.
-- Swaps font objects (GameFontNormal is that yellow) instead of SetTextColor,
-- because LockHighlight and mouse-over switch to the highlight font and wipe
-- a plain color change back to white.
local function SetSelected(b, on)
    local font = (on and "GameFontNormal" or "GameFontHighlight") .. (b.aetherSmall and "Small" or "")
    b:SetNormalFontObject(font)
    b:SetHighlightFontObject(font)
    if on then b:LockHighlight() else b:UnlockHighlight() end
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
    local MEDIA, WHITE = "Interface\\AddOns\\AetherHub\\Media\\", "Interface\\Buttons\\WHITE8X8"
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

-- Yes/No question. Our own small box, not WoW's shared popups: an addon using
-- those can get Blizzard's own protected popups blocked.
local confirmBox

local function Confirm(question, action)
    if not confirmBox then
        local f = CreateFrame("Frame", "AetherHubConfirm", UIParent, "BackdropTemplate")
        f:SetSize(320, 96)
        f:SetPoint("CENTER", UIParent, "CENTER", 0, 140)
        f:SetFrameStrata("FULLSCREEN_DIALOG")
        f:EnableMouse(true)
        f:Hide()
        if f.SetBackdrop then
            f:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8X8", edgeFile = "Interface\\Buttons\\WHITE8X8", edgeSize = 1 })
            f:SetBackdropColor(0.05, 0.05, 0.08, 0.95)
            f:SetBackdropBorderColor(0.3, 0.7, 1, 0.8)
        end
        AetherDecorate(f, 0)
        f.text = f:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
        f.text:SetPoint("TOPLEFT", 14, -14)
        f.text:SetPoint("TOPRIGHT", -14, -14)
        f.text:SetJustifyH("CENTER")
        local yes = AetherButton(f)
        yes:SetSize(100, 22)
        yes:SetPoint("BOTTOMRIGHT", f, "BOTTOM", -6, 12)
        yes:SetText(YES or "Yes")
        yes:SetScript("OnClick", function()
            local run = f.action
            f:Hide()
            if run then run() end
        end)
        local no = AetherButton(f)
        no:SetSize(100, 22)
        no:SetPoint("BOTTOMLEFT", f, "BOTTOM", 6, 12)
        no:SetText(NO or "No")
        no:SetScript("OnClick", function() f:Hide() end)
        confirmBox = f
    end
    confirmBox.text:SetText(question)
    confirmBox.action = action
    confirmBox:Show()
end

-- ==========================================
-- SETTINGS BACKUP
-- ==========================================

local function LoadHubDB()
    local merged = {}
    local sources = { AetherHubCharDB, AetherHubDB }
    for i = 1, 2 do              -- not ipairs: it stops at the first nil
        local source = sources[i]
        if type(source) == "table" then
            for k, v in pairs(source) do
                if merged[k] == nil then merged[k] = v end
            end
        end
    end
    merged.backup = type(merged.backup) == "table" and merged.backup or {}
    hubDB = merged
    AetherHubDB = hubDB
    AetherHubCharDB = hubDB
end

-- Called as each addon finishes loading, before that addon reads its settings.
local function RestoreIfEmpty(addon)
    local varName = BACKUP[addon]
    local saved = hubDB and (hubDB.backup[addon] or hubDB.backup[OLD_NAMES[addon] or ""])
    if not varName or type(saved) ~= "table" then return end
    local current = _G[varName]
    if current == nil or (type(current) == "table" and next(current) == nil) then
        _G[varName] = DeepCopy(saved)
        hubDB.restored = hubDB.restored or {}
        hubDB.restored[addon] = true
    end
end

local function TakeBackups()
    if not hubDB then return end
    for addon, varName in pairs(BACKUP) do
        if type(_G[varName]) == "table" then
            hubDB.backup[addon] = DeepCopy(_G[varName])
        end
    end
end

-- ==========================================
-- YOUR CHARACTER (shared with the other Aether addons)
-- ==========================================
-- Class, race, level and professions are read from the game, so there's
-- nothing to set up and it's right on every character. The only settings
-- are "interests" (which suggestions you want), kept per character.
-- Other addons read it through AetherHub_Profile.

local PROFESSIONS = {
    { key = "alchemy",        name = "Alchemy",        id = 171, kind = "craft",  words = { "alchem" } },
    { key = "blacksmithing",  name = "Blacksmithing",  id = 164, kind = "craft",  words = { "blacksmith" } },
    { key = "enchanting",     name = "Enchanting",     id = 333, kind = "craft",  words = { "enchant" } },
    { key = "engineering",    name = "Engineering",    id = 202, kind = "craft",  words = { "engineer" } },
    { key = "leatherworking", name = "Leatherworking", id = 165, kind = "craft",  words = { "leatherwork" } },
    { key = "tailoring",      name = "Tailoring",      id = 197, kind = "craft",  words = { "tailor" } },
    { key = "herbalism",      name = "Herbalism",      id = 182, kind = "gather", words = { "herbalis" } },
    { key = "mining",         name = "Mining",         id = 186, kind = "gather", words = { "mining", "miner" } },
    { key = "skinning",       name = "Skinning",       id = 393, kind = "gather", words = { "skinning", "skinner" } },
    { key = "cooking",        name = "Cooking",        id = 185, kind = "second", words = { "cooking", "chef" } },
    { key = "firstaid",       name = "First Aid",      id = 129, kind = "second", words = { "first aid" } },
    { key = "fishing",        name = "Fishing",        id = 356, kind = "second", words = { "fishing", "fisherman" } },
}
local PROFESSION_BY_NAME = {}
for _, p in ipairs(PROFESSIONS) do PROFESSION_BY_NAME[p.name:lower()] = p end

-- The next rank to train when your skill is capped at "cap".
-- trainers: words a trainer's title must have to teach it (nil = any trainer
-- of that profession). Crafting trainers are titled by their own rank, and
-- teach the rank below it (an "Artisan Leatherworker" teaches Expert).
local RANKS = {
    [75]  = { name = "Journeyman", cap = 150, level = 10, skill = 50 },
    [150] = { name = "Expert",     cap = 225, level = 20, skill = 125, craftTrainers = { "artisan", "master" } },
    [225] = { name = "Artisan",    cap = 300, level = 35, skill = 200, craftTrainers = { "master" } },
}

local INTERESTS = {
    { key = "rankUps",     label = "Remind me when a profession needs its next rank trained" },
    { key = "profQuests",  label = "Suggest profession quests" },
    { key = "classQuests", label = "Suggest class quests" },
    { key = "skinning",    label = "Suggest where to skin for skill-ups" },
    { key = "manageTracker", label = "Keep my quest tracker on my zone, sorted by level" },
}

local profCache, profDirty = nil, true

local function ReadProfessions()
    local list, seen = {}, {}
    local function Add(name, rank, max)
        local p = name and PROFESSION_BY_NAME[tostring(name):lower()]
        if p and not seen[p.key] and rank then
            seen[p.key] = true
            list[#list + 1] = { key = p.key, name = p.name, id = p.id, kind = p.kind, rank = rank, max = max or rank }
        end
    end
    if GetNumSkillLines and GetSkillLineInfo then
        pcall(function()
            for i = 1, GetNumSkillLines() or 0 do
                local name, isHeader, _, rank, _, _, max = GetSkillLineInfo(i)
                if not isHeader then Add(name, rank, max) end
            end
        end)
    end
    if #list == 0 and GetProfessions and GetProfessionInfo then
        pcall(function()
            for _, index in pairs({ GetProfessions() }) do
                if index then
                    local name, _, rank, max = GetProfessionInfo(index)
                    Add(name, rank, max)
                end
            end
        end)
    end
    table.sort(list, function(a, b) return a.name < b.name end)
    return list
end

local function CharKey()
    return (UnitName("player") or "?") .. "-" .. ((GetRealmName and GetRealmName()) or "?")
end

local function Interests()
    if not hubDB then return {} end
    hubDB.interests = hubDB.interests or {}
    hubDB.interests[CharKey()] = hubDB.interests[CharKey()] or {}
    return hubDB.interests[CharKey()]
end

local function GetProfile()
    if profDirty or not profCache then
        profCache, profDirty = ReadProfessions(), false
    end
    local className, classToken, classID = UnitClass("player")
    local raceName, raceToken, raceID = UnitRace("player")
    return {
        name = UnitName("player"), level = UnitLevel("player"),
        className = className, class = classToken, classID = classID,
        raceName = raceName, race = raceToken, raceID = raceID,
        faction = UnitFactionGroup("player"),
        professions = profCache,
    }
end

-- What to train next for a profession entry from GetProfile(), or nil when
-- it isn't near its cap (within "margin" points) or is maxed out.
local function NextRank(prof, margin)
    local rank = RANKS[prof.max]
    if not rank or prof.rank < prof.max - (margin or 5) then return nil end
    local info = PROFESSION_BY_NAME[prof.name:lower()]
    return {
        name = rank.name, cap = rank.cap, level = rank.level,
        trainerWords = info and info.words,
        titleWords = (info and info.kind == "craft") and rank.craftTrainers or nil,
        fromBook = info and info.kind == "second" and prof.max >= 150,   -- Expert/Artisan cooking, first aid, fishing
    }
end

AetherHub_Profile = {
    Get = GetProfile,
    NextRank = NextRank,
    PROFESSIONS = PROFESSIONS,
    Interest = function(key) return Interests()[key] ~= false end,
    SetInterest = function(key, value) Interests()[key] = value and true or false end,
}

-- ==========================================
-- WINDOW
-- ==========================================

local WIN_W, WIN_H = 620, 500
local SIDE_W = 160
local PAGE_W = WIN_W - SIDE_W - 24 - 30   -- page content width (room for the scroll bar); grows with the window
local hub, pages, tabs = nil, {}, {}
local SelectPage            -- below (the shared-page links use it)
local UpdateMinimapButton   -- below

local function Backdrop(frame, alpha)
    frame:SetBackdrop({
        bgFile   = "Interface\\ChatFrame\\ChatFrameBackground",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true, tileSize = 16, edgeSize = 12,
        insets = { left = 4, right = 4, top = 4, bottom = 4 },
    })
    frame:SetBackdropColor(0.05, 0.05, 0.05, alpha or 0.95)
    frame:SetBackdropBorderColor(0.3, 0.7, 1, 1)
end

-- ----- controls -----

local function Track(page, control)
    page.controls[#page.controls + 1] = control
    return control
end

-- A one-line explanation when you hover a control.
local function Tip(frame, text)
    if not text or not frame then return end
    frame:HookScript("OnEnter", function(self)
        -- Beside the window, level with the control, so it never covers the page.
        local top, hubTop = self:GetTop(), hub and hub:GetTop()
        if hub and hub:IsShown() and top and hubTop then
            GameTooltip:SetOwner(self, "ANCHOR_NONE")
            GameTooltip:ClearAllPoints()
            GameTooltip:SetPoint("TOPLEFT", hub, "TOPRIGHT", 6, math.min(0, top - hubTop + 4))
        else
            GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        end
        GameTooltip:SetText(text, 1, 1, 1, 1, true)
        GameTooltip:Show()
    end)
    frame:HookScript("OnLeave", function() GameTooltip:Hide() end)
end

local function AddHeader(page, text)
    local fs = page:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    fs:SetPoint("TOPLEFT", page, "TOPLEFT", 0, page.y)
    fs:SetText(text)
    page.y = page.y - 22
end

local function AddNote(page, text, getText, minLines)
    local fs = page:CreateFontString(nil, "OVERLAY", "GameFontHighlight")   -- easy-to-read size
    fs:SetPoint("TOPLEFT", page, "TOPLEFT", 2, page.y)
    fs:SetPoint("RIGHT", page, "RIGHT", -4, 0)
    fs:SetJustifyH("LEFT")
    fs:SetTextColor(0.86, 0.86, 0.86)
    fs:SetText(text)
    page.notes = page.notes or {}
    page.notes[#page.notes + 1] = { fs = fs, y = page.y }   -- for the scroll height
    page.y = page.y - math.max(18 * (minLines or 1), fs:GetStringHeight() + 8)
    if getText then
        Track(page, { Refresh = function() fs:SetText(getText()) end })
    end
end

local function MakeCheck(parent, label)
    -- Aether look: a navy box with a blue edge; when on, a gold fill and gold edge.
    local cb = CreateFrame("CheckButton", nil, parent, "BackdropTemplate")
    cb:SetSize(16, 16)
    if cb.SetBackdrop then
        cb:SetBackdrop({ edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        cb:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    cb:SetNormalTexture(AetherFill(cb, 0.07, 0.17, 0.32, 0.95))
    local hl = AetherFill(cb, 0.3, 0.65, 1, 0.3)
    hl:SetBlendMode("ADD")
    cb:SetHighlightTexture(hl)
    local function Mark(r, g, b)
        local t = cb:CreateTexture(nil, "ARTWORK")
        t:SetColorTexture(r, g, b, 1)
        t:SetPoint("TOPLEFT", 4, -4)
        t:SetPoint("BOTTOMRIGHT", -4, 4)
        return t
    end
    cb:SetCheckedTexture(Mark(1, 0.82, 0))
    cb:SetDisabledCheckedTexture(Mark(0.45, 0.45, 0.48))
    function cb:UpdateEdge()
        if not self.SetBackdropBorderColor then return end
        if not self:IsEnabled() then self:SetBackdropBorderColor(0.4, 0.4, 0.42, 0.9)
        elseif self:GetChecked() then self:SetBackdropBorderColor(1, 0.82, 0, 1)
        else self:SetBackdropBorderColor(0.3, 0.65, 1, 0.9) end
    end
    cb.label = cb:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    cb.label:SetPoint("LEFT", cb, "RIGHT", 6, 0)
    cb.label:SetText(label)
    cb:SetHitRectInsets(0, -(cb.label:GetStringWidth() + 6), 0, 0)   -- label is clickable too
    return cb
end

-- get() returns true/false; set(value) applies it.
-- label may be text or a function that returns the text (re-read on refresh).
-- enabled, if given, is a function; the box is grayed out when it returns false.
local function AddCheck(page, label, get, set, x, sameRow, enabled, tip)
    local labelFn = type(label) == "function" and label or nil
    local cb = MakeCheck(page, labelFn and labelFn() or label)
    Tip(cb, tip)
    cb:SetPoint("TOPLEFT", page, "TOPLEFT", (x or 0) + 4, page.y - 4)
    cb:SetScript("OnClick", function(self)
        set(self:GetChecked() and true or false)
        cb:Refresh()
    end)
    function cb:Refresh()
        if labelFn then
            self.label:SetText(labelFn())
            self:SetHitRectInsets(0, -(self.label:GetStringWidth() + 6), 0, 0)
        end
        local on = not enabled or enabled()
        self:SetEnabled(on)
        if on then self.label:SetTextColor(1, 1, 1) else self.label:SetTextColor(0.5, 0.5, 0.5) end
        self:SetChecked(get() and true or false)
        self:UpdateEdge()
    end
    if not sameRow then page.y = page.y - 26 end
    return Track(page, cb)
end

-- Two columns of checkboxes.
local function AddCheckGrid(page, items)
    for i, item in ipairs(items) do
        local col = (i - 1) % 2
        AddCheck(page, item.label, item.get, item.set, col == 0 and 0 or 210, true, item.enabled, item.tip)
        if col == 1 or i == #items then page.y = page.y - 26 end
    end
end

-- A slider; values are whole numbers between min and max.
local function AddSlider(page, label, min, max, step, get, set, suffix, tip)
    local title = page:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    title:SetPoint("TOPLEFT", page, "TOPLEFT", 4, page.y)
    title:SetText(label)
    page.y = page.y - 20

    local s = CreateFrame("Slider", nil, page)
    s:SetOrientation("HORIZONTAL")
    s:SetSize(240, 16)
    s:SetPoint("TOPLEFT", page, "TOPLEFT", 8, page.y)
    s:SetMinMaxValues(min, max)
    s:SetValueStep(step)
    if s.SetObeyStepOnDrag then s:SetObeyStepOnDrag(true) end
    local thumb = s:CreateTexture(nil, "OVERLAY")      -- Aether look: a gold handle
    thumb:SetColorTexture(1, 0.82, 0, 1)
    thumb:SetSize(8, 16)
    s:SetThumbTexture(thumb)
    s:EnableMouse(true)

    local track = s:CreateTexture(nil, "BACKGROUND")
    track:SetColorTexture(0.12, 0.28, 0.5, 0.9)
    track:SetHeight(4)
    track:SetPoint("LEFT", s, "LEFT", 0, 0)
    track:SetPoint("RIGHT", s, "RIGHT", 0, 0)

    Tip(s, tip)
    -- The range at each end, under the track.
    local function Fmt(v) return (math.floor(v * 100 + 0.5) / 100) .. (suffix or "") end
    local lo = s:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    lo:SetPoint("TOPLEFT", s, "BOTTOMLEFT", 0, 1)
    lo:SetText(Fmt(min))
    local hi = s:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    hi:SetPoint("TOPRIGHT", s, "BOTTOMRIGHT", 0, 1)
    hi:SetText(Fmt(max))

    -- The value: click it to type an exact number, Enter to apply.
    local valueText = CreateFrame("EditBox", nil, s, "BackdropTemplate")
    valueText:SetSize(54, 20)
    valueText:SetPoint("LEFT", s, "RIGHT", 12, 0)
    valueText:SetAutoFocus(false)
    valueText:SetFontObject("GameFontHighlight")
    valueText:SetJustifyH("CENTER")
    if valueText.SetBackdrop then
        valueText:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        valueText:SetBackdropColor(0.07, 0.17, 0.32, 0.95)
        valueText:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    Tip(valueText, "Click to type an exact value, then press Enter.")
    valueText:SetScript("OnEnterPressed", function(self)
        local v = tonumber((self:GetText() or ""):match("[%d%.]+"))
        self:ClearFocus()
        if v then
            v = math.max(min, math.min(max, math.floor(v / step + 0.5) * step))
            s:SetValue(v)
        end
        self:SetText(Fmt(s:GetValue()))
    end)
    valueText:SetScript("OnEscapePressed", function(self) self:ClearFocus(); self:SetText(Fmt(s:GetValue())) end)
    valueText:SetScript("OnEditFocusGained", function(self) self:HighlightText() end)

    local pending
    s:SetScript("OnValueChanged", function(self, value)
        value = math.floor(value / step + 0.5) * step
        valueText:SetText(Fmt(value))
        if self.refreshing then return end
        -- Wait until the slider stops moving, then apply once.
        if pending then pending:Cancel() end
        pending = C_Timer.NewTimer(0.2, function() pending = nil; set(value) end)
    end)
    function s:Refresh()
        local value = get()
        self.refreshing = true
        self:SetValue(value)
        self.refreshing = false
        valueText:SetText(Fmt(value))
    end
    page.y = page.y - 36
    return Track(page, s)
end

-- A row of buttons where one is selected: options = { {value, label}, ... }
local function AddChoice(page, label, options, get, set, tip)
    local title = page:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    title:SetPoint("TOPLEFT", page, "TOPLEFT", 4, page.y)
    title:SetText(label)
    page.y = page.y - 20

    local buttons, prev = {}, nil
    for _, opt in ipairs(options) do
        local b = AetherButton(page)
        b:SetText(opt[2])
        b:SetSize(math.max(80, b:GetFontString():GetStringWidth() + 20), 20)
        if prev then b:SetPoint("LEFT", prev, "RIGHT", 4, 0)
        else b:SetPoint("TOPLEFT", page, "TOPLEFT", 6, page.y) end
        b.value = opt[1]
        Tip(b, tip)
        buttons[#buttons + 1] = b
        prev = b
    end
    local control = {}
    function control:Refresh()
        local current = get()
        for _, b in ipairs(buttons) do
            SetSelected(b, b.value == current)
        end
    end
    for _, b in ipairs(buttons) do
        b:SetScript("OnClick", function() set(b.value); control:Refresh() end)
    end
    page.y = page.y - 28
    return Track(page, control)
end

-- A dropdown: a button showing the current choice; clicking it lists the options.
-- options() returns { {value, label}, ... }; getText() is the button's text.
-- After a choice, the whole page refreshes (other labels may depend on it).
local function AddDropdown(page, label, options, get, set, getText, tip)
    local title = page:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    title:SetPoint("TOPLEFT", page, "TOPLEFT", 4, page.y - 3)
    title:SetText(label)

    local b = AetherButton(page)
    b:SetSize(190, 22)
    b:SetPoint("LEFT", title, "RIGHT", 10, 0)
    Tip(b, tip)
    local control = {}
    function control:Refresh() b:SetText(getText() .. "  |cff4da6ffv|r") end
    b:SetScript("OnClick", function(self)
        MenuUtil.CreateContextMenu(self, function(_, root)
            for _, opt in ipairs(options()) do
                root:CreateRadio(opt[2],
                    function() return get() == opt[1] end,
                    function()
                        set(opt[1])
                        if page:IsShown() then page:GetScript("OnShow")(page) end
                    end)
            end
        end)
    end)
    page.y = page.y - 30
    return Track(page, control)
end

-- A row of action buttons: list = { {label, onClick}, ... }
local function AddButtons(page, list)
    local prev
    for _, item in ipairs(list) do
        local b = AetherButton(page)
        b:SetText(item[1])
        b:SetSize(math.max(90, b:GetFontString():GetStringWidth() + 24), 22)
        if prev then b:SetPoint("LEFT", prev, "RIGHT", 6, 0)
        else b:SetPoint("TOPLEFT", page, "TOPLEFT", 4, page.y) end
        Tip(b, item[3])
        b:SetScript("OnClick", function()
            item[2]()
            if page:IsShown() then page:GetScript("OnShow")(page) end
        end)
        prev = b
    end
    page.y = page.y - 30
end

-- "Also on: Fading, Layout": small buttons that open the shared pages where
-- this addon's look, fading or placement now live.
local function AddLinks(page, names, text)
    local label = page:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    label:SetPoint("TOPLEFT", page, "TOPLEFT", 4, page.y - 4)
    label:SetTextColor(0.7, 0.7, 0.7)
    label:SetText(text or "Its look, fading and placement:")
    local prev = label
    for _, name in ipairs(names) do
        local b = AetherButton(page, nil, true)
        b:SetText(name .. "  >")
        b:SetSize(b:GetFontString():GetStringWidth() + 20, 18)
        b:SetPoint("LEFT", prev, "RIGHT", 6, 0)
        Tip(b, "Open the " .. name .. " page.")
        b:SetScript("OnClick", function() SelectPage(name) end)
        prev = b
    end
    page.y = page.y - 28
end

-- ==========================================
-- RELOAD HINT
-- ==========================================
-- The few settings that need a reload turn the Reload UI button gold.
local needsReload = false
local function NeedReload()
    needsReload = true
    local b = hub and hub.reload
    if b then
        if b.SetBackdropBorderColor then b:SetBackdropBorderColor(1, 0.82, 0, 1) end
        b:SetText("|cffffd100Reload UI|r")
    end
end

-- ==========================================
-- MINIMAP BUTTON
-- ==========================================
-- A round button on the minimap's edge: left-click opens AetherHub,
-- right-click lists shortcuts, drag slides it around the edge.
local minimapButton

local function PlaceMinimapButton()
    local angle = math.rad(hubDB.minimapAngle or 215)
    local x, y = math.cos(angle), math.sin(angle)
    local radius = (Minimap:GetWidth() or 140) / 2 + 6
    local square = GetMinimapShape and GetMinimapShape() == "SQUARE"
    if square then   -- run along the square's edge instead of a circle
        local m = math.max(math.abs(x), math.abs(y))
        x, y = x / m, y / m
    end
    minimapButton:ClearAllPoints()
    minimapButton:SetPoint("CENTER", Minimap, "CENTER", x * radius, y * radius)
end

local function ShortcutMenu(owner)
    if not (MenuUtil and MenuUtil.CreateContextMenu) then AetherHub_Toggle(); return end
    MenuUtil.CreateContextMenu(owner, function(_, root)
        root:CreateTitle("Aether")
        root:CreateButton("Open AetherHub", function() AetherHub_Toggle() end)
        local ledger = AetherLedger_API
        if ledger then
            root:CreateButton("Check Zones Now", function() ledger.Check() end)
            root:CreateButton("Directions to Best Zone", function() ledger.GoBest() end)
            root:CreateButton("Clean Up Quest Log", function() ledger.Cleanup() end)
        end
        if SlashCmdList["AETHERMETER"] then
            root:CreateButton("Show or Hide Meter", function()
                Run("AETHERMETER", (AetherMeterFrame and AetherMeterFrame:IsShown()) and "hide" or "show")
            end)
        end
        root:CreateDivider()
        root:CreateButton("Reset Window Size", function() AetherHub_ResetSize() end)
        root:CreateButton("Hide This Button", function()
            hubDB.minimapHidden = true
            UpdateMinimapButton()
            print(PREFIX .. "minimap button hidden. Turn it back on at the bottom of AetherHub (/hub).")
        end)
    end)
end

UpdateMinimapButton = function()
    if not hubDB or not Minimap then return end
    if hubDB.minimapHidden then
        if minimapButton then minimapButton:Hide() end
        return
    end
    if not minimapButton then
        local b = CreateFrame("Button", "AetherHubMinimapButton", Minimap)
        b:SetSize(31, 31)
        b:SetFrameStrata("MEDIUM")
        b:SetFrameLevel((Minimap:GetFrameLevel() or 1) + 8)
        local bg = b:CreateTexture(nil, "BACKGROUND")
        bg:SetSize(22, 22)
        bg:SetPoint("CENTER")
        bg:SetColorTexture(0.05, 0.08, 0.14, 1)
        local icon = b:CreateTexture(nil, "ARTWORK")
        icon:SetSize(19, 19)
        icon:SetPoint("CENTER")
        icon:SetTexture("Interface\\Icons\\Spell_Arcane_Arcane02")
        icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
        if b.CreateMaskTexture then
            for _, tex in ipairs({ bg, icon }) do
                local mask = b:CreateMaskTexture()
                mask:SetTexture("Interface\\CharacterFrame\\TempPortraitAlphaMask", "CLAMPTOBLACKADDITIVE", "CLAMPTOBLACKADDITIVE")
                mask:SetAllPoints(tex)
                tex:AddMaskTexture(mask)
            end
        end
        local ring = b:CreateTexture(nil, "OVERLAY")
        ring:SetSize(53, 53)
        ring:SetPoint("TOPLEFT")
        ring:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
        ring:SetVertexColor(0.45, 0.75, 1)          -- Aether blue instead of Blizzard gold
        b:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")
        b:RegisterForClicks("LeftButtonUp", "RightButtonUp")
        b:RegisterForDrag("LeftButton")
        b:SetScript("OnClick", function(self, button)
            GameTooltip:Hide()
            if button == "RightButton" then ShortcutMenu(self) else AetherHub_Toggle() end
        end)
        b:SetScript("OnDragStart", function(self)
            self:SetScript("OnUpdate", function()
                local mx, my = Minimap:GetCenter()
                local px, py = GetCursorPosition()
                local scale = Minimap:GetEffectiveScale()
                hubDB.minimapAngle = math.deg(math.atan2(py / scale - my, px / scale - mx)) % 360
                PlaceMinimapButton()
            end)
        end)
        b:SetScript("OnDragStop", function(self) self:SetScript("OnUpdate", nil) end)
        b:SetScript("OnEnter", function(self)
            GameTooltip:SetOwner(self, "ANCHOR_LEFT")
            GameTooltip:AddLine("Aether  |cff9d9d9dAetherHub v" .. Version("AetherHub") .. "|r", 0.3, 0.65, 1)
            GameTooltip:AddLine("Left-click: open AetherHub", 1, 1, 1)
            GameTooltip:AddLine("Right-click: shortcuts", 1, 1, 1)
            GameTooltip:AddLine("Drag: move around the minimap", 0.7, 0.7, 0.7)
            GameTooltip:Show()
        end)
        b:SetScript("OnLeave", function() GameTooltip:Hide() end)
        minimapButton = b
    end
    PlaceMinimapButton()
    minimapButton:Show()
end

-- ==========================================
-- PAGES
-- ==========================================

-- General pages first (settings shared across the addons), then one page per
-- addon with what's unique to it.
local GENERAL = { "Character", "Appearance", "Fading", "Layout" }
local ADDONS = { "AetherMeter", "AetherBars", "AetherCoords", "AetherPathfinder", "AetherMarks", "AetherItemID", "AetherLedger", "AetherPack", "AetherChat", "AetherFrames" }
local IS_GENERAL = {}
for _, n in ipairs(GENERAL) do IS_GENERAL[n] = true end
local PAGE_ORDER = {}
for _, n in ipairs(GENERAL) do PAGE_ORDER[#PAGE_ORDER + 1] = n end
for _, n in ipairs(ADDONS) do PAGE_ORDER[#PAGE_ORDER + 1] = n end
local PAGE_TITLE = { Character = "Your character" }

local PAGE_INFO = {
    Character        = "Detected automatically",
    Appearance       = "Aether panels and sizes, for every addon",
    Fading           = "How solid things are in and out of combat",
    Layout           = "Moving, docking and lining things up",
    AetherMeter      = "DPS and HPS meter",
    AetherBars       = "Clean action bars and XP bar",
    AetherCoords     = "Coordinates and waypoints",
    AetherPathfinder = "NPC filters on the world map and minimap",
    AetherMarks      = "Quest and rare mob colors, plus Rare Radar",
    AetherItemID     = "Item details when you hover bag and bank items",
    AetherLedger     = "Where to quest, train and skin, with directions",
    AetherPack       = "Your bags, sorted into sections",
    AetherChat       = "Chat fitted beside your bars",
    AetherFrames     = "Your, your pet's, your target's and party frames",
}

local BUILDERS = {}

BUILDERS.Character = function(p)
    AddNote(p, "", function()
        local me = GetProfile()
        return string.format("%s, level %s %s %s (%s)", me.name or "?", me.level or "?",
            me.raceName or "", me.className or "", me.faction or "?")
    end)
    AddHeader(p, "Professions")
    AddNote(p, "", function()
        local me = GetProfile()
        if #me.professions == 0 then return "None learned yet." end
        local lines = {}
        for _, prof in ipairs(me.professions) do
            local line = string.format("%s  %d / %d", prof.name, prof.rank, prof.max)
            local nextRank = NextRank(prof)
            if nextRank then
                line = line .. "  |cffffd100train " .. nextRank.name .. (((me.level or 0) < nextRank.level)
                    and (" at level " .. nextRank.level) or " now") .. "|r"
            elseif prof.max >= 300 and prof.rank >= 300 then
                line = line .. "  |cff33dd66maxed|r"
            end
            lines[#lines + 1] = line
        end
        return table.concat(lines, "\n")
    end)
    p.y = p.y - 50   -- room for a few more professions
    AddHeader(p, "Aether addon versions")
    AddNote(p, "", function()
        local lines = {}
        for _, name in ipairs(ADDONS) do
            do
                lines[#lines + 1] = name .. "  " .. (IsLoaded(name) and ("|cffffd100v" .. Version(name) .. "|r")
                    or "|cff888888not installed|r")
            end
        end
        table.insert(lines, 1, "AetherHub  |cffffd100v" .. Version("AetherHub") .. "|r")
        return table.concat(lines, "\n")
    end, 12)
    AddNote(p, "Read straight from the game, so it's always up to date and right on every character. "
        .. "AetherLedger uses it for its suggestions (set them on the AetherLedger tab), and "
        .. "AetherPathfinder's class trainers follow your class when set to Auto.")
end

-- ----- Shared pages: one place for what several addons have in common -----
-- Each control runs the same slash commands the addon tabs always used, so
-- the addons don't change and each still works on its own.

local function Missing(page, names)
    AddNote(page, "|cff888888Needs " .. table.concat(names, " or ") .. " (not loaded).|r")
end

BUILDERS.Appearance = function(p)
    AddNote(p, "How the Aether addons look. Each addon's own tab keeps what's unique to it.")
    AddHeader(p, "Aether panels")
    local any = false
    if IsLoaded("AetherBars") then
        any = true
        AddCheck(p, "Behind your action bars",
            function() return (AetherBarsDB or {}).trim ~= false end,
            function(v) Run("AETHERBARS", "trim " .. (v and "on" or "off")) end, nil, nil, nil,
            "A navy panel with a blue frame and gold corners behind each bar (a gold chevron on the main bar), "
            .. "blue button edges and a framed XP bar.")
    end
    if IsLoaded("AetherChat") then
        any = true
        AddCheck(p, "Behind your chat",
            function() return (AetherChatDB or {}).trim ~= false end,
            function(v) Run("AETHERCHAT", "trim " .. (v and "on" or "off")) end, nil, nil, nil,
            "The same panel as your bars. Turns solid while your mouse is over the chat or you're typing.")
    end
    if not any then Missing(p, { "AetherBars", "AetherChat" }) end
    AddNote(p, "AetherMeter, AetherPack, AetherHub and the other Aether windows always use the Aether look. "
        .. "How see-through the panels are is on the Fading page.")

    AddHeader(p, "Sizes")
    any = false
    if IsLoaded("AetherFrames") then
        any = true
        AddSlider(p, "Unit frames (yours, pet, target, party)", 60, 160, 5,
            function() return Pct((AetherFramesDB or {}).scale or 1) end,
            function(v) Run("AETHERFRAMES", "scale " .. (v / 100)) end, "%",
            "Makes all of AetherFrames' frames bigger or smaller.")
    end
    if IsLoaded("AetherPack") then
        any = true
        AddSlider(p, "Bag window", 60, 150, 5,
            function() return Pct((AetherPackDB or {}).scale or 1) end,
            function(v) Run("AETHERPACK", "scale " .. (v / 100)) end, "%",
            "Makes AetherPack's whole window bigger or smaller.")
    end
    if IsLoaded("AetherChat") then
        any = true
        AddSlider(p, "Chat text", 8, 20, 1,
            function() return (AetherChatDB or {}).fontSize or 13 end,
            function(v) Run("AETHERCHAT", "font " .. v) end, "",
            "Size of the chat text in every chat tab.")
    end
    if not any then Missing(p, { "AetherFrames", "AetherPack", "AetherChat" }) end
end

BUILDERS.Fading = function(p)
    AddNote(p, "How solid things are in and out of combat. Everything turns solid under your mouse.")
    local any = false
    if IsLoaded("AetherMeter") then
        any = true
        AddHeader(p, "Aether panels")
        AddNote(p, "The meter, the panels behind your bars and chat, and the directions window.")
        AddSlider(p, "In combat", 10, 100, 5,
            function() return Pct((AetherMeterDB or {}).opacityInCombat or 0.8) end,
            function(v) Run("AETHERMETER", "opacity in " .. v) end, "%",
            "How solid the panels are during a fight.")
        AddSlider(p, "Out of combat", 0, 100, 5,
            function() return Pct((AetherMeterDB or {}).opacityOutCombat or 0.3) end,
            function(v) Run("AETHERMETER", "opacity out " .. v) end, "%",
            "How solid the panels are outside fights. Clicking the meter makes it solid for a few seconds.")
    end
    if IsLoaded("AetherBars") then
        any = true
        local function db() return AetherBarsDB or {} end
        AddHeader(p, "Action bars")
        AddSlider(p, "When idle", 0, 100, 5,
            function() return Pct(db().alpha or 1) end,
            function(v) Run("AETHERBARS", "alpha " .. (v / 100)) end, "%",
            "How solid your action bars are when you're not fighting or pointing at them. 100% means they never dim.")
        AddCheck(p, "Solid in combat",
            function() return db().combat end,
            function(v) Run("AETHERBARS", "combat " .. (v and "on" or "off")) end, 0, true, nil,
            "Bars are fully visible during fights.")
        AddCheck(p, "Solid under your mouse",
            function() return db().mouseover end,
            function(v) Run("AETHERBARS", "mouseover " .. (v and "on" or "off")) end, 210, nil, nil,
            "A bar turns solid while you point at it.")
    end
    if IsLoaded("AetherFrames") then
        any = true
        local function db() return AetherFramesDB or {} end
        AddHeader(p, "Unit frames")
        AddSlider(p, "Out of combat", 0, 100, 5,
            function() return Pct(db().alpha or 0.5) end,
            function(v) Run("AETHERFRAMES", "alpha " .. (v / 100)) end, "%",
            "How solid the rings, capsules and bars are when you're not fighting. Names, numbers and faces stay solid.")
        AddCheck(p, "Faces fade too",
            function() return db().fadeFaces end,
            function(v) Run("AETHERFRAMES", "faces " .. (v and "on" or "off")) end, nil, nil, nil,
            "Also fade the portraits to the level above.")
    end
    if not any then Missing(p, { "AetherMeter", "AetherBars", "AetherFrames" }) end
end

BUILDERS.Layout = function(p)
    AddHeader(p, "Move things")
    AddNote(p, "Unlock to Move unlocks your unit frames, the meter and the XP bar at once: drag them, then click "
        .. "Lock (or Done on any of them). Action bars move in Blizzard's Edit Mode.")
    AddButtons(p, {
        { "Unlock to Move", function()
            if InCombatLockdown() then print(PREFIX .. "can't move things in combat."); return end
            if IsLoaded("AetherFrames") then Run("AETHERFRAMES", "unlock") end
            if IsLoaded("AetherMeter") then Run("AETHERMETER", "unlock") end
            if IsLoaded("AetherBars") then Run("AETHERBARS", "xp unlock") end
        end, "Unlocks your unit frames (yours, pet, target, party), the meter and the XP bar together." },
        { "Lock", function()
            if IsLoaded("AetherFrames") then Run("AETHERFRAMES", "lock") end
            if IsLoaded("AetherMeter") then Run("AETHERMETER", "lock") end
            if IsLoaded("AetherBars") then Run("AETHERBARS", "xp lock") end
        end, "Locks them all where they are." },
        { "Open Edit Mode", function()
            if InCombatLockdown() then return end
            if EditModeManagerFrame then pcall(ShowUIPanel, EditModeManagerFrame) end
        end, "Blizzard's Edit Mode, for action bars, the minimap and the rest of Blizzard's UI." },
    })
    if IsLoaded("AetherFrames") then
        AddButtons(p, {
            { "Line Up Frames", function()
                if InCombatLockdown() then print(PREFIX .. "can't move things in combat."); return end
                Run("AETHERFRAMES", "lineup")
            end, "Your frame stays put; the target levels with it, and your pet's and the target of target's "
                .. "line up under them. Frames you parked far away stay there." },
            { "Line Up and Center Frames", function()
                if InCombatLockdown() then print(PREFIX .. "can't move things in combat."); return end
                Run("AETHERFRAMES", "lineup center")
            end, "Lines them up, then slides them into the middle of the screen at the same height." },
        })
    end
    if IsLoaded("AetherBars") or IsLoaded("AetherChat") or IsLoaded("AetherMeter") then
        AddHeader(p, "Around your action bars")
        if IsLoaded("AetherChat") then
            AddCheck(p, "Chat fits the space to the left of your bars",
                function() return (AetherChatDB or {}).fit ~= false end,
                function(v) Run("AETHERCHAT", "fit " .. (v and "on" or "off")) end, nil, nil, nil,
                "Chat fills the space between the left edge of your screen and your bars, as tall as the bars, "
                .. "and follows them when you Align. Off: move chat yourself in Edit Mode.")
        end
        if IsLoaded("AetherMeter") then
            AddCheck(p, "Meter docks to the right of your bars",
                function() return (AetherMeterDB or {}).dock ~= false end,
                function(v) Run("AETHERMETER", "dock " .. (v and "on" or "off")) end, nil, nil, nil,
                "The meter fills the space between your bars and the right edge of the screen, as tall as the bars. "
                .. "Needs AetherBars with its Aether panels. Off: place it yourself.")
        end
        if IsLoaded("AetherBars") then
            AddCheck(p, "Center the bars on screen when aligning",
                function() return (AetherBarsDB or {}).alignCenter ~= false end,
                function(v) Run("AETHERBARS", "align center " .. (v and "on" or "off")) end, nil, nil, nil,
                "Align also slides the whole layout sideways so it sits in the middle of the screen, keeping its shape.")
            AddButtons(p, {
                { "Align Bars...", function()
                    Confirm("Line up your action bars, bag bar and micro menu around Action Bar 1?", function()
                        Run("AETHERBARS", "align")
                    end)
                end, "Drag your bars roughly into place in Edit Mode first. Action Bar 1 stays put; the rest snap "
                    .. "into neat rows with even gaps and room for the trim. Asks first; Undo puts them back." },
                { "Undo Last Align", function() Run("AETHERBARS", "align undo") end,
                  "Puts your bars back exactly where they were before the last Align." },
            })
        end
        if IsLoaded("AetherChat") then
            AddButtons(p, {
                { "Fit Chat Now", function() Run("AETHERCHAT", "now") end, "Fits the chat beside your bars right away." },
            })
        end
    end
    AddHeader(p, "Start over")
    AddButtons(p, {
        { "Reset All Positions...", function()
            Confirm("Put your unit frames, meter, bag window, coordinates and XP bar back in their starting spots?", function()
                if IsLoaded("AetherFrames") then Run("AETHERFRAMES", "reset"); NeedReload() end
                if IsLoaded("AetherMeter") then Run("AETHERMETER", "reset") end
                if IsLoaded("AetherPack") then Run("AETHERPACK", "reset") end
                if IsLoaded("AetherCoords") then Run("AETHERCOORDS", "reset") end
                if IsLoaded("AetherBars") then Run("AETHERBARS", "xp reset") end
            end)
        end, "Every Aether window and frame back to its starting spot (asks first; unit frames need a reload). "
            .. "Your action bars stay where they are." },
    })
end

BUILDERS.AetherMeter = function(p)
    local function db() return AetherMeterDB or {} end
    AddHeader(p, "Window")
    AddCheck(p, "Show the meter",
        function() return AetherMeterFrame and AetherMeterFrame:IsShown() end,
        function(v) Run("AETHERMETER", v and "show" or "hide") end,
        nil, nil, nil, "Shows or hides the damage and healing meter.")
    AddCheck(p, "Lock window position (no moving or resizing)",
        function() return db().locked end,
        function(v) Run("AETHERMETER", v and "lock" or "unlock") end,
        nil, nil, nil, "When unlocked, drag a meter window to move it and drag its corner to resize it.")
    local SHOW = { both = "DPS and HPS", dps = "DPS only", hps = "HPS only" }
    AddDropdown(p, "Show",
        function() return { { "both", SHOW.both }, { "dps", SHOW.dps }, { "hps", SHOW.hps } } end,
        function() return db().metrics or "both" end,
        function(v) Run("AETHERMETER", "show " .. v) end,
        function() return SHOW[db().metrics or "both"] end,
        "Show both damage (DPS) and healing (HPS), or just one of them.")
    AddCheck(p, "Split DPS and HPS into two windows",
        function() return db().split end,
        function(v) Run("AETHERMETER", v and "split" or "join") end,
        nil, nil, function() return (db().metrics or "both") == "both" end,
        "Two separate windows you can place apart. Only when showing both.")
    AddLinks(p, { "Fading", "Layout" }, "Opacity and docking:")
    AddButtons(p, {
        { "Preview Meter", function() Run("AETHERMETER", "test") end, "Fills the meter with sample numbers so you can see how it looks." },
        { "Reset Meter Position", function() Run("AETHERMETER", "reset") end, "Moves the meter back to its starting spot (works while locked)." },
    })
end

BUILDERS.AetherBars = function(p)
    local function db() return AetherBarsDB or {} end
    AddLinks(p, { "Appearance", "Fading", "Layout" }, "Panels, fading and Align:")
    AddHeader(p, "Look")
    AddSlider(p, "Icon edge darkness", 0, 100, 5,
        function() return Pct(db().edgeAlpha or 0.85) end,
        function(v) Run("AETHERBARS", "edge " .. (v / 100)) end, "%",
        "How dark the thin frame around each button icon is.")
    AddCheck(p, "Cooldown glow: orange after use, turning green when ready",
        function() return db().readyGlow ~= false end,
        function(v) Run("AETHERBARS", "glow " .. (v and "on" or "off")) end,
        nil, nil, nil, "A button glows red right after you use it and fades to green as it comes off cooldown.")
    AddCheck(p, "Show macro names on buttons",
        function() return not db().hideMacro end,
        function(v) Run("AETHERBARS", "macro " .. (v and "on" or "off")) end,
        nil, nil, nil, "The small name text on macro buttons.")
    AddCheck(p, "Hide the default bar art",
        function() return db().hideArt end,
        function(v)
            Run("AETHERBARS", "art " .. (v and "off" or "on"))
            if not v then NeedReload() end
        end,
        nil, nil, nil, "Removes the gryphons, the dark background behind the main bar, and the page up/down arrows beside Action Bar 1 (your paging keybinds still work). Showing it again needs a reload.")
    AddHeader(p, "Sizes and XP bar")
    AddChoice(p, "Match button size to Action Bar 1",
        { { "bar2", "Bar 2" }, { "all", "All Bars" }, { "off", "Off" } },
        function() return db().size or "bar2" end,
        function(v) Run("AETHERBARS", "size " .. v) end,
        "Makes other bars' buttons the same size as your main bar's. The bag bar and micro menu match its height too (any setting but Off).")
    AddButtons(p, {
        { "Reset XP Bar Position", function() Run("AETHERBARS", "xp reset") end,
          "Puts the XP bar back in its starting spot (to move it, use Unlock to Move on the Layout page)." },
        { "Restore Defaults...", function()
            Confirm("Restore AetherBars to its default settings?", function()
                Run("AETHERBARS", "reset")
            end)
        end, "Every AetherBars setting back to how it started (asks first)." },
    })
end

BUILDERS.AetherCoords = function(p)
    local function db() return AetherCoordsDB or {} end
    AddHeader(p, "Coordinates")
    AddCheck(p, "Show your coordinates under the minimap",
        function() return db().minimap end,
        function(v) Run("AETHERCOORDS", "minimap " .. (v and "on" or "off")) end,
        nil, nil, nil, "Your position, always on screen. Shift-drag it to move it anywhere.")
    AddCheck(p, "Show cursor coordinates on the world map",
        function() return db().popup end,
        function(v) Run("AETHERCOORDS", "popup " .. (v and "on" or "off")) end,
        nil, nil, nil, "The map spot under your mouse, shown on the world map.")
    AddChoice(p, "Decimal places",
        { { 0, "45, 68" }, { 1, "45.2, 68.1" }, { 2, "45.23, 68.10" } },
        function() return db().decimals or 1 end,
        function(v) Run("AETHERCOORDS", "decimals " .. v) end,
        "How precise the numbers are.")
    AddButtons(p, {
        { "Reset Coordinates Position", function() Run("AETHERCOORDS", "reset") end,
          "Moves the coordinate readout back to its starting spot." },
    })
    AddHeader(p, "Waypoints")
    AddButtons(p, {
        { "Clear All Waypoints...", function()
            Confirm("Remove all your waypoints?", function() Run("AETHERWAY", "clear") end)
        end, "Removes every waypoint (asks first)." },
    })
    AddNote(p, "Double-click a zone map to add a waypoint, or type /way 26 42 note. "
        .. "Right-click a pin to remove it.")
end

-- Same keys and order as AetherPathfinder's filter menu. The first two follow
-- the class chosen in the class dropdown; AetherPathfinder supplies their labels.
local PFM_CATEGORIES = {
    { "mytrainer", "Class Trainer" }, { "classpet", "Class Pet Trainer" }, { "stable", "Stable Master" },
    { "general", "General Goods" }, { "ammo", "Ammo / Bows / Guns" }, { "food", "Food & Drink" },
    { "inn", "Innkeeper" }, { "flight", "Flight Master" }, { "mail", "Mailbox" }, { "repair", "Repair" },
    { "prof", "Profession Trainer" }, { "class", "Other Class Trainer" }, { "bank", "Banker" },
    { "auction", "Auctioneer" }, { "supplies", "Profession Supplies" },
}

BUILDERS.AetherPathfinder = function(p)
    local function filters()
        local db = AetherPathfinderDB
        if type(db) ~= "table" then return {} end
        db.filters = db.filters or {}
        return db.filters
    end
    local api = AetherPathfinder_API
    AddHeader(p, "Show on the map")
    if api then
        AddDropdown(p, "Class trainers for:",
            function()
                local opts = { { "AUTO", "Auto (your character's class)" } }
                for _, token in ipairs(api.classes) do opts[#opts + 1] = { token, api.ClassName(token) } end
                return opts
            end,
            function() return api.GetClassChoice() end,
            function(v) api.SetClassChoice(v) end,
            function()
                local choice = api.GetClassChoice()
                if choice == "AUTO" then return "Auto (" .. api.ClassName(api.SelectedClass()) .. ")" end
                return api.ClassName(choice)
            end,
            "Which class's trainers count as \"Class Trainer\". Auto follows your character.")
    end
    local items = {}
    for _, cat in ipairs(PFM_CATEGORIES) do
        local key = cat[1]
        items[#items + 1] = {
            label = (api and (key == "mytrainer" or key == "classpet"))
                and function() return api.LabelFor(key) end or cat[2],
            enabled = (api and key == "classpet") and function() return api.HasClassPet() end or nil,
            get = function() return filters()[key] end,
            set = function(v) filters()[key] = v; if api then api.Refresh() end end,
            tip = "Show " .. cat[2]:lower() .. " markers on the world map and minimap.",
        }
    end
    AddCheckGrid(p, items)
    local function setAll(v)
        for _, cat in ipairs(PFM_CATEGORIES) do filters()[cat[1]] = v end
        if api then api.Refresh() end
    end
    AddButtons(p, {
        { "Show All NPC Types", function() setAll(true) end, "Tick every kind of NPC." },
        { "Hide All NPC Types", function() setAll(false) end, "Untick every kind of NPC." },
    })
    local function opt(key) return type(AetherPathfinderDB) == "table" and AetherPathfinderDB[key] end
    local function setOpt(key) return function(v)
        if type(AetherPathfinderDB) == "table" then AetherPathfinderDB[key] = v end
        if api then api.Refresh() end
    end end
    AddHeader(p, "Options")
    AddCheck(p, "Built-in NPC locations", function() return opt("useSeed") end,
        setOpt("useSeed"), 0, true, nil, "About 1,550 NPCs from QuestieDB, so markers show before you've met them.")
    AddCheck(p, "Other faction's NPCs", function() return opt("otherFaction") end,
        setOpt("otherFaction"), 210, nil, nil, "Also show Alliance NPCs (or Horde, if you're Alliance).")
    AddCheck(p, "Show on the minimap", function() return opt("minimap") end,
        setOpt("minimap"), 0, nil, nil, "Markers for nearby NPCs on your minimap too.")
    AddHeader(p, "Learned NPCs")
    AddNote(p, "", function()
        local total, maps = 0, 0
        local db = AetherPathfinderDB
        if type(db) == "table" and type(db.npcs) == "table" then
            for _, list in pairs(db.npcs) do
                maps = maps + 1
                for _ in pairs(list) do total = total + 1 end
            end
        end
        return total .. " NPCs learned across " .. maps .. " maps (every NPC you talk to is added)."
    end)
    AddButtons(p, {
        { "Clear NPCs in This Zone...", function()
            Confirm("Forget every NPC AetherPathfinder learned in this zone?", function()
                Run("AETHERPATHFINDER", "clearzone")
            end)
        end, "Forgets the NPCs it learned in the zone you're in (asks first)." },
        { "Clear All Learned NPCs...", function()
            Confirm("Forget every NPC AetherPathfinder has learned?", function()
                Run("AETHERPATHFINDER", "reset")
            end)
        end, "Forgets every learned NPC; built-in ones stay (asks first)." },
    })
end

BUILDERS.AetherMarks = function(p)
    local function db() return AetherMarksDB or {} end
    -- AetherMarks' commands flip a setting, so only send one when it needs to change.
    local function setter(key, command)
        return function(v)
            if (db()[key] and true or false) ~= v then Run("AETHERMARKS", command) end
        end
    end
    AddHeader(p, "Name colors")
    AddCheck(p, "|cff8acff0Baby blue|r name on quest mobs, |cffa335eepurple|r on named ones",
        function() return db().quest end, setter("quest", "quest"), nil, nil, nil,
        "Mobs you still need for a quest. Named quest mobs (\"Hogger slain: 0/1\") are purple.")
    AddCheck(p, "|cffff8000Orange|r name on rare mobs",
        function() return db().rare end, setter("rare", "rare"), nil, nil, nil,
        "Rare mobs, on your target, focus and tooltip, and with Rare Radar over their heads.")
    AddCheck(p, "Sound, screen-edge pulse and alert when a rare appears",
        function() return db().rareSound end, setter("rareSound", "sound"), nil, nil, nil,
        "Once per rare per session.")
    AddHeader(p, "Rare Radar")
    AddCheck(p, "Rare Radar: spot rares by their nameplates",
        function() return db().radar end, setter("radar", "radar"), nil, nil, nil,
        "Needs enemy nameplates on (V). Rares get a glowing beacon over their heads, other mobs show "
        .. "just their name, and your target gets slim health and cast bars. Not in dungeons.")
    AddSlider(p, "Names of ordinary mobs", 0, 100, 10,
        function() return Pct(db().others or 1) end,
        function(v) Run("AETHERMARKS", "names " .. v) end, "%",
        "How visible ordinary mobs' names are with Rare Radar. 0 hides them.")
end

BUILDERS.AetherItemID = function(p)
    local function db() return AetherItemIDDB or {} end
    AddCheck(p, "Show the item window when hovering bag and bank items",
        function() return db().enabled ~= false end,
        function(v) Run("AETHERITEMID", v and "on" or "off") end, nil, nil, nil,
        "Quests that need the item (or \"safe to discard\"), professions that use it, soulbound, "
        .. "how many you have and its vendor price.")
    AddSlider(p, "Hover time before it opens", 0.25, 3, 0.25,
        function() return db().delay or 1 end,
        function(v) Run("AETHERITEMID", "delay " .. v) end, "s",
        "How long to hover an item before its window opens.")
    AddButtons(p, {
        { "Restore Defaults...", function()
            Confirm("Restore AetherItemID's settings to their defaults? (Learned recipes are kept.)", function() Run("AETHERITEMID", "reset") end)
        end, "Settings back to how they started; learned recipes are kept (asks first)." },
        { "Clear Learned Recipes...", function()
            Confirm("Forget the recipes AetherItemID learned from your profession windows?", function() Run("AETHERITEMID", "reset recipes") end)
        end, "Forgets learned recipes; open your profession windows to learn them again (asks first)." },
    })
    AddNote(p, "Open each of your profession windows once so it learns your recipes.")
end

local LEDGER_TIPS = {
    rankUps = "When a profession is near its cap, says which rank to train and where.",
    profQuests = "Quests for your professions, listed on their own.",
    classQuests = "Quests for your class, listed on their own.",
    skinning = "Zones with beasts that give skinning skill-ups at your skill.",
    manageTracker = "The objectives list on your screen follows your zone, lowest level first, and leaves out red quests.",
}

BUILDERS.AetherLedger = function(p)
    local function api() return AetherLedger_API or {} end
    AddHeader(p, "What AetherLedger does for you")
    AddCheck(p, "Suggest a better zone when one has more quests for your level",
        function() return api().Suggesting and api().Suggesting() end,
        function(v) Run("AETHERLEDGER", v and "suggest on" or "suggest off") end, nil, nil, nil,
        "A small window offers your best zones, each with a Go button for directions.")
    for _, interest in ipairs(INTERESTS) do
        AddCheck(p, interest.label,
            function() return AetherHub_Profile.Interest(interest.key) end,
            function(v)
                AetherHub_Profile.SetInterest(interest.key, v)
                if AetherLedger_API and AetherLedger_API.Refresh then AetherLedger_API.Refresh() end
                if v and interest.key == "manageTracker" and AetherLedger_API and AetherLedger_API.SortTracker then
                    AetherLedger_API.SortTracker()
                end
            end, nil, nil, nil, LEDGER_TIPS[interest.key])
    end
    AddButtons(p, {
        { "Check Zones Now", function() if api().Check then api().Check() end end,
          "Checks right away and shows the suggestion window." },
        { "Save Quest Log to File", function() Run("AETHERLEDGER", "export") end,
          "Saves your quest log to a file you can share (written on /reload or log out)." },
        { "Clean Up Quest Log", function() if api().Cleanup then api().Cleanup() end end,
          "Gray quests you could drop, each with an Abandon button." },
    })
    AddNote(p, "", function() return api().Status and api().Status() or "" end, 2)   -- room for two lines

    -- The best three zones: click one to see its quests below, Go for directions.
    AddHeader(p, "Pick a zone")
    local rows = {}
    for i = 1, 3 do
        local pick = AetherButton(p, nil, true)
        pick:SetSize(PAGE_W - 76, 22)
        pick:SetPoint("TOPLEFT", p, "TOPLEFT", 4, p.y)
        local fs = pick:GetFontString()
        if fs then
            fs:ClearAllPoints()
            fs:SetPoint("LEFT", pick, "LEFT", 8, 0)
            fs:SetPoint("RIGHT", pick, "RIGHT", -8, 0)
            fs:SetJustifyH("LEFT")
        end
        Tip(pick, "Show this zone's quests below.")
        local go = AetherButton(p, nil, true)
        go:SetSize(60, 22)
        go:SetPoint("LEFT", pick, "RIGHT", 6, 0)
        go:SetText("Go")
        Tip(go, "Waypoint on its main quest giver, plus step-by-step directions.")
        pick:SetScript("OnClick", function()
            if api().Select then api().Select(i) end
            if p:IsShown() then p:GetScript("OnShow")(p) end
        end)
        go:SetScript("OnClick", function() if api().GoOption then api().GoOption(i) end end)
        rows[i] = { pick = pick, go = go }
        p.y = p.y - 26
    end
    Track(p, { Refresh = function()
        local options = api().Options and api().Options() or {}
        local selected = api().Selected and api().Selected() or 1
        for i, row in ipairs(rows) do
            local o = options[i]
            row.pick:SetShown(o ~= nil)
            row.go:SetShown(o ~= nil and not o.here)
            if o then
                row.pick:SetText(i .. ". " .. o.label .. (o.here and "  (you're here)" or ""))
                SetSelected(row.pick, i == selected)
            end
        end
    end })
    p.y = p.y - 4
    AddNote(p, "", function() return api().HubReport and api().HubReport() or "" end)
end

BUILDERS.AetherPack = function(p)
    local function db() return AetherPackDB or {} end
    AddHeader(p, "Opening")
    AddCheck(p, "Open AetherPack instead of Blizzard's bags (B, bag buttons)",
        function() return db().replace end,
        function(v) Run("AETHERPACK", "replace " .. (v and "on" or "off")) end, nil, nil, nil,
        "When off, B opens Blizzard's bags again and /pack opens AetherPack.")
    AddCheck(p, "Show free bag slots on the backpack button",
        function() return db().backpackCount ~= false end,
        function(v) Run("AETHERPACK", "count " .. (v and "on" or "off")) end, nil, nil, nil,
        "A small number on your backpack button, green, gold when you're getting full, red when nearly full.")
    AddButtons(p, {
        { "Open Bags", function() Run("AETHERPACK", "") end, "Open or close the AetherPack bag window." },
        { "Reset Bag Window Position", function() Run("AETHERPACK", "reset") end, "Puts the bag window back in its starting spot." },
    })
    AddHeader(p, "Look")
    AddSlider(p, "Icons per row", 6, 16, 1,
        function() return db().columns or 10 end,
        function(v) Run("AETHERPACK", "columns " .. v) end, "",
        "How wide the window is.")
    AddLinks(p, { "Appearance" }, "Window size:")
    AddNote(p, "Sections: your class's supplies (Ammo, Soul shards or Class reagents), Quest items, Gear, "
        .. "Consumables, Trade goods, Other, Junk and Free slots. Bars at the bottom show bag space and your "
        .. "ammo, shards or class reagents. "
        .. "Click a section's title to fold it. Drag the window by its edge. At a vendor, Sell junk sells "
        .. "every gray item.")
end

BUILDERS.AetherChat = function(p)
    local function db() return AetherChatDB or {} end
    AddLinks(p, { "Appearance", "Layout" }, "Panel, text size and fitting:")
    AddHeader(p, "Look")
    AddCheck(p, "Hide the voice, channel and emote buttons",
        function() return db().hideButtons ~= false end,
        function(v) Run("AETHERCHAT", "buttons " .. (v and "off" or "on")) end, nil, nil, nil,
        "The small buttons beside the chat. Channels and emotes still work by typing (/join, /dance).")
    AddCheck(p, "Slim typing line that shows only while you type",
        function() return db().slimEdit ~= false end,
        function(v)
            Run("AETHERCHAT", "edit " .. (v and "on" or "off"))
            if not v then NeedReload() end
        end, nil, nil, nil,
        "Press Enter to type: a thin line appears over the bottom of the chat. Off brings Blizzard's box back after a reload.")
    AddButtons(p, {
        { "Restore Defaults...", function()
            Confirm("Restore AetherChat to its default settings?", function()
                Run("AETHERCHAT", "reset"); NeedReload()
            end)
        end, "Every AetherChat setting back to how it started (asks first)." },
    })
    AddNote(p, "Chat itself is still Blizzard's: tabs, channels, colors and filters work as before "
        .. "(right-click a tab for its settings).")
end

BUILDERS.AetherFrames = function(p)
    local function db() return AetherFramesDB or {} end
    AddHeader(p, "Frames")
    AddCheck(p, "Use AetherFrames instead of Blizzard's frames",
        function() return db().enabled ~= false end,
        function(v) Run("AETHERFRAMES", v and "on" or "off"); NeedReload() end, nil, nil, nil,
        "Your frame, your pet's and your target's in the Aether look. Off brings Blizzard's frames back after a reload.")
    AddLinks(p, { "Appearance", "Fading", "Layout" }, "Size, fading and moving:")
    AddCheck(p, "Your target's buffs and debuffs under its frame",
        function() return db().buffs ~= false end,
        function(v) Run("AETHERFRAMES", "buffs " .. (v and "on" or "off")) end, nil, nil, nil,
        "Like Blizzard's target frame: its debuffs (yours included) and buffs, each with its time left underneath.")
    AddCheck(p, "Your own buffs in your frame too",
        function() return db().myBuffs end,
        function(v) Run("AETHERFRAMES", "mybuffs " .. (v and "on" or "off")) end, nil, nil, nil,
        "Off: your buffs stay top right, where Blizzard shows them, and the space under your frame is for your hawk and totem timers.")
    AddCheck(p, "Threat glow around the portraits",
        function() return db().threat ~= false end,
        function(v) Run("AETHERFRAMES", "threat " .. (v and "on" or "off")) end, nil, nil, nil,
        "A blue glow around the portrait. You and your target: slow pulse when you're close to pulling, fast pulse when the next hit may come your way, solid when it's on you. Your pet: a dim steady glow while it holds aggro, a fast pulse when it's losing it.")
    AddCheck(p, "Party frames in the Aether look",
        function() return db().party ~= false end,
        function(v) Run("AETHERFRAMES", "party " .. (v and "on" or "off")); NeedReload() end, nil, nil, nil,
        "Your party in small crests down the left side, with class medallions, debuffs edged in their type's color, "
        .. "and a fade when someone's out of range. Off brings Blizzard's party frames back. Needs a reload.")
    AddCheck(p, "Numbers on your pet's resource bar (handy for warlocks)",
        function() return db().petPower end,
        function(v) Run("AETHERFRAMES", "petpower " .. (v and "on" or "off")); NeedReload() end, nil, nil, nil,
        "Makes the pet's mana, focus or energy bar taller with its number on it. Needs a reload.")
    AddButtons(p, {
        { "Reset Pet Frame Position", function() Run("AETHERFRAMES", "petreset") end, "Puts your pet's frame back under yours, below the buff row." },
    })
    AddNote(p, "Click a frame to target, right-click for its menu, just like Blizzard's. "
        .. "Hunters see their pet's happiness as a face at 3 o'clock on the pet's crest, and its level at 6 o'clock.")
end

SelectPage = function(name)
    if not pages[name] then name = PAGE_ORDER[1] end
    for n, page in pairs(pages) do page:SetShown(n == name) end
    for n, tab in pairs(tabs) do
        tab.selected:SetShown(n == name)
        tab.text:SetTextColor(n == name and 1 or 0.85, n == name and 0.82 or 0.85, n == name and 0 or 0.85)
    end
    if hubDB then hubDB.lastPage = name end
end

-- Pages scroll with the mouse wheel when they're taller than the window;
-- a thin bar on the right shows where you are.

local function UpdateScroll(view)
    local page = view.content
    local h = -page.y
    for _, n in ipairs(page.notes or {}) do h = math.max(h, -n.y + n.fs:GetStringHeight() + 8) end
    page:SetHeight(h + 12)
    local range = math.max(0, page:GetHeight() - view:GetHeight())
    if view:GetVerticalScroll() > range then view:SetVerticalScroll(range) end
    local bar = view.bar
    if range <= 0 then bar:Hide(); return end
    local trackH = view:GetHeight()
    local thumbH = math.max(24, trackH * view:GetHeight() / page:GetHeight())
    bar.thumb:SetHeight(thumbH)
    bar.thumb:ClearAllPoints()
    bar.thumb:SetPoint("TOP", bar, "TOP", 0, -(trackH - thumbH) * view:GetVerticalScroll() / range)
    bar:Show()
end

local function BuildPage(name)
    local view = CreateFrame("ScrollFrame", nil, hub)
    view:SetPoint("TOPLEFT", hub, "TOPLEFT", SIDE_W + 24, -40)
    view:SetPoint("BOTTOMRIGHT", hub, "BOTTOMRIGHT", -26, 44)
    local page = CreateFrame("Frame", nil, view)
    page:SetSize(PAGE_W, 10)
    view:SetScrollChild(page)
    view.content = page
    page.controls, page.y = {}, 0

    view.bar = CreateFrame("Frame", nil, hub)
    view.bar:SetPoint("TOPLEFT", view, "TOPRIGHT", 8, 0)
    view.bar:SetPoint("BOTTOMLEFT", view, "BOTTOMRIGHT", 8, 0)
    view.bar:SetWidth(4)
    local barBg = view.bar:CreateTexture(nil, "BACKGROUND")
    barBg:SetAllPoints()
    barBg:SetColorTexture(0.12, 0.28, 0.5, 0.6)
    view.bar.thumb = view.bar:CreateTexture(nil, "ARTWORK")
    view.bar.thumb:SetWidth(4)
    view.bar.thumb:SetColorTexture(1, 0.82, 0, 0.9)
    view:EnableMouseWheel(true)
    view:SetScript("OnMouseWheel", function(self, delta)
        local range = math.max(0, page:GetHeight() - self:GetHeight())
        self:SetVerticalScroll(math.max(0, math.min(range, self:GetVerticalScroll() - delta * 40)))
        UpdateScroll(self)
    end)
    view:SetScript("OnHide", function(self) self.bar:Hide() end)

    local title = page:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOPLEFT", page, "TOPLEFT", 0, 0)
    title:SetText(name)
    local sub = page:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    sub:SetPoint("LEFT", title, "RIGHT", 8, -1)
    sub:SetTextColor(0.6, 0.6, 0.6)
    if IS_GENERAL[name] then
        title:SetText(PAGE_TITLE[name] or name)
        sub:SetText(PAGE_INFO[name])
    else
        sub:SetText("v" .. Version(name) .. "  -  " .. PAGE_INFO[name])
    end
    page.y = -30

    if IS_GENERAL[name] or IsLoaded(name) then
        BUILDERS[name](page)
    else
        AddNote(page, "|cffff6666" .. name .. " isn't installed or is turned off.|r "
            .. "Turn it on from the AddOns button on the character select screen.")
    end

    page:SetScript("OnShow", function(self)
        for _, c in ipairs(self.controls) do c:Refresh() end
        UpdateScroll(view)
    end)
    view:Hide()
    pages[name] = view
end

local function BuildWindow()
    hub = CreateFrame("Frame", "AetherHubFrame", UIParent, "BackdropTemplate")
    -- Resizable: today's size is the smallest, the screen the largest. Saved.
    local function MaxW() return math.max(WIN_W, math.floor(UIParent:GetWidth() - 20)) end
    local function MaxH() return math.max(WIN_H, math.floor(UIParent:GetHeight() - 20)) end
    local saved = hubDB and hubDB.size
    local w = saved and tonumber(saved[1]) or WIN_W
    local h = saved and tonumber(saved[2]) or WIN_H
    w = math.max(WIN_W, math.min(MaxW(), w))
    h = math.max(WIN_H, math.min(MaxH(), h))
    PAGE_W = w - SIDE_W - 24 - 30
    hub:SetSize(w, h)
    hub:SetResizable(true)
    if hub.SetResizeBounds then hub:SetResizeBounds(WIN_W, WIN_H, MaxW(), MaxH())
    elseif hub.SetMinResize then hub:SetMinResize(WIN_W, WIN_H); hub:SetMaxResize(MaxW(), MaxH()) end
    hub:SetPoint("CENTER")
    hub:SetFrameStrata("DIALOG")
    hub:SetMovable(true)
    hub:SetClampedToScreen(true)
    hub:EnableMouse(true)
    hub:RegisterForDrag("LeftButton")
    hub:SetScript("OnDragStart", hub.StartMoving)
    hub:SetScript("OnDragStop", hub.StopMovingOrSizing)
    Backdrop(hub)
    AetherDecorate(hub, 30)
    tinsert(UISpecialFrames, "AetherHubFrame")   -- Esc closes it

    local title = hub:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    title:SetPoint("TOPLEFT", hub, "TOPLEFT", 14, -12)
    title:SetText("|cff4da6ffAETHER HUB|r  |cff9d9d9dv" .. Version("AetherHub") .. "|r")

    AetherClose(hub)

    -- Sidebar
    local side = CreateFrame("Frame", nil, hub, "BackdropTemplate")
    side:SetPoint("TOPLEFT", hub, "TOPLEFT", 10, -34)
    side:SetPoint("BOTTOMLEFT", hub, "BOTTOMLEFT", 10, 40)
    side:SetWidth(SIDE_W)
    Backdrop(side, 0.6)

    -- Two sections: General (shared settings) and Addons (one tab each).
    -- One line per tab, with the version on the right.
    local prev
    local function Section(text)
        local fs = side:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
        if prev then fs:SetPoint("TOPLEFT", prev, "BOTTOMLEFT", 2, -8)
        else fs:SetPoint("TOPLEFT", side, "TOPLEFT", 10, -9) end
        fs:SetText(text)
        fs:SetTextColor(0.3, 0.65, 1)
        local line = side:CreateTexture(nil, "ARTWORK")
        line:SetColorTexture(0.3, 0.65, 1, 0.35)
        line:SetHeight(1)
        line:SetPoint("LEFT", fs, "RIGHT", 6, 0)
        line:SetPoint("RIGHT", side, "RIGHT", -10, 0)
        return fs
    end
    local header
    for i, name in ipairs(PAGE_ORDER) do
        if i == 1 then header = Section("GENERAL") elseif name == ADDONS[1] then header = Section("ADDONS") end
        local tab = CreateFrame("Button", nil, side)
        tab:SetSize(SIDE_W - 12, 24)
        if header then
            tab:SetPoint("TOPLEFT", header, "BOTTOMLEFT", -4, -3)
            header = nil
        else
            tab:SetPoint("TOP", prev, "BOTTOM", 0, -1)
        end

        tab.selected = tab:CreateTexture(nil, "BACKGROUND")
        tab.selected:SetAllPoints()
        tab.selected:SetColorTexture(0.3, 0.7, 1, 0.25)
        tab.selected:Hide()
        local hl = tab:CreateTexture(nil, "HIGHLIGHT")
        hl:SetAllPoints()
        hl:SetColorTexture(1, 1, 1, 0.08)

        tab.text = tab:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
        tab.text:SetPoint("LEFT", tab, "LEFT", 8, 0)
        tab.text:SetText(PAGE_TITLE[name] or name)
        local status = tab:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
        status:SetPoint("RIGHT", tab, "RIGHT", -6, 0)
        if name == "Character" then
            local me = GetProfile()
            status:SetText(tostring(me.level or ""))
            status:SetTextColor(0.55, 0.55, 0.55)
        elseif IS_GENERAL[name] then
            status:SetText("")
        elseif IsLoaded(name) then
            status:SetText("v" .. Version(name))
            status:SetTextColor(0.55, 0.55, 0.55)
        else
            status:SetText("not loaded")
            status:SetTextColor(1, 0.4, 0.4)
        end

        tab:SetScript("OnClick", function() SelectPage(name) end)
        tabs[name] = tab
        prev = tab
        BuildPage(name)
    end

    -- Footer
    local reload = AetherButton(hub)
    reload:SetSize(100, 22)
    reload:SetPoint("BOTTOMRIGHT", hub, "BOTTOMRIGHT", -24, 12)
    reload:SetText("Reload UI")
    reload:SetScript("OnClick", function() ReloadUI() end)
    Tip(reload, "Reloads the interface. Only a few settings need it; this button turns gold when one does.")
    hub.reload = reload
    if needsReload then NeedReload() end

    -- Minimap button on or off.
    local mm = MakeCheck(hub, "Minimap button")
    mm:SetPoint("RIGHT", reload, "LEFT", -150, 0)
    Tip(mm, "The Aether button on the edge of your minimap: left-click opens this window, right-click for shortcuts, drag to move it.")
    mm:SetScript("OnClick", function(self)
        hubDB.minimapHidden = not self:GetChecked()
        UpdateMinimapButton()
        self:UpdateEdge()
    end)
    mm:SetScript("OnShow", function(self) self:SetChecked(not hubDB.minimapHidden); self:UpdateEdge() end)
    mm:SetChecked(not (hubDB and hubDB.minimapHidden))
    mm:UpdateEdge()

    local footer = hub:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    footer:SetPoint("BOTTOMLEFT", hub, "BOTTOMLEFT", 14, 17)
    footer:SetTextColor(0.6, 0.6, 0.6)
    footer:SetText("Changes apply right away. Hover anything for help.")

    -- Resize grip in the bottom-right corner (the same one AetherMeter uses).
    local grip = CreateFrame("Button", nil, hub)
    grip:SetSize(16, 16)
    grip:SetPoint("BOTTOMRIGHT", hub, "BOTTOMRIGHT", -3, 3)
    grip:SetFrameLevel((hub:GetFrameLevel() or 1) + 10)
    grip:SetNormalTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Up")
    grip:SetHighlightTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Highlight")
    grip:SetPushedTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Down")
    Tip(grip, "Drag to resize the window. Right-click the minimap button and pick Reset Window Size to go back.")
    local sizingFrom
    grip:SetScript("OnMouseDown", function(_, button)
        if button ~= "LeftButton" then return end
        sizingFrom = hub:GetWidth()
        hub:StartSizing("BOTTOMRIGHT")
    end)
    grip:SetScript("OnMouseUp", function()
        hub:StopMovingOrSizing()
        AetherHub_SizeChanged(sizingFrom)
        sizingFrom = nil
    end)
    -- While sizing, keep the scroll bar of the open page right.
    hub:SetScript("OnSizeChanged", function()
        for _, view in pairs(pages) do if view:IsShown() then UpdateScroll(view) end end
    end)

    hub:Hide()
    SelectPage(hubDB and hubDB.lastPage or PAGE_ORDER[1])
end

-- After a resize: save it, and if the window got wider or narrower, rebuild
-- the pages so text wraps to the new width.
function AetherHub_SizeChanged(oldWidth)
    if not hub then return end
    local w, h = math.floor(hub:GetWidth() + 0.5), math.floor(hub:GetHeight() + 0.5)
    if hubDB then hubDB.size = { w, h } end
    if oldWidth and math.abs(oldWidth - w) < 1 then return end
    PAGE_W = w - SIDE_W - 24 - 30
    local current = hubDB and hubDB.lastPage
    for name, view in pairs(pages) do
        view:Hide(); view.bar:Hide()
        pages[name] = nil
    end
    for _, name in ipairs(PAGE_ORDER) do BuildPage(name) end
    SelectPage(current or PAGE_ORDER[1])
end

function AetherHub_ResetSize()
    if hubDB then hubDB.size = nil end
    if not hub then return end
    local old = hub:GetWidth()
    hub:SetSize(WIN_W, WIN_H)
    AetherHub_SizeChanged(old)
    hubDB.size = nil
end

local ToggleWindow
-- For the keybinding, the minimap button and the addon list button.
function AetherHub_Toggle(pageName) ToggleWindow(pageName) end
AetherHub_OnCompartmentClick = function() ToggleWindow() end
BINDING_HEADER_AETHERHUB = "AetherHub"
BINDING_NAME_AETHERHUB_TOGGLE = "Open or close AetherHub"

ToggleWindow = function(pageName)
    if not hub then BuildWindow() end
    if pageName and pages[pageName] then
        SelectPage(pageName)
        hub:Show()
        if hub.Raise then hub:Raise() end
    else
        hub:SetShown(not hub:IsShown())
    end
    -- Re-read current values every time it opens.
    for name, view in pairs(pages) do
        local page = view.content or view
        if view:IsShown() then page:GetScript("OnShow")(page) end
    end
end

-- ==========================================
-- ENTRY IN OPTIONS -> ADDONS
-- ==========================================

local function RegisterOptionsEntry()
    local panel = CreateFrame("Frame")
    panel.name = "AetherHub"
    local t = panel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    t:SetPoint("TOPLEFT", 16, -16)
    t:SetText("AetherHub")
    local d = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    d:SetPoint("TOPLEFT", t, "BOTTOMLEFT", 0, -8)
    d:SetText("All options for the Aether addons, with shared Appearance, Fading and Layout pages.")
    local b = AetherButton(panel)
    b:SetSize(180, 26)
    b:SetPoint("TOPLEFT", d, "BOTTOMLEFT", 0, -14)
    b:SetText("Open AetherHub")
    b:SetScript("OnClick", function()
        if SettingsPanel and SettingsPanel:IsShown() then HideUIPanel(SettingsPanel) end
        if InterfaceOptionsFrame and InterfaceOptionsFrame:IsShown() then HideUIPanel(InterfaceOptionsFrame) end
        ToggleWindow(hubDB and hubDB.lastPage or PAGE_ORDER[1])
    end)

    if Settings and Settings.RegisterCanvasLayoutCategory then
        local category = Settings.RegisterCanvasLayoutCategory(panel, "AetherHub")
        Settings.RegisterAddOnCategory(category)
    elseif InterfaceOptions_AddCategory then
        InterfaceOptions_AddCategory(panel)
    end
end

-- ==========================================
-- EVENTS
-- ==========================================

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("PLAYER_LOGOUT")
pcall(events.RegisterEvent, events, "SKILL_LINES_CHANGED")

events:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" then
        if arg1 == ADDON_NAME then
            LoadHubDB()
        elseif hubDB and BACKUP[arg1] then
            RestoreIfEmpty(arg1)
        end
    elseif event == "PLAYER_LOGIN" then
        RegisterOptionsEntry()
        UpdateMinimapButton()
        if hubDB and hubDB.restored and next(hubDB.restored) then
            local names = {}
            for name in pairs(hubDB.restored) do names[#names + 1] = name end
            table.sort(names)
            print(PREFIX .. "restored saved settings for " .. table.concat(names, ", ") .. ".")
            hubDB.restored = nil
        end
    elseif event == "SKILL_LINES_CHANGED" then
        profDirty = true
    elseif event == "PLAYER_LOGOUT" then
        TakeBackups()
    end
end)

-- ==========================================
-- SLASH COMMANDS
-- ==========================================

local SHORTCUTS = {
    meter = "AetherMeter", am = "AetherMeter",
    bars = "AetherBars", cb = "AetherBars",
    coords = "AetherCoords", mc = "AetherCoords",
    map = "AetherPathfinder", pfm = "AetherPathfinder", pathfinder = "AetherPathfinder",
    marks = "AetherMarks", qm = "AetherMarks",
    itemid = "AetherItemID",
    me = "Character", character = "Character",
    look = "Appearance", appearance = "Appearance",
    fade = "Fading", fading = "Fading",
    layout = "Layout", move = "Layout",
    ledger = "AetherLedger",
    pack = "AetherPack", bags = "AetherPack",
    chat = "AetherChat", achat = "AetherChat",
    frames = "AetherFrames", af = "AetherFrames",
}

SLASH_AETHERHUB1 = "/hub"
SLASH_AETHERHUB2 = "/aetherhub"
SlashCmdList["AETHERHUB"] = function(msg)
    local word = (msg:match("^(%S*)") or ""):lower()
    if word == "version" or word == "versions" then
        print(PREFIX .. "AetherHub v" .. Version("AetherHub"))
        for _, name in ipairs(ADDONS) do
            do
                print("  " .. name .. " " .. (IsLoaded(name) and ("v" .. Version(name)) or "not installed"))
            end
        end
        return
    end
    if word == "resetsize" or word == "size" then
        AetherHub_ResetSize()
        print(PREFIX .. "window size reset.")
        return
    end
    if word == "minimap" then
        hubDB.minimapHidden = not hubDB.minimapHidden
        UpdateMinimapButton()
        print(PREFIX .. "minimap button " .. (hubDB.minimapHidden and "hidden." or "shown."))
        return
    end
    ToggleWindow(SHORTCUTS[word])
end
