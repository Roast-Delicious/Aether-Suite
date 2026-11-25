# AetherPack 1.6.4: the Ammo heading ("Arrows: 1,240" ... "buy 9 stacks to
# fill"), user idea Nov 25. AmmoHeading() is lifted out of AetherPack.lua.
import lupa, sys
src = open('/home/claude/brand/AetherPack/AetherPack.lua').read()
fn = src[src.index('local function AmmoHeading(st)'):src.index('-- Sorts the bags into sections')]
L = lupa.LuaRuntime()
L.execute('''
CLASS, RANGED_SUB = "HUNTER", 2
function UsesAmmo() return CLASS == "HUNTER" end
function MyClass() return CLASS end
function GetInventoryItemID() return RANGED_SUB and 100 or nil end
function GetItemInfoInstant() return nil, nil, nil, nil, nil, 2, RANGED_SUB end
AMMO_LOW = 300; SPACE_RED = {0.94, 0.37, 0.33}; SPACE_GREEN = {0.133, 0.902, 0.314}
''' + fn + '\nAH = AmmoHeading')
ok = True
def expect(label, got, want):
    global ok; good = got == want; ok &= good
    print(("ok   " if good else "FAIL ") + label + ("" if good else "   got %r, want %r" % (got, want)))
def run(st):
    r = L.eval('function(t) local a, b, c, d = AH(t); return {a, b, c, d and d[1]} end')(L.table_from(st))
    return tuple(r[i] for i in (1, 2, 3, 4))
base = dict(ammo=1240, quiverSlots=16, quiverFree=9, quiverAmmo=1240, ammoStack=200, pouch=False, soulSlots=0, soulFree=0, shards=0)
expect("bow, 16-slot quiver, 1,240 arrows", run(base)[:3], ("Arrows", "1240", "buy 9 stacks to fill"))
expect("full quiver", run(dict(base, quiverAmmo=3200, ammo=3200))[:3], ("Arrows", "3200", "quiver full"))
expect("full quiver shows in green", round(run(dict(base, quiverAmmo=3200, ammo=3200))[3], 3), 0.133)
expect("low: the hint turns red", round(run(dict(base, ammo=220, quiverAmmo=220))[3], 2), 0.94)
expect("one stack short", run(dict(base, quiverAmmo=3000, ammo=3000))[2], "buy 1 stack to fill")
L.execute('RANGED_SUB = 3')
expect("gun: bullets", run(dict(base, pouch=True))[0], "Bullets")
expect("no quiver: no hint", run(dict(base, quiverSlots=0))[2], None)
L.execute('CLASS = "WARLOCK"')
expect("warlock: soul shards and room", run(dict(base, shards=14, soulSlots=20, soulFree=6))[:3], ("Soul shards", "14", "room for 6 more"))
L.execute('CLASS = "MAGE"')
expect("other classes: no heading change", run(base)[0], None)
print("PASS" if ok else "FAILED"); sys.exit(0 if ok else 1)
