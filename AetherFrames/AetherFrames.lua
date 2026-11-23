-- AetherFrames: player, pet, target and party frames in the Aether look.
-- A round portrait crest (blue ring, gold ring, gold chevron accents) with a capsule
-- of bars that slides out from behind it; the capsule, bars and gold name line
-- are notched to follow the ring. Frames fade out of combat (text and faces
-- stay solid), and work like Blizzard's: click to target, right-click menu.

local ADDON = ...
local PREFIX = "|cff4da6ffAetherFrames:|r "
local function Print(msg) print(PREFIX .. msg) end

local defaults = {
    enabled     = true,   -- replace Blizzard's player, pet and target frames
    alpha       = 0.5,    -- frames and bars out of combat (text and faces stay solid)
    fadeFaces   = false,  -- fade the portraits too
    buffs       = true,   -- the target's buffs and debuffs under its frame
    myBuffs     = false,  -- your own buffs in your frame (Blizzard shows them top right)
    petPower    = false,  -- numbers on the pet's resource bar (makes it taller; reload)
    scale       = 1,
    locked      = true,
    threat      = true,   -- glow around the portrait when you (or your pet) have threat
    party       = true,   -- party frames in the Aether look (Blizzard's hidden; reload)
    tot         = true,   -- target of target, under the target frame (reload)
}

local db
local frames = {}
local inCombat = false

local BLUE   = { 0.30, 0.70, 1.00 }
local GOLD   = { 1.00, 0.82, 0.00 }
local DARK   = { 0.043, 0.051, 0.071 }   -- inside the rings
local PANEL  = { 0.051, 0.051, 0.051 }   -- capsule fill (AetherMeter's window color)
local BARBG  = { 0.024, 0.039, 0.071 }
local CIRCLE = "Interface\\CHARACTERFRAME\\TempPortraitAlphaMask"

local function IsSecret(v) return issecretvalue ~= nil and issecretvalue(v) end

-- ==========================================
-- FONTS
-- ==========================================
local function MakeFont(name, size, outline)
    local f = CreateFont(name)
    local file = (GameFontNormal and GameFontNormal:GetFont()) or "Fonts\\FRIZQT__.TTF"
    f:SetFont(file, size, outline and "OUTLINE" or "")
    f:SetShadowColor(0, 0, 0, 1)
    f:SetShadowOffset(1, -1)
    return f
end
-- Names and levels: Fira Sans Bold (SIL Open Font License, see
-- Media\\FiraSans-OFL.txt), heavier than WoW's font so they stand out.
-- If it can't load, WoW's own font is kept.
local NAME_FILE = "Interface\\AddOns\\AetherFrames\\Media\\FiraSans-Bold.ttf"
local function NameFont(name, size)
    local f = MakeFont(name, size, true)
    local ok, set = pcall(f.SetFont, f, NAME_FILE, size, "OUTLINE")
    if not ok or set == false then
        f:SetFont((GameFontNormal and GameFontNormal:GetFont()) or "Fonts\\FRIZQT__.TTF", size, "")
    end
    return f
end
local NAME_FONT     = NameFont("AetherFramesNameFont", 12)
local NAME_FONT_SM  = NameFont("AetherFramesNameSmallFont", 11)
-- Level badges: white numbers with a black outline, readable on every
-- badge color (red and orange included).
local function BadgeFont(name, size)
    local f = MakeFont(name, size, true)
    f:SetShadowOffset(0, 0)
    pcall(f.SetFont, f, NAME_FILE, size, "OUTLINE")
    return f
end
local BADGE_FONT    = BadgeFont("AetherFramesBadgeFont", 11)
local BADGE_FONT_SM = BadgeFont("AetherFramesBadgeSmallFont", 9)
local NUM_FONT      = MakeFont("AetherFramesNumberFont", 11, true)
local TIMER_FONT    = MakeFont("AetherFramesTimerFont", 10, true)

-- ==========================================
-- SHAPES (all in frame units, measured from the frame's ring side)
-- ==========================================
-- Each frame is laid out as if the ring were on the left; the target frame
-- mirrors every x. Textures that fade are kept in f.soft with their own alpha.

local function Tex(f, layer, sub, color, a, soft)
    local t = f:CreateTexture(nil, layer, nil, sub)
    t:SetColorTexture(color[1], color[2], color[3], 1)
    t.baseAlpha = a or 1
    t:SetAlpha(t.baseAlpha)
    if soft then f.soft[#f.soft + 1] = t end
    return t
end

-- Place a texture by its left edge x (from the ring side), top y and size.
local function Place(f, t, x, y, w, h)
    t:ClearAllPoints()
    if f.mirror then
        t:SetPoint("TOPRIGHT", f, "TOPRIGHT", -x, -y)
    else
        t:SetPoint("TOPLEFT", f, "TOPLEFT", x, -y)
    end
    t:SetSize(math.max(0.01, w), math.max(0.01, h))
end

-- Smooth, pre-drawn shapes (Media\*.tga: white with soft edges, tinted here).
-- Pixel snapping is off so they stay smooth at any scale. `flip` mirrors
-- the image on the target frame.
local ART = "Interface\\AddOns\\AetherFrames\\Media\\"
local function Art(f, layer, sub, file, color, a, soft, x, y, w, h, flip)
    local t = f:CreateTexture(nil, layer, nil, sub)
    t:SetTexture(ART .. file)
    t:SetVertexColor(color[1], color[2], color[3], 1)
    if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false) end
    if t.SetTexelSnappingBias then t:SetTexelSnappingBias(0) end
    if flip and f.mirror then t:SetTexCoord(1, 0, 0, 1) end
    t.baseAlpha = a or 1
    t:SetAlpha(t.baseAlpha)
    if soft then f.soft[#f.soft + 1] = t end
    Place(f, t, x, y, w, h)
    return t
end

-- Center a texture at (x, y) from the ring side / top.
local function PlaceCenter(f, t, x, y)
    t:ClearAllPoints()
    t:SetPoint("CENTER", f, "TOPLEFT", f.mirror and (f.w - x) or x, -y)
end

-- A ring drawn from short segments, so it's hollow (and fades cleanly).
local function Ring(f, layer, sub, cx, cy, r, thick, color, a)
    local n = math.max(24, math.floor(2 * math.pi * r / 2.5))
    local len = 2 * math.pi * r / n
    for i = 0, n - 1 do
        local ang = (i + 0.5) / n * 2 * math.pi
        local t = Tex(f, layer, sub, color, a, true)
        t:SetSize(len + 0.3, thick)
        PlaceCenter(f, t, cx + r * math.cos(ang), cy + r * math.sin(ang))
        if t.SetRotation then t:SetRotation(f.mirror and (ang - math.pi / 2) or (math.pi / 2 - ang)) end
    end
end

-- A filled circle (the circle mask used as a texture, tinted).
local function Disc(f, layer, sub, cx, cy, d, color, a, soft)
    local t = f:CreateTexture(nil, layer, nil, sub)
    t:SetTexture(CIRCLE)
    t:SetVertexColor(color[1], color[2], color[3], 1)
    t.baseAlpha = a or 1
    t:SetAlpha(t.baseAlpha)
    if soft then f.soft[#f.soft + 1] = t end
    t:SetSize(d, d)
    PlaceCenter(f, t, cx, cy)
    return t
end

-- Chevron accent: a thick gold chevron with a fine echo, pointing away from
-- the crest, on a dark backing that hugs its shape. Mirrored on the target.
local CHEV_BOX = { [80] = 22.49, [58] = 16.76 }       -- art box size (units), from the generator
local function Chevron(f, cx, cy, dir)
    local S = f.spec.S
    local box = CHEV_BOX[S] or 22.49
    local made = {}
    for _, g in ipairs({ { "dark", DARK, 5 }, { "gold", GOLD, 6 } }) do
        made[#made + 1] = Art(f, "OVERLAY", g[3], "chev" .. S .. "_" .. dir .. "_" .. g[1], g[2], 1, true, cx - box / 2, cy - box / 2, box, box, true)
    end
    return made
end

-- Class glyphs (original Aether designs), by the game's class tokens.
local CLASS_GLYPH = {
    HUNTER = "hunter", MAGE = "mage", WARRIOR = "warrior", ROGUE = "rogue", PRIEST = "priest",
    PALADIN = "paladin", DRUID = "druid", SHAMAN = "shaman", WARLOCK = "warlock",
}

local function Circle(cx, R, dy)
    if math.abs(dy) >= R then return cx end
    return cx + math.sqrt(R * R - dy * dy)
end

-- ==========================================
-- BUILDING A FRAME
-- ==========================================
-- spec: unit, mirror, S (ring size), capW (capsule length from the ring's
-- center), padTop, nameH, bars = { { kind, h, gap, text } }, padBottom,
-- textInset (text start from the ring's center), padRight.
local function Build(name, spec)
    local f = CreateFrame("Button", name, UIParent, "SecureUnitButtonTemplate")
    f.unit, f.mirror, f.spec = spec.unit, spec.mirror, spec
    f.soft = {}
    local S, R = spec.S, spec.S / 2
    local capH = spec.padTop + spec.nameH
    for _, b in ipairs(spec.bars) do capH = capH + b.gap + b.h end
    capH = capH + spec.padBottom
    f.w = R + spec.capW
    f.h = math.max(S, capH) + 12          -- room for the gems
    f:SetSize(f.w, f.h)
    local cx, cy = R + 6, f.h / 2          -- 6: room for the side gem
    f.w = f.w + 6
    f:SetSize(f.w, f.h)
    f.cx, f.cy, f.R = cx, cy, R

    -- Click to target, right-click for the menu (Blizzard's secure handling).
    f:SetAttribute("unit", spec.unit)
    f:SetAttribute("type1", "target")
    f:SetAttribute("type2", "togglemenu")
    f:RegisterForClicks("AnyUp")
    f:SetScript("OnEnter", function(self)
        if UnitFrame_OnEnter then pcall(UnitFrame_OnEnter, self)
        else GameTooltip_SetDefaultAnchor(GameTooltip, self); GameTooltip:SetUnit(self.unit); GameTooltip:Show() end
    end)
    f:SetScript("OnLeave", function(self)
        if UnitFrame_OnLeave then pcall(UnitFrame_OnLeave, self) else GameTooltip:Hide() end
    end)

    -- Capsule: one smooth image for the fill (cut to the ring's curve, with
    -- a rounded end) and one for its outline.
    local capTop = (f.h - capH) / 2
    local rr = capH / 2
    local xc = cx + spec.capW - rr
    local key = spec.art
    Art(f, "BACKGROUND", 0, "cap_" .. key .. "_fill", PANEL, 0.92, true, cx, capTop, spec.capW, capH, true)
    Art(f, "BORDER", 0, "cap_" .. key .. "_edge", BLUE, 1, true, cx, capTop, spec.capW, capH, true)
    -- Where the name line ends on the far side: following the rounded end,
    -- the same clearance as at the ring.
    local function FarX(dy)
        local r = rr - 4
        if math.abs(dy) >= r then return xc end
        return xc + math.sqrt(r * r - dy * dy)
    end

    -- The crest: dark disc, blue ring, gold ring, portrait, chevron accents.
    local inner = S - (S > 60 and 14 or 10)
    Art(f, "ARTWORK", 0, "crest" .. S .. "_dark", DARK, 1, true, cx - R, cy - R, S, S)
    Art(f, "ARTWORK", 2, "crest" .. S .. "_blue", BLUE, 1, true, cx - R, cy - R, S, S)
    Art(f, "ARTWORK", 2, "crest" .. S .. "_gold", GOLD, 1, true, cx - inner / 2, cy - inner / 2, inner, inner)
    -- Threat halo: a soft glow just outside the blue ring, under everything
    -- else. Hidden until there's threat; it doesn't fade with the frame.
    local HS = S + 34
    -- One layer per look (solid, fast pulse, slow pulse, dim), all the same
    -- glow: each is switched on by its own alpha, which can come straight
    -- from the game's (possibly hidden) threat level through a curve.
    f.glow = {}
    for _, k in ipairs({ "solid", "fast", "slow", "dim" }) do
        local t = Art(f, "BACKGROUND", -8, "halo" .. S, BLUE, 1, false, cx - HS / 2, cy - HS / 2, HS, HS)
        t:SetAlpha(0)
        f.glow[k] = t
    end
    local face = f:CreateTexture(nil, "ARTWORK", nil, 1)
    face:SetSize(inner - 2, inner - 2)
    PlaceCenter(f, face, cx, cy)
    if face.AddMaskTexture and f.CreateMaskTexture then
        local mask = f:CreateMaskTexture()
        mask:SetTexture(CIRCLE, "CLAMPTOBLACKADDITIVE", "CLAMPTOBLACKADDITIVE")
        mask:SetAllPoints(face)
        face:AddMaskTexture(mask)
    end
    f.face = face
    Chevron(f, cx, cy - (R - 1), "up")
    f.sideChev = Chevron(f, cx + (R - 1), cy, "right")   -- capsule side; hidden while the class medallion shows
    if spec.badge ~= "level" then Chevron(f, cx, cy + (R - 1), "down") end

    -- Badge at 6 o'clock: the level (gold for you, your pet and your party;
    -- the target's in its difficulty color). Drawn on its own
    -- small frame so it sits above the ring; it never fades.
    if spec.badge then
        local BD = S > 60 and 20 or 16          -- a little smaller on the pet's crest
        local RD = BD + 3
        local b = CreateFrame("Frame", nil, f)
        b:SetFrameLevel(f:GetFrameLevel() + 4)
        b:SetSize(RD, RD)
        b:SetPoint("CENTER", f, "TOPLEFT", f.mirror and (f.w - cx) or cx, -(cy + R - 1))
        local function Img(layer, sub, file, color, size)
            local t = b:CreateTexture(nil, layer, nil, sub)
            t:SetTexture(ART .. file)
            t:SetVertexColor(color[1], color[2], color[3], 1)
            if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false); t:SetTexelSnappingBias(0) end
            t:SetSize(size, size)
            t:SetPoint("CENTER")
            return t
        end
        Img("BACKGROUND", 0, "badge_rim", { 0.04, 0.04, 0.055 }, RD)
        if spec.badge == "level" then
            b.disc = Img("ARTWORK", 0, "badge_disc", GOLD, BD)
            -- "??" (far too high to tell): a red ring around a black center,
            -- the same outer size as the badge, so it reads as a warning.
            b.warnRing = Img("ARTWORK", 2, "badge_disc", { 1, 0.13, 0.13 }, RD)
            b.warnHole = Img("ARTWORK", 3, "badge_disc", { 0.04, 0.04, 0.055 }, RD * 0.62)
            b.warnRing:Hide(); b.warnHole:Hide()
            b.text = b:CreateFontString(nil, "OVERLAY")
            b.text:SetFontObject(BADGE_FONT)
            b.text:SetTextColor(1, 1, 1)
            -- Fira's digits sit a little left in their own space (measured
            -- in game: about 1 to 1.5 pixels), so nudge them right to center.
            b.text:SetPoint("CENTER", 1, 0)
        else
            -- happy (gold, smile), content (blue, straight), unhappy (red, frown)
            b.layers = {}
            for i, look in ipairs({ { "face_sad", { 0.90, 0.20, 0.20 } }, { "face_neutral", BLUE }, { "face_happy", GOLD } }) do
                b.layers[i] = { Img("ARTWORK", i, "badge_disc", look[2], BD), Img("OVERLAY", i, look[1], { 0.07, 0.07, 0.09 }, BD) }
            end
            b:Hide()
        end
        f.badge = b
    end
    Chevron(f, cx - (R - 1), cy, "left")

    -- Medallion at 3 o'clock (the capsule side): for player characters, a
    -- dark disc with a fine gold rim and the class glyph; on your pet's
    -- crest, its happiness face instead.
    if spec.badge == "level" then
        local MD = S > 60 and 23 or 17          -- smaller on the party crests
        local MR = S > 60 and 20 or 15
        local m = CreateFrame("Frame", nil, f)
        m:SetFrameLevel(f:GetFrameLevel() + 4)
        m:SetSize(MD, MD)
        m:SetPoint("CENTER", f, "TOPLEFT", f.mirror and (f.w - (cx + R - 1)) or (cx + R - 1), -cy)
        local function Img(layer, sub, file, color, size)
            local t = m:CreateTexture(nil, layer, nil, sub)
            t:SetTexture(ART .. file)
            t:SetVertexColor(color[1], color[2], color[3], 1)
            if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false); t:SetTexelSnappingBias(0) end
            t:SetSize(size, size)
            t:SetPoint("CENTER")
            return t
        end
        Img("BACKGROUND", 0, "badge_rim", { 0.04, 0.04, 0.055 }, MD)
        if spec.medal == "happy" then
            -- happy (gold, smile), content (blue, straight), unhappy (red, frown)
            m.layers = {}
            for i, look in ipairs({ { "face_sad", { 0.90, 0.20, 0.20 } }, { "face_neutral", BLUE }, { "face_happy", GOLD } }) do
                m.layers[i] = { Img("ARTWORK", i, "badge_disc", look[2], MR), Img("OVERLAY", i, look[1], { 0.07, 0.07, 0.09 }, MR) }
            end
            m:Hide()
            f.happyMedal = m
        else
            Img("ARTWORK", 0, "medal_ring", GOLD, MR)
            m.glyph = Img("OVERLAY", 0, "class_hunter", GOLD, MR)
            m:Hide()
            f.classMedal = m
        end
    end

    -- Name row: name, level, and a gold line notched to the ring.
    local gapR = R + 3                                   -- bars and lines stop 3 short of the ring
    local barRight = cx + spec.capW - spec.padRight
    local textX = cx + spec.textInset
    local y = capTop + spec.padTop
    local nameFS = f:CreateFontString(nil, "OVERLAY")
    nameFS:SetFontObject(spec.small and NAME_FONT_SM or NAME_FONT)
    nameFS:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
    nameFS:SetJustifyH(f.mirror and "RIGHT" or "LEFT")
    nameFS:SetWordWrap(false)
    Place(f, nameFS, textX, y, barRight - textX - (spec.badge == "level" and 0 or 30), spec.nameH - 2)
    f.nameFS = nameFS
    local levelFS = f:CreateFontString(nil, "OVERLAY")
    levelFS:SetFontObject(spec.small and NAME_FONT_SM or NAME_FONT)
    levelFS:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
    levelFS:SetJustifyH(f.mirror and "LEFT" or "RIGHT")
    Place(f, levelFS, barRight - 30 - 5, y, 30, spec.nameH - 2)
    f.levelFS = levelFS
    local lineY = y + spec.nameH - 1
    local lineX = Circle(cx, gapR, lineY + 0.5 - cy)
    local line = Tex(f, "OVERLAY", 0, GOLD, 0.7, false)  -- part of the text: stays solid
    Place(f, line, lineX, lineY, FarX(lineY + 0.5 - cy) - lineX, 1)
    y = y + spec.nameH

    -- Bars: a smooth background and outline (cut to the ring's curve and the
    -- rounded end), and one status bar clipped to the same shape by a mask,
    -- so the fill sweeps cleanly across both curves.
    f.bars = {}
    for i, b in ipairs(spec.bars) do
        y = y + b.gap
        local bar = { kind = b.kind }
        Art(f, "BORDER", 1, "bar_" .. key .. "_" .. i .. "_bg", BARBG, 0.5, true, cx, y, spec.capW, b.h, true)
        Art(f, "BORDER", 2, "bar_" .. key .. "_" .. i .. "_edge", BLUE, 0.35, true, cx, y, spec.capW, b.h, true)
        -- the fill's rect: the inner shape's left- and rightmost points
        -- (same formula as the art generator)
        local P0 = math.min(Circle(cx, gapR + 1, (y + 1) - cy), Circle(cx, gapR + 1, (y + b.h - 1) - cy))
        local lo, hi = (y + 1) - cy, (y + b.h - 1) - cy
        local dmin = (lo <= 0 and hi >= 0) and 0 or math.min(math.abs(lo), math.abs(hi))
        local P1 = xc - 1
        if dmin < rr - 5 then P1 = math.max(P1, xc + math.sqrt((rr - 5) ^ 2 - dmin ^ 2)) end
        local sb = CreateFrame("StatusBar", nil, f)
        sb:SetStatusBarTexture("Interface\\Buttons\\WHITE8X8")
        if f.mirror and sb.SetReverseFill then sb:SetReverseFill(true) end
        Place(f, sb, P0, y + 1, P1 - P0, b.h - 2)
        sb:SetMinMaxValues(0, 1)
        sb:SetValue(1)
        local fillTex = sb:GetStatusBarTexture()
        if fillTex then
            if fillTex.SetSnapToPixelGrid then fillTex:SetSnapToPixelGrid(false); fillTex:SetTexelSnappingBias(0) end
            if fillTex.AddMaskTexture and f.CreateMaskTexture then
                local mask = f:CreateMaskTexture()
                mask:SetTexture(ART .. "bar_" .. key .. "_" .. i .. (f.mirror and "_maskm" or "_mask"),
                    "CLAMPTOBLACKADDITIVE", "CLAMPTOBLACKADDITIVE")
                mask:SetAllPoints(sb)
                fillTex:AddMaskTexture(mask)
            end
        end
        bar.sb = sb
        f.soft[#f.soft + 1] = sb

        if b.text then
            local left = f:CreateFontString(nil, "OVERLAY")
            left:SetFontObject(NUM_FONT)
            left:SetJustifyH("LEFT")
            local right = f:CreateFontString(nil, "OVERLAY")
            right:SetFontObject(NUM_FONT)
            right:SetJustifyH("RIGHT")
            -- text lives on a frame above the bar so the bar's fading leaves it solid
            local holder = CreateFrame("Frame", nil, f)
            holder:SetFrameLevel(f:GetFrameLevel() + 3)
            holder:SetAllPoints(f)
            left:SetParent(holder); right:SetParent(holder)
            Place(f, left, textX, y, 90, b.h)
            Place(f, right, barRight - 5 - 90, y, 90, b.h)
            if f.mirror then left:SetJustifyH("RIGHT"); right:SetJustifyH("LEFT") end
            bar.pctFS, bar.valFS = left, right
        end
        f.bars[#f.bars + 1] = bar
        y = y + b.h
    end
    f.capBottom = capTop + capH
    f.capTop = capTop
    f:Hide()
    frames[spec.unit] = f
    return f
end

-- ==========================================
-- UPDATES
-- ==========================================
local function Thousands(n)
    local s = tostring(math.floor(n + 0.5))
    local out = s:reverse():gsub("(%d%d%d)", "%1,"):reverse()
    return (out:gsub("^,", ""))
end

local function SetValues(bar, cur, max, pctFn, empty)
    if empty or (not IsSecret(max) and (max == nil or max <= 0)) then
        -- Dead, or no power at all (a mob without mana): empty, no numbers.
        bar.sb:SetMinMaxValues(0, 1); bar.sb:SetValue(0)
        if bar.pctFS then
            bar.pctFS:SetText("")
            bar.valFS:SetText((empty and not IsSecret(max) and max ~= nil and max > 0) and "0" or "")
        end
        return
    end
    bar.sb:SetMinMaxValues(0, max)
    bar.sb:SetValue(cur)
    if not bar.pctFS then return end
    if not IsSecret(cur) and not IsSecret(max) then
        bar.valFS:SetText(Thousands(cur))
        bar.pctFS:SetText(math.floor(cur / max * 100 + 0.5) .. "%")
    else
        -- In combat the game may hand out hidden ("secret") numbers: they can be
        -- shown but not worked with, so show the number as is.
        pcall(bar.valFS.SetText, bar.valFS, cur)
        -- The game's percent comes back 0 to 1 unless it's given its 0-to-100
        -- curve (CurveConstants.ScaleTo100); without that curve, skip it.
        if pctFn and CurveConstants and CurveConstants.ScaleTo100 then
            local ok = pcall(function() bar.pctFS:SetFormattedText("%.0f%%", pctFn()) end)
            if not ok then bar.pctFS:SetText("") end
        else
            bar.pctFS:SetText("")
        end
    end
end

local function SetBarColor(bar, r, g, b)
    bar.sb:SetStatusBarColor(r, g, b)
end

-- Level difficulty, Blizzard's five colors: red (5+ levels above you),
-- orange (3-4 above), yellow (within 2), green (lower but still worth
-- experience), gray (too low to give any).
local DIFF = {
    red = { 1, 0.13, 0.13 }, orange = { 1, 0.5, 0.13 }, yellow = GOLD,
    green = { 0.25, 0.75, 0.25 }, gray = { 0.55, 0.55, 0.55 },
}
local function GrayLevel(my)
    if GetQuestGreenRange then
        local ok, r = pcall(GetQuestGreenRange)
        if ok and not IsSecret(r) and r then return my - r - 1 end
    end
    -- Classic's rule
    if my <= 5 then return 0 end
    if my <= 39 then return my - math.floor(my / 10) - 5 end
    if my <= 59 then return my - math.floor(my / 5) - 1 end
    return my - 12
end
local function Difficulty(lvl)
    local my = UnitLevel("player")
    if IsSecret(my) or not my then return DIFF.yellow end
    local d = lvl - my
    if d >= 5 then return DIFF.red end
    if d >= 3 then return DIFF.orange end
    if d >= -2 then return DIFF.yellow end
    if lvl > GrayLevel(my) then return DIFF.green end
    return DIFF.gray
end

local function NameColor(unit)
    if UnitIsPlayer(unit) and not UnitIsEnemy("player", unit) then return GOLD end
    local reaction = UnitReaction(unit, "player")
    if UnitIsEnemy("player", unit) or (reaction and reaction <= 3) then return { 1, 0.42, 0.42 } end
    if reaction == 4 then return { 1, 0.85, 0.3 } end
    return GOLD
end

local function IsParty(u) return type(u) == "string" and u:match("^party%d$") ~= nil end

-- Offline party members: gray name and bars, "Offline", a gray portrait.
local function Offline(u)
    if not IsParty(u) or not UnitIsConnected then return false end
    local ok, on = pcall(UnitIsConnected, u)
    return ok and not IsSecret(on) and on == false
end

local function UpdateHealth(f)
    local u = f.unit
    if not UnitExists(u) then return end
    local bar = f.bars[1]
    if Offline(u) then
        bar.sb:SetMinMaxValues(0, 1); bar.sb:SetValue(1)
        SetBarColor(bar, 0.4, 0.4, 0.4)
        if bar.pctFS then bar.pctFS:SetText("Offline"); bar.valFS:SetText("") end
        return
    end
    local dead = UnitIsDeadOrGhost(u)
    SetValues(bar, UnitHealth(u), UnitHealthMax(u), UnitHealthPercent and function()
        return UnitHealthPercent(u, true, CurveConstants and CurveConstants.ScaleTo100)
    end, dead)
    SetBarColor(bar, 0.184, 0.620, 0.267)
end

local function UpdatePower(f)
    local bar = f.bars[2]
    if not bar then return end
    local u = f.unit
    if not UnitExists(u) then return end
    if Offline(u) then
        bar.sb:SetMinMaxValues(0, 1); bar.sb:SetValue(0)
        if bar.pctFS then bar.pctFS:SetText(""); bar.valFS:SetText("") end
        return
    end
    local ptype, token = UnitPowerType(u)
    local c = (PowerBarColor and (PowerBarColor[token] or PowerBarColor[ptype])) or { r = 0.11, g = 0.44, b = 0.82 }
    local r, g, b = c.r, c.g, c.b
    if token == "MANA" or ptype == 0 then r, g, b = 0.11, 0.44, 0.82 end
    if token == "FOCUS" or ptype == 2 then r, g, b = 0.88, 0.48, 0.18 end
    SetValues(bar, UnitPower(u), UnitPowerMax(u), UnitPowerPercent and function()
        return UnitPowerPercent(u, ptype, false, CurveConstants and CurveConstants.ScaleTo100)
    end, UnitIsDeadOrGhost(u))
    SetBarColor(bar, r, g, b)
end

local function UpdateInfo(f)
    local u = f.unit
    if not UnitExists(u) then return end
    f.nameFS:SetText(UnitName(u) or "")
    local off = Offline(u)
    local c = off and { 0.6, 0.6, 0.6 } or NameColor(u)
    f.nameFS:SetTextColor(c[1], c[2], c[3])
    if f.face.SetDesaturated then f.face:SetDesaturated(off) end
    local lvl = UnitLevel(u)
    local known = not IsSecret(lvl) and lvl ~= nil and lvl > 0
    local text = known and tostring(lvl) or "??"
    local ok, class = pcall(UnitClassification, u)
    if ok and not IsSecret(class) and (class == "elite" or class == "rareelite" or class == "worldboss") then text = text .. "+" end
    if f.classMedal then
        local okP, isPlayer = pcall(UnitIsPlayer, u)
        local okC, _, token = pcall(UnitClass, u)
        local g = okP and okC and not IsSecret(isPlayer) and isPlayer and not IsSecret(token) and token and CLASS_GLYPH[token]
        if g then
            f.classMedal.glyph:SetTexture(ART .. "class_" .. g)
            f.classMedal:Show()
        else
            f.classMedal:Hide()
        end
        for _, t in ipairs(f.sideChev or {}) do t:SetShown(not g) end
    end
    if f.badge and f.badge.text then
        f.levelFS:SetText("")
        f.badge.text:SetFontObject(#text > 2 and BADGE_FONT_SM or BADGE_FONT)
        f.badge.text:SetText(text)
        local c = (u == "player" or u == "pet" or IsParty(u)) and GOLD or (known and Difficulty(lvl) or DIFF.red)
        f.badge.disc:SetVertexColor(c[1], c[2], c[3], 1)
        f.badge.warnRing:SetShown(not known)
        f.badge.warnHole:SetShown(not known)
    else
        f.levelFS:SetText(u == "pet" and "" or text)
    end
    SetPortraitTexture(f.face, u)
end

local function UpdateAll(f)
    if not f or not UnitExists(f.unit) then return end
    UpdateInfo(f); UpdateHealth(f); UpdatePower(f)
end

-- ==========================================
-- FADING
-- ==========================================
local function ApplyAlpha(f, a)
    if f.curAlpha == a then return end
    f.curAlpha = a
    for _, t in ipairs(f.soft) do t:SetAlpha((t.baseAlpha or 1) * a) end
    f.face:SetAlpha(db.fadeFaces and a or 1)
end

-- ==========================================
-- BUFF ROW AND PET HAPPINESS
-- ==========================================
local buffRow, buffIcons = nil, {}      -- your row (buffs, then debuffs)
local targetRow, targetIcons = nil, {}  -- the target's row (debuffs, then buffs)
local buffCont, targetCont              -- the same rows drawn by the game (see AURA CONTAINERS)
local MAX_BUFFS = 9
local RED = { 0.85, 0.15, 0.15 }

local function FormatTime(left)
    if left >= 3600 then return math.floor(left / 3600 + 0.5) .. "h" end
    if left >= 60 then return math.floor(left / 60 + 0.5) .. "m" end
    return math.floor(left + 0.5) .. "s"
end

-- One aura icon: a 24px square with a 1px edge, a stack count, and the time
-- left underneath. In combat WoW hides aura numbers from addons ("secret
-- values": addons may display them but not test or do math on them), so the
-- time left is then drawn by a Blizzard countdown under the icon instead.
local function AuraIcon(row, list, i, rightToLeft)
    if list[i] then return list[i] end
    local b = CreateFrame("Frame", nil, row)
    b:SetSize(24, 24 + 14)
    if rightToLeft then b:SetPoint("TOPRIGHT", row, "TOPRIGHT", -(i - 1) * 32, 0)
    else b:SetPoint("TOPLEFT", row, "TOPLEFT", (i - 1) * 32, 0) end
    local edge = b:CreateTexture(nil, "BACKGROUND")
    edge:SetPoint("TOPLEFT"); edge:SetSize(24, 24)
    b.edge = edge
    local icon = b:CreateTexture(nil, "ARTWORK")
    icon:SetPoint("TOPLEFT", 1, -1); icon:SetSize(22, 22)
    icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    b.icon = icon
    local count = b:CreateFontString(nil, "OVERLAY")
    count:SetFontObject(NUM_FONT)
    count:SetPoint("BOTTOMRIGHT", icon, "BOTTOMRIGHT", 1, -1)
    b.count = count
    local timer = b:CreateFontString(nil, "OVERLAY")
    timer:SetFontObject(TIMER_FONT)
    timer:SetPoint("TOP", edge, "BOTTOM", 0, -1)
    b.timer = timer
    -- Blizzard countdown under the icon (no swipe), for secret timers.
    local ok, cd = pcall(CreateFrame, "Cooldown", nil, b, "CooldownFrameTemplate")
    if ok and cd then
        cd:ClearAllPoints()
        cd:SetPoint("TOP", edge, "BOTTOM", 0, 0)
        cd:SetSize(24, 14)
        if cd.SetDrawSwipe then cd:SetDrawSwipe(false) end
        if cd.SetDrawEdge then cd:SetDrawEdge(false) end
        if cd.SetDrawBling then cd:SetDrawBling(false) end
        if cd.SetHideCountdownNumbers then cd:SetHideCountdownNumbers(false) end
        if cd.SetUseAuraDisplayTime then pcall(cd.SetUseAuraDisplayTime, cd, true) end
        local fs = cd.GetCountdownFontString and cd:GetCountdownFontString()
        if fs then fs:SetFontObject(TIMER_FONT); fs:ClearAllPoints(); fs:SetPoint("TOP", cd, "TOP", 0, -1) end
        cd:Hide()
        b.cd = cd
    end
    b:EnableMouse(true)
    b:SetScript("OnEnter", function(self)
        if not self.unit then return end
        GameTooltip:SetOwner(self, "ANCHOR_BOTTOMRIGHT")
        local done = false
        do
            local fn = self.harmful and GameTooltip.SetUnitDebuffByAuraInstanceID or GameTooltip.SetUnitBuffByAuraInstanceID
            if fn then done = pcall(fn, GameTooltip, self.unit, self.auraID) end
        end
        if not done then pcall(GameTooltip.SetUnitAura, GameTooltip, self.unit, self.index, self.harmful and "HARMFUL" or "HELPFUL") end
        GameTooltip:Show()
    end)
    b:SetScript("OnLeave", function() GameTooltip:Hide() end)
    list[i] = b
    return b
end

-- The auras on a unit, as raw aura tables (never tested field by field, so
-- secret values can't break the list). The table itself is never secret.
local lastAuraError, lastAuraSource
local function ReadAuras(unit, filter, max)
    local out = {}
    -- AuraUtil.ForEachAura is what Blizzard's own buff bar uses, so this is
    -- exactly the list you see there.
    if AuraUtil and AuraUtil.ForEachAura then
        local n = 0
        local ok, err = pcall(AuraUtil.ForEachAura, unit, filter, max, function(d)
            n = n + 1
            if d ~= nil and #out < max then out[#out + 1] = { data = d, index = n, harmful = (filter == "HARMFUL") } end
            return #out >= max
        end, true)
        if ok then lastAuraSource = "ForEachAura"; return out end
        lastAuraError = "ForEachAura: " .. tostring(err)
        out = {}
    end
    lastAuraSource = "GetAuraDataByIndex"
    for i = 1, 40 do
        if #out >= max then break end
        local d
        if C_UnitAuras and C_UnitAuras.GetAuraDataByIndex then
            local ok, r = pcall(C_UnitAuras.GetAuraDataByIndex, unit, i, filter)
            if ok then d = r end
        elseif UnitAura then
            local ok, name, icon, count, _, duration, expires = pcall(UnitAura, unit, i, filter)
            if ok and name ~= nil then d = { icon = icon, applications = count, duration = duration, expirationTime = expires } end
        end
        if d == nil then break end
        out[#out + 1] = { data = d, index = i, harmful = (filter == "HARMFUL") }
    end
    return out
end

local function FillIcon(b, unit, a)
    local d = a.data
    b.unit, b.index, b.harmful = unit, a.index, a.harmful
    b.auraID = d.auraInstanceID
    pcall(b.icon.SetTexture, b.icon, d.icon)
    local c = a.harmful and RED or BLUE
    b.edge:SetColorTexture(c[1], c[2], c[3], 1)
    -- Stack count: Blizzard formats it (works with secret values); else by hand.
    local countSet = false
    if C_UnitAuras and C_UnitAuras.GetAuraApplicationDisplayCount then
        countSet = pcall(function()
            b.count:SetText(C_UnitAuras.GetAuraApplicationDisplayCount(unit, d.auraInstanceID, 2, 99))
        end)
    end
    if not countSet then
        local n = d.applications
        if not IsSecret(n) and n ~= nil and n > 1 then b.count:SetText(tostring(n)) else b.count:SetText("") end
    end
    -- Time left: our own text when the numbers are readable, otherwise
    -- Blizzard's countdown (which can show secret times).
    local dur, exp = d.duration, d.expirationTime
    b.duration, b.expires, b.timerWay = nil, nil, nil
    b.timer:SetText("")
    if not IsSecret(dur) and not IsSecret(exp) and dur ~= nil and exp ~= nil then
        if b.cd then b.cd:Hide() end
        if dur > 0 and exp > 0 then b.duration, b.expires = dur, exp end
    elseif b.cd then
        local shown = false
        if C_UnitAuras and C_UnitAuras.GetAuraDuration and b.cd.SetCooldownFromDurationObject then
            shown = pcall(function()
                b.cd:SetCooldownFromDurationObject(C_UnitAuras.GetAuraDuration(unit, d.auraInstanceID), true)
            end)
        end
        if not shown and b.cd.SetCooldownFromExpirationTime then
            shown = pcall(b.cd.SetCooldownFromExpirationTime, b.cd, exp, dur)
        end
        b.cd:SetShown(shown)
        b.timerWay = shown and "Blizzard countdown" or "none (no countdown API worked)"
    end
    if b.duration then b.timerWay = "own text" elseif not b.timerWay then b.timerWay = "none (no end time)" end
    b:Show()
end

local function FillRow(row, list, unit, auras, rightToLeft)
    local n = 0
    for _, a in ipairs(auras) do
        n = n + 1
        local b = AuraIcon(row, list, n, rightToLeft)
        local ok, err = pcall(FillIcon, b, unit, a)
        if not ok then b:Hide(); n = n - 1; lastAuraError = tostring(err) end
    end
    for i = n + 1, #list do list[i]:Hide(); list[i].unit = nil; if list[i].cd then list[i].cd:Hide() end end
end

-- Up to 9 icons: the `first` kind, then the other kind. Debuffs always keep
-- room for up to 5 icons, so a long buff list can't push them off the row.
local function Pick(unit, firstFilter, secondFilter)
    local first = ReadAuras(unit, firstFilter, MAX_BUFFS)
    local second = ReadAuras(unit, secondFilter, MAX_BUFFS)
    local debuffs = (firstFilter == "HARMFUL") and first or second
    local reserve = math.min(#debuffs, 5)
    local out = {}
    local firstRoom = (firstFilter == "HARMFUL") and MAX_BUFFS or (MAX_BUFFS - reserve)
    for i = 1, math.min(#first, firstRoom) do out[#out + 1] = first[i] end
    for _, a in ipairs(second) do if #out < MAX_BUFFS then out[#out + 1] = a end end
    return out
end

-- ==========================================
-- AURA CONTAINERS
-- ==========================================
-- WoW Forever (like Midnight 12.1) hides aura data from addons in combat,
-- and debuffs mostly exist in combat. Blizzard's AuraContainer draws a
-- unit's auras itself (icon, stacks and time left), so these rows keep
-- working in combat. Each button is styled once, when the game makes it;
-- after that it belongs to the game. Without AuraContainer the rows above
-- are used instead.
local containers, lastContainerError = {}, nil
local function StyleAuraButton(button, size, edgeColor, dispel)
    button:SetSize(size, size)
    local edge = button:CreateTexture(nil, "BACKGROUND")
    edge:SetAllPoints()
    edge:SetColorTexture(edgeColor[1], edgeColor[2], edgeColor[3], 1)
    local icon = button:CreateTexture(nil, "BORDER")
    icon:SetPoint("TOPLEFT", 1, -1); icon:SetPoint("BOTTOMRIGHT", -1, 1)
    icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    pcall(button.SetIcon, button, icon)
    -- Party debuffs: the edge takes the debuff's type color (magic, curse,
    -- poison, disease), so you can see what you're able to remove.
    if dispel and button.AddDispelTypeTexture and Enum and Enum.CustomAuraButtonDispelTypeTextureStyle then
        local border = button:CreateTexture(nil, "OVERLAY")
        border:SetAllPoints()
        pcall(button.AddDispelTypeTexture, button, border,
            { style = Enum.CustomAuraButtonDispelTypeTextureStyle.Border, showWhenHarmful = true })
    end
    local count = button:CreateFontString(nil, "OVERLAY")
    count:SetFontObject(NUM_FONT)
    count:SetPoint("BOTTOMRIGHT", 1, -1)
    if button.SetApplicationCount then pcall(button.SetApplicationCount, button, count) end
    local timer = button:CreateFontString(nil, "OVERLAY")
    timer:SetFontObject(TIMER_FONT)
    timer:SetPoint("TOP", button, "BOTTOM", 0, -1)
    if button.SetDurationText then pcall(button.SetDurationText, button, timer) end
    if button.SetTooltipAnchorPoint then pcall(button.SetTooltipAnchorPoint, button, "ANCHOR_BOTTOMRIGHT", 0, 0) end
end

-- groups: { { filter, max, edge, dispel } }; o: w, h, size, gap, anchor, growX
local function MakeContainer(key, parent, unit, groups, o)
    if containers[key] ~= nil then return containers[key] or nil end
    local ok, c = pcall(CreateFrame, "AuraContainer", nil, parent, "CustomAuraContainerTemplate")
    if not ok or not c or not c.AddAuraGroup then
        lastContainerError = ok and "AuraContainer not available" or tostring(c)
        containers[key] = false
        return nil
    end
    local good, err = pcall(function()
        c:SetSize(o.w, o.h)
        if c.SetFlowLayoutAnchorPoint then c:SetFlowLayoutAnchorPoint(o.anchor) end
        if c.SetFlowLayoutMaximumLineSize then c:SetFlowLayoutMaximumLineSize(o.w) end
        if c.SetFlowLayoutGrowthDirection then c:SetFlowLayoutGrowthDirection(o.growX, -1) end
        for i, g in ipairs(groups) do
            c:AddAuraGroup(key .. i, g.filter, {
                maxFrameCount = g.max,
                layout = { elementSpacing = o.gap, lineSpacing = 16, groupSpacing = o.gap },
                initializeFrame = function(button) StyleAuraButton(button, o.size, g.edge, g.dispel) end,
            })
        end
        c:SetUnit(unit)
    end)
    if not good then
        lastContainerError = tostring(err)
        c:Hide()
        containers[key] = false
        return nil
    end
    containers[key] = c
    return c
end
local function RefreshContainer(c)
    if c then pcall(c.UpdateAllAuras, c) end
end

local function UpdateTargetAuras()
    if not targetRow then return end
    local show = db.buffs and frames.target and frames.target:IsShown() and UnitExists("target")
    if targetCont then
        targetRow:Hide()
        targetCont:SetShown(show and true or false)
        return
    end
    targetRow:SetShown(show and true or false)
    if not show then return end
    FillRow(targetRow, targetIcons, "target", Pick("target", "HARMFUL", "HELPFUL"), true)
end

local function UpdateBuffs()
    if buffCont then
        if buffRow then buffRow:Hide() end
        buffCont:SetShown(db.myBuffs and frames.player and frames.player:IsShown() or false)
    elseif buffRow then
        buffRow:SetShown(db.myBuffs and frames.player and frames.player:IsShown() or false)
        if buffRow:IsShown() then
            FillRow(buffRow, buffIcons, "player", Pick("player", "HELPFUL", "HARMFUL"), false)
        end
    end
    UpdateTargetAuras()
end

-- Threat glow: one color (Aether blue); how it moves says how urgent it is.
-- The game's threat levels: 0 low, 1 you've out-threatened the one tanking it
-- (its next swing may be at you), 2 it's on you but someone else has more
-- threat, 3 it's on you and you have the most.
--   You and your target:  none; slow pulse when you're getting close (80% of
--   the tank's threat, if the game says); fast pulse at 1; solid at 2 and 3.
--   Your pet:             a dim steady glow while it holds aggro (3); a fast
--   bright pulse when it's losing it (2); nothing otherwise.
-- If the game hides threat from addons (secret values), the glow stays off.
local WARN_PERCENT = 80

-- Step curves: hidden ("secret") values can't be compared by addons, but a
-- curve can turn one into an alpha that the game applies directly.
local function Step(points)
    if not (C_CurveUtil and C_CurveUtil.CreateCurve) then return nil end
    local ok, c = pcall(C_CurveUtil.CreateCurve)
    if not ok or not c then return nil end
    for _, p in ipairs(points) do c:AddPoint(p[1], p[2]) end
    return c
end
local CURVES                -- built on first use (after the game is ready)
local function Curves()
    if CURVES == nil and C_CurveUtil and C_CurveUtil.CreateCurve then
        CURVES = {
            happy   = { Step({ { 1, 1 }, { 1.5, 1 }, { 1.51, 0 }, { 3, 0 } }),                          -- unhappy
                        Step({ { 1, 0 }, { 1.5, 0 }, { 1.51, 1 }, { 2.5, 1 }, { 2.51, 0 }, { 3, 0 } }), -- content
                        Step({ { 1, 0 }, { 2.5, 0 }, { 2.51, 1 }, { 3, 1 } }) },                        -- happy
        }
    end
    return CURVES
end
local lastGlowError
-- Set a texture's alpha from a number, or from a hidden value through a curve.
local function SetLayer(t, value, curve, plain)
    if not IsSecret(value) then t:SetAlpha(plain); return end
    if not curve then t:SetAlpha(0); return end
    local ok, err = pcall(function() t:SetAlpha(curve:Evaluate(value)) end)
    if not ok then t:SetAlpha(0); lastGlowError = tostring(err) end
end

local function Threat(f)
    if f.unit == "targettarget" then return nil end   -- no glow: it's your threat, not theirs
    if not UnitThreatSituation or not UnitExists(f.unit) then return nil end
    local ok, st
    if f.unit == "target" then ok, st = pcall(UnitThreatSituation, "player", "target")
    elseif f.unit == "pet" then ok, st = pcall(UnitThreatSituation, "pet")
    elseif IsParty(f.unit) then ok, st = pcall(UnitThreatSituation, f.unit)
    else ok, st = pcall(UnitThreatSituation, "player") end
    if not ok then return nil end
    return st
end

-- Layer on/off levels as curves (x = the game's threat level 0-3). A
-- texture has only one alpha (SetAlpha and the color's alpha are the same
-- value), so the pulse is part of each layer's alpha: on-level x pulse.
-- For hidden values the curve itself carries the pulse, rebuilt each frame.
local LAYER_POINTS = {
    solid   = { { 0, 0 }, { 1.5, 0 }, { 1.51, 1 }, { 3, 1 } },                          -- 2 or 3
    fast    = { { 0, 0 }, { 0.5, 0 }, { 0.51, 1 }, { 1.5, 1 }, { 1.51, 0 }, { 3, 0 } }, -- 1
    petDim  = { { 0, 0 }, { 2.5, 0 }, { 2.51, 1 }, { 3, 1 } },                          -- 3
    petFast = { { 0, 0 }, { 1.5, 0 }, { 1.51, 1 }, { 2.5, 1 }, { 2.51, 0 }, { 3, 0 } }, -- 2
}
local live = {}            -- curves reused every frame
local function LiveCurve(key, scale)
    if not (C_CurveUtil and C_CurveUtil.CreateCurve) then return nil end
    local c = live[key]
    if not c then
        local ok, made = pcall(C_CurveUtil.CreateCurve)
        if not ok or not made then return nil end
        c = made; live[key] = c
    end
    c:ClearPoints()
    for _, p in ipairs(LAYER_POINTS[key]) do c:AddPoint(p[1], p[2] * scale) end
    return c
end
local function Plain(key, st)
    for i = #LAYER_POINTS[key], 1, -1 do
        local p = LAYER_POINTS[key][i]
        if st >= p[1] - 0.001 then return p[2] end
    end
    return 0
end
local function Apply(t, key, st, scale)
    if IsSecret(st) then
        local c = LiveCurve(key, scale)
        if not c then t:SetAlpha(0); return end
        local ok, err = pcall(function() t:SetAlpha(c:Evaluate(st)) end)
        if not ok then t:SetAlpha(0); lastGlowError = tostring(err) end
    else
        t:SetAlpha(Plain(key, st) * scale)
    end
end

local glowClock, modeTick = 0, 0
local function UpdateThreat(dt)
    glowClock = glowClock + dt
    local slow = 0.2 + 0.6 * (0.5 + 0.5 * math.sin(glowClock * 2 * math.pi / 1.6))
    local fast = 0.25 + 0.75 * (0.5 + 0.5 * math.sin(glowClock * 2 * math.pi / 0.5))
    modeTick = modeTick + dt
    local recheck = modeTick >= 0.1
    if recheck then modeTick = 0 end
    for _, f in pairs(frames) do
        local g = f.glow
        if g and f:IsShown() then
            if recheck then
                f.threatLevel = (db.threat ~= false) and Threat(f) or nil
                f.warn = false
                local st = f.threatLevel
                if f.unit ~= "pet" and not IsSecret(st) and st == 0 and UnitDetailedThreatSituation and UnitExists("target") then
                    local ok, _, _, pct = pcall(UnitDetailedThreatSituation, "player", "target")
                    f.warn = ok and not IsSecret(pct) and pct ~= nil and pct >= WARN_PERCENT
                end
                if IsSecret(st) then f.glowMode = "hidden"
                elseif st == nil then f.glowMode = "off"
                elseif f.unit == "pet" then f.glowMode = (st == 3 and "dim") or (st == 2 and "fast") or "off"
                else f.glowMode = (st >= 2 and "solid") or (st == 1 and "fast") or (f.warn and "slow") or "off" end
            end
            local st = f.threatLevel
            if not IsSecret(st) and st == nil then
                for _, t in pairs(g) do t:SetAlpha(0) end
            elseif f.unit == "pet" then
                Apply(g.dim, "petDim", st, 0.4)
                Apply(g.fast, "petFast", st, fast)
                g.solid:SetAlpha(0); g.slow:SetAlpha(0)
            else
                Apply(g.solid, "solid", st, 1)
                Apply(g.fast, "fast", st, fast)
                g.dim:SetAlpha(0)
                g.slow:SetAlpha(f.warn and slow or 0)
            end
        end
    end
end

local function UpdateTimers()
    local now = GetTime()
    for _, list in ipairs({ buffIcons, targetIcons }) do
        for _, b in ipairs(list) do
            if b:IsShown() and b.duration then
                b.timer:SetText(FormatTime(math.max(0, b.expires - now)))
            end
        end
    end
end

-- Your pet's happiness (1 unhappy, 2 content, 3 happy). WoW Forever has it
-- under C_PetInfo; the old GetPetHappiness is the fallback.
local function PetHappiness()
    for _, fn in ipairs({ C_PetInfo and C_PetInfo.GetPetHappiness or false, GetPetHappiness or false }) do
        if fn then
            local ok, v = pcall(fn)
            if ok and v ~= nil then return v end
        end
    end
    return nil
end

local function UpdateHappiness()
    local pet = frames.pet
    local b = pet and pet.happyMedal
    if not b or not b.layers then return end
    local h = UnitExists("pet") and PetHappiness() or nil
    local function Chev(on) for _, t in ipairs(pet.sideChev or {}) do t:SetShown(on) end end
    if not IsSecret(h) and (h == nil or h < 1) then b:Hide(); Chev(true); return end
    local C = Curves() or { happy = {} }
    for i, layer in ipairs(b.layers) do
        for _, t in ipairs(layer) do SetLayer(t, h, C.happy[i], (not IsSecret(h) and h == i) and 1 or 0) end
    end
    b:Show(); Chev(false)
end

-- ==========================================
-- POSITIONS
-- ==========================================
local function SavePos(f, key)
    local l, t = f:GetLeft(), f:GetTop()
    if not l then return end
    db.pos = db.pos or {}
    db.pos[key] = { l, t }
end

local function PlaceFrames()
    if InCombatLockdown() then return end
    local p, pet, tgt = frames.player, frames.pet, frames.target
    local s = db.scale or 1
    for _, f in pairs(frames) do f:SetScale(s) end
    p:ClearAllPoints()
    local pos = db.pos and db.pos.player
    if pos then p:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", pos[1], pos[2])
    else p:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 20, -20) end
    tgt:ClearAllPoints()
    pos = db.pos and db.pos.target
    if pos then tgt:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", pos[1], pos[2])
    else tgt:SetPoint("TOPLEFT", p, "TOPRIGHT", 40, 0) end
    -- Pet: below the row under your capsule (hawk timers, or your buffs if
    -- you show them there), unless you've moved it yourself.
    local buffH = 24 + 14 + 11
    pet:ClearAllPoints()
    pos = db.pos and db.pos.pet
    if pos then pet:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", pos[1], pos[2])
    else pet:SetPoint("TOPLEFT", p, "TOPLEFT", 40, -(p.capBottom + 11 + buffH - pet.capTop)) end
    buffRow:ClearAllPoints()
    buffRow:SetPoint("TOPLEFT", p, "TOPLEFT", p.cx + 66, -(p.capBottom + 11))
    -- The target's row mirrors yours: under its capsule, ending at its ring.
    targetRow:ClearAllPoints()
    targetRow:SetPoint("TOPRIGHT", tgt, "TOPLEFT", tgt.w - (tgt.cx + 66), -(tgt.capBottom + 11))
    if buffCont then
        buffCont:ClearAllPoints()
        buffCont:SetPoint("TOPLEFT", p, "TOPLEFT", p.cx + 66, -(p.capBottom + 11))
    end
    if targetCont then
        targetCont:ClearAllPoints()
        targetCont:SetPoint("TOPRIGHT", tgt, "TOPLEFT", tgt.w - (tgt.cx + 66), -(tgt.capBottom + 11))
    end
    -- Target of target: small, mirrored, below the target's aura row (on the
    -- ring side), unless you've moved it yourself.
    local tot = frames.targettarget
    if tot then
        tot:ClearAllPoints()
        pos = db.pos and db.pos.tot
        if pos then tot:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", pos[1], pos[2])
        else tot:SetPoint("TOPRIGHT", tgt, "TOPRIGHT", -40, -(tgt.capBottom + 11 + buffH - tot.capTop)) end
    end
    -- Party: four frames stacked, moved together by the first one.
    local p1 = frames.party1
    if p1 then
        p1:ClearAllPoints()
        pos = db.pos and db.pos.party
        if pos then p1:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", pos[1], pos[2])
        else p1:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 20, -300) end
        for i = 2, 4 do
            local f, prev = frames["party" .. i], frames["party" .. (i - 1)]
            f:ClearAllPoints()
            f:SetPoint("TOPLEFT", prev, "TOPLEFT", 0, -(prev.h + 12))
        end
    end
end

-- Blizzard's totem strip (it shows Summon Hawk's hawks, and totems and other
-- temporary helpers, each with its time left) lives inside Blizzard's player
-- frame, which is hidden. Move it under your crest instead. It stays
-- Blizzard's own, so its timers, tooltips and right-click dismiss all work.
local totemHooked, placingTotems = false, false
local function AttachTotems()
    local tf, p = _G.TotemFrame, frames.player
    if not tf or not p or (tf.IsForbidden and tf:IsForbidden()) then return end
    if InCombatLockdown() then return end
    placingTotems = true
    tf.ignoreFramePositionManager = true      -- keep Blizzard's layout from taking it back
    pcall(function()
        if tf:GetParent() ~= p then tf:SetParent(p) end
        tf:ClearAllPoints()
        tf:SetPoint("TOPLEFT", p, "TOPLEFT", p.cx + 56, -(p.capBottom + 8))
    end)
    placingTotems = false
    if not totemHooked then
        totemHooked = true
        local function Back() if not placingTotems then C_Timer.After(0, AttachTotems) end end
        hooksecurefunc(tf, "SetParent", Back)
        hooksecurefunc(tf, "SetPoint", Back)
    end
end

-- Default spots: where Blizzard's frames were, the first time.
local function RememberBlizzardSpots()
    if db.pos then return end
    db.pos = {}
    local pf, tf = _G.PlayerFrame, _G.TargetFrame
    if pf and pf:GetLeft() then db.pos.player = { pf:GetLeft(), pf:GetTop() } end
    if tf and tf:GetLeft() then db.pos.target = { tf:GetLeft(), tf:GetTop() } end
end

-- ==========================================
-- HIDE BLIZZARD'S FRAMES
-- ==========================================
local hiddenParent = CreateFrame("Frame")
hiddenParent:Hide()
local function HideBlizzard()
    if InCombatLockdown() then return end
    for _, n in ipairs({ "PlayerFrame", "PetFrame", "TargetFrame" }) do
        local f = _G[n]
        if f and not f:IsForbidden() then
            pcall(f.UnregisterAllEvents, f)
            pcall(f.Hide, f)
            pcall(f.SetParent, f, hiddenParent)
        end
    end
    if db.party then
        local function Off(f)
            if not f or (f.IsForbidden and f:IsForbidden()) then return end
            pcall(f.UnregisterAllEvents, f); pcall(f.Hide, f); pcall(f.SetParent, f, hiddenParent)
        end
        local pf = _G.PartyFrame
        if pf and not (pf.IsForbidden and pf:IsForbidden()) then
            -- first time: start where Blizzard's party frames were
            if db.pos and not db.pos.party and pf:GetLeft() then db.pos.party = { pf:GetLeft(), pf:GetTop() } end
            if pf.PartyMemberFramePool then
                pcall(function() for m in pf.PartyMemberFramePool:EnumerateActive() do m:UnregisterAllEvents() end end)
            end
            Off(pf)
        end
        Off(_G.CompactPartyFrame)
        for i = 1, 4 do Off(_G["PartyMemberFrame" .. i]) end
    end
end

-- ==========================================
-- MOVING (unlock)
-- ==========================================
local movers = {}
local MOVE_LABEL = { player = "Your frame", pet = "Your pet's frame", target = "Target frame", tot = "Target of target", party = "Party frames" }
local SetLocked
local function Mover(key, f)
    if movers[key] then return movers[key] end
    local m = CreateFrame("Frame", nil, UIParent)
    m:SetFrameStrata("DIALOG")
    m:SetAllPoints(f)
    m:EnableMouse(true)
    m:RegisterForDrag("LeftButton")
    local t = m:CreateTexture(nil, "OVERLAY")
    t:SetAllPoints(); t:SetColorTexture(0.3, 0.7, 1, 0.25)
    local fs = m:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    fs:SetPoint("CENTER", m, "CENTER", 0, 8); fs:SetText(MOVE_LABEL[key] .. " - drag to move")
    -- A Done button on each frame, so you never need a command to finish.
    local done = CreateFrame("Button", nil, m)
    done:SetSize(56, 18)
    done:SetPoint("TOP", fs, "BOTTOM", 0, -3)
    local bg = done:CreateTexture(nil, "BACKGROUND")
    bg:SetAllPoints(); bg:SetColorTexture(0.07, 0.17, 0.32, 0.95)
    local edge = done:CreateTexture(nil, "BORDER")
    edge:SetPoint("TOPLEFT", -1, 1); edge:SetPoint("BOTTOMRIGHT", 1, -1)
    edge:SetColorTexture(1, 0.82, 0, 1)
    bg:SetDrawLayer("ARTWORK")
    local dt = done:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dt:SetPoint("CENTER"); dt:SetText("Done")
    done:SetScript("OnClick", function() SetLocked(true); Print("Frames locked.") end)
    m:SetScript("OnDragStart", function()
        if InCombatLockdown() then return end
        f:SetMovable(true); f:StartMoving()
    end)
    m:SetScript("OnDragStop", function()
        f:StopMovingOrSizing()
        SavePos(f, key)
        PlaceFrames()
    end)
    -- Right-click anywhere on the overlay also finishes.
    m:SetScript("OnMouseUp", function(_, button) if button == "RightButton" then SetLocked(true); Print("Frames locked.") end end)
    movers[key] = m
    return m
end

SetLocked = function(locked)
    if not locked and InCombatLockdown() then return end
    db.locked = locked
    for key, f in pairs({ player = frames.player, pet = frames.pet, target = frames.target, tot = frames.targettarget, party = frames.party1 }) do
        local m = Mover(key, f)
        m:SetShown(not locked)
        -- While moving, show frames even without a pet or target (out of combat only).
        if not InCombatLockdown() then
            if not locked then
                UnregisterUnitWatch(f); f:Show()
            else
                RegisterUnitWatch(f)
            end
        end
    end
    for i = 2, 4 do                    -- the rest of the party moves with the first
        local f = frames["party" .. i]
        if f and not InCombatLockdown() then
            if not locked then UnregisterUnitWatch(f); f:Show() else RegisterUnitWatch(f) end
        end
    end
    if AetherFrames_OnLockChanged then AetherFrames_OnLockChanged(locked) end
end

-- ==========================================
-- SETUP
-- ==========================================
local function CreateAll()
    local petSpec = {
        unit = "pet", art = db.petPower and "pet12" or "pet4", badge = "level", medal = "happy", S = 58, capW = 29 + 151, padTop = 2, nameH = 14, padBottom = 3,
        textInset = 45, padRight = 14, small = true,
        bars = { { kind = "health", h = 12, gap = 3, text = true },
                 { kind = "power", h = db.petPower and 12 or 4, gap = 2, text = db.petPower } },
    }
    Build("AetherFramesPlayer", {
        unit = "player", art = "player", badge = "level", S = 80, capW = 40 + 184, padTop = 3, nameH = 16, padBottom = 4,
        textInset = 56, padRight = 22,
        bars = { { kind = "health", h = 13, gap = 3, text = true },
                 { kind = "power", h = 13, gap = 3, text = true } },
    })
    Build("AetherFramesPet", petSpec)
    Build("AetherFramesTarget", {
        unit = "target", art = "player", badge = "level", mirror = true, S = 80, capW = 40 + 184, padTop = 3, nameH = 16, padBottom = 4,
        textInset = 56, padRight = 22,
        bars = { { kind = "health", h = 13, gap = 3, text = true },
                 { kind = "power", h = 13, gap = 3, text = true } },
    })

    -- Blizzard's target of target lives inside its (hidden) target frame, so
    -- it's gone too; this one takes its place.
    if db.tot then
        Build("AetherFramesTargetTarget", {
            unit = "targettarget", art = "pet12", badge = "level", mirror = true, S = 58, capW = 29 + 151, padTop = 2,
            nameH = 14, padBottom = 3, textInset = 45, padRight = 14, small = true,
            bars = { { kind = "health", h = 12, gap = 3, text = true },
                     { kind = "power", h = 12, gap = 2, text = true } },
        })
    end

    if db.party then
        for i = 1, 4 do
            local f = Build("AetherFramesParty" .. i, {
                unit = "party" .. i, art = "pet12", badge = "level", S = 58, capW = 29 + 151, padTop = 2, nameH = 14,
                padBottom = 3, textInset = 45, padRight = 14, small = true,
                bars = { { kind = "health", h = 12, gap = 3, text = true },
                         { kind = "power", h = 12, gap = 2, text = true } },
            })
            -- debuffs to the right of the capsule, edged in their type's color
            f.auras = MakeContainer("party" .. i, f, "party" .. i, { { filter = "HARMFUL", max = 4, edge = RED, dispel = true } },
                { w = 4 * 24, h = 20 + 14, size = 20, gap = 4, anchor = "TOPLEFT", growX = 1 })
            if f.auras then f.auras:SetPoint("TOPLEFT", f, "TOPLEFT", f.w + 2, -(f.capTop + 4)) end
        end
    end

    buffRow = CreateFrame("Frame", "AetherFramesBuffs", frames.player)
    buffRow:SetSize(MAX_BUFFS * 32, 24 + 14)
    targetRow = CreateFrame("Frame", "AetherFramesTargetAuras", frames.target)
    targetRow:SetSize(MAX_BUFFS * 32, 24 + 14)
    targetCont = MakeContainer("target", frames.target, "target",
        { { filter = "HARMFUL", max = MAX_BUFFS, edge = RED }, { filter = "HELPFUL", max = MAX_BUFFS, edge = BLUE } },
        { w = MAX_BUFFS * 32 - 8, h = 24 + 14, size = 24, gap = 8, anchor = "TOPRIGHT", growX = -1 })
    buffCont = MakeContainer("player", frames.player, "player",
        { { filter = "HELPFUL", max = MAX_BUFFS, edge = BLUE }, { filter = "HARMFUL", max = 5, edge = RED } },
        { w = MAX_BUFFS * 32 - 8, h = 24 + 14, size = 24, gap = 8, anchor = "TOPLEFT", growX = 1 })

    -- Shown with their unit (secure: works in combat).
    RegisterUnitWatch(frames.player)
    RegisterUnitWatch(frames.pet)
    RegisterUnitWatch(frames.target)
    if frames.targettarget then RegisterUnitWatch(frames.targettarget) end
    for i = 1, 4 do if frames["party" .. i] then RegisterUnitWatch(frames["party" .. i]) end end
    for _, f in pairs(frames) do
        f:HookScript("OnShow", function(self) UpdateAll(self); if self.unit == "player" or self.unit == "target" then UpdateBuffs() end end)
    end
end

local ev = CreateFrame("Frame")
local function Reg(e) pcall(ev.RegisterEvent, ev, e) end
Reg("ADDON_LOADED")
Reg("PLAYER_LOGIN")

local function UnitFrameFor(unit)
    return unit and frames[unit]
end

ev:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" then
        if arg1 ~= ADDON then return end
        AetherFramesDB = AetherFramesDB or {}
        db = AetherFramesDB
        for k, v in pairs(defaults) do if db[k] == nil then db[k] = v end end
        return
    end
    if event == "PLAYER_LOGIN" then
        if not db.enabled then return end
        RememberBlizzardSpots()
        CreateAll()
        HideBlizzard(); AttachTotems()
        PlaceFrames()
        for _, e in ipairs({ "PLAYER_ENTERING_WORLD", "PLAYER_TARGET_CHANGED", "UNIT_PET", "UNIT_HEALTH",
            "UNIT_HEALTH_FREQUENT", "UNIT_MAXHEALTH", "UNIT_POWER_UPDATE", "UNIT_POWER_FREQUENT",
            "UNIT_MAXPOWER", "UNIT_DISPLAYPOWER", "UNIT_NAME_UPDATE", "UNIT_LEVEL", "UNIT_PORTRAIT_UPDATE",
            "UNIT_MODEL_CHANGED", "UNIT_AURA", "UNIT_HAPPINESS", "UNIT_FACTION", "UNIT_CLASSIFICATION_CHANGED",
            "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED", "GROUP_ROSTER_UPDATE", "UNIT_CONNECTION",
            "PARTY_MEMBER_ENABLE", "PARTY_MEMBER_DISABLE", "UNIT_TARGET" }) do Reg(e) end
        for _, f in pairs(frames) do UpdateAll(f) end
        UpdateBuffs(); UpdateHappiness()
        if not db.locked then SetLocked(false) end
        return
    end
    if not db or not db.enabled or not frames.player then return end
    if event == "PLAYER_ENTERING_WORLD" then
        HideBlizzard(); AttachTotems()
        for _, f in pairs(frames) do UpdateAll(f) end
        UpdateBuffs(); UpdateHappiness()
    elseif event == "PLAYER_TARGET_CHANGED" then
        UpdateAll(frames.target)
        UpdateAll(frames.targettarget)
        RefreshContainer(targetCont)
        UpdateTargetAuras()
    elseif event == "GROUP_ROSTER_UPDATE" then
        for i = 1, 4 do
            local f = frames["party" .. i]
            if f then UpdateAll(f); RefreshContainer(f.auras) end
        end
    elseif event == "UNIT_TARGET" then
        if arg1 == "target" then UpdateAll(frames.targettarget) end
    elseif event == "UNIT_PET" then
        if arg1 == "player" then UpdateAll(frames.pet); UpdateHappiness() end
    elseif event == "PLAYER_REGEN_DISABLED" then
        inCombat = true
    elseif event == "PLAYER_REGEN_ENABLED" then
        inCombat = false
        HideBlizzard(); AttachTotems()
        PlaceFrames()
    elseif event == "UNIT_AURA" then
        if arg1 == "player" then UpdateBuffs() elseif arg1 == "target" then UpdateTargetAuras() end
    elseif event == "UNIT_HAPPINESS" then
        UpdateHappiness()
    else
        local f = UnitFrameFor(arg1)
        if not f then
            if arg1 == "pet" then f = frames.pet end
        end
        if not f or not f:IsShown() then return end
        if event == "UNIT_CONNECTION" or event:find("^PARTY_MEMBER") then UpdateAll(f)
        elseif event:find("HEALTH") then UpdateHealth(f)
        elseif event:find("POWER") then UpdatePower(f)
        elseif event == "UNIT_PORTRAIT_UPDATE" or event == "UNIT_MODEL_CHANGED" then SetPortraitTexture(f.face, f.unit)
        else UpdateInfo(f) end
        if arg1 == "pet" then UpdateHappiness() end
    end
end)

local tick, happyTick, totTick = 0, 0, 0
ev:SetScript("OnUpdate", function(_, dt)
    if not db or not frames.player then return end
    UpdateThreat(dt)                 -- every frame, so the pulse is smooth
    tick = tick + dt
    if tick < 0.1 then return end
    tick = 0
    local combat = inCombat or InCombatLockdown()
    for _, f in pairs(frames) do
        if f:IsShown() then
            -- Under the mouse? The game-drawn aura rows can answer with a hidden
            -- ("secret") value in combat; those count as no.
            local function Over(fr)
                if not fr then return false end
                local okS, shown = pcall(fr.IsShown, fr)
                if not okS or IsSecret(shown) or shown ~= true then return false end
                local ok, v = pcall(fr.IsMouseOver, fr)
                return ok and not IsSecret(v) and v == true
            end
            local over = Over(f) or (f == frames.player and (Over(buffRow) or Over(buffCont)))
                or (f == frames.target and (Over(targetRow) or Over(targetCont)))
                or (f.auras and Over(f.auras))
            ApplyAlpha(f, (combat or over or not db.locked) and 1 or db.alpha)
            -- Party members out of range (about 40 yards) fade to half.
            if IsParty(f.unit) then
                local ok, inRange = pcall(UnitInRange, f.unit)
                if not ok or not UnitExists(f.unit) or Offline(f.unit) or not db.locked then f:SetAlpha(1)
                elseif f.SetAlphaFromBoolean then
                    if not pcall(f.SetAlphaFromBoolean, f, inRange, 1, 0.45) then f:SetAlpha(1) end
                elseif not IsSecret(inRange) then f:SetAlpha(inRange == false and 0.45 or 1) end
            end
        end
    end
    UpdateTimers()
    -- The game sends no health or power events for the target of target, so
    -- check it here: bars every tick, name, level and portrait twice a second.
    local tot = frames.targettarget
    if tot and tot:IsShown() and UnitExists("targettarget") then
        UpdateHealth(tot); UpdatePower(tot)
        totTick = totTick + 1
        if totTick >= 5 then totTick = 0; UpdateInfo(tot) end
    end
    happyTick = happyTick + 1
    if happyTick >= 10 then happyTick = 0; UpdateHappiness() end   -- once a second
end)

-- ==========================================
-- COMMANDS
-- ==========================================
local function OnOff(v) return v and "on" or "off" end
local function Refade() for _, f in pairs(frames) do f.curAlpha = nil end end

SLASH_AETHERFRAMES1, SLASH_AETHERFRAMES2 = "/aetherframes", "/af"
SlashCmdList["AETHERFRAMES"] = function(input)
    if not db then return end
    local cmd, val = strsplit(" ", strlower(strtrim(input or "")), 2)
    if cmd == "petreset" then
        if db.pos then db.pos.pet = nil end
        if frames.player then PlaceFrames() end
        Print("Your pet's frame is back under yours.")
    elseif cmd == "alpha" and tonumber(val) then
        db.alpha = math.max(0, math.min(1, tonumber(val))); Refade()
        Print("Frames out of combat: " .. math.floor(db.alpha * 100 + 0.5) .. "%")
    elseif cmd == "faces" then
        db.fadeFaces = (val == "on"); Refade()
        Print("Faces fade too: " .. OnOff(db.fadeFaces))
    elseif cmd == "mybuffs" then
        db.myBuffs = (val == "on")
        if frames.player then UpdateBuffs() end
        Print("Your buffs in your frame: " .. OnOff(db.myBuffs) .. (db.myBuffs and "" or " (Blizzard shows them top right)"))
    elseif cmd == "threat" then
        db.threat = (val ~= "off")
        Print("Threat glow: " .. OnOff(db.threat))
    elseif cmd == "auras" then
        -- What the game hands us, so a problem can be pinned down from one paste.
        local function Show(v)
            if IsSecret(v) then return "hidden" end
            if v == nil then return "-" end
            if type(v) == "number" then return string.format("%.1f", v) end
            return tostring(v)
        end
        local function Has(t, k) return (t and t[k]) and "yes" or "no" end
        local cd = buffIcons[1] and buffIcons[1].cd
        Print("Aura check. APIs: GetUnitAuras " .. Has(C_UnitAuras, "GetUnitAuras")
            .. ", ByIndex " .. Has(C_UnitAuras, "GetAuraDataByIndex")
            .. ", GetAuraDuration " .. Has(C_UnitAuras, "GetAuraDuration")
            .. ", StackText " .. Has(C_UnitAuras, "GetAuraApplicationDisplayCount")
            .. ", countdown " .. (cd and (Has(cd, "SetCooldownFromDurationObject") .. "/" .. Has(cd, "SetCooldownFromExpirationTime")) or "?")
            .. ", combat " .. ((inCombat or InCombatLockdown()) and "yes" or "no"))
        for _, q in ipairs({ { "player", "HELPFUL" }, { "player", "HARMFUL" }, { "target", "HARMFUL" }, { "target", "HELPFUL" } }) do
            lastAuraError = nil
            local list = ReadAuras(q[1], q[2], 40)
            print(string.format("  %s %s: %d (via %s)%s", q[1], q[2], #list, tostring(lastAuraSource),
                lastAuraError and ("  problem: " .. lastAuraError) or ""))
            for i, a in ipairs(list) do
                if i > 6 then print("    ..."); break end
                local d = a.data
                print("    " .. i .. ". " .. Show(d.name) .. "  duration " .. Show(d.duration)
                    .. "  ends " .. Show(d.expirationTime) .. "  stacks " .. Show(d.applications))
            end
        end
        local tf = _G.TotemFrame
        print("  hawk/totem strip: " .. (tf and ("found, " .. (tf:GetParent() == frames.player and "under your frame" or "elsewhere")
            .. ", " .. (tf:IsShown() and "showing" or "hidden")) or "not found"))
        if GetTotemInfo then
            for slot = 1, (MAX_TOTEMS or 4) do
                local ok, have, name, start, dur = pcall(GetTotemInfo, slot)
                if ok then print("    slot " .. slot .. ": " .. Show(have) .. "  " .. Show(name) .. "  " .. Show(dur)) end
            end
        end
        local ways = {}
        for i, b in ipairs(buffIcons) do if b:IsShown() then ways[#ways + 1] = i .. ":" .. tostring(b.timerWay) end end
        local tw = {}
        for i, b in ipairs(targetIcons) do if b:IsShown() then tw[#tw + 1] = i .. ":" .. tostring(b.timerWay) end end
        print("  target row: " .. (targetRow and (targetRow:IsShown() and "showing" or "hidden") or "missing")
            .. ", icons " .. #tw .. (#tw > 0 and ("  " .. table.concat(tw, ", ")) or ""))
        print("  your icons shown: " .. #ways .. (#ways > 0 and ("  timers " .. table.concat(ways, ", ")) or ""))
        local function T(u, m)
            if not UnitThreatSituation then return "-" end
            local ok, v
            if m then ok, v = pcall(UnitThreatSituation, u, m) else ok, v = pcall(UnitThreatSituation, u) end
            return ok and Show(v) or "error"
        end
        local okH, hv = pcall(PetHappiness)
        print("  threat: you " .. T("player") .. ", on target " .. T("player", "target") .. ", pet " .. T("pet")
            .. "  | glow " .. tostring(frames.player and frames.player.glowMode) .. "/" .. tostring(frames.pet and frames.pet.glowMode)
            .. "  | pet happiness " .. (okH and Show(hv) or "error") .. "  | curves " .. (Curves() and Curves().happy[1] and "yes" or "no"))
        if lastGlowError then print("  glow problem: " .. lastGlowError) end
        local function CS(c)
            if not c then return "not used" end
            local ok, v = pcall(c.IsShown, c)
            if not ok or IsSecret(v) then return "in use" end
            return v and "showing" or "hidden"
        end
        print("  game-drawn aura rows: target " .. CS(targetCont) .. ", yours " .. CS(buffCont)
            .. ", party " .. CS(frames.party1 and frames.party1.auras)
            .. (lastContainerError and ("  problem: " .. lastContainerError) or ""))
        print("  now " .. string.format("%.1f", GetTime()) .. "; last problem: " .. tostring(lastAuraError or "none"))
    elseif cmd == "buffs" then
        db.buffs = (val ~= "off")
        if frames.player then UpdateBuffs(); PlaceFrames() end
        Print("Buff row: " .. OnOff(db.buffs))
    elseif cmd == "party" then
        db.party = (val ~= "off")
        Print("Party frames: " .. OnOff(db.party) .. " (type /reload to apply)")
    elseif cmd == "tot" then
        db.tot = (val ~= "off")
        Print("Target of target: " .. OnOff(db.tot) .. " (type /reload to apply)")
    elseif cmd == "petpower" then
        db.petPower = (val == "on")
        Print("Numbers on the pet's resource bar: " .. OnOff(db.petPower) .. " (type /reload to apply)")
    elseif cmd == "scale" and tonumber(val) then
        db.scale = math.max(0.6, math.min(1.6, tonumber(val)))
        if frames.player then PlaceFrames() end
        Print("Frame size " .. math.floor(db.scale * 100 + 0.5) .. "%")
    elseif cmd == "unlock" or cmd == "move" then
        if InCombatLockdown() then Print("Frames can't be moved in combat."); return end
        if frames.player then SetLocked(false) end
        Print("Drag any frame, then click Done on it (or right-click it).")
    elseif cmd == "lock" then
        if frames.player then SetLocked(true) end
        Print("Frames locked.")
    elseif cmd == "reset" then
        db.pos = nil
        Print("Positions reset to where Blizzard's frames sit. Type /reload to apply.")
    elseif cmd == "on" or cmd == "off" then
        db.enabled = (cmd == "on")
        Print("AetherFrames " .. (db.enabled and "on" or "off (Blizzard's frames come back)") .. ". Type /reload to apply.")
    else
        Print("commands:")
        print("  /af alpha 0-1        frames out of combat (now " .. db.alpha .. ")")
        print("  /af faces on|off     faces fade too (now " .. OnOff(db.fadeFaces) .. ")")
        print("  /af buffs on|off     buff row (now " .. OnOff(db.buffs) .. ")")
        print("  /af mybuffs on|off   your own buffs in your frame too (now " .. OnOff(db.myBuffs) .. ")")
        print("  /af threat on|off    glow around the portrait when you have threat (now " .. OnOff(db.threat) .. ")")
        print("  /af auras            report what the game says about your auras")
        print("  /af petpower on|off  numbers on the pet's resource bar (now " .. OnOff(db.petPower) .. ")")
        print("  /af party on|off     party frames in the Aether look (now " .. OnOff(db.party) .. ")")
        print("  /af tot on|off       target of target under the target frame (now " .. OnOff(db.tot) .. ")")
        print("  /af scale 0.6-1.6    frame size (now " .. db.scale .. ")")
        print("  /af unlock | lock    move the frames (or Unlock to Move on AetherHub's Layout page; Done to finish)")
        print("  /af petreset         put your pet's frame back under yours")
        print("  /af reset            back to Blizzard's spots")
        print("  /af on | off         use AetherFrames or Blizzard's frames")
    end
end
