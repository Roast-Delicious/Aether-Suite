-- ==========================================
-- AetherMeter - lightweight DPS / HPS meter for WoW Forever (1.60.x)
-- Reads Blizzard's built-in meter through C_DamageMeter.
-- DPS and HPS side by side in one window, or split into two windows.
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

local DEFAULTS = {
    opacityInCombat  = 0.8,
    opacityOutCombat = 0.3,
    split            = false,   -- false = one combined window, true = separate DPS and HPS windows
    metrics          = "both",  -- what to show: "both", "dps" (DPS only) or "hps" (HPS only)
    locked           = false,   -- true = windows can't be dragged or resized
    dock             = true,    -- sit to the right of the action bars (needs AetherBars' trim)
}

local db                -- points at AetherMeterDB once saved variables have loaded
local ApplyDock         -- below: docks the meter beside the action bars
local isDocked = false
local simTicker         -- test-simulation ticker

local MAX_ROWS     = 20     -- most rows per side (when a window is dragged tall)
local MAX_ENTRIES  = 40     -- most players read per side; scroll to see the ones that don't fit
local barHeight    = 15     -- thin bars so more players fit in a small window
local barSpacing   = 2
local PANEL_GAP    = 10
local EDGE         = 10
local PANEL_TOP    = -28    -- where the DPS / HPS headers sit
local ROWS_TOP     = 16     -- rows start this far below the header
local BOTTOM_PAD   = 16     -- leaves room for the resize handle
local EMPTY        = {}
local GRAY         = { r = 0.5, g = 0.5, b = 0.5 }

-- Window height needed to show a given number of rows.
local function HeightForRows(rows)
    return -PANEL_TOP + ROWS_TOP + rows * (barHeight + barSpacing) - barSpacing + BOTTOM_PAD
end

local DEFAULT_HEIGHT = HeightForRows(8)
local MIN_HEIGHT     = HeightForRows(1)
local MAX_HEIGHT     = HeightForRows(MAX_ROWS)
local MAX_WIDTH      = 1000

-- Default and minimum widths for each window shape.
local SIZES = {
    combined = { w = 500, minW = 340 },   -- both halves in one window
    dps      = { w = 260, minW = 230 },   -- DPS window when split (holds SPLIT/TEST buttons)
    hps      = { w = 260, minW = 180 },   -- HPS window when split
    single   = { w = 260, minW = 200 },   -- one window showing only DPS or only HPS
}

-- "both", "dps" or "hps": which meters are showing.
local function Metrics()
    return (db and db.metrics) or "both"
end

-- In combat, C_DamageMeter hands out "secret values": they can be shown on
-- font strings and status bars, but can't be compared, added up or sorted.
local function IsSecret(v)
    return issecretvalue ~= nil and issecretvalue(v)
end

-- Filled in further down; the window scripts below call them.
local RefreshVisibleRows, OpenContextMenu, mainWindow, hpsWindow, ScrollPanel, Wake

-- ==========================================
-- WINDOWS
-- ==========================================

-- Which saved size belongs to this window right now.
local function SizeKeyFor(win)
    if win == hpsWindow then return "hps" end
    if Metrics() ~= "both" then return "single" end
    return (db and db.split) and "dps" or "combined"
end

-- While locked, the saved position is frozen; only force (e.g. /am reset) can change it.
local function SaveWindowPosition(win, force)
    if not db or not win:GetLeft() then return end
    if db.locked and not force then return end
    db.positions = db.positions or {}
    db.positions[win.posKey] = { left = win:GetLeft(), top = win:GetTop() }
end

local function SaveWindowSize(win)
    if not db then return end
    local key = SizeKeyFor(win)
    db[key .. "W"] = math.floor(win:GetWidth() + 0.5)
    db[key .. "H"] = math.floor(win:GetHeight() + 0.5)
end

local function RestoreWindowPosition(win)
    local pos = db and db.positions and db.positions[win.posKey]
    if not pos then return false end
    win:ClearAllPoints()
    win:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", pos.left, pos.top)
    return true
end

-- Positions are saved by the addon itself, so tell WoW not to also save them.
local function StopUserPlacement(win)
    if win.SetUserPlaced then pcall(win.SetUserPlaced, win, false) end
end

-- The Aether window look (same as AetherHub): soft blue halo, inner frame line,
-- title strip with a gold underline, gold corner brackets and a gold gem.
local function AetherDecorate(frame, titleHeight)
    if frame.aetherTrim then return end
    frame.aetherTrim = true
    -- The Aether window look: rounded corners, a blue edge with a fine inner
    -- line, a soft blue glow, a navy title strip with a gold underline, and
    -- gold chevrons at 12, 3, 6 and 9. Smooth images (Media\win_*), so it
    -- stays crisp at any UI scale.
    local MEDIA, WHITE = "Interface\\AddOns\\AetherMeter\\Media\\", "Interface\\Buttons\\WHITE8X8"
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

local function CreateWindow(globalName, posKey)
    local win = CreateFrame("Frame", globalName, UIParent, "BackdropTemplate")
    win.posKey = posKey
    win:SetMovable(true)
    win:SetResizable(true)
    win:SetClampedToScreen(true)
    win:EnableMouse(true)
    win:RegisterForDrag("LeftButton")

    win:SetBackdrop({
        bgFile   = "Interface\\ChatFrame\\ChatFrameBackground",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true, tileSize = 16, edgeSize = 12,
        insets = { left = 4, right = 4, top = 4, bottom = 4 },
    })
    win:SetBackdropColor(0.05, 0.05, 0.05, 1)
    win:SetBackdropBorderColor(0.3, 0.7, 1, 1)

    win:SetScript("OnDragStart", function(self)
        Wake()
        if (db and db.locked) or isDocked then return end
        self:StartMoving()
    end)
    win:SetScript("OnDragStop", function(self)
        Wake()
        self:StopMovingOrSizing()
        StopUserPlacement(self)
        SaveWindowPosition(self)
    end)
    win:SetScript("OnSizeChanged", function() RefreshVisibleRows() end)
    -- Any click on the window (the lists included) makes it solid for a while.
    win:SetScript("OnMouseDown", function(self, button)
        Wake()
        if button == "RightButton" then OpenContextMenu(self) end
    end)

    -- WoW's fonts have no emoji, so the title uses color codes instead.
    win.title = win:CreateFontString(nil, "OVERLAY", "AetherFontWorldNormal")
    win.title:SetPoint("TOPLEFT", win, "TOPLEFT", EDGE, -8)
    win.title:SetText("|cff4da6ffAETHER METER|r")
    AetherDecorate(win, 26)

    -- Resize handle in the bottom-right corner (the same one the chat window uses).
    local grip = CreateFrame("Button", nil, win)
    grip:SetSize(14, 14)
    grip:SetPoint("BOTTOMRIGHT", win, "BOTTOMRIGHT", -2, 2)
    grip:SetFrameLevel(win:GetFrameLevel() + 10)
    grip:SetNormalTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Up")
    grip:SetHighlightTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Highlight")
    grip:SetPushedTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Down")
    grip:SetScript("OnMouseDown", function(_, button)
        Wake()
        if button == "LeftButton" and not (db and db.locked) and not isDocked then win:StartSizing("BOTTOMRIGHT") end
    end)
    win.grip = grip
    grip:SetScript("OnMouseUp", function()
        Wake()
        win:StopMovingOrSizing()
        StopUserPlacement(win)
        SaveWindowSize(win)
        SaveWindowPosition(win)
        RefreshVisibleRows()
    end)

    return win
end

local function SetWindowBounds(win, key)
    if win.SetResizeBounds then
        win:SetResizeBounds(SIZES[key].minW, MIN_HEIGHT, MAX_WIDTH, MAX_HEIGHT)
    end
end

local function ApplyWindowSize(win, key)
    SetWindowBounds(win, key)
    local w = db and db[key .. "W"] or SIZES[key].w
    local h = db and db[key .. "H"] or DEFAULT_HEIGHT
    win:SetSize(math.max(SIZES[key].minW, math.min(MAX_WIDTH, w)),
                math.max(MIN_HEIGHT, math.min(MAX_HEIGHT, h)))
end

mainWindow = CreateWindow("AetherMeterFrame", "main")
mainWindow:SetSize(SIZES.combined.w, DEFAULT_HEIGHT)
mainWindow:SetPoint("CENTER", UIParent, "CENTER")
SetWindowBounds(mainWindow, "combined")

hpsWindow = CreateWindow("AetherMeterHPSFrame", "hps")
hpsWindow:SetSize(SIZES.hps.w, DEFAULT_HEIGHT)
hpsWindow:SetPoint("TOPLEFT", mainWindow, "TOPRIGHT", 8, 0)
SetWindowBounds(hpsWindow, "hps")
hpsWindow:Hide()

-- Locking stops dragging and resizing, and hides the resize handles.
local function ApplyLock()
    local locked = (db and db.locked) or isDocked
    mainWindow.grip:SetShown(not locked)
    hpsWindow.grip:SetShown(not locked)
end

local function SetLocked(locked)
    if not db then return end
    db.locked = locked and true or false
    ApplyLock()
end

-- Thin divider between the two halves (combined mode only).
local divider = mainWindow:CreateTexture(nil, "ARTWORK")
divider:SetColorTexture(0.3, 0.7, 1, 0.35)
divider:SetWidth(1)
divider:SetPoint("TOP", mainWindow, "TOP", 0, PANEL_TOP + 2)
divider:SetPoint("BOTTOM", mainWindow, "BOTTOM", 0, 8)

-- While you're using the meter it's fully solid ("awake"); 10 seconds after
-- your last click, scroll, drag or resize it goes back to its normal transparency.
local WAKE_SECONDS = 10
local awake, sleepTimer = false, nil

local function ApplyAlpha()
    if not db then return end
    local alpha = (InCombatLockdown() or simTicker) and db.opacityInCombat or db.opacityOutCombat
    if awake then alpha = 1 end
    mainWindow:SetAlpha(alpha)
    hpsWindow:SetAlpha(alpha)
end

Wake = function()
    awake = true
    if sleepTimer then sleepTimer:Cancel() end
    sleepTimer = C_Timer.NewTimer(WAKE_SECONDS, function()
        sleepTimer = nil
        awake = false
        ApplyAlpha()
    end)
    ApplyAlpha()
end

-- ==========================================
-- PANELS AND PLAYER ROWS
-- ==========================================

local function CreatePlayerRow(panel, index)
    local row = CreateFrame("StatusBar", nil, panel)
    local y = -ROWS_TOP - ((index - 1) * (barHeight + barSpacing))
    -- Pinned to both edges of its panel, so the row stretches when the window is resized.
    row:SetPoint("TOPLEFT", panel, "TOPLEFT", 0, y)
    row:SetPoint("TOPRIGHT", panel, "TOPRIGHT", 0, y)
    row:SetHeight(barHeight)
    row:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")

    row.bg = row:CreateTexture(nil, "BACKGROUND")
    row.bg:SetAllPoints(true)
    row.bg:SetColorTexture(0, 0, 0, 0.4)

    -- Thin gold strip on the left edge marks your own bar.
    row.youMark = row:CreateTexture(nil, "OVERLAY")
    row.youMark:SetColorTexture(1, 0.69, 0, 1)
    row.youMark:SetPoint("TOPLEFT", row, "TOPLEFT", 0, 0)
    row.youMark:SetPoint("BOTTOMLEFT", row, "BOTTOMLEFT", 0, 0)
    row.youMark:SetWidth(3)
    row.youMark:Hide()

    -- Each value gets its own font string, because secret values can't be
    -- glued together into one string during combat.
    row.pctText = row:CreateFontString(nil, "OVERLAY", "AetherFontWorldSmall")
    row.pctText:SetPoint("RIGHT", row, "RIGHT", -4, 0)
    row.pctText:SetJustifyH("RIGHT")

    row.rateText = row:CreateFontString(nil, "OVERLAY", "AetherFontWorldSmall")
    row.rateText:SetPoint("RIGHT", row.pctText, "LEFT", -5, 0)
    row.rateText:SetJustifyH("RIGHT")
    row.rateText:SetTextColor(0.75, 0.75, 0.75)

    row.amountText = row:CreateFontString(nil, "OVERLAY", "AetherFontWorldSmall")
    row.amountText:SetPoint("RIGHT", row.rateText, "LEFT", -5, 0)
    row.amountText:SetJustifyH("RIGHT")

    row.rankText = row:CreateFontString(nil, "OVERLAY", "AetherFontWorldSmall")
    row.rankText:SetPoint("LEFT", row, "LEFT", 4, 0)
    row.rankText:SetText(index .. ".")

    row.nameText = row:CreateFontString(nil, "OVERLAY", "AetherFontWorldSmall")
    row.nameText:SetPoint("LEFT", row.rankText, "RIGHT", 3, 0)
    row.nameText:SetPoint("RIGHT", row.amountText, "LEFT", -4, 0)
    row.nameText:SetJustifyH("LEFT")
    row.nameText:SetWordWrap(false)

    row:Hide()
    return row
end

local function CreatePanel(label)
    local panel = CreateFrame("Frame", nil, mainWindow)
    panel.header = panel:CreateFontString(nil, "OVERLAY", "AetherFontWorldNormalSmall")
    panel.header:SetPoint("TOPLEFT", panel, "TOPLEFT", 2, 0)
    panel.header:SetText(label)
    panel.label = label
    panel.offset = 0     -- how many players are scrolled past at the top

    -- Mouse wheel scrolls this side; hold Shift to move a whole page.
    panel:EnableMouseWheel(true)
    panel:SetScript("OnMouseWheel", function(self, delta) Wake(); ScrollPanel(self, delta) end)

    panel.bars = {}
    for i = 1, MAX_ROWS do
        panel.bars[i] = CreatePlayerRow(panel, i)
    end
    panel.liveEntries = {}
    panel.order = {}     -- which entries the rows show, top to bottom
    panel.visibleRows = 8
    panel.window = mainWindow
    return panel
end

local dpsPanel = CreatePanel("|cffff8040DPS|r")
local hpsPanel = CreatePanel("|cff33dd66HPS|r")
local panels   = { dpsPanel, hpsPanel }

-- Puts a panel in a window: the left half, the right half, or the whole width.
local function PlacePanel(panel, win, part)
    panel:SetParent(win)
    panel:ClearAllPoints()
    if part == "LEFT" then
        panel:SetPoint("TOPLEFT", win, "TOPLEFT", EDGE, PANEL_TOP)
        panel:SetPoint("BOTTOMRIGHT", win, "BOTTOM", -PANEL_GAP / 2, BOTTOM_PAD)
    elseif part == "RIGHT" then
        panel:SetPoint("TOPLEFT", win, "TOP", PANEL_GAP / 2, PANEL_TOP)
        panel:SetPoint("BOTTOMRIGHT", win, "BOTTOMRIGHT", -EDGE, BOTTOM_PAD)
    else
        panel:SetPoint("TOPLEFT", win, "TOPLEFT", EDGE, PANEL_TOP)
        panel:SetPoint("BOTTOMRIGHT", win, "BOTTOMRIGHT", -EDGE, BOTTOM_PAD)
    end
    panel.window = win
end

PlacePanel(dpsPanel, mainWindow, "LEFT")
PlacePanel(hpsPanel, mainWindow, "RIGHT")

-- Work out how many rows fit in each panel's window, and hide any that no longer do.
RefreshVisibleRows = function()
    for _, panel in ipairs(panels) do
        local height = panel.window:GetHeight() or DEFAULT_HEIGHT
        local fit = math.floor((height - HeightForRows(0) + barSpacing) / (barHeight + barSpacing))
        panel.visibleRows = math.max(1, math.min(MAX_ROWS, fit))
        for i = panel.visibleRows + 1, MAX_ROWS do
            panel.bars[i]:Hide()
        end
    end
end

-- ==========================================
-- RENDERING
-- ==========================================

-- Bars glide toward each new value instead of snapping (WoW Forever / 12.x StatusBar feature).
local SMOOTH = Enum.StatusBarInterpolation and Enum.StatusBarInterpolation.ExponentialEaseOut

local function SetBarRange(row, maxValue)
    if not (SMOOTH and pcall(row.SetMinMaxValues, row, 0, maxValue, SMOOTH)) then
        pcall(row.SetMinMaxValues, row, 0, maxValue)
    end
end

local function SetBarValue(row, value)
    if not (SMOOTH and pcall(row.SetValue, row, value, SMOOTH)) then
        pcall(row.SetValue, row, value)
    end
end

-- One decimal place everywhere: 850.3 / 2.4K / 1.3M / 1.1B.
-- In combat the numbers are secret, so Lua can't divide them; Blizzard's
-- AbbreviateNumbers can, and these breakpoints tell it to keep one decimal.
local ONE_DECIMAL = {
    breakpointData = {
        { breakpoint = 1e9, abbreviation = "B", significandDivisor = 1e8, fractionDivisor = 10, abbreviationIsGlobal = false },
        { breakpoint = 1e6, abbreviation = "M", significandDivisor = 1e5, fractionDivisor = 10, abbreviationIsGlobal = false },
        { breakpoint = 1e3, abbreviation = "K", significandDivisor = 1e2, fractionDivisor = 10, abbreviationIsGlobal = false },
        { breakpoint = 0,   abbreviation = "",  significandDivisor = 0.1, fractionDivisor = 10, abbreviationIsGlobal = false },
    },
}

local function FormatNumber(num)
    if num == nil then return "0.0" end
    if IsSecret(num) then
        if AbbreviateNumbers then
            local ok, text = pcall(AbbreviateNumbers, num, ONE_DECIMAL)
            if ok then return text end
            ok, text = pcall(AbbreviateNumbers, num)
            if ok then return text end
        end
        return num
    end
    if num >= 1e9 then
        return string.format("%.1fB", num / 1e9)
    elseif num >= 1e6 then
        return string.format("%.1fM", num / 1e6)
    elseif num >= 1e3 then
        return string.format("%.1fK", num / 1e3)
    end
    return string.format("%.1f", num)
end

-- entries: list of { name, class, amount, perSecond }, already in display order
-- (highest per-second first). maxRate is the top row's per-second value: bar
-- length shows live DPS/HPS, so the bars rise and fall with the fight.
-- totalAmount is everyone's damage/healing added up, for the % column.
local function UpdateRows(panel, entries, maxRate, totalAmount)
    -- Remember what was shown, so scrolling can redraw without new data.
    panel.lastEntries, panel.lastMax, panel.lastTotal = entries, maxRate, totalAmount

    if maxRate == nil or (not IsSecret(maxRate) and maxRate <= 0) then
        maxRate = 1
    end
    local canDoMath = totalAmount ~= nil and not IsSecret(totalAmount)

    -- Your own bar always takes the top row (with your real rank); everyone
    -- else follows in rank order, and scrolling moves only them.
    local count = #entries
    local slots = panel.visibleRows
    local mine
    for i = 1, count do
        if entries[i].isMe then mine = i; break end
    end
    local otherCount = count - (mine and 1 or 0)
    local otherSlots = slots - (mine and 1 or 0)
    local maxOffset = math.max(0, otherCount - otherSlots)
    panel.offset = math.max(0, math.min(panel.offset or 0, maxOffset))
    local offset = panel.offset

    local order, shown = panel.order, 0
    for i = #order, 1, -1 do order[i] = nil end
    if mine and slots >= 1 then
        shown = 1
        order[1] = mine
    end
    local passed = 0
    for i = 1, count do
        if i ~= mine then
            passed = passed + 1
            if passed > offset and shown < slots then
                shown = shown + 1
                order[shown] = i
            end
        end
    end

    if count > slots then
        panel.header:SetText(string.format("%s  |cff999999%d of %d (scroll)|r",
            panel.label, shown, count))
    else
        panel.header:SetText(panel.label)
    end

    for i = 1, MAX_ROWS do
        local row  = panel.bars[i]
        local rank = order[i]
        local data = rank and entries[rank]

        if data then
            row.rankText:SetText(rank .. ".")
            row.youMark:SetShown(rank == mine)
            local color = RAID_CLASS_COLORS[data.class] or GRAY
            row:SetStatusBarColor(color.r, color.g, color.b, 0.85)

            row.nameText:SetText(data.name or UNKNOWN)
            row.amountText:SetText(FormatNumber(data.amount))
            row.rateText:SetText(FormatNumber(data.perSecond))

            if canDoMath and totalAmount > 0 and data.amount and not IsSecret(data.amount) then
                row.pctText:SetText(string.format("%.1f%%", data.amount / totalAmount * 100))
            else
                row.pctText:SetText("")   -- percentages come back once combat ends
            end

            local wasHidden = not row:IsShown()
            SetBarRange(row, maxRate)
            SetBarValue(row, data.perSecond or 0)
            if wasHidden and row.SetToTargetValue then
                row:SetToTargetValue()    -- a newly shown row starts at its value, not at zero
            end
            row:Show()
        else
            row:Hide()
        end
    end
end

ScrollPanel = function(panel, delta)
    local step = IsShiftKeyDown() and panel.visibleRows or 1
    panel.offset = (panel.offset or 0) - delta * step
    if panel.lastEntries then
        UpdateRows(panel, panel.lastEntries, panel.lastMax, panel.lastTotal)
    end
end

-- ==========================================
-- LIVE DATA FROM C_DamageMeter
-- ==========================================

local function FetchPanel(panel, meterType)
    local ok, session = pcall(C_DamageMeter.GetCombatSessionFromType,
                              Enum.DamageMeterSessionType.Current, meterType)
    if not ok or not session then
        UpdateRows(panel, EMPTY)
        return
    end

    -- The Dps / Hps meter types arrive already sorted by per-second rate, so no
    -- table.sort here (sorting secret values in combat would throw an error).
    local entries, count = panel.liveEntries, 0
    for _, source in ipairs(session.combatSources or EMPTY) do
        count = count + 1
        local entry = entries[count] or {}
        entries[count] = entry
        entry.name      = source.name
        entry.class     = source.classFilename
        entry.amount    = source.totalAmount
        entry.perSecond = source.amountPerSecond
        entry.isMe      = (source.isLocalPlayer == true)
        if count >= MAX_ENTRIES then break end
    end
    for i = count + 1, #entries do entries[i] = nil end

    local topRate = entries[1] and entries[1].perSecond
    UpdateRows(panel, entries, topRate, session.totalAmount)
end

local function FetchLiveServerMetrics()
    if not db or simTicker then return end
    if not (C_DamageMeter and C_DamageMeter.GetCombatSessionFromType
            and Enum.DamageMeterType and Enum.DamageMeterSessionType) then
        return
    end
    FetchPanel(dpsPanel, Enum.DamageMeterType.Dps)
    FetchPanel(hpsPanel, Enum.DamageMeterType.Hps)
end

-- Refresh 4 times a second while either window is visible.
local heartbeat = CreateFrame("Frame")
local sinceLast, sinceDock = 0, 0
heartbeat:SetScript("OnUpdate", function(_, elapsed)
    sinceDock = sinceDock + elapsed
    if sinceDock >= 0.5 then
        sinceDock = 0
        if ApplyDock and db then ApplyDock() end
    end
    sinceLast = sinceLast + elapsed
    if sinceLast >= 0.25 then
        sinceLast = 0
        if mainWindow:IsShown() or hpsWindow:IsShown() then FetchLiveServerMetrics() end
    end
end)

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
-- BUTTONS: TEST, SPLIT / JOIN
-- ==========================================

local function CreateSmallButton(parent, globalName, width, label)
    local button = AetherButton(parent, globalName, true)
    button:SetSize(width, 18)
    button:SetText(label)
    return button
end

local testButton = CreateSmallButton(mainWindow, "AetherMeterTestButton", 45, "TEST")
testButton:SetPoint("TOPRIGHT", mainWindow, "TOPRIGHT", -8, -6)

local splitButton = CreateSmallButton(mainWindow, "AetherMeterSplitButton", 50, "SPLIT")
splitButton:SetPoint("RIGHT", testButton, "LEFT", -4, 0)

local joinButton = CreateSmallButton(hpsWindow, "AetherMeterJoinButton", 50, "JOIN")
joinButton:SetPoint("TOPRIGHT", hpsWindow, "TOPRIGHT", -8, -6)

-- Shows or hides the meter (both windows when split).
local function SetMeterShown(show)
    mainWindow:SetShown(show)
    hpsWindow:SetShown(show and db ~= nil and db.split and Metrics() == "both")
end

-- Arranges the panels for the current mode. placeBeside = true puts the HPS
-- window right next to the DPS window (used when the SPLIT button is clicked).
local function ApplyLayout(placeBeside)
    local split = db and db.split

    -- Pin the main window by its top-left corner so changing its width
    -- grows/shrinks it to the right instead of around its center.
    -- The saved spot wins over wherever the window happens to be drawn right now.
    if not RestoreWindowPosition(mainWindow) then
        local left, top = mainWindow:GetLeft(), mainWindow:GetTop()
        if left and top then
            mainWindow:ClearAllPoints()
            mainWindow:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", left, top)
        end
    end

    -- Only one meter: it fills the main window, and there's nothing to split.
    if Metrics() ~= "both" then
        local keep = (Metrics() == "hps") and hpsPanel or dpsPanel
        local other = (keep == dpsPanel) and hpsPanel or dpsPanel
        PlacePanel(keep, mainWindow, "FULL")
        keep:Show()
        other:Hide()
        divider:Hide()
        splitButton:Hide()
        ApplyWindowSize(mainWindow, "single")
        hpsWindow:Hide()
        RefreshVisibleRows()
        ApplyAlpha()
        if ApplyDock then ApplyDock(true) end
        return
    end
    dpsPanel:Show()
    hpsPanel:Show()
    splitButton:Show()

    if split then
        PlacePanel(dpsPanel, mainWindow, "FULL")
        PlacePanel(hpsPanel, hpsWindow, "FULL")
        divider:Hide()
        splitButton:SetText("JOIN")
        ApplyWindowSize(mainWindow, "dps")
        ApplyWindowSize(hpsWindow, "hps")

        if placeBeside or not RestoreWindowPosition(hpsWindow) then
            hpsWindow:ClearAllPoints()
            local right, top = mainWindow:GetRight(), mainWindow:GetTop()
            if right and top then
                hpsWindow:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", right + 8, top)
            else
                hpsWindow:SetPoint("TOPLEFT", mainWindow, "TOPRIGHT", 8, 0)
            end
            SaveWindowPosition(hpsWindow, placeBeside)
        end
        hpsWindow:SetShown(mainWindow:IsShown())
    else
        PlacePanel(dpsPanel, mainWindow, "LEFT")
        PlacePanel(hpsPanel, mainWindow, "RIGHT")
        divider:Show()
        splitButton:SetText("SPLIT")
        ApplyWindowSize(mainWindow, "combined")
        hpsWindow:Hide()
    end
    RefreshVisibleRows()
    ApplyAlpha()
    if ApplyDock then ApplyDock(true) end
end

-- ==========================================
-- DOCKED BESIDE THE ACTION BARS
-- ==========================================
-- The space between the bar panels' right edge and the screen's right edge,
-- as tall as the block of bars: the mirror image of AetherChat on the left.
local DOCK_GAP, DOCK_MARGIN, DOCK_OUT = 4, 6, 4   -- DOCK_OUT: room for the gold corners outside the window
local lastDock
-- Until the bars have settled after login, use the dock spot saved last
-- time, so the meter opens right where it belongs instead of hopping there.
local dockSettled = false
local function DockRect()
    if not db or db.dock == false then return nil end
    local panels = AetherBars_PanelRects and AetherBars_PanelRects()
    if not panels or #panels == 0 then
        local s = db.dockSpot
        if not dockSettled and type(s) == "table" and s[4] then return s[1], s[2], s[3], s[4] end
        return nil
    end
    local maxR, top, bottom
    for _, r in ipairs(panels) do
        maxR = math.max(maxR or -math.huge, r.R)
        top = math.max(top or -math.huge, r.T)
        bottom = math.min(bottom or math.huge, r.B)
    end
    local l = math.floor(maxR + DOCK_GAP + DOCK_OUT + 0.5)
    local r = math.floor(UIParent:GetWidth() - DOCK_MARGIN - DOCK_OUT + 0.5)
    local b = math.floor(bottom + DOCK_OUT + 0.5)
    local t = math.floor(top - DOCK_OUT + 0.5)
    db.dockSpot = { l, r, b, t }
    return l, r, b, t
end

local function PlaceAt(win, l, b, w, h)
    win:ClearAllPoints()
    win:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", l, b)
    win:SetSize(w, h)
end

ApplyDock = function(force)
    if not db then return end
    local l, r, b, t = DockRect()
    local fits = false
    if l then
        local w, h = r - l, t - b
        if Metrics() == "both" and db.split then
            local half = math.floor((w - 8) / 2)
            fits = half >= SIZES.dps.minW and h >= MIN_HEIGHT
            if fits then
                local key = table.concat({ l, r, b, t, "split" }, ",")
                if force or key ~= lastDock then
                    lastDock = key
                    PlaceAt(mainWindow, l, b, half, h)
                    PlaceAt(hpsWindow, l + half + 8, b, w - half - 8, h)
                    RefreshVisibleRows()
                end
            end
        else
            fits = w >= SIZES[Metrics() == "both" and "combined" or "single"].minW and h >= MIN_HEIGHT
            if fits then
                local key = table.concat({ l, r, b, t, "one" }, ",")
                if force or key ~= lastDock then
                    lastDock = key
                    PlaceAt(mainWindow, l, b, w, h)
                    RefreshVisibleRows()
                end
            end
        end
    end
    -- Bars not ready yet: keep the meter where it is rather than undocking.
    if not l and not dockSettled and db.dock ~= false then return end
    if fits ~= isDocked then
        isDocked = fits
        mainWindow.grip:SetShown(not fits and not db.locked)
        hpsWindow.grip:SetShown(not fits and not db.locked)
        -- Docked, the meter sits flush against the bars and the screen's edge:
        -- keep only the top chevron (the side and bottom ones would collide).
        for _, w in ipairs({ mainWindow, hpsWindow }) do
            local chev = type(w.aetherChevrons) == "table" and w.aetherChevrons or {}
            for key, set in pairs(chev) do
                for _, tex in ipairs(set) do tex:SetShown(key == "top" or not fits) end
            end
        end
        if not fits then
            lastDock = nil
            ApplyLayout(false)   -- back to your own saved spot and size
        end
    end
end

-- Follow the bars the moment they move (AetherBars calls this).
AetherBars_Listeners = AetherBars_Listeners or {}
table.insert(AetherBars_Listeners, function() if db and ApplyDock then ApplyDock() end end)

local function SetSplit(split)
    if not db then return end
    db.split = split
    ApplyLayout(split)
    FetchLiveServerMetrics()   -- does nothing while the test is running
end

-- Show both meters, or only DPS, or only HPS.
local METRIC_NAMES = { both = "DPS and HPS", dps = "DPS only", hps = "HPS only" }
local function SetMetrics(which)
    if not db or not METRIC_NAMES[which] then return end
    db.metrics = which
    ApplyLayout(false)
    FetchLiveServerMetrics()
end

splitButton:SetScript("OnClick", function() SetSplit(not (db and db.split)) end)
joinButton:SetScript("OnClick", function() SetSplit(false) end)

-- ==========================================
-- EVENTS (saved settings + combat opacity)
-- ==========================================

-- Puts both windows back on their saved spots. Run again after the loading
-- screen, once WoW has finished sizing the screen.
local function ReapplyPositions()
    if not db then return end
    -- Docked: the dock decides where it goes, not the old saved spot.
    if isDocked or (db.dock ~= false and not dockSettled) then
        if ApplyDock then ApplyDock(true) end
        if isDocked then return end
    end
    RestoreWindowPosition(mainWindow)
    if db.split then RestoreWindowPosition(hpsWindow) end
end

mainWindow:RegisterEvent("ADDON_LOADED")
mainWindow:RegisterEvent("PLAYER_ENTERING_WORLD")
mainWindow:RegisterEvent("PLAYER_REGEN_DISABLED")
mainWindow:RegisterEvent("PLAYER_REGEN_ENABLED")
mainWindow:SetScript("OnEvent", function(self, event, arg1)
    if event == "ADDON_LOADED" then
        if arg1 ~= ADDON_NAME then return end
        -- Saved variables only exist from this point on, not when the file first runs.
        -- WoW Forever 1.60 has been reported not to read account-wide saved
        -- variables back, so settings are also kept per character, and the
        -- per-character copy is used when it exists.
        local saved = AetherMeterDB
        if type(AetherMeterCharDB) == "table" and next(AetherMeterCharDB) then
            saved = AetherMeterCharDB
        end
        saved = type(saved) == "table" and saved or {}
        for key, value in pairs(DEFAULTS) do
            if saved[key] == nil then saved[key] = value end
        end
        -- Settings from older versions, no longer used.
        saved.mode = nil
        if saved.width then
            saved.combinedW, saved.combinedH = saved.width, saved.height
            saved.width, saved.height = nil, nil
        end
        db = saved
        AetherMeterDB = db
        AetherMeterCharDB = db

        -- Keep WoW's own layout cache from moving the windows; this addon places them.
        StopUserPlacement(mainWindow)
        StopUserPlacement(hpsWindow)

        ApplyLayout(false)
        ApplyLock()
        self:UnregisterEvent("ADDON_LOADED")
    elseif event == "PLAYER_ENTERING_WORLD" then
        ReapplyPositions()
        C_Timer.After(1, ReapplyPositions)   -- once more, after the UI has settled
        -- AetherBars' last login pass runs at 3s; after that, trust it fully.
        C_Timer.After(4, function() dockSettled = true; if ApplyDock then ApplyDock() end end)
    elseif event == "PLAYER_REGEN_DISABLED" then
        dpsPanel.offset, hpsPanel.offset = 0, 0   -- a new fight starts at the top of the list
        if db then
            local alpha = awake and 1 or db.opacityInCombat
            mainWindow:SetAlpha(alpha)
            hpsWindow:SetAlpha(alpha)
        end
    elseif event == "PLAYER_REGEN_ENABLED" then
        ApplyAlpha()
        FetchLiveServerMetrics()   -- values are readable again, so percentages return
    end
end)

-- ==========================================
-- TEST SIMULATION
-- ==========================================

local fakeParty = {
    { name = "Grommash", class = "WARRIOR", baseDps = 2400, baseHps = 0    },
    { name = "Jaina",    class = "MAGE",    baseDps = 2900, baseHps = 0    },
    { name = "Thrall",   class = "SHAMAN",  baseDps = 1500, baseHps = 1400 },
    { name = "Valeera",  class = "ROGUE",   baseDps = 2250, baseHps = 0    },
    { name = "Anduin",   class = "PRIEST",  baseDps = 500,  baseHps = 2600 },
    { name = "You",      class = "PALADIN", baseDps = 900,  baseHps = 2100 },
    { name = "Rexxar",   class = "HUNTER",  baseDps = 2600, baseHps = 0    },
    { name = "Guldan",   class = "WARLOCK", baseDps = 2700, baseHps = 0    },
    { name = "Malfurion",class = "DRUID",   baseDps = 800,  baseHps = 2300 },
    { name = "Tyrande",  class = "PRIEST",  baseDps = 1100, baseHps = 1900 },
}

local SIM_TICK   = 0.5   -- seconds between simulated hits / heals
local SIM_WINDOW = 10    -- per-second rate is averaged over the last 10 ticks (5 seconds)
local simDamage, simHealing = {}, {}

-- Adds one tick of swingy output to a tracker and refreshes its 5-second rate.
local function AdvanceTracker(tracker, base)
    local variance = math.random(60, 140) / 100
    local roll = math.random()
    if roll < 0.08 then
        variance = variance * 2.2   -- burst / cooldowns
    elseif roll < 0.15 then
        variance = variance * 0.3   -- moving, out of range, out of mana
    end
    local value = base * variance * SIM_TICK
    tracker.amount = tracker.amount + value

    table.insert(tracker.recent, value)
    if #tracker.recent > SIM_WINDOW then table.remove(tracker.recent, 1) end
    local windowTotal = 0
    for _, v in ipairs(tracker.recent) do windowTotal = windowTotal + v end
    tracker.perSecond = windowTotal / (#tracker.recent * SIM_TICK)
end

local function SimulatePanel(panel, store, baseKey)
    local total, list = 0, {}
    for i, member in ipairs(fakeParty) do
        local base = member[baseKey]
        if base > 0 then
            local tracker = store[i]
            if not tracker then
                tracker = { name = member.name, class = member.class, amount = 0, perSecond = 0, recent = {},
                            isMe = (member.name == "You") }
                store[i] = tracker
            end
            AdvanceTracker(tracker, base)
            total = total + tracker.amount
            list[#list + 1] = tracker
        end
    end
    table.sort(list, function(a, b) return a.perSecond > b.perSecond end)
    UpdateRows(panel, list, list[1] and list[1].perSecond, total)
end

local function RunSimulationTick()
    SimulatePanel(dpsPanel, simDamage, "baseDps")
    SimulatePanel(hpsPanel, simHealing, "baseHps")
end

local function StopSimulation()
    if simTicker then simTicker:Cancel() end
    simTicker = nil
    testButton:SetText("TEST")
    ApplyAlpha()
    FetchLiveServerMetrics()
end

testButton:SetScript("OnClick", function()
    if simTicker then
        StopSimulation()
    else
        simDamage, simHealing = {}, {}
        simTicker = C_Timer.NewTicker(SIM_TICK, RunSimulationTick)
        testButton:SetText("STOP")
        ApplyAlpha()
        RunSimulationTick()
    end
end)

for _, button in ipairs({ testButton, splitButton, joinButton }) do
    button:HookScript("OnClick", function() Wake() end)
end

-- ==========================================
-- RIGHT-CLICK MENU (works on either window)
-- ==========================================

local function SetOpacity(key, value)
    if not db then return end
    db[key] = value
    ApplyAlpha()
end

OpenContextMenu = function(owner)
    MenuUtil.CreateContextMenu(owner, function(_, rootDescription)
        rootDescription:CreateTitle("|cff4da6ffAetherMeter Options|r")

        local showMenu = rootDescription:CreateButton("Show")
        for _, which in ipairs({ "both", "dps", "hps" }) do
            showMenu:CreateRadio(METRIC_NAMES[which],
                function() return Metrics() == which end,
                function() SetMetrics(which) end)
        end

        if Metrics() == "both" then
            if db and db.split then
                rootDescription:CreateButton("Combine into One Window", function() SetSplit(false) end)
            else
                rootDescription:CreateButton("Split into Two Windows", function() SetSplit(true) end)
            end
        end

        rootDescription:CreateCheckbox("Lock Window Position",
            function() return db and db.locked end,
            function() SetLocked(not (db and db.locked)) end)

        local opacityMenu = rootDescription:CreateButton("Set Transparency")
        for _, pct in ipairs({ 100, 80, 60 }) do
            opacityMenu:CreateButton("In Combat: " .. pct .. "%", function()
                SetOpacity("opacityInCombat", pct / 100)
            end)
        end
        for _, pct in ipairs({ 100, 60, 30 }) do
            opacityMenu:CreateButton("Out of Combat: " .. pct .. "%", function()
                SetOpacity("opacityOutCombat", pct / 100)
            end)
        end

        rootDescription:CreateButton(simTicker and "Stop Preview" or "Preview Meter", function()
            testButton:Click()
        end)
        rootDescription:CreateButton("Hide Meter", function() SetMeterShown(false) end)
    end)
end

-- ==========================================
-- SLASH COMMANDS
-- ==========================================

SLASH_AETHERMETER1 = "/aether"
SLASH_AETHERMETER2 = "/am"

SlashCmdList["AETHERMETER"] = function(msg)
    local command = (msg:match("^(%S*)") or ""):lower()

    if command == "toggle" then
        SetMeterShown(not mainWindow:IsShown())
    elseif command == "dock" then
        if not db then return end
        db.dock = ((msg:match("^%S+%s+(%S+)") or ""):lower() ~= "off")
        print("|cff4da6ffAetherMeter:|r docked beside the action bars: " .. (db.dock and "on" or "off"))
        ApplyDock(true)
    elseif command == "split" then
        SetSplit(true)
    elseif command == "join" then
        SetSplit(false)
    elseif command == "reset" then
        if db then
            db.positions = nil
            for _, key in ipairs({ "combined", "dps", "hps" }) do
                db[key .. "W"], db[key .. "H"] = nil, nil
            end
        end
        ApplyLayout(false)                 -- back to default sizes
        mainWindow:ClearAllPoints()
        mainWindow:SetPoint("CENTER", UIParent, "CENTER")
        SetMeterShown(true)
        ApplyLayout(true)                  -- HPS window (if split) goes back beside it
        SaveWindowPosition(mainWindow, true)
    elseif command == "test" then
        testButton:Click()
    elseif command == "lock" or command == "unlock" then
        SetLocked(command == "lock")
        print("|cff4da6ffAetherMeter:|r window " .. (db and db.locked and "locked" or "unlocked"))
    elseif command == "show" then
        -- /am show (the meter), or /am show dps | hps | both (which meters)
        local which = (msg:match("^%S+%s+(%S+)") or ""):lower()
        if which == "" then
            SetMeterShown(true)
        elseif METRIC_NAMES[which] then
            SetMetrics(which)
            SetMeterShown(true)
            print("|cff4da6ffAetherMeter:|r showing " .. METRIC_NAMES[which])
        else
            print("|cff4da6ffAetherMeter:|r /am show dps, /am show hps or /am show both")
        end
    elseif command == "hide" then
        SetMeterShown(false)
    elseif command == "opacity" then
        -- /am opacity in 80   or   /am opacity out 0.3
        local which, num = (msg:match("^%S*%s*(.*)$") or ""):lower():match("^(%a+)%s+([%d%.]+)")
        num = tonumber(num)
        if num and num > 1 then num = num / 100 end
        if num and (which == "in" or which == "out") then
            num = math.max(0, math.min(1, num))
            SetOpacity(which == "in" and "opacityInCombat" or "opacityOutCombat", num)
            print(string.format("|cff4da6ffAetherMeter:|r opacity %s combat set to %d%%",
                which == "in" and "in" or "out of", math.floor(num * 100 + 0.5)))
        else
            print("|cff4da6ffAetherMeter:|r /am opacity in 0-100, /am opacity out 0-100")
        end
    else
        print("|cff4da6ffAetherMeter:|r /am toggle, /am show, /am hide, /am show dps|hps|both, /am lock, /am unlock, /am split, /am join, /am dock on|off, /am opacity, /am reset, /am test")
    end
end
