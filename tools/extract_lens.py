import re, sys
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
def body(path, var):
    s = open(path, encoding="utf-8").read()
    m = re.search(var + r"\s*=\s*\[\[(return \{.*\})\]\]", s, re.S)
    return lua.execute(m.group(1))
quests = body("/tmp/fquest.lua", "QuestieDB.questData")
items = body("/tmp/fitem.lua", "QuestieDB.itemData")
def lst(t):
    return [t[i] for i in range(1, len(t)+1)] if t is not None and hasattr(t, "__len__") else []
need = {}       # item -> set(quests)
for qid, q in quests.items():
    qid = int(qid)
    obj = q[10]
    if obj is not None and obj[3] is not None:
        for o in lst(obj[3]):
            if o and o[1]: need.setdefault(int(o[1]), set()).add(qid)
    if q[11]: need.setdefault(int(q[11]), set()).add(qid)
    for it in lst(q[21]): need.setdefault(int(it), set()).add(qid)
starts = {}
for iid, d in items.items():
    if d[5]: starts[int(iid)] = int(d[5])
for qid, q in quests.items():
    sb = q[2]
    if sb is not None and sb[3] is not None:
        for it in lst(sb[3]): starts.setdefault(int(it), int(qid))
names = {}
for qid in set(q for s in need.values() for q in s) | set(starts.values()):
    q = quests[qid]
    if q is not None and q[1]: names[qid] = q[1]
# recipes from AtlasLootClassic (Classic table only)
src = open("/tmp/prof.lua", encoding="utf-8").read()
a = src.index("PROFESSION_DATA.CLASSIC = {"); b = src.index("\n}", a)
uses = {}
for m in re.finditer(r"\[(\d+)\] = \{(nil|\d+),(\d+),(\d+),\d+,\d+,\{([\d,]*)\},\{([\d,]*)\}", src[a:b]):
    spell, prof, minlvl = int(m.group(1)), int(m.group(3)), int(m.group(4))
    for r in (m.group(5).split(",") if m.group(5) else []):
        uses.setdefault(int(r), []).append((spell, prof, minlvl))
esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
out = ["-- AetherLens item data for WoW Forever.",
       "-- Quests: QuestieDB Forever data (GPLv3). Recipes: AtlasLootClassic Classic profession data (GPLv2).",
       "-- See DATA_NOTICE.txt.", "",
       "AetherLens_QuestNeeds = {   -- itemID -> quest IDs that need it"]
out += ["[%d]={%s}," % (i, ",".join(map(str, sorted(s)))) for i, s in sorted(need.items())]
out += ["}", "", "AetherLens_StartsQuest = {   -- itemID -> quest it starts"]
out += ["[%d]=%d," % (i, q) for i, q in sorted(starts.items())]
out += ["}", "", "AetherLens_QuestNames = {"]
out += ['[%d]="%s",' % (q, esc(n)) for q, n in sorted(names.items())]
out += ["}", "", "AetherLens_Uses = {   -- reagent itemID -> { {recipe spellID, profession, skill}, ... }"]
out += ["[%d]={%s}," % (i, ",".join("{%d,%d,%d}" % r for r in sorted(v, key=lambda r: (r[1], r[2])))) for i, v in sorted(uses.items())]
out += ["}"]
open("/home/claude/brand/AetherLens/AetherLens_Data.lua", "w", newline="\r\n").write("\n".join(out) + "\n")
print("quest items:", len(need), "starters:", len(starts), "quest names:", len(names), "reagents:", len(uses), "recipe uses:", sum(map(len, uses.values())))
