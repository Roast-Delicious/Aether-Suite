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
  t.GetThickness = function(s) return s.thick or 4 end
  t.SetGradient = function(s) s.grad = true end
  t.GetTexture = function(s) return s.texture end
  t.SetColorTexture = function(s, r, g, b, a) s.colortex = {r, g, b, a}; s.atlas = nil end
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
ARR = kid(WIN, "Frame"); ARR.Line = tex(ARR); ARR.ArrowHead = tex(ARR, "talents-arrow-head-yellow"); ARR.Line.SetAtlas = function(s, a) s.atlas = a; s.colortex = nil end
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
L.execute(open('/home/claude/brand/AetherSkins/AetherSkins_Pass3.lua').read())
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
expect("selected side tab: gold edge (the old notch is replaced by the thick frame)", E('(function() for _, r in ipairs(TABS[2].regs) do if r.vc and r.vc[2] == 0.69 and r.w == 4 then return r.shown end end return "none" end)()'), False)
expect("other side tab: no notch", E('(function() for _, r in ipairs(TABS[1].regs) do if r.vc and r.vc[2] == 0.69 and r.w == 4 then return r.shown end end return "none" end)()'), False)
L.execute('TABS[1].SelectedTexture:Show(); TABS[2].SelectedTexture:Hide()')
expect("switching side tabs: no notch either way", E('(function() for _, r in ipairs(TABS[1].regs) do if r.vc and r.vc[2] == 0.69 and r.w == 4 then return r.shown end end end)()'), False)
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
def arrow(): return (E('ARR.ArrowHead.texture'), tuple(round(E('ARR.ArrowHead.vc[%d]' % k), 2) for k in (1, 2, 3)), tuple(round(E('ARR.Line.colortex[%d]' % k), 2) for k in (1, 2, 3)), E('ARR.Line.thick'))
FLAT = None
expect("gold arrow: flat head, solid gold shaft, 3.25 thick", arrow()[1:], ((1, 0.69, 0), (1, 0.69, 0), 3.25))
expect("gold arrow: our flat head art", E('tostring(ARR.ArrowHead.texture):find("arrow_head_flat") ~= nil'), True)
# Blizzard's pool: one arrow handed between links in any order
for st, want in (("locked", (0.78, 0.8, 0.86)), ("yellow", (1, 0.69, 0)), ("ghost", (0.3, 0.65, 1)), ("green", (0.3, 0.65, 1)), ("gray", (0.78, 0.8, 0.86)), ("yellow", (1, 0.69, 0))):
    L.execute('ARR.ArrowHead:SetAtlas("talents-arrow-head-%s")' % st)
    got = arrow()
    expect("pool -> %s: head and shaft %s, same width, nothing left over" % (st, want), (got[1], got[2], got[3], E('ARR.Line.vc[1] == 1 and ARR.Line.vc[2] == 1')), (want, want, 3.25, True))
L.execute('ARR.ArrowHead:SetAtlas("talents-arrow-head-yellow"); ARR.GhostArrowHead = tex(ARR, "talents-arrow-head-ghost"); ARR.GhostArrowHead:SetAtlas("talents-arrow-head-ghost")')
expect("the hidden ghost head leaves the real shaft alone (it was painted preview blue)", (tuple(round(E('ARR.Line.colortex[%d]' % k), 2) for k in (1, 2, 3)), E('ARR.Line.colortex[4]')), ((1, 0.69, 0), 1))
L.execute('ARR.Line:SetVertexColor(0.2, 0.4, 0.8, 0.6)')
expect("Blizzard recolors the shaft: ours comes back", (E('ARR.Line.vc[1] == 1 and ARR.Line.vc[2] == 1'), round(E('ARR.Line.colortex[2]'), 2)), (True, 0.69))
L.execute('ARR.ArrowHead:SetAtlas("talents-arrow-head-gray"); ARR.Line:SetAtlas("talents-arrow-line-gray")')
expect("Blizzard re-sets only the shaft: ours comes back (no art, no 2nd head)", (E('ARR.Line.colortex ~= nil and ARR.Line.colortex[1] == 0.78'), E('ARR.Line.thick')), (True, 3.25))
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
expect("friends card: Blizzard's art faded, our frame-dark fill (offline)", E('CARD.bg.alpha == 0 and (function() for _, r in ipairs(CARD.regs) do if r.vc and math.abs(r.vc[3] - 0.075) < 0.01 then return true end end return false end)()'), True)
def gear_edge(): return E('(function() for _, r in ipairs(GEAR.regs) do if r.texture and tostring(r.texture):find("WHITE") and r.vc and r.points[1] and r.points[1][2] == GEAR then return r.vc[2] end end end)()')
expect("gear slot: Blizzard's bronze frame and quality border faded", E('GEAR.bronze.alpha == 0 and GEAR.IconBorder.alpha == 0'), True)
expect("green item: our frame takes the quality color", gear_edge(), 1)
L.execute('GEAR.IconBorder:Hide()')
expect("no quality border, empty slot: dim slate frame", round(gear_edge(), 2), 0.25)
L.execute('GEAR.icon = tex(GEAR, nil, 133117); GEAR.IconBorder:Show(); GEAR.IconBorder.vc = {1, 1, 1}; GEAR.IconBorder:SetVertexColor(1, 1, 1)')
expect("plain (white) item: silver frame", round(gear_edge(), 2), 0.8)
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
L.execute('''PGB = kid(WIN, "Button"); PGB.enabled = true; PGB.IsEnabled = function(s) return s.enabled end
PGB.Disable = function(s) s.enabled = false end; PGB.Enable = function(s) s.enabled = true end
PGB.up = tex(PGB, nil, 130866); PGB.dis = tex(PGB, nil, 130864); AetherSkins_Windows.Contents(WIN)''')
def chevc(): return E('(function() for _, r in ipairs(PGB.regs) do if r.texture and tostring(r.texture):find("chev3d_right") then return r.desat and "gray" or "gold" end end end)()')
expect("page arrow: Blizzard's art hidden, our chevron in its place", (E('PGB.up.alpha == 0 and PGB.dis.alpha == 0'), chevc()), (True, "gold"))
L.execute('PGB:Disable()')
expect("last page: the chevron goes gray", chevc(), "gray")
L.execute('PGB:Enable()')
expect("page back: gold again", chevc(), "gold")
L.execute('WALKS = 0; local c = AetherSkins_Windows.Contents; QuestLogQuests_Update = function() end; WorldMapFrame = MAP; AetherSkins_Windows.P2.questLogHooked = nil; AetherSkins_Windows.Contents(WIN); AetherSkins_Windows.Contents = function(r) if r == MAP then WALKS = WALKS + 1 end; return c(r) end; QuestLogQuests_Update(); AetherSkins_Windows.Contents = c')
expect("map quest log update: the map is walked again", E('WALKS') >= 1, True)
L.execute('''SP2 = kid(WIN, "Frame"); SP2.Backplate = tex(SP2, "spellbook-item-backplate")
SP2.Button = kid(SP2, "Button"); SP2.Button.w = 40; SP2.Button.Border = tex(SP2.Button, "spellbook-item-iconframe"); SP2.Button.Icon = tex(SP2.Button)
SP2.TextContainer = kid(SP2, "Frame"); SP2.TextContainer.Name = SP2.TextContainer:CreateFontString()
SP2.UpdateVisuals = function(self) self.Button.Border.alpha = 1 end
AetherSkins_Windows.Contents(WIN); SP2:UpdateVisuals()''')
expect("Blizzard redraws a spell entry (mouse over): our look comes back", E('SP2.Button.Border.alpha'), 0)
# --- Build 2 designs (AetherSkins_Pass3.lua)
expect("pass 3 loaded", E('AetherSkins_Windows.P3 ~= nil'), True)
def has_tex(obj, name): return E('(function() for _, r in ipairs(%s.regs) do if r.texture and tostring(r.texture):find("%s") then return r.shown ~= false end end return false end)()' % (obj, name))
L.execute('TABS[2].Icon = tex(TABS[2], nil, 8197103); TABS[3] = nil')
L.execute('NT = kid(WIN, "Frame", "CharacterFrameModeTab9"); NT.w = 55; NT.Background = tex(NT, "common-sidetab"); NT.SelectedTexture = tex(NT, "common-sidetab-selected"); NT.SelectedTexture.shown = false; NT.TabGlow = tex(NT, "common-sidetab-selected"); NT.HighlightTexture = tex(NT, "common-sidetab-hover"); NT.Icon = tex(NT, nil, 8197104); AetherSkins_Windows.Contents(WIN)')
expect("side tab: Blizzard icon faded, flat gold glyph (stats)", (E('NT.Icon.alpha'), has_tex('NT', 'tab_stats')), (0, True))
expect("closed tab: no gold glow", has_tex('NT', 'glow_sq'), False)
L.execute('NT.SelectedTexture:Show()')
expect("open tab: soft gold glow", has_tex('NT', 'glow_sq'), True)
# the glow's hollow middle fits the tab's box (52x49 on a 55x55 tab, dump
# b161), 2 px inside it, so its hard edge hides under the box (user 16:49)
L.execute(r"""
local p = AetherSkins_Windows.P2.H.tabParts[NT]
p.fill.w, p.fill.h = 52, 49
p.fill.GetHeight = function(s) return s.h end
AetherSkins_Windows.P2.SideTabExtra(NT)
for _, r in ipairs(NT.regs) do if r.texture and tostring(r.texture):find("glow_sq") then GLW, GLH = r.w, r.h end end
RINGR = 0
for _, k in ipairs(NT.kids or {}) do for _, r in ipairs(k.regs or {}) do if r.texture and tostring(r.texture):find("btn_round4_line") then RINGR = RINGR + 1 end end end
""")
expect("open tab glow: hole = box minus 2 px a side", (E('GLW'), E('GLH')), (96, 90))
expect("open tab: inner gold rings rounded (radius 4 corners)", E('RINGR'), 4)
L.execute('VB = kid(WIN, "Button", "MerchantRepairAllButton"); VB.Icon = tex(VB, "SpellIcon-256x256-RepairAll"); VG = kid(WIN, "Button", "MerchantGuildBankRepairButton"); VG.Icon = tex(VG, "SpellIcon-256x256-RepairAll"); AetherSkins_Windows.Contents(WIN)')
L.execute('VB.enabled = false; VB.IsEnabled = function(s) return s.enabled end; VB.Disable = function(s) s.enabled = false end; VB.Enable = function(s) s.enabled = true end')
expect("vendor: flat anvil on repair all, shield on guild repair", (has_tex('VB', 'btn_repairall'), has_tex('VG', 'btn_guild'), E('VB.Icon.alpha'), E('VB.Icon.atlas')), (True, True, 0, "SpellIcon-256x256-RepairAll"))
L.execute('SB = kid(WIN, "Frame"); SB.t = tex(SB, "minimal-scrollbar-small-thumb-middle"); SB.a = tex(SB, "minimal-scrollbar-arrow-top"); SB.k = tex(SB, "!minimal-scrollbar-track-middle"); AetherSkins_Windows.Contents(WIN)')
expect("scroll bar: beveled gold thumb, chevron arrow, navy track", (has_tex('SB', 'sb_thumb_mid'), has_tex('SB', 'chev3d_up'), round(E('SB.k.vc[3]'), 2)), (True, True, 0.32))
expect("...laid over Blizzard's thumb, whose atlas stays (Blizzard reads it back)", (E('SB.t.atlas'), E('SB.t.alpha')), ("minimal-scrollbar-small-thumb-middle", 0))
L.execute('PG = kid(WIN, "Frame"); PG.bg = tex(PG, "QuestBG-Parchment"); PG.bg.alpha = 0; AetherSkins_Windows.Contents(WIN)')
expect("quest parchment: flat Aether blue page laid over it (bg_tiers A)", E('PG.bg.alpha == 0 and (function() for _, r in ipairs(PG.regs) do if r.vc and math.abs(r.vc[1] - 10/255) < 0.01 then return true end end return false end)()'), True)
L.execute('FC = kid(WIN, "Button"); FC.LockHighlight = function() end; FC.UnlockHighlight = function() end; FC.bg = tex(FC, "friends-card-battleNet"); FC.sel = tex(FC, "friends-card-selected"); AetherSkins_Windows.Contents(WIN)')
def notch(): return E('(function() for _, r in ipairs(FC.regs) do if r.vc and r.vc[2] == 0.69 and r.w == 4 then return r.shown end end end)()')
expect("Friends: mouse-over alone shows no notch", notch(), False)
L.execute('FC:LockHighlight()')
expect("picked (Blizzard locks the highlight): gold notch", notch(), True)
L.execute('FC:UnlockHighlight()')
expect("...gone when another is picked", notch(), False)
L.execute('NPFX = kid(WIN, "Button", "LFGListingFrameNewPlayerFriendlyButton"); NPFX.w, NPFX.h = 84, 84; NPFX.IsEnabled = function() return true end; NPFX.ic = tex(NPFX, "UI-LFG-RoleIcon-Leader"); AetherSkins_Windows.Contents(WIN)')
expect("New Player Friendly: the sprout", has_tex('NPFX', 'role_newcomer'), True)
L.execute('AetherSkinsDB = {}; GetCursorPosition = function() return 0, 0 end; WIN.SetScale = function(s, v) s.scale = v end; WIN.GetScale = function(s) return s.scale or 1 end; WIN.HookScript = WIN.HookScript or function() end; AetherSkins_Windows.P3.Grip(WIN)')
expect("corner grip made (not on quest windows)", E('(function() for _, k in ipairs({WIN:GetChildren()}) do if k.scripts and k.scripts.OnMouseDown then return true end end return false end)()'), True)
L.execute('AetherSkins_Windows.Contents(MAP)')
expect("world map crest: portrait faded, flat gold map", (E('MAP.BorderFrame.PortraitContainer.portrait.alpha'), has_tex('MAP.BorderFrame.PortraitContainer', 'gl_map')), (0, True))
expect("character window keeps its portrait", has_tex('WIN', 'gl_'), False)
L.execute('VR = kid(WIN, "Button", "MerchantRepairItemButton"); VR.enabled = true; VR.IsEnabled = function(s) return s.enabled end; VR.Disable = function(s) s.enabled = false end; VR.Enable = function(s) s.enabled = true end; VR.Icon = tex(VR, "SpellIcon-256x256-Repair"); AetherSkins_Windows.Contents(WIN)')
def hammer(): return E('(function() for _, r in ipairs(VR.regs) do if r.texture and tostring(r.texture):find("btn_repair") then return r.vc[2] end end end)()')
expect("repair button usable: gold hammer", hammer(), 0.69)
L.execute('VR:Disable()')
expect("nothing to repair: gray hammer", round(hammer(), 2), 0.65)
L.execute('VR:Enable(); GetRepairAllCost = function() return 0, true end; AetherSkins_Windows.P3.RefreshUsable()')
expect("repair item stays enabled, but costs nothing: gray", round(hammer(), 2), 0.65)
L.execute('GetRepairAllCost = function() return 1200, true end; AetherSkins_Windows.P3.RefreshUsable()')
expect("something to repair: gold", hammer(), 0.69)
# vendor tooltips (user 15:22): a note under Blizzard's tooltip on all
# three buttons when there's nothing to do, every line Aether gold
L.execute(r"""
TT = { lines = {} }
function TT:SetOwner() self.lines = {}; self.shown = false end
function TT:SetText(s, r, g, b) self.lines = { { s, r, g, b } } end
function TT:AddLine(s, r, g, b) self.lines[#self.lines + 1] = { s, r, g, b } end
function TT:Show() self.shown = true end
function TT:IsShown() return self.shown end
function TT:NumLines() return #self.lines end
GameTooltip = TT
setmetatable(_G, { __index = function(_, k) local n = type(k) == "string" and k:match("^GameTooltipTextLeft(%d+)$")
  if n then local l = TT.lines[tonumber(n)]; return l and { GetText = function() return l[1] end, SetTextColor = function(_, r, g, b) l[2], l[3], l[4] = r, g, b end } end end })
local function hookable(b) b.hooks = {}; b.HookScript = function(s, ev, fn) s.hooks[ev] = s.hooks[ev] or {}; table.insert(s.hooks[ev], fn) end
  b.SetMotionScriptsWhileDisabled = function() end; return b end
TR = hookable(kid(WIN, "Button", "MerchantRepairItemButton")); TR.IsEnabled = function() return true end; TR.Icon = tex(TR, "SpellIcon-256x256-Repair")
TJ = hookable(kid(WIN, "Button", "MerchantSellAllJunkButton")); TJ.on = false; TJ.IsEnabled = function(s) return s.on end; TJ.Icon = tex(TJ, "SpellIcon-256x256-SellJunk")
TA = hookable(kid(WIN, "Button", "MerchantRepairAllButton")); TA.IsEnabled = function() return false end; TA.Icon = tex(TA, "SpellIcon-256x256-RepairAll")
AetherSkins_Windows.Contents(WIN)
function Enter(b, blizTitle)       -- Blizzard's OnEnter (its own tooltip, or none), then ours
  TT:SetOwner(); if blizTitle then TT:SetText(blizTitle, 1, 1, 1); TT:Show() end
  for _, fn in ipairs((b.hooks or {}).OnEnter or {}) do fn(b) end
end
function Lines() local o = {} for _, l in ipairs(TT.lines) do o[#o + 1] = l[1] .. "@" .. tostring(l[3]) end return table.concat(o, " | ") end
""")
L.execute('GetRepairAllCost = function() return 0, true end')
L.execute('Enter(TR, "Repair an Item")')
expect("Repair an Item, nothing to repair: gold note under Blizzard's tooltip", E('Lines()'), "Repair an Item@0.69 | Nothing needs repair@0.69")
L.execute('Enter(TJ, "Sell All Junk Items")')
expect("Sell All Junk, no junk: gold note under Blizzard's tooltip", E('Lines()'), "Sell All Junk Items@0.69 | No junk to sell@0.69")
L.execute('Enter(TA, nil)')
expect("Repair All, nothing to repair: gold title and gold note", E('Lines()'), "Repair All Items@0.69 | Nothing needs repair@0.69")
L.execute('GetRepairAllCost = function() return 500, true end; TJ.on = true')
L.execute('Enter(TR, "Repair an Item")')
expect("something to repair: Blizzard's tooltip only", E('Lines()'), "Repair an Item@1")
L.execute('Enter(TJ, "Sell All Junk Items")')
expect("junk to sell: Blizzard's tooltip only", E('Lines()'), "Sell All Junk Items@1")
L.execute('setmetatable(_G, nil)')
L.execute('''SBB = kid(WIN, "Button"); SBB.enabled = false; SBB.IsEnabled = function(s) return s.enabled end
SBB.Enable = function(s) s.enabled = true end; SBA = tex(SBB, "minimal-scrollbar-arrow-top"); AetherSkins_Windows.Contents(WIN)''')
def up(): return E('(function() for _, r in ipairs(SBB.regs) do if r.texture and tostring(r.texture):find("chev3d_up") then return r.desat and "gray" or "gold" end end end)()')
expect("scroll at the top: up arrow gray", up(), "gray")
L.execute('SBB:Enable()')
expect("can scroll up: gold", up(), "gold")
L.execute('''POIB = kid(WIN, "Button"); POIB.NormalTexture = tex(POIB, "UI-QuestPoi-QuestNumber"); POIB.Display = kid(POIB, "Frame")
POIB.Display.Icon = tex(POIB.Display, "UI-QuestIcon-TurnIn-Normal")
TICK = kid(WIN, "Frame"); TICK.a = tex(TICK, "QuestLog-icon-ticksquare"); TICK.b = tex(TICK, "QuestLog-icon-ticksquare")
QLBG = tex(WIN, "QuestLog-main-background"); AetherSkins_Windows.Contents(WIN)''')
expect("map log quest icon: Blizzard's art hidden, navy disc + gold ring", (E('POIB.NormalTexture.alpha == 0 and POIB.Display.Icon.alpha == 0'), has_tex('POIB', 'trk_disc'), has_tex('POIB', 'trk_ring')), (True, True, True))
expect("map log turn-in: gold ? instead of dots", E('(function() for _, r in ipairs(POIB.regs) do if r.texture and tostring(r.texture):find("trk_dots") then return r.shown end end end)()'), False)
expect("map log track box: navy box, one per box", (E('TICK.a.alpha == 0 and TICK.b.alpha == 0'), E('(function() local n = 0; for _, r in ipairs(TICK.regs) do if r.texture and tostring(r.texture):find("WHITE8X8") then n = n + 1 end end return n end)()') >= 1), (True, True))
expect("map log background: near-black page (10,11,14)", E('(function() for _, r in ipairs(WIN.regs) do if r ~= QLBG and r.vc and math.abs(r.vc[1] - 10/255) < 0.01 and math.abs(r.vc[3] - 14/255) < 0.01 then return true end end return false end)()'), True)
L.execute('''RQ = kid(WIN, "Button"); RQ.NormalTexture = tex(RQ, "UI-QuestPoiRecurring-QuestNumber"); RQ.Display = kid(RQ, "Frame")
RQ.Display.Icon = tex(RQ.Display, "UI-QuestPoiRecurring-QuestBangTurnIn"); AetherSkins_Windows.Contents(WIN)''')
expect("daily quest icon: same navy disc", (E('RQ.NormalTexture.alpha == 0 and RQ.Display.Icon.alpha == 0'), has_tex('RQ', 'trk_disc')), (True, True))
L.execute('''QDB = tex(WIN, "QuestDetailsBackgrounds"); QRB = tex(WIN, "QuestLog-reward-bottom"); AetherSkins_Windows.Contents(WIN)''')
expect("map quest details: Blizzard's parchment and brown rewards hidden", E('QDB.alpha == 0 and QRB.alpha == 0'), True)
expect("map quest details: Aether blue page", E('(function() local n = 0; for _, r in ipairs(WIN.regs) do if r.vc and math.abs(r.vc[1] - 10/255) < 0.01 then n = n + 1 end end return n end)()') >= 2, True)
L.execute('''BIG = kid(WIN, "CheckButton"); BIG.w = 67; BIG.h = 67; BIG.Ring = tex(BIG, "Legacy-Tree-Frame-Card-Ring"); BIG.nt = tex(BIG, "UI-Legacy-Tree-Professions")
BIG.GetNormalTexture = function(s) return s.nt end; BIG.ck = tex(BIG, "charactercreate-ring-select"); BIG.GetCheckedTexture = function(s) return s.ck end
AetherSkins_Windows.Contents(WIN)''')
expect("Legacy Tree picture buttons are not checkboxes: the picture stays", E('BIG.nt.alpha ~= 0 and AetherSkins_Windows.done[BIG] ~= "check"'), True)
L.execute('''PC = tex(WIN, "Profession-overview-Card-Leatherworking"); PF = tex(WIN, "Skillbar_Fill_Flipbook_Leatherworking"); LC = tex(WIN, "Legacy-Challenge-Cards-Disable"); AetherSkins_Windows.Contents(WIN)''')
expect("profession card and legacy card: Blizzard art hidden", E('PC.alpha == 0 and LC.alpha == 0'), True)
expect("profession card: black like the pages (user 15:27, A)", E('(function() for _, r in ipairs(WIN.regs) do if r.points and r.points[1] and r.points[1][2] == PC and r.vc then return math.floor(r.vc[1] * 255 + 0.5) .. "," .. math.floor(r.vc[3] * 255 + 0.5) end end end)()'), "10,14")
expect("profession skill bar: gold fill", round(E('PF.vc[2]'), 2), 0.69)
L.execute('''MBG = tex(WIN, nil, 651761); CT = tex(WIN, "collections-background-tile"); CC = tex(WIN, "collections-background-corner"); PL = tex(WIN, "PetList-ButtonBackground"); AetherSkins_Windows.Contents(WIN)''')
expect("collections: model backdrop, page tile and list rows replaced, corners gone", E('MBG.alpha == 0 and CT.alpha == 0 and CC.alpha == 0 and PL.alpha == 0'), True)
L.execute('''LCB = kid(WIN, "Button"); LCB.mid = tex(LCB, "Legacy-Challenge-Cards-tiled-vertical-Disable"); LCB.mid.shown = false
LCB.bg = tex(LCB, "Legacy-Challenge-Cards-Disable"); AetherSkins_Windows.Contents(WIN)''')
expect("legacy card: one blue edge, none on the hidden tiled pieces", E('(function() local n = 0; for _, k in ipairs(LCB.kids or {}) do if k.shown ~= false then n = n + 1 end end return n end)()'), 1)
L.execute('''GF = kid(WIN, "Frame"); GF.Inset = kid(GF, "Frame"); GF.bg = tex(GF, "QuestBG-Parchment"); AetherSkins_Windows.Contents(WIN)''')
expect("gossip page: our blue fills the inset, not just Blizzard's smaller parchment", E('(function() for _, r in ipairs(GF.regs) do if r.vc and math.abs(r.vc[1] - 10/255) < 0.01 then for _, p in ipairs(r.points or {}) do if p[2] == GF.Inset then return true end end end end return false end)()'), True)
L.execute('''GFP = kid(WIN, "Frame"); GFP.WhoListingTab = kid(GFP, "Frame"); GFP.WhoListingTab.Icon = tex(GFP.WhoListingTab, nil, 8197123)
GFP.BrowsingTab = kid(GFP, "Frame"); GFP.BrowsingTab.Icon = tex(GFP.BrowsingTab, nil, 8197095)
GFP.ListingTab = kid(GFP, "Frame"); GFP.ListingTab.Icon = tex(GFP.ListingTab, nil, 8197096)''')
expect("Group Finder tabs by their real keys: Who people, Browsing magnifier, Listing eye", (E('AetherSkins_Windows.P3.TabGlyph(GFP.WhoListingTab)'), E('AetherSkins_Windows.P3.TabGlyph(GFP.BrowsingTab)'), E('AetherSkins_Windows.P3.TabGlyph(GFP.ListingTab)')), ("gl_people", "gl_search", "gl_eyeball"))
L.execute('''LN = kid(WIN, "Button"); LN.StateBorder = tex(LN, "Legacy-Tree-Frame-icon-frame-disable"); LN.SpendText = LN:CreateFontString()
LN.box = tex(LN, "Talents-Square-Box-c60"); AetherSkins_Windows.Contents(WIN)''')
expect("Legacy Tree rank box: Blizzard's dark square hidden", E('LN.box.alpha'), 0)
# switch off
# Spellbook (user 15:25): page fills stop at the title strip's gold line
L.execute("""
local W = AetherSkins_Windows
SBW = kid(UIParent, "Frame", "SpellbookTestWin"); W.chev[SBW] = {}
SBW.GetTop = function() return 800 end; SBW.GetEffectiveScale = function() return 1 end
SBP = kid(SBW, "Frame")
PGL = tex(SBP, "spellbook-Page-Left-C60"); PGL.GetTop = function() return 795 end; PGL.GetEffectiveScale = function() return 1 end
PGL.GetDrawLayer = function() return "BACKGROUND", 1 end
PGR = tex(SBP, "spellbook-Page-Right-C60"); PGR.GetTop = function() return 760 end; PGR.GetEffectiveScale = function() return 1 end
W.P3.BelowTitleTest = true
AetherSkins_Windows.Contents(SBW)
function TopPoint(o) for _, p in ipairs(o.points or {}) do if p[1] == "TOP" then return p[2] == SBW and p[5] end end return nil end
function FillOf(par) for _, r in ipairs(par.regs) do if r.texture == "Interface\\\\Buttons\\\\WHITE8x8" or (r.texture and tostring(r.texture):find("WHITE")) then return r end end end
""")
expect("page starting inside the title strip: our black stops at the gold line", E('(function() for _, r in ipairs(SBP.regs) do if r ~= PGL and r ~= PGR and r.points then local y = TopPoint(r); if y then return y end end end end)()'), -23)
expect("page already below the strip: left as Blizzard placed it", E('(function() local n = 0 for _, r in ipairs(SBP.regs) do if r ~= PGL and r ~= PGR and r.points and TopPoint(r) then n = n + 1 end end return n end)()'), 1)
expect("everything wrapped: no errors marked", E('(function() for k, v in pairs(AetherSkins_Windows.done) do if v == "failed" then return false end end return true end)()'), True)
# Forever gives BM row 5 -> 7 an extra edge back UP over the real arrow
# (dump b160: 9 arrows, 8 on the tree; user 16:46): up arrows are hidden
L.execute(r"""
local function btn(y) local b = kid(WIN, "Button"); b.GetCenter = function() return 100, y end; return b end
local function arrow(sy, ey)
  local a = kid(WIN, "Frame"); a.Line = tex(a); a.ArrowHead = tex(a, "talents-arrow-head-gray")
  a.alpha = 1; a.SetAlpha = function(s, v) s.alpha = v end
  a.startButton, a.endButton = btn(sy), btn(ey)
  return a
end
DOWN = arrow(500, 400); UP = arrow(400, 500)
""")
L.execute('AetherSkins_Windows.P2.Arrow(DOWN.ArrowHead, "gray"); AetherSkins_Windows.P2.Arrow(UP.ArrowHead, "gray")')
expect("talent arrow pointing down the tree: shown", E('DOWN.alpha'), 1)
expect("talent arrow pointing back up (Forever's extra edge): hidden", E('UP.alpha'), 0)
L.execute('UP.startButton, UP.endButton = DOWN.startButton, DOWN.endButton; AetherSkins_Windows.P2.Arrow(UP.ArrowHead, "gray")')
expect("pooled arrow reused for a downward link: shown again", E('UP.alpha'), 1)
print("ALL OK" if ok else "FAILED"); sys.exit(0 if ok else 1)
