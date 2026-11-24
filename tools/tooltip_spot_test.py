# Loads AetherLedger_TooltipSpot.lua with a mock GameTooltip, UIParent and
# ObjectiveTrackerFrame, and checks where the default tooltip ends up.
import lupa.lua51 as l, sys
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
HOOKS = {}
hooksecurefunc = function(name, fn)
  local orig = _G[name]; _G[name] = function(...) orig(...); fn(...) end
end
UIParent = { GetEffectiveScale = function() return 0.8 end }
local function Frame(l, r, s) return { l = l, r = r, s = s,
  GetLeft = function(self) return self.l end, GetRight = function(self) return self.r end,
  GetEffectiveScale = function(self) return self.s end } end
ObjectiveTrackerFrame = Frame(1400, 1640, 0.8)
GameTooltip = { points = {}, forbidden = false,
  IsForbidden = function(s) return s.forbidden end,
  SetOwner = function() end,
  ClearAllPoints = function(s) s.points = {} end,
  SetPoint = function(s, ...) s.points[#s.points + 1] = { ... } end }
function GameTooltip_SetDefaultAnchor(tt, parent)
  tt:SetOwner(parent, "ANCHOR_NONE"); tt:ClearAllPoints()
  tt:SetPoint("BOTTOMRIGHT", UIParent, "BOTTOMRIGHT", -13, 0)
end
''')
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_TooltipSpot.lua').read())
ok = True
def expect(label, got, want):
    global ok
    good = got == want; ok &= good
    print(("ok  " if good else "FAIL"), label, got)
def pt():
    n = L.eval('#GameTooltip.points'); p = L.eval('GameTooltip.points[%d]' % n)
    return (n,) + tuple(p[i] for i in range(1, 6))
L.execute('GameTooltip_SetDefaultAnchor(GameTooltip, {})')
p = pt()
expect("default spot -> left of tracker, mid-screen", (p[0], p[1], L.eval('GameTooltip.points[1][2] == UIParent'), p[3], p[4], p[5]), (1, "RIGHT", True, "LEFT", 1392, 0))
L.execute('ObjectiveTrackerFrame.s = 0.4; GameTooltip_SetDefaultAnchor(GameTooltip, {})')
expect("follows the tracker's scale", pt()[4], 692)
L.execute('ObjectiveTrackerFrame.s = 0.8; ObjectiveTrackerFrame.l = 40; ObjectiveTrackerFrame.r = 280; GameTooltip_SetDefaultAnchor(GameTooltip, {})')
expect("tracker at the left edge -> tooltip on its right", pt()[1:2] + (pt()[4],), ("LEFT", 288))
L.execute('ObjectiveTrackerFrame.l = nil; GameTooltip_SetDefaultAnchor(GameTooltip, {})')
expect("no tracker position -> game's spot kept", pt()[1], "BOTTOMRIGHT")
L.execute('ObjectiveTrackerFrame.l = 1400; AetherLedgerDB = { tooltipSpot = false }; GameTooltip_SetDefaultAnchor(GameTooltip, {})')
expect("turned off -> game's spot", pt()[1], "BOTTOMRIGHT")
expect("toggle turns it back on", L.eval('AetherLedger_TooltipSpot.Toggle()'), True)
L.execute('GameTooltip.forbidden = true; GameTooltip_SetDefaultAnchor(GameTooltip, {})')
expect("forbidden tooltip left alone", pt()[1], "BOTTOMRIGHT")
L.execute('GameTooltip.forbidden = false; GameTooltip.SetPoint = nil')
expect("errors are contained", L.eval('(pcall(AetherLedger_TooltipSpot.Place, GameTooltip))'), False)
L.execute('GameTooltip.SetPoint = function() end')
expect("the hook itself never errors", L.eval('(pcall(_G.GameTooltip_SetDefaultAnchor, GameTooltip, {}))'), True)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
