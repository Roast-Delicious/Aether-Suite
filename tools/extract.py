import re, sys, json
from lupa import LuaRuntime

npc_src = open(sys.argv[1], encoding="utf-8").read()
zones_src = open(sys.argv[2], encoding="utf-8").read()

# NPC table is the Lua chunk inside QuestieDB.npcData = [[ ... ]]
m = re.search(r"QuestieDB\.npcData\s*=\s*\[\[(.*)\]\]", npc_src, re.S)
lua = LuaRuntime(unpack_returned_tuples=True)
npcs = lua.execute(m.group(1))

# Area -> UiMap: main table, then overrides on top (overrides are listed first in the file)
area_to_map = {}
blocks = re.findall(r"=\s*\[\[(return \{.*?\})\]\]", zones_src, re.S)
tables = [lua.execute(b) for b in blocks]
for t in reversed(tables):          # main table last-in-file applied first, overrides win
    for k, v in t.items():
        area_to_map[int(k)] = int(v)
print("zone blocks:", len(blocks), "areas:", len(area_to_map), file=sys.stderr)

F = dict(VENDOR=4, FLIGHT=8, TRAINER=16, INN=128, BANK=256, AUCTION=4096, STABLE=8192, REPAIR=16384)

def lst(t):
    return [t[i] for i in range(1, len(t) + 1)] if t is not None else []

out = []
for npc_id, d in npcs.items():
    name, spawns, faction, sub, flags = d[1], d[7], d[13], d[14], d[15] or 0
    if not faction or not spawns:
        continue
    service = flags & (F["VENDOR"] | F["FLIGHT"] | F["TRAINER"] | F["INN"] | F["BANK"] |
                       F["AUCTION"] | F["STABLE"] | F["REPAIR"])
    if not service:
        continue
    for area, coords in spawns.items():
        mp = area_to_map.get(int(area))
        if not mp:
            continue
        for c in lst(coords):
            x, y = c[1], c[2]
            if x is None or x < 0 or y < 0:
                continue
            out.append(dict(id=int(npc_id), name=name, sub=sub, flags=int(flags),
                            fac=faction, map=mp, x=round(x / 100, 4), y=round(y / 100, 4)))
json.dump(out, open(sys.argv[3], "w"))
print("service spawns:", len(out), "npcs:", len({o["id"] for o in out}), file=sys.stderr)
