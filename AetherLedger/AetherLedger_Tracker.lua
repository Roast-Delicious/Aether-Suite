-- ==========================================
-- AetherLedger quest tracker
-- Keeps the quest tracker (the objectives list on screen) on the zone you're
-- in: that zone's quests in level order, lowest at the top, plus quests ready to
-- hand in here. Red quests (too hard for now) are left out until a level-up
-- makes them orange. Somewhere with nothing to do (a city, a road), it shows
-- the quests of where you're headed instead. Quests you track or untrack yourself are left as you set
-- them. Gray quests (little XP now) are offered for dropping in a small
-- cleanup window; nothing is ever abandoned without your click.
-- Runs only when something changes (a quest accepted or turned in, a level-up,
-- logging in), never in combat.
-- ==========================================

local PREFIX = "|cff4da6ffAetherLedger:|r "

local function AetherFill(button, r, g, b, a)
    local t = button:CreateTexture(nil, "BACKGROUND")
    t:SetColorTexture(r, g, b, a)
    t:SetPoint("TOPLEFT", 1, -1)
    t:SetPoint("BOTTOMRIGHT", -1, 1)
    return t
end

-- Aether look: navy button with a blue edge.
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
    -- soft rounded corners (AetherHub, Release C)
    b.aetherButton = true
    if AetherHub_Round then AetherHub_Round(b, 5) end
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

local Q = C_QuestLog or {}
local MODERN = Q.GetInfo and Q.AddQuestWatch and Q.RemoveQuestWatch and true or false

local function Wants(key)
    return not (AetherHub_Profile and AetherHub_Profile.Interest) or AetherHub_Profile.Interest(key)
end

-- Per-character memory of quests you tracked or untracked yourself.
local function Manual()
    AetherLedgerDB = AetherLedgerDB or {}
    if AetherLedgerDB.manualWatchVersion ~= 2 then   -- 1.5.0 could mistake the game's own tracking for yours
        AetherLedgerDB.manualWatch = nil
        AetherLedgerDB.manualWatchVersion = 2
    end
    AetherLedgerDB.manualWatch = AetherLedgerDB.manualWatch or {}
    local key = (UnitName("player") or "?") .. "-" .. ((GetRealmName and GetRealmName()) or "")
    AetherLedgerDB.manualWatch[key] = AetherLedgerDB.manualWatch[key] or { keep = {}, hide = {} }
    return AetherLedgerDB.manualWatch[key]
end

-- ==========================================
-- QUEST COLORS (the game's own)
-- ==========================================

-- Worked out from the levels, the same rule the quest log's colors use:
-- red from 5 levels above you, orange 3-4 above, gray below the game's
-- green range. (Comparing the game's color tables proved unreliable.)
local function Difficulty(level)
    local me = UnitLevel("player") or 1
    level = level or me
    if level - me >= 5 then return "red" end
    if level - me >= 3 then return "orange" end
    local range
    if UnitQuestTrivialLevelRange then range = UnitQuestTrivialLevelRange("player") end
    if not range and GetQuestGreenRange then range = GetQuestGreenRange() end
    range = range or (me <= 39 and 5 + math.floor(me / 10) or 9)
    if level < me - range then return "gray" end
    return "ok"
end

-- ==========================================
-- READING THE QUEST LOG
-- ==========================================

-- { id, title, level, index, watched, complete } for every quest in your log.
local function LogQuests()
    local list = {}
    local header
    if MODERN then
        for i = 1, Q.GetNumQuestLogEntries() or 0 do
            local info = Q.GetInfo(i)
            if info and info.isHeader then header = info.title end
            if info and not info.isHeader and not info.isHidden and info.questID then
                local id = info.questID
                list[#list + 1] = {
                    id = id, title = info.title, level = info.level or 0, index = i, header = header,
                    watched = Q.GetQuestWatchType and Q.GetQuestWatchType(id) ~= nil,
                    complete = Q.IsComplete and Q.IsComplete(id) or false,
                }
            end
        end
    elseif GetNumQuestLogEntries and GetQuestLogTitle then
        for i = 1, GetNumQuestLogEntries() or 0 do
            local title, level, _, isHeader, _, isComplete, _, id = GetQuestLogTitle(i)
            if isHeader then header = title end
            if title and not isHeader then
                list[#list + 1] = {
                    id = id or title, title = title, level = level or 0, index = i, header = header,
                    watched = IsQuestWatched and IsQuestWatched(i) and true or false,
                    complete = isComplete == 1 or isComplete == true,
                }
            end
        end
    end
    return list
end

-- Tracked quests in the order the tracker shows them.
local function WatchOrder(byIndex)
    local order = {}
    if MODERN and Q.GetNumQuestWatches and Q.GetQuestIDForQuestWatchIndex then
        for i = 1, Q.GetNumQuestWatches() or 0 do order[#order + 1] = Q.GetQuestIDForQuestWatchIndex(i) end
    elseif GetNumQuestWatches and GetQuestIndexForWatch then
        for i = 1, GetNumQuestWatches() or 0 do
            local q = byIndex[GetQuestIndexForWatch(i)]
            if q then order[#order + 1] = q.id end
        end
    end
    return order
end

local function MaxWatches()
    if MODERN and Q.GetMaxNumQuestsCanWatch then return Q.GetMaxNumQuestsCanWatch() or 25 end
    return MAX_WATCHABLE_QUESTS or 25
end

-- ==========================================
-- WHERE QUESTS BELONG
-- ==========================================

local function MapName(map)
    local info = map and C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    return info and info.name
end

-- Zone name -> map, for quests that aren't in the built-in data (the quest
-- log's zone heading is used for those).
local zoneByName
local function ZoneByName(name)
    if not name then return nil end
    if not zoneByName then
        zoneByName = {}
        local seen = {}
        for _, z in pairs(AetherLedger_Zones or {}) do
            for _, map in ipairs(z) do
                if map ~= 0 and not seen[map] then
                    seen[map] = true
                    local n = MapName(map)
                    if n and not zoneByName[n] then zoneByName[n] = map end
                end
            end
        end
    end
    return zoneByName[name]
end

-- Home zone (where the quest log files it) and turn-in zone of a quest.
local function ZonesOf(q)
    local z = AetherLedger_Zones and AetherLedger_Zones[q.id]
    local home = (z and z[1] ~= 0 and z[1]) or ZoneByName(q.header)
    local turnIn = (z and z[2] ~= 0 and z[2]) or home
    return home, turnIn
end

-- Where a finished quest is handed in. The game knows (the turn-in
-- waypoint): ask it first. Our data misses Forever's own quests and zones
-- (Lost Shipping Crate -> Powderfuse Port in the Riverglades: user, Nov 25).
local function TurnInOf(q)
    if q.complete and Q.GetNextWaypoint then
        local ok, wmap = pcall(Q.GetNextWaypoint, q.id)
        if ok and type(wmap) == "number" and wmap > 0 then return wmap end
    end
    local _, turnIn = ZonesOf(q)
    return turnIn
end

-- The maps you're in right now: the most detailed one and every one above it
-- up to the zone (a city, a dungeon and its zone all count).
local function Here()
    local set, zone = {}, nil
    local map = C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit("player")
    for _ = 1, 6 do
        local info = map and C_Map.GetMapInfo(map)
        if not info or (info.mapType and info.mapType <= 2) then break end
        set[map] = true
        zone = map
        map = info.parentMapID
    end
    return set, zone
end

-- ==========================================
-- KEEPING THE TRACKER IN ORDER
-- ==========================================

local applying = false     -- true while we change the tracker (so it isn't taken as you doing it)
local lastAccepted          -- the quest you just accepted (to say why a red one left the tracker)
local elsewhereZone = {}    -- questID -> name of the zone it's handed in, for finished quests from here
local pending, waitingForCombat = false, false

local function Watch(q, on)
    if MODERN then
        if on then Q.AddQuestWatch(q.id) else Q.RemoveQuestWatch(q.id) end
    elseif on then
        AddQuestWatch(q.index)
    else
        RemoveQuestWatch(q.index)
    end
end

local lastFocus
local lastWantKey, lastReadKey   -- what we last put on the tracker, and the order the game then reported
local function Apply()
    if not Wants("manageTracker") then return end
    if InCombatLockdown() then waitingForCombat = true; return end
    if UnitOnTaxi and UnitOnTaxi("player") then return end   -- after landing (PLAYER_CONTROL_GAINED)
    local quests = LogQuests()
    if #quests == 0 then return end
    local manual = Manual()
    local inLog, byIndex = {}, {}
    for _, q in ipairs(quests) do inLog[q.id] = true; byIndex[q.index] = q end
    for id in pairs(manual.keep) do if not inLog[id] then manual.keep[id] = nil end end
    for id in pairs(manual.hide) do if not inLog[id] then manual.hide[id] = nil end end

    -- Which zone to show: the one you're in, or (if it has nothing for you)
    -- the zone you're traveling to, or else the one with most of your quests.
    local here, hereZone = Here()
    local function Fits(q, set)
        local home = ZonesOf(q)
        if q.complete then local turnIn = TurnInOf(q); return turnIn and set[turnIn] end   -- ready: shown where you hand it in
        return home and set[home] and Difficulty(q.level) ~= "red"
    end
    local count = 0
    for _, q in ipairs(quests) do if Fits(q, here) then count = count + 1 end end
    local focus, focusMap, why = here, hereZone, ""
    local function CountIn(map)
        local n, set = 0, { [map] = true }
        for _, q in ipairs(quests) do if Fits(q, set) then n = n + 1 end end
        return n
    end
    if count == 0 then
        local dest = AetherLedger_Travel and AetherLedger_Travel.DestMap and AetherLedger_Travel.DestMap()
        if dest and CountIn(dest) == 0 then dest = nil end
        why = " (where you're headed)"
        if not dest then
            why = " (most of your quests)"
            local tally, best = {}, 0
            for _, q in ipairs(quests) do
                local home = ZonesOf(q)
                if home and not q.complete and Difficulty(q.level) ~= "red" then
                    tally[home] = (tally[home] or 0) + 1
                    if tally[home] > best then best, dest = tally[home], home end
                end
            end
        end
        if dest then focus, focusMap = { [dest] = true }, dest end
    end

    local want = {}
    for _, q in ipairs(quests) do
        if not manual.hide[q.id] and (manual.keep[q.id] or Fits(q, focus) or (q.complete and Fits(q, here))) then
            want[#want + 1] = q
        end
    end
    table.sort(want, function(a, b)
        if a.level ~= b.level then return a.level < b.level end
        return tostring(a.title) < tostring(b.title)
    end)
    -- Finished quests handed in somewhere else, from ANY zone: they stay, at
    -- the bottom, and the tracker says where (user, Nov 25: "hunting through
    -- the quest list" for completed quests; 06:41: Supply and Demand, a
    -- Stranglethorn quest, should show there while in Desolace).
    local inWant, elsewhere = {}, {}
    for _, q in ipairs(want) do inWant[q.id] = true end
    for k in pairs(elsewhereZone) do elsewhereZone[k] = nil end
    for _, q in ipairs(quests) do
        if q.complete and not inWant[q.id] and not manual.hide[q.id] then
            local turnIn = TurnInOf(q)
            if turnIn and not here[turnIn] then
                elsewhere[#elsewhere + 1] = q
                elsewhereZone[q.id] = MapName(turnIn)
            end
        end
    end
    table.sort(elsewhere, function(a, b) return tostring(a.title) < tostring(b.title) end)
    local cap = MaxWatches()
    while #want + #elsewhere > cap and #elsewhere > 0 do table.remove(elsewhere) end
    while #want > cap do table.remove(want) end
    -- A red quest you just accepted: the game put it on the tracker, we take it
    -- off; say why, once (user's pick 2, Nov 25).
    if lastAccepted then
        for _, q in ipairs(quests) do
            if q.id == lastAccepted and not inWant[q.id] and not manual.keep[q.id] and Difficulty(q.level) == "red" then
                print(PREFIX .. tostring(q.title) .. " is red for you right now (level " .. tostring(q.level)
                    .. "), so it's off the tracker until you level up. Shift-click it in your quest log to keep it on.")
            end
        end
        lastAccepted = nil
    end

    -- Nothing to do if the tracker already shows what we last set up and
    -- nothing has moved since. (The order the game reports isn't the order
    -- it shows, so compare with what it reported right after we set it.)
    local ids = {}
    for i, q in ipairs(want) do ids[i] = tostring(q.id) end
    for _, q in ipairs(elsewhere) do ids[#ids + 1] = "e" .. tostring(q.id) end
    local wantKey = table.concat(ids, ",")
    local currentKey = table.concat(WatchOrder(byIndex), ",")
    local function Repaint() if AetherLedger_TrackerLook and AetherLedger_TrackerLook.Repaint then AetherLedger_TrackerLook.Repaint() end end
    if wantKey == lastWantKey and currentKey == lastReadKey then Repaint(); return end

    -- Say which zone the list follows when that changes.
    if focusMap and focusMap ~= lastFocus then
        lastFocus = focusMap
        local name = MapName(focusMap)
        if name then
            print(PREFIX .. "quest tracker: " .. name .. why
                .. ", " .. #want .. (#want == 1 and " quest." or " quests."))
        end
    end

    applying = true
    local ok, err = pcall(function()
        for _, q in ipairs(quests) do if q.watched then Watch(q, false) end end
        -- In WoW Forever the tracker lists quests in the reverse of the order
        -- they were added (the newest on top), so add
        -- the highest level first and the lowest last: lowest ends up on top.
        for i = #elsewhere, 1, -1 do Watch(elsewhere[i], true) end   -- added first = shown last
        for i = #want, 1, -1 do Watch(want[i], true) end
    end)
    applying = false
    lastWantKey = wantKey
    lastReadKey = table.concat(WatchOrder(byIndex), ",")
    if QuestWatch_Update then pcall(QuestWatch_Update) end
    if C_Timer and C_Timer.After then C_Timer.After(0, Repaint) else Repaint() end
    if not ok then print(PREFIX .. "couldn't sort the quest tracker: " .. tostring(err)) end
end

local function ApplySoon(delay)
    if pending then return end
    pending = true
    C_Timer.After(delay or 1, function()
        pending = false
        Apply()
    end)
end

-- You tracked or untracked a quest yourself: remember it so it's left that way.
-- The game's own tracking right after you accept a quest, or while logging
-- in, doesn't count.
local quietUntil = 0
local function LogOpen()
    for _, name in ipairs({ "QuestLogFrame", "QuestMapFrame", "WorldMapFrame", "QuestLogDetailFrame" }) do
        local f = _G[name]
        if f and f.IsVisible and f:IsVisible() then return true end
    end
    return false
end

local function YouChanged(questID, added)
    if applying or not questID or GetTime() < quietUntil then return end
    -- The game also adds quests by itself (on accepting, or when you make
    -- progress). Only count it as yours when the quest log is open, where you
    -- shift-click. Taking a quest off the tracker counts from anywhere.
    if added and not LogOpen() then
        ApplySoon(1)      -- the game added it: put the list back the way it should be
        return
    end
    local manual = Manual()
    if added then
        manual.hide[questID] = nil
        manual.keep[questID] = true
    else
        manual.keep[questID] = nil
        manual.hide[questID] = true
    end
end

-- ==========================================
-- GRAY QUESTS AND THE CLEANUP WINDOW
-- ==========================================

-- Gray quests worth dropping (not class/profession quests, not ones whose
-- chain still leads to quests at your level), and gray ones ready to turn in.
local function Cleanup()
    local drop, turnIn = {}, {}
    local data = AetherLedger_Data or {}
    for _, q in ipairs(LogQuests()) do
        if Difficulty(q.level) == "gray" then
            local d = data[q.id]
            local special = d and d[16]
            local chainLeadsOn = d and d[12] and d[12] > 1 and d[11] and Difficulty(d[11]) ~= "gray"
            if q.complete then
                turnIn[#turnIn + 1] = q
            elseif not special and not chainLeadsOn then
                drop[#drop + 1] = q
            end
        end
    end
    return drop, turnIn
end

local function Abandon(q)
    local ok = pcall(function()
        if MODERN and Q.SetSelectedQuest and Q.SetAbandonQuest and Q.AbandonQuest then
            Q.SetSelectedQuest(q.id)
            Q.SetAbandonQuest()
            Q.AbandonQuest()
        else
            SelectQuestLogEntry(q.index)
            SetAbandonQuest()
            AbandonQuest()
        end
    end)
    if ok then print(PREFIX .. "dropped " .. tostring(q.title) .. ".")
    else print(PREFIX .. "WoW didn't let the addon drop " .. tostring(q.title) .. "; abandon it from your quest log.") end
end

local win
local ROWS = 8

local function BuildWindow()
    win = CreateFrame("Frame", "AetherLedgerCleanup", UIParent, "BackdropTemplate")
    win:SetSize(330, 120)
    win:SetPoint("CENTER", UIParent, "CENTER", 0, 80)
    win:SetFrameStrata("FULLSCREEN_DIALOG")   -- above AetherHub
    win:SetMovable(true)
    win:SetClampedToScreen(true)
    win:EnableMouse(true)
    win:RegisterForDrag("LeftButton")
    win:SetScript("OnDragStart", win.StartMoving)
    win:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        if AetherLedger_SavePos then AetherLedger_SavePos(self, "cleanup") end
    end)
    if win.SetBackdrop then
        win:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 })
        win:SetBackdropColor(0.05, 0.06, 0.09, 0.94)
        win:SetBackdropBorderColor(0.3, 0.65, 1, 0.9)
    end
    AetherDecorate(win, 28)
    tinsert(UISpecialFrames, "AetherLedgerCleanup")   -- Esc closes it
    local title = win:CreateFontString(nil, "OVERLAY", "AetherFontNormal")
    title:SetPoint("TOPLEFT", 12, -10)
    title:SetText("|cff4da6ffAetherLedger|r  quest log cleanup")
    local close = AetherButton(win, nil, true)
    close:SetSize(18, 18)
    close:SetText("x")
    close:SetPoint("TOPRIGHT", -6, -6)
    close:SetScript("OnClick", function() win:Hide() end)
    win.intro = win:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    win.intro:SetPoint("TOPLEFT", title, "BOTTOMLEFT", 0, -8)
    win.intro:SetPoint("RIGHT", win, "RIGHT", -12, 0)
    win.intro:SetJustifyH("LEFT")
    win.rows = {}
    for i = 1, ROWS do
        local row = CreateFrame("Frame", nil, win)
        row:SetHeight(22)
        row.drop = AetherButton(row, nil, true)
        row.drop:SetSize(70, 20)
        row.drop:SetPoint("RIGHT", row, "RIGHT", 0, 0)
        row.text = row:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
        row.text:SetPoint("LEFT", row, "LEFT", 0, 0)
        row.text:SetPoint("RIGHT", row.drop, "LEFT", -6, 0)
        row.text:SetJustifyH("LEFT")
        -- First click asks "Sure?", a second click within 3 seconds drops the quest.
        row.drop:SetScript("OnClick", function(self)
            if not row.quest then return end
            if self.armed then
                self.armed = false
                Abandon(row.quest)
                C_Timer.After(0.5, function() if win:IsShown() then AetherLedger_Tracker.ShowCleanup() end end)
            else
                self.armed = true
                self:SetText("|cffffb000Sure?|r")
                C_Timer.After(3, function()
                    if self.armed then self.armed = false; self:SetText("Abandon") end
                end)
            end
        end)
        win.rows[i] = row
    end
    win.footer = win:CreateFontString(nil, "OVERLAY", "AetherFontHighlightSmall")
    win.footer:SetJustifyH("LEFT")
    win:Hide()
end

local function GrayText(q)
    return string.format("|cff9d9d9d[%d]|r %s", q.level, tostring(q.title))
end

AetherLedger_Tracker = {}

-- The zone a finished quest from here is handed in (nil if it's handed in here),
-- for the tracker look's "Ready for turn-in: <zone>".
function AetherLedger_Tracker.ElsewhereZone(questID) return questID and elsewhereZone[questID] end

function AetherLedger_Tracker.ShowCleanup()
    if not win then BuildWindow() end
    local drop, turnIn = Cleanup()
    win.intro:SetText(#drop > 0 and "Gray quests give little XP now. Drop the ones you don't need:"
        or "No gray quests to drop.")
    local y = -36 - win.intro:GetStringHeight() - 8
    for i, row in ipairs(win.rows) do
        local q = drop[i]
        row.quest = q
        if q then
            row:ClearAllPoints()
            row:SetPoint("TOPLEFT", win, "TOPLEFT", 12, y)
            row:SetPoint("RIGHT", win, "RIGHT", -12, 0)
            row.text:SetText(GrayText(q))
            row.drop.armed = false
            row.drop:SetText("Abandon")
            row:Show()
            y = y - 24
        else
            row:Hide()
        end
    end
    local notes = {}
    if #drop > ROWS then notes[#notes + 1] = "...and " .. (#drop - ROWS) .. " more after these." end
    if #turnIn > 0 then
        local names = {}
        for _, q in ipairs(turnIn) do names[#names + 1] = GrayText(q) end
        notes[#notes + 1] = "Ready to turn in (worth the XP): " .. table.concat(names, ", ")
    end
    notes[#notes + 1] = "|cff888888Class and profession quests, and ones that lead on to quests at your level, aren't listed.|r"
    win.footer:ClearAllPoints()
    win.footer:SetPoint("TOPLEFT", win, "TOPLEFT", 12, y - 6)
    win.footer:SetPoint("RIGHT", win, "RIGHT", -12, 0)
    win.footer:SetText(table.concat(notes, "\n"))
    win:SetHeight(-y + win.footer:GetStringHeight() + 22)
    if AetherLedger_PlaceBeside then AetherLedger_PlaceBeside(win, { "CENTER", UIParent, "CENTER", 0, 80 }, "cleanup") end
    win:Show()
    C_Timer.After(0, function()          -- again once the text has wrapped to its real height
        if win:IsShown() then win:SetHeight(-y + win.footer:GetStringHeight() + 22) end
    end)
end

-- Gray quests to drop, for the suggestion window.
function AetherLedger_Tracker.Gray()
    local drop = Cleanup()
    return drop
end

AetherLedger_Tracker.Apply = Apply

-- /ledger tracker: every quest in your log and why it is or isn't tracked.
function AetherLedger_Tracker.Explain()
    local manual = Manual()
    local here, hereZone = Here()
    print(PREFIX .. "quest tracker, you're level " .. (UnitLevel("player") or "?") .. " in " .. tostring(MapName(hereZone)) .. ":")
    for _, q in ipairs(LogQuests()) do
        local home = ZonesOf(q)
        local turnIn = TurnInOf(q)
        local why = {}
        why[#why + 1] = Difficulty(q.level)
        if q.complete then why[#why + 1] = "ready, hand in: " .. tostring(MapName(turnIn) or "?") end
        why[#why + 1] = "zone: " .. tostring(MapName(home) or "?")
        if manual.keep[q.id] then why[#why + 1] = "pinned by you" end
        if manual.hide[q.id] then why[#why + 1] = "hidden by you" end
        print(string.format("  %s [%d] %s - %s", q.watched and "|cff33dd66tracked|r" or "|cff888888-|r",
            q.level, tostring(q.title), table.concat(why, ", ")))
    end
end

-- ==========================================
-- EVENTS
-- ==========================================

-- Older quest log: there's no event for your own tracking changes, so watch the calls.
if not MODERN and hooksecurefunc and AddQuestWatch and RemoveQuestWatch then
    local function Changed(index, added)
        if applying or not index then return end
        local title, _, _, _, _, _, _, id = GetQuestLogTitle(index)
        YouChanged(id or title, added)
    end
    hooksecurefunc("AddQuestWatch", function(index) Changed(index, true) end)
    hooksecurefunc("RemoveQuestWatch", function(index) Changed(index, false) end)
end

local events = CreateFrame("Frame")
for _, event in ipairs({ "PLAYER_LOGIN", "QUEST_ACCEPTED", "QUEST_TURNED_IN", "QUEST_REMOVED", "PLAYER_LEVEL_UP",
    "PLAYER_REGEN_ENABLED", "QUEST_WATCH_LIST_CHANGED", "ZONE_CHANGED_NEW_AREA", "PLAYER_CONTROL_GAINED" }) do
    pcall(events.RegisterEvent, events, event)
end
events:SetScript("OnEvent", function(_, event, arg1, arg2)
    if event == "PLAYER_LOGIN" then
        quietUntil = GetTime() + 10
        -- A first pass soon after a /reload (so the hand-in line shows right
        -- away), and the usual one at 6 s once the quest data has settled.
        ApplySoon(1.5)
        C_Timer.After(6, function() ApplySoon(0) end)
    elseif event == "PLAYER_REGEN_ENABLED" then
        if waitingForCombat then waitingForCombat = false; ApplySoon(1) end
    elseif event == "QUEST_WATCH_LIST_CHANGED" then
        YouChanged(arg1, arg2)                         -- newer tracker: (questID, added)
    elseif event == "ZONE_CHANGED_NEW_AREA" then
        -- Wait until you've been in the new zone for 5 seconds (no flicker along borders).
        local _, zone = Here()
        C_Timer.After(5, function()
            local _, now = Here()
            if now == zone then ApplySoon(0) end
        end)
    elseif event == "QUEST_ACCEPTED" then
        lastAccepted = tonumber(arg2) or tonumber(arg1)     -- (questID) newer, (logIndex, questID) older
        quietUntil = GetTime() + 2
        ApplySoon(1.5)   -- after the game's own auto-tracking of the new quest
    else
        ApplySoon(1)
    end
end)
