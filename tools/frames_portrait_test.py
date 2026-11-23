# 3D portraits: model + glow under the rings, 2D fallbacks, reload only on change,
# pet camera pulled back, /af portraits 2d|3d, fading. Mock WoW from frames_test.py.
import sys
txt = open('/home/claude/tools/frames_test.py').read().split("for name in")[0]
head, tail = txt.split("src=open(", 1)
exec(head)
L.execute('''
local M = getmetatable(UIParent)
function M.SetFrameLevel(s, l) s.level = l end
function M.GetFrameLevel(s) return s.level or (s.parent and s.parent.GetFrameLevel and s.parent:GetFrameLevel() + 1) or 1 end
function M.HasScript(s, k) return s.kind == "PlayerModel" and k == "OnModelLoaded" end
CALLS = {}
function M.SetUnit(s, u) if ERR_SETUNIT then error("blocked") end CALLS[#CALLS+1] = u; s.unitShown = u; if FAIL_SETUNIT then return false end return true end
function M.SetPortraitZoom(s, z) s.zoom = z end
function M.SetCamDistanceScale(s, d) s.cam = d end
function M.SetViewTranslation(s, x, y) s.vx, s.vy = x, y end
function M.GetModelFileID(s) return MODEL_ID end
MODEL_ID = 12345
VIS = { player=true, pet=true, target=true, targettarget=true }
UnitIsVisible = function(u) return VIS[u] end
GUIDS = { player="P-1", pet="Pet-1", target="T-1" }
UnitGUID = function(u) return GUIDS[u] end
NOW = 1000; GetTime = function() return NOW end
''')
exec("src=open(" + tail)
fails = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m)
    if not c: fails.append(m)
F = lambda n: L.eval(n)
L.execute('for _, n in ipairs({"AetherFramesPlayer","AetherFramesPet","AetherFramesTarget","AetherFramesTargetTarget"}) do _G[n].shown = true end')
P, PET, T = F('AetherFramesPlayer'), F('AetherFramesPet'), F('AetherFramesTarget')
def mode3d(f): return f.model.shown and f.portraitBack.shown and not f.face.shown and f.crestRim.shown and not f.crestDark.shown
def mode2d(f): return not f.model.shown and not f.portraitBack.shown and f.face.shown and not f.crestRim.shown and f.crestDark.shown
check(mode3d(P) and mode3d(PET) and mode3d(T), "3D on: model and glow shown, flat face hidden, rim over the model")
check(P.model.unitShown == "player" and T.model.unitShown == "target", "models show their units")
check(P.model.zoom == 1 and P.model.cam == 1 and PET.model.cam == 1.25, "portrait zoom; pet camera pulled back")
lv = lambda o: L.eval('function(o) return o:GetFrameLevel() end')(o)
badge = [c for c in P.children.values() if c.kind == "Button" or (c.kind == "Frame" and c.level and c.level > lv(P))]
check(lv(P.portraitBack) < lv(P.model) < lv(P), "glow under the model, model under the frame's rings")
check(all(lv(b) > lv(P) for b in badge) and len(badge) > 0, "badges and medallions above")
check(abs(P.model.w - 80 / 2 ** 0.5) < 1e-9 and abs(PET.model.w - 58 / 2 ** 0.5) < 1e-9, "model is the largest square inside the crest")
glow = [t for t in P.portraitBack.children.values()]
check(any(t.tex and "portrait_glow" in t.tex for t in glow) and any(t.vc and abs(t.vc[1]-0.075)<1e-9 for t in glow), "navy disc + Aether-blue glow")
n0 = len(L.eval('CALLS'))
L.execute('EV.scripts.OnEvent(EV, "UNIT_NAME_UPDATE", "player")')
check(len(L.eval('CALLS')) == n0, "same unit: model not reloaded")
L.execute('GUIDS.target = "T-2"; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(len(L.eval('CALLS')) == n0 + 1 + 0 or L.eval('CALLS')[len(L.eval('CALLS'))] in ("target", "targettarget"), "new target: model reloaded")
n1 = len(L.eval('CALLS'))
L.execute('EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "player")')
check(len(L.eval('CALLS')) == n1 + 1, "look changed: reloaded")
# target of target polling with a hidden (secret-like: nil) guid: no reload churn
L.execute('UNITS.targettarget = UNITS.target; GUIDS.targettarget = nil; EV.scripts.OnEvent(EV, "UNIT_TARGET", "target")')
TOT = F('AetherFramesTargetTarget'); TOT.shown = True
n2 = len(L.eval('CALLS'))
for i in range(12): L.execute('NOW = NOW + 0.1; EV.scripts.OnUpdate(EV, 0.1)')
check(len(L.eval('CALLS')) == n2, "target-of-target check doesn't restart its model")
# fallbacks
L.execute('VIS.target = false; EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "target")')
check(mode2d(T), "out of sight: flat portrait")
L.execute('VIS.target = true; FAIL_SETUNIT = true; EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "target")')
check(mode3d(T), "SetUnit says false (as WoW Forever does even on success): still 3D")
L.execute('NOW = NOW + 1; EV.scripts.OnUpdate(EV, 0.2)')
check(mode3d(T), "...and the model loaded, so it stays 3D")
L.execute('ERR_SETUNIT = true; EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "target")')
check(mode2d(T) and "error" in str(T.faceWhy), "SetUnit errors: flat portrait")
L.execute('ERR_SETUNIT = nil; FAIL_SETUNIT = nil')
L.execute('FAIL_SETUNIT = nil; MODEL_ID = nil; EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "target")')
check(mode3d(T), "model requested")
L.execute('NOW = NOW + 1; EV.scripts.OnUpdate(EV, 0.2)')
check(mode2d(T), "no model after a moment: flat portrait")
L.execute('MODEL_ID = 5; EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "target"); NOW = NOW + 1; EV.scripts.OnUpdate(EV, 0.2)')
check(mode3d(T), "model loads: stays 3D")
L.execute('MODEL_ID = nil; EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "target"); AetherFramesTarget.model.scripts.OnModelLoaded(AetherFramesTarget.model); NOW = NOW + 1; EV.scripts.OnUpdate(EV, 0.2)')
check(mode3d(T), "loaded event counts as loaded")
# toggle
L.execute('SlashCmdList.AETHERFRAMES("portraits 2d")')
check(mode2d(P) and mode2d(PET) and mode2d(T), "/af portraits 2d: flat everywhere")
L.execute('SlashCmdList.AETHERFRAMES("portraits 3d")')
check(mode3d(P) and mode3d(PET) and mode3d(T), "/af portraits 3d: back to 3D")
# fading follows the faces setting
L.execute('AetherFramesDB.fadeFaces = true; AetherFramesPlayer.curAlpha = nil')
L.execute('NOW = NOW + 1; EV.scripts.OnUpdate(EV, 0.2)')
check(P.model.alpha == L.eval('AetherFramesDB.alpha') and P.portraitBack.alpha == P.model.alpha, "faces fade on: model and glow fade too")
# hidden and shown again: reload
n3 = len(L.eval('CALLS'))
L.execute('AetherFramesPlayer.scripts.OnShow(AetherFramesPlayer)')
check(len(L.eval('CALLS')) == n3 + 1, "shown again: model reloaded")
# move mode placeholder: no model
L.execute('UNITS.pet = nil; SlashCmdList.AETHERFRAMES("unlock")')
check(mode2d(PET), "empty frame while moving: no model")
# report + test mode
L.execute('SlashCmdList.AETHERFRAMES("lock"); UNITS.pet = UNITS.target; GUIDS.pet = "Pet-1"')
L.execute('MODEL_ID = nil; SlashCmdList.AETHERFRAMES("portraits 3d"); NOW = NOW + 1; EV.scripts.OnUpdate(EV, 0.2)')
check(mode2d(T) and T.faceWhy and "no model file" in T.faceWhy, "fallback records why: " + str(T.faceWhy))
out = []
L.globals().print = lambda *a: out.append(" ".join(str(x) for x in a))
L.execute('SlashCmdList.AETHERFRAMES("auras")')
rep = [l for l in out if "SetUnit" in l]
print("\n".join(rep))
check(any(l.strip().startswith("target 2d (no model file") for l in rep), "/af auras lists each portrait and why")
L.execute('VIS.target = false; SlashCmdList.AETHERFRAMES("portraits test"); NOW = NOW + 5; EV.scripts.OnUpdate(EV, 0.2)')
check(mode3d(T) and mode3d(P), "test mode: 3D with no fallbacks (even unseen, no model id)")
L.execute('SlashCmdList.AETHERFRAMES("portraits 3d"); NOW = NOW + 1; EV.scripts.OnUpdate(EV, 0.2)')
check(mode2d(T), "back to normal: fallbacks again")
# live tuning
out2 = []
L.globals().print = lambda *a: out2.append(" ".join(str(x) for x in a))
L.execute('SlashCmdList.AETHERFRAMES("portraits 3d"); SlashCmdList.AETHERFRAMES("portraits zoom 1.3")')
check(P.model.cam == 1.3 and PET.model.cam == 1.3 and T.model.cam == 1.3, "zoom all 1.3 applies live (pet too)")
L.execute('SlashCmdList.AETHERFRAMES("portraits zoom pet 1.6")')
check(PET.model.cam == 1.6 and P.model.cam == 1.3, "zoom pet only")
L.execute('SlashCmdList.AETHERFRAMES("portraits shift 0 -2"); SlashCmdList.AETHERFRAMES("portraits shift tot 3 1")')
TOT = F('AetherFramesTargetTarget')
check(P.model.vx == 0 and P.model.vy == -2 and TOT.model.vx == 3 and TOT.model.vy == 1, "shift all, and tot on its own")
check(L.eval('AetherFramesDB.portraitTune.pet.zoom') == 1.6, "saved")
L.execute('VIS.target = true; MODEL_ID = 7; AetherFramesTarget.model.cam = nil; EV.scripts.OnEvent(EV, "UNIT_MODEL_CHANGED", "target")')
check(T.model.cam == 1.3 and T.model.vy == -2, "kept when a model reloads")
L.execute('SlashCmdList.AETHERFRAMES("portraits tune")')
print(out2[-1])
check("pet zoom 1.60" in out2[-1] and "tot zoom 1.30 shift 3 1" in out2[-1], "tune shows the values")
L.execute('SlashCmdList.AETHERFRAMES("portraits tune reset")')
check(PET.model.cam == 1.25 and P.model.cam == 1 and P.model.vy == 0, "reset: back to the built-in values")
L.execute('SlashCmdList.AETHERFRAMES("portraits zoom")')
check("Try:" in out2[-1], "bad input shows how")
# level glow on the target's rim
L.execute('UnitCanAttack = function(a, u) return UNITS[u] and UNITS[u].enemy or false end')
L.execute('UNITS.target = {name="Bloodfen Raptor",lvl=37,hp=612,hpm=1275,pw=0,pwm=0,pt=1,tok="RAGE",enemy=true}; UNITS.player.lvl = 34; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
rim = lambda n: tuple(round(v, 3) for v in L.eval('{%s.portraitDisc.vc[1], %s.portraitDisc.vc[2], %s.portraitDisc.vc[3]}' % (n, n, n)).values())
mid = lambda n: tuple(round(v, 3) for v in L.eval('{%s.portraitGlow.vc[1], %s.portraitGlow.vc[2], %s.portraitGlow.vc[3]}' % (n, n, n)).values())
navy = (0.075, 0.157, 0.29); blue = (0.3, 0.7, 1.0)
near = lambda a, b: all(abs(x - y) < 0.002 for x, y in zip(a, b))
check(rim('AetherFramesTarget') == (0.35, 0.175, 0.045) and near(mid('AetherFramesTarget'), (1.0, 0.5, 0.13)), "enemy 3 levels up: all orange, no blue %s %s" % (rim('AetherFramesTarget'), mid('AetherFramesTarget')))
check(rim('AetherFramesPlayer') == navy and rim('AetherFramesPet') == navy and mid('AetherFramesPlayer') == blue and mid('AetherFramesPet') == blue, "you and Steve: always blue")
L.execute('UNITS.target.lvl = 34; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(near(mid('AetherFramesTarget'), (1.0, 0.82, 0.0)) and near(rim('AetherFramesTarget'), (0.35, 0.287, 0.0)), "even fight: shades of real yellow %s %s" % (mid('AetherFramesTarget'), rim('AetherFramesTarget')))
L.execute('UNITS.target.lvl = 42; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(near(rim('AetherFramesTarget'), (0.35, 0.0455, 0.0455)), "5+ up: red")
L.execute('UNITS.target.lvl = S and -1 or -1; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(near(rim('AetherFramesTarget'), (0.35, 0.0455, 0.0455)), "?? level: red")
L.execute('UNITS.target.lvl = 37; UNITS.target.enemy = false; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(rim('AetherFramesTarget') == navy and mid('AetherFramesTarget') == blue, "friendly target: blue")
L.execute('UNITS.target.enemy = true; SlashCmdList.AETHERFRAMES("levelglow off")')
check(rim('AetherFramesTarget') == navy and mid('AetherFramesTarget') == blue, "/af levelglow off: blue")
L.execute('SlashCmdList.AETHERFRAMES("levelglow on")')
check(near(mid('AetherFramesTarget'), (1.0, 0.5, 0.13)), "/af levelglow on: back")
check(rim('AetherFramesTargetTarget') == navy, "target of target: navy")
# class colors
L.execute(r'''
CLASSCOL = { HUNTER = {r=0.67,g=0.83,b=0.45}, MAGE = {r=0.25,g=0.78,b=0.92}, WARRIOR = {r=0.78,g=0.61,b=0.43}, PRIEST = {r=1,g=1,b=1} }
C_ClassColor = { GetClassColor = function(t) return CLASSCOL[t] end }
UnitClass = function(u) local x = UNITS[u]; if x and x.cls then return x.cls, x.cls end end
UnitIsPlayer = function(u) local x = UNITS[u]; return x ~= nil and x.isPlayer == true end
UnitIsUnit = function(a, b) return UNITS[a] ~= nil and UNITS[a] == UNITS[b] end
UnitPlayerControlled = function(u) local x = UNITS[u]; return x ~= nil and (x.isPlayer or x.pet) or false end
UNITS.player.cls = "HUNTER"; UNITS.player.isPlayer = true; UNITS.pet.pet = true
''')
def glow_of(n): return mid(n), rim(n)
def tgt(setup):
    L.execute(setup + '; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
tgt('UNITS.target = {name="Ziggi",lvl=35,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="MANA",cls="MAGE",isPlayer=true,enemy=false}')
check(near(mid('AetherFramesTarget'), (0.25, 0.78, 0.92)) and near(rim('AetherFramesTarget'), (0.0875, 0.273, 0.322)), "friendly player target: shaded mage color")
tgt('UNITS.target = {name="Guard",lvl=40,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="MANA",cls="WARRIOR",enemy=false}')
check(near(mid('AetherFramesTarget'), (0.78, 0.61, 0.43)), "friendly NPC: its class color")
tgt('UNITS.target = {name="Horde Priest",lvl=36,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="MANA",cls="PRIEST",isPlayer=true,enemy=true}')
check(near(mid('AetherFramesTarget'), (1, 1, 1)), "enemy player: class color (not level)")
tgt('UNITS.target = {name="Raptor",lvl=37,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="RAGE",cls="WARRIOR",enemy=true}')
check(near(mid('AetherFramesTarget'), (1.0, 0.5, 0.13)), "enemy mob: still its level color")
tgt('UNITS.target = UNITS.player')
check(mid('AetherFramesTarget') == blue and mid('AetherFramesPlayer') == blue and mid('AetherFramesPet') == blue, "you as your target, you, and Steve: Aether blue")
tgt('UNITS.target = UNITS.pet')
check(mid('AetherFramesTarget') == blue, "Steve as your target: blue")
L.execute('UNITS.targettarget = {name="Ziggi",lvl=35,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="MANA",cls="MAGE",isPlayer=true}; UNITS.target = {name="Raptor",lvl=37,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="RAGE",enemy=true}; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(near(mid('AetherFramesTargetTarget'), (0.25, 0.78, 0.92)), "target of target a player: class color")
L.execute('UNITS.targettarget = {name="Wolf",lvl=37,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="RAGE",enemy=true}; EV.scripts.OnEvent(EV, "UNIT_TARGET", "target")')
check(mid('AetherFramesTargetTarget') == blue, "target of target an enemy mob: blue (level color is for the target only)")
L.execute('SlashCmdList.AETHERFRAMES("classglow off"); UNITS.target = {name="Ziggi",lvl=35,hp=1,hpm=1,pw=0,pwm=1,pt=0,tok="MANA",cls="MAGE",isPlayer=true}; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(mid('AetherFramesTarget') == blue, "/af classglow off: blue")
L.execute('SlashCmdList.AETHERFRAMES("classglow on")')
check(near(mid('AetherFramesTarget'), (0.25, 0.78, 0.92)), "/af classglow on: back")
L.execute('UnitClass = function() return "x", S("MAGE") end; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")')
check(mid('AetherFramesTarget') == blue, "class hidden by the game: blue, no error")
print("FAILURES:", fails) if fails else print("all good")
sys.exit(1 if fails else 0)
