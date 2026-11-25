# AetherLedger 1.8.5: where a flight lands. A known flight master in the
# destination's own zone wins over a slightly closer one across the zone
# border (user, Nov 25: Cork Gizelton in Desolace routed via Thunder Bluff).
import lupa, re, sys
src = open('/home/claude/brand/AetherLedger/AetherLedger_Travel.lua').read()
part = src[src.index('local function Dist('):src.index('local DIRS')] + src[src.index('local function Nearest('):src.index('-- Steps to get from spot')]
L = lupa.LuaRuntime()
L.execute(part + '\nLANDING = Landing')
ok = True
def expect(label, got, want):
    global ok; good = got == want; ok &= good
    print(("ok   " if good else "FAIL ") + label + ("" if good else "   got %r, want %r" % (got, want)))
L.execute('''
TAL = { name = "Tal", map = 1412, w = { inst = 1, x = 0, y = 1300 } }        -- Thunder Bluff, 1,300 yd away
THALON = { name = "Thalon", map = 1443, w = { inst = 1, x = 0, y = -1400 } } -- Shadowprey, 1,400 yd away
DEST = { inst = 1, x = 0, y = 0 }
''')
expect("Desolace destination: lands at the Desolace flight master, not the slightly closer Thunder Bluff",
       L.eval('LANDING({ TAL, THALON }, DEST, 1443).name'), "Thalon")
L.execute('TAL.w.y = 500')
expect("...unless the other one is less than half as far", L.eval('LANDING({ TAL, THALON }, DEST, 1443).name'), "Tal")
expect("no flight master known in that zone: the nearest one", L.eval('LANDING({ TAL }, DEST, 1443).name'), "Tal")
expect("no zone given: the nearest one", L.eval('LANDING({ TAL, THALON }, DEST, nil).name'), "Tal")
print("PASS" if ok else "FAILED"); sys.exit(0 if ok else 1)
