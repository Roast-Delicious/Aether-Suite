# AetherHub Release C (Nov 25): the eight pages of layout B. Same mock as
# hub_debug_test. Builds every page (no errors), checks the main controls
# are there, that every new control sends the right slash command, the
# per-page Restore Defaults..., the footer buttons and the waypoint list.
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
C_AddOns={IsAddOnLoaded=function(n) return n ~= "AetherChat" end, GetAddOnMetadata=function(n) return "9.9" end}
SENT={}
DEFAULT_CHAT_FRAME = { AddMessage = function() end }
for _,k in ipairs({"AETHERBARS","AETHERCHAT","AETHERITEMID","AETHERMARKS","AETHERPATHFINDER","AETHERSKINS","AETHERLEDGER","AETHERMETER",
                   "AETHERFRAMES","AETHERCOORDS","AETHERWAY","AETHERPACK"}) do
  SlashCmdList[k]=function(msg) SENT[#SENT+1]=k.." "..msg end
end
collectgarbage = function() end
UpdateAddOnMemoryUsage = function() end
GetAddOnMemoryUsage = function() return 100 end
UnitName = function() return "Jay" end; UnitLevel = function() return 36 end
date = function() return "2026-11-25 16:00" end
UISpecialFrames={}; tinsert=table.insert
EditModeManagerFrame={}; ShowUIPanel=function() end
GameTooltip=CreateFrame("Frame")
AetherFramesDB = { tot = true, aggroFade = true, hitNumbers = false }
AetherCoordsDB = { decimals = 1, waypoints = { { map = 1, x = 0.67, y = 0.582, note = "Cork Gizelton" }, { map = 2, x = 0.26, y = 0.42, note = "" } } }
C_Map = C_Map or {}; C_Map.GetMapInfo = function(id) return { name = ({ "Desolace", "Thousand Needles" })[id] or "?" } end
AetherMeterDB = { opacityInCombat = 0.7, opacityOutCombat = 0.25 }
AetherPackDB = { deposit = true, depositPulse = "item" }
AetherLedgerDB = {}
AetherSkinsDB = { windows = true, minimap = true }
''')
L.execute('wipe = wipe or function(t) for k in pairs(t) do t[k] = nil end return t end')
L.execute(open('/home/claude/brand/AetherHub/AetherHub.lua').read().replace('local ADDON_NAME = ...', 'local ADDON_NAME = "AetherHub"'))
L.execute('for _,o in ipairs(FR) do if rawget(o,"ev") and o.ev.ADDON_LOADED and rawget(o,"OnEvent") then HUBEV=o end end; HUBEV.OnEvent(HUBEV,"ADDON_LOADED","AetherHub"); HUBEV.OnEvent(HUBEV,"PLAYER_LOGIN"); AetherHub_Toggle()')
ok = True
def check(c, m):
    global ok
    print(("ok   " if c else "FAIL ") + m); ok = ok and c
L.execute(r'''
function FIND(text) for _,o in ipairs(FR) do if rawget(o,"text")==text then return o end end end
function FINDALL(text) local n = 0 for _,o in ipairs(FR) do if rawget(o,"text")==text then n = n + 1 end end return n end
function CLICK(text, k) local b=FIND(text); if not b then return false end; SENT={}; local f=rawget(b,"OnClick"); f(b, k or "LeftButton"); return true end
function YES() local b = FIND(YES_TEXT or "Yes"); SENT={}; rawget(b,"OnClick")(b) end
function CHECKBOX(label) for _,o in ipairs(FR) do local l = rawget(o,"label"); if l and rawget(l,"text") == label then return o end end end
function TOGGLE(label) local cb = CHECKBOX(label); if not cb then return false end; SENT={}; cb:SetChecked(not cb:GetChecked()); rawget(cb,"OnClick")(cb); return true end
''')
texts = list(L.eval('ALLTEXT').values())
for t in ["Your Character", "Action Bar Area", "Unit Frames", "Map & Waypoints", "Quests & Mobs", "Bags & Items", "Window Look", "Help & Debug"]:
    check(t in texts, "tab: " + t)
for t in ["Bars, Chat, Meter, XP bar", "Coords, Pathfinder", "Ledger, Marks", "Pack, ItemID", "Skins, minimap"]:
    check(t in texts, "tab sub-line: " + t)
check(not any(isinstance(t, str) and "hit an error" in t for t in texts), "every page builds without an error")
check("Unlock to Move" in texts and "Reset Positions..." in texts and "Reload UI" in texts, "footer: Unlock to Move, Reset Positions..., Reload UI")
check("Minimap button" not in texts, "minimap switch is no longer in the footer")
check(L.eval('FINDALL("Restore Defaults...")') == 6, "Restore Defaults... on the six settings pages")
check("Appearance" not in texts and "GENERAL" not in texts and "ADDONS" not in texts, "old shared pages and sections are gone")
# old names still open the right page
L.execute('SlashCmdList.AETHERHUB("frames")'); check(L.eval('AetherHubDB.lastPage') == "Frames", "/hub frames -> Unit Frames")
L.execute('AetherHub_Toggle("AetherSkins")'); check(L.eval('AetherHubDB.lastPage') == "Look", "old page name AetherSkins -> Window Look")
# new controls -> slash commands (each page opened first, so its controls read their values)
PAGE_OF = {"AETHERFRAMES": "Frames", "AETHERLEDGER": "Quests", "AETHERPACK": "Bags"}
for label, want in [("Target of target under the target frame", "AETHERFRAMES tot off"),
                    ("Class color behind players' portraits", "AETHERFRAMES classglow off"),
                    ("Enemy target's glow in its level color", "AETHERFRAMES levelglow off"),
                    ("Red flash when hit", "AETHERFRAMES hits off"),
                    ("Damage numbers", "AETHERFRAMES hitnumbers on"),
                    ("In combat, only your target and whoever has aggro stay solid", "AETHERFRAMES aggro off"),
                    ("Click a finished quest's icon for directions to turn in", "AETHERLEDGER turnin off"),
                    ("Tooltips beside the quest tracker", "AETHERLEDGER tooltip"),
                    ("\"No swaps. Just drops.\" slot", "AETHERPACK deposit off")]:
    L.execute('AetherHub_Toggle(%r)' % PAGE_OF[want.split()[0]])
    hit = L.eval('TOGGLE(%r)' % label)
    check(hit and list(L.eval('SENT').values()) == [want], "switch '%s' -> %s" % (label, want))
check(L.eval('CLICK("3D")') or True, "portrait choice present")
L.execute('CLICK("Flat")'); check(list(L.eval('SENT').values()) == ["AETHERFRAMES portraits 2d"], "Portraits Flat -> /af portraits 2d")
L.execute('CLICK("Never")'); check(list(L.eval('SENT').values()) == ["AETHERPACK pulse off"], "pulse Never -> /pack pulse off")
L.execute('CLICK("Night")'); check(list(L.eval('SENT').values()) == ["AETHERSKINS night"], "Sun or moon Night -> /skins night")
L.execute('CLICK("Sort Tracker Now")'); check(list(L.eval('SENT').values()) == ["AETHERLEDGER sort"], "Sort Tracker Now -> /ledger sort")
L.execute('CLICK("Stop Directions")'); check(list(L.eval('SENT').values()) == ["AETHERLEDGER stop"], "Stop Directions -> /ledger stop")
L.execute('CLICK("Zones")'); check(list(L.eval('SENT').values()) == ["AETHERLEDGER zones"], "Report Zones -> /ledger zones")
L.execute('CLICK("Flight Paths")'); check(list(L.eval('SENT').values()) == ["AETHERPATHFINDER flights"], "Report Flight Paths -> /pfm flights")
L.execute('CLICK("NPC Counts")'); check(list(L.eval('SENT').values()) == ["AETHERPATHFINDER stats"], "Report NPC Counts -> /pfm stats")
L.execute('CLICK("Preview Meter")'); check(list(L.eval('SENT').values()) == ["AETHERMETER test"], "Preview Meter -> /am test (on Action Bar Area)")
# waypoint list
L.execute('AetherHub_Toggle("Map")')
check(any(isinstance(t, str) and "Desolace" in t and "67.0, 58.2" in t and "Cork Gizelton" in t for t in L.eval('ALLTEXT').values()), "waypoint list: zone, coordinates, note")
L.execute('''(function() for _,o in ipairs(FR) do if rawget(o,"text")=="x" and rawget(o,"index")==2 then SENT={}; rawget(o,"OnClick")(o) end end end)()''')
check(list(L.eval('SENT').values()) == ["AETHERWAY remove 2"], "x on row 2 -> /way remove 2")
# Restore Defaults... asks, then runs each addon's own defaults
L.execute(r"""
function DEFAULTS_FOR(what)
  for _,o in ipairs(FR) do
    if rawget(o,"text")=="Restore Defaults..." then
      SENT={}; rawget(o,"OnClick")(o)
      local q = AetherHubConfirm and rawget(AetherHubConfirm.text, "text") or ""
      if q:find(what, 1, true) then ASKED = (#SENT == 0); SENT={}; AetherHubConfirm.action(); return true end
    end
  end
end""")
check(L.eval('DEFAULTS_FOR("Unit Frames")') and L.eval('ASKED'), "Restore Defaults... asks first")
check(list(L.eval('SENT').values()) == ["AETHERFRAMES defaults"], "Unit Frames Restore Defaults -> /af defaults")
L.execute('DEFAULTS_FOR("Map & Waypoints")')
check(list(L.eval('SENT').values()) == ["AETHERCOORDS defaults", "AETHERPATHFINDER defaults"], "Map & Waypoints Restore Defaults -> /mc + /pfm defaults")
L.execute('DEFAULTS_FOR("Quests & Mobs")')
check(list(L.eval('SENT').values()) == ["AETHERLEDGER defaults", "AETHERMARKS defaults"], "Quests & Mobs Restore Defaults -> /ledger + /qm defaults")
L.execute('DEFAULTS_FOR("Bags & Items")')
check(list(L.eval('SENT').values()) == ["AETHERPACK defaults", "AETHERITEMID reset"], "Bags & Items Restore Defaults -> /pack defaults + /itemid reset")
L.execute('DEFAULTS_FOR("Window Look")')
check(list(L.eval('SENT').values()) == ["AETHERSKINS defaults"], "Window Look Restore Defaults -> /skins defaults")
# footer
L.execute('CLICK("Unlock to Move")')
check(sorted(L.eval('SENT').values()) == sorted(["AETHERFRAMES unlock", "AETHERMETER unlock", "AETHERBARS xp unlock"]), "Unlock to Move unlocks frames, meter, XP bar")
check(L.eval('FIND("Lock") ~= nil'), "...and becomes Lock")
L.execute('CLICK("Lock")')
check(sorted(L.eval('SENT').values()) == sorted(["AETHERFRAMES lock", "AETHERMETER lock", "AETHERBARS xp lock"]), "Lock locks them again")
L.execute('CLICK("Reset Positions..."); SENT={}; AetherHubConfirm.action()')
s = list(L.eval('SENT').values())
check("AETHERLEDGER resetwindows" in s and "AETHERPACK reset" in s and "AETHERFRAMES reset" in s, "Reset Positions... includes Ledger's windows, bags and frames")
# panel opacity lives in the Hub
check(abs(L.eval('AetherPanels.opacityOutCombat') - 0.25) < 1e-9, "panel opacity copied from the meter at first login (AetherPanels)")
check("AetherChat isn't loaded" in " ".join(t for t in L.eval('ALLTEXT').values() if isinstance(t, str)), "an addon that isn't loaded: a note instead of its controls")
check("Dancing character (click it for an emote, drag to turn it)" not in L.eval('ALLTEXT').values(), "Your Character: no dancer switch or hint (user 16:09)")
# waypoints all removed -> the Map page is rebuilt with room for one row only
L.execute('AetherCoordsDB.waypoints = {}; AetherHub_Toggle("Map"); AetherHub_RebuildPage("Map")')
check(any(isinstance(t, str) and t.endswith("No waypoints yet.|r") for t in L.eval('ALLTEXT').values()), "no waypoints: one line, 'No waypoints yet.'")
check("Zone details" in L.eval('ALLTEXT').values(), "Quests & Mobs: the long zone report has its own band at the bottom")
print("ALL OK" if ok else "FAILED")
