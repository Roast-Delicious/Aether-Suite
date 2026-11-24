-- AetherBars: minimal action bar styling for WoW Forever (works on Classic-style UIs)
-- Only changes how things look (textures, alpha, fonts), so it never blocks your spells in combat.

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
local Print
local defaults = {
    alpha       = 1,     -- bar transparency when idle (0 = invisible, 1 = solid)
    combat      = true,  -- show bars fully while in combat
    mouseover   = true,  -- show a bar fully while your mouse is over it
    hideArt     = true,  -- hide gryphons, bar background, page arrows
    hideMacro   = true,  -- hide macro names on buttons
    size        = "bar2",-- resize buttons to match Action Bar 1: "bar2", "all" or "off"
    edgeAlpha   = 0.85,  -- darkness of the 1px edge around each icon
    readyGlow   = true,  -- red-to-green glow while on cooldown, green flare when ready
    trim        = true,  -- Aether trim: panel, blue frame and gold corners on each bar
    alignCenter = true,  -- Align also centers the whole layout across the screen
}

local db
local groups = {}   -- each group = list of buttons that fade together
local EdgeColor     -- below
local MicroButtonList -- below

-- Button name prefixes and how many buttons each bar has.
-- Missing frames are skipped, so names from other UI versions are harmless.
local BARS = {
    { "ActionButton", 12 },
    { "MultiBarBottomLeftButton", 12 },
    { "MultiBarBottomRightButton", 12 },
    { "MultiBarRightButton", 12 },
    { "MultiBarLeftButton", 12 },
    { "MultiBar5Button", 12 },
    { "MultiBar6Button", 12 },
    { "MultiBar7Button", 12 },
    { "PetActionButton", 10 },
    { "StanceButton", 10 },
    { "ShapeshiftButton", 10 },
}

-- Default bar art to hide (any that don't exist are ignored).
local ART = {
    "MainMenuBarLeftEndCap", "MainMenuBarRightEndCap",
    "MainMenuBarTexture0", "MainMenuBarTexture1", "MainMenuBarTexture2", "MainMenuBarTexture3",
    "MainMenuMaxLevelBar0", "MainMenuMaxLevelBar1", "MainMenuMaxLevelBar2", "MainMenuMaxLevelBar3",
    "MainMenuBarPageNumber", "ActionBarUpButton", "ActionBarDownButton",
    "MainMenuBarArtFrameBackground",
    "SlidingActionBarTexture0", "SlidingActionBarTexture1",
    "StanceBarLeft", "StanceBarMiddle", "StanceBarRight",
    "ShapeshiftBarLeft", "ShapeshiftBarMiddle", "ShapeshiftBarRight",
    "PossessBackground1", "PossessBackground2",
}

local function Fade(obj)
    if obj and obj.SetAlpha then obj:SetAlpha(0) end
end

-- Hide a texture for good: Blizzard sometimes re-shows bar art, so hide it again whenever it does.
local killed, scanned = {}, {}
local function Kill(region)
    if not region or killed[region] then return end
    if region.IsObjectType and region:IsObjectType("Texture") then
        killed[region] = true
        region:Hide()
        hooksecurefunc(region, "Show", region.Hide)
    elseif region.SetAlpha then
        region:SetAlpha(0)
    end
end

-- Remove every background texture on a bar frame, plus art-only child frames
-- (plain frames with no children and no mouse). Buttons, the XP bar, bags and
-- micro menu are separate child frames, so they are left alone.
local function StripArt(container)
    if not container or container == UIParent then return end
    if container.IsForbidden and container:IsForbidden() then return end
    scanned[container] = true
    for _, r in ipairs({ container:GetRegions() }) do
        if r:IsObjectType("Texture") then Kill(r) end
    end
    for _, child in ipairs({ container:GetChildren() }) do
        if child:GetObjectType() == "Frame" and child:GetNumChildren() == 0
            and not child:IsMouseEnabled() then
            for _, r in ipairs({ child:GetRegions() }) do
                if r:IsObjectType("Texture") then Kill(r) end
            end
        end
    end
end

local function HideArt()
    if not db.hideArt then return end
    for _, name in ipairs(ART) do Kill(_G[name]) end
    local art = _G.MainMenuBarArtFrame
    if art then
        Kill(art.LeftEndCap); Kill(art.RightEndCap); Kill(art.PageNumber)
        if art.Background then Kill(art.Background) end
    end
    -- Whatever frames hold Action Bar 1 (and the other bars), whatever they're called
    StripArt(_G.MainMenuBar); StripArt(_G.MainMenuBarArtFrame); StripArt(_G.MainActionBar)
    for _, list in ipairs(groups) do
        local p = list[1] and list[1]:GetParent()
        while p and p ~= UIParent do
            StripArt(p)
            p = p:GetParent()
        end
    end
    -- Page up/down arrows and page number beside Action Bar 1. Newer clients
    -- keep them in an "ActionBarPageNumber" frame on the main bar; older ones
    -- use the global names above. Hidden, and kept hidden if Blizzard re-shows them.
    -- (Paging still works with your keybinds, e.g. Shift+1..6 or Shift+mouse wheel.)
    local pagers = {}
    for _, holder in ipairs({ _G.MainActionBar, _G.MainMenuBar, _G.MainMenuBarArtFrame }) do
        if holder and holder.ActionBarPageNumber then pagers[#pagers + 1] = holder.ActionBarPageNumber end
    end
    local first = groups[1] and groups[1][1]
    local p = first and first:GetParent()
    while p and p ~= UIParent do
        if p.ActionBarPageNumber then pagers[#pagers + 1] = p.ActionBarPageNumber end
        p = p:GetParent()
    end
    for _, n in ipairs({ "ActionBarUpButton", "ActionBarDownButton", "MainMenuBarPageNumber" }) do
        if _G[n] then pagers[#pagers + 1] = _G[n] end
    end
    for _, f in ipairs(pagers) do
        if not f.aetherHidden and not f:IsForbidden() and not (f:IsProtected() and InCombatLockdown()) then
            f.aetherHidden = true
            pcall(f.Hide, f)
            if f.EnableMouse then pcall(f.EnableMouse, f, false) end
            hooksecurefunc(f, "Show", function(self)
                if db.hideArt and not (self:IsProtected() and InCombatLockdown()) then self:Hide() end
            end)
            if f.SetShown then
                hooksecurefunc(f, "SetShown", function(self, shown)
                    if shown and db.hideArt and not (self:IsProtected() and InCombatLockdown()) then self:Hide() end
                end)
            end
        end
    end
end

local function FlatTexture(button, setter, r, g, b, a)
    if not button[setter] then return end
    local t = button:CreateTexture(nil, "OVERLAY")
    t:SetColorTexture(r, g, b, a)
    t:SetAllPoints(button.cleanIcon or button)
    button[setter](button, t)
end

-- ==========================================
-- COOLDOWN GLOW
-- ==========================================
-- While an ability is on cooldown, a glow around its button runs from red
-- (just used) through yellow to green as the cooldown runs down. When it's
-- ready, a bright green flare plays and fades. The short global cooldown after
-- every cast is skipped: only cooldowns longer than GLOW_MIN_SECONDS glow.
-- The glow sits on its own frame so it shows even while the bar is faded.
local GLOW_MIN_SECONDS = 2
local GLOW_TEXTURE = "Interface\\Buttons\\UI-ActionButton-Border"
local TINT_ALPHA = 0.85          -- strength of the glow during the cooldown (the ready flare is full)

local function IsSecret(v) return issecretvalue and issecretvalue(v) end

-- Orange (just used), then blue, then through blue-green (aqua) to green
-- when it's almost ready. Stays at full brightness, so the in-between
-- shades don't go dim or muddy.
local GLOW_STOPS = {
    { 1.00, 0.60, 0.20 },   -- orange
    { 0.30, 0.60, 1.00 },   -- blue
    { 0.45, 1.00, 0.45 },   -- green
}
local READY_COLOR = { 0.45, 1.00, 0.50 }   -- the "ready" flare

local ORANGE_SECONDS = 2      -- orange always shows at least this long
local ORANGE_HOLD = 0.275     -- where orange starts blending into blue

local function CooldownColor(progress)
    progress = math.max(0, math.min(1, progress))
    local segments = #GLOW_STOPS - 1
    local i = math.min(segments, math.floor(progress * segments) + 1)
    local t = progress * segments - (i - 1)
    if i == 1 then
        -- Orange and blue are opposites: halfway they mix to nearly white, so
        -- hold orange and make that blend quick.
        t = math.max(0, math.min(1, (t - ORANGE_HOLD * 2) / (1 - ORANGE_HOLD * 2)))
        t = t * t * (3 - 2 * t)
    end
    local a, b = GLOW_STOPS[i], GLOW_STOPS[i + 1]
    local r, g, bl = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t
    local peak = math.max(r, g, bl, 0.001)
    return r / peak, g / peak, bl / peak
end

-- When the game hides a cooldown's length, the glow learns it: the next time
-- you use that ability it knows how long it takes (kept per action button).
local function ActionKey(button)
    local action = button.action or (button.GetAttribute and button:GetAttribute("action"))
    if not action then return nil end
    local ok, tex = pcall(GetActionTexture, action)
    if not ok or (tex and IsSecret(tex)) then tex = nil end
    return action .. ":" .. tostring(tex)
end

local function Learned(key)
    return key and db and db.cdLearned and db.cdLearned[key]
end

-- The spell you just cast. A cooldown starting on the button that holds it is
-- a real one (not the global cooldown), so its glow can start right away.
local lastCast = { id = nil, at = 0 }
local castWatch = CreateFrame("Frame")
pcall(castWatch.RegisterUnitEvent, castWatch, "UNIT_SPELLCAST_SUCCEEDED", "player")
castWatch:SetScript("OnEvent", function(_, _, unit, _, spellID)
    if unit == "player" and spellID and not IsSecret(spellID) then
        lastCast.id, lastCast.at = spellID, GetTime()
    end
end)

-- The spell on an action button (directly, or the one its macro casts).
local function ButtonSpell(button)
    local action = button.action or (button.GetAttribute and button:GetAttribute("action"))
    if not action or not GetActionInfo then return nil end
    local ok, kind, id = pcall(GetActionInfo, action)
    if not ok or IsSecret(kind) or IsSecret(id) then return nil end
    if kind == "spell" then return id end
    if kind == "macro" and GetMacroSpell then
        local ok2, sid = pcall(GetMacroSpell, id)
        if ok2 and sid and not IsSecret(sid) then return sid end
    end
    return nil
end

-- Was this cooldown started by casting this button's own spell?
local function OwnCast(cd)
    return cd.aetherSpell and lastCast.id == cd.aetherSpell and math.abs(lastCast.at - (cd.aetherStart or 0)) < 0.5
end

local function SizeGlow(glow, button)
    local w = button:GetWidth()
    glow:SetSize(w, w)
    glow.ring:SetSize(w * 1.75, w * 1.75)   -- the border art has empty padding around it
end

local function GetGlow(button)
    if button.aetherGlow then return button.aetherGlow end
    local glow = CreateFrame("Frame", nil, UIParent)
    glow:SetFrameStrata(button:GetFrameStrata())
    glow:SetFrameLevel(button:GetFrameLevel() + 10)
    glow:SetPoint("CENTER", button, "CENTER")
    glow:EnableMouse(false)

    local ring = glow:CreateTexture(nil, "OVERLAY")
    ring:SetTexture(GLOW_TEXTURE)
    if ring.SetDesaturated then ring:SetDesaturated(true) end   -- plain white art, so the tint shows true colors
    ring:SetBlendMode("ADD")
    ring:SetPoint("CENTER")
    glow.ring = ring

    -- A light green wash over the icon, only for the "ready" flare.
    local wash = glow:CreateTexture(nil, "ARTWORK")
    wash:SetAllPoints(button.cleanIcon or button)
    wash:SetColorTexture(0.45, 1, 0.5, 0.3)
    wash:SetBlendMode("ADD")
    glow.wash = wash

    -- Ready flare: up quickly, hold for a moment, fade out.
    local anim = glow:CreateAnimationGroup()
    local fadeIn = anim:CreateAnimation("Alpha")
    fadeIn:SetFromAlpha(0); fadeIn:SetToAlpha(1); fadeIn:SetDuration(0.15); fadeIn:SetOrder(1)
    local fadeOut = anim:CreateAnimation("Alpha")
    fadeOut:SetFromAlpha(1); fadeOut:SetToAlpha(0); fadeOut:SetDuration(0.7)
    fadeOut:SetStartDelay(0.25); fadeOut:SetOrder(2)
    anim:SetScript("OnFinished", function() glow.flaring = false; glow:Hide() end)
    glow.anim = anim

    SizeGlow(glow, button)
    glow:Hide()
    button.aetherGlow = glow
    return glow
end

local cooling = {}               -- button -> true while its cooldown glow runs

local function StopTint(button)
    cooling[button] = nil
    local glow = button.aetherGlow
    if glow and not glow.flaring then glow:Hide() end
end

local function PlayReadyGlow(button)
    if not db or not db.readyGlow or not button:IsVisible() then return end
    local glow = GetGlow(button)
    SizeGlow(glow, button)
    glow.ring:SetVertexColor(READY_COLOR[1], READY_COLOR[2], READY_COLOR[3])
    glow.wash:Show()
    glow.anim:Stop()
    glow.flaring = true
    glow:SetAlpha(0)
    glow:Show()
    glow.anim:Play()
end

-- Updates every running cooldown glow's color (and hides glows on hidden bars).
local tintDriver = CreateFrame("Frame")
tintDriver:SetScript("OnUpdate", function()
    if not next(cooling) then return end
    local now = GetTime()
    for button in pairs(cooling) do
        local cd, glow = button.aetherCD, button.aetherGlow
        if not db or not db.readyGlow then
            StopTint(button)
        elseif glow and not glow.flaring then
            local elapsed = now - (cd.aetherStart or now)
            local duration = cd.aetherDuration
            -- Your own cast (and not a spell that only has the global
            -- cooldown): no need to wait, start the glow now.
            cd.aetherWait = cd.aetherWait or GLOW_MIN_SECONDS
            if cd.aetherWait > 0 and OwnCast(cd) then
                local learned = Learned(cd.aetherKey)
                cd.aetherOwn = true
                if not learned or learned > GLOW_MIN_SECONDS then cd.aetherWait = 0 end
            end
            if not duration and elapsed < cd.aetherWait then
                -- Length unknown (hidden by the game): wait until it's clearly
                -- not the global cooldown before showing anything.
                glow:Hide()
            elseif not button:IsVisible() then
                glow:Hide()
            else
                -- Colors run from when the glow appears (after the 2-second wait
                -- when the length is hidden), and orange always shows for at
                -- least 2 seconds, so short cooldowns get every color too.
                local total, done, shownAt
                local learned = Learned(cd.aetherKey)
                if duration then
                    total, done, shownAt = duration, now - cd.aetherBegan, 0
                elseif learned and learned > GLOW_MIN_SECONDS then
                    total, done, shownAt = learned, elapsed, cd.aetherWait
                end
                local progress = 0               -- first use with the length hidden: orange until ready
                if total then
                    local orangeEnd = shownAt + math.max(ORANGE_SECONDS, 0.3 * (total - shownAt))
                    if done > orangeEnd and total > orangeEnd then
                        progress = ORANGE_HOLD + (1 - ORANGE_HOLD) * (done - orangeEnd) / (total - orangeEnd)
                        if not duration then progress = math.min(0.97, progress) end   -- full green waits for "ready"
                    end
                end
                glow.ring:SetVertexColor(CooldownColor(progress))
                glow.wash:Hide()
                glow:SetAlpha(TINT_ALPHA)
                glow:Show()
            end
        end
    end
end)

-- Times each cooldown with our own clock as well as the game's numbers, so it
-- still works when the game hides those numbers from addons.
local function WatchCooldown(button, cd)
    if not cd or cd.aetherWatched then return end
    cd.aetherWatched = true
    button.aetherCD = cd
    local function Started(self, start, duration)
        local readable = duration ~= nil and not IsSecret(duration) and start ~= nil and not IsSecret(start)
        if readable and duration == 0 then          -- cooldown cleared
            self.aetherStart, self.aetherDuration = nil, nil
            StopTint(button)
            return
        end
        if not self.aetherStart then
            self.aetherStart = GetTime()
            self.aetherKey = ActionKey(button)
            self.aetherSpell = ButtonSpell(button)
            self.aetherWait = GLOW_MIN_SECONDS   -- 0 once it's known to be your own cast
            self.aetherOwn = nil
        end
        if readable then
            if duration <= GLOW_MIN_SECONDS then
                -- The global cooldown (or another short one): no glow, unless a
                -- longer cooldown is already running on this button.
                if not self.aetherDuration then return end
            else
                self.aetherBegan, self.aetherDuration = start, duration
            end
        else
            self.aetherDuration = nil
        end
        if db and db.readyGlow then
            GetGlow(button)
            cooling[button] = true
        end
    end
    hooksecurefunc(cd, "SetCooldown", Started)
    if cd.SetCooldownFromDurationObject then
        hooksecurefunc(cd, "SetCooldownFromDurationObject", function(self) Started(self) end)
    end
    if cd.Clear then
        hooksecurefunc(cd, "Clear", function(self)
            self.aetherStart, self.aetherDuration = nil, nil
            StopTint(button)
        end)
    end
    cd:HookScript("OnCooldownDone", function(self)
        local start = self.aetherStart
        -- Remember how long it took, for when the game hides the length next time.
        -- (Only for your own casts: another spell's global cooldown on this
        -- button would teach it the wrong length.) A spell with only the
        -- global cooldown is remembered too, so it doesn't flash next time.
        if start and self.aetherKey and db and (self.aetherOwn or OwnCast(self)) then
            db.cdLearned = db.cdLearned or {}
            db.cdLearned[self.aetherKey] = GetTime() - start
        elseif start and self.aetherKey and db and GetTime() - start >= GLOW_MIN_SECONDS then
            db.cdLearned = db.cdLearned or {}
            db.cdLearned[self.aetherKey] = GetTime() - start
        end
        self.aetherStart, self.aetherDuration = nil, nil
        StopTint(button)
        if start and GetTime() - start >= GLOW_MIN_SECONDS then PlayReadyGlow(button) end
    end)
end

-- Button edges: Aether blue with the trim on, otherwise the plain dark edge.
-- "Edge darkness" sets how strong either one is.
-- How see-through the panels and empty slots are: the same as AetherMeter's
-- window when you're not fighting (its "opacity out of combat"), else 20%.
local function PanelAlpha()
    local m = _G.AetherMeterDB
    local a = type(m) == "table" and tonumber(m.opacityOutCombat)
    return a and math.max(0, math.min(1, a)) or 0.2
end

EdgeColor = function(edge)
    if edge.socket then
        edge.socket:SetShown(db.trim)
        edge.socket:SetColorTexture(0.05, 0.05, 0.05, PanelAlpha())   -- AetherMeter's window color
    end
    if db.trim and edge.lines then
        -- Trim on: a 1px blue outline (no fill), so empty slots show the socket.
        edge:SetColorTexture(0, 0, 0, 0)
        for _, t in ipairs(edge.lines) do t:SetColorTexture(0.3, 0.7, 1, db.edgeAlpha); t:Show() end
    else
        if db.trim then edge:SetColorTexture(0.3, 0.7, 1, db.edgeAlpha)
        else edge:SetColorTexture(0, 0, 0, db.edgeAlpha) end
        for _, t in ipairs(edge.lines or {}) do t:Hide() end
    end
end

-- Empty slot background (EdgeColor sets the real see-through level).
local SOCKET = { 0.05, 0.05, 0.05, 0.2 }

-- The 1px outline used with the trim (four thin lines around the button).
local function EdgeLines(button, edge)
    if edge.lines then return end
    edge.lines = {}
    for _, side in ipairs({ "TOP", "BOTTOM", "LEFT", "RIGHT" }) do
        local t = button:CreateTexture(nil, "BACKGROUND", nil, -6)
        if side == "TOP" or side == "BOTTOM" then
            t:SetPoint(side .. "LEFT"); t:SetPoint(side .. "RIGHT"); t:SetHeight(1)
        else
            t:SetPoint("TOP" .. side); t:SetPoint("BOTTOM" .. side); t:SetWidth(1)
        end
        edge.lines[#edge.lines + 1] = t
    end
end

local function StyleButton(button)
    if not button or button.cleanStyled then return end
    local name = button:GetName() or ""

    -- 1) Remove the chunky default border, now and whenever Blizzard resets it
    local nt = button.GetNormalTexture and button:GetNormalTexture()
    if nt then nt:SetAlpha(0) end
    if button.SetNormalTexture then
        hooksecurefunc(button, "SetNormalTexture", function(self)
            local t = self:GetNormalTexture()
            if t then t:SetAlpha(0) end
        end)
    end
    Fade(_G[name .. "FloatingBG"])
    Fade(button.SlotBackground); Fade(button.SlotArt)
    Fade(button.NormalTexture)

    -- 2) Crop the icon and inset it 1px so a thin dark edge shows around it
    local icon = button.icon or _G[name .. "Icon"] or _G[name .. "IconTexture"]
    if icon then
        if button.IconMask and icon.RemoveMaskTexture then
            pcall(icon.RemoveMaskTexture, icon, button.IconMask)
        end
        icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
        icon:ClearAllPoints()
        icon:SetPoint("TOPLEFT", button, "TOPLEFT", 1, -1)
        icon:SetPoint("BOTTOMRIGHT", button, "BOTTOMRIGHT", -1, 1)
        button.cleanIcon = icon
    end

    local edge = button:CreateTexture(nil, "BACKGROUND", nil, -8)
    edge:SetAllPoints(button)
    button.cleanEdge = edge
    EdgeColor(edge)
    -- Dark socket behind the icon: what an empty slot shows (with the trim on).
    local socket = button:CreateTexture(nil, "BACKGROUND", nil, -7)
    socket:SetPoint("TOPLEFT", button, "TOPLEFT", 1, -1)
    socket:SetPoint("BOTTOMRIGHT", button, "BOTTOMRIGHT", -1, 1)
    socket:SetColorTexture(SOCKET[1], SOCKET[2], SOCKET[3], SOCKET[4])
    edge.socket = socket
    socket:SetShown(db.trim)

    -- 3) Flat, subtle hover / press / active highlights instead of glossy ones
    if not InCombatLockdown() then
        FlatTexture(button, "SetHighlightTexture", 1, 1, 1, 0.15)
        FlatTexture(button, "SetPushedTexture", 1, 1, 1, 0.30)
        FlatTexture(button, "SetCheckedTexture", 1, 0.69, 0, 0.30)
    end

    -- 4) Cooldown swirl fits the cropped icon
    local cd = button.cooldown or _G[name .. "Cooldown"]
    if cd and icon then
        cd:ClearAllPoints()
        cd:SetAllPoints(icon)
    end
    WatchCooldown(button, cd)

    -- 5) Small, outlined keybind and count text
    local font = STANDARD_TEXT_FONT or "Fonts\\FRIZQT__.TTF"
    local hotkey = button.HotKey or _G[name .. "HotKey"]
    if hotkey then
        if not AetherSetFont(hotkey, "Bold", 10, true) then hotkey:SetFont(font, 10, "OUTLINE") end
        hotkey:ClearAllPoints()
        hotkey:SetPoint("TOPRIGHT", button, "TOPRIGHT", -2, -3)
    end
    local count = button.Count or _G[name .. "Count"]
    if count and not AetherSetFont(count, "Bold", 11, true) then count:SetFont(font, 11, "OUTLINE") end
    local macro = button.Name or _G[name .. "Name"]
    if macro then macro:SetAlpha(db.hideMacro and 0 or 1) end

    -- 6) Remove any other slot/background art built into the button itself,
    --    keeping only the icon, our edge, highlights, and useful indicators.
    local keep = {
        [icon or 0] = true, [edge] = true, [edge.socket] = true,
        [button.GetHighlightTexture and button:GetHighlightTexture() or 0] = true,
        [button.GetPushedTexture and button:GetPushedTexture() or 0] = true,
        [button.GetCheckedTexture and button:GetCheckedTexture() or 0] = true,
        [button.Flash or _G[name .. "Flash"] or 0] = true,               -- attack/auto-repeat flash
        [button.Border or _G[name .. "Border"] or 0] = true,             -- equipped item outline
        [button.AutoCastable or _G[name .. "AutoCastable"] or 0] = true, -- pet autocast corners
    }
    for _, r in ipairs({ button:GetRegions() }) do
        if r:IsObjectType("Texture") and not keep[r] then Kill(r) end
    end

    EdgeLines(button, edge)
    EdgeColor(edge)
    button.cleanStyled = true
end

local function StyleAll()
    wipe(groups)
    for _, bar in ipairs(BARS) do
        local prefix, n = bar[1], bar[2]
        local list = {}
        for i = 1, n do
            local b = _G[prefix .. i]
            if b then
                StyleButton(b)
                list[#list + 1] = b
            end
        end
        if #list > 0 then
            list.prefix = prefix
            groups[#groups + 1] = list
        end
    end

    -- Fallback: find any other action buttons by what they are, not by name,
    -- in case this client names its main bar differently. Grouped by parent bar.
    local grouped = {}
    for _, list in ipairs(groups) do
        for _, b in ipairs(list) do grouped[b] = true end
    end
    local byParent = {}
    local frame = EnumerateFrames()
    while frame do
        if not grouped[frame] and not frame:IsForbidden()
            and frame:IsObjectType("CheckButton")
            and (frame.action or (frame.GetAttribute and frame:GetAttribute("action")))
            and (frame.icon or (frame:GetName() and _G[frame:GetName() .. "Icon"])) then
            StyleButton(frame)
            local p = frame:GetParent() or UIParent
            byParent[p] = byParent[p] or {}
            table.insert(byParent[p], frame)
        end
        frame = EnumerateFrames(frame)
    end
    for _, list in pairs(byParent) do groups[#groups + 1] = list end

    HideArt()
end

-- Other bars: strip background art from the bar frame and any art-holding
-- child frames under it (never the buttons themselves, which are styled above).
local SKIP = { Button = true, CheckButton = true, StatusBar = true, Cooldown = true, Model = true }
local function StripDeep(container, depth)
    if not container or container == UIParent or depth > 3 then return end
    if container.IsForbidden and container:IsForbidden() then return end
    scanned[container] = true
    for _, r in ipairs({ container:GetRegions() }) do
        if r:IsObjectType("Texture") then Kill(r) end
    end
    for _, child in ipairs({ container:GetChildren() }) do
        if not SKIP[child:GetObjectType()] then StripDeep(child, depth + 1) end
    end
end

local function MainBar()
    for _, list in ipairs(groups) do
        if list.prefix == "ActionButton" then return list end
    end
    return groups[1]
end

-- True if a frame holds (at any depth) a button or status bar that isn't one of
-- our action buttons: the XP and reputation bars, bags, micro menu and so on.
local INTERACTIVE = { Button = true, CheckButton = true, StatusBar = true }
local function HoldsOtherWidgets(frame, actionButtons, depth)
    if depth > 6 then return true end           -- too deep to be sure: treat as holding something
    for _, child in ipairs({ frame:GetChildren() }) do
        if not actionButtons[child] then
            if INTERACTIVE[child:GetObjectType()] then return true end
            if HoldsOtherWidgets(child, actionButtons, depth + 1) then return true end
        end
    end
    return false
end

-- Action Bar 1 shares its frames with the XP bar, bags and menu buttons, so it
-- can't be stripped as bluntly as the other bars. Here every frame around it
-- loses its textures, down to background-only child frames, while any frame
-- holding something other than action buttons is left alone.
local function StripMainBar()
    if not db.hideArt then return end
    local main = MainBar()
    if not main or not main[1] then return end
    local actionButtons = {}
    for _, b in ipairs(main) do actionButtons[b] = true end
    local function Strip(frame, depth)
        if depth > 4 or (frame.IsForbidden and frame:IsForbidden()) then return end
        for _, child in ipairs({ frame:GetChildren() }) do
            if not actionButtons[child] and not SKIP[child:GetObjectType()]
                and not HoldsOtherWidgets(child, actionButtons, 1) then
                scanned[child] = true
                for _, r in ipairs({ child:GetRegions() }) do
                    if r:IsObjectType("Texture") then Kill(r) end
                end
                Strip(child, depth + 1)
            end
        end
    end
    local p = main[1]:GetParent()
    while p and p ~= UIParent do
        Strip(p, 1)
        p = p:GetParent()
    end
end

local function StripOtherBars()
    if not db.hideArt then return end
    local main = MainBar()
    local mainChain = {}
    local p = main and main[1] and main[1]:GetParent()
    while p and p ~= UIParent do mainChain[p] = true; p = p:GetParent() end
    for _, list in ipairs(groups) do
        if list ~= main then
            local container = list[1] and list[1]:GetParent()
            if container and not mainChain[container] then StripDeep(container, 1) end
        end
    end
end

-- Size matching: give other bars' buttons the same on-screen size as Action Bar 1.
-- Buttons are anchored to each other, so spacing stays even after resizing.
local sizePending = false
local function MatchSizes()
    if db.size == "off" then return end
    if InCombatLockdown() then sizePending = true; return end
    sizePending = false
    local main = MainBar()
    local ref = main and main[1]
    if not ref then return end
    local refSize = ref:GetWidth() * ref:GetEffectiveScale()
    local targets = {}
    if db.size == "all" then
        for _, list in ipairs(groups) do
            if list ~= main and list.prefix ~= "PetActionButton" and list.prefix ~= "StanceButton"
                and list.prefix ~= "ShapeshiftButton" then
                targets[#targets + 1] = list
            end
        end
    else
        for _, list in ipairs(groups) do
            if list.prefix == "MultiBarBottomLeftButton" then targets[1] = list end
        end
        if not targets[1] then
            for _, list in ipairs(groups) do
                if list ~= main then targets[1] = list; break end
            end
        end
    end
    for _, list in ipairs(targets) do
        for _, b in ipairs(list) do
            local size = refSize / b:GetEffectiveScale()
            if math.abs(b:GetWidth() - size) > 0.5 then b:SetSize(size, size) end
        end
    end
end

-- Bag bar: same clean look as the action buttons, and no background behind it.
-- (The key ring is skipped: its icon is drawn by its border texture.)
local BAGS = {
    "MainMenuBarBackpackButton",
    "CharacterBag0Slot", "CharacterBag1Slot", "CharacterBag2Slot", "CharacterBag3Slot",
    "CharacterReagentBag0Slot",
}
local function BagButtonList()
    local list = {}
    for _, n in ipairs(BAGS) do
        if _G[n] then list[#list + 1] = _G[n] end
    end
    -- The keyring lines up with the bags (sized and spaced), but keeps its own art.
    local key = _G.KeyRingButton
    if key and key.IsShown and key:IsShown() then list[#list + 1] = key end
    return list
end

-- Micro menu buttons (character, spellbook, ... help), by Blizzard's list or the container.
MicroButtonList = function()
    local list, seen = {}, {}
    if type(MICRO_BUTTONS) == "table" then
        for _, n in ipairs(MICRO_BUTTONS) do
            local b = _G[n]
            if b and not seen[b] then seen[b] = true; list[#list + 1] = b end
        end
    end
    if #list == 0 then
        local holder = _G.MicroMenu or _G.MicroMenuContainer
        if holder and not holder:IsForbidden() then
            for _, c in ipairs({ holder:GetChildren() }) do
                if c:IsObjectType("Button") then list[#list + 1] = c end
            end
        end
    end
    return list
end

local function StyleBags()
    for _, n in ipairs(BAGS) do
        local b = _G[n]
        if b then
            StyleButton(b)
            if db.hideArt then
                local p = b:GetParent()
                while p and p ~= UIParent do
                    StripArt(p)
                    p = p:GetParent()
                end
            end
        end
    end
    if db.hideArt then
        StripArt(_G.MicroButtonAndBagsBar); StripArt(_G.BagsBar)
        StripArt(_G.MicroMenuContainer); StripArt(_G.MicroMenu)
        -- Whatever holds the micro menu buttons: drop its dark rounded background.
        for _, b in ipairs(MicroButtonList()) do
            local p = b:GetParent()
            while p and p ~= UIParent do
                StripArt(p)
                if p.SetBackdrop and not p:IsForbidden() then pcall(p.SetBackdrop, p, nil) end
                if p.NineSlice then p.NineSlice:Hide() end
                p = p:GetParent()
            end
        end
    end
end

-- Bag bar and micro menu: same height as Action Bar 1's buttons, the same gap
-- between buttons, and (micro menu) the same blue edge and dark socket.
-- Never in combat; re-checked twice a second so Blizzard re-layouts get fixed.
local function MicroSocket(b)
    if b.aetherEdge then return end
    local edge = b:CreateTexture(nil, "BACKGROUND", nil, -8)
    edge:SetAllPoints(b)
    local socket = b:CreateTexture(nil, "BACKGROUND", nil, -7)
    socket:SetPoint("TOPLEFT", b, "TOPLEFT", 1, -1)
    socket:SetPoint("BOTTOMRIGHT", b, "BOTTOMRIGHT", -1, 1)
    socket:SetColorTexture(SOCKET[1], SOCKET[2], SOCKET[3], SOCKET[4])
    edge.socket = socket
    b.aetherEdge = edge
    EdgeLines(b, edge)
    EdgeColor(edge)
end

local function OneRow(list)
    local mid, size
    for _, b in ipairs(list) do
        local t, bt = b:GetTop(), b:GetBottom()
        if not t or not bt or IsSecret(t) then return false end
        local e = b:GetEffectiveScale()
        local c = (t + bt) / 2 * e
        size = size or (t - bt) * e
        if mid and math.abs(c - mid) > size / 2 then return false end
        mid = mid or c
    end
    return #list > 1
end

-- Lay buttons out in a row with an even gap. fromRight: the rightmost button
-- stays put and the others line up to its left; otherwise the leftmost does.
local stripOrig = {}   -- Blizzard's own anchors for buttons we pin to a spot (to hand back)

local function EvenRow(list, gap, fromRight, anchor)
    local sorted = {}
    for _, b in ipairs(list) do if b:IsShown() then sorted[#sorted + 1] = b end end
    table.sort(sorted, function(a, b)
        return a:GetLeft() * a:GetEffectiveScale() < b:GetLeft() * b:GetEffectiveScale()
    end)
    local n = #sorted
    -- Align's spot for the strip: pin its fixed end there (UIParent units).
    if anchor and n > 0 then
        local b = fromRight and sorted[n] or sorted[1]
        local k = UIParent:GetEffectiveScale() / b:GetEffectiveScale()
        local edge = fromRight and b:GetRight() or b:GetLeft()
        local haveX = edge * b:GetEffectiveScale() / UIParent:GetEffectiveScale()
        local haveY = b:GetBottom() * b:GetEffectiveScale() / UIParent:GetEffectiveScale()
        if math.abs(haveX - anchor.x) > 0.3 or math.abs(haveY - anchor.y) > 0.3 then
            if not stripOrig[b] then
                local pts = {}
                for i = 1, b:GetNumPoints() do pts[i] = { b:GetPoint(i) } end
                stripOrig[b] = pts
            end
            b:ClearAllPoints()
            b:SetPoint(fromRight and "BOTTOMRIGHT" or "BOTTOMLEFT", UIParent, "BOTTOMLEFT", anchor.x * k, anchor.y * k)
        end
    end
    for k = 2, n do
        local i = fromRight and (n - k + 1) or k
        local b, ref = sorted[i], sorted[fromRight and (i + 1) or (i - 1)]
        local want = gap / b:GetEffectiveScale()
        local have
        if fromRight then
            have = (ref:GetLeft() * ref:GetEffectiveScale() - b:GetRight() * b:GetEffectiveScale()) / b:GetEffectiveScale()
        else
            have = (b:GetLeft() * b:GetEffectiveScale() - ref:GetRight() * ref:GetEffectiveScale()) / b:GetEffectiveScale()
        end
        local refBottom = ref:GetBottom() * ref:GetEffectiveScale()
        local myBottom = b:GetBottom() * b:GetEffectiveScale()
        if math.abs(have - want) > 0.5 or math.abs(refBottom - myBottom) > 0.5 then
            local p1, p2, x = "BOTTOMLEFT", "BOTTOMRIGHT", want
            if fromRight then p1, p2, x = "BOTTOMRIGHT", "BOTTOMLEFT", -want end
            local point, rel, relPoint, ox, oy = b:GetPoint(1)
            b:ClearAllPoints()
            if not pcall(b.SetPoint, b, p1, ref, p2, x, 0) and point then
                b:ClearAllPoints(); b:SetPoint(point, rel, relPoint, ox, oy)   -- put it back
            end
        end
    end
end

-- Hand the strip back to Blizzard (Edit Mode, Undo): restore its own anchors.
local function ReleaseStrip()
    for b, pts in pairs(stripOrig) do
        b:ClearAllPoints()
        for _, pt in ipairs(pts) do pcall(b.SetPoint, b, unpack(pt)) end
    end
    wipe(stripOrig)
end

local utilScaled = {}
local function MatchUtilitySizes()
    if not db or InCombatLockdown() then return end
    local bags, micro = BagButtonList(), MicroButtonList()
    if db.size == "off" then
        for b in pairs(utilScaled) do b:SetScale(1) end
        wipe(utilScaled)
        return
    end
    local main = groups[1]
    local ref, ref2 = main and main[1], main and main[2]
    if not ref or not ref:GetWidth() or IsSecret(ref:GetWidth()) then return end
    local refSize = ref:GetHeight() * ref:GetEffectiveScale()
    if refSize <= 0 then return end
    local gap = 2 * ref:GetEffectiveScale()
    if ref2 and ref:GetRight() and ref2:GetLeft() and not IsSecret(ref2:GetLeft()) then
        gap = math.max(0, ref2:GetLeft() * ref2:GetEffectiveScale() - ref:GetRight() * ref:GetEffectiveScale())
    end
    for _, set in ipairs({ bags, micro }) do
        for _, b in ipairs(set) do
            local h = b:GetHeight()
            local parent = b:GetParent()
            if h and h > 0 and parent and not IsSecret(h) then
                local want = refSize / (h * parent:GetEffectiveScale())
                if math.abs(b:GetScale() - want) > 0.005 then b:SetScale(want) end
                utilScaled[b] = true
            end
        end
    end
    for _, b in ipairs(micro) do MicroSocket(b) end
    -- Bags and micro menu side by side: one even strip. Rows on the right half
    -- of the screen keep their right end in place (so they never run off the
    -- edge); rows on the left keep their left end.
    local function RightSide(list)
        local mid = UIParent:GetWidth() * UIParent:GetEffectiveScale() / 2
        local l, r
        for _, b in ipairs(list) do
            local e = b:GetEffectiveScale()
            l = math.min(l or math.huge, b:GetLeft() * e)
            r = math.max(r or -math.huge, b:GetRight() * e)
        end
        return l and (l + r) / 2 > mid
    end
    local both = {}
    for _, b in ipairs(bags) do both[#both + 1] = b end
    for _, b in ipairs(micro) do both[#both + 1] = b end
    -- Align's spot for the strip (bags and micro menu as one), if it set one.
    local anchor = not alignSuspended and db.strip and both[1] and OneRow(both) and db.strip or nil
    if anchor and anchor.uiScale and math.abs(anchor.uiScale - UIParent:GetEffectiveScale()) > 0.001 then
        anchor = nil   -- UI scale changed since Align: let Blizzard's spot stand
    end
    if OneRow(both) then
        local fromRight = RightSide(both)
        if anchor then fromRight = anchor.fromRight end
        EvenRow(both, gap, fromRight, anchor and { x = anchor.x, y = anchor.y })
    else
        if OneRow(bags) then EvenRow(bags, gap, RightSide(bags)) end
        if OneRow(micro) then EvenRow(micro, gap, RightSide(micro)) end
    end
end

-- XP bar: clean thin look, plus move/resize. Size and position are saved per account.
local xpBar, xpMover
local applyingXP = false

local function FindXPBar()
    -- This client uses Blizzard's modern status bars: the XP bar has no name
    -- of its own and lives inside MainStatusTrackingBarContainer (which also
    -- shows reputation or honor when you track those).
    local c = _G.MainStatusTrackingBarContainer
    if c and type(c.bars) == "table" then return c end
    local b = _G.MainMenuExpBar or (_G.MainMenuBar and _G.MainMenuBar.ExpBar)
    if b then return b end
    local f = EnumerateFrames()
    while f do
        if not f:IsForbidden() and f:IsObjectType("StatusBar") then
            local n = f:GetName() or ""
            if n:find("Exp") or n:find("XP") then return f end
        end
        f = EnumerateFrames(f)
    end
end

-- The modern container holds fixed-size bars that Blizzard sizes once at
-- startup, so when the container is resized the bars inside are resized to
-- match (filling it when the bar art is hidden, or inset inside Blizzard's
-- frame art when it's shown).
local function SizeInnerXP(w, h)
    if not xpBar or type(xpBar.bars) ~= "table" then return end
    local x, y, iw, ih = 0, 0, w, h
    if not db.hideArt then x, y, iw, ih = 1, 5, w - 6, h - 6 end
    iw, ih = math.max(1, iw), math.max(1, ih)
    for _, bar in pairs(xpBar.bars) do
        bar:ClearAllPoints()
        bar:SetPoint("BOTTOMLEFT", xpBar, "BOTTOMLEFT", x, y)
        bar:SetSize(iw, ih)
        if bar.StatusBar then bar.StatusBar:SetSize(iw, ih) end
        if bar.ExhaustionLevelFillBar then bar.ExhaustionLevelFillBar:SetHeight(ih) end
    end
    local art = xpBar.BarFrameTexture
    if art and not db.hideArt then
        art:ClearAllPoints()
        art:SetPoint("TOPLEFT", xpBar, "TOPLEFT", 0, 0)
        art:SetPoint("BOTTOMRIGHT", xpBar, "BOTTOMRIGHT", 0, 0)
    end
end

-- The XP fill texture (for the gold progress tick).
local function XPFill()
    if not xpBar then return end
    if type(xpBar.bars) == "table" then
        for _, bar in pairs(xpBar.bars) do
            if bar.isExpBar and bar.StatusBar then return bar.StatusBar:GetStatusBarTexture() end
        end
        return
    end
    return xpBar.GetStatusBarTexture and xpBar:GetStatusBarTexture()
end

local function ApplyXP()
    if not xpBar then return end
    local x = db.xp
    applyingXP = true
    if x.w and x.h then xpBar:SetSize(x.w, x.h); SizeInnerXP(x.w, x.h) end
    if x.left and x.bottom then
        xpBar:ClearAllPoints()
        xpBar:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", x.left, x.bottom)
    end
    applyingXP = false
end

local function SaveXP()
    local x = db.xp
    x.w, x.h = xpBar:GetWidth(), xpBar:GetHeight()
    x.left, x.bottom = xpBar:GetLeft(), xpBar:GetBottom()
    ApplyXP()
end

-- Pin the bar to a single screen anchor so moving and sizing behave predictably
local function DetachXP()
    local l, b, w, h = xpBar:GetLeft(), xpBar:GetBottom(), xpBar:GetWidth(), xpBar:GetHeight()
    applyingXP = true
    xpBar:ClearAllPoints()
    xpBar:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", l, b)
    xpBar:SetSize(w, h)
end

local function CleanXP()
    if not db.hideArt then return end
    for i = 0, 3 do Kill(_G["MainMenuXPBarTexture" .. i]) end
    for i = 1, 19 do Kill(_G["MainMenuXPBarDiv" .. i]) end
    if type(xpBar.bars) == "table" then
        Kill(xpBar.BarFrameTexture)   -- the modern frame art around the bar
    else
        local keep = {
            [XPFill() or 0] = true,
            [_G.ExhaustionLevelFillBar or 0] = true,       -- rested XP shading
            [xpBar.ExhaustionLevelFillBar or 0] = true,
        }
        for _, r in ipairs({ xpBar:GetRegions() }) do
            if r:IsObjectType("Texture") and not keep[r] then Kill(r) end
        end
    end
    local edge = xpBar:CreateTexture(nil, "BACKGROUND", nil, -8)
    edge:SetPoint("TOPLEFT", -1, 1)
    edge:SetPoint("BOTTOMRIGHT", 1, -1)
    edge:SetColorTexture(0, 0, 0, db.edgeAlpha)
    local bg = xpBar:CreateTexture(nil, "BACKGROUND", nil, -7)
    bg:SetAllPoints()
    bg:SetColorTexture(0, 0, 0, 0.4)
    xpBar.aetherSquare = { edge, bg }      -- hidden while the Aether XP bar is drawn
end

local function SetupXP()
    if xpBar then return end
    xpBar = FindXPBar()
    if not xpBar then return end
    CleanXP()
    -- Blizzard re-sizes / re-anchors the bar now and then; put ours back each time
    local function Reapply()
        if not applyingXP and (db.xp.w or db.xp.left) then ApplyXP() end
    end
    for _, m in ipairs({ "SetPoint", "SetSize", "SetWidth", "SetHeight" }) do
        hooksecurefunc(xpBar, m, Reapply)
    end
    ApplyXP()
end

-- Unlock (on = true) or lock the XP bar. Unlocked, it shows a blue overlay
-- you drag to move, a corner handle to resize, and a Done button to lock.
local SetXPUnlocked
SetXPUnlocked = function(on)
    if not xpBar then Print("Couldn't find the XP bar in this client."); return end
    if not xpMover then
        xpBar:SetMovable(true)
        xpBar:SetResizable(true)
        xpBar:SetClampedToScreen(true)
        if xpBar.SetResizeBounds then
            xpBar:SetResizeBounds(100, 3, 3000, 60)
        elseif xpBar.SetMinResize then
            xpBar:SetMinResize(100, 3); xpBar:SetMaxResize(3000, 60)
        end
        -- On UIParent (not the bar), so it shows even while Blizzard has the
        -- bar faded out.
        local m = CreateFrame("Frame", nil, UIParent)
        m:SetPoint("TOPLEFT", xpBar, "TOPLEFT", -2, 2)
        m:SetPoint("BOTTOMRIGHT", xpBar, "BOTTOMRIGHT", 2, -2)
        m:SetFrameStrata("DIALOG")
        m:EnableMouse(true)
        local t = m:CreateTexture(nil, "OVERLAY")
        t:SetAllPoints()
        t:SetColorTexture(0.25, 0.6, 1, 0.35)
        local label = m:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
        label:SetPoint("BOTTOM", m, "TOP", 0, 4)
        label:SetText("XP bar - drag to move, drag the corner handle to resize, then click Done.")
        -- Done: the same look as the unit frames' Done buttons.
        local done = CreateFrame("Button", nil, m)
        done:SetSize(56, 18)
        done:SetPoint("LEFT", m, "RIGHT", 8, 0)
        done:SetFrameLevel(m:GetFrameLevel() + 5)
        local dEdge = done:CreateTexture(nil, "BACKGROUND")
        dEdge:SetPoint("TOPLEFT", -1, 1); dEdge:SetPoint("BOTTOMRIGHT", 1, -1)
        dEdge:SetColorTexture(1, 0.69, 0, 1)
        local dBg = done:CreateTexture(nil, "ARTWORK")
        dBg:SetAllPoints(); dBg:SetColorTexture(0.07, 0.17, 0.32, 0.95)
        local dText = done:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
        dText:SetPoint("CENTER"); dText:SetText("Done")
        done:SetScript("OnClick", function() SetXPUnlocked(false) end)
        -- Moving and sizing are done by hand (following the cursor) rather than
        -- with StartMoving/StartSizing, which some clients ignore for this bar.
        local function Cursor()
            local x, y = GetCursorPosition()
            local s = UIParent:GetEffectiveScale()
            return x / s, y / s
        end
        local drag
        local function Finish()
            if not drag then return end
            drag = nil
            m:SetScript("OnUpdate", nil)
            applyingXP = false
            SaveXP()
        end
        local function Begin(mode)
            DetachXP()
            local cx, cy = Cursor()
            local k = UIParent:GetEffectiveScale() / xpBar:GetEffectiveScale()
            drag = { mode = mode, cx = cx, cy = cy, k = k,
                     l = xpBar:GetLeft(), b = xpBar:GetBottom(), w = xpBar:GetWidth(), h = xpBar:GetHeight() }
            m:SetScript("OnUpdate", function()
                if not IsMouseButtonDown("LeftButton") then Finish(); return end
                local x, y = Cursor()
                local dx, dy = (x - drag.cx) * drag.k, (y - drag.cy) * drag.k
                applyingXP = true
                if drag.mode == "move" then
                    xpBar:ClearAllPoints()
                    xpBar:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", drag.l + dx, drag.b + dy)
                else
                    -- bottom-right corner: wider to the right, taller downward
                    local w = math.max(100, math.min(3000, drag.w + dx))
                    local h = math.max(db.hideArt and 3 or 10, math.min(60, drag.h - dy))
                    xpBar:ClearAllPoints()
                    xpBar:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", drag.l, drag.b + drag.h - h)
                    xpBar:SetSize(w, h)
                    SizeInnerXP(w, h)
                end
            end)
        end
        m:SetScript("OnMouseDown", function(_, btn)
            if btn == "LeftButton" then Begin("move") end
        end)
        m:SetScript("OnMouseUp", Finish)
        local grip = CreateFrame("Button", nil, m)
        grip:SetSize(16, 16)
        grip:SetPoint("TOPLEFT", m, "BOTTOMRIGHT", -10, 6)
        grip:SetFrameLevel(m:GetFrameLevel() + 5)
        grip:SetNormalTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Up")
        grip:SetHighlightTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Highlight")
        grip:SetScript("OnMouseDown", function() Begin("size") end)
        grip:SetScript("OnMouseUp", Finish)
        m:Hide()
        xpMover = m
    end
    if on == nil then on = not xpMover:IsShown() end
    if on == xpMover:IsShown() then return end
    xpMover:SetShown(on)
    Print(on and "XP bar unlocked." or "XP bar locked and saved.")
end

local TrimXP   -- below (the Aether trim section)
local function ApplyAll()
    SetupXP()
    TrimXP()
    StyleAll()
    StripOtherBars()
    StripMainBar()
    MatchSizes()
    StyleBags()
    MatchUtilitySizes()
end

-- ==========================================
-- AETHER TRIM
-- ==========================================
-- A translucent navy panel behind each bar with the Aether window look: double
-- blue frame, soft glow, small gold corner brackets, and the gold gem on the
-- main bar only. Our own frames, placed behind the bars: the bars themselves
-- are never moved, so it's safe in combat. Fades along with its bar.
local trims = {}        -- panel frames, one per merged block of bars
local panelRects        -- their spots, for AetherBars_PanelRects()
local lastPanelSig
AetherBars_Listeners = AetherBars_Listeners or {}   -- AetherChat and AetherMeter add a function here
local groupPanel = {}   -- group index -> panel showing it (for fading)
local PAD = 4           -- space between the buttons and the panel edge (UI units)
local NEAR = 14         -- bars closer than this share one panel
local ALIGN = 20        -- ...if their edges line up within this (so blocks stay rectangles)
local CORNER_NEAR = 2   -- a gold corner hides only when another panel is this close
local GEM_NEAR = 8      -- the gem moves up when a panel sits this close above it

-- Everything inside a panel is measured in whole screen pixels (the panel is
-- scaled so 1 unit = 1 pixel), so lines, corners and the gem always meet
-- exactly. m = pixels per UI unit, rounded, so sizes look the same as before.
local function PixelInfo()
    local uiScale = UIParent:GetEffectiveScale()
    local physH = GetPhysicalScreenSize and select(2, GetPhysicalScreenSize()) or 768
    if not physH or physH <= 0 then physH = 768 end
    local px = 768 / (physH * uiScale)          -- one pixel in UIParent units
    local m = math.max(1, math.floor(1 / px + 0.5))
    return px, m
end

local function MakeTrim(m)
    local p = CreateFrame("Frame", nil, UIParent)
    p:SetFrameStrata("BACKGROUND")
    p:SetFrameLevel(1)
    p.m = m
    local function Rect(layer, sub, r, g, b, a)
        local t = p:CreateTexture(nil, layer, nil, sub)
        t:SetColorTexture(r, g, b, a)
        return t
    end
    -- Panel fill, blue lines and gold all use AetherMeter's window colors, and
    -- fade to the meter's "out of combat" opacity (PanelAlpha).
    p.soft = {}
    local function SoftRect(layer, sub, r, g, b, base)
        local t = Rect(layer, sub, r, g, b, base)
        p.soft[#p.soft + 1] = { t, r, g, b, base }
        return t
    end
    local bg = SoftRect("BACKGROUND", 0, 0.05, 0.05, 0.05, 1)
    bg:SetAllPoints()
    -- outer border, soft glow, inner line
    for _, spec in ipairs({ { 0, 1, 0.3, 0.7, 1, 1 }, { -3, 3, 0.3, 0.7, 1, 0.12 }, { 3, 1, 0.3, 0.7, 1, 0.3 } }) do
        local inset, w, r, g, b, a = spec[1] * m, spec[2] * m, spec[3], spec[4], spec[5], spec[6]
        local Rect = SoftRect
        local top = Rect("BORDER", 0, r, g, b, a)
        top:SetPoint("TOPLEFT", inset, -inset); top:SetPoint("TOPRIGHT", -inset, -inset); top:SetHeight(w)
        local bottom = Rect("BORDER", 0, r, g, b, a)
        bottom:SetPoint("BOTTOMLEFT", inset, inset); bottom:SetPoint("BOTTOMRIGHT", -inset, inset); bottom:SetHeight(w)
        local left = Rect("BORDER", 0, r, g, b, a)
        left:SetPoint("TOPLEFT", inset, -inset); left:SetPoint("BOTTOMLEFT", inset, inset); left:SetWidth(w)
        local right = Rect("BORDER", 0, r, g, b, a)
        right:SetPoint("TOPRIGHT", -inset, -inset); right:SetPoint("BOTTOMRIGHT", -inset, inset); right:SetWidth(w)
    end
    -- gold corner brackets on the outer border (thick), each with a fine echo
    -- just inside it: the Aether chevron accent, thick and fine
    p.corners = {}
    for _, corner in ipairs({ "TOPLEFT", "TOPRIGHT", "BOTTOMLEFT", "BOTTOMRIGHT" }) do
        local ix = corner:find("LEFT") and 1 or -1         -- toward the inside
        local iy = corner:find("TOP") and -1 or 1
        local across = SoftRect("OVERLAY", 6, 1, 0.69, 0, 1)
        across:SetSize(10 * m, 2 * m); across:SetPoint(corner, p, corner, 0, 0)
        local down = SoftRect("OVERLAY", 6, 1, 0.69, 0, 1)
        down:SetSize(2 * m, 10 * m); down:SetPoint(corner, p, corner, 0, 0)
        local fineA = SoftRect("OVERLAY", 6, 1, 0.69, 0, 0.9)
        fineA:SetSize(6 * m, 1 * m); fineA:SetPoint(corner, p, corner, ix * 3 * m, iy * 3 * m)
        local fineD = SoftRect("OVERLAY", 6, 1, 0.69, 0, 0.9)
        fineD:SetSize(1 * m, 6 * m); fineD:SetPoint(corner, p, corner, ix * 3 * m, iy * 3 * m)
        p.corners[corner] = { across, down, fineA, fineD }
    end
    -- the chevron (shown on the block holding Action Bar 1), pointing up: a
    -- smooth image on a dark backing, fading with the panel
    p.gem = {}
    for _, g in ipairs({ { "dark", 0.04, 0.05, 0.07, 6 }, { "gold", 1, 1, 1, 7 } }) do   -- gold = 3D bevel art (its own color)
        local t = p:CreateTexture(nil, "OVERLAY", nil, g[5])
        t:SetTexture("Interface\\AddOns\\AetherBars\\Media\\" .. (g[1] == "gold" and "chev3d_up" or "win_chev_dark"))
        t:SetVertexColor(g[2], g[3], g[4], 1)
        if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false); t:SetTexelSnappingBias(0) end
        t:SetSize(18.7 * m, 18.7 * m); t:SetPoint("CENTER", p, "TOP", 0, 2 * m)
        p.soft[#p.soft + 1] = { t, g[2], g[3], g[4], 1, art = true }
        p.gem[#p.gem + 1] = t
    end
    p:Hide()
    return p
end

local function SoftenPanel(p, a)
    if p.softAlpha == a then return end
    p.softAlpha = a
    for _, e in ipairs(p.soft) do
        if e.art then e[1]:SetVertexColor(e[2], e[3], e[4], e[5] * a)    -- an image: fade its tint
        else e[1]:SetColorTexture(e[2], e[3], e[4], e[5] * a) end
    end
end

local function BoundsOf(list, uiScale)
    local l, r, t, b
    for _, btn in ipairs(list) do
        if btn:IsVisible() then
            local s = btn:GetEffectiveScale() / uiScale
            local bl, br, bt, bb = btn:GetLeft(), btn:GetRight(), btn:GetTop(), btn:GetBottom()
            if bl and br and bt and bb and not IsSecret(bl) then
                bl, br, bt, bb = bl * s, br * s, bt * s, bb * s
                l = l and math.min(l, bl) or bl
                r = r and math.max(r, br) or br
                t = t and math.max(t, bt) or bt
                b = b and math.min(b, bb) or bb
            end
        end
    end
    if l then return { l = l, r = r, t = t, b = b, area = (r - l) * (t - b) } end
end

local function Gap(a, b)
    local dx = math.max(0, math.max(a.l, b.l) - math.min(a.r, b.r))
    local dy = math.max(0, math.max(a.b, b.b) - math.min(a.t, b.t))
    return dx, dy
end

-- Group nearby bars into blocks: stacked bars of the same width, or side-by-side
-- bars of the same height, share one panel. Bars that don't line up keep their
-- own panels (so an L-shaped pair doesn't become one big half-empty box).
local function Cluster(items)
    local blocks = {}
    for _, it in ipairs(items) do
        local r = it.rect
        blocks[#blocks + 1] = { l = r.l, r = r.r, t = r.t, b = r.b, util = it.util, members = { it } }
    end
    -- Every bar keeps its own panel (all four gold corners). The one exception:
    -- the bag bar and micro menu, which sit side by side as one strip.
    local merged = true
    while merged do
        merged = false
        for i = 1, #blocks do
            for j = i + 1, #blocks do
                local A, B = blocks[i], blocks[j]
                local dx, dy = Gap(A, B)
                if A.util and B.util and dx <= 3 * NEAR and dy == 0 then
                    A.l, A.r = math.min(A.l, B.l), math.max(A.r, B.r)
                    A.t, A.b = math.max(A.t, B.t), math.min(A.b, B.b)
                    for _, mb in ipairs(B.members) do A.members[#A.members + 1] = mb end
                    table.remove(blocks, j)
                    merged = true
                    break
                end
            end
            if merged then break end
        end
    end
    return blocks
end

local function LayoutTrims()
    wipe(groupPanel)
    local uiScale = UIParent:GetEffectiveScale()
    local px, m = PixelInfo()
    local items = {}
    if db.trim then
        for gi, list in ipairs(groups) do
            local rect = BoundsOf(list, uiScale)
            if rect then items[#items + 1] = { rect = rect, gi = gi, main = list.prefix == "ActionButton" } end
        end
        for _, list in ipairs({ BagButtonList(), MicroButtonList() }) do
            local rect = BoundsOf(list, uiScale)
            if rect then items[#items + 1] = { rect = rect, util = true } end
        end
    end
    local blocks = Cluster(items)
    local pad = PAD
    -- Blocks that still sit close: split the space between them and drop the
    -- corner brackets on the facing sides, so nothing overlaps.
    for _, A in ipairs(blocks) do
        A.L, A.R, A.T, A.B = A.l - pad, A.r + pad, A.t + pad, A.b - pad
        A.hide = {}
    end
    local near = 2 * pad + 6
    for i = 1, #blocks do
        for j = i + 1, #blocks do
            local A, B = blocks[i], blocks[j]
            local dx, dy = Gap(A, B)
            if dx < near and dy < near and dx >= dy then    -- side by side (or corner to corner)
                local left, right = A, B
                if B.l < A.l then left, right = B, A end
                local mid = (left.r + right.l) / 2
                left.R = math.min(left.R, mid - 2 * px); right.L = math.max(right.L, mid + 2 * px)
            elseif dx < near and dy < near then             -- stacked
                local low, high = A, B
                if B.b < A.b then low, high = B, A end
                local mid = (low.t + high.b) / 2
                low.T = math.min(low.T, mid - 2 * px); high.B = math.max(high.B, mid + 2 * px)
            end
        end
    end
    -- Drop a corner bracket only where another panel sits right next to it.
    for i, A in ipairs(blocks) do
        local pts = { TOPLEFT = { A.L, A.T }, TOPRIGHT = { A.R, A.T },
                      BOTTOMLEFT = { A.L, A.B }, BOTTOMRIGHT = { A.R, A.B } }
        for corner, pt in pairs(pts) do
            for j, B in ipairs(blocks) do
                if i ~= j and pt[1] >= B.L - CORNER_NEAR and pt[1] <= B.R + CORNER_NEAR
                    and pt[2] >= B.B - CORNER_NEAR and pt[2] <= B.T + CORNER_NEAR then
                    A.hide[corner] = true
                end
            end
        end
    end
    -- The gem goes on top of the block with Action Bar 1. If another panel sits
    -- right on top of it, it moves up to that panel's top edge instead.
    local gemBlock
    for _, A in ipairs(blocks) do
        for _, mb in ipairs(A.members) do if mb.main then gemBlock = A end end
    end
    for _ = 1, #blocks do
        if not gemBlock then break end
        local gx, gy = (gemBlock.L + gemBlock.R) / 2, gemBlock.T
        local above
        for _, B in ipairs(blocks) do
            if B ~= gemBlock and gx >= B.L and gx <= B.R and gy >= B.B - GEM_NEAR and gy < B.T then above = B end
        end
        if not above then break end
        gemBlock = above
    end
    for k, A in ipairs(blocks) do
        local p = trims[k]
        if not p or p.m ~= m then
            if p then p:Hide() end
            p = MakeTrim(m)
            trims[k] = p
        end
        -- Panel units = screen pixels; snap position and size to whole pixels.
        p:SetScale(px)
        local x = math.floor(A.L / px + 0.5)
        local y = math.floor(A.B / px + 0.5)
        local w = math.floor((A.R - A.L) / px + 0.5)
        local h = math.floor((A.T - A.B) / px + 0.5)
        if w % 2 == 0 then w = w + 1 end   -- odd width: the gem lands on a pixel
        p:ClearAllPoints()
        p:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", x, y)
        p:SetSize(w, h)
        for _, mb in ipairs(A.members) do
            if mb.gi then groupPanel[mb.gi] = p end
        end
        for _, t in ipairs(p.gem) do t:SetShown(A == gemBlock) end
        for corner, parts in pairs(p.corners) do
            for _, t in ipairs(parts) do t:SetShown(not A.hide[corner]) end
        end
        p.members = A.members
        SoftenPanel(p, PanelAlpha())
        p:Show()
    end
    for k = #blocks + 1, #trims do trims[k]:Hide() end
    -- Where the panels are (UIParent units), for AetherChat and AetherMeter to
    -- fit beside them. Only the main block counts: Action Bar 1's panel and
    -- the panels joined to it. A bar off on its own (say, a side bar at the
    -- screen's edge) is left out, so it can't stretch the chat or the meter.
    local inBlock, start = {}, nil
    for _, A in ipairs(blocks) do
        for _, mb in ipairs(A.members) do if mb.main then start = A end end
    end
    local rects = {}
    if start then
        inBlock[start] = true
        local grew = true
        while grew do
            grew = false
            for _, A in ipairs(blocks) do
                if not inBlock[A] then
                    for B in pairs(inBlock) do
                        local dx = math.max(0, math.max(A.L, B.L) - math.min(A.R, B.R))
                        local dy = math.max(0, math.max(A.B, B.B) - math.min(A.T, B.T))
                        if dx <= 30 and dy <= 30 then inBlock[A] = true; grew = true; break end
                    end
                end
            end
        end
        for _, A in ipairs(blocks) do
            if inBlock[A] then rects[#rects + 1] = { L = A.L, R = A.R, B = A.B, T = A.T } end
        end
    end
    panelRects = rects
    -- Tell AetherChat and AetherMeter right away when the bars' block changes,
    -- so they move together with the bars instead of catching up later.
    local sig = {}
    for _, r in ipairs(rects) do sig[#sig + 1] = string.format("%.0f,%.0f,%.0f,%.0f", r.L, r.R, r.B, r.T) end
    sig = table.concat(sig, ";")
    if sig ~= lastPanelSig then
        lastPanelSig = sig
        for _, fn in ipairs(AetherBars_Listeners) do pcall(fn) end
    end
end

-- Other Aether addons (AetherChat) ask where the bar panels are.
function AetherBars_PanelRects()
    if not db or not db.trim then return nil end
    local out = {}
    for i, r in ipairs(panelRects or {}) do out[i] = { L = r.L, R = r.R, B = r.B, T = r.T } end
    return out
end

-- ==========================================
-- ALIGN
-- ==========================================
-- Place bars roughly where you want them (Blizzard's Edit Mode), then Align
-- snaps them into a tidy layout: Action Bar 1 stays put; bars on the same row
-- line up along the bottom with an even gap; rows stack with room between
-- them for the trim's borders and gold corners. AetherBars keeps the result
-- (re-applied after login and whenever Blizzard repositions a bar). Opening
-- Edit Mode hands the bars back to Blizzard; /cb align undo puts them back.
local OUTER_GAP = 12      -- between separate panels (borders and gold corners fit)
local FAR = 3             -- bars more than 3 buttons apart on a row stay apart
local alignHooked = {}
local applyingAlign = false
local alignPending = false
local alignEditHooked = false
local alignSuspended = false   -- true while Edit Mode is open

-- The frame to move for a bar: the smallest named frame holding all of its
-- buttons (e.g. MultiBarBottomLeft), so the bar moves as one piece. Falls back
-- to each button's own holder if the buttons share nothing but UIParent.
local function AlignMovers(list)
    local shown = {}
    for _, b in ipairs(list) do if b:IsVisible() then shown[#shown + 1] = b end end
    if #shown == 0 then return nil end
    local function Holds(a, b)
        local p = b:GetParent()
        while p do
            if p == a then return true end
            p = p:GetParent()
        end
        return false
    end
    local a = shown[1]:GetParent()
    while a and a ~= UIParent do
        local all = true
        for _, b in ipairs(shown) do if not Holds(a, b) then all = false; break end end
        if all and a:GetName() and not a:IsForbidden() then return { a } end
        a = a:GetParent()
    end
    local movers, set = {}, {}
    for _, b in ipairs(shown) do
        local p = b:GetParent()
        if not p or p == UIParent or p:IsForbidden() or not p:GetName() then return nil end
        if not set[p] then set[p] = true; movers[#movers + 1] = p end
    end
    return movers
end

local function AlignUnits(uiScale)
    local units = {}
    local function Add(list, main, util)
        local r = BoundsOf(list, uiScale)
        if not r then return end
        if util then
            -- The bag and micro strip is placed button by button (see EvenRow),
            -- so Blizzard's bag bar container and its hidden spacing don't matter.
            units[#units + 1] = { rect = r, util = true, movers = {} }
        else
            units[#units + 1] = { rect = r, main = main, movers = AlignMovers(list) or {}, fixed = not AlignMovers(list) }
        end
    end
    for _, list in ipairs(groups) do Add(list, list.prefix == "ActionButton") end
    local bags, micro = BagButtonList(), MicroButtonList()
    local both = {}
    for _, b in ipairs(bags) do both[#both + 1] = b end
    for _, b in ipairs(micro) do both[#both + 1] = b end
    if OneRow(both) then Add(both, false, true) else Add(bags); Add(micro) end
    -- Units that share a frame move together: treat them as one.
    local merged = true
    while merged do
        merged = false
        for i = 1, #units do
            for j = i + 1, #units do
                local A, B = units[i], units[j]
                local shared = false
                for _, m in ipairs(A.movers) do
                    for _, n in ipairs(B.movers) do if m == n then shared = true end end
                end
                if shared then
                    local a, b = A.rect, B.rect
                    a.l, a.r = math.min(a.l, b.l), math.max(a.r, b.r)
                    a.b, a.t = math.min(a.b, b.b), math.max(a.t, b.t)
                    local set = {}
                    for _, m in ipairs(A.movers) do set[m] = true end
                    for _, n in ipairs(B.movers) do if not set[n] then A.movers[#A.movers + 1] = n end end
                    A.main = A.main or B.main
                    A.fixed = A.fixed or B.fixed
                    table.remove(units, j)
                    merged = true
                    break
                end
            end
            if merged then break end
        end
    end
    return units
end

-- Work out where every unit should go. Pure arithmetic on rectangles (UI units),
-- so it can be tested outside the game. Returns { [unit] = { dx, dy } }.
function AetherBars_PlanAlign(units, innerGap, buttonSize)
    local function W(u) return u.rect.r - u.rect.l end
    local function H(u) return u.rect.t - u.rect.b end
    local function VOverlap(a, b)
        return math.min(a.rect.t, b.rect.t) - math.max(a.rect.b, b.rect.b)
    end
    -- 1) Rows: bars that overlap vertically by at least half the shorter one.
    table.sort(units, function(a, b) return a.rect.l < b.rect.l end)
    local rows = {}
    for _, u in ipairs(units) do
        local home
        for _, row in ipairs(rows) do
            for _, m in ipairs(row) do
                local gapX = math.max(u.rect.l - m.rect.r, m.rect.l - u.rect.r)
                if VOverlap(u, m) >= 0.5 * math.min(H(u), H(m)) and gapX <= FAR * buttonSize then
                    home = row
                end
            end
        end
        if home then home[#home + 1] = u else rows[#rows + 1] = { u } end
    end
    -- 2) Lay each row out: bottoms lined up, even gaps. Bars of the same height
    --    share a panel (button gap); others get the wider panel gap.
    local plan = {}
    local bands = {}
    for _, row in ipairs(rows) do
        table.sort(row, function(a, b) return a.rect.l < b.rect.l end)
        local ai = 1
        for i, u in ipairs(row) do if u.main then ai = i end end
        local anchor = row[ai]
        local pos = { [anchor] = { l = anchor.rect.l, b = anchor.rect.b } }
        local onePanel = true
        local function Gap(a, b)
            if math.abs(H(a) - H(b)) <= ALIGN then return innerGap end
            onePanel = false
            return OUTER_GAP
        end
        for i = ai + 1, #row do
            local prev, u = row[i - 1], row[i]
            pos[u] = { l = pos[prev].l + W(prev) + Gap(prev, u), b = pos[anchor].b }
        end
        for i = ai - 1, 1, -1 do
            local nxt, u = row[i + 1], row[i]
            pos[u] = { l = pos[nxt].l - Gap(u, nxt) - W(u), b = pos[anchor].b }
        end
        local band = { units = row, pos = pos, onePanel = onePanel, main = anchor.main }
        local l, r, t, b
        for _, u in ipairs(row) do
            local p = pos[u]
            l = math.min(l or math.huge, p.l); r = math.max(r or -math.huge, p.l + W(u))
            b = math.min(b or math.huge, p.b); t = math.max(t or -math.huge, p.b + H(u))
        end
        band.l, band.r, band.b, band.t = l, r, b, t
        bands[#bands + 1] = band
    end
    -- 3) Stack the bands, starting from the one holding Action Bar 1.
    local start
    for _, band in ipairs(bands) do if band.main then start = band end end
    start = start or bands[1]
    if not start then return plan end
    local placed = { [start] = { dx = 0, dy = 0 } }
    local function Shifted(band) local s = placed[band]; return band.l + s.dx, band.r + s.dx, band.b + s.dy, band.t + s.dy end
    while true do
        local best, bestFrom, bestDist
        for _, q in ipairs(bands) do
            if not placed[q] then
                for p in pairs(placed) do
                    local pl, pr, pb, pt = Shifted(p)
                    local overlap = math.min(pr, q.r) - math.max(pl, q.l)
                    if overlap >= 0.5 * math.min(pr - pl, q.r - q.l) then
                        local dist = math.max(q.b - pt, pb - q.t, 0)
                        if not bestDist or dist < bestDist then best, bestFrom, bestDist = q, p, dist end
                    end
                end
            end
        end
        if not best then break end
        local q, p = best, bestFrom
        local pl, pr, pb, pt = Shifted(p)
        local sameWidth = math.abs((q.r - q.l) - (pr - pl)) <= ALIGN
        local gap = (sameWidth and q.onePanel and p.onePanel) and innerGap or OUTER_GAP
        local dy
        if (q.b + q.t) / 2 >= (pb + pt) / 2 then dy = (pt + gap) - q.b else dy = (pb - gap) - q.t end
        -- left edges, right edges or centers: whichever needs the smallest nudge
        local options = { pl - q.l, pr - q.r, (pl + pr) / 2 - (q.l + q.r) / 2 }
        local dx = options[1]
        for _, o in ipairs(options) do if math.abs(o) < math.abs(dx) then dx = o end end
        if sameWidth then dx = options[1] end
        placed[q] = { dx = dx, dy = dy }
    end
    for _, band in ipairs(bands) do
        local s = placed[band] or { dx = 0, dy = 0 }
        for _, u in ipairs(band.units) do
            local p = band.pos[u]
            -- attached: part of the main block (bars off on their own stay put)
            plan[u] = { dx = p.l + s.dx - u.rect.l, dy = p.b + s.dy - u.rect.b, attached = placed[band] ~= nil }
        end
    end
    return plan
end

-- Blizzard measures the side bars (Action Bars 4 and 5) from the screen's
-- right edge to decide where the quest tracker and other right-side frames
-- go, so those two are always anchored from the right. (A left anchor made
-- Blizzard think the side bar was ~1500 wide and pushed the tracker left.)
local RIGHT_SIDE_BARS = { MultiBarRight = true, MultiBarLeft = true }

local function PlaceMover(f, x, y)
    applyingAlign = true
    f:ClearAllPoints()
    if RIGHT_SIDE_BARS[f:GetName() or ""] then
        local pw = UIParent:GetWidth() * UIParent:GetEffectiveScale() / f:GetEffectiveScale()
        f:SetPoint("BOTTOMRIGHT", UIParent, "BOTTOMRIGHT", x + f:GetWidth() - pw, y)
    else
        f:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", x, y)
    end
    applyingAlign = false
end

local function HookMover(f)
    if alignHooked[f] then return end
    alignHooked[f] = true
    hooksecurefunc(f, "SetPoint", function(self)
        if applyingAlign or alignSuspended then return end
        local spot = db.align and db.align[self:GetName()]
        if not spot then return end
        if InCombatLockdown() then alignPending = true; return end
        PlaceMover(self, spot[1], spot[2])
    end)
end

local function ApplyAlign()
    if not db or type(db.align) ~= "table" or alignSuspended then return end
    if InCombatLockdown() then alignPending = true; return end
    alignPending = false
    for name, spot in pairs(db.align) do
        local f = _G[name]
        if f and f.SetPoint and not f:IsForbidden() then
            HookMover(f)
            PlaceMover(f, spot[1], spot[2])
        end
    end
end

local function ReleaseAlign()
    if db and ((db.align and next(db.align)) or db.strip) then
        db.align = {}
        db.strip = nil
        ReleaseStrip()
        Print("You moved bars in Edit Mode, so they're back in Blizzard's hands. Click Align Bars to tidy them again.")
    end
end

local function DoAlign(arg)
    if InCombatLockdown() then Print("Bars can't be moved in combat. Try again after the fight."); return end
    db.align = db.align or {}
    if arg == "undo" then
        local undo = db.alignUndo
        if (type(undo) ~= "table" or not next(undo)) and not db.alignStripUndo and not db.alignXPUndo then Print("Nothing to undo."); return end
        undo = undo or {}
        db.align = {}
        for name, spot in pairs(undo) do
            local f = _G[name]
            if f then PlaceMover(f, spot[1], spot[2]) end
        end
        db.alignUndo = nil
        db.strip = db.alignStripUndo
        db.alignStripUndo = nil
        if db.alignXPUndo then
            local x = db.alignXPUndo
            db.xp.left, db.xp.bottom, db.xp.w, db.xp.h = x.left, x.bottom, x.w, x.h
            db.alignXPUndo = nil
            if x.left then ApplyXP() else Print("The XP bar goes back to its own spot after a /reload.") end
        end
        MatchUtilitySizes(); LayoutTrims()
        Print("Bars are back where they were before Align.")
        return
    end
    local uiScale = UIParent:GetEffectiveScale()
    local units = AlignUnits(uiScale)
    local main = groups[1]
    local a, b2 = main and main[1], main and main[2]
    local buttonSize, innerGap = 36, 2
    if a and a:GetHeight() then
        local e = a:GetEffectiveScale() / uiScale
        buttonSize = a:GetHeight() * e
        if b2 and b2:GetLeft() and a:GetRight() and not IsSecret(b2:GetLeft()) then
            innerGap = math.max(0, math.min(NEAR - 2, (b2:GetLeft() - a:GetRight()) * e))
        end
    end
    -- Every bar gets its own panel, so every gap is the panel gap.
    local plan = AetherBars_PlanAlign(units, OUTER_GAP, buttonSize)
    -- Center: slide the whole aligned layout sideways so it sits in the middle
    -- of the screen (its shape and spacing stay exactly the same).
    -- Only the main block (Action Bar 1 and the bars joined to it) is centered;
    -- a bar off on its own, like a side bar at the screen's edge, stays put and
    -- doesn't count.
    if db.alignCenter ~= false then
        local l, r
        for u, d in pairs(plan) do
            if d.attached then
                l = math.min(l or math.huge, u.rect.l + d.dx)
                r = math.max(r or -math.huge, u.rect.r + d.dx)
            end
        end
        if l then
            local shift = math.floor(UIParent:GetWidth() / 2 - (l + r) / 2 + 0.5)
            for _, d in pairs(plan) do if d.attached then d.dx = d.dx + shift end end
        end
    end
    local undo, moved = {}, 0
    local stripUndo
    for u, d in pairs(plan) do
        if u.util then
            local mid = UIParent:GetWidth() / 2
            local fromRight = (u.rect.l + u.rect.r) / 2 > mid
            local oldX = fromRight and u.rect.r or u.rect.l
            stripUndo = { x = oldX, y = u.rect.b, fromRight = fromRight, uiScale = UIParent:GetEffectiveScale() }
            db.strip = { x = oldX + d.dx, y = u.rect.b + d.dy, fromRight = fromRight, uiScale = UIParent:GetEffectiveScale() }
            if math.abs(d.dx) > 0.3 or math.abs(d.dy) > 0.3 then moved = moved + 1 end
        elseif not u.fixed and d.attached then
            -- Every bar in the main block keeps a saved spot, moved or not, so
            -- the whole layout comes back exactly after a reload.
            local shifted = math.abs(d.dx) > 0.3 or math.abs(d.dy) > 0.3
            for _, f in ipairs(u.movers) do
                local name = f:GetName()
                local k = uiScale / f:GetEffectiveScale()
                local l, bt = f:GetLeft(), f:GetBottom()
                if name and l and bt then
                    if shifted then undo[name] = undo[name] or { l, bt } end
                    local x, y = l + d.dx * k, bt + d.dy * k
                    db.align[name] = { x, y }
                    HookMover(f)
                    if shifted then PlaceMover(f, x, y) end
                end
            end
            if shifted then moved = moved + 1 end
        elseif not d.attached then
            -- A bar off on its own isn't Align's business: forget any spot an
            -- earlier Align saved for it, so Blizzard places it again.
            for _, f in ipairs(u.movers) do
                local name = f:GetName()
                if name and db.align[name] then db.align[name] = nil; moved = moved + 1 end
            end
        end
    end
    -- The XP bar comes along with Action Bar 1, keeping its place beside the bars.
    local xpUndo
    for u, d in pairs(plan) do
        if u.main and xpBar and (math.abs(d.dx) > 0.3 or math.abs(d.dy) > 0.3) and xpBar:GetLeft() then
            local k = uiScale / xpBar:GetEffectiveScale()
            local l, bt = xpBar:GetLeft(), xpBar:GetBottom()
            xpUndo = { left = db.xp.left, bottom = db.xp.bottom, w = db.xp.w, h = db.xp.h }
            if not db.xp.w then db.xp.w, db.xp.h = xpBar:GetWidth(), xpBar:GetHeight() end
            db.xp.left, db.xp.bottom = l + d.dx * k, bt + d.dy * k
            ApplyXP()
        end
    end
    -- If the XP bar now sits on top of a bar, lift it to just above that bar.
    if xpBar and xpBar:GetLeft() then
        local e = xpBar:GetEffectiveScale() / uiScale
        local xl, xr = xpBar:GetLeft() * e, xpBar:GetRight() * e
        local xb, xt = xpBar:GetBottom() * e, xpBar:GetTop() * e
        local lift
        for u, d in pairs(plan) do
            if d.attached then
                local l, r = u.rect.l + d.dx, u.rect.r + d.dx
                local b, t = u.rect.b + d.dy, u.rect.t + d.dy
                if xl < r and xr > l and xb < t + 4 and xt > b - 4 then
                    lift = math.max(lift or -math.huge, t + 6)
                end
            end
        end
        if lift then
            xpUndo = xpUndo or { left = db.xp.left, bottom = db.xp.bottom, w = db.xp.w, h = db.xp.h }
            if not db.xp.w then db.xp.w, db.xp.h = xpBar:GetWidth(), xpBar:GetHeight() end
            db.xp.left = xpBar:GetLeft()
            db.xp.bottom = lift / e
            ApplyXP()
            moved = moved + 1
        end
    end
    if moved == 0 then Print("Your bars are already lined up."); return end
    db.alignUndo = undo
    db.alignStripUndo = stripUndo
    db.alignXPUndo = xpUndo
    MatchUtilitySizes(); LayoutTrims()
    Print("Lined up " .. moved .. " bar" .. (moved == 1 and "" or "s") .. ". Type /cb align undo to put them back.")
end

-- The Aether XP bar: a pill-shaped bar drawn over Blizzard's (whose own fill,
-- background and ticks are hidden; its hover text and rested tooltip still
-- work). Navy = XP earned, bright blue = your rested bonus ahead of it, faint
-- gold ticks every 5%, a gold mark where you are, and gold chevrons at 12, 3,
-- 6 and 9 sized from the bar's height (sides 175%, top and bottom 130%).
local XP_MEDIA = "Interface\\AddOns\\AetherBars\\Media\\"
local XPC = {
    edge = { 0.3, 0.65, 1, 1 }, gap = { 0.04, 0.05, 0.07, 1 }, back = { 0.04, 0.05, 0.07, 1 },
    earned = { 0.11, 0.29, 0.59, 1 }, rested = { 0.3, 0.65, 1, 0.85 }, gold = { 1, 0.69, 0, 1 },
}
local xpArt                       -- everything we draw, built once
local function XPExpBar()
    if not xpBar then return end
    if type(xpBar.bars) == "table" then
        for _, bar in pairs(xpBar.bars) do if bar.isExpBar then return bar end end
        return
    end
    return xpBar
end
local function XPTex(parent, layer, sub, file, c)
    local t = parent:CreateTexture(nil, layer, nil, sub)
    t:SetTexture(file)
    t:SetVertexColor(c[1], c[2], c[3], c[4] or 1)
    if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false); t:SetTexelSnappingBias(0) end
    return t
end
-- A pill (round-ended bar) that can be drawn partly filled from the left.
local function NewPill(parent, sub, c)
    local p = {
        l = XPTex(parent, "ARTWORK", sub, XP_MEDIA .. "xp_cap", c),
        m = XPTex(parent, "ARTWORK", sub, "Interface\\Buttons\\WHITE8X8", c),
        r = XPTex(parent, "ARTWORK", sub, XP_MEDIA .. "xp_cap", c),
    }
    -- x0..x1, y0..y1: the full pill's box (from the overlay's top-left, y down);
    -- frac: how much of it (0 to 1) is drawn, from the left.
    function p:Set(x0, y0, x1, y1, frac)
        local h = y1 - y0
        local r = h / 2
        local w = x1 - x0
        local stop = x0 + w * math.max(0, math.min(1, frac or 1))
        local function Show(t, on) t:SetShown(on) end
        -- left cap (partial if the fill ends inside it)
        local lw = math.min(r, stop - x0)
        Show(self.l, lw > 0.05)
        if lw > 0.05 then
            self.l:ClearAllPoints(); self.l:SetSize(lw, h)
            self.l:SetPoint("TOPLEFT", parent, "TOPLEFT", x0, -y0)
            self.l:SetTexCoord(0, lw / r, 0, 1)
        end
        -- middle
        local mw = math.min(stop, x1 - r) - (x0 + r)
        Show(self.m, mw > 0.05)
        if mw > 0.05 then
            self.m:ClearAllPoints(); self.m:SetSize(mw, h)
            self.m:SetPoint("TOPLEFT", parent, "TOPLEFT", x0 + r, -y0)
        end
        -- right cap (the left cap image, mirrored; partial if the fill ends in it)
        local rw = stop - (x1 - r)
        Show(self.r, rw > 0.05)
        if rw > 0.05 then
            rw = math.min(r, rw)
            self.r:ClearAllPoints(); self.r:SetSize(rw, h)
            self.r:SetPoint("TOPLEFT", parent, "TOPLEFT", x1 - r, -y0)
            self.r:SetTexCoord(1, 1 - rw / r, 0, 1)
        end
    end
    function p:Hide() self.l:Hide(); self.m:Hide(); self.r:Hide() end
    return p
end

local function XPNumbers()
    -- Earned and rested, each 0 to 1 of the level. Plain numbers only; if the
    -- game hides them, the bar shows empty rather than guessing.
    local ok, cur, max, rest = pcall(function() return UnitXP("player"), UnitXPMax("player"), GetXPExhaustion and GetXPExhaustion() end)
    if not ok or issecretvalue and (issecretvalue(cur) or issecretvalue(max) or issecretvalue(rest)) then return 0, 0 end
    if not cur or not max or max <= 0 then return 0, 0 end
    local earned = math.min(1, cur / max)
    local rested = math.min(1, (cur + (rest or 0)) / max)
    return earned, rested
end

local function LayoutXPArt()
    local a = xpArt
    if not a then return end
    local ov = a.frame
    local w, h = ov:GetWidth(), ov:GetHeight()
    if not w or w < 20 or not h or h < 2 then return end
    -- leave room at both ends for the side chevrons (so they don't touch the
    -- bars beside the XP bar)
    local side, mid, push = 1.75 * h, 1.30 * h, 3
    local E = math.min(w / 4, push + side * 0.5 - h * 0.25)
    local x0, x1 = E, w - E
    local line = math.max(1, math.floor(h / 9 + 0.5))
    local gap = math.max(1, math.floor(h * 0.12 + 0.5))
    local inset = line + gap
    local earned, rested = XPNumbers()
    a.edge:Set(x0, 0, x1, h, 1)
    a.back:Set(x0 + line, line, x1 - line, h - line, 1)
    local fx0, fy0, fx1, fy1 = x0 + inset, inset, x1 - inset, h - inset
    if rested > earned then a.rested:Set(fx0, fy0, fx1, fy1, rested) else a.rested:Hide() end
    a.earned:Set(fx0, fy0, fx1, fy1, earned)
    -- gold ticks every 5%, and a gold mark where you are
    local fw = fx1 - fx0
    for i, t in ipairs(a.ticks) do
        t:ClearAllPoints(); t:SetSize(1, fy1 - fy0)
        t:SetPoint("TOPLEFT", ov, "TOPLEFT", fx0 + fw * i / 20, -fy0)
    end
    a.tip:ClearAllPoints(); a.tip:SetSize(math.max(1, line), fy1 - fy0)
    a.tip:SetPoint("TOP", ov, "TOPLEFT", fx0 + fw * earned, -fy0)
    a.tip:SetShown(earned > 0.002 and earned < 0.998)
    -- chevrons: sides 175%, top and bottom 130% of the bar's height, 3 px out
    for key, set in pairs(a.chev) do
        for _, t in ipairs(set) do
            t:ClearAllPoints()
            local size = (key == "left" or key == "right") and side or mid
            t:SetSize(size, size)
            if key == "top" then t:SetPoint("CENTER", ov, "TOPLEFT", w / 2, push)
            elseif key == "bottom" then t:SetPoint("CENTER", ov, "TOPLEFT", w / 2, -h - push)
            elseif key == "left" then t:SetPoint("CENTER", ov, "TOPLEFT", x0 - push, -h / 2)
            else t:SetPoint("CENTER", ov, "TOPLEFT", x1 + push, -h / 2) end
        end
    end
end

-- Blizzard's own XP visuals: hidden while ours is drawn, back when it's off.
local function BlizzardXPVisible(on)
    local bar = XPExpBar()
    if not bar then return end
    local a = on and 1 or 0
    if bar.StatusBar then bar.StatusBar:SetAlpha(a) end
    if bar.ExhaustionLevelFillBar then bar.ExhaustionLevelFillBar:SetAlpha(a) end
    if bar.ExhaustionTick then bar.ExhaustionTick:SetAlpha(a) end      -- its tooltip still works
    if bar.OverlayFrame and bar.OverlayFrame.BarDividerTexture then bar.OverlayFrame.BarDividerTexture:SetAlpha(a) end
    for _, t in ipairs(xpBar.aetherSquare or {}) do t:SetShown(on) end
    if xpBar.BarFrameTexture and not db.hideArt then xpBar.BarFrameTexture:SetAlpha(a) end   -- Blizzard's square frame art
end

local function BuildXPArt()
    local bar = XPExpBar()
    if not bar or xpArt then return end
    local ov = CreateFrame("Frame", nil, bar)
    ov:SetAllPoints(bar)
    ov:SetFrameLevel((bar.StatusBar and bar.StatusBar:GetFrameLevel() or bar:GetFrameLevel()) + 1)
    local a = { frame = ov }
    a.edge = NewPill(ov, 0, XPC.edge)
    a.back = NewPill(ov, 1, XPC.back)
    a.rested = NewPill(ov, 2, XPC.rested)
    a.earned = NewPill(ov, 3, XPC.earned)
    a.ticks = {}
    for i = 1, 19 do
        a.ticks[i] = XPTex(ov, "ARTWORK", 4, "Interface\\Buttons\\WHITE8X8", { 1, 0.69, 0, 0.35 })
    end
    a.tip = XPTex(ov, "ARTWORK", 5, "Interface\\Buttons\\WHITE8X8", XPC.gold)
    a.chev = {}
    for _, c in ipairs({ { "top", 0, "up" }, { "bottom", math.pi, "down" }, { "left", math.pi / 2, "left" }, { "right", -math.pi / 2, "right" } }) do
        local set = {}
        for _, g in ipairs({ { "dark", { 0.04, 0.05, 0.07, 1 }, 6 }, { "gold", { 1, 1, 1, 1 }, 7 } }) do
            -- gold: the 3D bevel, one image per direction (lit from the top-right), never rotated
            local gold3d = g[1] == "gold"
            local t = XPTex(ov, "OVERLAY", g[3], XP_MEDIA .. (gold3d and ("chev3d_" .. c[3]) or ("win_chev_" .. g[1])), g[2])
            if not gold3d and c[2] ~= 0 and t.SetRotation then t:SetRotation(c[2]) end    -- positive turns counter-clockwise
            set[#set + 1] = t
        end
        a.chev[c[1]] = set
    end
    xpArt = a
    ov:SetScript("OnSizeChanged", LayoutXPArt)
    ov:RegisterEvent("PLAYER_XP_UPDATE")
    ov:RegisterEvent("UPDATE_EXHAUSTION")
    ov:RegisterEvent("PLAYER_LEVEL_UP")
    ov:RegisterEvent("PLAYER_ENTERING_WORLD")
    ov:SetScript("OnEvent", function() C_Timer.After(0, LayoutXPArt) end)
    -- Blizzard swaps its fill art when you become rested; keep it hidden.
    if bar.UpdateStatusBarTextures then
        hooksecurefunc(bar, "UpdateStatusBarTextures", function() if db and db.trim then BlizzardXPVisible(false) end end)
    end
end

TrimXP = function()
    if not xpBar then return end
    BuildXPArt()
    if not xpArt then return end
    xpArt.frame:SetShown(db.trim and true or false)
    BlizzardXPVisible(not db.trim)
    if db.trim then LayoutXPArt() end
end

-- Fading: each bar is solid while hovered (or in combat), otherwise db.alpha
local trimTick = 0
local lastPanelAlpha
local function UpdateFade()
    local inCombat = db.combat and (InCombatLockdown() or UnitAffectingCombat("player"))
    local panelAlpha = {}
    for gi, list in ipairs(groups) do
        local target = db.alpha
        if inCombat then
            target = 1
        elseif db.mouseover then
            for _, b in ipairs(list) do
                if b:IsVisible() and b:IsMouseOver() then target = 1; break end
            end
        end
        for _, b in ipairs(list) do
            if b:GetAlpha() ~= target then b:SetAlpha(target) end
        end
        local panel = groupPanel[gi]
        if panel then panelAlpha[panel] = math.max(panelAlpha[panel] or 0, target) end
    end
    for _, panel in ipairs(trims) do
        local onlyBars = true   -- a block with the bag bar or micro menu never fades
        for _, mb in ipairs(panel.members or {}) do if not mb.gi then onlyBars = false end end
        local target = onlyBars and panelAlpha[panel] or 1
        if panel:GetAlpha() ~= target then panel:SetAlpha(target) end
    end
    -- Keep the trim fitted to the bars (twice a second is plenty).
    trimTick = trimTick + 1
    if trimTick >= 5 then
        trimTick = 0
        local pa = PanelAlpha()
        if pa ~= lastPanelAlpha then
            lastPanelAlpha = pa
            for _, list in ipairs(groups) do
                for _, b in ipairs(list) do if b.cleanEdge then EdgeColor(b.cleanEdge) end end
            end
            for _, b in ipairs(MicroButtonList()) do if b.aetherEdge then EdgeColor(b.aetherEdge) end end
        end
        MatchUtilitySizes()
        LayoutTrims()
    end
end

local function RefreshLook()
    for _, list in ipairs(groups) do
        for _, b in ipairs(list) do
            if b.cleanEdge then EdgeColor(b.cleanEdge) end
            local macro = b.Name or _G[(b:GetName() or "") .. "Name"]
            if macro then macro:SetAlpha(db.hideMacro and 0 or 1) end
        end
    end
    for _, b in ipairs(MicroButtonList()) do
        if b.aetherEdge then EdgeColor(b.aetherEdge) end
    end
    UpdateFade()
end

local f = CreateFrame("Frame")
f:RegisterEvent("ADDON_LOADED")
f:RegisterEvent("PLAYER_ENTERING_WORLD")
f:RegisterEvent("UPDATE_BONUS_ACTIONBAR")
f:RegisterEvent("ACTIONBAR_PAGE_CHANGED")
f:RegisterEvent("PLAYER_REGEN_ENABLED")
f:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" and arg1 == ADDON then
        -- CleanBarsDB holds settings from before the rename (present only right after
        -- migrating). Then the per-character copy (WoW Forever may not load account-wide
        -- settings back), then the account-wide one.
        local saved
        local sources = { CleanBarsDB, AetherBarsCharDB, AetherBarsDB }
        for i = 1, 3 do              -- not ipairs: it stops at the first nil
            local source = sources[i]
            if type(source) == "table" and next(source) then saved = source; break end
        end
        saved = saved or {}
        for k, v in pairs(defaults) do
            if saved[k] == nil then saved[k] = v end
        end
        db = saved
        -- 1.9.1: bars no longer dim when idle (the slider can still bring it back).
        if not db.noDim191 then db.alpha = 1; db.noDim191 = true end
        -- 1.13.4: an older Align saved a spot for the side bar, which threw
        -- off the quest tracker. Forget it once; Blizzard places it again.
        if not db.sideFix1134 then
            if type(db.align) == "table" then db.align.MultiBarRight = nil; db.align.MultiBarLeft = nil end
            if type(db.alignUndo) == "table" then db.alignUndo.MultiBarRight = nil; db.alignUndo.MultiBarLeft = nil end
            db.sideFix1134 = true
        end
        AetherBarsDB, AetherBarsCharDB = db, db
        CleanBarsDB = nil
        if type(db.xp) ~= "table" then db.xp = {} end
    elseif event == "PLAYER_ENTERING_WORLD" then
        -- Put everything in its saved place right away, while the loading
        -- screen is still up, so nothing visibly jumps afterwards. The later
        -- passes only catch things the game creates late; they don't move
        -- anything that's already in place.
        ApplyAll()
        ApplyAlign()
        LayoutTrims()
        C_Timer.After(1, HideArt)   -- catch art that loads late
        C_Timer.After(3, function() ApplyAll(); ApplyAlign() end)
        if _G.EditModeManagerFrame and not alignEditHooked then
            alignEditHooked = true
            -- Edit Mode open: pause Align so bars can be dragged. When it closes,
            -- Align puts its layout back unless you actually dragged a bar.
            -- (Opening or closing Edit Mode makes Blizzard move bars itself,
            -- so we watch for your drags rather than comparing positions.)
            local dragged = false
            local watched = {}
            local function Watch(frame)
                if frame and frame.HookScript and not watched[frame] then
                    watched[frame] = true
                    frame:HookScript("OnDragStop", function() if alignSuspended then dragged = true end end)
                end
            end
            local em = _G.EditModeManagerFrame
            if em.OnSystemPositionChange then
                hooksecurefunc(em, "OnSystemPositionChange", function() if alignSuspended then dragged = true end end)
            end
            em:HookScript("OnShow", function()
                alignSuspended = true
                dragged = false
                for name in pairs(db.align or {}) do Watch(_G[name]) end
                for _, n in ipairs({ "BagsBar", "MicroMenu", "MicroMenuContainer", "MicroButtonAndBagsBar" }) do Watch(_G[n]) end
            end)
            em:HookScript("OnHide", function()
                alignSuspended = false
                if dragged then ReleaseAlign() else ApplyAlign() end
                MatchUtilitySizes(); LayoutTrims()
            end)
        end
    elseif event == "PLAYER_REGEN_ENABLED" then
        if sizePending then MatchSizes() end
        if alignPending then ApplyAlign() end
        MatchUtilitySizes()
    elseif db then
        HideArt()
    end
end)

local elapsed = 0
f:SetScript("OnUpdate", function(_, dt)
    elapsed = elapsed + dt
    if elapsed < 0.1 or not db then return end
    elapsed = 0
    UpdateFade()
end)

-- /aetherbars or /cb
Print = function(msg) print("|cff66ccffAetherBars:|r " .. msg) end
local function OnOff(v) return v and "on" or "off" end

SLASH_AETHERBARS1, SLASH_AETHERBARS2 = "/aetherbars", "/cb"
SlashCmdList.AETHERBARS = function(input)
    local cmd, val = strsplit(" ", strlower(strtrim(input or "")), 2)
    if cmd == "alpha" and tonumber(val) then
        db.alpha = math.max(0, math.min(1, tonumber(val)))
        Print("Idle transparency set to " .. db.alpha)
    elseif cmd == "edge" and tonumber(val) then
        db.edgeAlpha = math.max(0, math.min(1, tonumber(val)))
        Print("Edge darkness set to " .. db.edgeAlpha)
    elseif cmd == "combat" then
        db.combat = (val == "on"); Print("Solid in combat: " .. OnOff(db.combat))
    elseif cmd == "mouseover" then
        db.mouseover = (val == "on"); Print("Solid on mouseover: " .. OnOff(db.mouseover))
    elseif cmd == "trim" then
        db.trim = (val == "on")
        Print("Aether trim: " .. OnOff(db.trim))
        RefreshLook(); TrimXP(); LayoutTrims()
    elseif cmd == "macro" then
        db.hideMacro = (val ~= "on"); Print("Macro names: " .. OnOff(not db.hideMacro))
    elseif cmd == "align" and (val == "center on" or val == "center off") then
        db.alignCenter = (val == "center on")
        Print("Align centers the bars: " .. OnOff(db.alignCenter) .. ". Click Align Bars to apply.")
    elseif cmd == "align" then
        DoAlign(val)
    elseif cmd == "size" and (val == "bar2" or val == "all" or val == "off") then
        db.size = val
        Print("Button size matching: " .. val .. (val == "off" and " (type /reload to restore sizes)" or ""))
        MatchSizes(); MatchUtilitySizes()
    elseif cmd == "xp" then
        local sub, num = strsplit(" ", val or "", 2)
        num = tonumber(num)
        if sub == "width" and num and xpBar then
            DetachXP(); xpBar:SetWidth(num); SaveXP()
            Print("XP bar width " .. num)
        elseif sub == "height" and num and xpBar then
            DetachXP(); xpBar:SetHeight(num); SaveXP()
            Print("XP bar height " .. num)
        elseif sub == "reset" then
            db.xp = {}
            Print("XP bar size and position reset. Type /reload to apply.")
        elseif sub == "unlock" then
            SetXPUnlocked(true)
        elseif sub == "lock" then
            SetXPUnlocked(false)
        else
            SetXPUnlocked()
        end
        return
    elseif cmd == "glow" then
        db.readyGlow = (val ~= "off"); Print("Cooldown glow (red to green): " .. OnOff(db.readyGlow))
    elseif cmd == "art" then
        db.hideArt = (val ~= "on")
        Print("Bar art " .. (db.hideArt and "hidden" or "shown after /reload"))
        HideArt()
    elseif cmd == "debug" then
        Print("Interface " .. select(4, GetBuildInfo()) .. ", bars found:")
        local found = 0
        for _, bar in ipairs(BARS) do
            local first = _G[bar[1] .. "1"]
            if first then
                found = found + 1
                print("  " .. bar[1] .. "  styled=" .. tostring(first.cleanStyled))
            end
        end
        if found == 0 then print("  none (bar names differ in this client)") end
        local n = 0
        for _ in pairs(killed) do n = n + 1 end
        local names = {}
        for frame in pairs(scanned) do names[#names + 1] = frame:GetName() or "unnamed" end
        print("  Art textures hidden: " .. n .. "  in: " .. table.concat(names, ", "))
        local focus = GetMouseFoci and GetMouseFoci()[1] or (GetMouseFocus and GetMouseFocus())
        local fname = focus and focus.GetName and focus:GetName()
        print("  Under your mouse: " .. tostring(fname or "unnamed frame"))
        print("  XP bar: " .. tostring(xpBar and (xpBar:GetName() or "unnamed") or "not found"))
        -- Textures still showing around Action Bar 1 (not on the buttons themselves).
        local main, shown = MainBar(), {}
        if main and main[1] then
            local buttons = {}
            for _, b in ipairs(main) do buttons[b] = true end
            local function Look(frame, depth)
                if depth > 4 or buttons[frame] or (frame.IsForbidden and frame:IsForbidden()) then return end
                for _, r in ipairs({ frame:GetRegions() }) do
                    if r:IsObjectType("Texture") and r:IsShown() and r:GetAlpha() > 0 and not killed[r] then
                        shown[#shown + 1] = (frame:GetName() or "unnamed") .. "." .. (r:GetName() or r:GetDrawLayer() or "?")
                            .. string.format(" %dx%d", r:GetWidth() or 0, r:GetHeight() or 0)
                    end
                end
                for _, child in ipairs({ frame:GetChildren() }) do Look(child, depth + 1) end
            end
            local p = main[1]:GetParent()
            if p and p ~= UIParent then Look(p, 1) end
        end
        print("  Bar 1 textures still showing: " .. #shown)
        for i = 1, math.min(#shown, 12) do print("    " .. shown[i]) end
        if focus and focus.GetParent and focus:GetParent() and focus:GetParent().GetName then
            print("  Its parent: " .. tostring(focus:GetParent():GetName()))
        end
        return
    elseif cmd == "reset" then
        for k, v in pairs(defaults) do db[k] = v end
        Print("Settings reset. Type /reload to apply everything.")
    else
        Print("Commands:")
        print("  /cb alpha 0-1      idle transparency (now " .. db.alpha .. ")")
        print("  /cb edge 0-1       icon edge darkness (now " .. db.edgeAlpha .. ")")
        print("  /cb combat on|off  solid in combat (now " .. OnOff(db.combat) .. ")")
        print("  /cb mouseover on|off  solid on hover (now " .. OnOff(db.mouseover) .. ")")
        print("  /cb macro on|off   show macro names (now " .. OnOff(not db.hideMacro) .. ")")
        print("  /cb art on|off     show default bar art (now " .. OnOff(not db.hideArt) .. ")")
        print("  /cb glow on|off    red-to-green cooldown glow (now " .. OnOff(db.readyGlow) .. ")")
        print("  /cb size bar2|all|off  match button size to Action Bar 1 (now " .. db.size .. ")")
        print("  /cb align          line up your bars neatly (/cb align undo to put them back)")
        print("  /cb align center on|off   also center them on screen (now " .. OnOff(db.alignCenter ~= false) .. ")")
        print("  /cb xp             unlock/lock the XP bar to drag and resize it")
        print("  /cb xp width 800   /cb xp height 8   exact XP bar size")
        print("  /cb xp reset       put the XP bar back where it was")
        print("  /cb reset          restore defaults")
        return
    end
    RefreshLook()
end
