# AetherSkins 1.3.0: the second pass (AetherSkins_Pass2.lua). Mock parts
# built from the user's /skins tree dumps (tools/dumps/): side tabs, list
# headers, rep bars, talent nodes in every state, talent arrows, spec icons,
# spellbook entries, Group Finder role buttons, vendor tiles, the world map
# (chrome one level down) and maximize/minimize buttons.
import sys
src = open('skins_windows_test.py').read()
env = src.rsplit("L.execute(open('/home/claude/brand/AetherSkins/AetherSkins.lua').read())", 1)[0]
exec(env)
L.execute(r'''
local M = getmetatable(NEW("Texture")).__index
-- texture methods the second pass uses
local function addmethods(t)
  t.SetAtlas = function(s, a) s.atlas = a end
  t.GetAtlas = function(s) return s.atlas end
  t.SetDesaturated = function(s, v) s.desat = v end
  t.IsDesaturated = function(s) return s.desat end
  t.SetBlendMode = function(s, m) s.blend = m end
  t.GetVertexColor = function(s) local c = s.vc or {1,1,1,1}; return c[1], c[2], c[3], c[4] end
  t.SetShown = function(s, v) s.shown = v and true or false end
  t.SetThickness = function(s, v) s.thick = v end
  t.SetGradient = function(s) s.grad = true end
  t.GetTexture = function(s) return s.texture end
  t.SetColorTexture = function(s, r, g, b, a) s.colortex = {r, g, b, a} end
  return t
end
CreateColor = function(r, g, b, a) return {r, g, b, a} end
function kid(parent, kind, name) local f = CreateFrame(kind, name, parent); f.kind = kind; addmethods(f); return f end
function tex(owner, atlas, file)
  local t = addmethods(owner:CreateTexture()); t.atlas = atlas; if file then t.texture = file end; t.shown = true; t.alpha = 1; return t
end
-- make every texture created from now on (ours too) carry the methods
local oldCT = CreateFrame
CreateFrame = function(...) local f = oldCT(...); addmethods(f)
  local ct = f.CreateTexture; f.CreateTexture = function(s, ...) return addmethods(ct(s, ...)) end
  local cf = f.CreateFontString; f.CreateFontString = function(s, ...) local fs = cf(s, ...); fs.SetShown = function(x, v) x.shown = v end; return fs end
  return f end

WIN = WINDOW("CharacterFrame", false)
-- re-create the window's own textures with methods
-- side tabs: tab 2 selected
TABS = {}
for i = 1, 2 do
  local t = kid(WIN, "Frame", "CharacterFrameModeTab" .. i); t.w, t.h = 55, 55
  t.Background = tex(t, "common-sidetab"); t.SelectedTexture = tex(t, "common-sidetab-selected"); t.SelectedTexture.shown = (i == 2)
  t.TabGlow = tex(t, "common-sidetab-selected"); t.HighlightTexture = tex(t, "common-sidetab-hover")
  TABS[i] = t
end
-- a rep header and a rep row with its bar
HDR = kid(WIN, "Button"); HDR.w, HDR.h = 343, 28
HDR.bg1 = tex(HDR, "common-button-list-collapseExpand"); HDR.Name = HDR:CreateFontString(); HDR.Name.SetTextColor = function(s, r, g, b) s.color = {r, g, b} end
HDR.StateIcon = tex(HDR, "common-button-list-minus")
ROW = kid(WIN, "Frame"); BAR = kid(ROW, "Frame"); BAR.w, BAR.h = 160, 29
BAR.bg = tex(BAR, "common-stat-bar-BG"); BAR.Fill = tex(BAR, "common-stat-bar-white")
HL = tex(ROW, "charactercreate-customize-dropdown-linemouseover-middle")
DIV = tex(WIN, "common-framedivider"); GBG = tex(WIN, "UI-Character-Info-General-BG")
-- talent nodes in each state
function NODE(atlas, rank, maxr)
  local n = kid(WIN, "Button"); n.w, n.h = 40, 40
  n.StateBorder = tex(n, atlas); n.StateBorderHover = tex(n, atlas); n.Icon = tex(n); n.DisabledOverlay = tex(n)
  n.SpendText = n:CreateFontString(); n.SpendText.text = rank and tostring(rank) or nil
  n.Glow = tex(n, "talents-node-square-greenglow"); n.Glow.shown = false
  n.SelectableGlow = tex(n, "talents-node-square-greenglow"); n.SelectableGlow.shown = false
  n.SelectableIcon = tex(n, "talents-icon-learnableplus"); n.SelectableIcon.shown = false
  n.GetNodeInfo = function() return { currentRank = rank or 0, maxRanks = maxr or 5 } end
  return n
end
NMAX = NODE("talents-node-square-yellow", 5, 5); NPART = NODE("talents-node-square-green", 2, 3)
NCAN = NODE("talents-node-square-gray"); NCAN.SelectableIcon.shown = true
NNONE = NODE("talents-node-square-gray"); NLOCK = NODE("talents-node-square-locked")
ARR = kid(WIN, "Frame"); ARR.Line = tex(ARR); ARR.ArrowHead = tex(ARR, "talents-arrow-head-yellow")
SPEC = kid(WIN, "Frame"); SPEC.w, SPEC.h = 48, 48
SPEC.icon = tex(SPEC); SPEC.icon.w, SPEC.icon.h = 36, 36
SPEC.MainRing = tex(SPEC, "Talents-Main-Ring-c60"); SPEC.TextBackground = tex(SPEC, "Talents-Main-Ring-Box-c60")
-- spellbook entry: trainable
SPELL = kid(WIN, "Frame"); SPELL.Backplate = tex(SPELL, "spellbook-item-backplate")
SPELL.Button = kid(SPELL, "Button"); SPELL.Button.w = 40
SPELL.Button.Border = tex(SPELL.Button, "spellbook-item-iconframe"); SPELL.Button.Icon = tex(SPELL.Button)
SPELL.Button.TrainableShadow = tex(SPELL.Button, "spellbook-item-needtrainer-shadow"); SPELL.Button.TrainableShadow.shown = true
SPELL.TextContainer = kid(SPELL, "Frame"); SPELL.TextContainer.Name = SPELL.TextContainer:CreateFontString()
SPELL.TextContainer.RequiredLevel = SPELL.TextContainer:CreateFontString(); SPELL.TextContainer.RequiredLevel.shown = false
-- Group Finder role button
ROLEB = kid(WIN, "Button"); ROLEB.w, ROLEB.h = 64, 64; ROLEB.IsEnabled = function() return true end
ROLEB.bgt = tex(ROLEB, "UI-LFG-RoleIcon-Tank-Background"); ROLEB.cover = tex(ROLEB); ROLEB.cover.shown = false
ROLEB.ic = tex(ROLEB, "UI-LFG-RoleIcon-Tank")
ROLEB.CheckButton = kid(ROLEB, "CheckButton"); ROLEB.CheckButton.checked = false
ROLEB.CheckButton.SetChecked = function(s, v) s.checked = v end; ROLEB.CheckButton.GetChecked = function(s) return s.checked end
-- vendor tile with an item button
MI = kid(WIN, "Frame", "MerchantItem1"); MI.slot = tex(MI, nil, 130766); MI.plaque = tex(MI, nil, 136423)
MIB = kid(MI, "Button"); MIB.nt = tex(MIB, nil, 130841)
-- maximize button
MAXB = kid(WIN, "Button"); MAXB.a = tex(MAXB, "RedButton-Expand")
-- world map: chrome under BorderFrame
MAP = kid(UIParent, "Frame", "WorldMapFrame"); MAP.shown = false
MAP.BorderFrame = kid(MAP, "Frame"); MAP.BorderFrame.NineSlice = kid(MAP.BorderFrame, "Frame")
MAP.BorderFrame.TitleContainer = kid(MAP.BorderFrame, "Frame"); MAP.BorderFrame.TitleContainer.TitleText = MAP.BorderFrame.TitleContainer:CreateFontString()
MAP.BorderFrame.PortraitContainer = kid(MAP.BorderFrame, "Frame"); MAP.BorderFrame.PortraitContainer.portrait = tex(MAP.BorderFrame.PortraitContainer)
NAV = kid(MAP, "Frame"); NAV.t = tex(NAV, nil, 516764)
''')
L.execute(open('/home/claude/brand/AetherSkins/AetherSkins.lua').read())
L.execute(open('/home/claude/brand/AetherSkins/AetherSkins_Windows.lua').read())
L.execute(open('/home/claude/brand/AetherSkins/AetherSkins_Pass2.lua').read())
def fire(ev, arg=None):
    a = ('"%s"' % arg) if arg else 'nil'
    L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then f.scripts.OnEvent(f, "%s", %s) end end' % (ev, a))
fire("ADDON_LOADED", "AetherSkins"); fire("PLAYER_LOGIN")
L.execute('WIN.shown = true; AetherSkins_Windows.Skin(WIN)')
ok = True
def expect(label, got, want):
    global ok
    good = got == want; ok &= good
    print(("ok   " if good else "FAIL ") + label + ("" if good else "   got %r, want %r" % (got, want)))
E = L.eval
P2 = 'AetherSkins_Windows.P2'
expect("second pass loaded", E(P2 + ' ~= nil'), True)
# side tabs
expect("side tab: Blizzard art faded", E('TABS[1].Background.alpha == 0 and TABS[1].TabGlow.alpha == 0'), True)
expect("selected side tab: gold notch shown", E('(function() for _, r in ipairs(TABS[2].regs) do if r.vc and r.vc[2] == 0.69 and r.w == 4 then return r.shown ~= false end end return false end)()'), True)
expect("other side tab: no notch", E('(function() for _, r in ipairs(TABS[1].regs) do if r.vc and r.vc[2] == 0.69 and r.w == 4 then return r.shown end end return "none" end)()'), False)
L.execute('TABS[1].SelectedTexture:Show(); TABS[2].SelectedTexture:Hide()')
expect("switching side tabs moves the notch", E('(function() for _, r in ipairs(TABS[1].regs) do if r.vc and r.vc[2] == 0.69 and r.w == 4 then return r.shown end end end)()'), True)
expect("window with side tabs: right chevron hidden", E('AetherSkins_Windows.chev[WIN].right[2].shown'), False)
# headers, bars, rows, lines
expect("list header: brown bar faded, gold name", E('HDR.bg1.alpha == 0 and HDR.Name.color[2] == 0.69'), True)
expect("header +/- turned gold", E('HDR.StateIcon.desat == true and HDR.StateIcon.vc[2] == 0.69'), True)
expect("rep bar: Blizzard track faded, capsule drawn", E('BAR.bg.alpha == 0 and #BAR.regs > 4'), True)
L.execute('BAR.Fill:SetVertexColor(1, 0.82, 0)')
expect("rep bar: Blizzard's yellow fill becomes Aether gold", E('BAR.Fill.vc[2]'), 0.69)
L.execute('BAR.Fill:SetVertexColor(0, 0.6, 0.1)')
expect("rep bar: green fill becomes Aether green", round(E('BAR.Fill.vc[2]'), 3), 0.902)
expect("row highlight tinted blue", E('HL.desat == true and HL.vc[3] == 1'), True)
expect("divider tinted blue, brown background faded", E('DIV.vc[3] == 1 and GBG.alpha == 0'), True)
# talents
def border(n): return tuple(round(x, 2) for x in E('{%s.StateBorder.vc[1], %s.StateBorder.vc[2], %s.StateBorder.vc[3]}' % (n, n, n)).values())
expect("maxed: gold frame", border('NMAX'), (1, 0.69, 0))
expect("maxed: icon gold tint", E('NMAX.Icon.desat == true and NMAX.Icon.vc[2] == 0.69'), True)
expect("some points: blue frame, icon in color", (border('NPART'), E('NPART.Icon.desat')), ((0.3, 0.65, 1), False))
expect("can take: light frame, art in color, blue glow on", (border('NCAN'), E('NCAN.Icon.desat')), ((0.82, 0.84, 0.87), False))
expect("can take: glow shown", E('(function() for _, r in ipairs(NCAN.regs) do if r.texture and r.texture:find("glow_sq") then return r.shown end end end)()'), True)
expect("not taken (no points): lighter navy frame and navy icon", (border('NNONE'), E('NNONE.Icon.desat')), ((0.43, 0.59, 0.82), True))
expect("not taken: navy plate behind it", E('(function() for _, r in ipairs(NNONE.regs) do if r.vc and math.abs(r.vc[1] - 0.12) < 0.01 then return r.shown end end end)()'), True)
expect("locked: lighter gray, Blizzard's dark overlay hidden", (border('NLOCK'), E('NLOCK.DisabledOverlay.alpha')), ((0.62, 0.65, 0.7), 0))
NCAN2 = None
L.execute('NINFO = NODE("talents-node-square-gray"); NINFO.GetNodeInfo = function() return { currentRank = 0, maxRanks = 3, canPurchaseRank = true } end; AetherSkins_Windows.P2.Node(NINFO)')
expect("can take, from the node's own info (no glow parts shown)", border('NINFO'), (0.82, 0.84, 0.87))
def pill(n): return E('(function() for _, r in ipairs(%s.regs) do if r.kind == "FontString" and r.font and r.text and r.text:find(" of ") then return r.text end end end)()' % n)
expect("maxed shows '5 of 5'", pill('NMAX'), "5 of 5")
expect("some points shows '2 of 3'", pill('NPART'), "2 of 3")
expect("Blizzard's count hidden", E('NMAX.SpendText.alpha'), 0)
L.execute('NNONE.SelectableIcon:Show()')
expect("points come back: the empty talent gets the glow and its color", (border('NNONE'), E('NNONE.Icon.desat')), ((0.82, 0.84, 0.87), False))
L.execute('NPART.StateBorder:SetAtlas("talents-node-square-yellow")')
expect("Blizzard re-sets the frame (maxed now): restyled gold", border('NPART'), (1, 0.69, 0))
expect("arrow: 3D head and shaft, thicker", E('ARR.ArrowHead.texture:find("arrow_head_gold") ~= nil and ARR.Line.texture:find("arrow_shaft_gold") ~= nil and ARR.Line.thick == 6'), True)
L.execute('ARR.ArrowHead:SetAtlas("talents-arrow-head-locked")')
expect("arrow into a locked talent turns gray", E('ARR.ArrowHead.texture:find("arrow_head_gray") ~= nil'), True)
expect("gray arrow: solid shaft (no striped texture)", E('ARR.Line.colortex ~= nil and ARR.Line.colortex[1] == 0.59'), True)
expect("spec icon: gold on navy (desaturated, gold, added)", E('SPEC.icon.desat == true and SPEC.icon.vc[2] == 0.69 and SPEC.icon.blend == "ADD"'), True)
expect("spec ring blue, box navy", E('SPEC.MainRing.vc[3] == 1 and SPEC.TextBackground.vc[3] == 0.52'), True)
# spellbook
expect("trainable spell: Blizzard shadow faded, our glow shown", E('SPELL.Button.TrainableShadow.alpha == 0 and (function() for _, r in ipairs(SPELL.Button.regs) do if r.texture and r.texture:find("glow_sq") then return r.shown end end end)()'), True)
expect("Blizzard's ornate spell frame faded, our blue frame around the icon", E('SPELL.Button.Border.alpha == 0 and (function() local n = 0; for _, r in ipairs(SPELL.Button.regs) do if r.vc and r.vc[3] == 1 and r.points[1] and r.points[1][2] == SPELL.Button.Icon then n = n + 1 end end; return n >= 8 end)()'), True)
L.execute('SPELL.TextContainer.RequiredLevel.text = "Level 46"; SPELL.TextContainer.RequiredLevel:Show(); SPELL.Button.TrainableShadow:Hide()')
expect("level too low: icon navy", E('SPELL.Button.Icon.desat == true and SPELL.Button.Icon.vc[3] == 0.85'), True)
# roles
def ring(): return E('(function() for _, r in ipairs(ROLEB.regs) do if r.texture and r.texture:find("ring_thin") then return r.vc[2] end end end)()')
expect("role: Blizzard art faded, our glyph in gold", E('ROLEB.ic.alpha == 0 and ROLEB.bgt.alpha == 0 and (function() for _, r in ipairs(ROLEB.regs) do if r.texture and r.texture:find("role_tank") then return r.vc[2] == 0.69 end end end)()'), True)
expect("role not picked: blue ring", ring(), 0.65)
L.execute('ROLEB.CheckButton:SetChecked(true)')
expect("role picked: gold ring", ring(), 0.69)
# vendor, buttons, map
expect("vendor: slot and plaque faded, navy tile", E('MI.slot.alpha == 0 and MI.plaque.alpha == 0 and #MI.regs > 3'), True)
expect("vendor item: quickslot faded, blue icon frame", E('MIB.nt.alpha == 0 and #MIB.regs >= 8'), True)
expect("maximize: red art faded, navy box", E('MAXB.a.alpha == 0 and #MAXB.regs > 5'), True)
L.execute('MAP.shown = true; AetherSkins_Windows.Watch(MAP); AetherSkins_Windows.Skin(MAP)')
expect("world map recognized and skinned", E('AetherSkins_Windows.skinned[MAP] == true'), True)
expect("world map: chrome (one level down) faded", E('MAP.BorderFrame.NineSlice.alpha'), 0)
expect("world map: breadcrumb bar tinted navy", E('NAV.t.desat == true'), True)
# --- Build 1 fixes (Nov 25)
L.execute(r'''
local function fs(owner, r, g, b)
  local f = owner:CreateFontString(); f.c = {r, g, b}
  f.SetTextColor = function(s, r, g, b) s.c = {r, g, b} end
  f.GetTextColor = function(s) return s.c[1], s.c[2], s.c[3] end
  f.SetFontObject = function(s, o) s.fo = o end
  f.GetObjectType = function() return "FontString" end
  return f
end
-- dark spell name, gold title, white text
TXT = kid(WIN, "Frame"); DARKT = fs(TXT, 0.2, 0.12, 0.05); GOLDT2 = fs(TXT, 1, 0.69, 0); WHT = fs(TXT, 1, 1, 1)
TXT.GetRegions = function(s) return DARKT, GOLDT2, WHT end
-- friends card
CARD = kid(WIN, "Button"); CARD.bg = tex(CARD, "friends-card-offline")
-- an item button with Blizzard's quality border (green) and an empty vendor tile
GEAR = kid(WIN, "Button"); GEAR.nt = tex(GEAR, nil, 130841); GEAR.IconBorder = tex(GEAR, nil, 651080)
GEAR.IconBorder.vc = {0.12, 1, 0}; GEAR.bronze = tex(GEAR, "UI-Character-Info-GearSlot")
MI2 = kid(WIN, "Frame", "MerchantItem2"); MI2.slot = tex(MI2, nil, 130766)
MI2.ItemButton = kid(MI2, "Button"); MI2.ItemButton.shown = false
-- red close button on a page inside the window
RCB = kid(WIN, "Button"); RCB.a = tex(RCB, "RedButton-Exit")
-- New Player Friendly: an 84 px role button
NPF = kid(WIN, "Button"); NPF.w, NPF.h = 84, 84; NPF.IsEnabled = function() return true end
NPF.ic = tex(NPF, "UI-LFG-RoleIcon-Leader")
-- a scroll list
SCROLLUTIL_CB = {}
ScrollUtil = { AddAcquiredFrameCallback = function(sb, cb) SCROLLUTIL_CB[#SCROLLUTIL_CB + 1] = cb end,
               AddInitializedFrameCallback = function(sb, cb) SCROLLUTIL_CB[#SCROLLUTIL_CB + 1] = cb end }
C_Timer = C_Timer or {}; C_Timer.After = function(_, fn) fn() end
LIST = kid(WIN, "Frame"); LIST.ScrollTarget = kid(LIST, "Frame")
AetherSkins_Windows.Contents(WIN)
''')
expect("dark text on our navy turns light", tuple(round(x, 2) for x in E('{DARKT.c[1], DARKT.c[2], DARKT.c[3]}').values()) != (0.2, 0.12, 0.05) and E('DARKT.c[1] > 0.7'), True)
expect("gold and white text left as they are", E('GOLDT2.c[2] == 0.69 and WHT.c[1] == 1'), True)
L.execute('DARKT:SetTextColor(0.1, 0.05, 0)')
expect("Blizzard sets it dark again: light again", E('DARKT.c[1] > 0.7'), True)
L.execute('HDR.Name:SetTextColor(0.5, 0.5, 0.5)')
expect("list header recolored by Blizzard: gold again", E('HDR.Name.color[2]'), 0.69)
expect("friends card navy", E('CARD.bg.vc[3] < 0.3 and CARD.bg.desat == true'), True)
L.execute('CARD.bg:SetVertexColor(1, 0.82, 0)')
expect("Blizzard turns the card gold: navy again", E('CARD.bg.vc[2] < 0.3'), True)
def gear_edge(): return E('(function() for _, r in ipairs(GEAR.regs) do if r.texture and tostring(r.texture):find("WHITE") and r.vc and r.points[1] and r.points[1][2] == GEAR then return r.vc[2] end end end)()')
expect("gear slot: Blizzard's bronze frame and quality border faded", E('GEAR.bronze.alpha == 0 and GEAR.IconBorder.alpha == 0'), True)
expect("green item: our frame takes the quality color", gear_edge(), 1)
L.execute('GEAR.IconBorder:Hide()')
expect("no quality border (common item): blue frame", round(gear_edge(), 2), 0.65)
expect("empty vendor tile: navy tile hidden", E('(function() for _, r in ipairs(MI2.regs) do if r.vc and r.vc[3] == NAVYZ then end end; local n = 0; for _, r in ipairs(MI2.regs) do if r.shown == false then n = n + 1 end end; return n >= 5 end)()'), True)
L.execute('MI2.ItemButton:Show()')
expect("item appears: tile shown", E('(function() for _, r in ipairs(MI2.regs) do if r.shown == false then return false end end; return true end)()'), True)
expect("red close button on a page: faded, our navy box", E('RCB.a.alpha == 0 and #RCB.regs > 5'), True)
expect("New Player Friendly disc clamped to the 64 size", E('(function() for _, r in ipairs(NPF.regs) do if r.texture and r.texture:find("disc_plain") then return r.w end end end)()'), 64 * 0.92)
expect("scroll list registered for new rows", E('#SCROLLUTIL_CB'), 2)
L.execute('NEWROW = kid(LIST.ScrollTarget, "Button"); NEWROW.bg1 = tex(NEWROW, "common-button-list-collapseExpand"); SCROLLUTIL_CB[1](nil, NEWROW)')
expect("a row made later (on scroll) gets styled right away", E('NEWROW.bg1.alpha'), 0)
L.execute('STATH = kid(WIN, "Frame"); STATH.Background = tex(STATH, "UI-Character-Info-Title"); STATH.Title = STATH:CreateFontString(); STATH.Title.SetTextColor = function(x, r, g, b) x.color = {r, g, b} end; AetherSkins_Windows.Contents(WIN)')
expect("character stat headings: navy strip with a gold title", E('STATH.Background.alpha == 0 and STATH.Title.color[2] == 0.69 and #STATH.regs >= 3'), True)
L.execute('LTABS = kid(UIParent, "Frame"); LT = kid(LTABS, "Frame"); LT.w, LT.h = 55, 55; LT.Background = tex(LT, "common-sidetab"); LT.SelectedTexture = tex(LT, "common-sidetab-selected"); LT.TabGlow = tex(LT, "common-sidetab-selected"); LT.HighlightTexture = tex(LT, "common-sidetab-hover"); GetTime = function() return 1000 end; AetherSkins_Windows.Contents(WIN)')
expect("Group Finder side tabs (outside any window) styled like the Character ones", E('LT.Background.alpha == 0 and #LT.regs > 6'), True)
L.execute('UnitCharacterPoints = function() return 0 end; NZERO = NODE("talents-node-square-gray"); NZERO.GetNodeInfo = function() return { currentRank = 0, maxRanks = 3, canPurchaseRank = true } end; AetherSkins_Windows.P2.Node(NZERO); UnitCharacterPoints = nil')
expect("no points left: a talent the game calls buyable shows as not taken (navy)", border('NZERO'), (0.43, 0.59, 0.82))
L.execute('NLOCK.Icon:SetVertexColor(0.4, 0.4, 0.4)')
expect("Blizzard darkens a locked icon: ours comes back", round(E('NLOCK.Icon.vc[1]'), 2), 0.92)
L.execute('''PGB = kid(WIN, "Button"); PGB.up = tex(PGB, nil, 130866); PGB.dis = tex(PGB, nil, 130865)
PGB.GetDisabledTexture = function(s) return s.dis end; AetherSkins_Windows.Contents(WIN)''')
expect("page arrow: bright when clickable, dim when not", (E('PGB.up.vc[1] > 0.8'), E('PGB.dis.vc[1] < 0.4')), (True, True))
L.execute('WALKS = 0; local c = AetherSkins_Windows.Contents; QuestLogQuests_Update = function() end; WorldMapFrame = MAP; AetherSkins_Windows.P2.questLogHooked = nil; AetherSkins_Windows.Contents(WIN); AetherSkins_Windows.Contents = function(r) if r == MAP then WALKS = WALKS + 1 end; return c(r) end; QuestLogQuests_Update(); AetherSkins_Windows.Contents = c')
expect("map quest log update: the map is walked again", E('WALKS') >= 1, True)
L.execute('''SP2 = kid(WIN, "Frame"); SP2.Backplate = tex(SP2, "spellbook-item-backplate")
SP2.Button = kid(SP2, "Button"); SP2.Button.w = 40; SP2.Button.Border = tex(SP2.Button, "spellbook-item-iconframe"); SP2.Button.Icon = tex(SP2.Button)
SP2.TextContainer = kid(SP2, "Frame"); SP2.TextContainer.Name = SP2.TextContainer:CreateFontString()
SP2.UpdateVisuals = function(self) self.Button.Border.alpha = 1 end
AetherSkins_Windows.Contents(WIN); SP2:UpdateVisuals()''')
expect("Blizzard redraws a spell entry (mouse over): our look comes back", E('SP2.Button.Border.alpha'), 0)
# switch off
expect("everything wrapped: no errors marked", E('(function() for k, v in pairs(AetherSkins_Windows.done) do if v == "failed" then return false end end return true end)()'), True)
print("ALL OK" if ok else "FAILED"); sys.exit(0 if ok else 1)
