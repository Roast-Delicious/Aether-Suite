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
CreateFrame = function(kind, name, parent) local f = new("frame"); f.parent = parent; f.GetParent = function(self) return self.parent end; FRAMES = FRAMES or {}; FRAMES[#FRAMES+1] = f; return f end
hooksecurefunc = function(obj, name, fn)
  if type(obj) == "string" then return end
  local orig = obj[name]
  obj[name] = function(...) local r = { orig(...) }; fn(...); return unpack(r) end
end
print = function(...) OUT = (OUT or "") .. table.concat({...}, " ") .. "\n" end
QUEST_WATCH_QUEST_READY = "Ready for turn-in"
NOW = 100; GetTime = function() return NOW end
PLAYS = {}
function M.CreateAnimationGroup(s)
  local ag = { owner = s, anims = {}, scripts = {} }
  function ag:CreateAnimation(kind) local a = { kind = kind }
    function a:SetDuration(d) self.dur = d end
    function a:SetScaleFrom(x) self.from = x end
    function a:SetScaleTo(x) self.to = x end
    function a:SetFromAlpha(x) self.afrom = x end
    function a:SetToAlpha(x) self.ato = x end
    function a:SetOrigin() end
    function a:SetSmoothing(v) self.smooth = v end
    self.anims[#self.anims+1] = a; return a end
  function ag:Play() PLAYS[#PLAYS+1] = self end
  function ag:Stop() end
  function ag:SetScript(k, f) self.scripts[k] = f end
  return ag
end
function M.GetCenter(s) return 1882, 493 end
function M.GetWidth(s) return 32 end
function M.GetEffectiveScale(s) return 1 end
function M.GetRegions(s) s.r1 = s.r1 or new("tex"); s.r2 = s.r2 or new("tex"); return s.r1, s.r2 end
function M.GetChildren(s) return end
UIParent = new("frame")
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
expect("orange title: the map's lighter orange (user, Nov 25 14:32)", col("B2.HeaderText.color"), (1, 0.59, 0.33))
expect("yellow color code in title -> gold", L.eval('B3.HeaderText.text'), "|cffffb000[35]|r Bloodscalp Ears")
expect("Ready for turn-in -> Aether Blue", col('B1.usedLines[1].Text.color'), (0.3, 0.65, 1))
expect("objective line stays light gray", col('B2.usedLines[1].Text.color'), (0.8, 0.8, 0.8))
expect("complete quest icon shows ?", (L.eval('AetherLedger_TrackerIconFor(B1.poiButton).mark.shown'), L.eval('AetherLedger_TrackerIconFor(B1.poiButton).dots.shown')), (True, False))
expect("in-progress icon shows dots", (L.eval('AetherLedger_TrackerIconFor(B2.poiButton).mark.shown'), L.eval('AetherLedger_TrackerIconFor(B2.poiButton).dots.shown')), (False, True))
expect("followed quest's icon glows", (L.eval('AetherLedger_TrackerIconFor(B2.poiButton).glow.shown'), L.eval('AetherLedger_TrackerIconFor(B1.poiButton).glow.shown')), (True, False))
expect("icon overlay takes no clicks", L.eval('AetherLedger_TrackerIconFor(B1.poiButton).mouse'), False)
expect("icon overlay hangs off the block, not the animated button (no giant pop)",
       L.eval('AetherLedger_TrackerIconFor(B1.poiButton):GetParent() == B1 and AetherLedger_TrackerIconFor(B1.poiButton):GetParent() ~= B1.poiButton'), True)
L.execute('B1.isHighlighted = true; B1:UpdateHighlight()')
expect("hover: blue band shown", L.eval('B1.aetherHover.shown'), True)
expect("hover: title bright gold", col('B1.HeaderText.color'), (1, 0.69, 0))
L.execute('B1.isHighlighted = false; B1:UpdateHighlight()')
expect("leave: band hidden, title dim gold", (L.eval('B1.aetherHover.shown'), col('B1.HeaderText.color')), (False, (0.75, 0.52, 0)))
expect("fonts: Fira Sans", (L.eval('ObjectiveTrackerLineFont.file'), L.eval('ObjectiveTrackerHeaderFont.file')),
       ("Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-Regular.ttf", "Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-SemiBold.ttf"))
expect("fonts keep the game's size", (L.eval('ObjectiveTrackerLineFont.size'), L.eval('ObjectiveTrackerHeaderFont.size')), (12, 14))
expect("Blizzard's own icon art is invisible (nothing to balloon)", (L.eval('B1.poiButton.r1.alpha'), L.eval('B1.poiButton.r2.alpha')), (0, 0))
expect("no zoom on a normal tracker refresh", L.eval('#PLAYS'), 0)
def fire(ev, a1, a2='nil'):
    L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then f.scripts.OnEvent(f, "%s", %s, %s) end end' % (ev, a1, a2))
fire("QUEST_ACCEPTED", 2)
L.execute('QuestObjectiveTracker:Update()')
expect("accepted quest: its icon zooms in once", L.eval('#PLAYS'), 1)
expect("zoom in: from 25x to its spot, fading in, 0.6 s",
       (L.eval('PLAYS[1].owner == AetherLedger_TrackerIconFor(B2.poiButton)'), L.eval('PLAYS[1].anims[1].from'), L.eval('PLAYS[1].anims[1].to'),
        L.eval('PLAYS[1].anims[1].dur'), L.eval('PLAYS[1].anims[2].afrom'), L.eval('PLAYS[1].anims[2].ato')), (True, 25, 1, 0.6, 0, 1))
L.execute('QuestObjectiveTracker:Update()')
expect("...and only once (later refreshes don't replay it)", L.eval('#PLAYS'), 1)
fire("QUEST_ACCEPTED", 7, 3)          # older clients: (logIndex, questID)
NOWSET = L.execute('NOW = 110'); L.execute('QuestObjectiveTracker:Update()')
expect("too long after accepting: no zoom", L.eval('#PLAYS'), 1)
fire("QUEST_TURNED_IN", 1)
expect("handed in: a copy of its icon swells and fades", L.eval('#PLAYS'), 2)
expect("hand-in copy: above everything on UIParent, 1x -> 25x, fades out",
       (L.eval('PLAYS[2].owner.parent == UIParent'), L.eval('PLAYS[2].anims[1].from'), L.eval('PLAYS[2].anims[1].to'),
        L.eval('PLAYS[2].anims[2].afrom'), L.eval('PLAYS[2].anims[2].ato'), L.eval('PLAYS[2].owner.mouse')), (True, 1, 25, 1, 0, False))
fire("QUEST_TURNED_IN", 999)
expect("hand-in of an untracked quest: nothing", L.eval('#PLAYS'), 2)
# A finished quest handed in elsewhere (B1, ready): "Ready for turn-in: Orgrimmar",
# still Aether blue, with a gold divider line above it.
L.execute('''
AetherLedger_Tracker = { ElsewhereZone = function(id) if id == 1 then return "Orgrimmar" end end }
B1.usedLines[1].Text.text = "Ready for turn-in"
B1.GetTop = function() return 300 end; B2.GetTop = function() return 340 end; B3.GetTop = function() return 260 end
B1.IsShown = function() return true end; B2.IsShown = function() return true end; B3.IsShown = function() return true end
QuestObjectiveTracker:Update()
''')
expect("hand-in elsewhere: Ready line names the zone", L.eval('B1.usedLines[1].Text.text'), "Ready for turn-in: Orgrimmar")
expect("...and stays Aether blue", col('B1.usedLines[1].Text.color'), (0.3, 0.65, 1))
L.execute('QuestObjectiveTracker:Update()')
expect("...without adding the zone twice", L.eval('B1.usedLines[1].Text.text'), "Ready for turn-in: Orgrimmar")
expect("hand-in elsewhere: blue check instead of the ?", (L.eval('AetherLedger_TrackerIconFor(B1.poiButton).check.shown'), L.eval('AetherLedger_TrackerIconFor(B1.poiButton).mark.shown')), (True, False))
div = L.eval('(function() for _,o in ipairs(B1.kids or {}) do if o.texture and tostring(o.texture):find("trk_line") then return o end end end)()')
expect("a gold divider line sits on the first hand-in quest", div is not None, True)
L.execute('AetherLedger_Tracker = { ElsewhereZone = function() end }; QuestObjectiveTracker:Update()')
expect("no hand-ins elsewhere: divider hidden", div.shown if div is not None else None, False)
expect("...and the ? is back", (L.eval('AetherLedger_TrackerIconFor(B1.poiButton).check.shown'), L.eval('AetherLedger_TrackerIconFor(B1.poiButton).mark.shown')), (False, True))
expect("no errors printed", L.eval('OUT'), None)
L.execute('B9 = { HeaderText = { color = {1, 0.1, 0.1} } }; B9.HeaderText.GetTextColor = function(s) return unpack(s.color) end; B9.HeaderText.SetTextColor = function(s, r, g, b) s.color = {r, g, b} end; AetherLedger_TrackerNameColor(B9.HeaderText)')
expect("red title: the map's lighter red", col("B9.HeaderText.color"), (1, 0.38, 0.34))
L.execute('B9.HeaderText:SetTextColor(1, 0.1, 0.1)')
expect("Blizzard sets the red again (tracker update, hover): ours comes back", col("B9.HeaderText.color"), (1, 0.38, 0.34))
L.execute('B9.HeaderText:SetTextColor(0.25, 0.75, 0.25)')
expect("...and a green (easy) title is left alone", col("B9.HeaderText.color"), (0.25, 0.75, 0.25))
L.execute('QUESTLOG_READY = 777; C_QuestLog = C_QuestLog or {}; C_QuestLog.GetNextWaypoint = function(q) return 1413, 0.5, 0.6 end; C_QuestLog.GetTitleForQuestID = function() return "Lost Crate" end; STARTED = nil; AetherLedger_Travel = AetherLedger_Travel or {}; AetherLedger_Travel.Start = function(d) STARTED = d end')
if L.eval('AetherLedger_GoToTurnIn ~= nil'):
    L.execute('AetherLedger_GoToTurnIn(777)')
    expect("click a ready quest: travel to the game's turn-in spot", L.eval('STARTED and STARTED.map == 1413 and STARTED.x == 0.5 and STARTED.qid == 777'), True)
    # hand-in in your own zone: no waypoint, but the "?" marker is on the map (user 16:27)
    L.execute("""C_QuestLog.GetNextWaypoint = function() return nil end; STARTED = nil
      C_Map = C_Map or {}; C_Map.GetBestMapForUnit = function() return 1454 end
      C_Map.GetMapInfo = function(m) return ({ [1454] = { name = "Orgrimmar", mapType = 3, parentMapID = 1414 }, [1414] = { name = "Kalimdor", mapType = 2 }, [1413] = { name = "The Barrens", mapType = 3 } })[m] end
      C_QuestLog.GetQuestsOnMap = function(m) if m == 1454 then return { { questID = 5, x = 0.1, y = 0.1 }, { questID = 777, x = 0.42, y = 0.37 } } end return {} end
      AetherLedger_GoToTurnIn(777)""")
    expect("no waypoint: the quest's map marker where you are", L.eval('STARTED and STARTED.map == 1454 and STARTED.x == 0.42 and STARTED.y == 0.37'), True)
    L.execute("""C_QuestLog.GetQuestsOnMap = function(m) if m == 1413 then return { { questID = 777, x = 0.6, y = 0.3 } } end return {} end
      AetherLedger_Zones = AetherLedger_Zones or {}; AetherLedger_Zones[777] = { 1454, 1413 }; STARTED = nil
      AetherLedger_GoToTurnIn(777)""")
    expect("...or on its hand-in zone's map (our data)", L.eval('STARTED and STARTED.map == 1413 and STARTED.x == 0.6'), True)
    L.execute("""C_QuestLog.GetQuestsOnMap = function() return {} end; STARTED = nil; LASTPRINT = nil
      local p = print; print = function(...) LASTPRINT = table.concat({...}, " ") end
      AetherLedger_GoToTurnIn(777); print = p""")
    expect("nothing known: says which zone it's handed in", (L.eval('STARTED'), "handed in in The Barrens" in (L.eval('LASTPRINT') or "")), (None, True))
    # unfinished quest (user Nov 27): its area on the map, home zone first
    L.execute("""C_QuestLog.GetQuestsOnMap = function(m) if m == 1454 then return { { questID = 778, x = 0.2, y = 0.7 } } end return {} end
      AetherLedger_Zones[778] = { 1454, 1413 }; STARTED = nil
      C_Map.GetBestMapForUnit = function() return 1413 end
      AetherLedger_GoToQuest(778)""")
    expect("unfinished quest: travel to its area (home zone's map)", L.eval('STARTED and STARTED.map == 1454 and STARTED.x == 0.2 and STARTED.name == "Quest: Lost Crate"'), True)
    L.execute("""C_QuestLog.GetQuestsOnMap = function() return {} end; STARTED = nil; LASTPRINT = nil
      local p = print; print = function(...) LASTPRINT = table.concat({...}, " ") end
      AetherLedger_GoToQuest(778); print = p""")
    expect("unfinished, nothing marked: says which zone it's in", (L.eval('STARTED'), "it's in Orgrimmar" in (L.eval('LASTPRINT') or "")), (None, True))
# Forever writes the difficulty color into the title as a code (user 16:53)
L.execute('B10 = { HeaderText = { color = {1, 1, 1}, text = "|cffff1a1a[60] Craftsman\'s Writ|r" } }; local h = B10.HeaderText; h.GetTextColor = function(s) return unpack(s.color) end; h.SetTextColor = function(s, r, g, b) s.color = {r, g, b} end; h.GetText = function(s) return s.text end; h.SetText = function(s, t) s.text = t end; AetherLedger_TrackerNameColor(h)')
expect("red written into the title: lighter red code", L.eval('B10.HeaderText.text'), "|cffff6058[60] Craftsman's Writ|r")
L.execute('B10.HeaderText:SetText("|cffff1a1a[60] Craftsman\'s Writ|r")')
expect("tracker writes the title again: lighter red comes back", L.eval('B10.HeaderText.text'), "|cffff6058[60] Craftsman's Writ|r")
expect("orange code: lighter orange", L.eval('AetherLedger_TrackerNameCodes("|cffff8020[38] X|r")'), "|cffff9654[38] X|r")
expect("gold and green codes left alone", L.eval('AetherLedger_TrackerNameCodes("|cff40bf40[31] Y|r |cffffb000Z|r")'), "|cff40bf40[31] Y|r |cffffb000Z|r")
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
