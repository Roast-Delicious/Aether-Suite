# /af center: frames centered on screen, inner capsule ends lined up, rows level,
# edges on whole screen pixels. Reuses frames_test.py's mock WoW.
import re, sys
pre = open('/home/claude/tools/frames_test.py').read().split("for name in")[0]
pre = pre.replace("EV.scripts.OnUpdate(EV, 0.2)", "")
exec(pre)
PHYS_W, PHYS_H = 2560, 1440
UE, SCALE = 1.15 * 768 / PHYS_H, 1.17          # the user's ~1.15 px per UI unit
L.execute('''
local M = getmetatable(UIParent)
function M.SetScale(s,v) s.scale=v end
function M.GetEffectiveScale(s) if s==UIParent then return %r end return %r * (s.scale or 1) end
function M.GetWidth(s) if s==UIParent then return %r end return s.w end
function M.GetTop(s) local p=s.pts[1]; if p and p[2]==UIParent and p[3]=="BOTTOMLEFT" then return p[5] end return 700 end
GetPhysicalScreenSize=function() return %d, %d end
''' % (UE, UE, PHYS_W * 768 / PHYS_H / UE, PHYS_W, PHYS_H))
L.execute('AetherFramesDB.scale = %r' % SCALE)
fails = []
def check(cond, msg):
    if not cond: fails.append(msg)
    print(("ok   " if cond else "FAIL ") + msg)

L.execute('SlashCmdList.AETHERFRAMES("center")')
db = L.eval('AetherFramesDB')
e = UE * SCALE
pxu = e * PHYS_H / 768                          # screen pixels per frame unit
def fr(n): return L.eval(n)
P, T, PET, TOT = (fr(n) for n in ["AetherFramesPlayer", "AetherFramesTarget", "AetherFramesPet", "AetherFramesTargetTarget"])
pos = db.pos
pr  = (pos.player[1] + P.w) * pxu;  tl = pos.target[1] * pxu
petr = (pos.pet[1] + PET.w) * pxu;  totl = pos.tot[1] * pxu
print("px per unit %.3f  player right %.2f  target left %.2f  pet right %.2f  tot left %.2f" % (pxu, pr, tl, petr, totl))
def whole(v): return abs(v - round(v)) < 1e-6
check(whole(pr) and whole(tl), "inner capsule ends on whole pixels")
check(abs((pr + tl) / 2 - PHYS_W / 2) <= 0.5, "group centered on screen (within half a pixel)")
check(abs(petr - pr) < 1e-6 and abs(totl - tl) < 1e-6, "pet under player, tot under target, inner ends aligned")
check(abs(pos.player[2] - pos.target[2]) < 1e-9 and abs(pos.pet[2] - pos.tot[2]) < 1e-9, "rows level")
check(whole(pos.player[2] * pxu) and whole(pos.pet[2] * pxu), "row tops on whole pixels")
check(abs((tl - pr) / pxu - 61) < 1 and abs((pos.player[2] - pos.pet[2]) - 120) < 1, "gap ~61 and drop ~120 units")
check(abs(pos.player[2] - 700) < 1, "player height kept")
for n, f in [("player", P), ("target", T), ("pet", PET), ("tot", TOT)]:
    ok = L.eval('function(f, x, y) local p = f.pts[1]; return p[1] == "TOPLEFT" and p[2] == UIParent and p[3] == "BOTTOMLEFT" and math.abs(p[4] - x) < 1e-9 and math.abs(p[5] - y) < 1e-9 end')(f, pos[n][1], pos[n][2])
    check(ok, n + " placed from saved spot")
# in combat: refused, nothing moves
L.execute('InCombatLockdown=function() return true end; AetherFramesDB.pos.player[1]=5; SlashCmdList.AETHERFRAMES("center")')
check(L.eval('AetherFramesDB.pos.player[1]') == 5, "refused in combat")
print("FAILURES:", fails) if fails else print("all good")
sys.exit(1 if fails else 0)
