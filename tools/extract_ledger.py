import re, json
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
def body(path, var):
    s = open(path, encoding="utf-8").read()
    m = re.search(var + r"\s*=\s*\[\[(return \{.*\})\]\]", s, re.S)
    return lua.execute(m.group(1))
Q = body("/tmp/q/foreverQuestDB.lua", "QuestieDB.questData")
N = body("/tmp/q/foreverNpcDB.lua", "QuestieDB.npcData")
O = body("/tmp/q/foreverObjectDB.lua", "QuestieDB.objectData")
zs = open("/tmp/q/areaIdToUiMapId.lua", encoding="utf-8").read()
area = {}
for t in reversed([lua.execute(b) for b in re.findall(r"=\s*\[\[(return \{.*?\})\]\]", zs, re.S)]):
    for k, v in t.items(): area[int(k)] = int(v)
# dungeons
ds = open("/tmp/q/dungeons.lua", encoding="utf-8").read()
dungeon_areas = set()
for m in re.finditer(r"^\s*\[(\d+)\]\s*=\s*\{\"[^\"]*\",(\{[\d,]*\}|nil)", ds, re.M):
    dungeon_areas.add(int(m.group(1)))
    if m.group(2) != "nil":
        dungeon_areas |= {int(x) for x in re.findall(r"\d+", m.group(2))}
# blacklist
lua.execute("""
QuestieLoader = { CreateModule = function() return {} end, ImportModule = function() return {} end }
""")
bl_src = open("/tmp/q/blacklist.lua", encoding="utf-8").read()
bl_src = bl_src.replace('local ContentPhases = QuestieLoader:ImportModule("ContentPhases")', 'local ContentPhases = {activePhases={}}')
bl_src = bl_src.replace('local Expansions = QuestieLoader:ImportModule("Expansions")', 'local Expansions = {Era=1,Tbc=2,Wotlk=3,Cata=4,MoP=5,Current=1}')
lua.execute("Questie = {Debug=function() end}")
mod = lua.execute(bl_src + "\nreturn QuestieQuestBlacklist")
bl = {int(k) for k, v in mod.Load(mod).items() if v}
print("blacklisted", len(bl), "dungeon areas", len(dungeon_areas))

def lst(t):
    if t is None: return []
    return [t[i] for i in range(1, len(t) + 1)]

def spawn_of(spawns):
    if spawns is None: return None
    best = None
    for a, coords in spawns.items():
        mp = area.get(int(a))
        if not mp: continue
        cs = [c for c in lst(coords) if c and c[1] is not None and c[1] >= 0 and c[2] >= 0]
        if not cs: continue
        if best is None or len(cs) > best[3]:
            best = (mp, round(cs[0][1], 1), round(cs[0][2], 1), len(cs))
    return best

out = {}
skip = {}
def sk(r): skip[r] = skip.get(r, 0) + 1
for qid, q in Q.items():
    qid = int(qid)
    if qid in bl: sk("blacklist"); continue
    name, sb, req, lvl = q[1], q[2], q[4] or 0, q[5] or 0
    if not name or lvl <= 0: sk("nolevel"); continue
    if (q[24] or 0) & 1: sk("repeatable"); continue
    zos = q[17] or 0
    if zos > 0 and zos in dungeon_areas: sk("dungeon"); continue
    kind, skill, skillMin = "", 0, 0
    if q[18]:
        kind, skill, skillMin = "p", int(q[18][1] or 0), int(q[18][2] or 0)
    elif zos < 0:
        cm = int(q[7] or 0)
        if cm == 0: sk("sort"); continue      # holiday and other special quests
        kind = "c"
    giver = None
    if sb is not None:
        for nid in lst(sb[1]):
            n = N[nid]
            if n is None: continue
            sp = spawn_of(n[7])
            if sp:
                giver = (sp, n[1], n[13] or ""); break
        if not giver:
            for oid in lst(sb[2]):
                o = O[oid]
                if o is None: continue
                sp = spawn_of(o[4])
                if sp:
                    giver = (sp, o[1], ""); break
    if not giver: sk("nogiver"); continue
    (mp, x, y, _), gname, side = giver
    out[qid] = dict(n=name, r=int(req), l=int(lvl), m=mp, x=x, y=y, g=gname, s=side,
                    ra=int(q[6] or 0), c=int(q[7] or 0),
                    ps=[int(v) for v in lst(q[13])], pg=[int(v) for v in lst(q[12])],
                    ex=[int(v) for v in lst(q[16])], nx=int(q[22] or 0), k=kind, sk=skill, sm=skillMin)
# chain reach: highest quest level along the "next" chain
for qid, d in out.items():
    top, cur, seen, steps = d["l"], d["nx"], set(), 0
    while cur and cur in out and cur not in seen and steps < 30:
        seen.add(cur); top = max(top, out[cur]["l"]); cur = out[cur]["nx"]; steps += 1
    d["top"], d["len"] = top, steps + 1
print("kept", len(out), "skipped", skip)
json.dump(out, open("/tmp/q/ledger.json", "w"))

# ---- skinnable beasts per zone (by name: Questie has no creature type) ----
BEASTS = ["wolf","worg","boar","bear","tiger","panther","lion","lioness","cougar","leopard","lynx","jaguar",
          "saber","nightsaber","frostsaber","prowler","raptor","crocolisk","kodo","hyena","gorilla","silverback",
          "basilisk","thunder lizard","plainstrider","tallstrider","zhevra","wind serpent","turtle","snapjaw",
          "scorpid","yeti","devilsaur","ravasaur","stegodon","diemetradon","pterrordax","chimaera","thunderhawk",
          "shardtooth","mountain lion","bloodfang","bonegnasher","fleshstalker","strider","dragonhawk","ridge stalker",
          "highland stalker","jungle stalker","shadowmaw","thrasher","coyote","moonstalker","mottled boar"]
NOT = ["spirit","ghost","zombie","skeletal","rotting","druid","shaman","mystic","totem","spectral","undead",
       "illusion","image","summoned","wolfrider","rider","master","tamer","trainer","handler","pup","cub","whelp"]
import re as _re
pat = _re.compile(r"\b(" + "|".join(_re.escape(b) for b in sorted(BEASTS, key=len, reverse=True)) + r")s?\b", _re.I)
bad = _re.compile(r"\b(" + "|".join(NOT) + r")\b", _re.I)
zones = {}
for nid, n in N.items():
    name = n[1]
    if not name or n[13] or (n[6] or 0) != 0: continue          # friendly to a faction, or elite/rare
    if not pat.search(name) or bad.search(name): continue
    lo, hi = n[4] or 0, n[5] or 0
    if lo <= 0: continue
    sp = n[7]
    if sp is None: continue
    for a, coords in sp.items():
        mp = area.get(int(a))
        if not mp or not lst(coords): continue
        z = zones.setdefault(mp, {})
        cur = z.get(name)
        cnt = len(lst(coords))
        if cur: z[name] = (min(cur[0], lo), max(cur[1], hi), cur[2] + cnt)
        else: z[name] = (int(lo), int(hi), cnt)
skin = {mp: sorted([(v[0], v[1], v[2], k) for k, v in z.items() if v[2] >= 3]) for mp, z in zones.items()}
skin = {mp: v for mp, v in skin.items() if v}
json.dump(skin, open("/tmp/q/skin.json", "w"))
print("skin zones", len(skin), "mobs", sum(len(v) for v in skin.values()))

# ---- every quest's home zone (objectives) and turn-in zone, for the quest tracker ----
zones_out = {}
for qid, q in Q.items():
    qid = int(qid)
    if qid in bl or not q[1]: continue
    zos = int(q[17] or 0)
    home = area.get(zos) if zos > 0 else None
    turn = None
    fb = q[3]
    if fb is not None:
        for nid in lst(fb[1]):
            n = N[nid]
            sp = n is not None and spawn_of(n[7])
            if sp: turn = sp[0]; break
        if not turn:
            for oid in lst(fb[2]):
                o = O[oid]
                sp = o is not None and spawn_of(o[4])
                if sp: turn = sp[0]; break
    if home or turn:
        zones_out[qid] = (home or 0, turn or 0)
json.dump(zones_out, open("/tmp/q/zones.json", "w"))
print("quest zones", len(zones_out))
