-- AetherChat: Blizzard's chat window with the Aether look, sized to fit the
-- space beside your action bars. Only changes how chat looks and where it
-- sits; chat itself (channels, tabs, settings) is still Blizzard's.

local ADDON = ...
local PREFIX = "|cff4da6ffAetherChat:|r "
local function Print(msg) print(PREFIX .. msg) end

local defaults = {
    fit         = true,   -- fill the space between the screen's left edge and your bars
    fontSize    = nil,    -- set on first run: one step smaller than Blizzard's size
    trim        = true,   -- Aether panel behind the chat
    hideButtons = true,   -- hide the voice, channel and emote buttons beside chat
    slimEdit    = true,   -- slim typing line that shows only while you type
}

local db
local GAP = 4        -- space between the chat panel and the bar panels (same as between bars)
local MARGIN = 6     -- space from the screen's left edge
local TAB_H = 26     -- room above the chat text for the tabs
local INSET = 8      -- room inside the panel around the text

-- ==========================================
-- HELPERS
-- ==========================================
local hiddenHooked = {}
-- Hide a texture or frame, and keep it hidden if Blizzard shows it again.
local function Bury(obj)
    if type(obj) ~= "table" or not obj.Hide or (obj.IsForbidden and obj:IsForbidden()) then return end
    obj:Hide()
    if not hiddenHooked[obj] then
        hiddenHooked[obj] = true
        hooksecurefunc(obj, "Show", function(self)
            if hiddenHooked[self] == true then self:Hide() end
        end)
    end
    hiddenHooked[obj] = true
end
local function Unbury(obj)
    if type(obj) == "table" and hiddenHooked[obj] then hiddenHooked[obj] = "off"; obj:Show() end
end

-- Same see-through level as AetherMeter's window out of combat (else 20%).
local function PanelAlpha()
    local m = _G.AetherMeterDB
    local a = type(m) == "table" and tonumber(m.opacityOutCombat)
    return a and math.max(0, math.min(1, a)) or 0.2
end

local function Chat() return _G.ChatFrame1 end

local function ChatFrames()
    local list = {}
    for i = 1, (NUM_CHAT_WINDOWS or 10) do
        local cf = _G["ChatFrame" .. i]
        if cf then list[#list + 1] = cf end
    end
    return list
end

-- ==========================================
-- AETHER PANEL
-- ==========================================
-- The same frame as the action bars: AetherMeter's window color, blue frame,
-- soft glow and gold corners, all faded to the meter's out-of-combat level.
local panel
local function MakePanel()
    local p = CreateFrame("Frame", "AetherChatPanel", UIParent)
    p:SetFrameStrata("BACKGROUND")
    p:SetFrameLevel(1)
    p.soft = {}
    local function Rect(layer, sub, r, g, b, base)
        local t = p:CreateTexture(nil, layer, nil, sub)
        t:SetColorTexture(r, g, b, base)
        p.soft[#p.soft + 1] = { t, r, g, b, base }
        return t
    end
    Rect("BACKGROUND", 0, 0.05, 0.05, 0.05, 1):SetAllPoints()
    for _, spec in ipairs({ { 0, 1, 1 }, { -3, 3, 0.12 }, { 3, 1, 0.3 } }) do
        local inset, w, a = spec[1], spec[2], spec[3]
        local top = Rect("BORDER", 0, 0.3, 0.7, 1, a)
        top:SetPoint("TOPLEFT", inset, -inset); top:SetPoint("TOPRIGHT", -inset, -inset); top:SetHeight(w)
        local bottom = Rect("BORDER", 0, 0.3, 0.7, 1, a)
        bottom:SetPoint("BOTTOMLEFT", inset, inset); bottom:SetPoint("BOTTOMRIGHT", -inset, inset); bottom:SetHeight(w)
        local left = Rect("BORDER", 0, 0.3, 0.7, 1, a)
        left:SetPoint("TOPLEFT", inset, -inset); left:SetPoint("BOTTOMLEFT", inset, inset); left:SetWidth(w)
        local right = Rect("BORDER", 0, 0.3, 0.7, 1, a)
        right:SetPoint("TOPRIGHT", -inset, -inset); right:SetPoint("BOTTOMRIGHT", -inset, inset); right:SetWidth(w)
    end
    -- gold corners: thick on the border, with a fine echo just inside
    for _, corner in ipairs({ "TOPLEFT", "TOPRIGHT", "BOTTOMLEFT", "BOTTOMRIGHT" }) do
        local ix = corner:find("LEFT") and 1 or -1
        local iy = corner:find("TOP") and -1 or 1
        local across = Rect("OVERLAY", 6, 1, 0.69, 0, 1)
        across:SetSize(10, 2); across:SetPoint(corner, p, corner, 0, 0)
        local down = Rect("OVERLAY", 6, 1, 0.69, 0, 1)
        down:SetSize(2, 10); down:SetPoint(corner, p, corner, 0, 0)
        local fineA = Rect("OVERLAY", 6, 1, 0.69, 0, 0.9)
        fineA:SetSize(6, 1); fineA:SetPoint(corner, p, corner, ix * 3, iy * 3)
        local fineD = Rect("OVERLAY", 6, 1, 0.69, 0, 0.9)
        fineD:SetSize(1, 6); fineD:SetPoint(corner, p, corner, ix * 3, iy * 3)
    end
    -- a thin blue line under the tabs
    local line = Rect("BORDER", 1, 0.3, 0.7, 1, 0.5)
    line:SetHeight(1)
    p.tabLine = line
    p:Hide()
    return p
end

local function SoftenPanel(a)
    if not panel or panel.softAlpha == a then return end
    panel.softAlpha = a
    for _, e in ipairs(panel.soft) do e[1]:SetColorTexture(e[2], e[3], e[4], e[5] * a) end
end

-- ==========================================
-- WHERE THE CHAT GOES
-- ==========================================
-- The space between the screen's left edge and the bar panels, as tall as the
-- whole block of bars (so chat and a docked AetherMeter match on both sides).
local function FitRect()
    local panels = AetherBars_PanelRects and AetherBars_PanelRects()
    if not panels or #panels == 0 then return nil end
    local minL, top, bottom
    for _, r in ipairs(panels) do
        minL = math.min(minL or math.huge, r.L)
        top = math.max(top or -math.huge, r.T)
        bottom = math.min(bottom or math.huge, r.B)
    end
    local left, right = MARGIN, minL - GAP
    if right - left < 220 or top - bottom < 90 then return nil end   -- too small to read
    return math.floor(left + 0.5), math.floor(right + 0.5), math.floor(bottom + 0.5), math.floor(top + 0.5)
end

-- How much room the tabs need above the chat text (measured from Blizzard's
-- own layout, so tall or short tabs both fit inside the panel).
local tabRoom
local function TabRoom()
    if tabRoom then return tabRoom end
    local cf, tab = Chat(), _G.ChatFrame1Tab
    if cf and tab and cf:GetTop() and tab:GetTop() then
        local s = cf:GetEffectiveScale() / UIParent:GetEffectiveScale()
        local need = (tab:GetTop() * tab:GetEffectiveScale() / UIParent:GetEffectiveScale()) - cf:GetTop() * s
        if need > 0 and need < 60 then tabRoom = math.max(TAB_H, math.ceil(need) + 2) end
    end
    return tabRoom or TAB_H
end

local placing = false
local placed      -- the panel rect we last placed the chat in
-- Extra room to take off the left edge of the text (normally 0; /achat inset N).
local function TextInset()
    return db and tonumber(db.textInset) or 0
end

local function UI(frame, edge)   -- a frame's edge in UIParent units
    local v = frame and frame["Get" .. edge] and frame["Get" .. edge](frame)
    return v and v * frame:GetEffectiveScale() / UIParent:GetEffectiveScale()
end

local function PlaceChat(l, r, b, t)
    local cf = Chat()
    if not cf then return end
    local k = UIParent:GetEffectiveScale() / cf:GetEffectiveScale()
    local inset = TextInset()
    placing = true
    -- Blizzard keeps chat windows a good way in from the screen's edges
    -- (room for its old button column). That's what pushed the text right;
    -- inside the panel, let the chat sit where we put it.
    if cf.SetClampRectInsets then cf:SetClampRectInsets(0, 0, 0, 0) end
    cf:ClearAllPoints()
    cf:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", (l + INSET - inset) * k, (b + INSET) * k)
    cf:SetSize((r - l - INSET * 2 + inset) * k, (t - b - INSET - TabRoom()) * k)
    placing = false
end

-- Panel around the chat when it isn't fitted to the bars: wraps the text and tabs.
local function WrapRect()
    local cf = Chat()
    if not cf or not cf:GetLeft() then return nil end
    local s = cf:GetEffectiveScale() / UIParent:GetEffectiveScale()
    return cf:GetLeft() * s + TextInset() - INSET, cf:GetRight() * s + INSET, cf:GetBottom() * s - INSET, cf:GetTop() * s + TabRoom()
end

local function Layout()
    if not db then return end
    local l, r, b, t
    if db.fit then
        l, r, b, t = FitRect()
        if l and (not placed or placed[1] ~= l or placed[2] ~= r or placed[3] ~= b or placed[4] ~= t) then
            placed = { l, r, b, t }
            PlaceChat(l, r, b, t)
        elseif not l then
            placed = nil
        end
    end
    if not l then l, r, b, t = WrapRect() end
    panel = panel or MakePanel()
    if db.trim and l then
        panel:ClearAllPoints()
        panel:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", l, b)
        panel:SetSize(r - l, t - b)
        panel.tabLine:ClearAllPoints()
        panel.tabLine:SetPoint("TOPLEFT", panel, "TOPLEFT", 4, -(TabRoom() - 2))
        panel.tabLine:SetPoint("TOPRIGHT", panel, "TOPRIGHT", -4, -(TabRoom() - 2))
        panel:Show()
    else
        panel:Hide()
    end
end

-- ==========================================
-- CLEANUP: BACKGROUNDS, BUTTONS, TABS, TYPING LINE
-- ==========================================
local function StripChatArt(cf)
    local name = cf:GetName()
    for _, tex in ipairs(CHAT_FRAME_TEXTURES or {}) do Bury(_G[name .. tex]) end
    if cf.Background then Bury(cf.Background) end
    Bury(_G[name .. "ButtonFrame"] or cf.buttonFrame)
end

local BUTTONS = {
    "ChatFrameMenuButton", "ChatFrameChannelButton", "ChatFrameToggleVoiceDeafenButton",
    "ChatFrameToggleVoiceMuteButton", "QuickJoinToastButton", "TextToSpeechButton",
}
local function ApplyButtons()
    for _, n in ipairs(BUTTONS) do
        local b = _G[n]
        if b then
            if db.hideButtons then Bury(b) else Unbury(b) end
        end
    end
end

-- Flat tabs: Blizzard's tab art hidden, our dark strip behind, and a gold
-- underline under the tab you're on.
local function StyleTab(cf)
    local tab = _G[cf:GetName() .. "Tab"]
    if not tab or tab.aetherStyled then return tab end
    tab.aetherStyled = true
    for _, r in ipairs({ tab:GetRegions() }) do
        if r:IsObjectType("Texture") and r ~= tab.glow and r ~= _G[tab:GetName() .. "Glow"] then Bury(r) end
    end
    local bg = tab:CreateTexture(nil, "BACKGROUND", nil, -8)
    bg:SetPoint("TOPLEFT", 2, -6); bg:SetPoint("BOTTOMRIGHT", -2, 2)
    bg:SetColorTexture(0.05, 0.05, 0.05, 0.6)
    tab.aetherBg = bg
    local under = tab:CreateTexture(nil, "OVERLAY")
    under:SetPoint("BOTTOMLEFT", 6, 2); under:SetPoint("BOTTOMRIGHT", -6, 2)
    under:SetHeight(2)
    under:SetColorTexture(1, 0.69, 0, 1)
    under:Hide()
    tab.aetherUnder = under
    return tab
end

local function SelectedChat()
    local dock = _G.GeneralDockManager
    return (dock and dock.selected) or _G.SELECTED_CHAT_FRAME or Chat()
end

local function UpdateTabs()
    local sel = SelectedChat()
    for _, cf in ipairs(ChatFrames()) do
        local tab = StyleTab(cf)
        if tab and tab.aetherUnder then tab.aetherUnder:SetShown(cf == sel) end
    end
end

local function StyleEditBox(eb)
    if not eb or eb.aetherStyled then return end
    eb.aetherStyled = true
    for _, r in ipairs({ eb:GetRegions() }) do
        if r:IsObjectType("Texture") then Bury(r) end
    end
    local bg = eb:CreateTexture(nil, "BACKGROUND", nil, -8)
    bg:SetAllPoints()
    bg:SetColorTexture(0.05, 0.05, 0.05, 0.9)
    local line = eb:CreateTexture(nil, "BORDER")
    line:SetPoint("TOPLEFT"); line:SetPoint("TOPRIGHT"); line:SetHeight(1)
    line:SetColorTexture(0.3, 0.7, 1, 0.9)
end

-- The typing line sits over the bottom of the chat, inside the panel.
local placingEdit = false
local function PlaceEditBox(eb, cf)
    if not db.slimEdit or not eb or not cf then return end
    placingEdit = true
    eb:ClearAllPoints()
    eb:SetPoint("BOTTOMLEFT", cf, "BOTTOMLEFT", -4, -4)
    eb:SetPoint("BOTTOMRIGHT", cf, "BOTTOMRIGHT", 4, -4)
    eb:SetHeight(22)
    placingEdit = false
end

local function SetupEditBoxes()
    for _, cf in ipairs(ChatFrames()) do
        local eb = _G[cf:GetName() .. "EditBox"] or cf.editBox
        if eb and not eb.aetherHooked then
            eb.aetherHooked = true
            if db.slimEdit then StyleEditBox(eb) end
            hooksecurefunc(eb, "SetPoint", function(self)
                if not placingEdit and db.slimEdit then PlaceEditBox(self, cf) end
            end)
            PlaceEditBox(eb, cf)
            if db.slimEdit and not eb:HasFocus() then eb:Hide() end
        end
    end
end

-- ==========================================
-- FONT SIZE
-- ==========================================
local function ApplyFont()
    if not db.fontSize then return end
    for _, cf in ipairs(ChatFrames()) do
        if FCF_SetChatWindowFontSize then
            pcall(FCF_SetChatWindowFontSize, nil, cf, db.fontSize)
        else
            local font, _, flags = cf:GetFont()
            if font then cf:SetFont(font, db.fontSize, flags) end
        end
    end
end

-- ==========================================
-- SETUP AND UPDATES
-- ==========================================
local function ApplyAll()
    for _, cf in ipairs(ChatFrames()) do
        StripChatArt(cf)
        StyleTab(cf)
    end
    ApplyButtons()
    SetupEditBoxes()
    ApplyFont()
    placed = nil
    Layout()
    UpdateTabs()
end

local hooked = false
local function HookBlizzard()
    if hooked then return end
    hooked = true
    local cf = Chat()
    -- Blizzard (Edit Mode, dock updates) moves the chat now and then: put it back.
    if cf then
        hooksecurefunc(cf, "SetPoint", function()
            if not placing and db and db.fit and placed then
                -- placed can be cleared before the next frame (a loading
                -- screen re-runs the layout), so re-check it when the timer
                -- fires and skip if it's gone or changed.
                local p = placed
                C_Timer.After(0, function()
                    if placed == p and db and db.fit and not placing then
                        PlaceChat(p[1], p[2], p[3], p[4])
                    end
                end)
            end
        end)
    end
    if ChatEdit_DeactivateChat then
        hooksecurefunc("ChatEdit_DeactivateChat", function(eb)
            if db and db.slimEdit and eb and eb.aetherHooked then eb:Hide() end
        end)
    end
    if ChatEdit_ActivateChat then
        hooksecurefunc("ChatEdit_ActivateChat", function(eb)
            if db and db.slimEdit and eb then
                local owner = eb.chatFrame or Chat()
                PlaceEditBox(eb, owner)
            end
        end)
    end
    if FCF_Tab_OnClick then hooksecurefunc("FCF_Tab_OnClick", function() C_Timer.After(0, UpdateTabs) end) end
    if FCF_OpenTemporaryWindow then
        hooksecurefunc("FCF_OpenTemporaryWindow", function() C_Timer.After(0, ApplyAll) end)
    end
end

-- Solid while you're using it (mouse over the chat, its tabs, or typing).
local function InUse()
    local cf = Chat()
    if not cf then return false end
    if cf:IsMouseOver() or (panel and panel:IsShown() and panel:IsMouseOver()) then return true end
    for _, f in ipairs(ChatFrames()) do
        local eb = _G[f:GetName() .. "EditBox"]
        if eb and eb:IsShown() and eb:HasFocus() then return true end
    end
    return false
end

local tick, current, layoutTick = 0, nil, 0
local function OnUpdate(_, dt)
    if not db then return end
    tick = tick + dt
    if tick < 0.1 then return end
    local step = tick
    tick = 0
    local want = InUse() and math.max(PanelAlpha(), 0.85) or PanelAlpha()
    current = current or want
    if current ~= want then
        local speed = step / 0.25   -- quarter-second fade
        if current < want then current = math.min(want, current + speed) else current = math.max(want, current - speed) end
        SoftenPanel(current)
    elseif panel and panel.softAlpha ~= current then
        SoftenPanel(current)
    end
    -- Re-fit twice a second (cheap) so the chat follows the bars after Align.
    layoutTick = layoutTick + step
    if layoutTick >= 0.5 then
        layoutTick = 0
        Layout()
        UpdateTabs()
    end
end

-- Follow the bars the moment they move (AetherBars calls this).
AetherBars_Listeners = AetherBars_Listeners or {}
table.insert(AetherBars_Listeners, function()
    if db and hooked then placed = nil; Layout() end
end)

local f = CreateFrame("Frame")
f:RegisterEvent("ADDON_LOADED")
f:RegisterEvent("PLAYER_ENTERING_WORLD")
f:RegisterEvent("UPDATE_CHAT_WINDOWS")
f:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" and arg1 == ADDON then
        AetherChatDB = AetherChatDB or {}
        db = AetherChatDB
        for k, v in pairs(defaults) do if db[k] == nil then db[k] = v end end
    elseif event == "PLAYER_ENTERING_WORLD" then
        if not db then return end
        if not db.fontSize and Chat() then
            local _, size = Chat():GetFont()
            db.fontSize = math.max(9, math.floor((size or 14) + 0.5) - 1)
        end
        HookBlizzard()
        ApplyAll()
        C_Timer.After(2, ApplyAll)   -- after Edit Mode and the bars have settled
        f:SetScript("OnUpdate", OnUpdate)
    elseif event == "UPDATE_CHAT_WINDOWS" and db and hooked then
        C_Timer.After(0, ApplyAll)
    end
end)

-- ==========================================
-- COMMANDS
-- ==========================================
local function OnOff(v) return v and "on" or "off" end

SLASH_AETHERCHAT1, SLASH_AETHERCHAT2 = "/aetherchat", "/achat"
SlashCmdList["AETHERCHAT"] = function(input)
    if not db then return end
    local cmd, val = strsplit(" ", strlower(strtrim(input or "")), 2)
    if cmd == "fit" then
        db.fit = (val ~= "off")
        placed = nil
        Print("Fit chat beside the bars: " .. OnOff(db.fit)
            .. (db.fit and "" or " (move it in Blizzard's Edit Mode; /reload puts Blizzard's spot back)"))
        Layout()
    elseif cmd == "now" then
        placed = nil
        Layout()
        if db.fit and not FitRect() then
            Print("Not enough room beside your bars (needs about 220 wide and 90 tall), so chat stays put.")
        else
            Print("Chat fitted.")
        end
    elseif cmd == "font" and tonumber(val) then
        db.fontSize = math.max(8, math.min(24, math.floor(tonumber(val))))
        ApplyFont()
        Print("Font size " .. db.fontSize)
    elseif cmd == "trim" then
        db.trim = (val ~= "off"); Layout(); Print("Aether panel: " .. OnOff(db.trim))
    elseif cmd == "buttons" then
        db.hideButtons = (val == "off"); ApplyButtons()
        Print("Voice, channel and emote buttons: " .. (db.hideButtons and "hidden" or "shown"))
    elseif cmd == "edit" then
        db.slimEdit = (val ~= "off")
        Print("Slim typing line: " .. OnOff(db.slimEdit) .. (db.slimEdit and "" or " (type /reload to restore Blizzard's)"))
        if db.slimEdit then SetupEditBoxes() end
    elseif cmd == "inset" then
        db.textInset = tonumber(val)
        placed = nil; Layout()
        Print(db.textInset and ("Text pulled left by " .. db.textInset .. " (/achat inset to undo)") or "Text inset back to normal.")
    elseif cmd == "debug" then
        local cf, dock = Chat(), _G.GeneralDockManager
        local inner = cf and cf.FontStringContainer
        Print(string.format("chat left %.0f right %.0f, text left %s, tabs left %.0f, panel %s, inset %d",
            UI(cf, "Left") or -1, UI(cf, "Right") or -1,
            type(inner) == "table" and string.format("%.0f", UI(inner, "Left") or -1) or "?",
            UI(dock, "Left") or -1,
            placed and (placed[1] .. "-" .. placed[2]) or "not fitted", TextInset()))
    elseif cmd == "reset" then
        for k, v in pairs(defaults) do db[k] = v end
        db.fontSize = nil
        Print("Settings reset. Type /reload to apply everything.")
    else
        Print("commands:")
        print("  /achat fit on|off     fit chat beside your bars (now " .. OnOff(db.fit) .. ")")
        print("  /achat now            fit it again right away")
        print("  /achat font 8-24      text size (now " .. tostring(db.fontSize) .. ")")
        print("  /achat trim on|off    Aether panel (now " .. OnOff(db.trim) .. ")")
        print("  /achat buttons on|off voice/channel/emote buttons (now " .. (db.hideButtons and "off" or "on") .. ")")
        print("  /achat edit on|off    slim typing line (now " .. OnOff(db.slimEdit) .. ")")
        print("  /achat reset          restore defaults")
    end
end
