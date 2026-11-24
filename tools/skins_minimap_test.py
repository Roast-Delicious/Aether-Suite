# Loads AetherSkins.lua against a mock minimap (frame names from Blizzard's
# Minimap / MinimapCluster, wow-ui-source) and checks what it changes.
import lupa.lua51 as l, sys
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
local function new(kind, name)
  local o = { kind = kind, name = name, shown = true, alpha = 1, color = {1,1,1}, kids = {}, regs = {},
              scripts = {}, points = {}, w = 0, h = 0, scale = 1, level = 1, mouse = true }
  if name then _G[name] = o end
  return setmetatable(o, { __index = function(t, k)
    local v = M[k]; if v then return v end
    if type(k) == "string" and k:match("^%u") then return function() end end
  end })
end
NEW = new
function M.CreateTexture(s) local t = new("Texture"); t.parent = s; s.regs[#s.regs+1] = t; return t end
function M.CreateFontString(s) local t = new("FontString"); t.parent = s; s.regs[#s.regs+1] = t; return t end
function M.GetObjectType(s) return s.kind end
function M.GetRegions(s) return unpack(s.regs) end
function M.GetChildren(s) return unpack(s.kids) end
function M.GetParent(s) return s.parent end
function M.GetName(s) return s.name end
function M.GetDebugName(s) return s.name end
function M.SetTexture(s, x) s.texture = x end
function M.SetColorTexture(s) s.texture = "COLOR" end
function M.SetVertexColor(s, r, g, b, a) s.vc = {r, g, b, a} end
function M.SetTextColor(s, r, g, b) s.color = {r, g, b} end
function M.GetTextColor(s) return s.color[1], s.color[2], s.color[3] end
function M.SetAlpha(s, a) s.alpha = a end
function M.GetAlpha(s) return s.alpha end
function M.SetRotation(s, r) s.rot = r end
function M.Show(s) s.shown = true end
function M.Hide(s) s.shown = false end
function M.IsShown(s) return s.shown end
function M.EnableMouse(s, v) s.mouse = v end
function M.IsProtected(s) return s.protected or false end
function M.SetSize(s, w, h) s.w, s.h = w, h end
function M.SetWidth(s, w) s.w = w end
function M.SetHeight(s, h) s.h = h end
function M.GetWidth(s) return s.w end
function M.GetHeight(s) return s.h end
function M.GetSize(s) return s.w, s.h end
function M.GetCenter(s) return s.cx, s.cy end
function M.GetEffectiveScale(s) return s.scale end
function M.GetFrameLevel(s) return s.level end
function M.SetFrameLevel(s, v) s.level = v end
function M.SetPoint(s, ...) s.points[#s.points+1] = {...} end
function M.ClearAllPoints(s) s.points = {} end
function M.SetScript(s, k, f) s.scripts[k] = f end
function M.HookScript(s, k, f) s.scripts[k] = f end
function M.GetHighlightTexture(s) return s.hl end
function M.GetFont(s) return "Fonts\\FRIZQT__.TTF", 12, "" end
function M.SetFont(s, f) s.font = f end
CreateFrame = function(kind, name, parent)
  local f = new("Frame", name); f.parent = parent
  if parent then parent.kids[#parent.kids+1] = f; f.level = (parent.level or 1) + 1 end
  FRAMES = FRAMES or {}; FRAMES[#FRAMES+1] = f
  return f
end
hooksecurefunc = function(obj, name, fn)
  if type(obj) == "string" then local o = _G[obj]; _G[obj] = function(...) local r = {o(...)}; fn(...); return unpack(r) end; return end
  local orig = obj[name]
  obj[name] = function(...) local r = { orig(...) }; fn(...); return unpack(r) end
end
OUT = ""
print = function(...) OUT = OUT .. table.concat({...}, " ") .. "\n" end
strlower, strtrim = string.lower, function(s) return (s:gsub("^%s+", ""):gsub("%s+$", "")) end
TIMERS = {}; AFTER = {}
C_Timer = { NewTicker = function(t, f) TIMERS[#TIMERS+1] = f end, After = function(t, f) AFTER[#AFTER+1] = f end }
GAME = { 12, 0 }
GetGameTime = function() return GAME[1], GAME[2] end
DAY = true
C_DateAndTime = { IsDayTime = function() return DAY end }
GetCVarBool = function() return true end
CALENDAR = 0; ToggleCalendar = function() CALENDAR = CALENDAR + 1 end
SlashCmdList = {}
GameTooltip = setmetatable({ lines = {} }, { __index = function() return function() end end })

-- The minimap: 140 wide, center (1000, 700), Blizzard's ring art on it
UIParent = new("Frame", "UIParent")
Minimap = new("Frame", "Minimap"); Minimap.w, Minimap.h, Minimap.cx, Minimap.cy, Minimap.level = 140, 140, 1000, 700, 2
local border = Minimap:CreateTexture(); border.name = "MinimapCompassTexture"; MinimapCompassTexture = border
MinimapBackdrop = new("Frame", "MinimapBackdrop"); local mb = MinimapBackdrop:CreateTexture(); mb.name = "MinimapBorder"
MinimapCluster = new("Frame", "MinimapCluster")
MinimapCluster.BorderTop = MinimapCluster:CreateTexture(); MinimapCluster.BorderTop.name = "BorderTop"
MinimapCluster.BorderTop.parent = MinimapCluster; MinimapCluster.BorderTop.w, MinimapCluster.BorderTop.h = 175, 16
MinimapZoneText = NEW("FontString", "MinimapZoneText"); MinimapZoneText.color = {1, 0.82, 0}
TimeManagerClockButton = new("Frame", "TimeManagerClockButton"); TimeManagerClockButton:CreateTexture()
TimeManagerClockButton.cx, TimeManagerClockButton.cy, TimeManagerClockButton.w, TimeManagerClockButton.h, TimeManagerClockButton.level = 1065, 812, 40, 16, 6
TimeManagerClockButton.hl = TimeManagerClockButton:CreateTexture()
-- Forever's day/night icon: top-right on the ring (0.72R, 0.73R), 28 wide
local function Kid(parent, name, x, y, w, prot)
  local f = new("Button", name); f.parent = parent; parent.kids[#parent.kids+1] = f
  f.cx, f.cy, f.w, f.h, f.protected = 1000 + x, 700 + y, w, w, prot; return f
end
-- Forever's sun/moon: about 1 o'clock (57 deg), 1.08 map radii out, one level down
HOLDER = Kid(MinimapCluster, "ForeverHolder", 0, 0, 200)
DAYNIGHT = Kid(HOLDER, "ForeverDayNightButton", 41, 63, 30)
-- the zone bar's calendar and the small button under it: further out, left alone
CALBTN = Kid(MinimapCluster, "GameTimeFrame", 58, 101, 24)
-- the top bar: tracking (left), zone name, clock, calendar (right), all on one row
ZONEBTN = Kid(MinimapCluster, "MinimapZoneTextButton", -20, 112, 120); ZONEBTN.h = 16; ZONEBTN.level = 5
MinimapCluster.ZoneTextButton = ZONEBTN
TRACK = Kid(MinimapCluster, "MiniMapTracking", -92, 112, 20); TRACK.level = 5
ONEBTN = Kid(MinimapCluster, "ForeverIndicator", 58, 84, 18)
HUBBTN = Kid(Minimap, "AetherHubMinimapButton", -55, -48, 31)
PROT = Kid(MinimapCluster, "SomeProtectedButton", 48, 50, 26, true)
ZOOM = Kid(Minimap, "MinimapZoomIn", 76, -12, 24)
''')
L.execute(open('/home/claude/brand/AetherSkins/AetherSkins.lua').read())
def fire(ev):
    L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then f.scripts.OnEvent(f, "%s") end end' % ev)
fire("PLAYER_LOGIN")
ok = True
def expect(label, got, want):
    global ok
    good = got == want
    ok &= good
    print(("ok  " if good else "FAIL"), label, got)
def near(a, b, e=0.02): return abs(a - b) <= e
expect("no errors at login", L.eval('OUT'), "")
expect("Blizzard ring hidden", (L.eval('MinimapCompassTexture.alpha'), L.eval('MinimapBackdrop.regs[1].alpha')), (0, 0))
expect("ring made, 2K wide", near(L.eval('AetherSkinsMinimapRing.w'), 2 * 1.2821 * 70, 0.1), True)
expect("ring texture (day)", L.eval('AetherSkinsMinimapRing.lit.texture'), "Interface\\AddOns\\AetherSkins\\Media\\ring_day")
expect("four 3D chevrons, one texture per direction (not rotated)",
       [(L.eval('AetherSkinsMinimapRing.chevrons[%d].gold.texture' % i).split('\\')[-1], L.eval('AetherSkinsMinimapRing.chevrons[%d].gold.rot' % i)) for i in (1, 2, 3, 4)],
       [("chev3d_up", None), ("chev3d_right", None), ("chev3d_down", None), ("chev3d_left", None)])
expect("dark outlines rotated", [L.eval('AetherSkinsMinimapRing.chevrons[%d].dark.rot' % i) for i in (1, 2, 3, 4)],
       [None, -3.141592653589793 / 2, 3.141592653589793, 3.141592653589793 / 2])
expect("sun button on the ring at the top-right", [round(v, 1) for v in L.eval('{AetherSkinsDayNight.points[1][4], AetherSkinsDayNight.points[1][5]}').values()], [50.3, 51.4])
expect("sun icon, Aether gold", (L.eval('AetherSkinsDayNight.icon.texture'), tuple(round(v, 2) for v in list(L.eval('AetherSkinsDayNight.icon.vc').values())[:3])),
       ("Interface\\AddOns\\AetherSkins\\Media\\ico_sun", (1, 0.69, 0)))
expect("Forever's day/night icon hidden", (L.eval('DAYNIGHT.alpha'), L.eval('DAYNIGHT.mouse')), (0, False))
expect("AetherHub's button left alone", L.eval('HUBBTN.alpha'), 1)
expect("protected frame left alone", L.eval('PROT.alpha'), 1)
expect("zoom button left alone", L.eval('ZOOM.alpha'), 1)
expect("calendar and the small button by the bar left alone", (L.eval('CALBTN.alpha'), L.eval('ONEBTN.alpha')), (1, 1))
expect("zone bar art hidden", L.eval('MinimapCluster.BorderTop.alpha'), 0)
L.execute('''PILL = nil; for _, f in ipairs(FRAMES) do if f.points[1] and f.points[1][2] == ZONEBTN and f.points[1][1] == "TOPLEFT" then PILL = f end end''')
expect("pill starts at the zone name (not the whole bar)", L.eval('PILL ~= nil'), True)
expect("pill ends at the clock", L.eval('PILL.points[2][2] == TimeManagerClockButton and PILL.points[2][1]'), "BOTTOMRIGHT")
expect("pill sits under the bar's buttons", L.eval('PILL.level < TRACK.level and PILL.level < CALBTN.level + 5'), True)
expect("tracking and calendar untouched", (L.eval('TRACK.alpha'), L.eval('CALBTN.alpha')), (1, 1))
expect("yellow zone text -> Aether gold", tuple(round(v, 2) for v in L.eval('{MinimapZoneText:GetTextColor()}').values()), (1, 0.69, 0))
L.execute('MinimapZoneText:SetTextColor(0.1, 1, 0.1)')
expect("green (friendly) zone text kept", tuple(round(v, 2) for v in L.eval('{MinimapZoneText:GetTextColor()}').values()), (0.1, 1, 0.1))
L.execute('MinimapZoneText:SetTextColor(1, 0.82, 0)')
expect("yellow again -> gold", tuple(round(v, 2) for v in L.eval('{MinimapZoneText:GetTextColor()}').values()), (1, 0.69, 0))
expect("clock art hidden, its highlight kept", (L.eval('TimeManagerClockButton.regs[1].alpha'), L.eval('TimeManagerClockButton.hl.alpha')), (0, 1))
expect("Hub told the ring is up", L.eval('AetherSkins_RingActive'), True)
# night falls: fade out, swap, fade in
L.execute('DAY = false; TIMERS[1]()')
upd = 'local f; for _, x in ipairs(FRAMES) do if x.scripts.OnUpdate then f = x end end; return f'
L.execute('FADER = (function() ' + upd + ' end)()')
L.execute('FADER.scripts.OnUpdate(FADER, 0.4)')
expect("fading out: still day art, half lit", (L.eval('AetherSkinsMinimapRing.lit.texture')[-8:], round(L.eval('AetherSkinsMinimapRing.lit.alpha'), 2)), ("ring_day", 0.5))
L.execute('FADER.scripts.OnUpdate(FADER, 0.6)')
expect("swapped to night art", (L.eval('AetherSkinsMinimapRing.lit.texture')[-10:], L.eval('AetherSkinsDayNight.icon.texture')[-8:]), ("ring_night", "ico_moon"))
L.execute('FADER.scripts.OnUpdate(FADER, 1.0)')
expect("night fully lit, fade done", (L.eval('AetherSkinsMinimapRing.lit.alpha'), L.eval('FADER.scripts.OnUpdate')), (1, None))
expect("moon tinted pale", tuple(round(v, 2) for v in list(L.eval('AetherSkinsDayNight.icon.vc').values())[:3]), (0.88, 0.91, 0.96))
# without Forever's IsDayTime: the realm clock (5:30-21:00 is day)
L.execute('C_DateAndTime = nil')
for (h, m), want in (((5, 29), False), ((5, 30), True), ((20, 59), True), ((21, 0), False)):
    L.execute('GAME = {%d, %d}' % (h, m))
    expect("clock %02d:%02d is %s" % (h, m, "day" if want else "night"), L.eval('(AetherSkins_API.IsDay())'), want)
# the button opens the calendar
L.execute('AetherSkinsDayNight.scripts.OnClick()')
expect("click: calendar", L.eval('CALENDAR'), 1)
# commands
L.execute('OUT = ""; SlashCmdList.AETHERSKINS("debug")')
out = L.eval('OUT')
expect("debug names the replaced icon", "ForeverDayNightButton" in out, True)
expect("debug lists what's near the top-right", "GameTimeFrame (60 deg" in out, True)
L.execute('OUT = ""; SlashCmdList.AETHERSKINS("day")')
expect("/skins day previews day", L.eval('OUT').strip().endswith("day (set by /skins)"), True)
L.execute('SlashCmdList.AETHERSKINS("minimap off")')
expect("/skins minimap off saved", L.eval('AetherSkinsDB.minimap'), False)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
