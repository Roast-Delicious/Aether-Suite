# AetherHub: the Debug page (Nov 25). Same mock as skins_hub_test (built from
# ledger_full_test's, without the user's SavedVariables). Fakes each addon's
# slash command printing to the chat frame, then checks the page's buttons,
# that their output lands in the copy box, the memory report and the full report.
src = open('ledger_full_test.py').read()
pre = src.split("for f in ['AetherHub/AetherHub.lua'")[0]
pre = pre.replace('L.execute(open("/mnt/user-data/uploads/54619117#1--SavedVariables/AetherLedger.lua").read().replace("AetherLedgerDB","JAY",1))',
                  'L.execute("JAY={characters={Jay={completed={},questLog={}}}}")')
exec(pre)
L.execute(r'''
hooksecurefunc = function(obj, name, fn)
  if type(obj) == "string" then fn = name; name = obj; obj = _G end
  local orig = obj[name]
  if not orig then return end
  obj[name] = function(...) local r = { orig(...) }; fn(...); return unpack(r) end
end
''')
L.execute(r'''
C_AddOns={IsAddOnLoaded=function(n) return n ~= "AetherPack" end, GetAddOnMetadata=function(n) return "9.9" end}
SENT={}
CHATLINES={}
DEFAULT_CHAT_FRAME = { AddMessage = function(self, t) CHATLINES[#CHATLINES+1] = t end }
local _print = print
print = function(...) local t = table.concat({...}, " "); DEFAULT_CHAT_FRAME:AddMessage(t) end
for _,k in ipairs({"AETHERBARS","AETHERCHAT","AETHERITEMID","AETHERMARKS","AETHERPATHFINDER","AETHERSKINS","AETHERLEDGER","AETHERMETER"}) do
  SlashCmdList[k]=function(msg) SENT[#SENT+1]=k.." "..msg; print("|cff4da6ff"..k..":|r report line for "..msg) end
end
MEM = { AetherHub = 405.4, AetherCoords = 78, AetherLedger = 3152 }
collectgarbage = function() GC = (GC or 0) + 1 end
UpdateAddOnMemoryUsage = function() end
GetAddOnMemoryUsage = function(n) return MEM[n] or 100 end
UnitName = function() return "Jay" end; UnitLevel = function() return 36 end
date = function() return "2026-11-25 04:10" end
UISpecialFrames={}; tinsert=table.insert
EditModeManagerFrame={}; ShowUIPanel=function() end
GameTooltip=CreateFrame("Frame")
''')
L.execute(open('/home/claude/brand/AetherHub/AetherHub.lua').read().replace('local ADDON_NAME = ...', 'local ADDON_NAME = "AetherHub"'))
L.execute('for _,o in ipairs(FR) do if rawget(o,"ev") and o.ev.ADDON_LOADED and rawget(o,"OnEvent") then HUBEV=o end end; HUBEV.OnEvent(HUBEV,"ADDON_LOADED","AetherHub"); AetherHub_Toggle()')
ok = True
def check(c, m):
    global ok
    print(("ok   " if c else "FAIL ") + m); ok = ok and c
L.execute(r'''
function FIND(text) for _,o in ipairs(FR) do if rawget(o,"text")==text then return o end end end
function CLICK(text) local b=FIND(text); if not b then return false end; SENT={}; local f=rawget(b,"OnClick"); f(b,"LeftButton"); return true end
function BOXTEXT() for _,o in ipairs(FR) do if rawget(o,"multi") or rawget(o,"isBox") then return o.text end end end
''')
L.execute('SlashCmdList.AETHERHUB("debug")')
check(L.eval('AetherHubDB.lastPage') == "Debug", "/hub debug opens the Debug page")
texts = list(L.eval('ALLTEXT').values())
check("Help & Debug" in texts, "Help & Debug tab (Release C)")
for b in ["Bars", "Chat", "Marks", "Pathfinder", "Skins", "Ledger", "Zones", "Tracker", "NPC Counts", "Flight Paths",
          "Check Memory", "Show Window Dump", "Copy Full Report", "Clear"]:
    check(b in texts, "button: " + b)
box = L.eval('(function() for _,o in ipairs(FR) do if rawget(o,"text")=="Pick a report above, or Copy Full Report." then return o end end end)()')
check(box is not None, "copy box shows its starting hint")
L.execute('CHATLINES = {}')
check(L.eval('CLICK("Skins")') and list(L.eval('SENT').values()) == ["AETHERSKINS debug"], "Report: Skins runs /skins debug")
t = box.text
check("== AetherSkins debug ==" in t and "AETHERSKINS: report line for debug" in t, "its output is in the copy box")
check("|c" not in t and "|r" not in t, "color codes stripped for copying")
check(L.eval('#CHATLINES') == 1, "it still prints in chat too")
L.execute('CLICK("Ledger")')
check(list(L.eval('SENT').values()) == ["AETHERLEDGER status"] and "report line for status" in box.text, "Report: Ledger -> /ledger status, in the box")
L.execute('CLICK("Check Memory")')
t = box.text
check("== Memory ==" in t and "AetherLedger" in t and "3152 KB" in t and "AetherCoords" in t and "78 KB" in t, "Check Memory lists each addon's KB")
check("AetherPack" not in t, "addons that aren't loaded are left out")
check(L.eval('GC or 0') >= 1, "memory cleaned up first (real numbers, not garbage)")
L.execute('CLICK("Copy Full Report")')
t = box.text
for part in ["== Aether report ==", "Jay, level 36", "== Versions ==", "AetherHub 9.9", "AetherPack not loaded", "== Memory ==",
             "== AetherBars debug ==", "AETHERBARS: report line for debug", "== AetherSkins debug ==", "== AetherLedger status ==",
             "== AetherLedger zones ==", "== AetherPathfinder flights =="]:
    check(part in t, "full report has: " + part)
check(L.eval('CLICK("Clear")') and box.text == "", "Clear empties the box")
L.execute('CLICK("Show Window Dump")')
check("type /skins tree" in box.text, "Show Window Dump with nothing saved: explains")
L.execute('AetherSkinsDB = { lastTree = { name = "CharacterFrame", lines = { "Frame CharacterFrame 338x424", "  Frame .Inset 330x350" } } }; CLICK("Show Window Dump")')
check("== Window dump: CharacterFrame ==" in box.text and "Frame .Inset" in box.text, "Show Window Dump shows the saved dump")
L.execute('CLICK("Copy Full Report")')
check("== Window dump: CharacterFrame ==" in box.text, "full report includes the window dump")
print("ALL OK" if ok else "SOME FAILED")
raise SystemExit(0 if ok else 1)
