# Line Up after moving: the question box, Line Up, Line Up and Center, Keep As Is,
# parked frames left alone, no question without a move. Mock WoW from frames_test.py.
import sys
pre = open('/home/claude/tools/frames_test.py').read().split("for name in")[0]
exec(pre)
PHYS_W, PHYS_H = 2560, 1440
UE, SCALE = 1.15 * 768 / PHYS_H, 1.17
L.execute('''
local M = getmetatable(UIParent)
function M.SetScale(s,v) s.scale=v end
function M.GetEffectiveScale(s) if s==UIParent then return %r end return %r * (s.scale or 1) end
function M.GetWidth(s) if s==UIParent then return %r end return s.w end
local function At(s) local p=s.pts[1]; if p and p[2]==UIParent and p[3]=="BOTTOMLEFT" then return p[4], p[5] end end
function M.GetLeft(s) local x=At(s); return x or 100 end
function M.GetTop(s) local _,y=At(s); return y or 700 end
GetPhysicalScreenSize=function() return %d, %d end
function MoverOf(f) for _,o in ipairs(ALL) do if o.all==f and o.scripts.OnDragStop then return o end end end
function Drag(f, x, y) f:ClearAllPoints(); f:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", x, y); MoverOf(f).scripts.OnDragStop() end
function Click(label) for _,o in ipairs(ALL) do if o.text==label and o.scripts.OnClick and o.parent==AetherFramesLineUp then o.scripts.OnClick(o); return true end end end
''' % (UE, UE, PHYS_W * 768 / PHYS_H / UE, PHYS_W, PHYS_H))
L.execute('AetherFramesDB.scale = %r' % SCALE)
pxu = UE * SCALE * PHYS_H / 768
fails = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m)
    if not c: fails.append(m)
cmd = L.eval('function(c) SlashCmdList.AETHERFRAMES(c) end')
box = lambda: L.eval('AetherFramesLineUp')
shown = lambda: box() is not None and box().shown
pos = lambda k: tuple(L.eval('AetherFramesDB.pos')[k][i] for i in (1, 2))
W = {"player": 270, "target": 270, "pet": 215, "tot": 215}
def layout():
    L.execute('AetherFramesDB.pos = nil'); 
    L.execute('Drag(AetherFramesPlayer, 400.3, 600.2); Drag(AetherFramesTarget, 735, 603.7)')
    L.execute('Drag(AetherFramesPet, 461, 480.9); Drag(AetherFramesTargetTarget, 728.5, 476.6)')
whole = lambda v: abs(v * pxu - round(v * pxu)) < 1e-6

# no move, no question
cmd("unlock"); cmd("lock")
check(not shown(), "no question when nothing moved")
# party only: no question
cmd("unlock"); L.execute('Drag(AetherFramesParty1, 50, 500)'); cmd("lock")
check(not shown(), "no question when only the party moved")

# Keep As Is
cmd("unlock"); layout(); before = {k: pos(k) for k in W}; cmd("lock")
check(shown(), "question shows after a move")
check(L.eval('Click')("Keep As Is") and not shown(), "Keep As Is closes it")
check(all(pos(k) == before[k] for k in W), "Keep As Is leaves every frame exactly where it was")

# Line Up
cmd("unlock"); check(not shown(), "unlocking again hides any question")
layout(); cmd("lock"); L.eval('Click')("Line Up")
P, T, Pe, To = pos("player"), pos("target"), pos("pet"), pos("tot")
check(not shown(), "Line Up closes it")
check(abs(P[0] - 400.3) <= 0.5 / pxu + 1e-9 and abs(P[1] - 600.2) <= 0.5 / pxu + 1e-9, "your frame stays (within half a pixel)")
check(T[1] == P[1], "target level with you")
check(abs((Pe[0] + 215) - (P[0] + 270)) < 1e-9, "pet's inner end under yours")
check(To[0] == T[0], "target of target's inner end under the target's")
check(To[1] == Pe[1], "bottom row level")
check(abs(T[0] - 735) <= 0.5 / pxu + 1e-9, "target's sideways spot kept")
check(whole(P[0] + 270) and whole(T[0]) and whole(P[1]) and whole(Pe[1]), "edges on whole pixels")

# Line Up and Center
cmd("unlock"); layout(); cmd("lock"); L.eval('Click')("Line Up and Center")
P, T, Pe, To = pos("player"), pos("target"), pos("pet"), pos("tot")
mid = (P[0] + T[0] + 270) / 2 * pxu
check(abs(mid - PHYS_W / 2) <= 0.5 + 1e-6, "pair centered on screen, within half a pixel (%.2f px)" % mid)
check(abs((Pe[0] + 215) - (P[0] + 270)) < 1e-9 and To[0] == T[0], "pet and target of target came along")
check(T[1] == P[1] and To[1] == Pe[1], "rows level")
check(abs(P[1] - 600.2) <= 0.5 / pxu + 1e-9, "height kept")

# parked pet stays put
cmd("unlock"); layout(); L.execute('Drag(AetherFramesPet, 100, 300)'); cmd("lock"); L.eval('Click')("Line Up")
Pe, To, T = pos("pet"), pos("tot"), pos("target")
check(abs(Pe[0] - 100) < 1 and abs(Pe[1] - 300) < 1, "a pet parked far away stays there")
check(To[0] == T[0] and abs(To[1] - 476.6) < 1, "target of target lines up with the target, not the parked pet's row")

# combat: refused, box stays
cmd("unlock"); layout(); cmd("lock")
L.execute('InCombatLockdown=function() return true end')
L.eval('Click')("Line Up")
check(shown(), "in combat the question stays open")
L.execute('InCombatLockdown=function() return false end'); L.eval('Click')("Line Up")
check(not shown(), "works after combat")
# Done button and right-click also ask
cmd("unlock"); layout()
L.execute('MoverOf(AetherFramesPlayer).scripts.OnMouseUp(nil, "RightButton")')
check(shown(), "right-click to finish asks too")
L.eval('Click')("Keep As Is")
print("FAILURES:", fails) if fails else print("all good")
sys.exit(1 if fails else 0)
