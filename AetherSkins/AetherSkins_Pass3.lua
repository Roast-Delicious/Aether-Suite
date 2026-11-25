-- AetherSkins, Build 2 designs (Nov 25), all approved from mockups:
--   side tabs: flat gold glyphs on navy, the open tab with a thick gold
--     frame, gold notch and soft gold glow (mock/sidetabs_flat.py B,
--     mock/crests_flat.py); the Character tab keeps your portrait
--   window crests: flat gold glyphs on a navy disc (map, spellbook,
--     talents, Group Finder, Friends, Progress Track)
--   vendor: flat gold repair, guild repair and sell-junk buttons
--     (mock/vendor.py A)
--   scroll bars: beveled gold thumb on a dark navy track, the arrows our
--     3D gold chevrons (mock/slider3d.py)
--   quest and gossip pages: the Aether page (mock/pass2_parch.py 3), gold
--     headings, gossip choices in Aether blue (mock/gossip_opt.py B)
--   Friends: the picked friend brighter, with a gold notch and blue edge;
--     a thin blue edge under the mouse (mock/friends_sel.py A)
--   a corner grip on every window but the quest windows: drag to scale,
--     right-click to reset; saved per window.
-- Same safety rules: Blizzard's art is faded, tinted or given our texture;
-- nothing of Blizzard's is moved (the grip scales the whole window, as
-- Blizzard's own UI scale does); hooks are post-hooks.

local W = AetherSkins_Windows
local P = W and W.P2
if not (P and P.H and W.H) then return end
local H, PH = W.H, P.H
local Tex, Fade, T, Edge, NavyBox, Forbidden = H.Tex, H.Fade, H.T, H.Edge, H.NavyBox, H.Forbidden
local MEDIA, WHITE, GOLD, BLUE, NAVY, TEXT = H.MEDIA, H.WHITE, H.GOLD, H.BLUE, H.NAVY, H.TEXT
local Tint, Atlas, FileID, Shown, Once, HookShow = PH.Tint, PH.Atlas, PH.FileID, PH.Shown, PH.Once, PH.HookShow
local weak = PH.weak
local P3 = {}
W.P3 = P3
local Usable

-- ------------------------------------------
-- Gold when you can click it, gray when you can't (user, Nov 25)
-- ------------------------------------------
local usable = weak()            -- button -> { look = fn }
local GRAY = { 0.62, 0.65, 0.72 }
Usable = function(b, o, extra, col)
    local u = usable[b]
    if not u then
        u = { list = {} }
        usable[b] = u
        u.look = function()
            local okE, en = pcall(function() return not b.IsEnabled or b:IsEnabled() end)
            local on = (not okE) or en
            if on and u.extra then local okX, x = pcall(u.extra); on = okX and x end
            for ob, c in pairs(u.list) do
                if ob.SetDesaturated then ob:SetDesaturated(not on) end
                local k = on and c or GRAY
                ob:SetVertexColor(k[1], k[2], k[3], 1)
            end
            if u.onLook then pcall(u.onLook, on) end
        end
        if hooksecurefunc then
            for _, m in ipairs({ "Enable", "Disable", "SetEnabled" }) do
                if b[m] then pcall(hooksecurefunc, b, m, u.look) end
            end
        end
    end
    if o then u.list[o] = col or { 1, 1, 1 } end
    if extra then u.extra = extra end
    u.look()
    return u
end
P3.Usable = Usable
function P3.RefreshUsable() for _, u in pairs(usable) do pcall(u.look) end end
-- repairs and money change without the buttons being touched
if CreateFrame then
    local ev = CreateFrame("Frame")
    for _, e in ipairs({ "MERCHANT_SHOW", "MERCHANT_UPDATE", "UPDATE_INVENTORY_DURABILITY", "PLAYER_MONEY", "BAG_UPDATE_DELAYED" }) do
        pcall(ev.RegisterEvent, ev, e)
    end
    ev:SetScript("OnEvent", function() P3.RefreshUsable() end)
end

-- ------------------------------------------
-- Page arrows (vendor, Spellbook): our chevron inside a navy square
-- ------------------------------------------
local PAGE_DIR = { ["130864"] = "right", ["130865"] = "right", ["130866"] = "right",
                   ["130867"] = "left", ["130868"] = "left", ["130869"] = "left" }
function P.PageArrow(t, id)
    local dir = PAGE_DIR[id]
    local b = t.GetParent and t:GetParent()
    if not dir or not b or not b.CreateTexture then return false end
    t:SetAlpha(0)
    if not Once(b, "pagearrow") then return true end
    local s = Tex(b, "BACKGROUND", 7, WHITE, { NAVY[1], NAVY[2], NAVY[3], 0.95 })
    s:SetSize(26, 26); s:SetPoint("CENTER", b, "CENTER")
    local f = CreateFrame("Frame", nil, b)
    f:SetSize(26, 26); f:SetPoint("CENTER", b, "CENTER")
    local e = Edge(f, "BORDER", 1, { BLUE[1], BLUE[2], BLUE[3], 1 }, 0)
    local c = Tex(b, "ARTWORK", 7, MEDIA .. "chev3d_" .. dir, { 1, 1, 1, 1 })
    c:SetSize(20, 20); c:SetPoint("CENTER", b, "CENTER")
    local u = Usable(b, c)
    u.onLook = function(on)
        local k = on and BLUE or { 0.24, 0.27, 0.35 }
        for _, x in ipairs(e) do x:SetVertexColor(k[1], k[2], k[3], 1) end
    end
    u.look()
    if b.HookScript then
        b:HookScript("OnMouseDown", function() c:ClearAllPoints(); c:SetPoint("CENTER", b, "CENTER", 1, -1) end)
        b:HookScript("OnMouseUp", function() c:ClearAllPoints(); c:SetPoint("CENTER", b, "CENTER") end)
    end
    return true
end

-- ------------------------------------------
-- Side tabs: glyph, thick gold frame and glow on the open one
-- ------------------------------------------
local TAB_BY_ICON = {
    ["8197103"] = "tab_rep", ["2447783"] = "tab_skills", ["8197098"] = "tab_pvp",
    ["8197078"] = "tab_coin", ["8197104"] = "tab_stats", ["8197096"] = "gl_eyeball",
    ["2056011"] = "gl_track", ["413584"] = "tab_pvp", ["442272"] = "gl_talents",
}
local TAB_BY_ATLAS = { { "^friends%-icon%-tab%-friends", "gl_friends" }, { "^friends%-icon%-tab%-recentAllies", "gl_clock" },
    { "^friends%-icon%-tab%-friendRequest", "gl_request" }, { "^friends%-icon%-tab%-raid", "gl_people" } }
local TAB_BY_KEY = { { "Listing", "gl_eyeball" }, { "Browse", "gl_eye" }, { "Who", "gl_people" },
    { "RewardTrack", "gl_track" }, { "Challenge", "tab_pvp" }, { "Tree", "gl_talents" } }

local function TabKey(tab)
    local par = tab.GetParent and tab:GetParent()
    if type(par) ~= "table" then return nil end
    for k, v in pairs(par) do if v == tab and type(k) == "string" then return k end end
end
function P3.TabGlyph(tab)
    local ic = T(tab, "Icon")
    local a = ic and Atlas(ic)
    if a then for _, m in ipairs(TAB_BY_ATLAS) do if a:find(m[1]) then return m[2] end end end
    local id = ic and FileID(ic)
    if id and TAB_BY_ICON[id] then return TAB_BY_ICON[id] end
    local key = TabKey(tab)
    if key then for _, m in ipairs(TAB_BY_KEY) do if key:find(m[1]) then return m[2] end end end
    return nil     -- the portrait tab, or one we don't know: Blizzard's icon stays
end

local extra = weak()
function P.SideTabExtra(tab)
    local p = PH.tabParts[tab]; if not p then return end
    local x = extra[tab]
    if not x then
        x = {}
        extra[tab] = x
        -- the thick frame: two more gold rings inside the edge, on a frame over the fill
        local ff = CreateFrame("Frame", nil, tab)
        ff:SetPoint("TOPLEFT", p.fill, "TOPLEFT"); ff:SetPoint("BOTTOMRIGHT", p.fill, "BOTTOMRIGHT")
        x.rings = {}
        for i = 1, 2 do
            for _, e in ipairs(Edge(ff, "BORDER", 2, { GOLD[1], GOLD[2], GOLD[3], 1 }, i)) do x.rings[#x.rings + 1] = e end
        end
        x.glow = Tex(tab, "BACKGROUND", -3, MEDIA .. "glow_sq", GOLD)
        local w = (tab.GetWidth and tab:GetWidth()) or 55
        x.glow:SetSize(w * 2, w * 2); x.glow:SetPoint("CENTER", p.fill, "CENTER")
        local g = P3.TabGlyph(tab)
        if g then
            local ic = T(tab, "Icon")
            if ic then ic:SetAlpha(0) end
            x.glyph = Tex(tab, "ARTWORK", 7, MEDIA .. g, GOLD)
            x.glyph:SetSize(w * 0.55, w * 0.55); x.glyph:SetPoint("CENTER", p.fill, "CENTER")
        end
    end
    local sel = Shown(T(tab, "SelectedTexture"))
    for _, e in ipairs(x.rings) do e:SetShown(sel) end
    x.glow:SetShown(sel)
    if p.notch then p.notch:Hide() end   -- the thick gold frame replaces it (user, Nov 25 11:36)
end

-- ------------------------------------------
-- Window crests
-- ------------------------------------------
local CREST = { WorldMapFrame = "gl_map", SocialUIFrame = "gl_friends", FriendsFrame = "gl_friends",
    LegacySystemFrame = "gl_track", LFGListingFrame = "gl_eyeball", LFGBrowseFrame = "gl_eyeball",
    LFGWhoListFrame = "gl_eyeball", PlayerSpellsFrame = "gl_book" }
local crestParts = weak()
local function CrestKind(win, name)
    if name == "PlayerSpellsFrame" then
        local tf = T(win, "TalentsFrame")
        if tf and tf.IsShown and tf:IsShown() then return "gl_talents" end
    end
    return CREST[name]
end
function P3.Crest(win)
    local name = win.GetName and win:GetName()
    local kind = name and CrestKind(win, name)
    if not kind then return end
    local chrome = (not T(win, "NineSlice") and T(win, "BorderFrame")) or win
    local pc = T(chrome, "PortraitContainer")
    local portrait = (pc and (T(pc, "portrait") or T(pc, "Portrait"))) or (name and _G[name .. "Portrait"])
    if not portrait then return end
    local c = crestParts[win]
    if not c then
        local owner = pc or chrome
        c = {}
        c.disc = Tex(owner, "OVERLAY", 5, MEDIA .. "disc_plain", NAVY)
        c.disc:SetSize(60, 60); c.disc:SetPoint("CENTER", portrait, "CENTER")
        c.glyph = Tex(owner, "OVERLAY", 6, MEDIA .. kind, GOLD)
        c.glyph:SetSize(36, 36); c.glyph:SetPoint("CENTER", portrait, "CENTER")
        crestParts[win] = c
        if name == "PlayerSpellsFrame" then
            for _, k in ipairs({ "TalentsFrame", "SpellBookFrame", "SpecFrame" }) do
                local sub = T(win, k)
                if sub and sub.HookScript then sub:HookScript("OnShow", function() pcall(P3.Crest, win) end) end
            end
        end
    end
    portrait:SetAlpha(0)
    c.glyph:SetTexture(MEDIA .. kind)
end

-- ------------------------------------------
-- Art rules (called first by the second pass's Rule)
-- ------------------------------------------
local VENDOR = { ["SpellIcon-256x256-RepairAll"] = "btn_repairall", ["SpellIcon-256x256-Repair"] = "btn_repair",
                 ["SpellIcon-256x256-SellJunk"] = "btn_junk" }
-- Our art goes on a texture of our own laid over Blizzard's, which turns
-- invisible but keeps its atlas: Blizzard reads some atlases back (the
-- scroll thumb asks for its size on every resize; replacing it raised
-- "Usage: C_Texture.GetAtlasInfo(atlas)", user, Nov 25 10:55).
local over = weak()
local function Ours(t, file, col, w, h, path)
    -- (returns our texture)
    local o = over[t]
    local par = t.GetParent and t:GetParent()
    if not par or not par.CreateTexture then return end
    if not o then
        local layer, sub = "ARTWORK", 0
        if t.GetDrawLayer then
            local ok, l, sl = pcall(t.GetDrawLayer, t)
            if ok and l then layer, sub = l, math.min((sl or 0) + 1, 7) end
        end
        o = Tex(par, layer, sub, path or (MEDIA .. file), col)
        over[t] = o
        local function Sync()
            o:SetShown(Shown(t))
            if o.mirrorDesat then
                local okd, d = pcall(function() return t.IsDesaturated and t:IsDesaturated() end)
                if o.SetDesaturated then o:SetDesaturated(okd and d or false) end
            end
        end
        HookShow(t, Sync)
        if hooksecurefunc and t.SetDesaturated then pcall(hooksecurefunc, t, "SetDesaturated", Sync) end
        Sync()
    end
    o:SetTexture(path or (MEDIA .. file))
    o:SetVertexColor(col[1], col[2], col[3], col[4] or 1)
    o:ClearAllPoints()
    if w then o:SetSize(w, h or w); o:SetPoint("CENTER", t, "CENTER")
    else o:SetPoint("TOPLEFT", t, "TOPLEFT"); o:SetPoint("BOTTOMRIGHT", t, "BOTTOMRIGHT") end
    t:SetAlpha(0)
    return o
end

-- The Aether page in place of the parchment, with a thin blue edge.
local pageEdge = weak()
local function Page(t)
    Ours(t, "page_aether", { 1, 1, 1, 1 })
    if not pageEdge[t] then
        local par = t.GetParent and t:GetParent()
        if par then
            local f = CreateFrame("Frame", nil, par)
            f:SetPoint("TOPLEFT", t, "TOPLEFT"); f:SetPoint("BOTTOMRIGHT", t, "BOTTOMRIGHT")
            pageEdge[t] = Edge(f, "BORDER", 3, { 0.24, 0.43, 0.69, 0.9 }, 0)
        end
    end
end

local cardFill, cardSel = weak(), weak()
local function FriendCardSel(card)
    local f = cardFill[card]; if not f then return end
    local sel = cardSel[card] or false
    local c = sel and { 0.19, 0.34, 0.58, 0.97 } or f.c
    f.o:SetVertexColor(c[1], c[2], c[3], c[4])
    local x = card.aetherSel
    if x then x.notch:SetShown(sel); for _, e in ipairs(x.edge) do e:SetShown(sel) end end
end
local friendSel = weak()
local function FriendSelected(t)
    local card = t.GetParent and t:GetParent()
    if not card or friendSel[t] then return end
    local notch = Tex(card, "OVERLAY", 4, WHITE, GOLD)
    notch:SetPoint("TOPLEFT", t, "TOPLEFT", 0, -4); notch:SetPoint("BOTTOMLEFT", t, "BOTTOMLEFT", 0, 4); notch:SetWidth(4)
    local f = CreateFrame("Frame", nil, card)
    f:SetPoint("TOPLEFT", t, "TOPLEFT"); f:SetPoint("BOTTOMRIGHT", t, "BOTTOMRIGHT")
    local e = Edge(f, "OVERLAY", 3, { BLUE[1], BLUE[2], BLUE[3], 1 }, 0)
    friendSel[t] = { notch, e }
    card.aetherSel = { notch = notch, edge = e }
    -- Blizzard marks the picked friend by locking the card's highlight
    if hooksecurefunc and card.LockHighlight then
        pcall(hooksecurefunc, card, "LockHighlight", function() cardSel[card] = true; FriendCardSel(card) end)
        pcall(hooksecurefunc, card, "UnlockHighlight", function() cardSel[card] = false; FriendCardSel(card) end)
    end
    notch:SetShown(false); for _, x in ipairs(e) do x:SetShown(false) end
    FriendCardSel(card)
    -- under the mouse: a thin blue edge (Blizzard's own highlight layer)
    if card.CreateTexture and Once(card, "frhover") then
        Edge(card, "HIGHLIGHT", 1, { BLUE[1], BLUE[2], BLUE[3], 0.9 }, 1)
    end
end


-- ------------------------------------------
-- Map quest log: tracker-style quest icons, navy track boxes, Aether
-- blue background (decided Nov 25 10:55 / 11:10, mock/maplog_icons.py,
-- mock/maplog_bg2.py)
-- ------------------------------------------
local poi = weak()
local function PoiLook(b)
    local o = poi[b]
    if o then return o end
    o = {}
    o.disc = Tex(b, "ARTWORK", 6, MEDIA .. "trk_disc", { NAVY[1], NAVY[2], NAVY[3], 0.96 })
    o.ring = Tex(b, "ARTWORK", 7, MEDIA .. "trk_ring", GOLD)
    o.dots = Tex(b, "OVERLAY", 6, MEDIA .. "trk_dots", GOLD)
    o.mark = b:CreateFontString(nil, "OVERLAY")
    if not (H.FontFile and pcall(o.mark.SetFont, o.mark, H.FontFile("Bold"), 11, "")) then o.mark:SetFontObject("GameFontNormal") end
    o.mark:SetPoint("CENTER", b, "CENTER", 0.5, 0); o.mark:SetText("?")
    o.mark:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
    for _, k in ipairs({ "disc", "ring", "dots" }) do
        o[k]:ClearAllPoints(); o[k]:SetSize(18, 18); o[k]:SetPoint("CENTER", b, "CENTER")
    end
    o.mark:Hide()
    poi[b] = o
    return o
end
local function PoiButton(t)     -- the icon sits in .Display inside the button
    local d = t.GetParent and t:GetParent()
    local b = d and d.GetParent and d:GetParent()
    return b and b.CreateTexture and b or nil
end
function P3.MapLogRule(t, a)
    if a == "UI-QuestPoi-QuestNumber" or a == "UI-QuestPoi-QuestNumber-Pressed" then
        t:SetAlpha(0)
        local b = t.GetParent and t:GetParent()
        if b and b.CreateTexture then PoiLook(b) end
        return true
    end
    if a == "UI-QuestPoi-InnerGlow" or a == "UI-QuestPoi-OuterGlow" then
        Tint(t, BLUE, 0.5); return true
    end
    if a == "Quest-In-Progress-Icon-yellow" or a == "UI-QuestIcon-TurnIn-Normal" then
        t:SetAlpha(0)
        local b = PoiButton(t)
        if b then
            local o = PoiLook(b)
            local turnIn = (a == "UI-QuestIcon-TurnIn-Normal")
            o.dots:SetShown(not turnIn); o.mark:SetShown(turnIn)
        end
        return true
    end
    if a == "QuestLog-icon-ticksquare" then
        t:SetAlpha(0)
        local cb = t.GetParent and t:GetParent()
        if cb and cb.CreateTexture and Once(cb, "tickbox") then
            local f = Tex(cb, "BACKGROUND", 7, WHITE, { NAVY[1], NAVY[2], NAVY[3], 0.95 })
            f:SetSize(12, 12); f:SetPoint("CENTER", cb, "CENTER")
            local e = CreateFrame("Frame", nil, cb)
            e:SetSize(12, 12); e:SetPoint("CENTER", cb, "CENTER")
            Edge(e, "BORDER", 1, { BLUE[1], BLUE[2], BLUE[3], 1 }, 0)
        end
        return true
    end
    if a == "QuestLog-main-background" then
        Ours(t, nil, { 35 / 255, 75 / 255, 115 / 255, 1 }, nil, nil, WHITE)
        return true
    end
    return false
end

function P.ExtraRule(t, a)
    if P3.MapLogRule(t, a) then return true end
    -- vendor buttons
    local v = VENDOR[a]
    if v then
        local b = t.GetParent and t:GetParent()
        local nm = b and b.GetName and b:GetName()
        if nm == "MerchantGuildBankRepairButton" then v = "btn_guild" end
        local o = Ours(t, v, GOLD, 26)
        -- gray when there's nothing to repair or sell (user, Nov 25).
        -- Repair item is never disabled by Blizzard, and repair all may
        -- not be refreshed after repairing, so the repair cost decides too.
        if o and b then
            local repair = nm and nm:find("Repair")
            Usable(b, o, function()
                if not repair or not GetRepairAllCost then return true end
                local ok, cost = pcall(GetRepairAllCost)
                return ok and type(cost) == "number" and cost > 0
            end, GOLD)
        end
        return true
    end
    -- scroll bars: beveled gold thumb, dark navy track, gold chevrons
    local part = a:match("^minimal%-scrollbar%-.*thumb%-(%a+)")
    if part then
        local f = (part == "top" and "sb_thumb_top") or (part == "bottom" and "sb_thumb_bot") or "sb_thumb_mid"
        Ours(t, f, { 1, 1, 1, 1 })
        return true
    end
    if a:find("^!?minimal%-scrollbar%-track") then
        if t.SetDesaturated then t:SetDesaturated(true) end
        t:SetVertexColor(0.1, 0.18, 0.32, 1)
        return true
    end
    local dir = a:match("^minimal%-scrollbar%-arrow%-(%a+)")
    if dir then
        local o = Ours(t, (dir == "top") and "chev3d_up" or "chev3d_down", { 1, 1, 1, 1 }, 14)
        -- gray at the end of the list (user, Nov 25)
        local b = t.GetParent and t:GetParent()
        if o and b and b.IsEnabled then Usable(b, o) end
        return true
    end
    -- quest and gossip pages
    if a == "QuestBG-Parchment" then Page(t); return true end
    -- Friends: our own navy card (Blizzard's art is near-black once tinted);
    -- the mouse-over highlight a soft blue; the picked card (Blizzard locks
    -- its highlight) brighter, with a gold notch and a blue edge
    if a == "friends-card-selected" then
        Tint(t, BLUE, 0.18)
        FriendSelected(t)
        return true
    end
    if a:find("^friends%-card%-") then
        local dim = a:find("disabled") or a:find("offline")
        local c = dim and { 0.07, 0.11, 0.18, 0.97 } or { 0.12, 0.22, 0.38, 0.97 }
        local o = Ours(t, nil, c, nil, nil, WHITE)
        local card = t.GetParent and t:GetParent()
        if card then cardFill[card] = { o = o, c = c } ; FriendCardSel(card) end
        return true
    end
    return false
end

-- ------------------------------------------
-- Text: gold quest headings, blue gossip choices
-- ------------------------------------------
local HEADINGS = { "QuestInfoTitleHeader", "QuestInfoDescriptionHeader", "QuestInfoObjectivesHeader",
    "QuestInfoRewardsFrameHeader", "QuestProgressTitleText", "QuestProgressRequiredItemsText",
    "QuestInfoRewardsHeader", "QuestFrameGreetingTitleText", "CurrentQuestsText", "AvailableQuestsText" }
function P3.Headings()
    for _, n in ipairs(HEADINGS) do
        local fs = _G[n]
        if type(fs) == "table" and fs.SetTextColor then P.KeepColor(fs, GOLD) end
    end
    local rf = _G.QuestInfoRewardsFrame
    if rf and T(rf, "Header") then P.KeepColor(rf.Header, GOLD) end
end

local function GossipChoice(f, root)
    if not (root and root.GetName and root:GetName() == "GossipFrame") then return end
    if not (T(f, "Icon") and f.GetFontString) then return end
    local ok, fs = pcall(f.GetFontString, f)
    if ok and fs and fs.SetTextColor then P.KeepColor(fs, BLUE) end
end

-- ------------------------------------------
-- Corner grip: drag to scale a window, right-click to reset
-- ------------------------------------------
local NO_GRIP = { QuestFrame = true, GossipFrame = true, QuestLogPopupDetailFrame = true }
local MIN_S, MAX_S = 0.7, 1.5
local function DB()
    AetherSkinsDB = AetherSkinsDB or {}
    AetherSkinsDB.scale = AetherSkinsDB.scale or {}
    return AetherSkinsDB.scale
end
function P3.ApplyScale(win)
    local name = win.GetName and win:GetName()
    local s = name and DB()[name]
    if s and not (InCombatLockdown and InCombatLockdown()) then pcall(win.SetScale, win, s) end
end
function P3.Grip(win)
    local name = win.GetName and win:GetName()
    if not name or NO_GRIP[name] or not Once(win, "grip") then return end
    local g = CreateFrame("Button", nil, win)
    g:SetSize(14, 14); g:SetPoint("BOTTOMRIGHT", win, "BOTTOMRIGHT", 6, -6)   -- on the rim, clear of scroll bars
    g:SetFrameLevel((win.GetFrameLevel and win:GetFrameLevel() or 1) + 20)
    for i, len in ipairs({ 12, 8, 4 }) do      -- three short gold strokes, corner to corner
        local l = Tex(g, "OVERLAY", 1, WHITE, { GOLD[1], GOLD[2], GOLD[3], 0.9 })
        l:SetSize(len * 1.41, 2); l:SetPoint("CENTER", g, "BOTTOMRIGHT", -len / 2 - 1, len / 2 + 1)
        if l.SetRotation then l:SetRotation(math.pi / 4) end
    end
    local hl = Tex(g, "HIGHLIGHT", 0, WHITE, { GOLD[1], GOLD[2], GOLD[3], 0.25 }); hl:SetAllPoints()
    g:RegisterForClicks("RightButtonUp")
    g:SetScript("OnClick", function()
        if InCombatLockdown and InCombatLockdown() then return end
        DB()[name] = nil; pcall(win.SetScale, win, 1)
    end)
    g:SetScript("OnMouseDown", function(self, btn)
        if btn ~= "LeftButton" or (InCombatLockdown and InCombatLockdown()) then return end
        local cx, cy = GetCursorPosition()
        local s0, w0 = win:GetScale() or 1, win:GetWidth() or 400
        self:SetScript("OnUpdate", function()
            local x, y = GetCursorPosition()
            local ui = (UIParent and UIParent:GetEffectiveScale()) or 1
            local d = ((x - cx) - (y - cy)) / 2 / ui           -- right and down grow it
            local s = math.max(MIN_S, math.min(MAX_S, s0 * (1 + d / (w0 * s0))))
            pcall(win.SetScale, win, s)
            DB()[name] = math.floor(s * 100 + 0.5) / 100
        end)
    end)
    g:SetScript("OnMouseUp", function(self) self:SetScript("OnUpdate", nil) end)
    g:SetScript("OnEnter", function(self)
        if not GameTooltip then return end
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText("Drag to resize", GOLD[1], GOLD[2], GOLD[3])
        GameTooltip:AddLine("Right-click: normal size", 1, 1, 1)
        GameTooltip:Show()
    end)
    g:SetScript("OnLeave", function() if GameTooltip then GameTooltip:Hide() end end)
    if win.HookScript then win:HookScript("OnShow", function() P3.ApplyScale(win) end) end
    P3.ApplyScale(win)
end

-- ------------------------------------------
-- Wiring: after the second pass's walk of each window
-- ------------------------------------------
local afterWalk = W.AfterWalk
function W.AfterWalk(root)
    if afterWalk then pcall(afterWalk, root) end
    pcall(P3.Crest, root)
    pcall(P3.Grip, root)
    pcall(P3.Headings)
end
local visit = W.Visit
function W.Visit(f, root)
    if visit then visit(f, root) end
    if not Forbidden(f) then pcall(GossipChoice, f, root) end
end
