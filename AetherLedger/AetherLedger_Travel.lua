-- ==========================================
-- AetherLedger travel directions
-- "Take me there" plans a route to a quest giver and shows it, step by step,
-- in a small window that ticks steps off as you go:
--   walk to a zeppelin or boat and ride it (other continent),
--   walk to a flight master you know and fly (when that's clearly shorter),
--   walk the rest, with the distance and direction counting down.
-- Flight paths come from AetherPathfinder (the ones this character knows).
-- While a flight is part of the plan, the flight map makes your destination
-- glow. The window only updates while it's open (twice a second, one
-- position read), and closes itself shortly after you arrive.
-- ==========================================

local PREFIX = "|cff4da6ffAetherLedger:|r "

-- Zeppelins and boats. Spots are map coordinates (0-100) of the tower or dock.
-- side: "H" Horde, "A" Alliance, "" anyone.
local TRANSPORTS = {
    { kind = "zeppelin", side = "H",
      a = { 1411, 50.9, 13.8, "the zeppelin tower north of Orgrimmar", "Orgrimmar" },
      b = { 1420, 60.7, 58.8, "the zeppelin tower outside Undercity", "Undercity" } },
    { kind = "zeppelin", side = "H",
      a = { 1411, 50.6, 12.6, "the zeppelin tower north of Orgrimmar", "Orgrimmar" },
      b = { 1434, 31.5, 29.1, "the zeppelin tower at Grom'gol", "Grom'gol" } },
    { kind = "zeppelin", side = "H",
      a = { 1420, 61.9, 59.0, "the zeppelin tower outside Undercity", "Undercity" },
      b = { 1434, 31.6, 30.1, "the zeppelin tower at Grom'gol", "Grom'gol" } },
    { kind = "boat", side = "",
      a = { 1413, 63.7, 38.6, "the docks in Ratchet", "Ratchet" },
      b = { 1434, 25.9, 73.1, "the docks in Booty Bay", "Booty Bay" } },
    { kind = "boat", side = "A",
      a = { 1445, 71.6, 56.4, "the docks in Theramore", "Theramore" },
      b = { 1437, 5.0, 63.5, "the docks in Menethil Harbor", "Menethil Harbor" } },
    { kind = "boat", side = "A",
      a = { 1439, 32.4, 43.8, "the docks in Auberdine", "Auberdine" },
      b = { 1437, 4.6, 57.1, "the docks in Menethil Harbor", "Menethil Harbor" } },
}

local ARRIVED_YARDS = 20      -- close enough to the quest giver
local REACHED_YARDS = 35      -- close enough to a flight master or dock
local FLY_RATIO = 0.6         -- fly when walk-to-flight + walk-from-landing is under 60% of walking all the way

local function MapName(map)
    local info = map and C_Map.GetMapInfo(map)
    return info and info.name or "?"
end

-- World spot (yards) of a map position (0-1): { inst, x, y }.
local function World(map, x, y)
    if not (C_Map.GetWorldPosFromMapPos and CreateVector2D) then return nil end
    local ok, inst, pos = pcall(C_Map.GetWorldPosFromMapPos, map, CreateVector2D(x, y))
    if not ok or not inst or not pos then return nil end
    local wx, wy = pos.x, pos.y
    if issecretvalue and (issecretvalue(wx) or issecretvalue(inst)) then return nil end
    return { inst = inst, x = wx, y = wy }
end

local function PlayerWorld()
    local map = C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit("player")
    local pos = map and C_Map.GetPlayerMapPosition(map, "player")
    if not pos then return nil end
    local x, y = pos:GetXY()
    if not x or (x == 0 and y == 0) then return nil end
    return World(map, x, y)
end

local function Dist(a, b)
    if not a or not b or a.inst ~= b.inst then return math.huge end
    return math.sqrt((a.x - b.x) ^ 2 + (a.y - b.y) ^ 2)
end

-- Compass direction from a to b. World x grows north, world y grows west.
local DIRS = { "north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest" }
local function Direction(a, b)
    local north, east = b.x - a.x, -(b.y - a.y)
    local angle = math.deg(math.atan2(east, north)) % 360
    return DIRS[math.floor((angle + 22.5) / 45) % 8 + 1]
end

local function MySide()
    local f = UnitFactionGroup("player")
    return f == "Horde" and "H" or (f == "Alliance" and "A" or "")
end

-- ==========================================
-- PLANNING
-- ==========================================

-- Known flight masters as { name, map, x, y, w = world spot }.
local function KnownFlights()
    local list = {}
    if not (AetherPathfinder_API and AetherPathfinder_API.FlightMasters) then return list end
    for _, fm in ipairs(AetherPathfinder_API.FlightMasters()) do
        if fm.known then
            local w = World(fm.map, fm.x, fm.y)
            if w then fm.w = w; list[#list + 1] = fm end
        end
    end
    return list
end

local function Nearest(list, spot)
    local best, bestDist
    for _, item in ipairs(list) do
        local d = Dist(item.w, spot)
        if d < (bestDist or math.huge) then best, bestDist = item, d end
    end
    return best, bestDist
end

-- Steps to get from spot "from" to spot "to" on the same continent.
local function OverLand(steps, from, to, toLabel, flights)
    local fs, toFs = Nearest(flights, from)
    local ft, fromFt = Nearest(flights, to)
    local direct = Dist(from, to)
    if fs and ft and fs ~= ft and toFs + fromFt < direct * FLY_RATIO then
        if toFs > REACHED_YARDS then
            steps[#steps + 1] = { kind = "walk", w = fs.w, text = string.format("Go to %s, the flight master in %s (%.0f, %.0f)",
                fs.name, MapName(fs.map), fs.x * 100, fs.y * 100) }
        end
        steps[#steps + 1] = { kind = "fly", w = ft.w, flight = ft, text = "Fly to " .. MapName(ft.map) .. " (" .. ft.name .. ")" }
    end
    steps[#steps + 1] = { kind = "walk", w = to, final = (toLabel ~= nil), text = toLabel or "" }
end

-- A route to dest { name, map, x, y (0-1) }. Returns steps, or nil and why not.
local function Plan(dest)
    local here = PlayerWorld()
    if not here then return nil, "couldn't tell where you are (try again outside)" end
    local target = World(dest.map, dest.x, dest.y)
    if not target then return nil, "couldn't place " .. dest.name .. " on the map" end
    local flights = KnownFlights()
    local steps = {}
    local label = string.format("Walk to %s in %s (%.0f, %.0f)", dest.name, MapName(dest.map), dest.x * 100, dest.y * 100)
    if here.inst == target.inst then
        OverLand(steps, here, target, label, flights)
        return steps, nil, target
    end
    -- Another continent: pick the zeppelin or boat that makes the trip shortest.
    local side, best, bestCost = MySide(), nil, nil
    for _, t in ipairs(TRANSPORTS) do
        if t.side == "" or t.side == side then
            for _, dir in ipairs({ { t.a, t.b }, { t.b, t.a } }) do
                local from = World(dir[1][1], dir[1][2] / 100, dir[1][3] / 100)
                local to = World(dir[2][1], dir[2][2] / 100, dir[2][3] / 100)
                if from and to and from.inst == here.inst and to.inst == target.inst then
                    local cost = Dist(here, from) + Dist(to, target)
                    if not bestCost or cost < bestCost then
                        best, bestCost = { t = t, from = dir[1], to = dir[2], fromW = from, toW = to }, cost
                    end
                end
            end
        end
    end
    if not best then return nil, "no zeppelin or boat route known to " .. MapName(dest.map) end
    OverLand(steps, here, best.fromW, nil, flights)
    local last = steps[#steps]
    last.text = "Go to " .. best.from[4] .. " (" .. MapName(best.from[1]) .. string.format(" %.0f, %.0f)", best.from[2], best.from[3])
    steps[#steps + 1] = { kind = "ride", inst = target.inst, w = best.toW,
                          text = "Take the " .. best.t.kind .. " to " .. best.to[5] }
    OverLand(steps, best.toW, target, label, flights)
    return steps, nil, target
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

-- ==========================================
-- WINDOW
-- ==========================================

local win, trip
local tick = 0

-- Fades like AetherMeter (and uses its opacity settings when it's installed):
-- solid for 10 seconds after you click or drag it, or a step is done,
-- then back to the meter's in-combat or out-of-combat transparency.
local WAKE_SECONDS = 10
local awakeUntil = 0

local SHOW_ARRIVED, FADE_SECONDS = 2.5, 1.5   -- "You're there!" stays this long, then fades out

local function ApplyAlpha()
    if not win then return end
    if trip and trip.doneAt then                 -- arrived: hold, then fade away
        local t = GetTime() - trip.doneAt
        win:SetAlpha(t < SHOW_ARRIVED and 1 or math.max(0, 1 - (t - SHOW_ARRIVED) / FADE_SECONDS))
        return
    end
    if GetTime() < awakeUntil then win:SetAlpha(1); return end
    local m = AetherMeterDB or {}
    local alpha = InCombatLockdown() and (m.opacityInCombat or 0.8) or (m.opacityOutCombat or 0.3)
    win:SetAlpha(alpha)
end

local function Wake()
    awakeUntil = GetTime() + WAKE_SECONDS
    ApplyAlpha()
end

local function BuildWindow()
    win = CreateFrame("Frame", "AetherLedgerTravel", UIParent, "BackdropTemplate")
    win:SetSize(300, 100)
    win:SetPoint("RIGHT", UIParent, "RIGHT", -40, 120)
    win:SetFrameStrata("MEDIUM")
    win:SetMovable(true)
    win:SetClampedToScreen(true)
    win:EnableMouse(true)
    win:RegisterForDrag("LeftButton")
    win:SetScript("OnDragStart", function(self) Wake(); self:StartMoving() end)
    win:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        if AetherLedger_SavePos then AetherLedger_SavePos(self, "travel") end
        Wake()
    end)
    win:SetScript("OnMouseDown", Wake)
    if win.SetBackdrop then
        win:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        win:SetBackdropColor(0.05, 0.06, 0.09, 0.88)
        win:SetBackdropBorderColor(0.3, 0.65, 1, 0.8)
    end
    AetherDecorate(win, 26)
    win.title = win:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    win.title:SetPoint("TOPLEFT", 10, -8)
    win.title:SetPoint("RIGHT", win, "RIGHT", -26, 0)
    win.title:SetJustifyH("LEFT")
    win.body = win:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    win.body:SetPoint("TOPLEFT", win.title, "BOTTOMLEFT", 0, -6)
    win.body:SetPoint("RIGHT", win, "RIGHT", -10, 0)
    win.body:SetJustifyH("LEFT")
    win.body:SetSpacing(3)
    local close = AetherClose(win)
    close:SetScript("OnClick", function() AetherLedger_Travel.Stop() end)
    win:SetScript("OnUpdate", function(_, elapsed)
        tick = tick + elapsed
        if tick < 0.5 then return end
        tick = 0
        AetherLedger_Travel.Update()
        ApplyAlpha()
    end)
    win:Hide()
end

local function Render(extra)
    if not trip then return end
    local lines = {}
    for i, step in ipairs(trip.steps) do
        local mark
        if i < trip.at then mark = "|cff33dd66done|r  |cff888888" .. step.text .. "|r"
        elseif i == trip.at then mark = "|cffffd100> " .. step.text .. "|r"
        else mark = "|cffbbbbbb  " .. step.text .. "|r" end
        lines[#lines + 1] = mark
    end
    if extra then lines[#lines + 1] = " "; lines[#lines + 1] = extra end
    win.title:SetText("To " .. trip.dest.name .. " (" .. MapName(trip.dest.map) .. ")")
    win.body:SetText(table.concat(lines, "\n"))
    win:SetHeight(win.body:GetStringHeight() + 40)
end

-- ==========================================
-- FLIGHT MAP GLOW
-- ==========================================

local glow
local function GlowOn(button)
    if not glow then
        glow = CreateFrame("Frame", nil, UIParent)
        glow:SetFrameStrata("TOOLTIP")
        local t = glow:CreateTexture(nil, "OVERLAY")
        t:SetAllPoints()
        t:SetTexture("Interface\\Buttons\\UI-ActionButton-Border")
        t:SetBlendMode("ADD")
        t:SetVertexColor(0.2, 1, 0.4)
        local anim = glow:CreateAnimationGroup()
        anim:SetLooping("BOUNCE")
        local a = anim:CreateAnimation("Alpha")
        a:SetFromAlpha(1); a:SetToAlpha(0.25); a:SetDuration(0.6)
        glow.anim = anim
    end
    glow:ClearAllPoints()
    glow:SetPoint("CENTER", button, "CENTER")
    glow:SetSize(math.max(40, (button:GetWidth() or 20) * 2.6), math.max(40, (button:GetHeight() or 20) * 2.6))
    glow:Show()
    glow.anim:Play()
end

local function GlowOff()
    if glow then glow.anim:Stop(); glow:Hide() end
end

-- On the flight map, find the node for the flight master you're flying to and make it glow.
local function MarkFlightNode()
    local step = trip and trip.steps[trip.at]
    local fly = step and step.kind == "fly" and step
    if not fly then
        for i = trip and trip.at or 1, trip and #trip.steps or 0 do
            if trip.steps[i].kind == "fly" then fly = trip.steps[i]; break end
        end
    end
    if not fly or not (NumTaxiNodes and TaxiNodePosition) then return end
    local taxiMap = (GetTaxiMapID and GetTaxiMapID()) or nil
    local best, bestDist
    for i = 1, NumTaxiNodes() or 0 do
        local x, y = TaxiNodePosition(i)
        local w = x and taxiMap and World(taxiMap, x, y)
        local d = w and Dist(w, fly.w) or math.huge
        if d < (bestDist or math.huge) then best, bestDist = i, d end
    end
    if not best or bestDist > 200 then return end
    local name = TaxiNodeName and TaxiNodeName(best)
    if name then print(PREFIX .. "fly to |cff33dd66" .. name .. "|r.") end
    local button = _G["TaxiButton" .. best]
    if not button and FlightMapFrame and FlightMapFrame.EnumerateAllPins then
        pcall(function()
            for pin in FlightMapFrame:EnumerateAllPins() do
                if pin.taxiNodeData and pin.taxiNodeData.slotIndex == best then button = pin end
            end
        end)
    end
    if button then GlowOn(button) end
end

-- ==========================================
-- PROGRESS
-- ==========================================

AetherLedger_Travel = {}

function AetherLedger_Travel.Start(dest)
    if not win then BuildWindow() end
    local steps, why, target = Plan(dest)
    if not steps then
        print(PREFIX .. "no directions: " .. why .. ". The waypoint is on your map.")
        return
    end
    trip = { dest = dest, steps = steps, at = 1, target = target }
    if AetherLedger_SavedPos then AetherLedger_SavedPos(win, "travel") end
    win:Show()
    Wake()
    if AetherLedger_Tracker and AetherLedger_Tracker.Apply then AetherLedger_Tracker.Apply() end
    AetherLedger_Travel.Update()
end

-- The map you're headed to (the quest tracker shows its quests on the way).
function AetherLedger_Travel.DestMap()
    return trip and not trip.doneAt and trip.dest.map or nil
end

function AetherLedger_Travel.Stop()
    trip = nil
    GlowOff()
    if win then win:Hide() end
end

-- ==========================================
-- ARRIVAL FLASH
-- ==========================================
-- Big text in the upper middle of the screen (where zone names appear):
-- fades in, holds, fades out. No sound.
local flash
local FLASH_IN, FLASH_HOLD, FLASH_OUT = 0.25, 2, 1

local function Flash(title, subtitle)
    if not flash then
        flash = CreateFrame("Frame", "AetherLedgerFlash", UIParent)
        flash:SetSize(800, 90)
        flash:SetPoint("TOP", UIParent, "TOP", 0, -170)
        flash:SetFrameStrata("HIGH")
        flash.title = flash:CreateFontString(nil, "OVERLAY", "AetherFontNormalHuge")
        flash.title:SetPoint("TOP", 0, 0)
        flash.title:SetTextColor(0.45, 1, 0.5)
        flash.title:SetShadowOffset(2, -2)
        flash.sub = flash:CreateFontString(nil, "OVERLAY", "AetherFontNormalLarge")
        flash.sub:SetPoint("TOP", flash.title, "BOTTOM", 0, -6)
        flash.sub:SetTextColor(1, 0.82, 0)
        flash.sub:SetShadowOffset(1, -1)
        flash:SetScript("OnUpdate", function(self)
            local t = GetTime() - self.started
            local alpha
            if t < FLASH_IN then alpha = t / FLASH_IN
            elseif t < FLASH_IN + FLASH_HOLD then alpha = 1
            else alpha = 1 - (t - FLASH_IN - FLASH_HOLD) / FLASH_OUT end
            if alpha <= 0 then self:Hide() else self:SetAlpha(alpha) end
        end)
    end
    flash.title:SetText(title)
    flash.sub:SetText(subtitle or "")
    flash.started = GetTime()
    flash:SetAlpha(0)
    flash:Show()
end

-- You've reached the quest giver: flash it in the middle of the screen, take
-- the waypoint off the map, and close the directions window.
function AetherLedger_Travel.Arrived()
    if not trip or trip.doneAt then return end
    Flash("You're there!", trip.dest.name)
    local db = AetherLedgerDB
    if db and db.waypoint and AetherCoords_API then
        AetherCoords_API.RemoveWaypoint(db.waypoint)
        db.waypoint = nil
    end
    AetherLedger_Travel.Stop()
end

function AetherLedger_Travel.Update()
    if not trip then return end
    if trip.doneAt then
        if GetTime() - trip.doneAt >= SHOW_ARRIVED + FADE_SECONDS then AetherLedger_Travel.Stop() end
        return
    end
    local here = PlayerWorld()
    if not here then Render("(position unknown here)"); return end
    local onTaxi = UnitOnTaxi and UnitOnTaxi("player")
    -- Already at the quest giver (whatever way you came)?
    if Dist(here, trip.target) <= ARRIVED_YARDS then
        AetherLedger_Travel.Arrived()
        return
    end
    -- Skip ahead past every step that's done.
    local advanced = true
    while advanced and trip.at <= #trip.steps do
        advanced = false
        local step = trip.steps[trip.at]
        local nextStep = trip.steps[trip.at + 1]
        local done
        if step.kind == "ride" then
            done = here.inst == step.inst
        elseif step.kind == "fly" then
            done = not onTaxi and Dist(here, step.w) <= 150
        else
            done = Dist(here, step.w) <= REACHED_YARDS
                or (nextStep and nextStep.kind == "fly" and onTaxi)
                or (nextStep and nextStep.kind == "ride" and here.inst == nextStep.inst)
        end
        if done then
            trip.at = trip.at + 1
            advanced = true
            Wake()          -- a step is done: show the next one clearly
        end
    end
    local step = trip.steps[trip.at]
    local extra
    if step and step.kind == "walk" and step.w.inst == here.inst then
        extra = string.format("%.0f yards %s", Dist(here, step.w), Direction(here, step.w))
    elseif step and step.kind == "fly" then
        extra = onTaxi and "In flight..." or "Open the flight map: your stop glows green."
    elseif step and step.kind == "ride" then
        extra = "Waiting for the ride..."
    end
    Render(extra)
end

local events = CreateFrame("Frame")
for _, event in ipairs({ "TAXIMAP_OPENED", "TAXIMAP_CLOSED", "PLAYER_TARGET_CHANGED",
    "GOSSIP_SHOW", "QUEST_GREETING", "QUEST_DETAIL", "QUEST_PROGRESS" }) do
    pcall(events.RegisterEvent, events, event)
end

-- Is this unit the quest giver you're headed to?
local function IsDestination(unit)
    if not trip or trip.doneAt then return false end
    local ok, name = pcall(UnitName, unit)
    if not ok or not name or (issecretvalue and issecretvalue(name)) then return false end
    return name == trip.dest.name
end

events:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_TARGET_CHANGED" then
        if IsDestination("target") then AetherLedger_Travel.Arrived() end
    elseif event == "GOSSIP_SHOW" or event:find("^QUEST_") then
        if IsDestination("npc") or IsDestination("target") then AetherLedger_Travel.Arrived() end
    elseif event == "TAXIMAP_OPENED" then
        if trip then
            -- The flight map builds its buttons as it opens; look a moment later.
            C_Timer.After(0.2, function() pcall(MarkFlightNode) end)
        end
    else
        GlowOff()
    end
end)
