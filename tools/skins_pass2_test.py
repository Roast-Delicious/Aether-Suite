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
  return t
end
CreateColor = function(r, g, b, a) return {r, g, b, a} end
local function kid(parent, kind, name) local f = CreateFrame(kind, name, parent); f.kind = kind; addmethods(f); return f end
local function tex(owner, atlas, file)
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
expect("not taken (no points): navy frame and navy icon", (border('NNONE'), E('NNONE.Icon.desat')), ((0.24, 0.35, 0.55), True))
expect("locked: gray", border('NLOCK'), (0.27, 0.29, 0.33))
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
expect("spec icon: gold on navy (desaturated, gold, added)", E('SPEC.icon.desat == true and SPEC.icon.vc[2] == 0.69 and SPEC.icon.blend == "ADD"'), True)
expect("spec ring blue, box navy", E('SPEC.MainRing.vc[3] == 1 and SPEC.TextBackground.vc[3] == 0.52'), True)
# spellbook
expect("trainable spell: Blizzard shadow faded, our glow shown", E('SPELL.Button.TrainableShadow.alpha == 0 and (function() for _, r in ipairs(SPELL.Button.regs) do if r.texture and r.texture:find("glow_sq") then return r.shown end end end)()'), True)
expect("spell frame blue", E('SPELL.Button.Border.vc[3] == 1'), True)
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
# switch off
expect("everything wrapped: no errors marked", E('(function() for k, v in pairs(AetherSkins_Windows.done) do if v == "failed" then return false end end return true end)()'), True)
print("ALL OK" if ok else "FAILED"); sys.exit(0 if ok else 1)
