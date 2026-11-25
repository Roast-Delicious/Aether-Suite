-- ==========================================
-- AetherLedger: the quest tracker's Aether look
-- Restyles Blizzard's objectives list (the quest tracker on your screen):
--  * the "All Objectives" bar is hidden (each section keeps its own fold);
--  * section headers ("Quests"): a navy band that fades out to the right,
--    Aether-gold text, a gold line that tapers at both ends, and a plain
--    gold - / + instead of Blizzard's button;
--  * quest icons: a navy disc with a gold ring and gold dots (in progress)
--    or a gold "?" (ready to turn in);
--  * yellow text becomes the Aether gold; "Ready for turn-in" turns sky blue;
--  * the Aether font (Fira Sans), and a soft blue band behind a quest you
--    point at.
-- Only looks are changed: Blizzard's tracker still lays everything out and
-- handles every click. Nothing runs on its own; it reapplies right after
-- the tracker updates. Turn it off in AetherHub (AetherLedger tab).
-- ==========================================

local MEDIA = "Interface\\AddOns\\AetherLedger\\Media\\"
local WHITE = "Interface\\Buttons\\WHITE8X8"
local GOLD  = { 1, 0.69, 0 }
local NAVY  = { 0.075, 0.157, 0.29 }
local BLUE  = { 0.3, 0.65, 1 }
local READY = BLUE                           -- Aether Blue #4DA6FF: "Ready for turn-in"

local function Wants()
    return not (AetherHub_Profile and AetherHub_Profile.Interest) or AetherHub_Profile.Interest("trackerLook")
end

local function FontFile(weight)
    return (AETHER_FONT_DIR or "Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-") .. weight .. ".ttf"
end

-- ------------------------------------------
-- Colors: yellow becomes the Aether gold
-- ------------------------------------------
-- Any yellow (red full, green 0.75-0.92, blue low) is swapped for the gold at
-- the same brightness; other colors are left alone. "Ready for turn-in" is
-- sky blue. Runs after Blizzard sets a color, so it never fights the game.
local function IsYellow(r, g, b)
    return r and r > 0.6 and g > r * 0.72 and g < r * 0.93 and b < 0.3 * r
end

-- Yellow color codes inside the text ("|cffffd100[35] Tiger Mastery|r") too.
local function GoldCodes(text)
    return (text:gsub("|c(%x%x)(%x%x)(%x%x)(%x%x)", function(a, r, g, b)
        local R, G, B = tonumber(r, 16) / 255, tonumber(g, 16) / 255, tonumber(b, 16) / 255
        if IsYellow(R, G, B) then
            return string.format("|c%s%02x%02x%02x", a, math.floor(R * 255 + 0.5), math.floor(R * GOLD[2] * 255 + 0.5), 0)
        end
    end))
end

local function Recolor(fs, ready)
    if not fs or not fs.GetTextColor then return end
    if ready then fs:SetTextColor(READY[1], READY[2], READY[3]); return end
    local r, g, b = fs:GetTextColor()
    if IsYellow(r, g, b) then fs:SetTextColor(r * GOLD[1], r * GOLD[2], r * GOLD[3]) end
    local text = fs.GetText and fs:GetText()
    if type(text) == "string" and text:find("|c", 1, true) then
        local gold = GoldCodes(text)
        if gold ~= text then fs:SetText(gold) end
    end
end

-- ------------------------------------------
-- Fonts
-- ------------------------------------------
-- The tracker's two font objects (lines and headers) get Fira Sans at the size
-- the game picked (it changes with the tracker's text-size setting).
local function ApplyFonts()
    for name, weight in pairs({ ObjectiveTrackerLineFont = "Regular", ObjectiveTrackerHeaderFont = "SemiBold" }) do
        local f = _G[name]
        if f and f.GetFont then
            local file, size, flags = f:GetFont()
            if file and size and not tostring(file):find("FiraSans") then
                pcall(f.SetFont, f, FontFile(weight), size, flags or "")
            end
        end
    end
end

-- ------------------------------------------
-- Section headers ("Quests", "Campaign", ...)
-- ------------------------------------------
local function StyleHeader(header)
    if not header or header.aether then return end
    header.aether = true
    -- Blizzard's brown bar and its glow go; the sweep of light on a new quest stays.
    if header.Background then header.Background:SetTexture(nil) end
    if header.Glow then header.Glow:SetTexture(nil) end

    local band = header:CreateTexture(nil, "BACKGROUND", nil, -1)
    band:SetTexture(MEDIA .. "trk_band")
    band:SetVertexColor(NAVY[1], NAVY[2], NAVY[3], 0.9)
    band:SetPoint("TOPLEFT", -4, -1)
    band:SetPoint("BOTTOMRIGHT", 10, 2)

    local line = header:CreateTexture(nil, "BACKGROUND", nil, 1)
    line:SetTexture(MEDIA .. "trk_line")
    line:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 1)
    line:SetPoint("BOTTOMLEFT", -6, -1)
    line:SetPoint("BOTTOMRIGHT", 6, -1)
    line:SetHeight(4)

    if header.Text then header.Text:SetTextColor(GOLD[1], GOLD[2], GOLD[3]) end

    -- A plain gold - (open) or + (folded) in place of Blizzard's button art.
    local mb = header.MinimizeButton
    if mb then
        for _, get in ipairs({ "GetNormalTexture", "GetPushedTexture", "GetHighlightTexture" }) do
            local t = mb[get] and mb[get](mb)
            if t then t:SetAlpha(0) end
        end
        local glyph = mb:CreateFontString(nil, "OVERLAY")
        if not pcall(glyph.SetFont, glyph, FontFile("Bold"), 16, "") then glyph:SetFontObject("GameFontNormalLarge") end
        glyph:SetPoint("CENTER", 0, 1)
        glyph:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
        glyph:SetShadowColor(0, 0, 0, 1); glyph:SetShadowOffset(1, -1)
        header.aetherGlyph = glyph
        local function Sync(_, collapsed) glyph:SetText(collapsed and "+" or "–") end
        Sync(nil, header.GetParent and header:GetParent() and header:GetParent().IsCollapsed
            and header:GetParent():IsCollapsed())
        if header.SetCollapsed then hooksecurefunc(header, "SetCollapsed", Sync) end
        mb:HookScript("OnEnter", function() glyph:SetTextColor(1, 1, 1) end)   -- white on hover (Aether gold is the only yellow)
        mb:HookScript("OnLeave", function() glyph:SetTextColor(GOLD[1], GOLD[2], GOLD[3]) end)
    end
end

-- ------------------------------------------
-- Quest icons
-- ------------------------------------------
-- An overlay on Blizzard's button: it covers the old art, takes no clicks
-- (the button underneath still handles them), and follows the quest's state.
-- It's a child of the BLOCK, only anchored to the button: Blizzard's "pop"
-- animation when a quest is added or handed in scales the button itself, and
-- as the button's child our disc was scaled with it until it filled the
-- screen (user's video, Nov 25). Anchors follow the button's real size and
-- place, not the animation, so the Aether icon just stays put.
-- ------------------------------------------
-- Quest zoom (user's pick b, Nov 25): a quest you accept flies onto the list
-- (the icon starts about a third of the screen across, faint, and shrinks
-- into its spot as it turns solid); a quest you hand in swells and fades
-- off. 0.6 s each. Ours, on our own icon: Blizzard's pop scaled the real
-- button so far on Forever that it covered the screen.
-- ------------------------------------------
local ZOOM, ZOOM_TIME = 25, 0.6
local justAccepted = {}                  -- questID -> time accepted
local byQuest = {}                       -- questID -> overlay on screen now

local function ScaleAnim(ag, from, to, smoothing)
    local a = ag:CreateAnimation("Scale")
    if not a then return end
    a:SetDuration(ZOOM_TIME)
    if a.SetScaleFrom then a:SetScaleFrom(from, from); a:SetScaleTo(to, to)
    elseif a.SetFromScale then a:SetFromScale(from, from); a:SetToScale(to, to) end
    if a.SetOrigin then a:SetOrigin("CENTER", 0, 0) end
    if smoothing and a.SetSmoothing then a:SetSmoothing(smoothing) end
    return a
end
local function AlphaAnim(ag, from, to, dur, smoothing)
    local a = ag:CreateAnimation("Alpha")
    if not a then return end
    a:SetDuration(dur)
    if a.SetFromAlpha then a:SetFromAlpha(from); a:SetToAlpha(to) end
    if smoothing and a.SetSmoothing then a:SetSmoothing(smoothing) end
    return a
end

local function ZoomIn(o)
    if not o.CreateAnimationGroup then return end
    if not o.zoomIn then
        local ag = o:CreateAnimationGroup()
        if not ag then return end
        ScaleAnim(ag, ZOOM, 1, "OUT")
        AlphaAnim(ag, 0, 1, ZOOM_TIME * 0.35, nil)
        o.zoomIn = ag
    end
    o.zoomIn:Stop()
    o.zoomIn:Play()
    o.zoomedAt = GetTime and GetTime() or 0
end

-- The handed-in quest's row goes at once, so a copy of its icon plays the
-- swell above everything, then hides.
local ghost
local function ZoomOut(o)
    if not (o and o.GetCenter and UIParent) then return end
    local x, y = o:GetCenter()
    local w = o:GetWidth()
    if not (x and y and w and w > 0) then return end
    local k = (o:GetEffectiveScale() or 1) / (UIParent:GetEffectiveScale() or 1)
    if not ghost then
        ghost = CreateFrame("Frame", nil, UIParent)
        ghost:SetFrameStrata("HIGH")
        ghost:EnableMouse(false)
        local function Tex(file, layer, sub, c, a)
            local t = ghost:CreateTexture(nil, layer, nil, sub)
            t:SetAllPoints(); t:SetTexture(MEDIA .. file); t:SetVertexColor(c[1], c[2], c[3], a or 1)
            return t
        end
        Tex("trk_disc", "ARTWORK", 0, NAVY, 0.96)
        Tex("trk_ring", "ARTWORK", 1, GOLD)
        ghost.mark = ghost:CreateFontString(nil, "OVERLAY")
        if not pcall(ghost.mark.SetFont, ghost.mark, FontFile("Bold"), 13, "") then ghost.mark:SetFontObject("GameFontNormal") end
        ghost.mark:SetPoint("CENTER", 0.5, 0); ghost.mark:SetText("?"); ghost.mark:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
        local ag = ghost.CreateAnimationGroup and ghost:CreateAnimationGroup()
        if ag then
            ScaleAnim(ag, 1, ZOOM, "IN")
            AlphaAnim(ag, 1, 0, ZOOM_TIME, "IN")
            ag:SetScript("OnFinished", function() ghost:Hide() end)
            ghost.anim = ag
        end
    end
    ghost:ClearAllPoints()
    ghost:SetSize(w * k, w * k)
    ghost:SetPoint("CENTER", UIParent, "BOTTOMLEFT", x * k, y * k)
    ghost:Show()
    if ghost.anim then ghost.anim:Stop(); ghost.anim:Play() else ghost:Hide() end
end

local zev = CreateFrame("Frame")
zev:RegisterEvent("QUEST_ACCEPTED")
zev:RegisterEvent("QUEST_TURNED_IN")
zev:SetScript("OnEvent", function(_, event, a1, a2)
    if not Wants() then return end
    -- QUEST_ACCEPTED is (questID) on newer clients, (logIndex, questID) on older ones
    local id = (event == "QUEST_ACCEPTED" and a2) or a1
    if event == "QUEST_ACCEPTED" then
        id = tonumber(a2) or tonumber(a1)
        if id then justAccepted[id] = GetTime and GetTime() or 0 end
    elseif tonumber(id) then
        pcall(ZoomOut, byQuest[tonumber(id)])
    end
end)

AetherLedger_TrackerZoom = { ZoomIn = ZoomIn, ZoomOut = ZoomOut, accepted = justAccepted, byQuest = byQuest }

local overlays = setmetatable({}, { __mode = "k" })   -- button -> overlay
function AetherLedger_TrackerIconFor(button) return overlays[button] end   -- for tests and /ledger debug
local function StyleIcon(block)
    local button = block.poiButton
    if not button then return end
    local o = overlays[button]
    if o and o:GetParent() ~= block then o:Hide(); o = nil end   -- pooled button moved to another block
    if not o then
        o = CreateFrame("Frame", nil, block)
        o:SetPoint("TOPLEFT", button, "TOPLEFT", -1, 1)
        o:SetPoint("BOTTOMRIGHT", button, "BOTTOMRIGHT", 1, -1)
        o:SetFrameLevel(button:GetFrameLevel() + 5)
        o:EnableMouse(false)
        local function Tex(file, layer, sub, c, a)
            local t = o:CreateTexture(nil, layer, nil, sub)
            t:SetAllPoints()
            t:SetTexture(MEDIA .. file)
            t:SetVertexColor(c[1], c[2], c[3], a or 1)
            return t
        end
        o.glow = o:CreateTexture(nil, "BACKGROUND")
        o.glow:SetTexture(MEDIA .. "trk_disc")
        o.glow:SetPoint("TOPLEFT", -5, 5); o.glow:SetPoint("BOTTOMRIGHT", 5, -5)
        o.glow:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 0.35)
        o.glow:SetBlendMode("ADD")
        o.disc = Tex("trk_disc", "ARTWORK", 0, NAVY, 0.96)
        o.ring = Tex("trk_ring", "ARTWORK", 1, GOLD)
        o.dots = Tex("trk_dots", "OVERLAY", 0, GOLD)
        o.mark = o:CreateFontString(nil, "OVERLAY")
        if not pcall(o.mark.SetFont, o.mark, FontFile("Bold"), 13, "") then o.mark:SetFontObject("GameFontNormal") end
        o.mark:SetPoint("CENTER", 0.5, 0)
        o.mark:SetText("?")
        o.mark:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
        overlays[button] = o
        -- hide with the button (it's no longer our parent)
        if button.HookScript then button:HookScript("OnHide", function(b) local x = overlays[b]; if x then x:Hide() end end) end
    end
    o:SetFrameLevel(button:GetFrameLevel() + 5)
    -- Blizzard's own icon art turns invisible: our icon is the one you see,
    -- and their pop animation then has nothing to balloon.
    if not o.fadedArt and button.GetRegions then
        for _, r in ipairs({ button:GetRegions() }) do if type(r) == "table" and r.SetAlpha then r:SetAlpha(0) end end
        if button.GetChildren then
            for _, c in ipairs({ button:GetChildren() }) do if type(c) == "table" and c.SetAlpha then c:SetAlpha(0) end end
        end
        o.fadedArt = true
    end
    local qid = tonumber(block.id)
    if qid then
        byQuest[qid] = o
        local t = justAccepted[qid]
        if t and (GetTime and GetTime() or 0) - t < 6 then
            justAccepted[qid] = nil
            pcall(ZoomIn, o)
        end
    end
    local done = block.poiIsComplete and true or false
    o.dots:SetShown(not done)
    o.mark:SetShown(done)
    o.glow:SetShown(block.poiIsSuperTracked and true or false)   -- the quest you're following
    o:Show()
end

-- ------------------------------------------
-- Quest blocks
-- ------------------------------------------
local function ReadyLine(line)
    local t = line and line.Text and line.Text:GetText()
    if not t or not QUEST_WATCH_QUEST_READY or (issecretvalue and issecretvalue(t)) then return false end
    return t:sub(1, #QUEST_WATCH_QUEST_READY) == QUEST_WATCH_QUEST_READY
end

local function Paint(block)
    if not block then return end
    Recolor(block.HeaderText)
    -- A finished quest handed in elsewhere (kept at the bottom by the tracker):
    -- "Ready for turn-in: Orgrimmar".
    local where = AetherLedger_Tracker and AetherLedger_Tracker.ElsewhereZone and AetherLedger_Tracker.ElsewhereZone(tonumber(block.id))
    for _, line in pairs(block.usedLines or {}) do
        if where and ReadyLine(line) and line.Text:GetText() == QUEST_WATCH_QUEST_READY then
            line.Text:SetText(QUEST_WATCH_QUEST_READY .. ": " .. where)
        end
        Recolor(line.Text, ReadyLine(line))
        if line.Dash then Recolor(line.Dash) end
    end
    if block.poiButton then StyleIcon(block) end
end

-- A soft blue band behind the quest you point at.
local function HookBlock(block)
    if block.aetherHooked then return end
    block.aetherHooked = true
    local band = block:CreateTexture(nil, "BACKGROUND", nil, -2)
    band:SetTexture(MEDIA .. "trk_band")
    band:SetVertexColor(BLUE[1], BLUE[2], BLUE[3], 0.22)
    band:SetPoint("TOPLEFT", -30, 3)
    band:SetPoint("BOTTOMRIGHT", 10, -3)
    band:Hide()
    block.aetherHover = band
    if block.UpdateHighlight then
        hooksecurefunc(block, "UpdateHighlight", function(self)
            if self.aetherHover then self.aetherHover:SetShown(self.isHighlighted and true or false) end
            Paint(self)
        end)
    end
end

-- A tapered gold line above the first finished quest that's handed in
-- elsewhere: the divider between "your zone" and "hand in elsewhere" (user,
-- Nov 25). One per module, on the block it marks; hidden when there are none.
local dividers = setmetatable({}, { __mode = "k" })   -- module -> texture
local function Divider(module, block)
    local d = dividers[module]
    if not block then if d then d:Hide() end; return end
    if not d or d:GetParent() ~= block then
        if d then d:Hide() end
        d = block:CreateTexture(nil, "OVERLAY")
        d:SetTexture(MEDIA .. "trk_line")
        d:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 0.85)
        d:SetHeight(4)
        dividers[module] = d
    end
    d:ClearAllPoints()
    -- Sits in the gap above the block, clear of its title (user, Nov 25:
    -- the title touched the line). Blizzard places the blocks, so the line
    -- moves up instead of the block moving down.
    d:SetPoint("BOTTOMLEFT", block, "TOPLEFT", -6, 5)
    d:SetPoint("BOTTOMRIGHT", block, "TOPRIGHT", 6, 5)
    d:Show()
end

local function PaintModule(module)
    if not module then return end
    StyleHeader(module.Header)
    local blocks = module.usedBlocks
    if type(blocks) ~= "table" then return end
    local firstElsewhere, firstTop
    local function One(block)
        HookBlock(block); Paint(block)
        local id = tonumber(block.id)
        if id and AetherLedger_Tracker and AetherLedger_Tracker.ElsewhereZone and AetherLedger_Tracker.ElsewhereZone(id)
            and block.IsShown and block:IsShown() then
            local top = block.GetTop and block:GetTop()
            if top and (not firstTop or top > firstTop) then firstElsewhere, firstTop = block, top end
        end
    end
    -- usedBlocks is keyed by template, then by id (or a flat list on some versions).
    for _, v in pairs(blocks) do
        if type(v) == "table" and v.HeaderText then
            One(v)
        elseif type(v) == "table" then
            for _, block in pairs(v) do
                if type(block) == "table" and block.HeaderText then One(block) end
            end
        end
    end
    Divider(module, firstElsewhere)
end

-- ------------------------------------------
-- Wiring
-- ------------------------------------------
local MODULES = { "QuestObjectiveTracker", "CampaignQuestObjectiveTracker", "WorldQuestObjectiveTracker",
    "BonusObjectiveTracker", "AchievementObjectiveTracker", "ScenarioObjectiveTracker",
    "ProfessionsRecipeTracker", "MonthlyActivitiesObjectiveTracker", "AdventureObjectiveTracker",
    "InitiativeTasksObjectiveTracker" }

local installed = false
local function Install()
    if installed or not Wants() then return end
    local container = _G.ObjectiveTrackerFrame
    if not container then return end
    installed = true
    ApplyFonts()
    -- Hide "All Objectives": invisible and unclickable. Blizzard keeps its space.
    local top = container.Header
    if top then
        top:SetAlpha(0)
        for _, key in ipairs({ "MinimizeButton", "FilterButton" }) do
            local b = rawget(top, key) or top[key]
            if type(b) == "table" and b.EnableMouse then b:EnableMouse(false) end
        end
    end
    for _, name in ipairs(MODULES) do
        local module = _G[name]
        if module and module.Update then
            hooksecurefunc(module, "Update", function(self) pcall(PaintModule, self) end)
            pcall(PaintModule, module)
        end
    end
    if ObjectiveTrackerManager and ObjectiveTrackerManager.SetTextSize then
        hooksecurefunc(ObjectiveTrackerManager, "SetTextSize", function() pcall(ApplyFonts) end)
    end
end

local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_LOGIN")
f:RegisterEvent("ADDON_LOADED")
f:SetScript("OnEvent", function(_, event, name)
    if event == "PLAYER_LOGIN" or name == "Blizzard_ObjectiveTracker" then
        local ok, err = pcall(Install)
        if not ok then print("|cff4da6ffAetherLedger:|r couldn't restyle the quest tracker: " .. tostring(err)) end
    end
end)

-- Paint again now (the hand-in list was just worked out; without this the
-- gold line waited for the tracker's next update, a few seconds after a
-- /reload, user Nov 25).
local function Repaint()
    if not installed then return end
    for _, name in ipairs(MODULES) do
        local module = _G[name]
        if module then pcall(PaintModule, module) end
    end
end

AetherLedger_TrackerLook = { Install = Install, IsYellow = IsYellow, Repaint = Repaint }
