import json
D = {int(k): v for k, v in json.load(open('/tmp/q/ledger.json')).items()}
S = json.load(open('/tmp/q/skin.json'))
Z = {int(k): v for k, v in json.load(open('/tmp/q/zones.json')).items()}
def s(x): return '"' + x.replace('\\', '\\\\').replace('"', '\\"') + '"'
def t(l): return "{" + ",".join(map(str, l)) + "}" if l else "nil"
lines = []
for qid in sorted(D):
    d = D[qid]
    f = [s(d['n']), d['r'], d['l'], d['m'], d['x'], d['y'], s(d['g']), s(d['s']), d['ra'], d['c'], d['top'], d['len'],
         t(d['ps']), t(d['pg']), t(d['ex']), s(d['k']) if d['k'] else "nil", d['sk'] or "nil", d['sm'] or "nil"]
    while f and f[-1] == "nil": f.pop()
    lines.append("[%d]={%s}," % (qid, ",".join(map(str, f))))
skin = ["[%s]={%s}," % (mp, ",".join("{%d,%d,%s}" % (a, b, s(n)) for a, b, c, n in S[mp])) for mp in sorted(S, key=int)]
zl = ["[%d]={%d,%d}," % (q, h, tn) for q, (h, tn) in sorted(Z.items())]
hdr = """-- AetherLedger quest data, generated from QuestieDB (Forever), GPLv3: see DATA_NOTICE.txt.
-- [questID] = { name, required level, quest level, uiMapID, x, y, giver, giver faction ("A", "H", "AH" or ""),
--   race mask (0 = any), class mask (0 = any), highest level along its chain, chain length,
--   needs one of {..}, needs all of {..}, not with {..},
--   kind ("c" class quest, "p" profession quest), profession skill ID, skill needed }
AetherLedger_Data = {
"""
out = hdr + "\n".join(lines) + "\n}\n"
out += """
-- Skinnable beasts by zone (matched by name; QuestieDB has no creature types):
-- [uiMapID] = { { min level, max level, name }, ... }
AetherLedger_Skinning = {
""" + "\n".join(skin) + "\n}\n"
out += """
-- Every quest's zones, for the quest tracker: [questID] = { home zone (where the
-- quest log files it), turn-in zone } as uiMapIDs (0 = unknown).
AetherLedger_Zones = {
""" + "\n".join(zl) + "\n}\n"
open('/home/claude/brand/AetherLedger/AetherLedger_Data.lua', 'w').write(out)
print(len(lines), len(skin), len(zl))
