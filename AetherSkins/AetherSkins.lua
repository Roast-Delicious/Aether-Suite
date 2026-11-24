-- ==========================================
-- AetherSkins: Blizzard's windows in the Aether look
-- First part: the minimap.
--  * Blizzard's ring art is hidden; a navy bevel ring takes its place, with
--    the four gold chevrons (12, 3, 6, 9) and a soft blue glow.
--  * Light comes from the sun/moon button at the top-right: by day a gold
--    glow on the ring's inner wall across from it, by night a white one.
--    It follows the game's day and night (realm time), and changes over
--    by fading to the plain ring and back.
--  * The day/night button is our own: a navy button with an Aether-gold
--    sun or a pale moon. Click it for the calendar.
--  * The zone name and clock bar gets a navy pill; yellow zone text turns
--    Aether gold (Aether gold is the only yellow).
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
    for _, r in ipairs({ frame:GetRegions() }) do
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
    for _, r in ipairs({ b:GetRegions() }) do ours[r] = true end
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
        for _, r in ipairs({ frame:GetRegions() }) do
            if r.GetObjectType and r:GetObjectType() == "Texture" then
                local score = Candidate(r)
                if score and (not best.score or score < best.score) then best.obj, best.score = r, score end
            end
        end
    end
    if frame.GetChildren then
        for _, f in ipairs({ frame:GetChildren() }) do
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
        for _, f in ipairs({ frame:GetChildren() }) do
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

-- Zone name + clock: a navy pill behind Blizzard's bar (its art hidden). The
-- bar's buttons (tracking, calendar, clock) keep working where they are.
local function GoldZoneText(fs)
    if not fs or fs.aetherGold then return end
    fs.aetherGold = true
    local busy = false
    local function Fix(self, r, g, b)
        if busy or not r then return end
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

local function SkinTopBar()
    local cluster = Obj(_G.MinimapCluster)
    local bar = (cluster and Obj(cluster.BorderTop)) or Obj(_G.MinimapBorderTop)
    local zoneButton = (cluster and Obj(cluster.ZoneTextButton)) or Obj(_G.MinimapZoneTextButton)
    zoneText = Obj(_G.MinimapZoneText) or (zoneButton and Obj(zoneButton.Text))
    local anchor
    if bar then
        if bar.GetObjectType and bar:GetObjectType() == "Texture" then HideRegion(bar) else HideTextures(bar) end
        anchor = bar
    elseif zoneButton then
        anchor = zoneButton
    end
    if zoneButton then HideTextures(zoneButton) end
    local clock = Obj(_G.TimeManagerClockButton)
    if clock then
        for _, r in ipairs({ clock:GetRegions() }) do
            if r:GetObjectType() == "Texture" and r ~= clock:GetHighlightTexture() then HideRegion(r) end
        end
    end
    GoldZoneText(zoneText)
    found.bar = anchor and Name(anchor) or "none"
    if anchor then
        local holder = CreateFrame("Frame", nil, anchor:GetObjectType() == "Texture" and anchor:GetParent() or anchor)
        holder:SetAllPoints(anchor)
        holder:SetFrameLevel(math.max(0, (holder:GetParent():GetFrameLevel() or 1) - 1))
        ours[holder] = true
        local p = Pill(holder, "BACKGROUND")
        p:Place(holder, 2, 1)
        holder:SetScript("OnSizeChanged", function() p:Place(holder, 2, 1) end)
        topBar = holder
    end
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
    for _, c in ipairs({ { 0, 1, 0 }, { 1, 0, -math.pi / 2 }, { 0, -1, math.pi }, { -1, 0, math.pi / 2 } }) do
        local dark = ring:CreateTexture(nil, "OVERLAY", nil, 0); dark:SetTexture(MEDIA .. "win_chev_dark")
        dark:SetVertexColor(0.04, 0.045, 0.055, 1)
        local gold = ring:CreateTexture(nil, "OVERLAY", nil, 1); gold:SetTexture(MEDIA .. "win_chev_gold")
        gold:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 1)
        if c[3] ~= 0 then dark:SetRotation(c[3]); gold:SetRotation(c[3]) end
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
    -- 4) Zone + clock pill
    pcall(SkinTopBar)
    -- keep it all in step
    hooksecurefunc(Minimap, "SetSize", Layout)
    Minimap:HookScript("OnSizeChanged", Layout)
    _G.AetherSkins_RingActive = true
    if AetherHub_RefreshMinimapButton then pcall(AetherHub_RefreshMinimapButton) end
    CheckDay(true)
    C_Timer.NewTicker(15, function() CheckDay(false); Rehide() end)
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
    elseif cmd == "day" or cmd == "night" or cmd == "auto" then
        forced = (cmd ~= "auto") and cmd or nil
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
        Print("zone bar: " .. tostring(found.bar))
        Print("hidden (" .. #hiddenNames .. "): " .. table.concat(hiddenNames, ", "))
        local kids = {}
        for _, p in ipairs({ Minimap, Obj(_G.MinimapCluster) or false }) do
            if p then for _, c in ipairs({ p:GetChildren() }) do if not ours[c] then kids[#kids + 1] = Name(c) end end end
        end
        Print("other minimap frames: " .. table.concat(kids, ", "))
    else
        Print("the Aether look for Blizzard's windows. Now: the minimap.")
        print("  /skins minimap       turn the minimap look on or off (then /reload)")
        print("  /skins day | night   preview the day or night light; /skins auto follows the game again")
        print("  /skins debug         what was found and hidden (send this if something looks off)")
    end
end

AetherSkins_API = { IsDay = IsDay, Layout = Layout, Found = found }
