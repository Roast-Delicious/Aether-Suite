# Login sequence: does the meter ever sit anywhere but its dock spot?
import sys
hdr=open('meter_show_test.py').read().split("src = open(")[0]
hdr=hdr.replace("After = function() end", "After = function(t, fn) TIMERS[#TIMERS+1] = {t, fn} end")
hdr=hdr.replace("FRAMES = {}", "FRAMES = {}; TIMERS = {}")
exec(hdr)
L.execute(open('/mnt/user-data/uploads/54619117#1--SavedVariables/AetherMeter.lua').read())
if len(sys.argv)>1 and sys.argv[1]: L.execute('AetherMeterDB.dockSpot = {1222, 2550, 24, 206}')   # saved by last session
L.execute('''
UIParent.GetWidth = function() return 2560 end
READY = false
REAL = { {L=524,R=1210,B=20,T=82}, {L=1216,R=1210+4,B=20,T=82}, {L=524,R=1210,B=86,T=210} }
function AetherBars_PanelRects() if READY then return REAL end return {} end
LOG = {}
''')
src=open(sys.argv[2] if len(sys.argv)>2 else '/home/claude/brand/AetherMeter/AetherMeter.lua').read()
L.execute(src, 'AetherMeter')
L.execute('''
AetherMeterFrame.SetPoint = function(s, p, rel, rp, x, y)
  local k = p .. " " .. math.floor(x) .. "," .. math.floor(y)
  if LOG[#LOG] ~= k then LOG[#LOG+1] = k end
end
for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then EV = f end end
function Step(label) STEP = label end
EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMeter")
LOG[#LOG+1] = "-- PLAYER_ENTERING_WORLD (bars place themselves)"
READY = true
for _, fn in ipairs(AetherBars_Listeners or {}) do fn() end
EV.scripts.OnEvent(EV, "PLAYER_ENTERING_WORLD")
table.sort(TIMERS, function(a,b) return a[1] < b[1] end)
for _, t in ipairs(TIMERS) do LOG[#LOG+1] = "-- " .. t[1] .. "s timer"; t[2]() end
for _, f in ipairs(FRAMES) do if f.scripts.OnUpdate then for i=1,4 do f.scripts.OnUpdate(f, 0.6) end end end
LOG[#LOG+1] = "-- heartbeat x4"
''')
log=L.eval('LOG'); print("\n".join(log[i] for i in range(1,len(log)+1)))
print("saved dock spot now:", list(L.eval('AetherMeterDB.dockSpot').values()) if L.eval('AetherMeterDB.dockSpot') else None)
