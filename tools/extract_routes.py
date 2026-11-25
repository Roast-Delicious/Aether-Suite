# Moving quest givers for AetherLedger (Nov 25): QuestieDB (Forever) keeps a
# walking route ("waypoints", npc field 8) for NPCs that move, like the
# Gizelton caravan in Desolace. For each quest already in AetherLedger_Data
# whose giver is such an NPC, write the route on the giver's map to
# AetherLedger_Routes.lua: [questID] = { uiMapID, x1, y1, x2, y2, ... } (0-100).
# Inputs (from github.com/Questie/QuestieDB): data/Forever/foreverQuestDB.lua,
# foreverNpcDB.lua, support/Forever/Zones/areaIdToUiMapId.lua, in the folder
# given as argv[1]. Same giver choice as extract_ledger.py (first NPC with a spawn).
import re, sys, math
from lupa import LuaRuntime
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/q2'
lua = LuaRuntime(unpack_returned_tuples=True)
def body(path, var):
    s = open(path, encoding="utf-8").read()
    m = re.search(var + r"\s*=\s*\[\[(return \{.*\})\]\]", s, re.S)
    return lua.execute(m.group(1))
Q = body(SRC + "/foreverQuestDB.lua", "QuestieDB.questData")
N = body(SRC + "/foreverNpcDB.lua", "QuestieDB.npcData")
zs = open(SRC + "/areaIdToUiMapId.lua", encoding="utf-8").read()
area = {}
for t in reversed([lua.execute(b) for b in re.findall(r"=\s*\[\[(return \{.*?\})\]\]", zs, re.S)]):
    for k, v in t.items(): area[int(k)] = int(v)
def lst(t):
    if t is None: return []
    return [t[i] for i in range(1, len(t) + 1)]

# the quests AetherLedger already knows, with their giver's map and spot
data = open('/home/claude/brand/AetherLedger/AetherLedger_Data.lua', encoding='utf-8').read()
known = {}
for m in re.finditer(r'^\[(\d+)\]=\{"(?:[^"\\]|\\.)*",\d+,\d+,(\d+),([\d.]+),([\d.]+),"((?:[^"\\]|\\.)*)"', data, re.M):
    known[int(m.group(1))] = (int(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5))

def has_spawn(n):
    sp = n[7]
    if sp is None: return False
    for a, coords in sp.items():
        if area.get(int(a)) and any(c and c[1] is not None and c[1] >= 0 for c in lst(coords)): return True
    return False

def route_of(n, mp):
    wp = n[8]
    if wp is None: return None
    best = None
    for a, paths in wp.items():
        if area.get(int(a)) != mp: continue
        for path in lst(paths):
            pts = [(round(c[1], 1), round(c[2], 1)) for c in lst(path) if c and c[1] is not None and c[1] >= 0 and c[2] >= 0]
            if best is None or len(pts) > len(best): best = pts
    if not best or len(best) < 2: return None
    # thin: drop points within 1.0 map units of the last kept one, cap at 80
    out = [best[0]]
    for p in best[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) >= 1.0: out.append(p)
    if len(out) > 80:
        step = len(out) / 80.0
        out = [out[int(i * step)] for i in range(80)]
    span = max(math.hypot(a[0] - b[0], a[1] - b[1]) for a in out for b in out) if len(out) > 1 else 0
    return out if span >= 3 else None      # a few steps on the spot isn't "on the move"

routes = {}
for qid, (mp, x, y, gname) in known.items():
    q = Q[qid]
    if q is None or q[2] is None: continue
    for nid in lst(q[2][1]):
        n = N[nid]
        if n is None or not has_spawn(n): continue
        r = route_of(n, mp)
        if r: routes[qid] = (mp, r, n[1])
        break
# Travel companions: a giver with no route of his own, standing within 1.5 map
# units of a walker's start on the same map, goes with him (Rigger Gizelton
# rides with Cork Gizelton's caravan).
# Only long journeys (a caravan, 25+ units across): a town patrol (3-12 units)
# would otherwise sweep in the shopkeepers it walks past.
def span(pts): return max(math.hypot(a[0] - b[0], a[1] - b[1]) for a in pts for b in pts)
starts = [(mp, pts[0], pts, name) for mp, pts, name in routes.values() if span(pts) >= 25]
for qid, (mp, x, y, gname) in known.items():
    if qid in routes: continue
    for smp, (sx, sy), pts, wname in starts:
        if smp == mp and math.hypot(sx - x, sy - y) <= 1.5 and gname != wname:
            routes[qid] = (mp, pts, gname.replace('\\"', '"') + " (with " + wname + ")")
            break
lines = ["[%d]={%d,%s}, -- %s" % (q, mp, ",".join("%s,%s" % p for p in pts), name.replace("\n", " "))
         for q, (mp, pts, name) in sorted(routes.items())]
hdr = """-- AetherLedger: quest givers who walk a route (from QuestieDB's Forever data,
-- GPLv3: see DATA_NOTICE.txt). [questID] = { uiMapID, x1, y1, x2, y2, ... }
-- (map coordinates 0-100, thinned to 1-unit steps). Made by tools/extract_routes.py.
AetherLedger_Routes = {
"""
open('/home/claude/brand/AetherLedger/AetherLedger_Routes.lua', 'w', encoding='utf-8').write(hdr + "\n".join(lines) + "\n}\n")
givers = sorted({name for _, _, name in routes.values()})
print(len(routes), "quests,", len(givers), "givers:", ", ".join(givers[:40]))
