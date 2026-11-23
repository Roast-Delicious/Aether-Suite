# AetherHub: General pages (Appearance, Fading, Layout), sidebar, links, and moved controls.
src=open('ledger_full_test.py').read()
pre=src.split("for f in ['AetherHub/AetherHub.lua'")[0]
exec(pre)
L.execute(r'''
C_AddOns={IsAddOnLoaded=function() return true end, GetAddOnMetadata=function(n) return "9.9" end}
SENT={}
for _,k in ipairs({"AETHERFRAMES","AETHERMETER","AETHERBARS","AETHERCHAT","AETHERPACK","AETHERCOORDS"}) do
  SlashCmdList[k]=function(msg) SENT[#SENT+1]=k.." "..msg end
end
AetherBarsDB={trim=true, alpha=0.8, combat=true}; AetherChatDB={fontSize=14}; AetherMeterDB={opacityOutCombat=0.4}
AetherFramesDB={scale=0.9, alpha=0.5}; AetherPackDB={scale=1}
UISpecialFrames={}; tinsert=table.insert
EditModeManagerFrame={}; SHOWN_PANEL=nil; ShowUIPanel=function(f) SHOWN_PANEL=f end
GameTooltip=CreateFrame("Frame"); 
''')
L.execute(open('/home/claude/brand/AetherHub/AetherHub.lua').read().replace('local ADDON_NAME = ...','local ADDON_NAME = "AetherHub"'))
L.execute('for _,o in ipairs(FR) do if rawget(o,"ev") and o.ev.ADDON_LOADED and rawget(o,"OnEvent") then HUBEV=o end end; HUBEV.OnEvent(HUBEV,"ADDON_LOADED","AetherHub"); AetherHub_Toggle()')
ok=True
def check(c,m):
    global ok
    print(("ok   " if c else "FAIL ")+m); ok=ok and c
L.execute(r'''
function FIND(text) for _,o in ipairs(FR) do if rawget(o,"text")==text then return o end end end
function CLICK(text) local b=FIND(text); if not b then return false end; SENT={}; local f=rawget(b,"OnClick"); f(b,"LeftButton"); return true end
''')
texts=list(L.eval('ALLTEXT').values())
for t in ["GENERAL","ADDONS","Appearance","Fading","Layout","Your character"]:
    check(t in texts, "sidebar/page shows %r"%t)
for t in ["Behind your action bars","Behind your chat","Unit frames (yours, pet, target, party)","Bag window","Chat text",
          "Solid in combat","Solid under your mouse","Faces fade too","Unlock to Move","Lock","Open Edit Mode",
          "Chat fits the space to the left of your bars","Meter docks to the right of your bars","Align Bars...","Reset All Positions...","Preview Meter","Reset Meter Position","Clear Learned Recipes...","Reset Pet Frame Position","Open Bags"]:
    check(t in texts, "control: %s"%t)
# moved: these should no longer be on the addon tabs
for t in ["Bar transparency when idle","Aether panel behind the chat","Opacity in combat","Frames out of combat","Move Frames","Dock beside the action bars (right side)","Fit chat into the space beside my action bars"]:
    check(t not in texts, "moved off its addon tab: %s"%t)
check(L.eval('CLICK("Unlock to Move")') and list(L.eval('SENT').values())==["AETHERFRAMES unlock","AETHERMETER unlock","AETHERBARS xp unlock"], "Unlock to Move -> %s"%list(L.eval('SENT').values()))
check(L.eval('CLICK("Lock")') and list(L.eval('SENT').values())==["AETHERFRAMES lock","AETHERMETER lock","AETHERBARS xp lock"], "Lock")
L.execute('CLICK("Open Edit Mode")'); check(L.eval('SHOWN_PANEL==EditModeManagerFrame'), "Edit Mode opens Blizzard's Edit Mode")
# Reset All asks first: click Yes on the confirm box
L.execute('CLICK("Reset All Positions..."); SENT={}; local y=FIND(YES or "Yes"); rawget(y,"OnClick")(y)')
sent=list(L.eval('SENT').values())
check(set(sent)=={"AETHERFRAMES reset","AETHERMETER reset","AETHERPACK reset","AETHERCOORDS reset","AETHERBARS xp reset"}, "Reset All Positions (after Yes) -> %s"%sent)
# links jump to pages
L.execute('CLICK("Fading  >")'); check(L.eval('AetherHubDB.lastPage')=="Fading", "link button opens the Fading page")
for old in ["Move Everything","Run Test","Pet Under Mine","Readout Back Under Minimap","Forget All NPCs","Record quest log","Open AetherPack","Move / Resize XP Bar"]:
    check(old not in texts, "old name gone: %s"%old)
# ItemID split: Restore Defaults keeps recipes, Clear Learned Recipes forgets them
SlashOK=True
L.execute('SlashCmdList.AETHERITEMID=function(m) SENT[#SENT+1]="AETHERITEMID "..m end')
L.execute('CLICK("Clear Learned Recipes..."); SENT={}; local y=FIND(YES or "Yes"); rawget(y,"OnClick")(y)')
check(list(L.eval('SENT').values())==["AETHERITEMID reset recipes"], "Clear Learned Recipes -> %s"%list(L.eval('SENT').values()))
print("ALL OK" if ok else "SOME FAILED")
