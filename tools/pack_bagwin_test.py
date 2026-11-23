import lupa.lua51 as l
L = l.LuaRuntime(unpack_returned_tuples=True)
print(L.execute('local f,e = loadstring(...); return e or "compiles"', open('/home/claude/brand/AetherPack/AetherPack.lua').read()))
L.execute(r'''
OUT={}; print=function(m) OUT[#OUT+1]=tostring(m) end
function Obj() return setmetatable({shown=false}, {__index=function(t,k)
  if k=="Show" then return function(s) s.shown=true; local f=rawget(s,"OnShow"); if f then f(s) end end end
  if k=="Hide" then return function(s) local was=s.shown; s.shown=false; local f=rawget(s,"OnHide"); if was and f then f(s) end end end
  if k=="IsShown" then return function(s) return s.shown end end
  if k=="SetShown" then return function(s,v) s.shown=v and true or false end end
  if k=="SetText" then return function(s,x) s.text=x end end
  if k=="GetText" then return function(s) return s.text end end
  if k=="SetID" then return function(s,v) s.id=v end end
  if k=="GetID" then return function(s) return s.id end end
  if k=="SetAlpha" then return function(s,a) s.alpha=a end end
  if k=="SetPoint" then return function(s,a,b,c,x,y) s.pos={x,y} end end
  if k=="SetSize" then return function(s,w,h) s.w=w; s.h=h end end
  if k=="SetWidth" then return function(s,w) s.w=w end end
  if k=="CreateFontString" or k=="CreateTexture" then return function() return Obj() end end
  if k=="SetScript" then return function(s,n,f) s[n]=f end end
  if k=="HookScript" then return function(s,n,f) local o=rawget(s,n); s[n]=function(...) if o then o(...) end f(...) end end end
  if type(k)=="string" and k:match("^%u") then return function() end end
  return nil end}) end
FR={}; CreateFrame=function(kind, name, parent, tmpl) local o=Obj(); o.kind=kind; o.tmpl=tmpl; o.parent=parent; FR[#FR+1]=o; if name then _G[name]=o end; return o end
UIParent=Obj(); UISpecialFrames={}; tinsert=table.insert; GameTooltip=Obj(); SlashCmdList={}
TIMERS={}; C_Timer={After=function(t,fn) TIMERS[#TIMERS+1]=fn end}
function Fire() for _=1,40 do local t=TIMERS; TIMERS={}; if #t==0 then break end for _,f in ipairs(t) do f() end end end
COMBAT=false; InCombatLockdown=function() return COMBAT end
strlower=string.lower; strtrim=function(s) return (s:gsub("^%s+",""):gsub("%s+$","")) end
CopyTable=function(t) local o={} for k,v in pairs(t) do o[k]=v end return o end
GetMoney=function() return 123456 end
CLASS='HUNTER'; UnitClass=function() return 'Hunter', CLASS end
MainMenuBarBackpackButton=Obj(); FormatLargeNumber=function(n) return tostring(n) end
GetCoinTextureString=function(c) return c.."c" end
SetItemButtonTexture=function(b,t) b.icon=t end; SetItemButtonCount=function(b,c) b.count=c end
SetItemButtonDesaturated=function() end; SetItemButtonQuality=function(b,q) b.q=q end
hooksecurefunc=function(name, fn) local o=_G[name]; _G[name]=function(...) local r=o(...); fn(...); return r end end
ToggleAllBags=function() end; OpenAllBags=function() end; CloseAllBags=function() end; ToggleBackpack=function() end; ToggleBag=function() end; OpenBackpack=function() end; CloseBackpack=function() end
-- bags: 0 backpack 16 slots, 1 = quiver 12 slots, 2 = 10 slots
ITEMS = {
  [0]={ {1,"Roasted Quail",0,1,4604,5}, {2,"Heavy Leather",7,1,4234,8}, {3,"Ragged Wolf Tail",15,0,1,1,30}, {4,"Cutthroat's Hat",4,2,8888,1},
        {5,"Bloodscalp Tusk",12,1,1524,4}, {6,"Hearthstone",15,1,6948,1}, {7,"Broken Fang",15,0,2,3,10}, {8,"Ornate Bow",2,3,9999,1} },
  [1]={ {1,"Jagged Arrow",6,1,3030,200}, {2,"Jagged Arrow",6,1,3030,200} },
  [2]={ {1,"Healing Potion",0,1,929,3}, {2,"Recipe: Murloc Fin Soup",9,1,3681,1} },
}
SLOTS={[0]=16,[1]=12,[2]=10,[3]=0,[4]=0}
local function find(bag,slot) for _,it in ipairs(ITEMS[bag] or {}) do if it[1]==slot then return it end end end
C_Container={
  GetContainerNumSlots=function(b) return SLOTS[b] or 0 end,
  GetContainerNumFreeSlots=function(b) local n=0; return n, b==1 and 1 or 0 end,
  GetContainerItemInfo=function(b,s) local it=find(b,s); if not it then return nil end
     return {iconFileID=100+it[5], stackCount=it[6], quality=it[4], hyperlink="|cff|Hitem:"..it[5].."|h["..it[2].."]|h|r", itemID=it[5]} end,
  GetContainerItemQuestInfo=function(b,s) return {isQuestItem=false} end,
  UseContainerItem=function(b,s) SOLD=SOLD or {}; SOLD[#SOLD+1]=find(b,s)[2]; for i,it in ipairs(ITEMS[b]) do if it[1]==s then table.remove(ITEMS[b],i) end end end,
}
local CLS={} for _,list in pairs(ITEMS) do for _,it in ipairs(list) do CLS[it[5]]=it[3] end end
C_Item={GetItemInfoInstant=function(id) return id,nil,nil,nil,nil,CLS[id],0 end,
        GetItemInfo=function(link) local id=tonumber(link:match("item:(%d+)")); local p=0; for _,list in pairs(ITEMS) do for _,it in ipairs(list) do if it[5]==id then p=it[7] or 0 end end end; return nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,p end}
''')


import sys
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "plain"
L.execute("""
CLASS='MAGE'; Enum={BagIndex={ReagentBag=5}}
ITEMS={[0]={{1,'Linen Cloth',7,1,2589,10}}, [2]={{1,'Healing Potion',0,1,929,3},{2,'Silk Cloth',7,1,4306,4}}, [5]={{1,'Peacebloom',7,1,2447,5}}}
SLOTS={[0]=16,[1]=6,[2]=10,[3]=0,[4]=0,[5]=12,[6]=24}
C_Container.GetContainerNumFreeSlots=function(b) return 0, 0 end
C_Container.GetBagName=function(b) return ({[1]='Small Pouch',[2]='Linen Bag',[5]='Herb Pouch'})[b] end
CLS={} for _,list in pairs(ITEMS) do for _,it in ipairs(list) do CLS[it[5]]=it[3] end end
ContainerFrame1=Obj(); ContainerFrame1.id=0; ContainerFrame1.GetID=function(s) return s.id end
ToggleBag=function(id) ContainerFrame1.id=id; ContainerFrame1:Show() end
OpenBag=function(id) ContainerFrame1.id=id; ContainerFrame1:Show() end
ToggleBackpack=function() ContainerFrame1.id=0; ContainerFrame1:Show() end
""")
if VARIANT == "allviatogglebag":   # a client whose ToggleAllBags calls ToggleBag for every bag
    L.execute("ToggleAllBags=function() ToggleBackpack(); for i=1,4 do ToggleBag(i) end end")
else:
    L.execute("ToggleAllBags=function() ToggleBackpack(); for i=1,4 do OpenBag(i) end end")
for i in range(4):
    L.execute(f"CharacterBag{i}Slot=Obj()")
L.execute("CharacterReagentBag0Slot=Obj()")
L.execute(open('/home/claude/brand/AetherPack/AetherPack.lua').read())
L.execute('for _,f in ipairs(FR) do if rawget(f,"OnEvent") then EV=f end end; EV.OnEvent(EV,"ADDON_LOADED","AetherPack"); EV.OnEvent(EV,"PLAYER_LOGIN"); Fire()')
L.execute("""
function Click(slotName, bag, mouse) local b=_G[slotName]; b.PreClick(b, mouse or "LeftButton"); if not (CursorHasItem and CursorHasItem()) then ToggleBag(bag) end; b.PostClick(b, mouse or "LeftButton"); Fire() end
function W(bag) local w=_G["AetherPackBag"..bag.."Frame"]; return w and w.shown or false end
function Combined() return AetherPackFrame.shown end
""")
fails = []
def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
E = L.eval
check("nothing open at start", not E("Combined()") and not E("W(2)"))
L.execute("CF_O=CreateFrame; CreateFrame=function(...) local o=CF_O(...); return o end")
L.execute('Click("CharacterBag1Slot", 2)')
check("bag slot click opens that bag only", E("W(2)") and not E("Combined()"))
check("Blizzard's bag window stays closed", not E("ContainerFrame1.shown"))
check("title is the bag's name", E("AetherPackBag2Frame.title.text") == "Linen Bag")
check("count shows used/total", E("AetherPackBag2Frame.count.text") == "2/10")
L.execute("N=0 for s,b in pairs(AetherPackBag2Frame.buttons) do if b.shown then N=N+1 end end")
check("one button per slot", E("N") == 10)
check("buttons find their bag via the holder ID", E("AetherPackBag2_1.parent.id") == 2)
check("slot 5 starts row 2", E("AetherPackBag2_5.pos[1]") == 10 and E("AetherPackBag2_5.pos[2]") == -71)
check("stacked at lower right", E("AetherPackBag2Frame.pos[1]") == -20 and E("AetherPackBag2Frame.pos[2]") == 110)
check("Esc closes it", E("(function() for _,n in ipairs(UISpecialFrames) do if n=='AetherPackBag2Frame' then return true end end end)()") == True)
L.execute('Click("CharacterReagentBag0Slot", 5)')
check("second bag opens too", E("W(5)") and E("W(2)"))
check("Blizzard's reagent bag window stays closed", not E("ContainerFrame1.shown"))
check("second window stacks above the first", E("AetherPackBag5Frame.pos[2]") == 110 + E("AetherPackBag2Frame.h") + 16)
L.execute('Click("CharacterBag1Slot", 2)')
check("clicking again closes it", not E("W(2)") and E("W(5)"))
check("the rest close the gap", E("AetherPackBag5Frame.pos[2]") == 110)
L.execute("ToggleAllBags(); Fire()")
check("bag key opens the combined window", E("Combined()") and not E("W(2)"))
check("bag key leaves open bag windows alone when opening", E("W(5)"))
L.execute("ToggleAllBags(); Fire()")
check("bag key again closes everything", not E("Combined()") and not E("W(5)"))
L.execute("ToggleBackpack(); Fire()")
check("backpack button opens the combined window", E("Combined()") and not E("W(2)"))
L.execute("CloseAllBags(); Fire()")
check("close all closes it", not E("Combined()"))
L.execute("ToggleBag(3); Fire()")
check("single-bag key (Toggle Bag) opens that bag", E("W(3)") if E("SLOTS[3]") > 0 else True)
L.execute("ToggleBag(1); Fire()")
check("single-bag key for bag 1", E("W(1)") and not E("Combined()"))
L.execute("ToggleBag(1); Fire()")
L.execute("CursorHasItem=function() return true end")
L.execute('Click("CharacterBag0Slot", 1)')
check("dropping an item on a bag slot opens nothing", not E("W(1)") and not E("Combined()"))
L.execute("CursorHasItem=nil")
L.execute('Click("CharacterBag0Slot", 1, "RightButton")')
check("right-click acts like Blizzard's (toggles that bag)", E("W(1)") and not E("Combined()"))
L.execute("ToggleBag(1); Fire(); ToggleBag(1); Fire()")
L.execute("ToggleBag(6); Fire()")
check("bank bags stay Blizzard's", not E("Combined()") and E("_G['AetherPackBag6Frame']") is None)
L.execute('COMBAT=true; Click("CharacterBag2Slot", 3)')
L.execute('Click("CharacterBag3Slot", 4)')
L.execute("SLOTS[3]=8")
L.execute('Click("CharacterBag2Slot", 3)')
check("in combat a new bag window waits", not E("W(3)") and any("fight ends" in x for x in E("OUT").values()))
L.execute('COMBAT=false; EV.OnEvent(EV,"PLAYER_REGEN_ENABLED"); Fire()')
check("it opens when the fight ends", E("W(3)"))
L.execute('SLOTS[3]=0; EV.OnEvent(EV,"BAG_UPDATE_DELAYED"); Fire()')
check("a bag taken off closes its window", not E("W(3)"))
L.execute('Click("CharacterBag1Slot", 2); SLOTS[2]=14; EV.OnEvent(EV,"BAG_UPDATE_DELAYED"); Fire()')
check("a bigger bag gets more buttons", E("AetherPackBag2Frame.count.text") == "2/14" and E("AetherPackBag2_14.shown"))
L.execute('ToggleAllBags(); Fire(); AetherPackSearch:SetText("zzz"); AetherPackSearch.OnTextChanged(AetherPackSearch); EV.OnEvent(EV,"ITEM_LOCK_CHANGED")')
check("combined search doesn't dim bag windows", E("AetherPackBag2_1.alpha") == 1)
L.execute('AetherPackDB.replace=false; ToggleAllBags(); Fire(); AetherPackDB.replace=true')
L.execute("ForceW=function(fs) return #(fs.text or '') * 7 end")
L.execute('local w=AetherPackBag5Frame; w.title.GetUnboundedStringWidth=ForceW; w.count.GetUnboundedStringWidth=ForceW; C_Container.GetBagName=function() return "Linen Reagent Bag" end; ToggleBag(5); Fire(); ToggleBag(5); Fire()')
check("window widens to fit a long bag name", E("AetherPackBag5Frame.w") >= 10 + 17*7 + 10 + 4*7 + 6 + 24)
print("FAILED:", fails) if fails else print("all passed (" + VARIANT + ")")
sys.exit(1 if fails else 0)
