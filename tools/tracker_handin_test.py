# AetherLedger 1.8.3: finished quests (from any zone) handed in elsewhere
# stay on the tracker, at the bottom, with their hand-in zone; and a red
# quest you just accepted gets a chat line saying why it left. Same mock as
# tracker_sort_test (newest-on-top tracker), in Desolace (1443).
import lupa.lua51 as l, sys
ok = True
def expect(label, got, want):
    global ok
    good = got == want; ok &= good
    print(("ok   " if good else "FAIL ") + label + ("" if good else "   got %r, want %r" % (got, want)))
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
OUT = {}
print = function(...) OUT[#OUT+1] = table.concat({...}, " ") end
UnitLevel = function() return 36 end; UnitName = function() return "Jay" end; GetRealmName = function() return "Forever" end
InCombatLockdown = function() return false end
UnitOnTaxi = function() return false end
GetTime = function() return 1000 end
TIMERS = {}
C_Timer = { After = function(t, f) TIMERS[#TIMERS+1] = f end }
GetQuestDifficultyColor = nil
-- 201/202: in progress here; 203: finished here, handed in in Orgrimmar (1454);
-- 204: finished here, handed in here; 205: a quest elsewhere (Badlands); 206: red, just accepted
LOG = { {id=201, title="Catch of the Day", level=37}, {id=202, title="Ongeku", level=37},
        {id=203, title="Bodyguard for Hire", level=35, done=true}, {id=204, title="The Corrupter", level=35, done=true},
        {id=205, title="Badlands Reagent Run", level=38}, {id=206, title="Horde Trauma", level=45} }
WATCH = {}
C_QuestLog = {
  GetNumQuestLogEntries = function() return #LOG + 1 end,
  GetInfo = function(i) if i == 1 then return { isHeader = true, title = "Desolace" } end
             local q = LOG[i-1]; return { questID = q.id, title = q.title, level = q.level } end,
  GetQuestWatchType = function(id) for _, w in ipairs(WATCH) do if w == id then return 0 end end end,
  IsComplete = function(id) for _, q in ipairs(LOG) do if q.id == id then return q.done or false end end return false end,
  AddQuestWatch = function(id) table.insert(WATCH, 1, id) end,
  RemoveQuestWatch = function(id) for i, w in ipairs(WATCH) do if w == id then table.remove(WATCH, i) end end end,
  GetNumQuestWatches = function() return #WATCH end,
  GetQuestIDForQuestWatchIndex = function(i) return WATCH[i] end,
  GetMaxNumQuestsCanWatch = function() return 25 end,
}
MAPS = { [1443] = "Desolace", [1454] = "Orgrimmar", [1418] = "Badlands" }
C_Map = { GetBestMapForUnit = function() return 1443 end,
          GetMapInfo = function(m) if MAPS[m] then return { name = MAPS[m], mapType = 3, parentMapID = 12 } end
                                   return { name = "Kalimdor", mapType = 2 } end }
AetherLedger_Zones = { [201]={1443,1443}, [202]={1443,1443}, [203]={1443,1454}, [204]={1443,1443}, [205]={1418,1418}, [206]={1417,1417} }
EV = nil
CreateFrame = function() local f = setmetatable({}, { __index = function() return function() end end })
  f.SetScript = function(self, k, fn) if k == "OnEvent" then EV = fn end end; return f end
hooksecurefunc = function() end
''')
L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Tracker.lua').read())
L.execute('AetherLedger_Tracker.Apply()')
shown = [L.eval('WATCH[%d]' % i) for i in range(1, L.eval('#WATCH') + 1)]
expect("tracker, top to bottom: here's quests by level, then the hand-in elsewhere", shown, [204, 201, 202, 203])
expect("the hand-in elsewhere knows its zone", L.eval('AetherLedger_Tracker.ElsewhereZone(203)'), "Orgrimmar")
expect("a quest handed in here has no elsewhere zone", L.eval('AetherLedger_Tracker.ElsewhereZone(204)'), None)
expect("another zone's quest stays off", 205 in shown, False)
# a red quest just accepted: the game tracks it, we take it off and say why
L.execute('table.insert(WATCH, 1, 206); EV(nil, "QUEST_ACCEPTED", 206); for _, f in ipairs(TIMERS) do f() end; AetherLedger_Tracker.Apply()')
shown = [L.eval('WATCH[%d]' % i) for i in range(1, L.eval('#WATCH') + 1)]
expect("the red quest is off the tracker", 206 in shown, False)
out = "\n".join(L.eval('OUT').values())
expect("chat says why, once", out.count("Horde Trauma is red for you right now (level 45)"), 1)
L.execute('AetherLedger_Tracker.Apply()')
out = "\n".join(L.eval('OUT').values())
expect("...and not again on later refreshes", out.count("Horde Trauma is red"), 1)
# A Forever-only quest our data doesn't know (no AetherLedger_Zones entry):
# the game's turn-in waypoint says where it goes (Riverglades, map 2001).
L.execute('''
MAPS[2001] = "The Riverglades"
table.insert(LOG, {id=207, title="Lost Shipping Crate", level=38, done=true})
C_QuestLog.GetNextWaypoint = function(id) if id == 207 then return 2001, 0.5, 0.5 end end
WATCH = {}
AetherLedger_Tracker.Apply()
''')
shown = [L.eval('WATCH[%d]' % i) for i in range(1, L.eval('#WATCH') + 1)]
expect("a quest our data doesn't know: the game's turn-in waypoint puts it at the bottom", shown[-2:] == [203, 207] or shown[-2:] == [207, 203], True)
expect("...with the right zone name", L.eval('AetherLedger_Tracker.ElsewhereZone(207)'), "The Riverglades")

# 1.8.3: a finished quest from ANOTHER zone (Supply and Demand, Stranglethorn
# 1434) handed in elsewhere shows too, with its zone (user, Nov 25 06:41).
L.execute('''
MAPS[1434] = "Stranglethorn Vale"
table.insert(LOG, {id=208, title="Supply and Demand", level=31, done=true})
AetherLedger_Zones[208] = {1434, 1434}
AetherLedger_Tracker.Apply()
''')
shown = [L.eval('WATCH[%d]' % i) for i in range(1, L.eval('#WATCH') + 1)]
expect("a finished quest from another zone sits in the hand-in list", 208 in shown, True)
expect("...with its hand-in zone", L.eval('AetherLedger_Tracker.ElsewhereZone(208)'), "Stranglethorn Vale")
expect("...below the quests for here", shown.index(208) > shown.index(202), True)
expect("an unfinished quest from another zone still stays off", 205 in shown, False)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
