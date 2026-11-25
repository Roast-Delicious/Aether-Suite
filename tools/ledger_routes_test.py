# AetherLedger 1.8.0: quest givers on the move (AetherLedger_Routes). Loads
# the real routes file and AetherLedger_Travel.lua on a mock map where world
# yards = map coordinates x 10 (one instance), then walks the player around.
import lupa.lua51 as l, sys
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Routes.lua').read())
ok = True
def expect(label, got, want):
    global ok
    good = got == want; ok &= good
    print(("ok   " if good else "FAIL ") + label + ("" if good else "   got %r, want %r" % (got, want)))
n = L.eval('(function() local n=0 for _ in pairs(AetherLedger_Routes) do n=n+1 end return n end)()')
expect("routes file loads, 61 quests", n, 61)
expect("Cork Gizelton's quest (5821) has his Desolace route", (L.eval('AetherLedger_Routes[5821][1]'), L.eval('#AetherLedger_Routes[5821] > 20')), (1443, True))
expect("Rigger Gizelton's quest (5943) rides the same route", L.eval('#AetherLedger_Routes[5943] == #AetherLedger_Routes[5821]'), True)
expect("a stationary quest giver (Madame Eva, quest 66) has none", L.eval('AetherLedger_Routes[66]'), None)
L.execute(r'''
local function Obj() return setmetatable({ pts = {} }, { __index = function(t, k)
  if type(k) == "string" and k:match("^%u") then return function() end end end }) end
function Obj_() return Obj() end
CreateFrame = function(kind, name) local o = Obj(); o.CreateFontString = function() return Obj() end
  o.CreateTexture = function() return Obj() end; if name then _G[name] = o end; return o end
UIParent = Obj(); C_Timer = { After = function() end, NewTicker = function() end }; GetTime = function() return 0 end
PLAYER = { 1443, 0.10, 0.10 }
CreateVector2D = function(x, y) return { x = x, y = y } end
C_Map = { GetMapInfo = function(m) return { name = "Desolace" } end,
  GetWorldPosFromMapPos = function(map, v) return 1, { x = v.x * 1000, y = v.y * 1000 } end,
  GetBestMapForUnit = function() return PLAYER[1] end,
  GetPlayerMapPosition = function() return { GetXY = function() return PLAYER[2], PLAYER[3] end } end }
AetherDecorate = function() end; AetherClose = function() return Obj() end
UnitOnTaxi = function() return false end
ARRIVED = nil
''')
src = open('/home/claude/brand/AetherLedger/AetherLedger_Travel.lua').read()
src += '\nfunction TEST_Trip() return trip end\n'
L.execute(src)
L.execute('local A = AetherLedger_Travel.Arrived; AetherLedger_Travel.Arrived = function(how) ARRIVED = how or "giver"; return A(how) end')
L.execute('DEST = { name = "Cork Gizelton", map = 1443, x = 0.668, y = 0.581, qid = 5821 }; AetherLedger_Travel.Start(DEST)')
expect("travel to a moving giver knows his route", L.eval('DEST.route ~= nil and #DEST.route > 20'), True)
expect("far away: not there yet", L.eval('ARRIVED'), None)
L.execute('PLAYER = { 1443, 0.677, 0.500 }; AetherLedger_Travel.Update()')   # beside the road, mid-route (67.8, 49.7)
expect("anywhere along his road counts as there", L.eval('ARRIVED'), "route")
L.execute('ARRIVED = nil; PLAYER = { 1443, 0.10, 0.10 }; DEST2 = { name = "Madame Eva", map = 1443, x = 0.5, y = 0.5, qid = 66 }; AetherLedger_Travel.Start(DEST2)')
expect("a stationary giver has no route", L.eval('DEST2.route'), None)
L.execute('PLAYER = { 1443, 0.677, 0.500 }; AetherLedger_Travel.Update()')
expect("...and his road doesn't count for her", L.eval('ARRIVED'), None)
L.execute('PLAYER = { 1443, 0.5005, 0.5005 }; AetherLedger_Travel.Update()')
expect("...only her own spot does", L.eval('ARRIVED'), "giver")
L.execute('ARRIVED = nil; DEST3 = { name = "Cork Gizelton", map = 1411, x = 0.668, y = 0.581, qid = 5821 }; AetherLedger_Travel.Start(DEST3)')
expect("a route on another map isn't used", L.eval('DEST3.route'), None)
# The "(on the move)" helper must come after the data field names (Nov 25:
# above them GIVER was nil and the Hub's Ledger page errored on Cork Gizelton).
src = open('/home/claude/brand/AetherLedger/AetherLedger.lua').read()
expect("GiverText comes after the field names it uses", src.index("local NAME, REQ, LEVEL, MAP, X, Y, GIVER") < src.index("local function GiverText"), True)
expect("...and before its first use", src.index("local function GiverText") < src.index("GiverText(id)"), True)
L2 = l.LuaRuntime(unpack_returned_tuples=True)
L2.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Data.lua').read())
L2.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Routes.lua').read())
i, j = src.index("local DATA = AetherLedger_Data"), src.index("AetherLedger_Moving = Moving")
L2.execute(src[i:j] + "\nTEST_GiverText = GiverText")
expect("a moving giver's text (Cork Gizelton, quest 5821)", L2.eval('TEST_GiverText(5821)'), "Cork Gizelton (on the move)")
expect("a stationary giver's text has no tag", L2.eval('TEST_GiverText(5386)'), "Nataka Longhorn")
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
