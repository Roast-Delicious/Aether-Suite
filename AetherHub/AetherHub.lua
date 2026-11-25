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

-- Soft rounded corners (Release C, user Nov 25 15:36: the button shape of
-- the Hub mockups, everywhere; radius 5, checkboxes 3). Turns a square
-- Aether box (a backdrop edge, and for buttons the plain color textures
-- AetherFill made) into rounded pieces in the same colors: fill, blue edge,
-- and for buttons a rounded hover glow and pressed / disabled shades. Later
-- SetBackdropColor / SetBackdropBorderColor calls paint the rounded pieces.
-- Global, so every Aether addon's buttons use it (they load after AetherHub).
local ROUND_MEDIA = "Interface\\AddOns\\AetherHub\\Media\\"
local ROUND_FLIP = { TOPLEFT = { 0, 1, 0, 1 }, TOPRIGHT = { 1, 0, 0, 1 }, BOTTOMLEFT = { 0, 1, 1, 0 }, BOTTOMRIGHT = { 1, 0, 1, 0 } }
local BTN = { normal = { 0.07, 0.17, 0.32, 0.95 }, pushed = { 0.03, 0.09, 0.19, 0.95 },
              disabled = { 0.13, 0.13, 0.15, 0.9 }, hover = { 0.3, 0.65, 1, 0.3 } }
local function RoundShape(f, layer, sub, R, kind, color)
    local parts = {}
    local W8 = "Interface\\Buttons\\WHITE8X8"
    local function Tex(file)
        local t = f:CreateTexture(nil, layer, nil, sub)
        t:SetTexture(file)
        t:SetVertexColor(color[1], color[2], color[3], color[4] or 1)
        if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false); t:SetTexelSnappingBias(0) end
        parts[#parts + 1] = t
        return t
    end
    for c, fl in pairs(ROUND_FLIP) do
        local t = Tex(ROUND_MEDIA .. "btn_round" .. R .. "_" .. kind)
        t:SetTexCoord(fl[1], fl[2], fl[3], fl[4]); t:SetSize(R, R); t:SetPoint(c, f, c, 0, 0)
    end
    if kind == "line" then
        local t = Tex(W8); t:SetPoint("TOPLEFT", f, "TOPLEFT", R, 0); t:SetPoint("TOPRIGHT", f, "TOPRIGHT", -R, 0); t:SetHeight(1)
        t = Tex(W8); t:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", R, 0); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -R, 0); t:SetHeight(1)
        t = Tex(W8); t:SetPoint("TOPLEFT", f, "TOPLEFT", 0, -R); t:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", 0, R); t:SetWidth(1)
        t = Tex(W8); t:SetPoint("TOPRIGHT", f, "TOPRIGHT", 0, -R); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", 0, R); t:SetWidth(1)
    else
        local t = Tex(W8); t:SetPoint("TOPLEFT", f, "TOPLEFT", R, 0); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -R, 0)
        t = Tex(W8); t:SetPoint("TOPLEFT", f, "TOPLEFT", 0, -R); t:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", 0, R); t:SetWidth(R)
        t = Tex(W8); t:SetPoint("TOPRIGHT", f, "TOPRIGHT", 0, -R); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", 0, R); t:SetWidth(R)
    end
    return parts
end
local function Paint(parts, c)
    if not (c and c[1] and c[2] and c[3]) then return end      -- never paint with an empty color
    for _, t in ipairs(parts) do t:SetVertexColor(c[1], c[2], c[3], c[4] or 1) end
end

function AetherHub_Round(f, R, fill)
    if not f or f.aetherRound or not f.CreateTexture then return end
    f.aetherRound = true
    R = (R == 3) and 3 or 5
    local edge, bg = { 0.3, 0.65, 1, 0.9 }, fill
    if f.GetBackdrop and f:GetBackdrop() then
        local bd = f:GetBackdrop()
        if bd.bgFile and not bg then local r, g, b, a = f:GetBackdropColor(); if r then bg = { r, g, b, a or 1 } end end
        local r, g, b, a = f:GetBackdropBorderColor(); if r then edge = { r, g, b, a or 1 } end
        f:SetBackdrop(nil)
    end
    local button = f.aetherButton
    if button then bg = bg or BTN.normal end
    local fillParts = bg and RoundShape(f, "BACKGROUND", 1, R, "fill", bg)
    local edgeParts = RoundShape(f, "BORDER", 2, R, "line", edge)
    f.SetBackdropBorderColor = function(_, r, g, b, a) edge = { r, g, b, a or 1 }; Paint(edgeParts, edge) end
    f.GetBackdropBorderColor = function() return edge[1], edge[2], edge[3], edge[4] end
    f.SetBackdropColor = function(_, r, g, b, a)
        -- a button's fill follows its state only: Blizzard's backdrop code can
        -- set it white on a resize (Release C in game: every button was white)
        if button or not r then return end
        bg = { r, g, b, a or 1 }
        if fillParts then Paint(fillParts, bg) else fillParts = RoundShape(f, "BACKGROUND", 1, R, "fill", bg) end
    end
    f.GetBackdropColor = function() if bg then return bg[1], bg[2], bg[3], bg[4] end end
    if not button then return end
    -- the button's own square state textures give way to the rounded pieces
    for _, get in ipairs({ "GetNormalTexture", "GetPushedTexture", "GetDisabledTexture", "GetHighlightTexture" }) do
        local t = f[get] and f[get](f)
        if t and t.SetAlpha then t:SetAlpha(0) end
    end
    local hover = RoundShape(f, "HIGHLIGHT", 0, R, "fill", BTN.hover)
    for _, t in ipairs(hover) do t:SetBlendMode("ADD") end
    local down = false
    local function State()
        local c = (f.IsEnabled and not f:IsEnabled()) and BTN.disabled or (down and BTN.pushed) or BTN.normal
        if fillParts and c then Paint(fillParts, c) end
    end
    f:HookScript("OnMouseDown", function() down = true; State() end)
    f:HookScript("OnMouseUp", function() down = false; State() end)
    f:HookScript("OnShow", State)
    if hooksecurefunc then
        for _, m in ipairs({ "Enable", "Disable", "SetEnabled" }) do
            if f[m] then hooksecurefunc(f, m, State) end
        end
    end
    State()
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
    b.aetherSmall = small
    b.aetherButton = true
    AetherHub_Round(b, 5)
    return b
end

-- Mark a choice button as selected: highlighted, lettering in Aether yellow.
-- Swaps font objects (AetherFontNormal is that gold) instead of SetTextColor,
-- because LockHighlight and mouse-over switch to the highlight font and wipe
-- a plain color change back to white.
local function SetSelected(b, on)
    local font = (on and "AetherFontNormal" or "AetherFontHighlight") .. (b.aetherSmall and "Small" or "")
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
        f.text = f:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
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
    { key = "trackerLook", label = "Give the quest tracker the Aether look" },
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

local WIN_W, WIN_H = 620, 525     -- 525: room for the Debug tab (Nov 25)
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
    local fs = page:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    fs:SetPoint("TOPLEFT", page, "TOPLEFT", 0, page.y)
    fs:SetText(text)
    page.y = page.y - 22
end

local function AddNote(page, text, getText, minLines)
    local fs = page:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")   -- easy-to-read size
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
    cb:SetCheckedTexture(Mark(1, 0.69, 0))
    cb:SetDisabledCheckedTexture(Mark(0.45, 0.45, 0.48))
    function cb:UpdateEdge()
        if not self.SetBackdropBorderColor then return end
        if not self:IsEnabled() then self:SetBackdropBorderColor(0.4, 0.4, 0.42, 0.9)
        elseif self:GetChecked() then self:SetBackdropBorderColor(1, 0.69, 0, 1)
        else self:SetBackdropBorderColor(0.3, 0.65, 1, 0.9) end
    end
    AetherHub_Round(cb, 3, { 0.07, 0.17, 0.32, 0.95 })
    local n = cb.GetNormalTexture and cb:GetNormalTexture(); if n then n:SetAlpha(0) end
    hl:SetAlpha(0)                                     -- a rounded hover glow instead
    for _, t in ipairs(RoundShape(cb, "HIGHLIGHT", 0, 3, "fill", BTN.hover)) do t:SetBlendMode("ADD") end
    cb.label = cb:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
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
    local title = page:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
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
    thumb:SetColorTexture(1, 0.69, 0, 1)
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
    local lo = s:CreateFontString(nil, "OVERLAY", "AetherFontDisableSmall")
    lo:SetPoint("TOPLEFT", s, "BOTTOMLEFT", 0, 1)
    lo:SetText(Fmt(min))
    local hi = s:CreateFontString(nil, "OVERLAY", "AetherFontDisableSmall")
    hi:SetPoint("TOPRIGHT", s, "BOTTOMRIGHT", 0, 1)
    hi:SetText(Fmt(max))

    -- The value: click it to type an exact number, Enter to apply.
    local valueText = CreateFrame("EditBox", nil, s, "BackdropTemplate")
    valueText:SetSize(54, 20)
    valueText:SetPoint("LEFT", s, "RIGHT", 12, 0)
    valueText:SetAutoFocus(false)
    valueText:SetFontObject("AetherFontHighlight")
    valueText:SetJustifyH("CENTER")
    if valueText.SetBackdrop then
        valueText:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        valueText:SetBackdropColor(0.07, 0.17, 0.32, 0.95)
        valueText:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    AetherHub_Round(valueText, 5)
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
    local title = page:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
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
    local title = page:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
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
        -- reset / restore / clear: a faint red edge (Hub naming rules)
        local first = item[1]:match("^(%a+)")
        if (first == "Reset" or first == "Restore" or first == "Clear") and b.SetBackdropBorderColor then
            b:SetBackdropBorderColor(0.85, 0.3, 0.25, 0.9)
        end
        b:SetScript("OnClick", function()
            item[2]()
            if page:IsShown() then page:GetScript("OnShow")(page) end
        end)
        prev = b
    end
    page.y = page.y - 30
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
        if b.SetBackdropBorderColor then b:SetBackdropBorderColor(1, 0.69, 0, 1) end
        b:SetText("|cffffb000Reload UI|r")
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
    -- on AetherSkins' ring, sit on the ring itself; otherwise just outside Blizzard's
    local radius = _G.AetherSkins_RingActive and (Minimap:GetWidth() or 140) / 2 * 1.03
        or (Minimap:GetWidth() or 140) / 2 + 6
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
            print(PREFIX .. "minimap button hidden. Turn it back on in AetherHub, Window Look (/hub skins).")
        end)
    end)
end

-- AetherSkins calls this once its ring is up, so the button moves onto it.
function AetherHub_RefreshMinimapButton()
    if minimapButton and minimapButton:IsShown() then PlaceMinimapButton() end
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
        -- a navy button with a fine Aether-blue rim (as on AetherSkins' minimap)
        local disc = b:CreateTexture(nil, "BACKGROUND", nil, -1)
        disc:SetSize(27, 27)
        disc:SetPoint("CENTER")
        disc:SetTexture("Interface\\AddOns\\AetherHub\\Media\\btn_disc")
        local hl = b:CreateTexture(nil, "HIGHLIGHT")
        hl:SetAllPoints(disc)
        hl:SetTexture("Interface\\AddOns\\AetherHub\\Media\\btn_disc")
        hl:SetBlendMode("ADD"); hl:SetAlpha(0.3)
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
-- PAGES (Release C, Nov 25: eight tabs grouped by what you see)
-- ==========================================
-- Every option of every Aether addon has a control here; the slash commands
-- still work as a backup. Each page is split into bands (navy strip, gold
-- name, the addon it belongs to on the right).

local ADDONS = { "AetherMeter", "AetherBars", "AetherCoords", "AetherPathfinder", "AetherMarks", "AetherItemID", "AetherLedger", "AetherPack", "AetherChat", "AetherFrames", "AetherSkins" }
local PAGES = {
    { key = "Character", title = "Your Character",  side = "Level, professions",        info = "Read from the game, always up to date" },
    { key = "ActionBar", title = "Action Bar Area", side = "Bars, Chat, Meter, XP bar", info = "Your bars, chat, meter and XP bar" },
    { key = "Frames",    title = "Unit Frames",     side = "Frames",                    info = "You, your pet, your target and your party" },
    { key = "Map",       title = "Map & Waypoints", side = "Coords, Pathfinder",        info = "Coordinates, waypoints and NPCs on your maps" },
    { key = "Quests",    title = "Quests & Mobs",   side = "Ledger, Marks",             info = "Where to quest, your tracker, and mob names" },
    { key = "Bags",      title = "Bags & Items",    side = "Pack, ItemID",              info = "Your bags and item details" },
    { key = "Look",      title = "Window Look",     side = "Skins, minimap",            info = "The Aether look for Blizzard's windows and the minimap" },
    { key = "Debug",     title = "Help & Debug",    side = "Versions, reports",         info = "Versions and reports, ready to copy" },
}
local PAGE_ORDER, PAGE_BY_KEY = {}, {}
for _, pg in ipairs(PAGES) do PAGE_ORDER[#PAGE_ORDER + 1] = pg.key; PAGE_BY_KEY[pg.key] = pg end
-- old page names (saved lastPage, other addons' links) -> the new page
local OLD_PAGE = {
    Appearance = "ActionBar", Fading = "ActionBar", Layout = "ActionBar",
    AetherMeter = "ActionBar", AetherBars = "ActionBar", AetherChat = "ActionBar",
    AetherFrames = "Frames", AetherCoords = "Map", AetherPathfinder = "Map",
    AetherLedger = "Quests", AetherMarks = "Quests", AetherPack = "Bags", AetherItemID = "Bags",
    AetherSkins = "Look",
}

local BUILDERS = {}

-- A band: navy strip fading to the right, gold name, a thin gold line under
-- it, and the addon it belongs to on the right in gray.
local function AddBand(page, text, addon)
    if page.y < -34 then page.y = page.y - 6 end
    local band = CreateFrame("Frame", nil, page)
    band:SetPoint("TOPLEFT", page, "TOPLEFT", -4, page.y)
    band:SetPoint("RIGHT", page, "RIGHT", 0, 0)
    band:SetHeight(20)
    local bg = band:CreateTexture(nil, "BACKGROUND")
    bg:SetAllPoints()
    bg:SetColorTexture(1, 1, 1, 1)
    local ok = bg.SetGradient and CreateColor and pcall(bg.SetGradient, bg, "HORIZONTAL",
        CreateColor(0.075, 0.157, 0.29, 0.95), CreateColor(0.075, 0.157, 0.29, 0.15))
    if not ok then bg:SetColorTexture(0.075, 0.157, 0.29, 0.75) end
    local line = band:CreateTexture(nil, "ARTWORK")
    line:SetPoint("BOTTOMLEFT"); line:SetPoint("BOTTOMRIGHT"); line:SetHeight(1)
    line:SetColorTexture(1, 0.69, 0, 0.75)
    local fs = band:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    fs:SetPoint("LEFT", band, "LEFT", 8, 1)
    fs:SetText(text)
    if addon then
        local a = band:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
        a:SetPoint("RIGHT", band, "RIGHT", -6, 1)
        a:SetTextColor(0.6, 0.62, 0.68)
        a:SetText(addon)
    end
    page.y = page.y - 27
end

-- An addon that isn't loaded: a gray line instead of its controls.
local function Need(page, addon)
    if IsLoaded(addon) then return true end
    AddNote(page, "|cff888888" .. addon .. " isn't loaded (turn it on from the AddOns button on the character select screen).|r")
    return false
end

-- A row of short buttons after a label ("Report:  Bars  Chat ...").
local function AddRowButtons(page, label, list, labelW)
    local fs = page:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
    fs:SetPoint("TOPLEFT", page, "TOPLEFT", 4, page.y - 4)
    fs:SetTextColor(0.7, 0.72, 0.78)
    fs:SetText(label)
    local x0 = 4 + (labelW or 90)
    local x, prev = x0, nil
    for _, item in ipairs(list) do
        local b = AetherButton(page)
        b:SetText(item[1])
        local w = math.max(56, b:GetFontString():GetStringWidth() + 22)
        b:SetSize(w, 22)
        if x + w > PAGE_W - 4 then page.y = page.y - 28; x = x0 end
        b:SetPoint("TOPLEFT", page, "TOPLEFT", x, page.y)
        Tip(b, item[3])
        b:SetScript("OnClick", function()
            item[2]()
            if page:IsShown() then page:GetScript("OnShow")(page) end
        end)
        x = x + w + 6
    end
    page.y = page.y - 30
end

-- Restore Defaults... for a page: asks first, runs each addon's own defaults
-- command, then the Reload UI button turns gold.
local function AddDefaults(page, what, run)
    AddButtons(page, {
        { "Restore Defaults...", function()
            Confirm("Put every " .. what .. " setting back to its default? (Positions, waypoints and learned data are kept.)", function()
                run(); NeedReload()
            end)
        end, "Every setting on this page back to how it started (asks first). Positions and learned data are kept." },
    })
    page.danger = page.danger or {}
end

-- Panel opacity lives in AetherHub (AetherPanels) so it works without the meter.
local function Panels()
    hubDB.panels = type(hubDB.panels) == "table" and hubDB.panels or {}
    local p = hubDB.panels
    if p.opacityInCombat == nil then
        local m = type(AetherMeterDB) == "table" and AetherMeterDB or {}
        p.opacityInCombat = m.opacityInCombat or 0.8
        p.opacityOutCombat = m.opacityOutCombat or 0.3
    end
    AetherPanels = p
    return p
end

-- ----- Your Character -----
local DANCE, EMOTES = 69, { 67, 68, 70, 66 }      -- dance; wave, cheer, laugh, bow
local function Dancer(page)
    local stage = CreateFrame("Frame", nil, page, "BackdropTemplate")
    stage:SetPoint("TOPLEFT", page, "TOPLEFT", 4, page.y)
    stage:SetPoint("RIGHT", page, "RIGHT", -4, 0)
    stage:SetHeight(190)
    if stage.SetBackdrop then
        stage:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        stage:SetBackdropColor(0.04, 0.043, 0.055, 1)
        stage:SetBackdropBorderColor(0.18, 0.41, 0.63, 1)
    end
    if AetherHub_Round then AetherHub_Round(stage, 5) end
    local floor = stage:CreateTexture(nil, "ARTWORK")        -- soft blue light on the floor
    floor:SetTexture("Interface\\AddOns\\AetherHub\\Media\\btn_disc")
    floor:SetVertexColor(0.3, 0.65, 1, 0.2)
    floor:SetSize(170, 26)
    floor:SetPoint("BOTTOM", stage, "BOTTOM", 0, 14)
    floor:SetBlendMode("ADD")
    -- a squarish model in the middle of the stage, camera pulled back so the
    -- whole character shows (user 16:09: "zoom out on the character a bit")
    local m = CreateFrame("PlayerModel", nil, stage)
    m:SetSize(230, 182)
    m:SetPoint("BOTTOM", stage, "BOTTOM", 0, 6)
    m:EnableMouse(true)
    local back                                           -- timer back to the dance
    local function Play(anim)
        if not (m.HasAnimation and m.SetAnimation) then return end
        local ok, has = pcall(m.HasAnimation, m, anim)
        if ok and has == false then anim = 0 end          -- no such animation: stand
        pcall(m.SetAnimation, m, anim)
    end
    local function Camera()
        if m.SetPortraitZoom then pcall(m.SetPortraitZoom, m, 0) end
        if m.SetCamDistanceScale then pcall(m.SetCamDistanceScale, m, 1.9) end
        if m.SetPosition then pcall(m.SetPosition, m, 0, 0, 0) end
    end
    local function Refresh()
        if not stage:IsVisible() then return end
        pcall(m.SetUnit, m, "player")
        Camera()
        Play(DANCE)
    end
    -- the model resets its camera when it finishes loading
    pcall(m.SetScript, m, "OnModelLoaded", function() Camera(); Play(DANCE) end)
    -- click: another emote, then back to the dance; drag: turn it around
    local nextEmote, downX, facing = 1, nil, 0
    m:SetScript("OnMouseDown", function(self, button)
        if button ~= "LeftButton" then return end
        downX = GetCursorPosition()
        facing = (self.GetFacing and self:GetFacing()) or 0
        self:SetScript("OnUpdate", function()
            local x = GetCursorPosition()
            if self.SetFacing then self:SetFacing(facing + (x - downX) * 0.012) end
        end)
    end)
    m:SetScript("OnMouseUp", function(self, button)
        self:SetScript("OnUpdate", nil)
        if button ~= "LeftButton" or not downX then return end
        local moved = math.abs(GetCursorPosition() - downX) > 4
        downX = nil
        if moved then return end
        Play(EMOTES[nextEmote]); nextEmote = nextEmote % #EMOTES + 1
        if back then back:Cancel() end
        back = C_Timer.NewTimer(2.6, function() back = nil; Play(DANCE) end)
    end)
    local ev = CreateFrame("Frame", nil, stage)
    ev:RegisterUnitEvent("UNIT_MODEL_CHANGED", "player")
    ev:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")
    ev:SetScript("OnEvent", function() if stage:IsVisible() then Refresh() end end)
    stage:SetScript("OnShow", function() C_Timer.After(0.05, Refresh) end)
    page.y = page.y - 198
    Track(page, { Refresh = function() C_Timer.After(0.05, Refresh) end })
end

BUILDERS.Character = function(p)
    AddNote(p, "", function()
        local me = GetProfile()
        return string.format("%s, level %s %s %s (%s)", me.name or "?", me.level or "?",
            me.raceName or "", me.className or "", me.faction or "?")
    end)
    AddBand(p, "Professions")
    AddNote(p, "", function()
        local me = GetProfile()
        if #me.professions == 0 then return "None learned yet." end
        local lines = {}
        for _, prof in ipairs(me.professions) do
            local line = string.format("%s  %d / %d", prof.name, prof.rank, prof.max)
            local nextRank = NextRank(prof)
            if nextRank then
                line = line .. "  |cffffb000train " .. nextRank.name .. (((me.level or 0) < nextRank.level)
                    and (" at level " .. nextRank.level) or " now") .. "|r"
            elseif prof.max >= 300 and prof.rank >= 300 then
                line = line .. "  |cff22e650maxed|r"
            end
            lines[#lines + 1] = line
        end
        return table.concat(lines, "\n")
    end, 5)
    AddNote(p, "Quests & Mobs uses this for its suggestions; Map & Waypoints' class trainers follow your class.")
    Dancer(p)
end

-- ----- Action Bar Area -----
BUILDERS.ActionBar = function(p)
    AddBand(p, "Panels", "Bars, Chat, Meter")
    if IsLoaded("AetherBars") then
        AddCheck(p, "Aether panel behind your action bars",
            function() return (AetherBarsDB or {}).trim ~= false end,
            function(v) Run("AETHERBARS", "trim " .. (v and "on" or "off")) end, nil, nil, nil,
            "A navy panel with a blue frame and gold corners behind each bar, blue button edges and a framed XP bar.")
    end
    if IsLoaded("AetherChat") then
        AddCheck(p, "Aether panel behind your chat",
            function() return (AetherChatDB or {}).trim ~= false end,
            function(v) Run("AETHERCHAT", "trim " .. (v and "on" or "off")) end, nil, nil, nil,
            "The same panel as your bars. Turns solid while your mouse is over the chat or you're typing.")
    end
    AddSlider(p, "Panels in combat", 10, 100, 5,
        function() return Pct(Panels().opacityInCombat) end,
        function(v)
            Panels().opacityInCombat = v / 100
            if IsLoaded("AetherMeter") then Run("AETHERMETER", "opacity in " .. v) end
        end, "%", "How solid the meter, the panels and the directions window are during a fight.")
    AddSlider(p, "Panels out of combat", 0, 100, 5,
        function() return Pct(Panels().opacityOutCombat) end,
        function(v)
            Panels().opacityOutCombat = v / 100
            if IsLoaded("AetherMeter") then Run("AETHERMETER", "opacity out " .. v) end
        end, "%", "How solid they are outside fights. Everything turns solid under your mouse.")

    AddBand(p, "Action bars", "AetherBars")
    if Need(p, "AetherBars") then
        local function db() return AetherBarsDB or {} end
        AddSlider(p, "Bars when idle", 0, 100, 5,
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
        AddSlider(p, "Icon edge darkness", 0, 100, 5,
            function() return Pct(db().edgeAlpha or 0.85) end,
            function(v) Run("AETHERBARS", "edge " .. (v / 100)) end, "%",
            "How dark the thin frame around each button icon is.")
        AddCheck(p, "Cooldown glow (orange after use, green when ready)",
            function() return db().readyGlow ~= false end,
            function(v) Run("AETHERBARS", "glow " .. (v and "on" or "off")) end, nil, nil, nil,
            "A button glows orange right after you use it and turns green as it comes off cooldown.")
        AddCheck(p, "Macro names on buttons",
            function() return not db().hideMacro end,
            function(v) Run("AETHERBARS", "macro " .. (v and "on" or "off")) end, 0, true, nil,
            "The small name text on macro buttons.")
        AddCheck(p, "Hide Blizzard's bar art",
            function() return db().hideArt end,
            function(v)
                Run("AETHERBARS", "art " .. (v and "off" or "on"))
                if not v then NeedReload() end
            end, 210, nil, nil,
            "Removes the gryphons, the dark background behind the main bar, and the page arrows beside Action Bar 1. Showing it again needs a reload.")
        AddChoice(p, "Match button size to Action Bar 1",
            { { "bar2", "Bar 2" }, { "all", "All Bars" }, { "off", "Off" } },
            function() return db().size or "bar2" end,
            function(v) Run("AETHERBARS", "size " .. v) end,
            "Makes other bars' buttons the same size as your main bar's. The bag bar and micro menu match its height too.")
        AddCheck(p, "Center the bars when aligning",
            function() return db().alignCenter ~= false end,
            function(v) Run("AETHERBARS", "align center " .. (v and "on" or "off")) end, nil, nil, nil,
            "Align also slides the whole layout sideways so it sits in the middle of the screen.")
        AddButtons(p, {
            { "Align Bars...", function()
                Confirm("Line up your action bars, bag bar and micro menu around Action Bar 1?", function()
                    Run("AETHERBARS", "align")
                end)
            end, "Drag your bars roughly into place in Edit Mode first. Action Bar 1 stays put; the rest snap into neat rows. Asks first; Undo puts them back." },
            { "Undo Last Align", function() Run("AETHERBARS", "align undo") end,
              "Puts your bars back exactly where they were before the last Align." },
            { "Open Edit Mode", function()
                if InCombatLockdown() then return end
                if EditModeManagerFrame then pcall(ShowUIPanel, EditModeManagerFrame) end
            end, "Blizzard's Edit Mode, for action bars, the minimap and the rest of Blizzard's UI." },
        })

        AddBand(p, "XP bar", "AetherBars")
        local function xpw()
            local x = db().xp or {}
            local bar = _G.MainStatusTrackingBarContainer
            return x.w or (bar and bar.GetWidth and bar:GetWidth()) or 800
        end
        local function xph()
            local x = db().xp or {}
            local bar = _G.MainStatusTrackingBarContainer
            return x.h or (bar and bar.GetHeight and bar:GetHeight()) or 10
        end
        AddSlider(p, "Width", 200, 2000, 10,
            function() return math.floor(xpw() + 0.5) end,
            function(v) Run("AETHERBARS", "xp width " .. v) end, "",
            "How wide the XP bar is. Unlock to Move at the bottom lets you drag it.")
        AddSlider(p, "Height", 3, 40, 1,
            function() return math.floor(xph() + 0.5) end,
            function(v) Run("AETHERBARS", "xp height " .. v) end, "",
            "How tall the XP bar is.")
    end

    AddBand(p, "Chat", "AetherChat")
    if Need(p, "AetherChat") then
        local function db() return AetherChatDB or {} end
        AddCheck(p, "Chat fits left of your bars",
            function() return db().fit ~= false end,
            function(v) Run("AETHERCHAT", "fit " .. (v and "on" or "off")) end, nil, nil, nil,
            "Chat fills the space between the left edge of your screen and your bars, as tall as the bars. Off: move chat yourself in Edit Mode.")
        AddCheck(p, "Hide the voice, channel and emote buttons",
            function() return db().hideButtons ~= false end,
            function(v) Run("AETHERCHAT", "buttons " .. (v and "off" or "on")) end, nil, nil, nil,
            "The small buttons beside the chat. Channels and emotes still work by typing (/join, /dance).")
        AddCheck(p, "Slim typing line, only while you type",
            function() return db().slimEdit ~= false end,
            function(v)
                Run("AETHERCHAT", "edit " .. (v and "on" or "off"))
                if not v then NeedReload() end
            end, nil, nil, nil,
            "Press Enter to type: a thin line appears over the bottom of the chat. Off brings Blizzard's box back after a reload.")
        AddSlider(p, "Chat text size", 8, 20, 1,
            function() return db().fontSize or 13 end,
            function(v) Run("AETHERCHAT", "font " .. v) end, "",
            "Size of the chat text in every chat tab.")
        AddButtons(p, {
            { "Fit Chat Now", function() Run("AETHERCHAT", "now") end, "Fits the chat beside your bars right away." },
        })
    end

    AddBand(p, "Meter", "AetherMeter")
    if Need(p, "AetherMeter") then
        local function db() return AetherMeterDB or {} end
        AddCheck(p, "Show the meter",
            function() return AetherMeterFrame and AetherMeterFrame:IsShown() end,
            function(v) Run("AETHERMETER", v and "show" or "hide") end, 0, true, nil,
            "Shows or hides the damage and healing meter.")
        AddCheck(p, "Lock the meter",
            function() return db().locked end,
            function(v) Run("AETHERMETER", v and "lock" or "unlock") end, 210, nil, nil,
            "When unlocked, drag a meter window to move it and drag its corner to resize it.")
        AddChoice(p, "Show",
            { { "both", "DPS and HPS" }, { "dps", "DPS only" }, { "hps", "HPS only" } },
            function() return db().metrics or "both" end,
            function(v) Run("AETHERMETER", "show " .. v) end,
            "Show both damage (DPS) and healing (HPS), or just one of them.")
        AddCheck(p, "Split DPS and HPS into two windows",
            function() return db().split end,
            function(v) Run("AETHERMETER", v and "split" or "join") end,
            nil, nil, function() return (db().metrics or "both") == "both" end,
            "Two separate windows you can place apart. Only when showing both.")
        AddCheck(p, "Meter docks right of your bars",
            function() return db().dock ~= false end,
            function(v) Run("AETHERMETER", "dock " .. (v and "on" or "off")) end, nil, nil, nil,
            "The meter fills the space between your bars and the right edge of the screen. Needs the panel behind your bars. Off: place it yourself.")
        AddButtons(p, {
            { "Preview Meter", function() Run("AETHERMETER", "test") end, "Fills the meter with sample numbers so you can see how it looks." },
        })
    end
    AddDefaults(p, "Action Bar Area", function()
        if IsLoaded("AetherBars") then Run("AETHERBARS", "reset") end
        if IsLoaded("AetherChat") then Run("AETHERCHAT", "reset") end
        if IsLoaded("AetherMeter") then Run("AETHERMETER", "defaults") end
        local pn = Panels(); pn.opacityInCombat, pn.opacityOutCombat = 0.8, 0.3
    end)
end

-- ----- Unit Frames -----
BUILDERS.Frames = function(p)
    AddBand(p, "Frames", "AetherFrames")
    if not Need(p, "AetherFrames") then return end
    local function db() return AetherFramesDB or {} end
    local function onoff(key, cmd, reload)
        return function() return db()[key] ~= false end,
               function(v) Run("AETHERFRAMES", cmd .. " " .. (v and "on" or "off")); if reload then NeedReload() end end
    end
    local g, s = function() return db().enabled ~= false end,
                 function(v) Run("AETHERFRAMES", v and "on" or "off"); NeedReload() end
    AddCheck(p, "Aether frames for you, your pet and your target", g, s, nil, nil, nil,
        "Off brings Blizzard's frames back after a reload.")
    g, s = onoff("party", "party", true)
    AddCheck(p, "Aether party frames", g, s, nil, nil, nil,
        "Your party in small crests down the left side, with class medallions and debuffs. Needs a reload.")
    g, s = onoff("tot", "tot", true)
    AddCheck(p, "Target of target under the target frame", g, s, nil, nil, nil,
        "Who your target is targeting, in a small crest under its frame. Needs a reload.")
    AddCheck(p, "Numbers on your pet's resource bar",
        function() return db().petPower end,
        function(v) Run("AETHERFRAMES", "petpower " .. (v and "on" or "off")); NeedReload() end, nil, nil, nil,
        "Makes the pet's mana, focus or energy bar taller with its number on it (handy for warlocks). Needs a reload.")
    AddSlider(p, "Frame size", 60, 160, 5,
        function() return Pct(db().scale or 1) end,
        function(v) Run("AETHERFRAMES", "scale " .. (v / 100)) end, "%",
        "Makes all of AetherFrames' frames bigger or smaller.")
    AddButtons(p, {
        { "Line Up Frames", function()
            if InCombatLockdown() then print(PREFIX .. "can't move things in combat."); return end
            Run("AETHERFRAMES", "lineup")
        end, "Your frame stays put; the target levels with it, and your pet's and the target of target's line up under them." },
        { "Line Up and Center", function()
            if InCombatLockdown() then print(PREFIX .. "can't move things in combat."); return end
            Run("AETHERFRAMES", "lineup center")
        end, "Lines them up, then slides them into the middle of the screen at the same height." },
    })

    AddBand(p, "Portraits")
    AddChoice(p, "Portraits",
        { { true, "3D" }, { false, "Flat" } },
        function() return db().portrait3d ~= false end,
        function(v) Run("AETHERFRAMES", "portraits " .. (v and "3d" or "2d")) end,
        "Live 3D faces on a soft blue glow, or the game's flat portraits.")
    g, s = onoff("threat", "threat")
    AddCheck(p, "Threat glow around portraits", g, s, nil, nil, nil,
        "A blue glow: slow pulse when you're close to pulling, fast when the next hit may come your way, solid when it's on you.")
    g, s = onoff("classGlow", "classglow")
    AddCheck(p, "Class color behind players' portraits", g, s, nil, nil, nil,
        "Players and friendly NPCs (target, target of target, party) get their class color behind the face.")
    g, s = onoff("levelGlow", "levelglow")
    AddCheck(p, "Enemy target's glow in its level color", g, s, nil, nil, nil,
        "An enemy mob as your target: its portrait glow takes its level color at the rim.")
    g, s = onoff("hitGlow", "hits")
    AddCheck(p, "Red flash when hit", g, s, 0, true, nil,
        "A quick red flash around a crest when that unit is hit.")
    AddCheck(p, "Damage numbers",
        function() return db().hitNumbers end,
        function(v) Run("AETHERFRAMES", "hitnumbers " .. (v and "on" or "off")) end, 210, nil, nil,
        "The damage, floating up over the portrait.")

    AddBand(p, "Fading")
    AddSlider(p, "Out of combat", 0, 100, 5,
        function() return Pct(db().alpha or 0.5) end,
        function(v) Run("AETHERFRAMES", "alpha " .. (v / 100)) end, "%",
        "How solid the rings, capsules and bars are when you're not fighting. Names, numbers and faces stay solid.")
    AddCheck(p, "Faces fade too",
        function() return db().fadeFaces end,
        function(v) Run("AETHERFRAMES", "faces " .. (v and "on" or "off")) end, nil, nil, nil,
        "Also fade the portraits to the level above.")
    g, s = onoff("aggroFade", "aggro")
    AddCheck(p, "In combat, only your target and whoever has aggro stay solid", g, s, nil, nil, nil,
        "The rest fade to the level below during fights. Off: every frame goes solid in combat.")
    AddSlider(p, "Everyone else in combat", 0, 100, 5,
        function() return Pct(db().combatAlpha or 0.2) end,
        function(v) Run("AETHERFRAMES", "combatalpha " .. (v / 100)) end, "%",
        "How solid the frames without aggro on your target are during a fight.")

    AddBand(p, "Buffs")
    g, s = onoff("buffs", "buffs")
    AddCheck(p, "Your target's buffs and debuffs under its frame", g, s, nil, nil, nil,
        "Its debuffs (yours included) and buffs, each with its time left underneath.")
    AddCheck(p, "Your own buffs in your frame",
        function() return db().myBuffs end,
        function(v) Run("AETHERFRAMES", "mybuffs " .. (v and "on" or "off")) end, nil, nil, nil,
        "Off: your buffs stay top right, where Blizzard shows them, and the space under your frame is for hawk and totem timers.")
    AddDefaults(p, "Unit Frames", function() Run("AETHERFRAMES", "defaults") end)
    AddNote(p, "Click a frame to target, right-click for its menu. Hunters see their pet's happiness at 3 o'clock on the pet's crest.")
end

-- ----- Map & Waypoints -----
local PFM_CATEGORIES = {
    { "mytrainer", "Class Trainer" }, { "classpet", "Class Pet Trainer" }, { "stable", "Stable Master" },
    { "general", "General Goods" }, { "ammo", "Ammo / Bows / Guns" }, { "food", "Food & Drink" },
    { "inn", "Innkeeper" }, { "flight", "Flight Master" }, { "mail", "Mailbox" }, { "repair", "Repair" },
    { "prof", "Profession Trainer" }, { "class", "Other Class Trainer" }, { "bank", "Banker" },
    { "auction", "Auctioneer" }, { "supplies", "Profession Supplies" },
}

-- Your waypoints, one row each, with a red x to remove one.
local WP_ROWS = 8
local function AddWaypointList(p)
    local box = CreateFrame("Frame", nil, p, "BackdropTemplate")
    box:SetPoint("TOPLEFT", p, "TOPLEFT", 4, p.y)
    box:SetPoint("RIGHT", p, "RIGHT", -4, 0)
    if box.SetBackdrop then
        box:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        box:SetBackdropColor(0.04, 0.043, 0.055, 1)
        box:SetBackdropBorderColor(0.18, 0.41, 0.63, 1)
    end
    if AetherHub_Round then AetherHub_Round(box, 5) end
    local rows = {}
    for i = 1, WP_ROWS do
        local fs = box:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
        fs:SetPoint("TOPLEFT", box, "TOPLEFT", 10, -6 - (i - 1) * 22)
        fs:SetPoint("RIGHT", box, "RIGHT", -34, 0)
        fs:SetJustifyH("LEFT"); fs:SetWordWrap(false)
        local x = AetherButton(box, nil, true)
        x:SetSize(18, 18); x:SetText("x")
        x:SetPoint("TOPRIGHT", box, "TOPRIGHT", -8, -4 - (i - 1) * 22)
        if x.SetBackdropBorderColor then x:SetBackdropBorderColor(0.85, 0.3, 0.25, 0.9) end
        Tip(x, "Remove this waypoint.")
        x:SetScript("OnClick", function()
            Run("AETHERWAY", "remove " .. (x.index or 0))
            if p:IsShown() then p:GetScript("OnShow")(p) end
        end)
        rows[i] = { fs = fs, x = x }
    end
    local more = box:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    more:SetTextColor(0.6, 0.62, 0.68)
    local top = p.y
    -- room for the waypoints you have now (the page is rebuilt when that changes)
    local function Count() return #((type(AetherCoordsDB) == "table" and AetherCoordsDB.waypoints) or {}) end
    local built = math.max(1, math.min(Count(), WP_ROWS))
    p.y = p.y - (built * 22 + 10 + (Count() > WP_ROWS and 16 or 0) + 6)
    local function Zone(mapID)
        local info = mapID and C_Map and C_Map.GetMapInfo and C_Map.GetMapInfo(mapID)
        return info and info.name or "?"
    end
    Track(p, { Refresh = function()
        local list = type(AetherCoordsDB) == "table" and AetherCoordsDB.waypoints or {}
        local dec = (AetherCoordsDB or {}).decimals or 1
        local f = "%." .. dec .. "f, %." .. dec .. "f"
        local n = #list
        for i, r in ipairs(rows) do
            local wp = list[i]
            r.fs:SetShown(wp ~= nil); r.x:SetShown(wp ~= nil); r.x.index = i
            if wp then
                r.fs:SetText(string.format("|cff9aa0aa%d.|r  |cffffffff%s|r  |cffffb000" .. f .. "|r  %s",
                    i, Zone(wp.map), (wp.x or 0) * 100, (wp.y or 0) * 100, wp.note or ""))
            end
        end
        local shown = math.max(1, math.min(n, WP_ROWS))
        if shown ~= built and AetherHub_RebuildPage then C_Timer.After(0, function() AetherHub_RebuildPage("Map") end); return end
        box:SetHeight(shown * 22 + 10 + (n > WP_ROWS and 16 or 0))
        more:ClearAllPoints(); more:SetPoint("BOTTOMLEFT", box, "BOTTOMLEFT", 10, 4)
        more:SetShown(n > WP_ROWS)
        more:SetText(n > WP_ROWS and ("and " .. (n - WP_ROWS) .. " more (/way list)") or "")
        if n == 0 then rows[1].fs:Show(); rows[1].fs:SetText("|cff9aa0aaNo waypoints yet.|r") end
    end })
    return top
end

BUILDERS.Map = function(p)
    AddBand(p, "Coordinates", "AetherCoords")
    if Need(p, "AetherCoords") then
        local function db() return AetherCoordsDB or {} end
        AddCheck(p, "Your coordinates under the minimap",
            function() return db().minimap end,
            function(v) Run("AETHERCOORDS", "minimap " .. (v and "on" or "off")) end,
            nil, nil, nil, "Your position, always on screen. Shift-drag it to move it anywhere.")
        AddCheck(p, "Cursor coordinates on the world map",
            function() return db().popup end,
            function(v) Run("AETHERCOORDS", "popup " .. (v and "on" or "off")) end,
            nil, nil, nil, "The map spot under your mouse, shown on the world map.")
        AddChoice(p, "Decimal places",
            { { 0, "45, 68" }, { 1, "45.2, 68.1" }, { 2, "45.23, 68.10" } },
            function() return db().decimals or 1 end,
            function(v) Run("AETHERCOORDS", "decimals " .. v) end,
            "How precise the numbers are.")

        AddBand(p, "Waypoints", "AetherCoords")
        AddWaypointList(p)
        AddNote(p, "Double-click a zone map to add one, or type /way 26 42 note. Right-click a pin to remove it.")
        AddButtons(p, {
            { "Clear All Waypoints...", function()
                Confirm("Remove all your waypoints?", function() Run("AETHERWAY", "clear") end)
            end, "Removes every waypoint (asks first)." },
        })
    end

    AddBand(p, "NPCs on your maps", "AetherPathfinder")
    if Need(p, "AetherPathfinder") then
        local function filters()
            local db = AetherPathfinderDB
            if type(db) ~= "table" then return {} end
            db.filters = db.filters or {}
            return db.filters
        end
        local api = AetherPathfinder_API
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
        AddCheck(p, "Built-in NPC locations", function() return opt("useSeed") end,
            setOpt("useSeed"), 0, true, nil, "About 1,550 NPCs from QuestieDB, so markers show before you've met them.")
        AddCheck(p, "Other faction's NPCs", function() return opt("otherFaction") end,
            setOpt("otherFaction"), 210, nil, nil, "Also show Alliance NPCs (or Horde, if you're Alliance).")
        AddCheck(p, "Markers on the minimap too", function() return opt("minimap") end,
            setOpt("minimap"), 0, nil, nil, "Markers for nearby NPCs on your minimap too.")

        AddBand(p, "Learned NPCs", "AetherPathfinder")
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
    AddDefaults(p, "Map & Waypoints", function()
        if IsLoaded("AetherCoords") then Run("AETHERCOORDS", "defaults") end
        if IsLoaded("AetherPathfinder") then Run("AETHERPATHFINDER", "defaults") end
    end)
end

-- ----- Quests & Mobs -----
local LEDGER_TIPS = {
    rankUps = "When a profession is near its cap, says which rank to train and where.",
    profQuests = "Quests for your professions, listed on their own.",
    classQuests = "Quests for your class, listed on their own.",
    skinning = "Zones with beasts that give skinning skill-ups at your skill.",
    manageTracker = "The objectives list on your screen follows your zone, lowest level first, and leaves out red quests.",
    trackerLook = "Aether headers, quest icons and colors, and no All Objectives bar. Turning it off takes effect after a reload.",
}
local INTEREST_LABEL = {
    profQuests = "Profession quests", classQuests = "Class quests",
    skinning = "Where to skin for skill-ups", rankUps = "Profession rank reminders",
    manageTracker = "Keep the tracker on your zone, sorted by level",
    trackerLook = "Aether look for the quest tracker",
}
local function InterestCheck(p, key, x, sameRow)
    AddCheck(p, INTEREST_LABEL[key],
        function() return AetherHub_Profile.Interest(key) end,
        function(v)
            AetherHub_Profile.SetInterest(key, v)
            if AetherLedger_API and AetherLedger_API.Refresh then AetherLedger_API.Refresh() end
            if v and key == "manageTracker" and AetherLedger_API and AetherLedger_API.SortTracker then
                AetherLedger_API.SortTracker()
            end
            if v and key == "trackerLook" and AetherLedger_TrackerLook then AetherLedger_TrackerLook.Install() end
        end, x, sameRow, nil, LEDGER_TIPS[key])
end

BUILDERS.Quests = function(p)
    local function api() return AetherLedger_API or {} end
    AddBand(p, "Suggestions", "AetherLedger")
    if Need(p, "AetherLedger") then
        AddCheck(p, "Suggest a better zone when one has more quests for your level",
            function() return api().Suggesting and api().Suggesting() end,
            function(v) Run("AETHERLEDGER", v and "suggest on" or "suggest off") end, nil, nil, nil,
            "A small window offers your best zones, each with a Go button for directions.")
        InterestCheck(p, "profQuests", 0, true); InterestCheck(p, "classQuests", 210)
        InterestCheck(p, "skinning", 0, true); InterestCheck(p, "rankUps", 210)
        AddButtons(p, {
            { "Check Zones Now", function() if api().Check then api().Check() end end,
              "Checks right away and shows the suggestion window." },
        })

        AddBand(p, "Pick a zone", "AetherLedger")
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
        AddNote(p, "", function() return api().Status and api().Status() or "" end, 2)

        AddBand(p, "Quest tracker", "AetherLedger")
        InterestCheck(p, "manageTracker")
        InterestCheck(p, "trackerLook")
        AddCheck(p, "Click a finished quest's icon for directions to turn in",
            function() return (AetherLedgerDB or {}).turnInDirections ~= false end,
            function(v) Run("AETHERLEDGER", "turnin " .. (v and "on" or "off")) end, nil, nil, nil,
            "Click the round icon of a quest that's ready to hand in: a waypoint and directions to the NPC who takes it.")
        AddCheck(p, "Tooltips beside the quest tracker",
            function() return (AetherLedgerDB or {}).tooltipSpot ~= false end,
            function(v)
                if ((AetherLedgerDB or {}).tooltipSpot ~= false) ~= v then Run("AETHERLEDGER", "tooltip") end
            end, nil, nil, nil,
            "Tooltips open just left of the quest tracker instead of in the corner.")
        AddButtons(p, {
            { "Sort Tracker Now", function() Run("AETHERLEDGER", "sort") end, "Re-sorts the quest tracker right away." },
            { "Stop Directions", function() Run("AETHERLEDGER", "stop") end, "Ends the directions you're following." },
        })

        AddBand(p, "Quest log", "AetherLedger")
        AddButtons(p, {
            { "Clean Up Quest Log", function() if api().Cleanup then api().Cleanup() end end,
              "Gray quests you could drop, each with an Abandon button." },
            { "Save Quest Log to File", function() Run("AETHERLEDGER", "export") end,
              "Saves your quest log to a file you can share (written on /reload or log out)." },
        })
    end

    AddBand(p, "Mob names", "AetherMarks")
    if Need(p, "AetherMarks") then
        local function db() return AetherMarksDB or {} end
        local function setter(key, command)
            return function(v) if (db()[key] and true or false) ~= v then Run("AETHERMARKS", command) end end
        end
        AddCheck(p, "Quest mobs: |cff8acff0blue|r name, |cffa335eepurple|r if named",
            function() return db().quest end, setter("quest", "quest"), nil, nil, nil,
            "Mobs you still need for a quest. Named quest mobs (\"Hogger slain: 0/1\") are purple.")
        AddCheck(p, "Rare mobs: |cffff8000orange|r name",
            function() return db().rare end, setter("rare", "rare"), nil, nil, nil,
            "Rare mobs, on your target, focus and tooltip, and with Rare Radar over their heads.")
        AddCheck(p, "Sound, screen-edge pulse and alert when a rare appears",
            function() return db().rareSound end, setter("rareSound", "sound"), nil, nil, nil,
            "Once per rare per session.")
        AddCheck(p, "Rare Radar: spot rares by their nameplates",
            function() return db().radar end, setter("radar", "radar"), nil, nil, nil,
            "Needs enemy nameplates on (V). Rares get a glowing beacon over their heads. Not in dungeons.")
        AddSlider(p, "Names of ordinary mobs with Rare Radar", 0, 100, 10,
            function() return Pct(db().others or 1) end,
            function(v) Run("AETHERMARKS", "names " .. v) end, "%",
            "How visible ordinary mobs' names are with Rare Radar. 0 hides them.")
    end
    AddDefaults(p, "Quests & Mobs", function()
        if IsLoaded("AetherLedger") then Run("AETHERLEDGER", "defaults") end
        if IsLoaded("AetherMarks") then Run("AETHERMARKS", "defaults") end
        wipe(Interests())
    end)
    -- last on the page: it can run long, and nothing sits below it
    if IsLoaded("AetherLedger") then
        AddBand(p, "Zone details", "AetherLedger")
        AddNote(p, "", function() return api().HubReport and api().HubReport() or "" end)
    end
end

-- ----- Bags & Items -----
BUILDERS.Bags = function(p)
    AddBand(p, "Bags", "AetherPack")
    if Need(p, "AetherPack") then
        local function db() return AetherPackDB or {} end
        AddCheck(p, "Open AetherPack instead of Blizzard's bags (B, bag buttons)",
            function() return db().replace end,
            function(v) Run("AETHERPACK", "replace " .. (v and "on" or "off")) end, nil, nil, nil,
            "When off, B opens Blizzard's bags again and /pack opens AetherPack.")
        AddCheck(p, "Free bag slots on the backpack button",
            function() return db().backpackCount ~= false end,
            function(v) Run("AETHERPACK", "count " .. (v and "on" or "off")) end, nil, nil, nil,
            "A small number on your backpack button: green, gold when you're getting full, red when nearly full.")
        AddCheck(p, "\"No swaps. Just drops.\" slot",
            function() return db().deposit ~= false end,
            function(v) Run("AETHERPACK", "deposit " .. (v and "on" or "off")) end, nil, nil, nil,
            "Drop an item on it and it goes into the first free slot.")
        AddChoice(p, "Its number pulses",
            { { "item", "While Holding an Item" }, { "always", "Always" }, { "off", "Never" } },
            function() return db().depositPulse or "item" end,
            function(v) Run("AETHERPACK", "pulse " .. v) end,
            "When the free-slot number on that slot pulses.")
        AddSlider(p, "Icons per row", 6, 16, 1,
            function() return db().columns or 10 end,
            function(v) Run("AETHERPACK", "columns " .. v) end, "",
            "How wide the window is.")
        AddSlider(p, "Bag window size", 60, 150, 5,
            function() return Pct(db().scale or 1) end,
            function(v) Run("AETHERPACK", "scale " .. (v / 100)) end, "%",
            "Makes AetherPack's whole window bigger or smaller.")
        AddButtons(p, {
            { "Open Bags", function() Run("AETHERPACK", "") end, "Open or close the AetherPack bag window." },
        })
    end
    AddBand(p, "Item details", "AetherItemID")
    if Need(p, "AetherItemID") then
        local function db() return AetherItemIDDB or {} end
        AddCheck(p, "Item window when you hover bag and bank items",
            function() return db().enabled ~= false end,
            function(v) Run("AETHERITEMID", v and "on" or "off") end, nil, nil, nil,
            "Quests that need the item (or \"safe to discard\"), professions that use it, soulbound, how many you have and its vendor price.")
        AddSlider(p, "Hover time before it opens", 0.25, 3, 0.25,
            function() return db().delay or 1 end,
            function(v) Run("AETHERITEMID", "delay " .. v) end, "s",
            "How long to hover an item before its window opens.")
        AddNote(p, "Open each of your profession windows once so it learns your recipes.")
        AddButtons(p, {
            { "Clear Learned Recipes...", function()
                Confirm("Forget the recipes AetherItemID learned from your profession windows?", function() Run("AETHERITEMID", "reset recipes") end)
            end, "Forgets learned recipes; open your profession windows to learn them again (asks first)." },
        })
    end
    AddDefaults(p, "Bags & Items", function()
        if IsLoaded("AetherPack") then Run("AETHERPACK", "defaults") end
        if IsLoaded("AetherItemID") then Run("AETHERITEMID", "reset") end
    end)
end

-- ----- Window Look -----
BUILDERS.Look = function(p)
    local function db() return AetherSkinsDB or {} end
    AddBand(p, "Blizzard's windows", "AetherSkins")
    if Need(p, "AetherSkins") then
        AddCheck(p, "Blizzard's windows in the Aether look (needs a reload)",
            function() return db().windows ~= false end,
            function(v) Run("AETHERSKINS", "windows " .. (v and "on" or "off")); NeedReload() end, nil, nil, nil,
            "Character, Reputation, Friends, Talents, the world map and the rest: the Aether frame, navy buttons, gold checks and Aether gold. Needs a reload.")
        AddNote(p, "Drag a window's gold corner grip to resize it; right-click the grip for normal size.")
        AddButtons(p, {
            { "Reset Window Sizes...", function()
                Confirm("Put every window you resized back to its normal size?", function() Run("AETHERSKINS", "sizes") end)
            end, "Every window resized with its corner grip back to normal size (asks first)." },
        })
        AddNote(p, "A window that wasn't restyled: point at it and type /skins this.")
    end
    AddBand(p, "Minimap", "AetherSkins")
    if IsLoaded("AetherSkins") then
        AddCheck(p, "Minimap in the Aether look (needs a reload)",
            function() return db().minimap ~= false end,
            function(v) Run("AETHERSKINS", "minimap " .. (v and "on" or "off")); NeedReload() end, nil, nil, nil,
            "A navy ring with gold chevrons, the sun or moon and the tracking button on the ring, and the zone and clock in a pill underneath. Needs a reload.")
        AddChoice(p, "Sun or moon",
            { { "auto", "Follow the Game" }, { "day", "Day" }, { "night", "Night" } },
            function() return AetherSkins_Light or "auto" end,
            function(v) Run("AETHERSKINS", v) end,
            "The sun or moon on the minimap ring follows the game's clock, or stays on day or night until you change it back.")
    end
    AddCheck(p, "AetherHub button on the minimap",
        function() return not hubDB.minimapHidden end,
        function(v) hubDB.minimapHidden = not v; UpdateMinimapButton() end, nil, nil, nil,
        "The Aether button on the edge of your minimap: left-click opens this window, right-click for shortcuts, drag to move it.")
    AddDefaults(p, "Window Look", function()
        if IsLoaded("AetherSkins") then Run("AETHERSKINS", "defaults") end
        hubDB.minimapHidden = nil; UpdateMinimapButton()
    end)
end

-- ----- Help & Debug -----
-- Every addon's report in one place, with the output in a box you can copy
-- (chat can't be copied), and one button that builds a full report.
local REPORTS = {     -- label, addon, slash key, command, row
    { "Bars",         "AetherBars",       "AETHERBARS",       "debug",   "Report:" },
    { "Chat",         "AetherChat",       "AETHERCHAT",       "debug",   "Report:" },
    { "Marks",        "AetherMarks",      "AETHERMARKS",      "debug",   "Report:" },
    { "Pathfinder",   "AetherPathfinder", "AETHERPATHFINDER", "debug",   "Report:" },
    { "Skins",        "AetherSkins",      "AETHERSKINS",      "debug",   "Report:" },
    { "Ledger",       "AetherLedger",     "AETHERLEDGER",     "status",  "Report:" },
    { "Zones",        "AetherLedger",     "AETHERLEDGER",     "zones",   "Ledger:" },
    { "Tracker",      "AetherLedger",     "AETHERLEDGER",     "tracker", "Ledger:" },
    { "NPC Counts",   "AetherPathfinder", "AETHERPATHFINDER", "stats",   "Pathfinder:" },
    { "Flight Paths", "AetherPathfinder", "AETHERPATHFINDER", "flights", "Pathfinder:" },
}

-- Lines the addons print while we run their command are caught here too.
local capture
if DEFAULT_CHAT_FRAME and hooksecurefunc then
    hooksecurefunc(DEFAULT_CHAT_FRAME, "AddMessage", function(_, text)
        if capture and type(text) == "string" then capture[#capture + 1] = text end
    end)
end
local function Plain(text)            -- color codes and icons out: it's for pasting
    text = tostring(text or "")
    text = text:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", ""):gsub("|T.-|t", ""):gsub("|A.-|a", "")
    text = text:gsub("|H.-|h(.-)|h", "%1")
    return text
end
local function Capture(fn)
    local lines = {}
    capture = lines
    local ok, err = pcall(fn)
    capture = nil
    if not ok then lines[#lines + 1] = "(error: " .. tostring(err) .. ")" end
    for i, t in ipairs(lines) do lines[i] = Plain(t) end
    return lines
end

local function MemoryLines()
    local out, total = {}, 0
    if collectgarbage then collectgarbage("collect") end
    if UpdateAddOnMemoryUsage then pcall(UpdateAddOnMemoryUsage) end
    local list = { "AetherHub" }
    for _, n in ipairs(ADDONS) do list[#list + 1] = n end
    for _, n in ipairs(list) do
        if IsLoaded(n) and GetAddOnMemoryUsage then
            local ok, kb = pcall(GetAddOnMemoryUsage, n)
            if ok and kb then
                total = total + kb
                out[#out + 1] = string.format("%-18s %6d KB", n, math.floor(kb + 0.5))
            end
        end
    end
    out[#out + 1] = string.format("%-18s %6d KB", "Total", math.floor(total + 0.5))
    return out
end

local function VersionLines()
    local out = { "AetherHub " .. Version("AetherHub") }
    for _, n in ipairs(ADDONS) do
        out[#out + 1] = n .. " " .. (IsLoaded(n) and Version(n) or "not loaded")
    end
    return out
end

BUILDERS.Debug = function(p)
    local box   -- the output box, made below
    local function Show(title, lines)
        local text = "== " .. title .. " ==\n" .. table.concat(lines, "\n")
        box:SetText(text)
        box:SetCursorPosition(0)
        box.scroll:SetVerticalScroll(0)
    end
    local function RunOne(d)
        if not IsLoaded(d[2]) then Show(d[1], { d[2] .. " isn't loaded." }); return end
        Show(d[2] .. " " .. d[4], Capture(function() Run(d[3], d[4]) end))
    end

    AddBand(p, "Versions")
    local names = { "AetherHub" }
    for _, n in ipairs(ADDONS) do names[#names + 1] = n end
    local half = math.ceil(#names / 2)
    for i, n in ipairs(names) do
        local col, row = (i <= half) and 0 or 1, (i <= half) and (i - 1) or (i - half - 1)
        local a = p:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
        a:SetPoint("TOPLEFT", p, "TOPLEFT", 6 + col * 210, p.y - row * 18)
        a:SetText(n)
        local v = p:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
        v:SetPoint("TOPRIGHT", p, "TOPLEFT", 6 + col * 210 + 190, p.y - row * 18)
        v:SetText(IsLoaded(n) and ("|cffffb000" .. Version(n) .. "|r") or "|cff888888not loaded|r")
    end
    p.y = p.y - half * 18 - 8

    AddBand(p, "Reports")
    for _, row in ipairs({ "Report:", "Ledger:", "Pathfinder:" }) do
        local list = {}
        for _, d in ipairs(REPORTS) do
            if d[5] == row then
                list[#list + 1] = { d[1], function() RunOne(d) end, "Runs /" .. d[4] .. " for " .. d[2] .. " and shows what it says below." }
            end
        end
        AddRowButtons(p, row, list)
    end
    AddButtons(p, {
        { "Check Memory", function() Show("Memory", MemoryLines()) end,
          "Cleans up first, then shows how much memory each Aether addon really uses." },
        { "Show Window Dump", function()
            local t = AetherSkinsDB and AetherSkinsDB.lastTree
            if t then Show("Window dump: " .. tostring(t.name), t.lines)
            else Show("Window dump", { "Nothing saved yet. Point at a Blizzard window and type /skins tree, then click this again." }) end
        end, "Shows the window structure /skins tree saved (point at a window and type /skins tree first)." },
    })
    if IsLoaded("AetherItemID") then
        AddCheck(p, "ItemID: explain in chat what it finds while you hover",
            function() return AetherItemID_Debugging end,
            function(v) if (AetherItemID_Debugging and true or false) ~= v then Run("AETHERITEMID", "debug") end end, nil, nil, nil,
            "While on, hovering an item prints what AetherItemID detects. Turns off when you reload.")
    end
    AddNote(p, "Window dump: point at a window, type /skins tree, then Show Window Dump.")

    AddBand(p, "Output")
    AddNote(p, "Click in the box, press Ctrl+A, then Ctrl+C to copy.")
    local frame = CreateFrame("Frame", nil, p, "BackdropTemplate")
    frame:SetPoint("TOPLEFT", p, "TOPLEFT", 4, p.y)
    frame:SetPoint("RIGHT", p, "RIGHT", -4, 0)
    frame:SetHeight(190)
    if frame.SetBackdrop then
        frame:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        frame:SetBackdropColor(0.03, 0.045, 0.085, 1)
        frame:SetBackdropBorderColor(0.3, 0.65, 1, 0.8)
    end
    if AetherHub_Round then AetherHub_Round(frame, 5) end
    local scroll = CreateFrame("ScrollFrame", nil, frame)
    scroll:SetPoint("TOPLEFT", 6, -6)
    scroll:SetPoint("BOTTOMRIGHT", -6, 6)
    box = CreateFrame("EditBox", nil, scroll)
    box:SetMultiLine(true)
    box:SetAutoFocus(false)
    box:SetFontObject("AetherFontHighlightSmall")
    box:SetWidth(PAGE_W - 24)
    box:SetText("Pick a report above, or Copy Full Report.")
    box:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    box:SetScript("OnTextChanged", function() scroll:UpdateScrollChildRect() end)
    scroll:SetScrollChild(box)
    scroll:EnableMouseWheel(true)
    scroll:SetScript("OnMouseWheel", function(self, delta)
        local range = self:GetVerticalScrollRange() or 0
        self:SetVerticalScroll(math.max(0, math.min(range, self:GetVerticalScroll() - delta * 30)))
    end)
    frame:EnableMouse(true)
    frame:SetScript("OnMouseDown", function() box:SetFocus() end)
    box.scroll = scroll
    p.debugBox = box
    p.y = p.y - 198

    AddButtons(p, {
        { "Copy Full Report", function()
            local all = {}
            local function Add(title, lines)
                all[#all + 1] = "== " .. title .. " =="
                for _, l in ipairs(lines) do all[#all + 1] = l end
                all[#all + 1] = ""
            end
            local who = (UnitName and UnitName("player") or "?") .. ", level " .. (UnitLevel and UnitLevel("player") or "?")
            Add("Aether report", { (date and date("%Y-%m-%d %H:%M") or "") .. "  " .. who })
            Add("Versions", VersionLines())
            Add("Memory", MemoryLines())
            for _, d in ipairs(REPORTS) do
                if IsLoaded(d[2]) then Add(d[2] .. " " .. d[4], Capture(function() Run(d[3], d[4]) end)) end
            end
            local t = AetherSkinsDB and AetherSkinsDB.lastTree
            if t then Add("Window dump: " .. tostring(t.name), t.lines) end
            box:SetText(table.concat(all, "\n"))
            box:SetCursorPosition(0)
            scroll:SetVerticalScroll(0)
            box:SetFocus()
            box:HighlightText()
        end, "Versions, memory and every report above in one go, selected and ready to copy (Ctrl+C)." },
        { "Clear", function() box:SetText("") end, "Empties the box." },
    })
end

SelectPage = function(name)
    name = OLD_PAGE[name] or name
    if not pages[name] then name = PAGE_ORDER[1] end
    for n, page in pairs(pages) do page:SetShown(n == name) end
    for n, tab in pairs(tabs) do
        tab.selected:SetShown(n == name)
        if tab.notch then tab.notch:SetShown(n == name) end
        tab.text:SetTextColor(n == name and 1 or 0.85, n == name and 0.69 or 0.85, n == name and 0 or 0.85)
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
    view.bar.thumb:SetColorTexture(1, 0.69, 0, 0.9)
    view:EnableMouseWheel(true)
    view:SetScript("OnMouseWheel", function(self, delta)
        local range = math.max(0, page:GetHeight() - self:GetHeight())
        self:SetVerticalScroll(math.max(0, math.min(range, self:GetVerticalScroll() - delta * 40)))
        UpdateScroll(self)
    end)
    view:SetScript("OnHide", function(self) self.bar:Hide() end)

    local info = PAGE_BY_KEY[name]
    local title = page:CreateFontString(nil, "OVERLAY", "AetherFontNormalLarge")
    title:SetPoint("TOPLEFT", page, "TOPLEFT", 0, 0)
    title:SetText(info.title)
    local sub = page:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    sub:SetPoint("LEFT", title, "RIGHT", 8, -1)
    sub:SetTextColor(0.6, 0.6, 0.6)
    sub:SetText(info.info)
    page.y = -30

    local ok, err = pcall(BUILDERS[name], page)
    if not ok then
        AddNote(page, "|cffff6666This page hit an error: " .. tostring(err) .. "|r")
        geterrorhandler()(err)
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

    local title = hub:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    title:SetPoint("TOPLEFT", hub, "TOPLEFT", 14, -12)
    title:SetText("|cff4da6ffAETHER HUB|r  |cff9d9d9dv" .. Version("AetherHub") .. "|r")

    AetherClose(hub)

    -- Sidebar
    local side = CreateFrame("Frame", nil, hub, "BackdropTemplate")
    side:SetPoint("TOPLEFT", hub, "TOPLEFT", 10, -34)
    side:SetPoint("BOTTOMLEFT", hub, "BOTTOMLEFT", 10, 40)
    side:SetWidth(SIDE_W)
    Backdrop(side, 0.6)

    -- Eight tabs, grouped by what you see: the name, and under it the
    -- addons it covers (Release C, layout B).
    local prev
    for _, name in ipairs(PAGE_ORDER) do
        local info = PAGE_BY_KEY[name]
        local tab = CreateFrame("Button", nil, side)
        tab:SetSize(SIDE_W - 12, 36)
        if prev then tab:SetPoint("TOP", prev, "BOTTOM", 0, -3)
        else tab:SetPoint("TOPLEFT", side, "TOPLEFT", 6, -7) end

        tab.selected = tab:CreateTexture(nil, "BACKGROUND")
        tab.selected:SetAllPoints()
        tab.selected:SetColorTexture(0.3, 0.7, 1, 0.25)
        tab.selected:Hide()
        tab.notch = tab:CreateTexture(nil, "ARTWORK")      -- gold notch on the open tab
        tab.notch:SetColorTexture(1, 0.69, 0, 1)
        tab.notch:SetPoint("TOPLEFT", tab, "TOPLEFT", 0, -4)
        tab.notch:SetPoint("BOTTOMLEFT", tab, "BOTTOMLEFT", 0, 4)
        tab.notch:SetWidth(2)
        tab.notch:Hide()
        local hl = tab:CreateTexture(nil, "HIGHLIGHT")
        hl:SetAllPoints()
        hl:SetColorTexture(1, 1, 1, 0.08)

        tab.text = tab:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
        tab.text:SetPoint("TOPLEFT", tab, "TOPLEFT", 10, -4)
        tab.text:SetText(info.title)
        local subline = tab:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
        subline:SetPoint("TOPLEFT", tab.text, "BOTTOMLEFT", 0, -2)
        subline:SetTextColor(0.55, 0.57, 0.63)
        subline:SetText(info.side)

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

    -- Always at hand, on every page: move things, and put them back.
    local unlock = AetherButton(hub)
    unlock:SetText("Unlock to Move")
    unlock:SetSize(112, 22)
    unlock:SetPoint("BOTTOMLEFT", hub, "BOTTOMLEFT", 14, 12)
    Tip(unlock, "Unlocks your unit frames, the meter and the XP bar together: drag them, then click Lock (or Done on any of them). Action bars move in Edit Mode.")
    local locked = true
    unlock:SetScript("OnClick", function(self)
        if InCombatLockdown() then print(PREFIX .. "can't move things in combat."); return end
        local cmd = locked and "unlock" or "lock"
        if IsLoaded("AetherFrames") then Run("AETHERFRAMES", cmd) end
        if IsLoaded("AetherMeter") then Run("AETHERMETER", cmd) end
        if IsLoaded("AetherBars") then Run("AETHERBARS", "xp " .. cmd) end
        locked = not locked
        self:SetText(locked and "Unlock to Move" or "Lock")
        SetSelected(self, not locked)
    end)
    local resetPos = AetherButton(hub)
    resetPos:SetText("Reset Positions...")
    resetPos:SetSize(128, 22)
    resetPos:SetPoint("LEFT", unlock, "RIGHT", 6, 0)
    if resetPos.SetBackdropBorderColor then resetPos:SetBackdropBorderColor(0.85, 0.3, 0.25, 0.9) end
    Tip(resetPos, "Every Aether window and frame back to its starting spot (asks first; unit frames need a reload). Your action bars stay where they are.")
    resetPos:SetScript("OnClick", function()
        Confirm("Put your unit frames, meter, bag window, coordinates, XP bar and directions windows back in their starting spots?", function()
            if IsLoaded("AetherFrames") then Run("AETHERFRAMES", "reset"); NeedReload() end
            if IsLoaded("AetherMeter") then Run("AETHERMETER", "reset") end
            if IsLoaded("AetherPack") then Run("AETHERPACK", "reset") end
            if IsLoaded("AetherCoords") then Run("AETHERCOORDS", "reset") end
            if IsLoaded("AetherBars") then Run("AETHERBARS", "xp reset") end
            if IsLoaded("AetherLedger") then Run("AETHERLEDGER", "resetwindows") end
        end)
    end)

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

function AetherHub_RebuildPage(name)
    local view = pages[name]
    if not view then return end
    local shown = view:IsShown()
    view:Hide(); view.bar:Hide()
    pages[name] = nil
    BuildPage(name)
    if shown then SelectPage(name); local page = pages[name].content; page:GetScript("OnShow")(page) end
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
    pageName = pageName and (OLD_PAGE[pageName] or pageName)
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
    local t = panel:CreateFontString(nil, "OVERLAY", "AetherFontNormalLarge")
    t:SetPoint("TOPLEFT", 16, -16)
    t:SetText("AetherHub")
    local d = panel:CreateFontString(nil, "OVERLAY", "AetherFontHighlight")
    d:SetPoint("TOPLEFT", t, "BOTTOMLEFT", 0, -8)
    d:SetText("All options for the Aether addons, in eight pages grouped by what you see.")
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
            if type(hubDB.panels) == "table" and hubDB.panels.opacityInCombat then AetherPanels = hubDB.panels end
        elseif hubDB and BACKUP[arg1] then
            RestoreIfEmpty(arg1)
        end
    elseif event == "PLAYER_LOGIN" then
        RegisterOptionsEntry()
        Panels()
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
    me = "Character", character = "Character",
    bars = "ActionBar", cb = "ActionBar", chat = "ActionBar", achat = "ActionBar", meter = "ActionBar", am = "ActionBar",
    xp = "ActionBar", look = "ActionBar", fade = "ActionBar", layout = "ActionBar", move = "ActionBar",
    frames = "Frames", af = "Frames",
    map = "Map", coords = "Map", mc = "Map", way = "Map", pfm = "Map", pathfinder = "Map",
    quests = "Quests", ledger = "Quests", marks = "Quests", qm = "Quests",
    bags = "Bags", pack = "Bags", itemid = "Bags", items = "Bags",
    skins = "Look", askins = "Look", windows = "Look", minimapskin = "Look",
    debug = "Debug", report = "Debug", help = "Debug",
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
