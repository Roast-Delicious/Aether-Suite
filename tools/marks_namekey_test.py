from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
pre = open('marks_test.py').read().split("L.execute(open('/home/claude/brand")[0]
exec(pre)
L.execute(open("/mnt/user-data/uploads/54619117#1--SavedVariables/AetherMarks.lua").read())
L.execute(r'''
C_QuestLog = { GetNumQuestLogEntries=function() return 1 end,
  GetInfo=function(i) return {questID=905, isHeader=false} end,
  GetQuestObjectives=function(id) return { {text="Unpopped Darkmist Eye: 0/40", type="item", finished=false, numRequired=40} } end }
''')
src = open('/home/claude/brand/AetherMarks/AetherMarks.lua').read()
src = src.replace("local function Classify(unit)", "function Classify(unit)")
L.execute(src, 'AetherMarks')
L.execute('EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMarks")')
def classify(desc, unit):
    L.execute('UNITS.nameplate1 = ' + unit)
    r = L.eval('{Classify("nameplate1")}')
    print(desc.ljust(58), "quest" if r[2] else "NOT quest")
print("before: name key saved:", L.eval('AetherMarksDB.learned["n:Darkmist Spider"] ~= nil'))
classify("far spider, ID hidden, name readable (the bug)", '{guid=nil, name="Darkmist Spider"}')
classify("you target one out of combat (ID and name readable)", '{guid="Creature-0-1-2-3-4376-0000AB", name="Darkmist Spider", quest="Unpopped Darkmist Eye: 3/40"}')
print("after: name key saved:", L.eval('AetherMarksDB.learned["n:Darkmist Spider"] ~= nil'))
classify("far spider again, ID hidden", '{guid=nil, name="Darkmist Spider"}')
classify("far spider, ID readable, no tooltip lines", '{guid="Creature-0-1-2-3-4376-0000CD", name="Darkmist Spider"}')
classify("unrelated mob, ID hidden", '{guid=nil, name="Mottled Raptor"}')
