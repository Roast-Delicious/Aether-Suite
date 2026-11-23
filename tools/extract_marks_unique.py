import re, json
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
def body(path, var):
    s = open(path, encoding="utf-8").read()
    m = re.search(var + r"\s*=\s*\[\[(return \{.*\})\]\]", s, re.S)
    return lua.execute(m.group(1))
Q = body("/tmp/q/foreverQuestDB.lua", "QuestieDB.questData")
I = body("/tmp/q/foreverItemDB.lua", "QuestieDB.itemData")
N = body("/tmp/q/foreverNpcDB.lua", "QuestieDB.npcData")
def lst(t): return [] if t is None else [t[i] for i in range(1, len(t)+1)]
unique, shared = {}, 0
for qid, q in Q.items():
    obj = q[10]
    if obj is None: continue
    for it in lst(obj[3]):          # item objectives: {itemID, text}
        iid = it[1]
        d = I[iid]
        if d is None: continue
        drops = lst(d[2])
        if len(drops) == 1:
            n = N[drops[0]]
            if n is None: continue
            spawns = sum(len(lst(c)) for c in (n[7].values() if n[7] is not None else []))
            if spawns <= 3:                       # one of a kind in the world, not a mob type
                unique[int(drops[0])] = n[1]
        elif drops: shared += 1
print("unique droppers", len(unique), "shared-drop items", shared)
for k in list(unique)[:15]: print(k, unique[k])
json.dump(sorted(unique), open("/tmp/q/unique_droppers.json","w"))
