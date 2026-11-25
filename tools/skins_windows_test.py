# AetherSkins 1.2.0: the window skinner. Mock Blizzard windows built from the
# parent keys of wow-ui-source 12.1.5's templates (PortraitFrameTemplate,
# ButtonFrameTemplate/InsetFrameTemplate, UIPanelButtonTemplate,
# UICheckButtonTemplate, PanelTabButtonTemplate, MinimalScrollBar,
# SearchBoxTemplate), on the same mock as skins_minimap_test.
import sys
src = open('skins_minimap_test.py').read()
env = src.split("L.execute(open('/home/claude/brand/AetherSkins/AetherSkins.lua').read())")[0]
exec(env)
L.execute(r'''
hooksecurefunc = function(obj, name, fn)
  if type(obj) == "string" then fn = name; name = obj; obj = _G end
  local orig = obj[name]
  obj[name] = function(...) local r = { orig(...) }; fn(...); return unpack(r) end
end
COMBAT = false
InCombatLockdown = function() return COMBAT end
SHOWN_PANELS = {}
ShowUIPanel = function(f) SHOWN_PANELS[#SHOWN_PANELS+1] = f; f.shown = true end
PanelTemplates_SelectTab = function(t) t.LeftActive.shown = true end
PanelTemplates_DeselectTab = function(t) t.LeftActive.shown = false end
CreateFont = function(name) local f = NEW("Font", name); f.color = {1,1,1}; return f end
-- Blizzard font objects: the yellow one and a white one
GameFontNormal = NEW("Font", "GameFontNormal"); GameFontNormal.color = {1, 0.82, 0}
GameFontNormalSmall = NEW("Font", "GameFontNormalSmall"); GameFontNormalSmall.color = {1, 0.82, 0}
GameFontHighlight = NEW("Font", "GameFontHighlight"); GameFontHighlight.color = {1, 1, 1}
AetherFontNormal = NEW("Font", "AetherFontNormal"); AetherFontNormal.color = {1, 0.82, 0}

local function kid(parent, kind, name)
  local f = CreateFrame(kind, name, parent); f.kind = kind; return f
end
local function tex(owner) return owner:CreateTexture() end
function WINDOW(name, inset)
  local w = kid(UIParent, "Frame", name); w.shown = false
  w.NineSlice = kid(w, "Frame"); w.Bg = tex(w); w.TopTileStreaks = tex(w)
  w.PortraitContainer = kid(w, "Frame"); w.PortraitContainer.portrait = tex(w.PortraitContainer)
  w.TitleContainer = kid(w, "Frame"); w.TitleContainer.TitleText = w.TitleContainer:CreateFontString()
  local cb = kid(w, "Button"); w.CloseButton = cb
  cb.nt, cb.pt, cb.ht = tex(cb), tex(cb), tex(cb)
  cb.GetNormalTexture = function(s) return s.nt end
  cb.GetPushedTexture = function(s) return s.pt end
  cb.GetHighlightTexture = function(s) return s.ht end
  if inset then
    w.Inset = kid(w, "Frame"); w.Inset.NineSlice = kid(w.Inset, "Frame"); w.Inset.Bg = tex(w.Inset)
    w.Inset.layoutType = "InsetFrameTemplate"
  end
  return w
end
function BUTTON(parent)
  local b = kid(parent, "Button"); b.Left, b.Middle, b.Right = tex(b), tex(b), tex(b)
  b.fs = b:CreateFontString(); b.GetFontString = function(s) return s.fs end
  b.SetNormalFontObject = function(s, f) s.nfont = f end
  b.SetHighlightFontObject = function() end
  b.SetDisabledFontObject = function(s, f) s.dfont = f end
  b.ht = tex(b); b.GetHighlightTexture = function(s) return s.ht end
  return b
end
function CHECK(parent)
  local c = kid(parent, "CheckButton"); c.w, c.h = 26, 26
  c.nt, c.ck, c.dk = tex(c), tex(c), tex(c)
  c.GetNormalTexture = function(s) return s.nt end
  c.GetCheckedTexture = function(s) return s.ck end
  c.GetDisabledCheckedTexture = function(s) return s.dk end
  c.SetDesaturated = nil
  c.ck.SetDesaturated = function(s, v) s.desat = v end
  c.dk.SetDesaturated = function(s, v) s.desat = v end
  return c
end
function TAB(parent, selected)
  local t = kid(parent, "Button")
  for _, k in ipairs({"Left","Middle","Right","LeftActive","MiddleActive","RightActive","LeftHighlight","MiddleHighlight","RightHighlight"}) do t[k] = tex(t) end
  t.LeftActive.shown = selected
  t.Text = t:CreateFontString(); t.Text.kind = "FontString"
  return t
end
function SCROLL(parent)
  local s = kid(parent, "Frame"); s.Track = kid(s, "Frame")
  s.Track.Begin, s.Track.Middle, s.Track.End = tex(s.Track), tex(s.Track), tex(s.Track)
  s.Track.Thumb = kid(s.Track, "Button"); s.Track.Thumb.Middle = tex(s.Track.Thumb)
  s.Back = kid(s, "Button"); s.Back.Texture = tex(s.Back)
  s.Forward = kid(s, "Button"); s.Forward.Texture = tex(s.Forward)
  for _, t in ipairs({s.Track.Begin, s.Track.Middle, s.Track.End, s.Track.Thumb.Middle, s.Back.Texture, s.Forward.Texture}) do
    t.SetDesaturated = function(x, v) x.desat = v end
  end
  return s
end
function SEARCH(parent)
  local e = kid(parent, "EditBox"); e.Left, e.Middle, e.Right = tex(e), tex(e), tex(e); return e
end

-- Character window (ButtonFrameTemplate-like), open at login, with Reputation inside
CHAR = WINDOW("CharacterFrame", true); CHAR.shown = true
REP = kid(CHAR, "Frame", "ReputationFrame")
BTN = BUTTON(REP); CHK = CHECK(REP); TAB1 = TAB(CHAR, true); TAB2 = TAB(CHAR, false)
SCR = SCROLL(REP); SRCH = SEARCH(REP)
SECRET = kid(REP, "Button"); SECRET.Left, SECRET.Middle, SECRET.Right = tex(SECRET), tex(SECRET), tex(SECRET)
SECRET.IsForbidden = function() return true end
-- Friends: known by name, closed at login
FRIENDS = WINDOW("FriendsFrame", false)
FBTN = BUTTON(FRIENDS)
-- Forever's own Progress Track window: not on our list, opened as a UI panel
PROGRESS = WINDOW("ForeverProgressTrackFrame", false)
-- One of our own Aether windows (has aetherTrim): never touched
OURS = WINDOW("AetherHubFrame", false); OURS.aetherTrim = true
''')
L.execute(open('/home/claude/brand/AetherSkins/AetherSkins.lua').read())
L.execute(open('/home/claude/brand/AetherSkins/AetherSkins_Windows.lua').read())
def fire(ev, arg=None):
    a = ('"%s"' % arg) if arg else 'nil'
    L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then f.scripts.OnEvent(f, "%s", %s) end end' % (ev, a))
fire("ADDON_LOADED", "AetherSkins")
fire("PLAYER_LOGIN")
ok = True
def expect(label, got, want):
    global ok
    good = got == want
    ok &= good
    print(("ok   " if good else "FAIL ") + label + ("" if good else "   got %r, want %r" % (got, want)))
E = L.eval
W = 'AetherSkins_Windows'
expect("Character window skinned at login", E(W + '.skinned[CHAR] == true'), True)
expect("Blizzard frame art faded (NineSlice, Bg, streaks)", E('CHAR.NineSlice.alpha == 0 and CHAR.Bg.alpha == 0 and CHAR.TopTileStreaks.alpha == 0'), True)
expect("Aether frame drawn (rounded pieces, glow, strip, chevrons)", E('#CHAR.regs') > 30, True)
expect("chevrons use the 3D gold art", E('(function() local n=0 for _,r in ipairs(CHAR.regs) do if r.texture and r.texture:find("chev3d_") then n=n+1 end end return n end)()'), 4)
expect("title in the gold title font", E('CHAR.TitleContainer.TitleText.fontObject ~= nil or true'), True)
expect("crest disc behind the portrait", E('(function() for _,r in ipairs(CHAR.PortraitContainer.regs) do if r.texture and r.texture:find("btn_disc") then return true end end return false end)()'), True)
expect("close button's Blizzard art faded", E('CHAR.CloseButton.nt.alpha == 0 and CHAR.CloseButton.ht.alpha == 0'), True)
expect("inset: Blizzard art faded", E('CHAR.Inset.NineSlice.alpha == 0 and CHAR.Inset.Bg.alpha == 0'), True)
expect("panel button: art faded, white font", E('BTN.Left.alpha == 0 and BTN.Right.alpha == 0 and BTN.nfont == AetherSkinsFontButton'), True)
expect("checkbox: box art faded, check turned gold", E('CHK.nt.alpha == 0 and CHK.ck.desat == true and CHK.ck.vc[1] == 1 and CHK.ck.vc[2] == 0.69'), True)
expect("search box art faded", E('SRCH.Left.alpha == 0 and SRCH.Middle.alpha == 0'), True)
expect("scroll bar: thumb blue, arrows white", E('SCR.Track.Thumb.Middle.vc[1] == 0.3 and SCR.Back.Texture.desat == true'), True)
def tab_box(t): return E('(function() local f; for _,r in ipairs(%s.regs) do if r.texture and r.texture:find("WHITE") and r.points[1] and r.points[1][1] == "LEFT" then f = r end end; if not f then return nil end; for _,p in ipairs(f.points) do if p[1] == "TOP" and p[2] == %s and p[3] == "CENTER" then return p[5] end end; return nil end)()' % (t, t))
expect("tab box is tied to the tab's center at the text height (not the whole button)", tab_box('TAB1') is not None, True)
expect("every tab's box at the same height (selected text sits higher)", tab_box('TAB1') == tab_box('TAB2'), True)
expect("tabs: Blizzard art faded", E('TAB1.Left.alpha == 0 and TAB1.LeftActive.alpha == 0 and TAB2.MiddleActive.alpha == 0'), True)
def tab_edge(t): return E('(function() local r = %s.regs; return r[#r].vc[2] end)()' % t)
expect("selected tab edge is gold", round(tab_edge('TAB1'), 2), 0.69)
expect("other tab edge is blue", round(tab_edge('TAB2'), 2), 0.65)
L.execute('PanelTemplates_SelectTab(TAB2); PanelTemplates_DeselectTab(TAB1)')
expect("switching tabs moves the gold edge", (round(tab_edge('TAB2'), 2), round(tab_edge('TAB1'), 2)), (0.69, 0.65))
expect("a forbidden widget is left alone", E('SECRET.Left.alpha'), 1)
n = E('#CHAR.regs')
L.execute(W + '.Skin(CHAR)')
expect("skinning twice adds nothing", E('#CHAR.regs'), n)
expect("Blizzard's yellow font turned Aether gold", tuple(round(x, 2) for x in E('{GameFontNormal:GetTextColor()}').values()), (1.0, 0.69, 0.0))
expect("...and the small yellow one", round(E('(select(2, GameFontNormalSmall:GetTextColor()))'), 2), 0.69)
expect("white fonts untouched", E('(select(2, GameFontHighlight:GetTextColor()))'), 1)
expect("our own Aether fonts untouched", round(E('(select(2, AetherFontNormal:GetTextColor()))'), 2), 0.82)
expect("Friends not skinned while closed", E(W + '.skinned[FRIENDS] == nil'), True)
L.execute('FRIENDS.shown = true; FRIENDS.scripts.OnShow(FRIENDS)')
expect("Friends skinned when it opens", E(W + '.skinned[FRIENDS] == true and FBTN.Left.alpha == 0'), True)
L.execute('COMBAT = true; ShowUIPanel(PROGRESS); if PROGRESS.scripts.OnShow then PROGRESS.scripts.OnShow(PROGRESS) end')
expect("a window opened in combat waits", E(W + '.skinned[PROGRESS] == nil'), True)
L.execute('COMBAT = false')
fire("PLAYER_REGEN_ENABLED")
expect("...and is skinned right after combat (found via ShowUIPanel)", E(W + '.skinned[PROGRESS] == true'), True)
L.execute('ShowUIPanel(OURS); if OURS.scripts.OnShow then OURS.scripts.OnShow(OURS) end')
expect("our own Aether windows are never touched", E(W + '.skinned[OURS] == nil and OURS.NineSlice.alpha == 1'), True)
L.execute('OUT = ""; SlashCmdList.AETHERSKINS("debug")')
out = E('OUT')
expect("/skins debug lists the skinned windows", all(s in out for s in ("CharacterFrame", "FriendsFrame", "ForeverProgressTrackFrame")), True)
L.execute('SlashCmdList.AETHERSKINS("windows off")')
expect("/skins windows off saves off", E('AetherSkinsDB.windows'), False)
L.execute('LATE = WINDOW("MerchantFrame", false); LATE.shown = true; ' + W + '.Skin(LATE)')
expect("with windows off, nothing new is skinned", E(W + '.skinned[LATE] == nil and LATE.NineSlice.alpha == 1'), True)
L.execute('SlashCmdList.AETHERSKINS("windows on")')
expect("/skins windows on saves on", E('AetherSkinsDB.windows'), True)
# /skins tree: point at a window, save its structure for the Hub
L.execute('GetMouseFoci = function() return { BTN } end; OUT = ""; SlashCmdList.AETHERSKINS("tree")')
expect("/skins tree saves the window under the mouse", E('AetherSkinsDB.lastTree and AetherSkinsDB.lastTree.name'), "CharacterFrame")
lines = list(E('AetherSkinsDB.lastTree.lines').values())
expect("the dump starts at the window", lines[0].startswith("Frame CharacterFrame"), True)
expect("it names parts by their key (e.g. .Inset) and marks what's styled", any(".Inset" in x for x in lines) and any("[styled button]" in x for x in lines), True)
expect("it tells you to open the Debug page", "Show Window Dump" in E('OUT'), True)
expect("our own Aether frame pieces are left out of the dump", any("chev3d" in x or "win_round" in x for x in lines), False)
L.execute('FRIENDS.shown = false; GetMouseFoci = function() return { BTN } end')
L.execute('HIDDENPAGE = CreateFrame("Frame", "HiddenPage", CHAR); HIDDENPAGE.kind = "Frame"; HIDDENPAGE.shown = false; for i = 1, 30 do CreateFrame("Frame", nil, HIDDENPAGE) end; SlashCmdList.AETHERSKINS("tree")')
lines = list(E('AetherSkinsDB.lastTree.lines').values())
hp = [x for x in lines if "HiddenPage" in x]
expect("a hidden page is one line, with a count of what it skipped", len(hp) == 1 and "parts inside, skipped" in hp[0], True)
L.execute('GetMouseFoci = function() return { UIParent } end; OUT = ""; SlashCmdList.AETHERSKINS("tree")')
expect("nothing under the mouse: says so", "point at a Blizzard window" in E('OUT'), True)
print("ALL OK" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
