# The quest tracker's order: AetherLedger adds the highest level first so the
# lowest shows on top. Mocks a quest log whose watch list puts the newest
# quest first (how WoW Forever's tracker appears to behave), and one that
# appends, to check both settle without re-applying on every event.
import lupa.lua51 as l, sys
ok = True
def run(prepend):
    global ok
    L = l.LuaRuntime(unpack_returned_tuples=True)
    L.execute(r'''
    PREPEND = %s
    print = function() end
    UnitLevel = function() return 34 end; UnitName = function() return "Jay" end; GetRealmName = function() return "Forever" end; wipe = function(t) for k in pairs(t) do t[k] = nil end end
    InCombatLockdown = function() return false end
    UnitOnTaxi = function() return false end
    GetTime = function() return 1000 end
    C_Timer = { After = function(t, f) end }
    LOG = { {id=101, title="Panther Mastery", level=38}, {id=102, title="Hunting in Stranglethorn", level=31},
            {id=103, title="Raptor Mastery", level=36}, {id=104, title="Bloodscalp Ears", level=35},
            {id=105, title="Investigate the Camp", level=32} }
    WATCH = {}
    ADDS = 0
    C_QuestLog = {
      GetNumQuestLogEntries = function() return #LOG + 1 end,
      GetInfo = function(i) if i == 1 then return { isHeader = true, title = "Stranglethorn Vale" } end
                 local q = LOG[i-1]; return { questID = q.id, title = q.title, level = q.level } end,
      GetQuestWatchType = function(id) for _, w in ipairs(WATCH) do if w == id then return 0 end end end,
      IsComplete = function() return false end,
      AddQuestWatch = function(id) ADDS = ADDS + 1; if PREPEND then table.insert(WATCH, 1, id) else table.insert(WATCH, id) end end,
      RemoveQuestWatch = function(id) for i, w in ipairs(WATCH) do if w == id then table.remove(WATCH, i) end end end,
      GetNumQuestWatches = function() return #WATCH end,
      GetQuestIDForQuestWatchIndex = function(i) return WATCH[i] end,
      GetMaxNumQuestsCanWatch = function() return 25 end,
    }
    C_Map = { GetBestMapForUnit = function() return 1434 end,
              GetMapInfo = function(m) if m == 1434 then return { name = "Stranglethorn Vale", mapType = 3, parentMapID = 13 } end
                                       return { name = "Eastern Kingdoms", mapType = 2 } end }
    AetherLedger_Zones = { [101]={1434,1434}, [102]={1434,1434}, [103]={1434,1434}, [104]={1434,1434}, [105]={1434,1434} }
    CreateFrame = function() return setmetatable({}, { __index = function() return function() end end }) end
    hooksecurefunc = function() end
    ''' % ('true' if prepend else 'false'))
    L.execute(open('/home/claude/brand/AetherLedger/AetherLedger_Tracker.lua').read())
    L.execute('AetherLedger_Tracker.Apply()')
    # what the player sees: newest-on-top tracker shows WATCH in index order when prepending
    shown = [L.eval('WATCH[%d]' % i) for i in range(1, L.eval('#WATCH') + 1)]
    levels = {101:38, 102:31, 103:36, 104:35, 105:32}
    lv = [levels[i] for i in shown]
    if prepend:
        good = lv == sorted(lv)
        print(("ok  " if good else "FAIL"), "newest-on-top tracker: top to bottom", lv)
        ok &= good
    adds = L.eval('ADDS')
    L.execute('AetherLedger_Tracker.Apply(); AetherLedger_Tracker.Apply()')
    again = L.eval('ADDS') - adds
    print(("ok  " if again == 0 else "FAIL"), ("prepend" if prepend else "append") + ": no re-apply on later events (extra adds:", again, ")")
    ok &= again == 0
    L.execute('C_QuestLog.RemoveQuestWatch(104)')
    L.execute('AetherLedger_Tracker.Apply()')
    back = 104 in [L.eval('WATCH[%d]' % i) for i in range(1, L.eval('#WATCH') + 1)]
    print(("ok  " if back else "FAIL"), "a change by the game is put back")
    ok &= back
run(True); run(False)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
