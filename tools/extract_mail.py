import re, sys
from lupa import LuaRuntime
obj_src = open(sys.argv[1], encoding="utf-8").read()
zones_src = open(sys.argv[2], encoding="utf-8").read()
lua = LuaRuntime(unpack_returned_tuples=True)
m = re.search(r"QuestieDB\.objectData\s*=\s*\[\[(.*)\]\]", obj_src, re.S)
objs = lua.execute(m.group(1))
area_to_map = {}
for t in reversed([lua.execute(b) for b in re.findall(r"=\s*\[\[(return \{.*?\})\]\]", zones_src, re.S)]):
    for k, v in t.items(): area_to_map[int(k)] = int(v)
ALLIANCE, HORDE = {12, 55, 80}, {29, 68, 104}
bymap, skipped = {}, 0
for oid, d in objs.items():
    if d[1] != "Mailbox" or not d[4]: continue
    f = d[6] or 0
    fac = 1 if f in ALLIANCE else 2 if f in HORDE else 3
    for area, coords in d[4].items():
        mp = area_to_map.get(int(area))
        if not mp: skipped += 1; continue
        for i in range(1, len(coords) + 1):
            x, y = coords[i][1], coords[i][2]
            if x is None or x < 0: continue
            bymap.setdefault(mp, []).append((int(oid), fac, round(x/100, 4), round(y/100, 4)))
out = ["-- AetherPathfinder mailbox locations for WoW Forever.",
       "-- From QuestieDB's Forever object data (data/Forever/foreverObjectDB.lua), GPLv3; see DATA_NOTICE.txt.",
       "-- Format per map: { objectID, faction (1 = Alliance, 2 = Horde, 3 = both), x, y }",
       "", "AetherPathfinder_Mailboxes = {"]
n = 0
for mp in sorted(bymap):
    rows = sorted(set(bymap[mp]))
    n += len(rows)
    out.append("[%d] = {" % mp)
    out += ["{%d,%d,%s,%s}," % r for r in rows]
    out.append("},")
out.append("}")
open(sys.argv[3], "w", newline="\r\n").write("\n".join(out) + "\n")
print("mailboxes:", n, "maps:", len(bymap), "unmapped areas:", skipped, file=sys.stderr)
