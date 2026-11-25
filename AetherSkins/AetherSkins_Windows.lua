-- AetherSkins: Blizzard's windows in the Aether look (user, Nov 25: "the
-- entire interface"). One skinner for every window built on Blizzard's
-- standard portrait-window templates (PortraitFrameTemplate,
-- ButtonFrameTemplate and friends, wow-ui-source 12.1.5), which covers
-- Character/Reputation, Friends, Talents, Progress Track and most others.
--
-- The approved look (style A, Nov 24): rounded dark panel, blue edge with a
-- fine inner line, soft blue glow, navy title strip with a gold underline,
-- gold title text, the four 3D gold chevrons, a plain navy crest with a blue
-- rim behind the portrait, a navy close button with a white x. Inside:
-- navy buttons with a blue edge and white text, dark checkboxes with a gold
-- check, blue scroll bars, navy tabs (gold edge when selected), and
-- Blizzard's yellow text turned Aether gold (the only yellow).
--
-- Safety: Blizzard's own art is only faded out (SetAlpha 0), never removed,
-- moved or resized, so their code keeps working; nothing is written into
-- Blizzard's frames (our notes live in weak tables); windows that open in
-- combat are skinned right after it. /skins windows off + /reload turns it
-- all off.

local MEDIA = "Interface\\AddOns\\AetherSkins\\Media\\"
local WHITE = "Interface\\Buttons\\WHITE8X8"
local GOLD  = { 1, 0.69, 0 }
local BLUE  = { 0.3, 0.65, 1 }
local NAVY  = { 0.075, 0.157, 0.29 }
local PANEL = { 0.047, 0.055, 0.075, 0.95 }
local TEXT  = { 0.92, 0.93, 0.96 }

local function FontFile(weight)
    return (AETHER_FONT_DIR or "Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-") .. weight .. ".ttf"
end

local W = {}                -- the module, for /skins and tests
AetherSkins_Windows = W
W.skinned = setmetatable({}, { __mode = "k" })   -- window -> true
W.done    = setmetatable({}, { __mode = "k" })   -- any styled widget -> kind
W.names   = {}                                   -- window names, for /skins debug
W.ours    = setmetatable({}, { __mode = "k" })   -- textures we made (left out of /skins tree)
local pending = setmetatable({}, { __mode = "k" })

local function Enabled()
    return not (AetherSkinsDB and AetherSkinsDB.windows == false)
end
W.Enabled = Enabled

local function Forbidden(f)
    return not f or (f.IsForbidden and f:IsForbidden())
end

-- A widget or texture stored under a key (Blizzard parentKeys), else nil.
local function T(o, k)
    local v = o and o[k]
    return type(v) == "table" and v or nil
end

local function Fade(r)
    if type(r) == "table" and r.SetAlpha and not Forbidden(r) then r:SetAlpha(0) end
end

local function Tex(owner, layer, sub, file, c)
    local t = owner:CreateTexture(nil, layer, nil, sub)
    if W.ours then W.ours[t] = true end
    t:SetTexture(file)
    t:SetVertexColor(c[1], c[2], c[3], c[4] or 1)
    if t.SetSnapToPixelGrid then t:SetSnapToPixelGrid(false); t:SetTexelSnappingBias(0) end
    return t
end

-- 1-pixel edge on all four sides of owner, inset px in.
local function Edge(owner, layer, sub, c, inset)
    inset = inset or 0
    local parts = {}
    for _, side in ipairs({ "TOP", "BOTTOM", "LEFT", "RIGHT" }) do
        local t = Tex(owner, layer, sub, WHITE, c)
        if side == "TOP" or side == "BOTTOM" then
            local dy = side == "TOP" and -inset or inset
            t:SetPoint(side .. "LEFT", owner, side .. "LEFT", inset, dy)
            t:SetPoint(side .. "RIGHT", owner, side .. "RIGHT", -inset, dy)
            t:SetHeight(1)
        else
            local dx = side == "LEFT" and inset or -inset
            t:SetPoint("TOP" .. side, owner, "TOP" .. side, dx, -inset)
            t:SetPoint("BOTTOM" .. side, owner, "BOTTOM" .. side, dx, inset)
            t:SetWidth(1)
        end
        parts[#parts + 1] = t
    end
    return parts
end

-- ------------------------------------------
-- Fonts: white buttons, gray disabled, gold window titles (Fira Sans).
-- ------------------------------------------
local fonts
local function Fonts()
    if fonts then return fonts end
    local function Make(name, weight, size, c)
        local f = _G[name] or CreateFont(name)
        f:SetFont(FontFile(weight), size, "")
        f:SetTextColor(c[1], c[2], c[3])
        f:SetShadowColor(0, 0, 0, 0.8); f:SetShadowOffset(1, -1)
        return f
    end
    fonts = {
        button  = Make("AetherSkinsFontButton", "SemiBold", 12, TEXT),
        disable = Make("AetherSkinsFontDisable", "SemiBold", 12, { 0.5, 0.52, 0.56 }),
        title   = Make("AetherSkinsFontTitle", "SemiBold", 12, GOLD),
    }
    return fonts
end

-- Blizzard's yellow text -> Aether gold, on every font object that is
-- Blizzard's yellow (1, 0.82, 0). Font objects only: no secure tables touched.
function W.GoldText()
    if W.goldDone then return W.goldDone end
    local n = 0
    for name, v in pairs(_G) do
        if type(name) == "string" and name:find("Font") and type(v) == "table" and type(v.GetObjectType) == "function" then
            local ok, kind = pcall(v.GetObjectType, v)
            if ok and kind == "Font" and not name:find("^Aether") then
                local ok2, r, g, b = pcall(v.GetTextColor, v)
                if ok2 and r and math.abs(r - 1) < 0.02 and math.abs(g - 0.82) < 0.02 and b < 0.05 then
                    v:SetTextColor(GOLD[1], GOLD[2], GOLD[3]); n = n + 1
                end
            end
        end
    end
    W.goldDone = n
    return n
end

-- ------------------------------------------
-- The window frame
-- ------------------------------------------
local R, IN, GLOW, TITLE_H = 8, 3, 6.7, 22
local FLIP = { TOPLEFT = { 0, 1, 0, 1 }, TOPRIGHT = { 1, 0, 0, 1 }, BOTTOMLEFT = { 0, 1, 1, 0 }, BOTTOMRIGHT = { 1, 0, 1, 0 } }
local CORNERS = { "TOPLEFT", "TOPRIGHT", "BOTTOMLEFT", "BOTTOMRIGHT" }

local function Shape(f, layer, sub, file, color, inset, line)
    for _, c in ipairs(CORNERS) do
        local t = Tex(f, layer, sub, MEDIA .. file, color)
        local fl = FLIP[c]
        t:SetTexCoord(fl[1], fl[2], fl[3], fl[4]); t:SetSize(R, R); t:SetPoint(c, f, c, 0, 0)
    end
    if line then
        local t = Tex(f, layer, sub, WHITE, color)
        t:SetPoint("TOPLEFT", f, "TOPLEFT", R, -inset); t:SetPoint("TOPRIGHT", f, "TOPRIGHT", -R, -inset); t:SetHeight(line)
        t = Tex(f, layer, sub, WHITE, color)
        t:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", R, inset); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -R, inset); t:SetHeight(line)
        t = Tex(f, layer, sub, WHITE, color)
        t:SetPoint("TOPLEFT", f, "TOPLEFT", inset, -R); t:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", inset, R); t:SetWidth(line)
        t = Tex(f, layer, sub, WHITE, color)
        t:SetPoint("TOPRIGHT", f, "TOPRIGHT", -inset, -R); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -inset, R); t:SetWidth(line)
    else
        local t = Tex(f, layer, sub, WHITE, color)
        t:SetPoint("TOPLEFT", f, "TOPLEFT", R, 0); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -R, 0)
        t = Tex(f, layer, sub, WHITE, color)
        t:SetPoint("TOPLEFT", f, "TOPLEFT", 0, -R); t:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", 0, R); t:SetWidth(R)
        t = Tex(f, layer, sub, WHITE, color)
        t:SetPoint("TOPRIGHT", f, "TOPRIGHT", 0, -R); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", 0, R); t:SetWidth(R)
    end
end

local function Frame(f)
    Shape(f, "BACKGROUND", -7, "win_round_fill", PANEL, 0, nil)
    Shape(f, "BORDER", 3, "win_round_line", { BLUE[1], BLUE[2], BLUE[3], 1 }, 0, 1)
    Shape(f, "BORDER", 1, "win_round_inner", { BLUE[1], BLUE[2], BLUE[3], 0.3 }, IN, 1)
    -- soft blue glow outside
    local G = { BLUE[1], BLUE[2], BLUE[3], 0.42 }
    local function Glow(file, l, r, t, b)
        local g = Tex(f, "BACKGROUND", -8, MEDIA .. file, G); g:SetTexCoord(l, r, t, b); return g
    end
    local t = Glow("win_glow_v", 0, 1, 1, 0)
    t:SetPoint("BOTTOMLEFT", f, "TOPLEFT", R, 0); t:SetPoint("BOTTOMRIGHT", f, "TOPRIGHT", -R, 0); t:SetHeight(GLOW)
    t = Glow("win_glow_v", 0, 1, 0, 1)
    t:SetPoint("TOPLEFT", f, "BOTTOMLEFT", R, 0); t:SetPoint("TOPRIGHT", f, "BOTTOMRIGHT", -R, 0); t:SetHeight(GLOW)
    t = Glow("win_glow_h", 1, 0, 0, 1)
    t:SetPoint("TOPRIGHT", f, "TOPLEFT", 0, -R); t:SetPoint("BOTTOMRIGHT", f, "BOTTOMLEFT", 0, R); t:SetWidth(GLOW)
    t = Glow("win_glow_h", 0, 1, 0, 1)
    t:SetPoint("TOPLEFT", f, "TOPRIGHT", 0, -R); t:SetPoint("BOTTOMLEFT", f, "BOTTOMRIGHT", 0, R); t:SetWidth(GLOW)
    for _, c in ipairs(CORNERS) do
        local fl = FLIP[c]
        t = Glow("win_rglow_c", fl[1], fl[2], fl[3], fl[4])
        t:SetSize(GLOW + R, GLOW + R)
        t:SetPoint(c, f, c, c:find("LEFT") and -GLOW or GLOW, c:find("TOP") and GLOW or -GLOW)
    end
    -- navy title strip, rounded at the top, gold underline
    local S = IN + 1
    for _, c in ipairs({ "TOPLEFT", "TOPRIGHT" }) do
        local fl = FLIP[c]
        t = Tex(f, "BORDER", 0, MEDIA .. "win_round_strip", NAVY)
        t:SetTexCoord(fl[1], fl[2], fl[3], fl[4]); t:SetSize(R, R); t:SetPoint(c, f, c, 0, 0)
    end
    t = Tex(f, "BORDER", 0, WHITE, NAVY)
    t:SetPoint("TOPLEFT", f, "TOPLEFT", R, -S); t:SetPoint("TOPRIGHT", f, "TOPRIGHT", -R, -S); t:SetHeight(R - S)
    t = Tex(f, "BORDER", 0, WHITE, NAVY)
    t:SetPoint("TOPLEFT", f, "TOPLEFT", S, -R); t:SetPoint("TOPRIGHT", f, "TOPRIGHT", -S, -R); t:SetHeight(TITLE_H - R)
    t = Tex(f, "BORDER", 2, WHITE, { GOLD[1], GOLD[2], GOLD[3], 0.7 })
    t:SetPoint("TOPLEFT", f, "TOPLEFT", S, -TITLE_H); t:SetPoint("TOPRIGHT", f, "TOPRIGHT", -S, -TITLE_H); t:SetHeight(1)
    -- the four 3D gold chevrons (gold baked per direction; dark backing turns)
    for _, c in ipairs({ { "up", "TOP", 0, 3, 0, 26 }, { "down", "BOTTOM", 0, -3, math.pi, 26 },
                         { "left", "LEFT", -3, 0, math.pi / 2, 34 }, { "right", "RIGHT", 3, 0, -math.pi / 2, 34 } }) do
        local dark = Tex(f, "OVERLAY", 6, MEDIA .. "win_chev_dark", { 0.04, 0.05, 0.07, 1 })
        dark:SetSize(c[6], c[6]); dark:SetPoint("CENTER", f, c[2], c[3], c[4])
        if c[5] ~= 0 and dark.SetRotation then dark:SetRotation(c[5]) end
        local gold = Tex(f, "OVERLAY", 7, MEDIA .. "chev3d_" .. c[1], { 1, 1, 1, 1 })
        gold:SetSize(c[6], c[6]); gold:SetPoint("CENTER", f, c[2], c[3], c[4])
    end
end

-- Portrait crest: plain navy disc with a blue rim behind Blizzard's portrait.
local function Crest(f)
    local pc = T(f, "PortraitContainer")
    local p = pc and T(pc, "portrait") or T(f, "portrait")
    if not p or Forbidden(pc) then return end
    local owner = pc or f
    local disc = Tex(owner, "BORDER", 0, MEDIA .. "btn_disc", { 1, 1, 1, 1 })
    disc:SetSize(66, 66)
    disc:SetPoint("CENTER", p, "CENTER", 0, 0)
end

-- Close button: navy square, blue edge, white x. Blizzard's art fades out.
local function Close(b)
    if not b or W.done[b] or Forbidden(b) then return end
    W.done[b] = "close"
    for _, get in ipairs({ "GetNormalTexture", "GetPushedTexture", "GetHighlightTexture", "GetDisabledTexture" }) do
        if b[get] then Fade(b[get](b)) end
    end
    local box = Tex(b, "BACKGROUND", 1, WHITE, NAVY)
    box:SetSize(20, 20); box:SetPoint("CENTER", b, "CENTER", 0, 0)
    local c = { BLUE[1], BLUE[2], BLUE[3], 1 }
    local top = Tex(b, "BORDER", 2, WHITE, c); top:SetPoint("TOPLEFT", box); top:SetPoint("TOPRIGHT", box); top:SetHeight(1)
    local bot = Tex(b, "BORDER", 2, WHITE, c); bot:SetPoint("BOTTOMLEFT", box); bot:SetPoint("BOTTOMRIGHT", box); bot:SetHeight(1)
    local lft = Tex(b, "BORDER", 2, WHITE, c); lft:SetPoint("TOPLEFT", box); lft:SetPoint("BOTTOMLEFT", box); lft:SetWidth(1)
    local rgt = Tex(b, "BORDER", 2, WHITE, c); rgt:SetPoint("TOPRIGHT", box); rgt:SetPoint("BOTTOMRIGHT", box); rgt:SetWidth(1)
    for _, rot in ipairs({ math.pi / 4, -math.pi / 4 }) do
        local x = Tex(b, "ARTWORK", 1, WHITE, TEXT)
        x:SetSize(2, 12); x:SetPoint("CENTER", box, "CENTER", 0, 0)
        if x.SetRotation then x:SetRotation(rot) end
    end
    local hl = Tex(b, "HIGHLIGHT", 0, WHITE, { BLUE[1], BLUE[2], BLUE[3], 0.3 })
    hl:SetAllPoints(box); hl:SetBlendMode("ADD")
end

-- ------------------------------------------
-- Widgets inside a window
-- ------------------------------------------
local function NavyBox(owner, l, r, t, b)   -- navy fill + blue edge on owner, inset by l/r/t/b
    local fill = Tex(owner, "BACKGROUND", 1, WHITE, { NAVY[1], NAVY[2], NAVY[3], 0.95 })
    fill:SetPoint("TOPLEFT", owner, "TOPLEFT", l, -t); fill:SetPoint("BOTTOMRIGHT", owner, "BOTTOMRIGHT", -r, b)
    local c = { BLUE[1], BLUE[2], BLUE[3], 0.9 }
    local e = {}
    e[1] = Tex(owner, "BORDER", 1, WHITE, c); e[1]:SetPoint("TOPLEFT", fill); e[1]:SetPoint("TOPRIGHT", fill); e[1]:SetHeight(1)
    e[2] = Tex(owner, "BORDER", 1, WHITE, c); e[2]:SetPoint("BOTTOMLEFT", fill); e[2]:SetPoint("BOTTOMRIGHT", fill); e[2]:SetHeight(1)
    e[3] = Tex(owner, "BORDER", 1, WHITE, c); e[3]:SetPoint("TOPLEFT", fill); e[3]:SetPoint("BOTTOMLEFT", fill); e[3]:SetWidth(1)
    e[4] = Tex(owner, "BORDER", 1, WHITE, c); e[4]:SetPoint("TOPRIGHT", fill); e[4]:SetPoint("BOTTOMRIGHT", fill); e[4]:SetWidth(1)
    return fill, e
end

-- Red/gold panel buttons (Left/Middle/Right art) -> navy, blue edge, white text.
local function Button(b)
    W.done[b] = "button"
    Fade(T(b, "Left")); Fade(T(b, "Middle")); Fade(T(b, "Right")); Fade(T(b, "Center"))
    if b.GetHighlightTexture then Fade(b:GetHighlightTexture()) end
    NavyBox(b, 1, 1, 1, 1)
    local hl = Tex(b, "HIGHLIGHT", 0, WHITE, { BLUE[1], BLUE[2], BLUE[3], 0.3 })
    hl:SetPoint("TOPLEFT", b, "TOPLEFT", 1, -1); hl:SetPoint("BOTTOMRIGHT", b, "BOTTOMRIGHT", -1, 1); hl:SetBlendMode("ADD")
    local F = Fonts()
    if b.SetNormalFontObject then
        b:SetNormalFontObject(F.button); b:SetHighlightFontObject(F.button); b:SetDisabledFontObject(F.disable)
    end
end

-- Checkboxes -> dark box, blue edge, gold check.
local function Check(b)
    W.done[b] = "check"
    local n = b.GetNormalTexture and b:GetNormalTexture()
    Fade(n)
    if b.GetPushedTexture then Fade(b:GetPushedTexture()) end
    if b.GetHighlightTexture then Fade(b:GetHighlightTexture()) end
    local w = math.min(b:GetWidth() or 0, b:GetHeight() or 0)
    local inset = w > 20 and math.floor((w - 18) / 2) or 3
    local fill = Tex(b, "BACKGROUND", 1, WHITE, { 0.03, 0.047, 0.086, 1 })
    fill:SetPoint("TOPLEFT", b, "TOPLEFT", inset, -inset); fill:SetPoint("BOTTOMRIGHT", b, "BOTTOMRIGHT", -inset, inset)
    local c = { BLUE[1], BLUE[2], BLUE[3], 1 }
    for _, s in ipairs({ { "TOPLEFT", "TOPRIGHT", "H" }, { "BOTTOMLEFT", "BOTTOMRIGHT", "H" },
                         { "TOPLEFT", "BOTTOMLEFT", "V" }, { "TOPRIGHT", "BOTTOMRIGHT", "V" } }) do
        local e = Tex(b, "BORDER", 1, WHITE, c); e:SetPoint(s[1], fill); e:SetPoint(s[2], fill)
        if s[3] == "H" then e:SetHeight(1) else e:SetWidth(1) end
    end
    local ck = b.GetCheckedTexture and b:GetCheckedTexture()
    if ck then ck:SetDesaturated(true); ck:SetVertexColor(GOLD[1], GOLD[2], GOLD[3]) end
    local dk = b.GetDisabledCheckedTexture and b:GetDisabledCheckedTexture()
    if dk then dk:SetDesaturated(true); dk:SetVertexColor(0.5, 0.5, 0.5) end
    local hl = Tex(b, "HIGHLIGHT", 0, WHITE, { BLUE[1], BLUE[2], BLUE[3], 0.25 })
    hl:SetAllPoints(fill); hl:SetBlendMode("ADD")
end

-- Blizzard's minimal scroll bar -> faint blue track, blue thumb, white arrows.
local function Scroll(s)
    W.done[s] = "scroll"
    local function Tint(t, c, a)
        if type(t) == "table" and t.SetVertexColor and not Forbidden(t) then
            if t.SetDesaturated then t:SetDesaturated(true) end
            t:SetVertexColor(c[1], c[2], c[3], a or 1)
        end
    end
    local tr = T(s, "Track")
    local th = (tr and T(tr, "Thumb")) or T(s, "Thumb")
    if tr then Tint(T(tr, "Begin"), BLUE, 0.35); Tint(T(tr, "Middle"), BLUE, 0.35); Tint(T(tr, "End"), BLUE, 0.35) end
    if th then Tint(T(th, "Begin"), BLUE); Tint(T(th, "Middle"), BLUE); Tint(T(th, "End"), BLUE) end
    for _, k in ipairs({ "Back", "Forward" }) do
        local a = T(s, k)
        if a then Tint(T(a, "Texture") or (a.GetNormalTexture and a:GetNormalTexture()), TEXT) end
    end
end

-- Bottom tabs (PanelTabButtonTemplate) -> navy, blue edge; gold edge when selected.
local tabEdges = setmetatable({}, { __mode = "k" })
local function TabColor(tab)
    local e = tabEdges[tab]; if not e then return end
    local la = T(tab, "LeftActive")
    local sel = la and la:IsShown()
    local c = sel and GOLD or BLUE
    for _, t in ipairs(e) do t:SetVertexColor(c[1], c[2], c[3], sel and 1 or 0.9) end
end
W.TabColor = TabColor
local function Tab(tab)
    W.done[tab] = "tab"
    for _, k in ipairs({ "Left", "Middle", "Right", "LeftActive", "MiddleActive", "RightActive",
                         "LeftHighlight", "MiddleHighlight", "RightHighlight" }) do
        local t = T(tab, k)
        if t and t.GetAlpha then
            -- Active pieces stay as Blizzard shows/hides them (we read that for
            -- the gold edge) but turn invisible.
            Fade(t)
        end
    end
    -- The box is centered on the tab's text, not stretched over the whole
    -- button: Blizzard's tab buttons are taller than their art, and the text
    -- sits where the art was, so a full-height box left it low (user, Nov 25,
    -- Talents' Primary / Secondary).
    local fill, e = NavyBox(tab, 4, 4, 2, 4)
    local text = T(tab, "Text") or (tab.GetFontString and tab:GetFontString())
    if type(text) == "table" and text.GetObjectType then
        fill:ClearAllPoints()
        fill:SetPoint("LEFT", tab, "LEFT", 4, 0)
        fill:SetPoint("RIGHT", tab, "RIGHT", -4, 0)
        fill:SetPoint("TOP", text, "TOP", 0, 7)
        fill:SetPoint("BOTTOM", text, "BOTTOM", 0, -7)
    end
    tabEdges[tab] = e
    TabColor(tab)
end

-- Search and input boxes (Left/Middle/Right art on an EditBox) -> dark, blue edge.
local function Input(eb)
    W.done[eb] = "input"
    Fade(T(eb, "Left")); Fade(T(eb, "Middle")); Fade(T(eb, "Right"))
    local fill = Tex(eb, "BACKGROUND", 1, WHITE, { 0.03, 0.047, 0.086, 0.95 })
    fill:SetPoint("TOPLEFT", eb, "TOPLEFT", -4, 0); fill:SetPoint("BOTTOMRIGHT", eb, "BOTTOMRIGHT", 0, 0)
    local c = { BLUE[1], BLUE[2], BLUE[3], 0.8 }
    for _, s in ipairs({ { "TOPLEFT", "TOPRIGHT", "H" }, { "BOTTOMLEFT", "BOTTOMRIGHT", "H" },
                         { "TOPLEFT", "BOTTOMLEFT", "V" }, { "TOPRIGHT", "BOTTOMRIGHT", "V" } }) do
        local e = Tex(eb, "BORDER", 1, WHITE, c); e:SetPoint(s[1], fill); e:SetPoint(s[2], fill)
        if s[3] == "H" then e:SetHeight(1) else e:SetWidth(1) end
    end
end

-- Insets (InsetFrameTemplate) -> a faint dark panel with a fine blue line.
local function Inset(f)
    W.done[f] = "inset"
    Fade(T(f, "NineSlice")); Fade(T(f, "Bg"))
    local fill = Tex(f, "BACKGROUND", -6, WHITE, { 0, 0, 0, 0.25 })
    fill:SetAllPoints(f)
    Edge(f, "BORDER", -1, { BLUE[1], BLUE[2], BLUE[3], 0.22 }, 0)
end

-- What a widget is, from Blizzard's template keys.
local function Kind(o)
    local ok, t = pcall(o.GetObjectType, o)
    if not ok then return end
    if t == "CheckButton" then
        local n = o.GetNormalTexture and o:GetNormalTexture()
        if n and o.GetCheckedTexture and o:GetCheckedTexture() then return "check" end
    elseif t == "Button" then
        if T(o, "LeftActive") and T(o, "MiddleActive") then return "tab" end
        if T(o, "Left") and T(o, "Right") and (T(o, "Middle") or T(o, "Center")) and o.GetFontString and o:GetFontString() then return "button" end
    elseif t == "EditBox" then
        if T(o, "Left") and T(o, "Right") and T(o, "Middle") then return "input" end
    end
    local tr = T(o, "Track")
    if (tr and T(tr, "Thumb")) or (T(o, "Thumb") and T(o, "Back") and T(o, "Forward")) then return "scroll" end
    if T(o, "NineSlice") and o.layoutType == "InsetFrameTemplate" then return "inset" end
end
W.Kind = Kind

local STYLE = { check = Check, tab = Tab, button = Button, input = Input, scroll = Scroll, inset = Inset }

-- Style everything inside a window (depth-first, capped).
function W.Contents(root)
    local seen, count = 0, 0
    local function Walk(f, depth)
        if depth > 10 or seen > 4000 then return end
        local kids = { f:GetChildren() }
        for i = 1, #kids do
            local k = kids[i]
            seen = seen + 1
            if not Forbidden(k) then
                if not W.done[k] then
                    local kind = Kind(k)
                    if kind and STYLE[kind] then
                        local ok = pcall(STYLE[kind], k)
                        if ok then count = count + 1 else W.done[k] = "failed" end
                    end
                end
                if W.done[k] ~= "close" then Walk(k, depth + 1) end
            end
        end
    end
    Walk(root, 0)
    return count
end

-- ------------------------------------------
-- Which frames are windows we skin
-- ------------------------------------------
function W.IsWindow(f)
    if Forbidden(f) or type(f) ~= "table" or not f.GetObjectType then return false end
    if f.aetherTrim then return false end                    -- one of our own Aether windows
    return (T(f, "NineSlice") and (T(f, "TitleContainer") or T(f, "PortraitContainer"))) and true or false
end

function W.Skin(f)
    if not Enabled() or not W.IsWindow(f) then return false end
    if InCombatLockdown and InCombatLockdown() then pending[f] = true; return false end
    if not W.skinned[f] then
        W.skinned[f] = true
        Fade(T(f, "NineSlice")); Fade(T(f, "Bg")); Fade(T(f, "TopTileStreaks"))
        Fade(T(f, "Background"))
        Frame(f)
        Crest(f)
        local title = (T(f, "TitleContainer") and T(f.TitleContainer, "TitleText")) or T(f, "TitleText")
        if title and title.SetFontObject then title:SetFontObject(Fonts().title) end
        Close(T(f, "CloseButton"))
        if T(f, "Inset") and not W.done[f.Inset] then pcall(Inset, f.Inset) end
        local name = f.GetName and f:GetName() or (f.GetDebugName and f:GetDebugName()) or "?"
        W.names[#W.names + 1] = name
        -- content that appears later (tabs switched, lists filled) gets styled on each show
        if f.HookScript then f:HookScript("OnShow", function(self) if Enabled() then W.Contents(self) end end) end
    end
    W.Contents(f)
    return true
end

-- Blizzard windows by name (some load later, with their Blizzard_ addon).
W.KNOWN = {
    "CharacterFrame", "FriendsFrame", "SocialUIFrame", "PVEFrame", "PlayerSpellsFrame", "SpellBookFrame", "PlayerTalentFrame",
    "ProfessionsFrame", "CollectionsJournal", "EncounterJournal", "AchievementFrame", "CommunitiesFrame",
    "GuildFrame", "MerchantFrame", "GossipFrame", "QuestFrame", "MailFrame", "OpenMailFrame", "TradeFrame",
    "BankFrame", "AuctionHouseFrame", "ClassTrainerFrame", "TaxiFrame", "DressUpFrame", "ItemTextFrame",
    "PetStableFrame", "InspectFrame", "ChannelFrame", "MacroFrame", "KeyBindingFrame", "WardrobeFrame",
    "ItemSocketingFrame", "TradeSkillFrame", "LootFrame", "GuildBankFrame", "QuestLogPopupDetailFrame",
    "WorldMapFrame", "CalendarFrame", "TimeManagerFrame", "HelpFrame", "PlayerChoiceFrame",
}

local hooked = setmetatable({}, { __mode = "k" })
function W.Watch(f)
    if not f or hooked[f] or not W.IsWindow(f) then return end
    hooked[f] = true
    f:HookScript("OnShow", function(self) W.Skin(self) end)
    if f:IsShown() then W.Skin(f) end
end

function W.ScanKnown()
    for _, n in ipairs(W.KNOWN) do
        local f = _G[n]
        if f then pcall(W.Watch, f) end
    end
end

function W.Init()
    if not Enabled() or W.started then return end
    W.started = true
    Fonts()
    pcall(W.GoldText)
    W.ScanKnown()
    -- any other standard window, when Blizzard opens it as a panel
    if hooksecurefunc then
        if ShowUIPanel then hooksecurefunc("ShowUIPanel", function(f) if f then pcall(W.Watch, f) end end) end
        if PanelTemplates_SelectTab then hooksecurefunc("PanelTemplates_SelectTab", function(t) TabColor(t) end) end
        if PanelTemplates_DeselectTab then hooksecurefunc("PanelTemplates_DeselectTab", function(t) TabColor(t) end) end
        if PanelTemplates_UpdateTabs then
            hooksecurefunc("PanelTemplates_UpdateTabs", function(frame)
                if frame and frame.Tabs then for _, t in ipairs(frame.Tabs) do TabColor(t) end end
            end)
        end
    end
end

-- The window under the mouse (or its window), for /skins this.
function W.SkinUnderMouse()
    local foci = GetMouseFoci and GetMouseFoci() or { GetMouseFocus and GetMouseFocus() }
    local f = foci and foci[1]
    while f and not W.IsWindow(f) do f = f.GetParent and f:GetParent() end
    if f then W.Watch(f); W.Skin(f); return f end
end

-- /skins tree: the structure of the window under the mouse, so the second
-- pass can style Forever's own parts by name (they aren't Blizzard's
-- standard templates). Saved in AetherSkinsDB.lastTree for the Hub's Debug
-- page to show in its copy box. Names only: no text that could be secret.
local function KeyIn(parent, child)
    if type(parent) ~= "table" then return nil end
    local ok, key = pcall(function()
        for k, v in pairs(parent) do if v == child and type(k) == "string" then return k end end
    end)
    return ok and key or nil
end
local function Describe(o, parent)
    local ok, kind = pcall(o.GetObjectType, o)
    kind = ok and kind or "?"
    local name = (o.GetName and o:GetName()) or nil
    local key = KeyIn(parent, o)
    local bits = { kind, name or ("." .. (key or "?")) }
    if o.GetWidth then
        local okw, w, h = pcall(function() return o:GetWidth(), o:GetHeight() end)
        if okw and w and not (issecretvalue and (issecretvalue(w) or issecretvalue(h))) then
            bits[#bits + 1] = string.format("%dx%d", math.floor(w + 0.5), math.floor(h + 0.5))
        end
    end
    if o.IsShown and not o:IsShown() then bits[#bits + 1] = "hidden" end
    if kind == "Texture" then
        local a = o.GetAtlas and o:GetAtlas()
        local t = o.GetTexture and o:GetTexture()
        if a and not (issecretvalue and issecretvalue(a)) then bits[#bits + 1] = "atlas=" .. tostring(a)
        elseif t and not (issecretvalue and issecretvalue(t)) then bits[#bits + 1] = "tex=" .. tostring(t) end
    end
    if W.done[o] then bits[#bits + 1] = "[styled " .. W.done[o] .. "]" end
    return table.concat(bits, " ")
end
local MAX_LINES = 1500
function W.Tree(root)
    local lines, count = {}, 0
    local function Walk(f, parent, depth)
        if count >= MAX_LINES or Forbidden(f) then return end
        count = count + 1
        local line = string.rep("  ", depth) .. Describe(f, parent)
        -- A hidden part (another tab's page, gamepad hints): one line, not its insides.
        if f.IsShown and not f:IsShown() and depth > 0 then
            local n = f.GetNumChildren and f:GetNumChildren() or 0
            local r = f.GetNumRegions and f:GetNumRegions() or 0
            lines[#lines + 1] = line .. string.format(" (%d parts inside, skipped)", n + r)
            return
        end
        lines[#lines + 1] = line
        if depth >= 7 then return end
        if f.GetRegions then
            for _, r in ipairs({ f:GetRegions() }) do
                if count >= MAX_LINES then break end
                if not Forbidden(r) and not W.ours[r] then
                    count = count + 1
                    lines[#lines + 1] = string.rep("  ", depth + 1) .. Describe(r, f)
                end
            end
        end
        if f.GetChildren then
            for _, c in ipairs({ f:GetChildren() }) do Walk(c, f, depth + 1) end
        end
    end
    Walk(root, root.GetParent and root:GetParent(), 0)
    if count >= MAX_LINES then lines[#lines + 1] = "(stopped at " .. MAX_LINES .. " lines)" end
    return lines
end
function W.TreeUnderMouse()
    local foci = GetMouseFoci and GetMouseFoci() or { GetMouseFocus and GetMouseFocus() }
    local f = foci and foci[1]
    local top = f
    while f do
        if W.IsWindow(f) then top = f; break end
        f = f.GetParent and f:GetParent()
        if f == UIParent then break end
    end
    if not top or top == UIParent then return nil end
    local name = (top.GetName and top:GetName()) or "window"
    AetherSkinsDB = AetherSkinsDB or {}
    AetherSkinsDB.lastTree = { name = name, lines = W.Tree(top) }
    return name, #AetherSkinsDB.lastTree.lines
end

function W.Debug(print)
    print(("Windows: %s; %d skinned; Blizzard yellow text turned gold on %d fonts.")
        :format(Enabled() and "on" or "off", #W.names, W.goldDone or 0))
    if #W.names > 0 then print("  " .. table.concat(W.names, ", ")) end
    local kinds = {}
    for _, k in pairs(W.done) do kinds[k] = (kinds[k] or 0) + 1 end
    local out = {}
    for k, n in pairs(kinds) do out[#out + 1] = k .. " " .. n end
    table.sort(out)
    if #out > 0 then print("  Styled inside: " .. table.concat(out, ", ")) end
end

local ev = CreateFrame("Frame")
ev:RegisterEvent("PLAYER_LOGIN")
ev:RegisterEvent("ADDON_LOADED")
ev:RegisterEvent("PLAYER_REGEN_ENABLED")
ev:SetScript("OnEvent", function(_, event, arg)
    if event == "PLAYER_LOGIN" then
        W.Init()
    elseif event == "ADDON_LOADED" then
        if W.started and type(arg) == "string" and arg:find("^Blizzard_") then W.ScanKnown() end
    elseif event == "PLAYER_REGEN_ENABLED" then
        for f in pairs(pending) do pending[f] = nil; W.Skin(f) end
    end
end)
