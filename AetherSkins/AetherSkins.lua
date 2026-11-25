-- ==========================================
-- AetherSkins: Blizzard's windows in the Aether look
-- First part: the minimap.
--  * Blizzard's ring art is hidden; a navy bevel ring takes its place, with
--    the four gold chevrons (12, 3, 6, 9, beveled like the ring) and a
--    soft blue glow.
--  * Light comes from the sun/moon button at the top-right: by day a gold
--    glow on the ring's inner wall across from it, by night a white one.
--    It follows the game's day and night (realm time), and changes over
--    by fading to the plain ring and back.
--  * The day/night button is our own: a navy button with an Aether-gold
--    sun or a pale moon. Click it for the calendar.
--  * Under the minimap: AetherCoords' coordinates pill just under the
--    bottom chevron, then a navy pill with the zone name and the clock
--    (yellow zone text turns Aether gold, the only yellow). The tracking
--    magnifier moves onto the ring across from the sun; the calendar button
--    (our sun opens it), the addon compartment and Forever's own minimap
--    coordinates are hidden.
-- Only looks change: the map, its pins and every button keep working.
-- /skins for options; /skins debug lists what was found and hidden.
-- ==========================================

local MEDIA = "Interface\\AddOns\\AetherSkins\\Media\\"
local GOLD  = { 1, 0.69, 0 }
local NAVY  = { 0.075, 0.157, 0.29 }
local BLUE  = { 0.3, 0.65, 1 }
local MOON  = { 0.88, 0.91, 0.96 }
local PREFIX = "|cff4da6ffAetherSkins:|r "
local K = 1.2821            -- ring art spans +-K map radii (tools/gen_skins_art.py)
local SUN_AT = { 0.718, 0.735 }   -- the day/night button, in map radii from the center (right, up)
local SUN_SIZE = 0.29             -- button diameter, in map diameters' halves (radii)
local FADE = 0.8                  -- seconds for each half of a day/night change

AetherSkinsDB = AetherSkinsDB or {}
local db
local function Print(s) print(PREFIX .. s) end
local function Obj(x) return type(x) == "table" and x or nil end   -- only real frames/regions
-- Some Blizzard frames are forbidden to addons (touching them errors); every
-- scan lists regions and children through these, which skip such frames.
local function SafeList(obj, method)
    if not obj or not obj[method] then return {} end
    if obj.IsForbidden then
        local okF, forb = pcall(obj.IsForbidden, obj)
        if not okF or forb then return {} end
    end
    local ok, list = pcall(function() return { obj[method](obj) } end)
    return ok and list or {}
end
local function Regions(obj) return SafeList(obj, "GetRegions") end
local function Children(obj) return SafeList(obj, "GetChildren") end
local function FontFile(weight)
    return (AETHER_FONT_DIR or "Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-") .. weight .. ".ttf"
end

-- ------------------------------------------
-- Day or night: the game's own answer when Forever offers it
-- (C_DateAndTime.IsDayTime), else the classic rule: day from 5:30 to 21:00
-- realm time, the hours Blizzard's sun/moon icon used.
-- ------------------------------------------
local DAWN = (_G.GAMETIME_DAWN or (5 * 60 + 30))
local DUSK = (_G.GAMETIME_DUSK or (21 * 60))
local forced            -- "day" / "night" from /skins day|night, for checking the look
local function IsDay()
    if forced then return forced == "day", "set by /skins" end
    if C_DateAndTime and C_DateAndTime.IsDayTime then
        local ok, v = pcall(C_DateAndTime.IsDayTime)
        if ok and type(v) == "boolean" then return v, "game (IsDayTime)" end
    end
    local h, m = GetGameTime()
    local t = (h or 12) * 60 + (m or 0)
    return t >= DAWN and t < DUSK, "realm clock"
end

-- ------------------------------------------
-- Hiding Blizzard's minimap art (kept hidden)
-- ------------------------------------------
local hidden, hiddenNames = {}, {}
local function Name(obj)
    local n = obj.GetDebugName and obj:GetDebugName() or (obj.GetName and obj:GetName())
    return n or tostring(obj)
end
local function HideRegion(obj)
    obj = Obj(obj)
    if not obj or hidden[obj] or not obj.SetAlpha then return end
    hidden[obj] = true
    hiddenNames[#hiddenNames + 1] = Name(obj)
    obj:SetAlpha(0)
    if obj.GetObjectType and obj:GetObjectType() ~= "Texture" and obj.EnableMouse and not obj:IsProtected() then
        obj:EnableMouse(false)
    end
end
local function Rehide()
    for obj in pairs(hidden) do if obj.GetAlpha and obj:GetAlpha() > 0 then obj:SetAlpha(0) end end
end
local ours = {}         -- everything AetherSkins creates is skipped by the scans
local function HideTextures(frame)
    frame = Obj(frame)
    if not frame or not frame.GetRegions then return end
    for _, r in ipairs(Regions(frame)) do
        if not ours[r] and r.GetObjectType and r:GetObjectType() == "Texture" then HideRegion(r) end
    end
end

-- ------------------------------------------
-- Pills: navy, rounded ends, a fine blue edge (shared with AetherCoords' look)
-- ------------------------------------------
local function Pill(parent, layer)
    local p = { parts = {} }
    local function T(file, sub, c, a)
        local t = parent:CreateTexture(nil, layer or "BACKGROUND", nil, sub)
        if file then t:SetTexture(MEDIA .. file) else t:SetColorTexture(1, 1, 1, 1) end
        t:SetVertexColor(c[1], c[2], c[3], a or 1)
        ours[t] = true; p.parts[#p.parts + 1] = t
        return t
    end
    p.l = T("pill_cap", -6, NAVY, 0.94); p.r = T("pill_cap", -6, NAVY, 0.94); p.m = T(nil, -6, NAVY, 0.94)
    p.r:SetTexCoord(1, 0, 0, 1)
    p.ll = T("pill_capline", -5, BLUE); p.rl = T("pill_capline", -5, BLUE); p.rl:SetTexCoord(1, 0, 0, 1)
    p.top = T(nil, -5, BLUE); p.bot = T(nil, -5, BLUE)
    function p:Place(anchor, padX, padY)
        local h = anchor:GetHeight() + 2 * (padY or 0)
        local cap = h / 2
        self.l:ClearAllPoints(); self.l:SetPoint("RIGHT", anchor, "LEFT", -(padX or 0) + cap, 0); self.l:SetSize(cap, h)
        self.r:ClearAllPoints(); self.r:SetPoint("LEFT", anchor, "RIGHT", (padX or 0) - cap, 0); self.r:SetSize(cap, h)
        self.ll:ClearAllPoints(); self.ll:SetAllPoints(self.l); self.rl:ClearAllPoints(); self.rl:SetAllPoints(self.r)
        self.m:ClearAllPoints(); self.m:SetPoint("TOPLEFT", self.l, "TOPRIGHT"); self.m:SetPoint("BOTTOMRIGHT", self.r, "BOTTOMLEFT")
        self.top:ClearAllPoints(); self.top:SetPoint("TOPLEFT", self.m, "TOPLEFT"); self.top:SetPoint("TOPRIGHT", self.m, "TOPRIGHT"); self.top:SetHeight(1)
        self.bot:ClearAllPoints(); self.bot:SetPoint("BOTTOMLEFT", self.m, "BOTTOMLEFT"); self.bot:SetPoint("BOTTOMRIGHT", self.m, "BOTTOMRIGHT"); self.bot:SetHeight(1)
    end
    return p
end
AetherSkins_Pill = Pill

-- ------------------------------------------
-- The minimap
-- ------------------------------------------
local ring, sunButton, state, topBar, zoneText, found = nil, nil, {}, nil, nil, {}
local PlaceTracking      -- defined with the top bar below; Layout calls it

local function Radius() return (Minimap:GetWidth() or 140) / 2 end

local function Layout()
    if not ring then return end
    local R = Radius()
    ring:SetSize(2 * K * R, 2 * K * R)
    for _, c in ipairs(ring.chevrons) do
        local s = 0.343 * R
        c.dark:SetSize(s, s); c.gold:SetSize(s, s)
        c.dark:ClearAllPoints(); c.dark:SetPoint("CENTER", Minimap, "CENTER", c.dx * 1.094 * R, c.dy * 1.094 * R)
        c.gold:ClearAllPoints(); c.gold:SetAllPoints(c.dark)
    end
    if PlaceTracking then PlaceTracking() end
    if AetherSkins_PlaceZonePill then AetherSkins_PlaceZonePill() end
    if sunButton then
        sunButton:SetSize(SUN_SIZE * R, SUN_SIZE * R)
        sunButton:ClearAllPoints()
        sunButton:SetPoint("CENTER", Minimap, "CENTER", SUN_AT[1] * R, SUN_AT[2] * R)
    end
end

-- Day/night: the lit ring and the icon fade out to the plain ring, swap, fade in.
local fader = CreateFrame("Frame")
local function ShowState(day, instant)
    if not ring then return end
    local function Apply(d)
        ring.lit:SetTexture(MEDIA .. (d and "ring_day" or "ring_night"))
        sunButton.icon:SetTexture(MEDIA .. (d and "ico_sun" or "ico_moon"))
        local c = d and GOLD or MOON
        sunButton.icon:SetVertexColor(c[1], c[2], c[3], 1)
    end
    state.day = day
    if instant then
        fader:SetScript("OnUpdate", nil); Apply(day); ring.lit:SetAlpha(1); sunButton.icon:SetAlpha(1); return
    end
    local t, swapped = 0, false
    fader:SetScript("OnUpdate", function(self, elapsed)
        t = t + elapsed
        local a
        if t < FADE then a = 1 - t / FADE
        else
            if not swapped then Apply(day); swapped = true end
            a = math.min(1, (t - FADE) / FADE)
        end
        ring.lit:SetAlpha(a); sunButton.icon:SetAlpha(0.25 + 0.75 * a)
        if t >= 2 * FADE then self:SetScript("OnUpdate", nil) end
    end)
end

local function CheckDay(instant)
    local day = IsDay()
    if day ~= state.day then ShowState(day, instant) end
end

local function GameTimeText()
    local h, m = GetGameTime()
    if GetCVarBool and GetCVarBool("timeMgrUseMilitaryTime") then return string.format("%02d:%02d", h, m) end
    local suffix = h < 12 and " AM" or " PM"
    local hh = h % 12; if hh == 0 then hh = 12 end
    return string.format("%d:%02d%s", hh, m, suffix)
end

local function MakeSunButton()
    local b = CreateFrame("Button", "AetherSkinsDayNight", Minimap)
    b:SetFrameStrata("MEDIUM")
    b:SetFrameLevel((Minimap:GetFrameLevel() or 1) + 9)
    local disc = b:CreateTexture(nil, "BACKGROUND"); disc:SetAllPoints(); disc:SetTexture(MEDIA .. "btn_disc")
    local icon = b:CreateTexture(nil, "ARTWORK")
    icon:SetPoint("CENTER"); icon:SetSize(1, 1)
    b:SetScript("OnSizeChanged", function(self, w) icon:SetSize(w * 0.75, w * 0.75) end)
    local hl = b:CreateTexture(nil, "HIGHLIGHT"); hl:SetAllPoints(); hl:SetTexture(MEDIA .. "btn_disc")
    hl:SetBlendMode("ADD"); hl:SetAlpha(0.3)
    b.icon = icon
    b:RegisterForClicks("LeftButtonUp")
    b:SetScript("OnClick", function()
        GameTooltip:Hide()
        if ToggleCalendar then ToggleCalendar()
        elseif Calendar_Toggle then Calendar_Toggle() end
    end)
    b:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_LEFT")
        GameTooltip:AddLine(IsDay() and "Day" or "Night", 1, 1, 1)
        GameTooltip:AddLine("Game time " .. GameTimeText(), 0.8, 0.8, 0.8)
        if ToggleCalendar or Calendar_Toggle then GameTooltip:AddLine("Click: calendar", 0.6, 0.6, 0.6) end
        GameTooltip:Show()
    end)
    b:SetScript("OnLeave", function() GameTooltip:Hide() end)
    for _, r in ipairs(Regions(b)) do ours[r] = true end
    ours[b] = true
    return b
end

-- Forever's own day/night icon sits on the ring at the top-right (about
-- 1 o'clock, a little higher than ours). It's found by where it is, never by
-- guessing its name: something button-sized whose center is on the ring
-- (0.8-1.35 map radii out) between 20 and 85 degrees (3 o'clock = 0, 12 = 90).
-- Frames and loose textures are both checked, a few levels deep under the
-- minimap and its cluster. The zone bar's buttons sit further out and aren't
-- touched; nor are protected frames or other addons' minimap buttons.
local ARC = { 20, 85 }; local DIST = { 0.8, 1.35 }; local AIM = { 57, 1.08 }
local function IsOtherAddonsButton(f)
    local n = f.GetName and f:GetName() or ""
    return n:find("^LibDBIcon") or (n:find("^Aether") and not n:find("^AetherSkins"))
end
local function Spot(obj)
    -- where obj's center is, in degrees and map radii from the minimap's center
    local mx, my = Minimap:GetCenter(); local cx, cy = obj:GetCenter()
    if not (mx and cx) then return end
    local s = obj:GetEffectiveScale() / Minimap:GetEffectiveScale()
    local dx, dy = cx * s - mx, cy * s - my
    local R = Radius()
    local w, h = obj:GetSize(); w, h = (w or 0) * s, (h or 0) * s
    return math.deg(math.atan2(dy, dx)), math.sqrt(dx * dx + dy * dy) / R, w / R, h / R
end
local function Candidate(obj)
    if ours[obj] or not obj.GetCenter or not obj:IsShown() then return end
    if obj.IsProtected and obj:IsProtected() then return end
    if obj.GetName and IsOtherAddonsButton(obj) then return end
    local ang, dist, w, h = Spot(obj)
    if not ang then return end
    if ang >= ARC[1] and ang <= ARC[2] and dist >= DIST[1] and dist <= DIST[2]
        and w > 0.15 and w < 0.8 and h > 0.15 and h < 0.8 then
        return math.abs(ang - AIM[1]) / 40 + math.abs(dist - AIM[2])   -- how far from the expected spot
    end
end
local function Scan(frame, depth, best)
    if not frame or depth > 3 then return best end
    if frame.GetRegions then
        for _, r in ipairs(Regions(frame)) do
            if r.GetObjectType and r:GetObjectType() == "Texture" then
                local score = Candidate(r)
                if score and (not best.score or score < best.score) then best.obj, best.score = r, score end
            end
        end
    end
    if frame.GetChildren then
        for _, f in ipairs(Children(frame)) do
            local score = Candidate(f)
            if score and (not best.score or score < best.score) then best.obj, best.score = f, score end
            if not ours[f] then Scan(f, depth + 1, best) end
        end
    end
    return best
end
local function FindDayNightIcon()
    if not Minimap:GetCenter() then return end
    local best = { }
    local named = Obj(_G.GameTimeFrame)
    if named and Candidate(named) then return named end      -- Blizzard's classic sun/moon, if it's on the ring
    for _, p in ipairs({ Minimap, Obj(_G.MinimapCluster) or false, Obj(_G.MinimapBackdrop) or false }) do
        if p then Scan(p, 1, best) end
    end
    return best.obj
end
-- for /skins debug: everything near the ring's top-right, with where it is
local function NearTopRight()
    local out = {}
    local function Look(frame, depth)
        if not frame or depth > 3 then return end
        if not frame.GetChildren then return end
        for _, f in ipairs(Children(frame)) do
            if not ours[f] and f.GetCenter then
                local ang, dist = Spot(f)
                if ang and ang > 0 and ang < 110 and dist > 0.6 and dist < 1.9 then
                    out[#out + 1] = string.format("%s (%d deg, %.2fR%s)", Name(f), ang, dist, f:IsShown() and "" or ", hidden")
                end
                Look(f, depth + 1)
            end
        end
    end
    for _, p in ipairs({ Minimap, Obj(_G.MinimapCluster) or false, Obj(_G.MinimapBackdrop) or false }) do
        if p then Look(p, 1) end
    end
    return out
end

-- Zone name + clock. Layout 3 (user, Nov 24): under the minimap come
-- AetherCoords' coordinates pill (just under the bottom chevron), then a navy
-- pill with the zone name and the clock. Blizzard's own zone button and clock
-- are moved into it, so they keep working (click the clock for the stopwatch,
-- hover the zone for its tooltip). The top bar's art stays hidden.
local function GoldZoneText(fs)
    if not fs or fs.aetherGold then return end
    fs.aetherGold = true
    local busy = false
    local function Fix(self, r, g, b)
        if busy or not r or (issecretvalue and (issecretvalue(r) or issecretvalue(g) or issecretvalue(b))) then return end
        if r > 0.6 and g > r * 0.72 and g < r * 0.93 and b < 0.3 * r then
            busy = true; self:SetTextColor(GOLD[1] * r, GOLD[2] * r, GOLD[3]); busy = false
        end
    end
    hooksecurefunc(fs, "SetTextColor", Fix)
    Fix(fs, fs:GetTextColor())
    pcall(function()
        local _, size, flags = fs:GetFont()
        if size then fs:SetFont(FontFile("SemiBold"), size, flags or "") end
    end)
end

local cluster, zoneButton, clock, indicator, zonePill, placing
local PILL_H, PILL_PAD, PILL_GAP = 20, 10, 5      -- pill height, end padding, gap under the coordinates
local function TextWidth(fs, fallback)
    local ok, w = pcall(function() return fs:GetStringWidth() end)
    return (ok and w and w > 0) and w or fallback
end
-- Re-anchored Blizzard frames go back to Blizzard's spot when its minimap
-- re-lays itself out; put them back in the pill when that happens.
local function Keep(frame)
    if not frame or frame.aetherKept then return end
    frame.aetherKept = true
    hooksecurefunc(frame, "SetPoint", function()
        if placing or not zonePill then return end
        C_Timer.After(0, function() if AetherSkins_PlaceZonePill then AetherSkins_PlaceZonePill() end end)
    end)
end
function AetherSkins_PlaceZonePill()
    if not zonePill or placing then return end
    placing = true
    local ok, err = pcall(function()
        zonePill:ClearAllPoints()
        local mini = AetherCoords_MiniUnderMap and AetherCoords_MiniUnderMap()
        if mini then
            zonePill:SetPoint("TOP", mini, "BOTTOM", 0, -PILL_GAP)
            found.zonePill = "under the coordinates"
        else   -- no coordinates pill there: take its spot, just under the bottom chevron
            zonePill:SetPoint("TOP", Minimap, "BOTTOM", 0, -(Radius() * 0.223 + 2))
            found.zonePill = "under the minimap"
        end
        -- contents: the zone name on the left, the clock on the right
        local zw = math.min(TextWidth(zoneText, 80), 130)
        local width = PILL_PAD + zw + PILL_PAD
        if zoneButton then
            zoneButton:ClearAllPoints()
            zoneButton:SetPoint("LEFT", zonePill, "LEFT", PILL_PAD - 2, 0)
            zoneButton:SetSize(zw + 4, 14)
        end
        if clock and clock:IsShown() then
            local cw = TextWidth(_G.TimeManagerClockTicker, clock:GetWidth() or 40)
            clock:ClearAllPoints()
            clock:SetPoint("RIGHT", zonePill, "RIGHT", -(PILL_PAD - 2), 0)
            clock:SetSize(cw + 4, 16)
            width = width + 12 + cw
        end
        zonePill:SetSize(width, PILL_H)
        -- the mail / crafting-order indicator hung under the tracking button,
        -- which is now on the ring: it sits just left of the pill instead
        if indicator then
            indicator:ClearAllPoints()
            indicator:SetPoint("RIGHT", zonePill, "LEFT", -3, 0)
        end
        local lv = zoneButton and zoneButton:GetFrameLevel() or 2
        if clock then lv = math.min(lv, clock:GetFrameLevel() or lv) end
        zonePill:SetFrameLevel(math.max(0, lv - 1))
    end)
    placing = false
    if not ok then found.zonePill = "error: " .. tostring(err) end
end

-- The tracking magnifier on the ring, across from the sun (top-left): Blizzard's
-- own button (its menu and clicks unchanged), its art hidden, our navy disc
-- and a flat magnifier in Aether Blue on top. Mouse goes through ours to it.
local TRACK_AT = { -SUN_AT[1], SUN_AT[2] }
local tracking, trackBtn, trackDeco
PlaceTracking = function()
    if not tracking then return end
    placing = true
    local R = Radius(); local d = SUN_SIZE * R
    tracking:ClearAllPoints()
    tracking:SetPoint("CENTER", Minimap, "CENTER", TRACK_AT[1] * R, TRACK_AT[2] * R)
    tracking:SetSize(d, d)
    if trackBtn ~= tracking then trackBtn:ClearAllPoints(); trackBtn:SetAllPoints(tracking) end
    placing = false
end
local function MoveTracking()
    tracking = (cluster and Obj(cluster.Tracking)) or Obj(_G.MiniMapTracking)
    if not tracking then found.track = "none found"; return end
    trackBtn = Obj(tracking.Button) or Obj(_G.MiniMapTrackingButton) or tracking
    HideTextures(tracking); if trackBtn ~= tracking then HideTextures(trackBtn) end
    if tracking.SetFrameStrata then tracking:SetFrameStrata("MEDIUM") end
    tracking:SetFrameLevel((Minimap:GetFrameLevel() or 1) + 9)
    if trackBtn ~= tracking then trackBtn:SetFrameLevel((Minimap:GetFrameLevel() or 1) + 10) end
    trackDeco = CreateFrame("Frame", "AetherSkinsTracking", tracking)
    trackDeco:SetAllPoints(tracking); trackDeco:EnableMouse(false)
    trackDeco:SetFrameLevel((Minimap:GetFrameLevel() or 1) + 11)
    local disc = trackDeco:CreateTexture(nil, "BACKGROUND"); disc:SetAllPoints(); disc:SetTexture(MEDIA .. "btn_disc")
    local icon = trackDeco:CreateTexture(nil, "ARTWORK"); icon:SetTexture(MEDIA .. "ico_track")
    icon:SetVertexColor(BLUE[1], BLUE[2], BLUE[3], 1); icon:SetPoint("CENTER")
    local hl = trackDeco:CreateTexture(nil, "OVERLAY"); hl:SetAllPoints(); hl:SetTexture(MEDIA .. "btn_disc")
    hl:SetBlendMode("ADD"); hl:SetAlpha(0)
    trackDeco:SetScript("OnSizeChanged", function(_, w) icon:SetSize(w * 0.68, w * 0.68) end)
    trackBtn:HookScript("OnEnter", function() hl:SetAlpha(0.3) end)
    trackBtn:HookScript("OnLeave", function() hl:SetAlpha(0) end)
    ours[trackDeco] = true; ours[disc] = true; ours[icon] = true; ours[hl] = true
    trackDeco.icon = icon
    hooksecurefunc(tracking, "SetPoint", function()
        if not placing then C_Timer.After(0, PlaceTracking) end
    end)
    PlaceTracking()
    found.track = Name(tracking)
end

-- Forever's own coordinates under the minimap (the game option "Player
-- Minimap Coordinates"): AetherCoords' pill replaces them. /fstack showed the
-- frame: MinimapCluster.MinimapContainer.PlayerCoords (with .CoordText). It's
-- hidden by name; any other text near the minimap that reads as a pair of
-- numbers ("26.8, 77.0") is hidden too, in case the name differs.
local function IsCoordText(fs)
    if not fs.GetText then return false end
    local ok, t = pcall(fs.GetText, fs)
    -- Forever hides some text from addons (Midnight's "secret" values, in
    -- instances and combat): reading one is an error, so skip it (user's
    -- /skins debug error, Nov 25).
    if not ok or (issecretvalue and issecretvalue(t)) or type(t) ~= "string" then return false end
    t = t:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", "")
    return t:match("^%s*%(?%s*%d+%.?%d*%s*[,/ ]%s*%d+%.?%d*%s*%)?%s*$") ~= nil
end
local function HideCoordText(frame, depth)
    if not frame or depth > 4 or ours[frame] then return end
    if frame.GetRegions then
        for _, r in ipairs(Regions(frame)) do
            if not ours[r] and r.GetObjectType and r:GetObjectType() == "FontString" and IsCoordText(r) then
                if not hidden[r] then found.coords = (found.coords and found.coords .. ", " or "") .. Name(r) end
                HideRegion(r)
            end
        end
    end
    if frame.GetChildren then
        for _, c in ipairs(Children(frame)) do HideCoordText(c, depth + 1) end
    end
end
local function HideForeverCoords()
    local box = cluster and Obj(cluster.MinimapContainer)
    local pc = box and Obj(box.PlayerCoords)
    if pc then
        if not hidden[pc] then found.coords = (found.coords and found.coords .. ", " or "") .. Name(pc) end
        HideRegion(pc)
        if not pc.aetherHidden and pc.Hide then
            pc.aetherHidden = true
            pc:Hide()
            hooksecurefunc(pc, "Show", function(self) self:Hide() end)
        end
    end
    for _, p in ipairs({ Minimap, cluster or false, Obj(_G.MinimapBackdrop) or false }) do
        if p then HideCoordText(p, 1) end
    end
end
-- for /skins debug: coordinate-like text anywhere on screen, with its frame
local function CoordTextAnywhere()
    local out = {}
    local function Look(frame, depth)
        if not frame or depth > 4 or ours[frame] then return end
        if frame.GetRegions then
            for _, r in ipairs(Regions(frame)) do
                if r.GetObjectType and r:GetObjectType() == "FontString" and IsCoordText(r) then
                    out[#out + 1] = Name(r) .. (hidden[r] and " (hidden)" or "")
                end
            end
        end
        if frame.GetChildren then for _, c in ipairs(Children(frame)) do Look(c, depth + 1) end end
    end
    Look(UIParent, 1)
    return out
end

local function SkinTopBar()
    cluster = Obj(_G.MinimapCluster)
    local bar = (cluster and Obj(cluster.BorderTop)) or Obj(_G.MinimapBorderTop)
    zoneButton = (cluster and Obj(cluster.ZoneTextButton)) or Obj(_G.MinimapZoneTextButton)
    zoneText = Obj(_G.MinimapZoneText) or (zoneButton and Obj(zoneButton.Text))
    if bar then
        if bar.GetObjectType and bar:GetObjectType() == "Texture" then HideRegion(bar) else HideTextures(bar) end
    end
    found.bar = bar and Name(bar) or "none"
    if zoneButton then HideTextures(zoneButton) end
    clock = Obj(_G.TimeManagerClockButton)
    if clock then
        for _, r in ipairs(Regions(clock)) do
            if r:GetObjectType() == "Texture" and r ~= clock:GetHighlightTexture() then HideRegion(r) end
        end
    end
    indicator = cluster and Obj(cluster.IndicatorFrame)
    GoldZoneText(zoneText)
    -- the calendar button and the addon compartment ("1"): hidden. Our sun
    -- opens the calendar; AetherHub's ring button opens the Hub.
    local cal = Obj(_G.GameTimeFrame)
    if cal then HideRegion(cal) end
    local comp = Obj(_G.AddonCompartmentFrame)
    if comp then HideRegion(comp) end
    found.hidTop = (cal and "calendar " or "") .. (comp and "addon compartment" or "")
    -- the pill
    zonePill = CreateFrame("Frame", "AetherSkinsZonePill", (zoneButton and zoneButton:GetParent()) or cluster or UIParent)
    ours[zonePill] = true
    zonePill:EnableMouse(false)
    local p = Pill(zonePill, "BACKGROUND")
    zonePill:SetScript("OnSizeChanged", function() p:Place(zonePill, 0, 0) end)
    zonePill:SetSize(120, PILL_H); p:Place(zonePill, 0, 0)
    Keep(zoneButton); Keep(clock); Keep(indicator)
    if zoneText and zoneText.SetText then hooksecurefunc(zoneText, "SetText", function() AetherSkins_PlaceZonePill() end) end
    AetherSkins_PlaceZonePill()
    C_Timer.After(1, AetherSkins_PlaceZonePill)          -- the bar may still be laying out at login
    -- the tracking magnifier goes onto the ring
    pcall(MoveTracking)
    found.pill = (zoneButton and Name(zoneButton) or "no zone button") .. (clock and (" + " .. Name(clock)) or "")
end

local function InstallMinimap()
    if ring or not Minimap then return end
    -- 1) Blizzard's ring art
    HideTextures(Minimap)
    if _G.MinimapBackdrop then HideTextures(MinimapBackdrop) end
    for _, n in ipairs({ "MinimapBorder", "MinimapCompassTexture", "MinimapNorthTag" }) do
        if _G[n] then HideRegion(_G[n]) end
    end
    HideRegion(Minimap.MinimapCompassTexture)
    -- 2) Our ring: plain underneath, the lit one (day or night) on top
    ring = CreateFrame("Frame", "AetherSkinsMinimapRing", Minimap)
    ring:SetPoint("CENTER")
    ring:SetFrameLevel((Minimap:GetFrameLevel() or 1) + 1)
    ring:EnableMouse(false)
    ours[ring] = true
    ring.plain = ring:CreateTexture(nil, "ARTWORK", nil, 0); ring.plain:SetAllPoints(); ring.plain:SetTexture(MEDIA .. "ring_plain")
    ring.lit = ring:CreateTexture(nil, "ARTWORK", nil, 1); ring.lit:SetAllPoints()
    ours[ring.plain] = true; ours[ring.lit] = true
    ring.chevrons = {}
    -- 3D gold chevrons (bevel ridge), lit from the top-right like the ring: one
    -- baked texture per direction, so the light stays put (no rotation).
    for _, c in ipairs({ { 0, 1, 0, "up" }, { 1, 0, -math.pi / 2, "right" }, { 0, -1, math.pi, "down" }, { -1, 0, math.pi / 2, "left" } }) do
        local dark = ring:CreateTexture(nil, "OVERLAY", nil, 0); dark:SetTexture(MEDIA .. "win_chev_dark")
        dark:SetVertexColor(0.04, 0.045, 0.055, 1)
        local gold = ring:CreateTexture(nil, "OVERLAY", nil, 1); gold:SetTexture(MEDIA .. "chev3d_" .. c[4])
        if c[3] ~= 0 then dark:SetRotation(c[3]) end
        ours[dark] = true; ours[gold] = true
        ring.chevrons[#ring.chevrons + 1] = { dx = c[1], dy = c[2], dark = dark, gold = gold }
    end
    -- 3) Day/night button: ours in place of Forever's
    sunButton = MakeSunButton()
    Layout()
    local function ReplaceIcon()
        if found.daynightFrame then return true end
        local icon = FindDayNightIcon()
        if icon then HideRegion(icon); found.daynightFrame = icon; found.daynight = Name(icon); return true end
        found.daynight = "none found"
    end
    -- the minimap's buttons may not be in place yet right at login: try again shortly
    if not ReplaceIcon() then C_Timer.After(2, ReplaceIcon); C_Timer.After(6, ReplaceIcon) end
    -- 4) Zone + clock pill under the coordinates; magnifier onto the ring;
    --    calendar and addon compartment hidden
    local ok, err = pcall(SkinTopBar)
    if not ok then found.pill = "error: " .. tostring(err) end
    -- 5) Forever's own coordinates text (it may only get its text a moment after login)
    HideForeverCoords(); C_Timer.After(2, HideForeverCoords); C_Timer.After(6, HideForeverCoords)
    -- keep it all in step
    hooksecurefunc(Minimap, "SetSize", Layout)
    Minimap:HookScript("OnSizeChanged", Layout)
    _G.AetherSkins_RingActive = true
    if AetherHub_RefreshMinimapButton then pcall(AetherHub_RefreshMinimapButton) end
    if AetherCoords_RefreshMini then pcall(AetherCoords_RefreshMini) end   -- coordinates go under the bottom chevron
    CheckDay(true)
    C_Timer.NewTicker(15, function() CheckDay(false); HideForeverCoords(); Rehide(); AetherSkins_PlaceZonePill() end)
end

-- ------------------------------------------
-- Wiring and commands
-- ------------------------------------------
local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_LOGIN")
f:RegisterEvent("PLAYER_ENTERING_WORLD")
f:RegisterEvent("ZONE_CHANGED_NEW_AREA")
f:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_LOGIN" then
        db = AetherSkinsDB
        if db.minimap == nil then db.minimap = true end
        if db.minimap then
            local ok, err = pcall(InstallMinimap)
            if not ok then Print("couldn't restyle the minimap: " .. tostring(err)) end
        end
    elseif ring then
        Rehide()
    end
end)

SLASH_AETHERSKINS1 = "/skins"
SLASH_AETHERSKINS2 = "/aetherskins"
SlashCmdList["AETHERSKINS"] = function(msg)
    local cmd = strlower(strtrim(msg or ""))
    if cmd == "minimap" or cmd == "minimap on" or cmd == "minimap off" then
        if cmd == "minimap" then db.minimap = not db.minimap else db.minimap = (cmd == "minimap on") end
        Print("minimap look " .. (db.minimap and "on" or "off") .. ". Type /reload to see the change.")
    elseif cmd == "windows" or cmd == "windows on" or cmd == "windows off" then
        local on = db.windows ~= false
        if cmd == "windows" then on = not on else on = (cmd == "windows on") end
        db.windows = on
        Print("windows look " .. (on and "on" or "off") .. ". Type /reload to see the change.")
    elseif cmd == "tree" then
        local W = AetherSkins_Windows
        local name, n
        if W then name, n = W.TreeUnderMouse() end
        if name then
            Print("saved the structure of " .. name .. " (" .. n .. " lines). Open AetherHub's Debug page and click Show Window Dump to copy it.")
        else
            Print("point at a Blizzard window first, then type /skins tree.")
        end
    elseif cmd == "this" then
        local W = AetherSkins_Windows
        local f = W and W.Enabled() and W.SkinUnderMouse()
        Print(f and ("styled " .. (f:GetName() or "that window") .. ".") or "no Blizzard window under the mouse (or windows look is off).")
    elseif cmd == "sizes" then
        -- every window the grip resized back to its normal size
        db.scale = nil
        local W = AetherSkins_Windows
        if W and W.P3 and W.P3.ResetScales then pcall(W.P3.ResetScales) end
        Print("every window back to its normal size.")
    elseif cmd == "defaults" then
        db.minimap, db.windows = true, true
        forced = nil; AetherSkins_Light = "auto"; CheckDay(false)
        Print("settings back to their defaults. Type /reload to see the change.")
    elseif cmd == "day" or cmd == "night" or cmd == "auto" then
        forced = (cmd ~= "auto") and cmd or nil
        AetherSkins_Light = cmd     -- AetherHub reads it for its Sun or moon choice
        CheckDay(false)
        local day, src = IsDay()
        Print((day and "day" or "night") .. " (" .. src .. ")")
    elseif cmd == "debug" then
        local day, src = IsDay()
        Print(string.format("minimap %s, %.0f wide; ring %s", db.minimap and "on" or "off", Minimap:GetWidth() or 0, ring and "shown" or "not made"))
        Print("now: " .. (day and "day" or "night") .. " (" .. src .. "), game time " .. GameTimeText())
        Print("day/night icon replaced: " .. tostring(found.daynight))
        local near = NearTopRight()
        Print("near the ring's top-right: " .. (#near > 0 and table.concat(near, ", ") or "nothing"))
        Print("zone bar art: " .. tostring(found.bar) .. "; zone pill holds " .. tostring(found.pill) .. ", " .. tostring(found.zonePill))
        Print("tracking (magnifier on the ring): " .. tostring(found.track) .. "; hidden at the top: " .. tostring(found.hidTop))
        Print("Forever's coordinates hidden: " .. tostring(found.coords or "none found"))
        local ct = CoordTextAnywhere()
        Print("coordinate text on screen: " .. (#ct > 0 and table.concat(ct, ", ") or "none"))
        Print("hidden (" .. #hiddenNames .. "): " .. table.concat(hiddenNames, ", "))
        local kids = {}
        for _, p in ipairs({ Minimap, Obj(_G.MinimapCluster) or false }) do
            if p then for _, c in ipairs(Children(p)) do if not ours[c] then kids[#kids + 1] = Name(c) end end end
        end
        Print("other minimap frames: " .. table.concat(kids, ", "))
        if AetherSkins_Windows then AetherSkins_Windows.Debug(Print) end
    else
        Print("the Aether look for the minimap and Blizzard's windows.")
        print("  /skins minimap       turn the minimap look on or off (then /reload)")
        print("  /skins windows       turn the windows look on or off (then /reload)")
        print("  /skins this          style the Blizzard window under your mouse, if it was missed")
        print("  /skins tree          save the structure of the window under your mouse (for its next restyle)")
        print("  /skins day | night   preview the day or night light; /skins auto follows the game again")
        print("  /skins debug         what was found and hidden (send this if something looks off)")
    end
end

AetherSkins_API = { IsDay = IsDay, Layout = Layout, Found = found }
