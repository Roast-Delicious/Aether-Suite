# AetherHub: the AetherSkins tab (Nov 24). Builds the Hub with the shared mock
# from ledger_full_test (its SavedVariables line swapped for an empty DB, so
# this test runs without the user's files), opens the AetherSkins page, and
# checks its controls and what they send to /skins.
src = open('ledger_full_test.py').read()
pre = src.split("for f in ['AetherHub/AetherHub.lua'")[0]
pre = pre.replace('L.execute(open("/mnt/user-data/uploads/54619117#1--SavedVariables/AetherLedger.lua").read().replace("AetherLedgerDB","JAY",1))',
                  'L.execute("JAY={characters={Jay={completed={},questLog={}}}}")')
exec(pre)
L.execute(r'''
JAY = JAY or {}
C_AddOns={IsAddOnLoaded=function() return true end, GetAddOnMetadata=function(n) return "9.9" end}
SENT={}
SlashCmdList.AETHERSKINS=function(msg) SENT[#SENT+1]="AETHERSKINS "..msg end
AetherSkinsDB={minimap=true}
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
''')
texts = list(L.eval('ALLTEXT').values())
check("Window Look" in texts, "sidebar has a Window Look tab (AetherSkins, Release C)")
check("Minimap in the Aether look (needs a reload)" in texts, "minimap switch on the page")
check("Blizzard's windows in the Aether look (needs a reload)" in texts, "windows switch on the page")
check("Reset Window Sizes..." in texts, "Reset Window Sizes... on the page")
L.execute('SlashCmdList.AETHERHUB("chat")'); before = L.eval('AetherHubDB.lastPage')
L.execute('SlashCmdList.AETHERHUB("skins")')
check(before == "ActionBar" and L.eval('AetherHubDB.lastPage') == "Look", "/hub skins opens Window Look")
print("ALL OK" if ok else "SOME FAILED")
raise SystemExit(0 if ok else 1)
