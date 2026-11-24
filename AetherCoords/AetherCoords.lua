-- AetherCoords: always-on player coordinates, a cursor popup on the world map,
-- and your own waypoints (with notes) on the world map and minimap.
-- Clean look to match AetherBars: dark translucent panels, thin edges, outlined text.

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

local ADDON = ...
local defaults = {
    decimals = 1,     -- 0, 1 or 2 decimal places
    minimap  = true,  -- show the readout under the minimap
    popup    = true,  -- show the cursor popup on the world map
    -- saved position of the minimap readout (nil = under the minimap)
}
local db
local FONT = STANDARD_TEXT_FONT or "Fonts\\FRIZQT__.TTF"

local function Print(msg) print("|cff66ccffAetherCoords:|r " .. msg) end

local function Format(x, y)
    if not x or not y then return "--, --" end
    local f = "%." .. db.decimals .. "f"
    return format(f .. ", " .. f, x * 100, y * 100)
end

-- Player position on a given map (or the map you're standing in). Returns nil in instances.
local function PlayerPos(mapID)
    if not C_Map or not C_Map.GetBestMapForUnit then return end
    mapID = mapID or C_Map.GetBestMapForUnit("player")
    if not mapID then return end
    local pos = C_Map.GetPlayerMapPosition(mapID, "player")
    if not pos then return end
    local x, y = pos:GetXY()
    if not x or (x == 0 and y == 0) then return end
    return x, y
end

-- A small clean panel: dark background, 1px edge, outlined text
local function MakePanel(parent, size)
    local f = CreateFrame("Frame", nil, parent)
    local edge = f:CreateTexture(nil, "BACKGROUND", nil, -8)
    edge:SetPoint("TOPLEFT", -1, 1)
    edge:SetPoint("BOTTOMRIGHT", 1, -1)
    edge:SetColorTexture(0, 0, 0, 0.8)
    local bg = f:CreateTexture(nil, "BACKGROUND", nil, -7)
    bg:SetAllPoints()
    bg:SetColorTexture(0.05, 0.05, 0.05, 0.6)
    f.edge, f.bg = edge, bg
    local text = f:CreateFontString(nil, "OVERLAY")
    if not AetherSetFont(text, "Bold", size, true) then text:SetFont(FONT, size, "OUTLINE") end
    text:SetPoint("CENTER")
    f.text = text
    f.SetValue = function(self, s)
        self.text:SetText(s)
        self:SetSize(self.text:GetStringWidth() + 12, size + 8)
    end
    return f
end

-- The readout under the minimap: a navy pill with rounded ends and a fine
-- Aether-blue edge (matches AetherSkins' minimap). Plain textures only.
local function PillLook(f)
    local MEDIA_P = "Interface\\AddOns\\AetherCoords\\Media\\"
    f.edge:SetAlpha(0); f.bg:SetAlpha(0)
    local NAVY, BLUE = { 0.075, 0.157, 0.29 }, { 0.3, 0.65, 1 }
    local function T(file, sub, c, a)
        local t = f:CreateTexture(nil, "BACKGROUND", nil, sub)
        if file then t:SetTexture(MEDIA_P .. file) else t:SetColorTexture(1, 1, 1, 1) end
        t:SetVertexColor(c[1], c[2], c[3], a or 1)
        return t
    end
    local l, r, m = T("pill_cap", -6, NAVY, 0.94), T("pill_cap", -6, NAVY, 0.94), T(nil, -6, NAVY, 0.94)
    local ll, rl = T("pill_capline", -5, BLUE), T("pill_capline", -5, BLUE)
    local top, bot = T(nil, -5, BLUE), T(nil, -5, BLUE)
    r:SetTexCoord(1, 0, 0, 1); rl:SetTexCoord(1, 0, 0, 1)
    local function Place()
        local h = f:GetHeight(); if not h or h <= 0 then return end
        l:ClearAllPoints(); l:SetPoint("TOPLEFT"); l:SetPoint("BOTTOMLEFT"); l:SetWidth(h / 2)
        r:ClearAllPoints(); r:SetPoint("TOPRIGHT"); r:SetPoint("BOTTOMRIGHT"); r:SetWidth(h / 2)
        ll:SetAllPoints(l); rl:SetAllPoints(r)
        m:ClearAllPoints(); m:SetPoint("TOPLEFT", l, "TOPRIGHT"); m:SetPoint("BOTTOMRIGHT", r, "BOTTOMLEFT")
        top:ClearAllPoints(); top:SetPoint("TOPLEFT", m); top:SetPoint("TOPRIGHT", m); top:SetHeight(1)
        bot:ClearAllPoints(); bot:SetPoint("BOTTOMLEFT", m); bot:SetPoint("BOTTOMRIGHT", m); bot:SetHeight(1)
    end
    f:HookScript("OnSizeChanged", Place)
    Place()
    local set = f.SetValue   -- a little more room at the ends for the round caps
    f.SetValue = function(self, s) set(self, s); self:SetWidth(self.text:GetStringWidth() + 12 + self:GetHeight() / 2) end
end

------------------------------------------------------------
-- 1) Always-on readout under the minimap
------------------------------------------------------------
local mini

local function PlaceMini()
    mini:ClearAllPoints()
    if db.point then
        mini:SetPoint("CENTER", UIParent, "BOTTOMLEFT", db.point[1], db.point[2])
    elseif Minimap then
        -- AetherSkins' ring has a gold chevron hanging below the minimap: sit under it
        local gap = 6
        if _G.AetherSkins_RingActive then gap = (Minimap:GetWidth() or 140) / 2 * 0.28 + 4 end
        mini:SetPoint("TOP", Minimap, "BOTTOM", 0, -gap)
    else
        mini:SetPoint("TOP", UIParent, "TOP", 0, -10)
    end
end

-- AetherSkins calls this once its ring is up (it loads after AetherCoords)
function AetherCoords_RefreshMini() if mini then PlaceMini() end end

local function CreateMini()
    mini = MakePanel(UIParent, 12)
    PillLook(mini)
    mini:SetFrameStrata("MEDIUM")
    mini:SetClampedToScreen(true)
    mini:SetMovable(true)
    mini:RegisterForDrag("LeftButton")
    mini:SetScript("OnDragStart", function(self)
        if IsShiftKeyDown() then self:StartMoving() end
    end)
    mini:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        local x, y = self:GetCenter()
        db.point = { x, y }
        PlaceMini()
    end)
    mini:EnableMouse(true)
    mini:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_BOTTOM")
        GameTooltip:AddLine("Your coordinates")
        GameTooltip:AddLine("Shift-drag to move. /mc for options.", 0.7, 0.7, 0.7)
        GameTooltip:Show()
    end)
    mini:SetScript("OnLeave", function() GameTooltip:Hide() end)
    PlaceMini()

    local t = 0
    mini:SetScript("OnUpdate", function(self, dt)
        t = t + dt
        if t < 0.1 then return end
        t = 0
        self:SetValue(Format(PlayerPos()))
    end)
    mini:SetValue(Format(PlayerPos()))
    mini:SetShown(db.minimap)
end

------------------------------------------------------------
-- 2) World map: cursor popup + your position in the top-right corner
------------------------------------------------------------
local popup, mapLine
local LayoutWorldPins, AskForNote   -- waypoints, below

-- Cursor position on the map canvas as 0..1, or nil when off the map
local function CursorOnMap()
    local wm = WorldMapFrame
    local sc = wm and wm.ScrollContainer
    if not sc or not sc:IsMouseOver() then return end
    local x, y
    if sc.GetNormalizedCursorPosition then
        x, y = sc:GetNormalizedCursorPosition()
    elseif sc.Child then
        local cx, cy = GetCursorPosition()
        local s = sc.Child:GetEffectiveScale()
        cx, cy = cx / s, cy / s
        x = (cx - sc.Child:GetLeft()) / sc.Child:GetWidth()
        y = (sc.Child:GetTop() - cy) / sc.Child:GetHeight()
    end
    if x and y and x >= 0 and x <= 1 and y >= 0 and y <= 1 then return x, y end
end

local function SetupWorldMap()
    local wm = WorldMapFrame
    if not wm or popup then return end
    local anchor = wm.ScrollContainer or wm

    popup = MakePanel(wm, 13)
    popup:SetFrameStrata("TOOLTIP")
    popup:Hide()

    mapLine = MakePanel(anchor, 12)
    mapLine:SetFrameLevel(anchor:GetFrameLevel() + 20)
    mapLine:SetPoint("TOPRIGHT", anchor, "TOPRIGHT", -8, -8)

    local t = 0
    local updater = CreateFrame("Frame", nil, wm)
    updater:SetScript("OnUpdate", function(_, dt)
        -- Popup follows the cursor every frame for smoothness
        local x, y = CursorOnMap()
        if db.popup and x then
            popup:SetValue(Format(x, y))
            local cx, cy = GetCursorPosition()
            local s = popup:GetEffectiveScale()
            popup:ClearAllPoints()
            popup:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", cx / s + 16, cy / s + 12)
            popup:Show()
        else
            popup:Hide()
        end
        -- Your position on whichever map is being viewed
        t = t + dt
        if t < 0.2 then return end
        t = 0
        local mapID = wm.GetMapID and wm:GetMapID()
        local px, py = PlayerPos(mapID)
        mapLine:SetValue("You: " .. Format(px, py))
        LayoutWorldPins()
    end)

    -- Double-click a spot on the map to add a waypoint there. (Both clicks must
    -- land on the same spot of the same map: on a continent the first click
    -- opens the zone instead.)
    if wm.ScrollContainer then
        local lastClick
        wm.ScrollContainer:HookScript("OnMouseUp", function(_, button)
            if button ~= "LeftButton" then return end
            local x, y = CursorOnMap()
            local mapID = wm:GetMapID()
            if not x or not mapID then lastClick = nil; return end
            local now = GetTime()
            if lastClick and now - lastClick.t <= 0.4 and lastClick.map == mapID
                and math.abs(x - lastClick.x) < 0.01 and math.abs(y - lastClick.y) < 0.01 then
                lastClick = nil
                AskForNote(mapID, x, y)
            else
                lastClick = { t = now, map = mapID, x = x, y = y }
            end
        end)
    end
end


------------------------------------------------------------
-- 3) Waypoints: your own notes on the world map and minimap
------------------------------------------------------------
-- Add one with /way 26 42 note, or double-click the world map. Hover a pin for
-- its note and distance; right-click it to remove it.

-- The Aether waypoint star (our own art, white, tinted in game): a navy
-- disc, a thin gold ring and a gold star, like the unit frame crests.
local WP_MEDIA = "Interface\\AddOns\\AetherCoords\\Media\\"
local WP_GOLD = { 1, 0.69, 0 }                -- Aether gold
local WP_NAVY = { 0.075, 0.157, 0.29, 0.92 }  -- the title strips' navy
local WORLD_PIN_SIZE, MINI_PIN_SIZE = 18, 14
local GLOW_TEXTURE = WP_MEDIA .. "wp_glow"   -- round soft glow (tools/gen_wp_glow.py)
local waypointsDirty = true

local function Waypoints()
    db.waypoints = db.waypoints or {}
    return db.waypoints
end

local function ZoneName(mapID)
    local info = mapID and C_Map.GetMapInfo and C_Map.GetMapInfo(mapID)
    return info and info.name or "?"
end

-- World position (yards) of a spot on a map: instance, x, y.
local function WorldOf(mapID, x, y)
    if not (C_Map.GetWorldPosFromMapPos and CreateVector2D) then return end
    local ok, instance, pos = pcall(C_Map.GetWorldPosFromMapPos, mapID, CreateVector2D(x, y))
    if ok and instance and pos then return instance, pos.x, pos.y end
end

-- Where a waypoint falls on another map (0 to 1), or nil if it isn't on it.
local function OnMap(wp, mapID)
    if wp.map == mapID then return wp.x, wp.y end
    if not C_Map.GetMapPosFromWorldPos then return end
    local instance, wx, wy = WorldOf(wp.map, wp.x, wp.y)
    if not instance then return end
    local ok, _, pos = pcall(C_Map.GetMapPosFromWorldPos, instance, CreateVector2D(wx, wy), mapID)
    if not ok or not pos then return end
    local x, y = pos:GetXY()
    if x and y and x >= 0 and x <= 1 and y >= 0 and y <= 1 then return x, y end
end

local function PlayerWorld()
    local mapID = C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit("player")
    local x, y = PlayerPos(mapID)
    if x then return WorldOf(mapID, x, y) end
end

local function YardsTo(wp)
    local inst, px, py = PlayerWorld()
    local winst, wx, wy = WorldOf(wp.map, wp.x, wp.y)
    if inst and winst == inst then return math.sqrt((wx - px) ^ 2 + (wy - py) ^ 2) end
end

local function Describe(wp)
    local note = (wp.note and wp.note ~= "") and (wp.note .. " ") or ""
    return note .. "(" .. ZoneName(wp.map) .. " " .. Format(wp.x, wp.y) .. ")"
end

local function AddWaypoint(mapID, x, y, note)
    local wp = { map = mapID, x = x, y = y, note = strtrim(note or "") }
    table.insert(Waypoints(), wp)
    waypointsDirty = true
    Print("Waypoint added: " .. Describe(wp))
end

local function RemoveWaypoint(wp)
    for i, w in ipairs(Waypoints()) do
        if w == wp then
            table.remove(Waypoints(), i)
            waypointsDirty = true
            GameTooltip:Hide()
            Print("Waypoint removed: " .. Describe(wp))
            return
        end
    end
end

local function PinTooltip(pin)
    local wp = pin.wp
    if not wp then return end
    GameTooltip:SetOwner(pin, pin.tooltipAnchor or "ANCHOR_RIGHT")
    GameTooltip:AddLine((wp.note and wp.note ~= "") and wp.note or "Waypoint", 1, 0.69, 0)
    GameTooltip:AddLine(ZoneName(wp.map) .. "  " .. Format(wp.x, wp.y), 1, 1, 1)
    local yards = YardsTo(wp)
    if yards then GameTooltip:AddLine(format("%d yards away", yards), 0.7, 0.7, 0.7) end
    GameTooltip:AddLine("Right-click to remove", 0.5, 0.5, 0.5)
    GameTooltip:Show()
end

-- The Aether star (gold star in a gold ring on navy), with a soft gold glow that slowly pulses, so it
-- stands out on any part of the map.
local function MakeWaypointPin(parent, size)
    local pin = CreateFrame("Button", nil, parent)
    pin.isAetherPin = true
    pin:SetSize(size, size)

    local glow = pin:CreateTexture(nil, "BACKGROUND")
    glow:SetTexture(GLOW_TEXTURE)
    glow:SetBlendMode("ADD")
    glow:SetVertexColor(1, 0.69, 0)   -- Aether gold
    glow:SetPoint("CENTER")
    glow:SetSize(size * 2.4, size * 2.4)   -- brightest at the disc's edge, fading out round

    -- Disc, ring and star: three white images tinted navy and Aether gold.
    for _, part in ipairs({ { "wp_disc", "BORDER", WP_NAVY }, { "wp_ring", "ARTWORK", WP_GOLD },
                            { "wp_star", "OVERLAY", WP_GOLD } }) do
        local t = pin:CreateTexture(nil, part[2])
        t:SetAllPoints()
        t:SetTexture(WP_MEDIA .. part[1])
        local c = part[3]
        t:SetVertexColor(c[1], c[2], c[3], c[4] or 1)
    end

    if glow.CreateAnimationGroup then
        local pulse = glow:CreateAnimationGroup()
        pulse:SetLooping("BOUNCE")
        local fade = pulse:CreateAnimation("Alpha")
        fade:SetFromAlpha(1)
        fade:SetToAlpha(0.35)
        fade:SetDuration(0.9)
        if fade.SetSmoothing then fade:SetSmoothing("IN_OUT") end
        pulse:Play()
    end
    pin:RegisterForClicks("RightButtonUp")
    pin:SetScript("OnClick", function(self, button)
        if button == "RightButton" then RemoveWaypoint(self.wp) end
    end)
    pin:SetScript("OnEnter", PinTooltip)
    pin:SetScript("OnLeave", function() GameTooltip:Hide() end)
    return pin
end

-- Double-click on the world map: ask for a note, then add the waypoint.
-- (Our own small box, not WoW's shared popups: an addon using those can get
-- Blizzard's own protected popups blocked.)
local noteBox

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
    local MEDIA, WHITE = "Interface\\AddOns\\AetherCoords\\Media\\", "Interface\\Buttons\\WHITE8X8"
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

local function GetNoteBox()
    if noteBox then return noteBox end
    local f = CreateFrame("Frame", "AetherCoordsNoteBox", UIParent, "BackdropTemplate")
    f:SetSize(300, 112)
    f:SetPoint("CENTER", UIParent, "CENTER", 0, 120)
    f:SetFrameStrata("DIALOG")
    f:EnableMouse(true)
    f:Hide()
    if f.SetBackdrop then
        f:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8X8", edgeFile = "Interface\\Buttons\\WHITE8X8", edgeSize = 1 })
        f:SetBackdropColor(0.05, 0.05, 0.08, 0.95)
        f:SetBackdropBorderColor(0.3, 0.7, 1, 0.8)
    end
    AetherDecorate(f, 28)

    f.title = f:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    f.title:SetPoint("TOP", 0, -10)
    local label = f:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    label:SetPoint("TOPLEFT", 16, -32)
    label:SetText("Note (optional):")

    local box = CreateFrame("EditBox", nil, f, "InputBoxTemplate")
    box:SetSize(262, 20)
    box:SetPoint("TOPLEFT", 22, -46)
    box:SetAutoFocus(true)
    box:SetMaxLetters(80)
    f.box = box

    local function Accept()
        local d = f.data
        f:Hide()
        if d then AddWaypoint(d.map, d.x, d.y, box:GetText() or "") end
    end
    box:SetScript("OnEnterPressed", Accept)
    box:SetScript("OnEscapePressed", function() f:Hide() end)

    local add = AetherButton(f)
    add:SetSize(100, 22)
    add:SetPoint("BOTTOMRIGHT", f, "BOTTOM", -6, 10)
    add:SetText("Add")
    add:SetScript("OnClick", Accept)
    local cancel = AetherButton(f)
    cancel:SetSize(100, 22)
    cancel:SetPoint("BOTTOMLEFT", f, "BOTTOM", 6, 10)
    cancel:SetText("Cancel")
    cancel:SetScript("OnClick", function() f:Hide() end)

    noteBox = f
    return f
end

AskForNote = function(mapID, x, y)
    local f = GetNoteBox()
    f.data = { map = mapID, x = x, y = y }
    f.title:SetText("Waypoint at " .. ZoneName(mapID) .. " " .. Format(x, y))
    f.box:SetText("")
    f:Show()
    f.box:SetFocus()
end

-- World map pins
local worldPins = {}
local lastMap, lastScale

local function CanvasScale(sc)
    if sc.GetCanvasScale then
        local ok, s = pcall(sc.GetCanvasScale, sc)
        if ok and s and s > 0 then return s end
    end
    return 1
end

-- Above everything else on the map canvas (zone maps add layers of their own).
local function TopLevel(canvas)
    local top = canvas:GetFrameLevel()
    for _, child in ipairs({ canvas:GetChildren() }) do
        if not child.isAetherPin then
            local level = child:GetFrameLevel()
            if level and level > top then top = level end
        end
    end
    return math.min(top + 25, 9000)
end

LayoutWorldPins = function()
    local wm = WorldMapFrame
    local sc = wm and wm.ScrollContainer
    local canvas = sc and sc.Child
    if not canvas then return end
    local mapID = wm:GetMapID()
    local scale = CanvasScale(sc)
    if not waypointsDirty and mapID == lastMap and scale == lastScale then return end
    waypointsDirty, lastMap, lastScale = false, mapID, scale

    local w, h = canvas:GetWidth(), canvas:GetHeight()
    local pinScale = 1 / scale              -- same size on screen however far you zoom
    local level = TopLevel(canvas)
    local used = 0
    for _, wp in ipairs(Waypoints()) do
        local x, y = OnMap(wp, mapID)
        if x then
            used = used + 1
            local pin = worldPins[used]
            if not pin then
                pin = MakeWaypointPin(canvas, WORLD_PIN_SIZE)
                worldPins[used] = pin
            end
            pin.wp = wp
            pin:SetScale(pinScale)
            pin:SetFrameLevel(level)
            pin:ClearAllPoints()
            pin:SetPoint("CENTER", canvas, "TOPLEFT", x * w / pinScale, -y * h / pinScale)
            pin:Show()
        end
    end
    for i = used + 1, #worldPins do worldPins[i]:Hide() end
end

-- Minimap pins: follow you, turn with "Rotate Minimap", scale with zoom.
-- Waypoints past the edge sit on the rim, faded, pointing the way.
local MINIMAP_YARDS = {   -- minimap diameter in yards at each zoom level
    outdoor = { [0] = 466 + 2/3, 400, 333 + 1/3, 266 + 2/3, 200, 133 + 1/3 },
    indoor  = { [0] = 300, 240, 180, 120, 80, 50 },
}
local miniPins = {}

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
    local list = Waypoints()
    local used = 0
    local inst, px, py
    if #list > 0 and Minimap and Minimap:IsVisible() then inst, px, py = PlayerWorld() end
    if inst then
        local width = Minimap:GetWidth()
        local perYard = width / MinimapDiameter()
        local limit = width / 2 - MINI_PIN_SIZE / 2
        local round = not (GetMinimapShape and GetMinimapShape() ~= "ROUND")
        local sin, cos
        if GetCVar("rotateMinimap") == "1" and GetPlayerFacing then
            local facing = GetPlayerFacing()
            if facing and not (issecretvalue and issecretvalue(facing)) then
                sin, cos = math.sin(-facing), math.cos(-facing)
            end
        end
        for _, wp in ipairs(list) do
            local winst, wx, wy = WorldOf(wp.map, wp.x, wp.y)
            if winst == inst then
                -- World x points north and world y points west.
                local east, north = (py - wy) * perYard, (wx - px) * perYard
                if sin then east, north = east * cos - north * sin, east * sin + north * cos end
                local alpha = 1
                if round then
                    local dist = math.sqrt(east * east + north * north)
                    if dist > limit then
                        east, north, alpha = east / dist * limit, north / dist * limit, 0.6
                    end
                else
                    local big = math.max(math.abs(east), math.abs(north))
                    if big > limit then east, north, alpha = east / big * limit, north / big * limit, 0.6 end
                end
                used = used + 1
                local pin = miniPins[used]
                if not pin then
                    pin = MakeWaypointPin(Minimap, MINI_PIN_SIZE)
                    pin.tooltipAnchor = "ANCHOR_LEFT"
                    pin:SetFrameLevel(Minimap:GetFrameLevel() + 6)
                    miniPins[used] = pin
                end
                pin.wp = wp
                pin:SetAlpha(alpha)
                pin:ClearAllPoints()
                pin:SetPoint("CENTER", Minimap, "CENTER", east, north)
                pin:Show()
            end
        end
    end
    for i = used + 1, #miniPins do miniPins[i]:Hide() end
end

local miniDriver = CreateFrame("Frame")
miniDriver:SetScript("OnUpdate", function()
    if db then LayoutMiniPins() end
end)

-- Finds a zone by name (for /way Thousand Needles 26 42).
local function FindZone(name)
    name = strlower(strtrim(name))
    local here = C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit("player")
    local root = here
    while root do
        local info = C_Map.GetMapInfo(root)
        if not info or not info.parentMapID or info.parentMapID == 0 then break end
        root = info.parentMapID
    end
    if not root or not C_Map.GetMapChildrenInfo then return nil end
    local best
    for _, info in ipairs(C_Map.GetMapChildrenInfo(root, nil, true) or {}) do
        local n = strlower(info.name or "")
        if n == name then return info.mapID end
        if not best and n:find(name, 1, true) then best = info.mapID end
    end
    return best
end

------------------------------------------------------------
-- Events and slash commands
------------------------------------------------------------
local f = CreateFrame("Frame")
f:RegisterEvent("ADDON_LOADED")
f:RegisterEvent("PLAYER_LOGIN")
f:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" and arg1 == ADDON then
        -- MapCoordsDB holds settings from before the rename (present only right after
        -- migrating). Then the per-character copy (WoW Forever may not load account-wide
        -- settings back), then the account-wide one.
        local saved
        local sources = { MapCoordsDB, AetherCoordsCharDB, AetherCoordsDB }
        for i = 1, 3 do              -- not ipairs: it stops at the first nil
            local source = sources[i]
            if type(source) == "table" and next(source) then saved = source; break end
        end
        saved = saved or {}
        for k, v in pairs(defaults) do
            if saved[k] == nil then saved[k] = v end
        end
        db = saved
        AetherCoordsDB, AetherCoordsCharDB = db, db
        MapCoordsDB = nil
    elseif event == "ADDON_LOADED" and arg1 == "Blizzard_WorldMap" then
        SetupWorldMap()
    elseif event == "PLAYER_LOGIN" then
        CreateMini()
        SetupWorldMap()  -- if the world map is already loaded
    end
end)

SLASH_AETHERWAY1, SLASH_AETHERWAY2 = "/way", "/aetherway"
SlashCmdList.AETHERWAY = function(input)
    input = strtrim(input or "")
    local lower = strlower(input)
    local list = Waypoints()
    if lower == "list" then
        if #list == 0 then Print("No waypoints. Add one with /way 26 42 note.") return end
        for i, wp in ipairs(list) do print(format("  %d. %s", i, Describe(wp))) end
        return
    elseif lower == "clear" then
        wipe(list); waypointsDirty = true
        Print("All waypoints removed.")
        return
    elseif lower:match("^remove %d+$") then
        local wp = list[tonumber(lower:match("%d+"))]
        if wp then RemoveWaypoint(wp) else Print("No waypoint with that number. /way list shows them.") end
        return
    end
    -- [zone] x y [note]
    local zone, x, y, note = input:match("^(.-)%s*(%d+%.?%d*)[%s,]+(%d+%.?%d*)%s*(.*)$")
    x, y = tonumber(x), tonumber(y)
    if x and y and x <= 100 and y <= 100 then
        local mapID
        if zone and zone ~= "" then
            mapID = FindZone(zone)
            if not mapID then Print("Couldn't find a zone called \"" .. zone .. "\".") return end
        elseif WorldMapFrame and WorldMapFrame:IsShown() then
            mapID = WorldMapFrame:GetMapID()     -- the map you're looking at
        else
            mapID = C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit("player")
        end
        if not mapID then Print("Couldn't tell which zone you're in.") return end
        AddWaypoint(mapID, x / 100, y / 100, note)
        return
    end
    Print("Waypoints:")
    print("  /way 26 42 note          add one in your zone (or the map you have open)")
    print("  /way Thousand Needles 26 42 note   add one in another zone")
    print("  /way list                list them")
    print("  /way remove 2            remove number 2")
    print("  /way clear               remove them all")
    print("  Double-click the world map to add one there. Right-click a pin to remove it.")
end

SLASH_AETHERCOORDS1, SLASH_AETHERCOORDS2 = "/aethercoords", "/mc"
SlashCmdList.AETHERCOORDS = function(input)
    local cmd, val = strsplit(" ", strlower(strtrim(input or "")), 2)
    if cmd == "decimals" and tonumber(val) then
        db.decimals = math.max(0, math.min(2, math.floor(tonumber(val))))
        Print("Decimal places: " .. db.decimals)
    elseif cmd == "minimap" then
        db.minimap = (val ~= "off"); mini:SetShown(db.minimap)
        Print("Minimap readout " .. (db.minimap and "on" or "off"))
    elseif cmd == "popup" then
        db.popup = (val ~= "off")
        Print("Map cursor popup " .. (db.popup and "on" or "off"))
    elseif cmd == "reset" then
        db.point = nil; PlaceMini()
        Print("Readout moved back under the minimap.")
    else
        Print("Commands:")
        print("  /mc decimals 0-2     coordinate precision (now " .. db.decimals .. ")")
        print("  /mc minimap on|off   readout under the minimap")
        print("  /mc popup on|off     cursor popup on the world map")
        print("  /mc reset            move the readout back under the minimap")
        print("  Shift-drag the readout to move it.")
        print("  /way for waypoints (notes on the world map and minimap).")
    end
end

-- ==========================================
-- FOR OTHER AETHER ADDONS
-- ==========================================
-- AetherLedger adds a waypoint on the quest giver it sends you to.
AetherCoords_API = {
    -- x, y from 0 to 1. Returns the waypoint (pass it to RemoveWaypoint later).
    AddWaypoint = function(mapID, x, y, note)
        if not db or not mapID or not x or not y then return nil end
        for _, wp in ipairs(Waypoints()) do       -- already there: don't double up
            if wp.map == mapID and math.abs(wp.x - x) < 0.002 and math.abs(wp.y - y) < 0.002 then return wp end
        end
        AddWaypoint(mapID, x, y, note)
        local list = Waypoints()
        return list[#list]
    end,
    RemoveWaypoint = function(wp)
        if db and wp then
            for _, w in ipairs(Waypoints()) do
                if w == wp then RemoveWaypoint(wp); return end
            end
        end
    end,
}
