exec(open('/home/claude/tools/cast_base.py').read())
SETUP = '''
AddPlate("nameplate1", {guid="a", name="Dalaran Apprentice"})
UNITS.target = UNITS.nameplate1; PLATES.target = PLATES.nameplate1; EV.scripts.OnEvent(EV, "PLAYER_TARGET_CHANGED")
O = OVERLAYS[PLATES.nameplate1]
'''
BLIZZ = '''
TargetFrameSpellBar = { shown = true, min = 0, max = 3.0, value = 0 }
function TargetFrameSpellBar:IsShown() return self.shown end
function TargetFrameSpellBar:GetMinMaxValues() return self.min, self.max end
function TargetFrameSpellBar:GetValue() return self.value end
'''
def st(label):
    print("%-40s method=%-8s shown=%-5s value=%s range=%s..%s sealed-timer=%s" % (label, L.eval('O.castMethod'), L.eval('O.cast.shown'),
          L.eval('O.cast.value'), L.eval('O.cast.min'), L.eval('O.cast.max'), L.eval('O.cast.timer ~= nil')))
L.execute(SETUP); L.execute(BLIZZ)
L.execute('SECRET_TIMES = true; CASTING = {"Frostbolt", 100000, 103000}; EV.scripts.OnEvent(EV, "UNIT_SPELLCAST_START", "target")')
st("secret times: copy Blizzard bar, start")
L.execute('TargetFrameSpellBar.value = 1.5; O.cast.scripts.OnUpdate(O.cast)'); st("secret times: Blizzard bar halfway")
L.execute('TargetFrameSpellBar.shown = false; O.cast.scripts.OnUpdate(O.cast)'); st("Blizzard bar done")
L.execute('TargetFrameSpellBar = nil; SECRET_TIMES = false; NOW = 100; CASTING = {"Frostbolt", 100000, 103000}; EV.scripts.OnEvent(EV, "UNIT_SPELLCAST_START", "target"); NOW = 101.5; O.cast.scripts.OnUpdate(O.cast)')
st("readable times, halfway")
L.execute('SECRET_TIMES = true; EV.scripts.OnEvent(EV, "UNIT_SPELLCAST_START", "target")'); st("nothing works: full bar")
L.execute('''Enum.StatusBarTimerDirection = { ElapsedTime = 0, RemainingTime = 1 }
Enum.StatusBarInterpolation = { Immediate = 0 }
UnitCastingDuration = function(u) return { sealed = true } end
function M_SetTimerDuration(self, d, interp, dir) self.timer = { d = d, dir = dir } end''')
src = open('/home/claude/brand/AetherMarks/AetherMarks.lua').read().replace('local overlays   = {}', 'OVERLAYS = {}; local overlays = OVERLAYS')
L.execute('FRAMES = {}'); L.execute(src, 'AetherMarks')
L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then EV = f end end; EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks"); PLATES = {}')
L.execute(SETUP)
L.execute('CASTING = {"Frostbolt", 100000, 103000}; EV.scripts.OnEvent(EV, "UNIT_SPELLCAST_START", "target")')
st("game has sealed cast timers")
print("  timer direction (0 = fills as it casts):", L.eval('O.cast.timer.dir'))
