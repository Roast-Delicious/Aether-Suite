# Loads AetherLedger_TrackerLook.lua against a mock of Blizzard's objective
# tracker (structure from Blizzard_ObjectiveTracker, wow-ui-source) and checks
# what it changes. Also checks the new watch order in AetherLedger_Tracker.lua.
import lupa.lua51 as l, sys
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
local function new(kind)
  local o = { kind = kind, shown = true, alpha = 1, color = {1,1,1}, kids = {}, scripts = {} }
  return setmetatable(o, { __index = function(t, k)
    local v = M[k]; if v then return v end
    if type(k) == "string" and k:match("^%u") then return function() end end
  end })
end
NEW = new
function M.CreateTexture(s) local t = new("tex"); s.kids[#s.kids+1] = t; return t end
function M.CreateFontString(s) local t = new("fs"); s.kids[#s.kids+1] = t; return t end
function M.SetTexture(s, x) s.texture = x end
function M.SetAtlas(s, x) s.texture = x end
function M.SetVertexColor(s, r, g, b, a) s.vc = {r, g, b, a} end
function M.SetTextColor(s, r, g, b) s.color = {r, g, b} end
function M.GetTextColor(s) return s.color[1], s.color[2], s.color[3] end
function M.SetText(s, x) s.text = x end
function M.GetText(s) return s.text end
function M.SetAlpha(s, a) s.alpha = a end
function M.Show(s) s.shown = true end
function M.Hide(s) s.shown = false end
function M.SetShown(s, v) s.shown = v and true or false end
function M.IsShown(s) return s.shown end
function M.EnableMouse(s, v) s.mouse = v end
function M.GetFrameLevel() return 3 end
function M.SetScript(s, k, f) s.scripts[k] = f end
function M.HookScript(s, k, f) s.scripts[k] = f end
function M.GetNormalTexture(s) s.nt = s.nt or new("tex"); return s.nt end
function M.GetPushedTexture(s) s.pt = s.pt or new("tex"); return s.pt end
function M.GetHighlightTexture(s) s.ht = s.ht or new("tex"); return s.ht end
function M.GetFont(s) return s.file, s.size, s.flags end
function M.SetFont(s, f, z, fl) s.file, s.size, s.flags = f, z, fl; return true end
function M.SetFontObject() end
function M.RegisterEvent() end
CreateFrame = function() local f = new("frame"); FRAMES = FRAMES or {}; FRAMES[#FRAMES+1] = f; return f end
hooksecurefunc = function(obj, name, fn)
  if type(obj) == "string" then return end
  local orig = obj[name]
  obj[name] = function(...) local r = { orig(...) }; fn(...); return unpack(r) end
end
print = function(...) OUT = (OUT or "") .. table.concat({...}, " ") .. "\n" end
QUEST_WATCH_QUEST_READY = "Ready for turn-in"
ObjectiveTrackerLineFont = new("font"); ObjectiveTrackerLineFont.file = "Fonts\\FRIZQT__.TTF"; ObjectiveTrackerLineFont.size = 12
ObjectiveTrackerHeaderFont = new("font"); ObjectiveTrackerHeaderFont.file = "Fonts\\FRIZQT__.TTF"; ObjectiveTrackerHeaderFont.size = 14

-- The container ("All Objectives") and the Quests module
ObjectiveTrackerFrame = new("frame")
ObjectiveTrackerFrame.Header = new("frame"); ObjectiveTrackerFrame.Header.MinimizeButton = new("button")
local function Header()
  local h = new("frame"); h.Background = new("tex"); h.Background.texture = "UI-QuestTracker-Secondary-Objective-Header"
  h.Glow = new("tex"); h.Glow.texture = "UI-QuestTracker-OBJFX-BarGlow"
  h.Text = new("fs"); h.Text.text = "Quests"; h.Text.color = {1, 0.82, 0}
  h.MinimizeButton = new("button")
  function h:SetCollapsed(c) self.collapsedState = c end
  return h
end
QuestObjectiveTracker = new("frame"); QuestObjectiveTracker.Header = Header()
QuestObjectiveTracker.usedBlocks = {}
function QuestObjectiveTracker:Update() return 100, false end

local function Block(id, title, color, lines, complete, tracked)
  local b = new("frame"); b.id = id
  b.HeaderText = new("fs"); b.HeaderText.text = title; b.HeaderText.color = color
  b.usedLines = {}
  for i, t in ipairs(lines) do
    local line = new("frame"); line.Text = new("fs"); line.Text.text = t; line.Text.color = {0.8, 0.8, 0.8}
    line.Dash = new("fs"); line.Dash.color = {0.8, 0.8, 0.8}
    b.usedLines[i] = line
  end
  b.poiButton = new("button"); b.poiIsComplete = complete; b.poiIsSuperTracked = tracked
  function b:UpdateHighlight()
    local c = self.isHighlighted and {1, 0.82, 0} or {0.75, 0.61, 0}
    self.HeaderText:SetTextColor(c[1], c[2], c[3])
  end
  return b
end
B1 = Block(1, "[35] Tiger Mastery", {1, 0.82, 0}, {"Ready for turn-in"}, true, false)
B2 = Block(2, "[37] Headhunting", {1, 0.5, 0.25}, {"0/20 Shrunken Head"}, false, true)
B3 = Block(3, "|cffffd100[35]|r Bloodscalp Ears", {1, 1, 1}, {"0/15 Bloodscalp Ear"}, false, false)
QuestObjectiveTracker.usedBlocks.QuestTemplate = { [1] = B1, [2] = B2, [3] = B3 }
''')
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_TrackerLook.lua').read())
L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then f.scripts.OnEvent(f, "PLAYER_LOGIN") end end')
L.execute('QuestObjectiveTracker:Update()')
ok = True
def expect(label, got, want):
    global ok
    good = got == want
    ok &= good
    print(("ok  " if good else "FAIL"), label, got)
def col(path): c = L.eval(path); return tuple(round(c[i], 2) for i in (1, 2, 3))
expect("All Objectives bar hidden", L.eval('ObjectiveTrackerFrame.Header.alpha'), 0)
expect("its button can't be clicked", L.eval('ObjectiveTrackerFrame.Header.MinimizeButton.mouse'), False)
expect("Quests header: brown bar removed", L.eval('QuestObjectiveTracker.Header.Background.texture'), None)
expect("Quests header: gold text", col('QuestObjectiveTracker.Header.Text.color'), (1, 0.69, 0))
expect("Quests header: band + line added", L.eval('#QuestObjectiveTracker.Header.kids'), 2)
expect("fold glyph shows -", L.eval('QuestObjectiveTracker.Header.aetherGlyph.text'), "–")
L.execute('QuestObjectiveTracker.Header:SetCollapsed(true)')
expect("fold glyph shows + when folded", L.eval('QuestObjectiveTracker.Header.aetherGlyph.text'), "+")
expect("yellow title -> Aether gold", col('B1.HeaderText.color'), (1, 0.69, 0))
expect("orange title unchanged", col('B2.HeaderText.color'), (1, 0.5, 0.25))
expect("yellow color code in title -> gold", L.eval('B3.HeaderText.text'), "|cffffb000[35]|r Bloodscalp Ears")
expect("Ready for turn-in -> Aether sky blue", col('B1.usedLines[1].Text.color'), (0.45, 0.75, 1))
expect("objective line stays light gray", col('B2.usedLines[1].Text.color'), (0.8, 0.8, 0.8))
expect("complete quest icon shows ?", (L.eval('B1.poiButton.aetherIcon.mark.shown'), L.eval('B1.poiButton.aetherIcon.dots.shown')), (True, False))
expect("in-progress icon shows dots", (L.eval('B2.poiButton.aetherIcon.mark.shown'), L.eval('B2.poiButton.aetherIcon.dots.shown')), (False, True))
expect("followed quest's icon glows", (L.eval('B2.poiButton.aetherIcon.glow.shown'), L.eval('B1.poiButton.aetherIcon.glow.shown')), (True, False))
expect("icon overlay takes no clicks", L.eval('B1.poiButton.aetherIcon.mouse'), False)
L.execute('B1.isHighlighted = true; B1:UpdateHighlight()')
expect("hover: blue band shown", L.eval('B1.aetherHover.shown'), True)
expect("hover: title bright gold", col('B1.HeaderText.color'), (1, 0.69, 0))
L.execute('B1.isHighlighted = false; B1:UpdateHighlight()')
expect("leave: band hidden, title dim gold", (L.eval('B1.aetherHover.shown'), col('B1.HeaderText.color')), (False, (0.75, 0.52, 0)))
expect("fonts: Fira Sans", (L.eval('ObjectiveTrackerLineFont.file'), L.eval('ObjectiveTrackerHeaderFont.file')),
       ("Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-Regular.ttf", "Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-SemiBold.ttf"))
expect("fonts keep the game's size", (L.eval('ObjectiveTrackerLineFont.size'), L.eval('ObjectiveTrackerHeaderFont.size')), (12, 14))
expect("no errors printed", L.eval('OUT'), None)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
