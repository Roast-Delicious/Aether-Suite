-- AetherSkins, second pass (Nov 25): Forever's own window parts by name,
-- from the user's /skins tree dumps (tools/dumps/), styled to the approved
-- mockups (mock/pass2_*.py, talent_*.py, roles.py):
--   side tabs navy (gold edge + notch when selected); list headers as
--   navy strips with gold text; capsule rep and progress bars; blue
--   selected rows; bronze lines and borders blue; parchment and brown
--   backgrounds faded; friend cards navy; vendor tiles navy with blue icon
--   frames; Group Finder role buttons as gold glyphs on a navy disc with a
--   blue ring (gold when picked); the talent tree (maxed = gold tint + gold
--   frame, some points = blue, can take = art + blue glow, not taken with
--   no points left = navy, locked = gray, 3D arrows, "2 of 5" pills on the
--   frame's bottom edge, spec icons gold on navy); the Spellbook in the same
--   scheme; the world map's chrome, breadcrumb bar and quest log.
--
-- Same safety rules as the first pass: Blizzard's textures are only faded,
-- desaturated, tinted or given our texture file; nothing is moved; hooks
-- are post-hooks (hooksecurefunc); our notes live in weak tables.

local W = AetherSkins_Windows
if not W or not W.H then return end
local H = W.H
local Tex, Fade, T, Edge, NavyBox, Forbidden = H.Tex, H.Fade, H.T, H.Edge, H.NavyBox, H.Forbidden
local MEDIA, WHITE, GOLD, BLUE, NAVY, TEXT = H.MEDIA, H.WHITE, H.GOLD, H.BLUE, H.NAVY, H.TEXT
local DARK = { 0.03, 0.047, 0.086 }
local GRAY = { 0.27, 0.29, 0.33 }
local P = {}
W.P2 = P

local weak = function() return setmetatable({}, { __mode = "k" }) end
local hookedAtlas, made, busy = weak(), weak(), weak()
local nodeOf = weak()            -- talent StateBorder / Icon -> its node button
local sidetabsIn = weak()        -- window -> true when it has side tabs

local function Atlas(t)
    if not (t and t.GetAtlas) then return nil end
    local ok, a = pcall(t.GetAtlas, t)
    if not ok or a == nil or (issecretvalue and issecretvalue(a)) then return nil end
    return a
end
local function FileID(t)
    if not (t and t.GetTexture) then return nil end
    local ok, f = pcall(t.GetTexture, t)
    if not ok or f == nil or (issecretvalue and issecretvalue(f)) then return nil end
    return tostring(f)
end
local function Shown(r) return r and r.IsShown and r:IsShown() or false end
local function Tint(t, c, a, desat)
    if not (t and t.SetVertexColor) or Forbidden(t) then return end
    if desat ~= false and t.SetDesaturated then t:SetDesaturated(true) end
    t:SetVertexColor(c[1], c[2], c[3], a or c[4] or 1)
end
local function Once(t, key)
    made[t] = made[t] or {}
    if made[t][key] then return false end
    made[t][key] = true
    return true
end
local function HookShow(r, fn)
    if not r or not r.HookScript or not Once(r, "showhook") then return end
    if hooksecurefunc then
        for _, m in ipairs({ "Show", "Hide", "SetShown" }) do
            if r[m] then pcall(hooksecurefunc, r, m, fn) end
        end
    end
end

-- ------------------------------------------
-- Shared pieces
-- ------------------------------------------
local LIGHT = { 0.82, 0.84, 0.87 }
local NAVYB = { 0.24, 0.35, 0.55 }        -- navy frame (not taken)
local NAVYI = { 0.36, 0.52, 0.85 }        -- navy tint for icons (multiplies the gray)

-- A capsule pill around a font string: dark fill, colored edge.
local function PillOn(owner, fs, c, layer)
    local p = AetherSkins_Pill and AetherSkins_Pill(owner, layer or "OVERLAY")
    if not p then return end
    for _, t in ipairs(p.parts) do W.ours[t] = true end
    for _, k in ipairs({ "l", "r", "m" }) do p[k]:SetVertexColor(DARK[1], DARK[2], DARK[3], 1) end
    function p:Color(col) for _, k in ipairs({ "ll", "rl", "top", "bot" }) do self[k]:SetVertexColor(col[1], col[2], col[3], 1) end end
    function p:SetShown(v) for _, t in ipairs(self.parts) do t:SetShown(v) end end
    p:Color(c); p:Place(fs, 5, 2)
    return p
end

-- Navy header strip (tracker style): fading navy band, gold underline.
local function HeaderStrip(b)
    if not Once(b, "header") then return end
    local band = Tex(b, "BACKGROUND", 2, WHITE, { 1, 1, 1, 1 })
    band:SetPoint("TOPLEFT", b, "TOPLEFT", 0, -1); band:SetPoint("BOTTOMRIGHT", b, "BOTTOMRIGHT", 0, 2)
    if band.SetGradient and CreateColor then
        band:SetGradient("HORIZONTAL", CreateColor(NAVY[1], NAVY[2], NAVY[3], 0.95), CreateColor(NAVY[1], NAVY[2], NAVY[3], 0.15))
    else band:SetVertexColor(NAVY[1], NAVY[2], NAVY[3], 0.8) end
    local line = Tex(b, "BORDER", 2, WHITE, { GOLD[1], GOLD[2], GOLD[3], 0.85 })
    line:SetPoint("BOTTOMLEFT", b, "BOTTOMLEFT", 0, 1); line:SetPoint("BOTTOMRIGHT", b, "BOTTOMRIGHT", 0, 1); line:SetHeight(1)
    for _, k in ipairs({ "Name", "ButtonText", "Text" }) do
        local fs = T(b, k)
        if fs and fs.SetTextColor then fs:SetTextColor(GOLD[1], GOLD[2], GOLD[3]) end
    end
end

-- Capsule track behind a Blizzard status bar (rep, standing): dark, blue edge.
local function Capsule(bar)
    if not Once(bar, "capsule") then return end
    local a = CreateFrame("Frame", nil, bar)
    a:SetPoint("LEFT", bar, "LEFT", 7, 0); a:SetPoint("RIGHT", bar, "RIGHT", -7, 0); a:SetHeight(13)
    local p = AetherSkins_Pill and AetherSkins_Pill(bar, "BACKGROUND")
    if p then
        for _, t in ipairs(p.parts) do W.ours[t] = true end
        for _, k in ipairs({ "l", "r", "m" }) do p[k]:SetVertexColor(DARK[1], DARK[2], DARK[3], 0.95) end
        for _, k in ipairs({ "ll", "rl", "top", "bot" }) do p[k]:SetVertexColor(0.24, 0.43, 0.69, 1) end
        p:Place(a, 0, 1)
    end
    -- Blizzard colors the fill by standing; its yellow becomes Aether gold
    -- and its green the Aether green (#22e650), approved Nov 24.
    local fill = T(bar, "Fill")
    if fill and hooksecurefunc and Once(fill, "fillcolor") then
        local function Fix(self, r, g, b)
            if busy[self] or type(r) ~= "number" then return end
            local nr, ng, nb
            if r > 0.85 and g > 0.55 and g < 0.95 and b < 0.3 then nr, ng, nb = GOLD[1], GOLD[2], GOLD[3]
            elseif g > 0.55 and r < 0.4 and b < 0.4 then nr, ng, nb = 0.133, 0.902, 0.314 end
            if nr then busy[self] = true; self:SetVertexColor(nr, ng, nb); busy[self] = nil end
        end
        pcall(hooksecurefunc, fill, "SetVertexColor", Fix)
        local ok, r, g, b = pcall(fill.GetVertexColor, fill)
        if ok then Fix(fill, r, g, b) end
    end
end

-- Small navy box with a white glyph (maximize / minimize).
local function WinButton(b, kind)
    if not b or not Once(b, "winbtn") then return end
    local box = Tex(b, "BACKGROUND", 1, WHITE, NAVY)
    box:SetSize(20, 20); box:SetPoint("CENTER", b, "CENTER", 0, 0)
    Edge(b, "BORDER", 2, { BLUE[1], BLUE[2], BLUE[3], 1 }, 4)
    if kind == "min" then
        local l = Tex(b, "ARTWORK", 1, WHITE, TEXT); l:SetSize(10, 2); l:SetPoint("CENTER", box, "CENTER", 0, -3)
    else
        for _, s in ipairs({ { "TOP", 10, 2, 0, 4 }, { "BOTTOM", 10, 2, 0, -4 }, { "LEFT", 2, 10, -4, 0 }, { "RIGHT", 2, 10, 4, 0 } }) do
            local l = Tex(b, "ARTWORK", 1, WHITE, TEXT); l:SetSize(s[2], s[3]); l:SetPoint("CENTER", box, "CENTER", s[4], s[5])
        end
    end
    local hl = Tex(b, "HIGHLIGHT", 0, WHITE, { BLUE[1], BLUE[2], BLUE[3], 0.3 }); hl:SetAllPoints(box); hl:SetBlendMode("ADD")
end

-- ------------------------------------------
-- Texture rules, by atlas name (or file ID for old art)
-- ------------------------------------------
local FADE = {}
for _, a in ipairs({ "UI-Character-Info-General-BG", "UI-Character-Info-Stat-BG", "UI-Character-Info-Stat-StoneBG3",
    "friends-frame-topTexBG", "friends-frame-bottomTexBG", "QuestLog-main-background", "QuestLog-frame-filigree",
    "QuestLog-Frame-Gradient-bottom", "spellbook-Page-Left-C60", "spellbook-Page-Right-C60", "spellbook-list-backplate",
    "spellbook-corner-flipbook-evergreen", "Legacy-Rewards-Tracker-background", "groupfinder-background",
    "groupfinder-roles-background", "gamepad-mapquestlog-bgtile-2k", "gamepad-mapquestlog-bg-vignette",
    "UI-Merchant-BotFrame", "MapCornerShadow-Right", "_UI-Frame-TopTileStreaks", "common-stat-bar-BG",
    "128-RedButton-Left", "128-RedButton-Right", "_128-RedButton-Center", "128-RedButton-Highlight",
    "spellbook-Tab-Frame-glow-gradient-C60", "spellbook-item-needtrainer-shadow", "common-button-list-collapseExpand",
    "talents-node-square-greenglow", "talents-node-circle-greenglow", "talents-node-choice-greenglow",
    "RedButton-Expand", "RedButton-Expand-Pressed", "RedButton-Expand-Disabled",
    "RedButton-Condense", "RedButton-Condense-Pressed", "RedButton-Condense-disabled", "RedButton-Highlight" }) do FADE[a] = true end
local BLUEL, NAVYF, BLUEH, GOLDT, LIGHTT = {}, {}, {}, {}, {}
for _, a in ipairs({ "common-framedivider", "UI-Character-Info-ScrollLine-Long", "UI-Character-Info-ScrollLine",
    "perks-divider-short", "Talents-divider-left-c60", "Talents-divider-right-c60", "Talents-divider-vertical-c60",
    "Talents-small-divider-c60", "Talents-inner-frame-c60", "spellbook-divider", "questlog_line_scrollbar",
    "QuestLog-frame", "Legacy-Rewards-Tracker-Icons-Frame-Disable", "Legacy-Rewards-Tracker-Icons-Frame",
    "Legacy-Progressbar-Frame", "Talents-Main-Ring-c60", "spellbook-item-iconframe", "talents-node-circle-gray",
    "QuestLog-icon-ticksquare", "common-insideframe" }) do BLUEL[a] = true end
for _, a in ipairs({ "Talents-Main-Ring-Box-c60", "Talents-Square-Box-c60", "UI-Character-Info-Title",
    "UI-Character-Info-ItemLevel-Bounce", "common-dropdown-textholder", "common-dropdown-b-button",
    "common-button-tertiary-square-normal", "common-button-tertiary-square-pressed", "Legacy-Progressbar-BG",
    "Legacy-Rewards-Tracker-Cards-Disable", "Legacy-Rewards-Tracker-Cards", "Legacy-Rewards-Tracker-Diamond-Disable",
    "spellbook-Tab-Frame-C60", "groupfinder-button-cover", "groupfinder-button-cover-down" }) do NAVYF[a] = true end
for _, a in ipairs({ "charactercreate-customize-dropdown-linemouseover-side", "charactercreate-customize-dropdown-linemouseover-middle",
    "friends-card-selected", "groupfinder-button-cover-hover", "QuestLog-quest-glow-yellow", "spellbook-item-iconframe-hover",
    "spellbook-item-iconframe-passive-hover", "UI-Character-Info-Line-Bounce2" }) do BLUEH[a] = true end
for _, a in ipairs({ "Legacy-Progressbar-Fill", "Legacy-Rewards-Tracker-Diamond", "spellbook-Tab-Frame-Glow-C60",
    "QuestLog-icon-checkmark-yellow", "common-button-list-minus", "common-button-list-plus" }) do GOLDT[a] = true end
for _, a in ipairs({ "common-dropdown-a-button", "QuestLog-icon-setting", "QuestCollapse-Hide-Up", "QuestCollapse-Hide-Down",
    "QuestCollapse-Show-Up", "QuestCollapse-Show-Down", "friends-icon-menu", "common-search-clearbutton" }) do LIGHTT[a] = true end
-- old art by file ID
local FADEID = { ["130766"] = "slot", ["136423"] = true, ["525911"] = true, ["130841"] = "itemframe" }
local NAVYID = { ["516764"] = true, ["516763"] = true, ["423811"] = true, ["136430"] = true, ["136467"] = true }
local LIGHTID = { ["130864"] = true, ["130865"] = true, ["130866"] = true, ["130867"] = true, ["130868"] = true,
                  ["130869"] = true, ["796424"] = true, ["796423"] = true, ["423808"] = true }

local function IconFrame(b)     -- a blue frame around an item button (vendor tiles, buy-back)
    if not b or not Once(b, "iconframe") then return end
    Edge(b, "OVERLAY", 6, { BLUE[1], BLUE[2], BLUE[3], 1 }, 0)
    Edge(b, "OVERLAY", 6, { BLUE[1], BLUE[2], BLUE[3], 0.55 }, 1)
end

local Rule      -- forward
function P.Texture(t)
    if not t or W.ours[t] or Forbidden(t) then return end
    if nodeOf[t] then P.Node(nodeOf[t]); return end
    if hooksecurefunc and not hookedAtlas[t] and t.SetAtlas then
        hookedAtlas[t] = true
        pcall(hooksecurefunc, t, "SetAtlas", function(self) if W.Enabled() then pcall(P.Texture, self) end end)
    end
    local a = Atlas(t)
    if a then return Rule(t, a) end
    local id = FileID(t)
    if not id then return end
    if FADEID[id] then
        t:SetAlpha(0)
        local par = t.GetParent and t:GetParent()
        if FADEID[id] == "itemframe" then IconFrame(par)
        elseif FADEID[id] == "slot" and par and par.GetObjectType then
            local ok, kind = pcall(par.GetObjectType, par)
            if ok and kind == "Button" and Once(par, "slotbox") then NavyBox(par, -1, -1, -1, -1) end
        end
    elseif NAVYID[id] then Tint(t, { 0.2, 0.36, 0.62 }, 0.95)
    elseif LIGHTID[id] then Tint(t, { 0.6, 0.78, 1 }) end
end

local ARROW = { yellow = "gold", gold = "gold", green = "blue" }
function Rule(t, a)
    if FADE[a] then
        t:SetAlpha(0)
        local par = t.GetParent and t:GetParent()
        if a == "common-button-list-collapseExpand" and par then HeaderStrip(par)
        elseif a == "common-stat-bar-BG" and par then Capsule(par)
        elseif a:find("^RedButton%-Expand") and par then WinButton(par, "max")
        elseif a:find("^RedButton%-Condense") and par then WinButton(par, "min") end
        return
    end
    if BLUEL[a] then return Tint(t, BLUE, 0.9) end
    if NAVYF[a] then return Tint(t, { 0.16, 0.3, 0.52 }, 0.95) end
    if BLUEH[a] then return Tint(t, BLUE, 0.4) end
    if GOLDT[a] then return Tint(t, GOLD) end
    if LIGHTT[a] then return Tint(t, { 0.75, 0.86, 1 }) end
    if a == "friends-card-battleNet" then return Tint(t, { 0.16, 0.33, 0.6 }, 0.95) end
    if a == "friends-card-disabled" then return Tint(t, { 0.1, 0.15, 0.24 }, 0.95) end
    if a == "spellbook-item-backplate" then return Tint(t, { 0.12, 0.25, 0.46 }, 0.6) end
    local state = a:match("^talents%-arrow%-head%-(%a+)")
    if state then
        local col = ARROW[state] or "gray"
        t:SetTexture(MEDIA .. "arrow_head_" .. col); t:SetVertexColor(1, 1, 1, 1)
        if t.SetDesaturated then t:SetDesaturated(false) end
        t:SetSize(20, 20)
        local par = t.GetParent and t:GetParent()
        local line = par and T(par, "Line")
        if line and line.SetThickness then
            line:SetThickness(6)
            if line.SetTexture then line:SetTexture(MEDIA .. "arrow_shaft_" .. col) end
            if line.SetVertexColor then line:SetVertexColor(1, 1, 1, 1) end
        end
        return
    end
end

-- ------------------------------------------
-- Frames with their own treatment
-- ------------------------------------------
-- Side tabs (Character, Friends, Progress Track): navy box, blue edge; the
-- selected one gets a gold edge and a gold notch on the window side.
local tabParts = weak()
local function SideTabColor(tab)
    local p = tabParts[tab]; if not p then return end
    local sel = Shown(T(tab, "SelectedTexture"))
    local c = sel and GOLD or BLUE
    for _, e in ipairs(p.edge) do e:SetVertexColor(c[1], c[2], c[3], 1) end
    p.notch:SetShown(sel)
    p.fill:SetVertexColor(sel and 0.11 or NAVY[1], sel and 0.23 or NAVY[2], sel and 0.41 or NAVY[3], 0.97)
end
function P.SideTab(tab)
    if not Once(tab, "sidetab") then return end
    Fade(T(tab, "Background")); Fade(T(tab, "TabGlow")); Fade(T(tab, "HighlightTexture"))
    local sel = T(tab, "SelectedTexture"); if sel then sel:SetAlpha(0) end
    local fill, edge = NavyBox(tab, 3, 0, 3, 3)
    local notch = Tex(tab, "BORDER", 3, WHITE, GOLD)
    notch:SetPoint("TOPLEFT", fill, "TOPLEFT", 0, -8); notch:SetPoint("BOTTOMLEFT", fill, "BOTTOMLEFT", 0, 8); notch:SetWidth(4)
    local hl = Tex(tab, "HIGHLIGHT", 0, WHITE, { BLUE[1], BLUE[2], BLUE[3], 0.22 }); hl:SetAllPoints(fill); hl:SetBlendMode("ADD")
    tabParts[tab] = { fill = fill, edge = edge, notch = notch }
    HookShow(sel, function() SideTabColor(tab) end)
    SideTabColor(tab)
end

-- Spellbook's square category tabs: navy square, gold when active, icon
-- gold on navy (like the talent spec icons).
function W.SquareTab(tab)
    local ic = T(tab, "Icon")
    if ic and ic.SetDesaturated then
        ic:SetDesaturated(true); ic:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 1)
        if ic.SetBlendMode then ic:SetBlendMode("ADD") end
    end
    for _, k in ipairs({ "LeftHighlight", "MiddleHighlight", "RightHighlight" }) do Fade(T(tab, k)) end
end

-- Group Finder role buttons: gold glyph on a navy disc, blue ring; the ring
-- turns gold when the role is picked; dim when it can't be picked.
local ROLE = { Tank = "tank", Healer = "healer", DPS = "dps", Damager = "dps", Leader = "leader" }
local roleParts = weak()
local function RoleUpdate(b)
    local p = roleParts[b]; if not p then return end
    local cb = T(b, "CheckButton") or T(b, "checkButton")
    local picked = cb and cb.GetChecked and cb:GetChecked()
    local off = Shown(T(b, "cover")) or (b.IsEnabled and not b:IsEnabled())
    local c = picked and GOLD or BLUE
    p.ring:SetVertexColor(c[1], c[2], c[3], 1)
    if off then p.glyph:SetVertexColor(0.47, 0.38, 0.2, 1) else p.glyph:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 1) end
end
function P.Role(b, kind, icon)
    if not Once(b, "role") then return end
    icon:SetAlpha(0)
    local w = math.min(b:GetWidth() or 64, b:GetHeight() or 64)
    local d = Tex(b, "BACKGROUND", 2, MEDIA .. "disc_plain", NAVY); d:SetSize(w * 0.92, w * 0.92); d:SetPoint("CENTER")
    local ring = Tex(b, "BORDER", 2, MEDIA .. "ring_thin", BLUE); ring:SetAllPoints(d)
    local g = Tex(b, "ARTWORK", 3, MEDIA .. "role_" .. kind, GOLD); g:SetSize(w * 0.5, w * 0.5); g:SetPoint("CENTER")
    roleParts[b] = { ring = ring, glyph = g }
    for _, r in ipairs({ b:GetRegions() }) do
        local a = Atlas(r)
        if a and a:find("^UI%-LFG%-RoleIcon%-.*%-Background$") then r:SetAlpha(0) end
    end
    local cov = T(b, "cover"); if cov then cov:SetAlpha(0); HookShow(cov, function() RoleUpdate(b) end) end
    local cb = T(b, "CheckButton") or T(b, "checkButton")
    if cb and hooksecurefunc then
        pcall(hooksecurefunc, cb, "SetChecked", function() RoleUpdate(b) end)
        cb:HookScript("OnClick", function() RoleUpdate(b) end)
    end
    RoleUpdate(b)
end

-- Talent nodes: see the header. State comes from the frame atlas Blizzard
-- sets (yellow = maxed, green = some points, gray = no points, locked).
local nodeParts = weak()
local function NodeRanks(node)
    local n, m
    if node.GetNodeInfo then
        local ok, info = pcall(node.GetNodeInfo, node)
        if ok and type(info) == "table" then
            n = info.currentRank or info.ranksPurchased; m = info.maxRanks
        end
    end
    if not n then
        local st = T(node, "SpendText")
        local ok, txt = pcall(function() return st and st:GetText() end)
        if ok and txt and not (issecretvalue and issecretvalue(txt)) then n = tonumber(txt) end
    end
    return n, m
end
function P.Node(node)
    if busy[node] then return end
    busy[node] = true
    local ok, err = pcall(function()
        local sb, ic = T(node, "StateBorder"), T(node, "Icon")
        local p = nodeParts[node]
        if not p then
            p = {}
            nodeParts[node] = p
            if sb then nodeOf[sb] = node end
            local w = node:GetWidth() or 40
            p.glow = Tex(node, "BACKGROUND", -2, MEDIA .. "glow_sq", BLUE)
            p.glow:SetSize(w * 2, w * 2); p.glow:SetPoint("CENTER")
            p.text = node:CreateFontString(nil, "OVERLAY", nil, 7)
            p.text:SetFont(H.FontFile("Bold"), 10, ""); p.text:SetPoint("CENTER", node, "BOTTOM", 0, 2)
            p.pill = PillOn(node, p.text, GOLD, "OVERLAY")
            for _, k in ipairs({ "SpendText", "SpendTextShadow1", "SpendTextShadow2", "SpendTextShadow3", "SpendTextShadow4" }) do
                local fs = T(node, k)
                if fs then fs:SetAlpha(0); if hooksecurefunc then pcall(hooksecurefunc, fs, "SetText", function() P.Node(node) end) end end
            end
            for _, k in ipairs({ "Glow", "SelectableGlow", "SelectableIcon" }) do
                local r = T(node, k); if r then r:SetAlpha(0); HookShow(r, function() P.Node(node) end) end
            end
            if ic and hooksecurefunc then pcall(hooksecurefunc, ic, "SetDesaturated", function() P.Node(node) end) end
        end
        local a = Atlas(sb) or ""
        local state = a:find("yellow") and "max" or a:find("green") and "part" or a:find("locked") and "lock"
                      or a:find("gray") and "gray" or nil
        if state == "gray" then
            state = (Shown(T(node, "SelectableIcon")) or Shown(T(node, "Glow")) or Shown(T(node, "SelectableGlow"))) and "can" or "none"
        end
        p.glow:SetShown(state == "can")
        local bc = ({ max = GOLD, part = BLUE, can = LIGHT, none = NAVYB, lock = GRAY })[state]
        if bc then Tint(sb, bc, 1); Tint(T(node, "StateBorderHover"), bc, 1) end
        if ic then
            if state == "max" then ic:SetDesaturated(true); ic:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 1)
            elseif state == "part" or state == "can" then ic:SetDesaturated(false); ic:SetVertexColor(1, 1, 1, 1)
            elseif state == "none" then ic:SetDesaturated(true); ic:SetVertexColor(NAVYI[1], NAVYI[2], NAVYI[3], 1)
            elseif state == "lock" then ic:SetDesaturated(true); ic:SetVertexColor(0.55, 0.55, 0.58, 1) end
        end
        local dov = T(node, "DisabledOverlay")
        if dov then dov:SetAlpha((state == "none" or state == "can") and 0 or 1) end
        local show = (state == "max" or state == "part")
        if show then
            local n, m = NodeRanks(node)
            p.text:SetText(n and (m and (n .. " of " .. m) or tostring(n)) or "")
            if p.pill then p.pill:Place(p.text, 5, 2) end
            local c = state == "max" and GOLD or BLUE
            p.text:SetTextColor(c[1], c[2], c[3]); if p.pill then p.pill:Color(c) end
            show = n ~= nil
        end
        p.text:SetShown(show); if p.pill then p.pill:SetShown(show) end
    end)
    busy[node] = nil
end

-- Spec header icons (Talents): gold on navy, on a navy disc.
function P.SpecIcon(f)
    if not Once(f, "spec") then return end
    for _, r in ipairs({ f:GetRegions() }) do
        local ok, kind = pcall(r.GetObjectType, r)
        if ok and kind == "Texture" and not Atlas(r) and not W.ours[r] and (r:GetWidth() or 0) <= 44 then
            local d = Tex(f, "BACKGROUND", 3, MEDIA .. "disc_plain", NAVY)
            d:SetSize((r:GetWidth() or 36) + 2, (r:GetHeight() or 36) + 2); d:SetPoint("CENTER", r, "CENTER")
            r:SetDesaturated(true); r:SetVertexColor(GOLD[1], GOLD[2], GOLD[3], 1)
            if r.SetBlendMode then r:SetBlendMode("ADD") end
        end
    end
end

-- Spellbook entries: known = blue frame (ring for passives, from the rules);
-- trainable now = blue glow + "Trainer" pill; level too low = navy icon +
-- the level in a pill; unavailable = gray.
local spellParts = weak()
local function SpellUpdate(item)
    local p = spellParts[item]; if not p then return end
    local b = T(item, "Button"); local ic = b and T(b, "Icon")
    local tc = T(item, "TextContainer"); local req = tc and T(tc, "RequiredLevel")
    local train = Shown(b and T(b, "TrainableShadow")) or Shown(b and T(b, "TrainableBackplate"))
    local lowLevel = Shown(req) and req.GetText and (function() local ok, t = pcall(req.GetText, req); return ok and t and t ~= "" end)()
    p.glow:SetShown(train); p.trainText:SetShown(train); p.trainPill:SetShown(train)
    if train and p.trainPill.Place then p.trainPill:Place(p.trainText, 5, 2) end
    if req then
        req:SetTextColor(0.55, 0.72, 1)
        if p.reqPill then
            p.reqPill:SetShown(lowLevel and true or false)
            if lowLevel then p.reqPill:Place(req, 5, 2) end
        end
    end
    if ic and not busy[item] then
        busy[item] = true
        local ok, desat = pcall(function() return ic.IsDesaturated and ic:IsDesaturated() end)
        if lowLevel then ic:SetDesaturated(true); ic:SetVertexColor(NAVYI[1], NAVYI[2], NAVYI[3], 1)
        elseif ok and desat then ic:SetVertexColor(0.55, 0.55, 0.58, 1)
        else ic:SetVertexColor(1, 1, 1, 1) end
        busy[item] = nil
    end
end
function P.SpellItem(item)
    if not Once(item, "spell") then return end
    local b = T(item, "Button")
    local w = b and b:GetWidth() or 40
    local p = {}
    p.glow = Tex(b or item, "BACKGROUND", -2, MEDIA .. "glow_sq", BLUE); p.glow:SetSize(w * 2, w * 2); p.glow:SetPoint("CENTER", b or item, "CENTER")
    local tc = T(item, "TextContainer")
    local name = tc and T(tc, "Name")
    p.trainText = item:CreateFontString(nil, "OVERLAY", nil, 7)
    p.trainText:SetFont(H.FontFile("Bold"), 10, ""); p.trainText:SetText("Trainer"); p.trainText:SetTextColor(BLUE[1], BLUE[2], BLUE[3])
    if name then p.trainText:SetPoint("TOPLEFT", name, "BOTTOMLEFT", 6, -4) else p.trainText:SetPoint("BOTTOMLEFT", item, "BOTTOMLEFT", 60, 8) end
    p.trainPill = PillOn(item, p.trainText, BLUE, "OVERLAY") or { SetShown = function() end }
    local req = tc and T(tc, "RequiredLevel")
    if req then p.reqPill = PillOn(item, req, { 0.35, 0.51, 0.75 }, "OVERLAY") end
    spellParts[item] = p
    if b then
        HookShow(T(b, "TrainableShadow"), function() SpellUpdate(item) end)
        HookShow(T(b, "TrainableBackplate"), function() SpellUpdate(item) end)
        local ic = T(b, "Icon")
        if ic and hooksecurefunc then pcall(hooksecurefunc, ic, "SetDesaturated", function() SpellUpdate(item) end) end
        local tb = T(b, "TrainableBackplate"); if tb then tb:SetAlpha(0) end
    end
    if req then HookShow(req, function() SpellUpdate(item) end); if hooksecurefunc then pcall(hooksecurefunc, req, "SetText", function() SpellUpdate(item) end) end end
    SpellUpdate(item)
end

-- Vendor tiles: navy tile behind each item, the brown plaque faded.
function P.MerchantTile(f)
    if not Once(f, "mtile") then return end
    local fill = NavyBox(f, -2, -2, -2, -2)
    fill:SetVertexColor(NAVY[1], NAVY[2], NAVY[3], 0.75)
end

-- ------------------------------------------
-- Visiting every frame and texture of a window
-- ------------------------------------------
function W.Visit(f, root)
    if Forbidden(f) then return end
    -- textures
    if f.GetRegions then
        for _, r in ipairs({ f:GetRegions() }) do
            local ok, kind = pcall(r.GetObjectType, r)
            if ok and kind == "Texture" then pcall(P.Texture, r) end
        end
    end
    -- frames with their own treatment
    local bg = T(f, "Background")
    if bg and Atlas(bg) == "common-sidetab" and T(f, "SelectedTexture") then
        P.SideTab(f); sidetabsIn[root] = true; return
    end
    if T(f, "StateBorder") and T(f, "Icon") and (T(f, "SpendText") or f.GetNodeInfo) then P.Node(f); return end
    if T(f, "MainRing") and T(f, "TextBackground") then P.SpecIcon(f); return end
    if T(f, "Backplate") and T(f, "Button") and T(f.Button, "Border") then P.SpellItem(f); return end
    local nm = f.GetName and f:GetName()
    if nm and (nm:find("^MerchantItem%d+$") or nm == "MerchantBuyBackItem") then P.MerchantTile(f) end
    if f.GetRegions and not roleParts[f] then
        for _, r in ipairs({ f:GetRegions() }) do
            local a = Atlas(r)
            local role = a and a:match("^UI%-LFG%-RoleIcon%-(%a+)$")
            if role and ROLE[role] then P.Role(f, ROLE[role], r); break end
        end
    end
end

-- After a window's walk: windows with side tabs drop the right chevron.
function W.AfterWalk(root)
    if sidetabsIn[root] and W.chev[root] and W.chev[root].right then
        for _, t in ipairs(W.chev[root].right) do t:Hide() end
    end
end
