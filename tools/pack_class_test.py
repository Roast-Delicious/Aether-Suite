import lupa.lua51 as l
L = l.LuaRuntime(unpack_returned_tuples=True)
print(L.execute('local f,e = loadstring(...); return e or "compiles"', open('/home/claude/brand/AetherPack/AetherPack.lua').read()))
L.execute(r'''
OUT={}; print=function(m) OUT[#OUT+1]=tostring(m) end
local function Obj() return setmetatable({shown=false}, {__index=function(t,k)
  if k=="Show" then return function(s) s.shown=true; local f=rawget(s,"OnShow"); if f then f(s) end end end
  if k=="Hide" then return function(s) s.shown=false end end
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
  if k=="SetTextColor" then return function(s,r,g,b) s.color={r,g,b} end end
  if k=="CreateAnimationGroup" or k=="CreateAnimation" then return function() local g=Obj(); g.Play=function(s) s.playing=true end; g.Stop=function(s) s.playing=false end; g.IsPlaying=function(s) return s.playing end; return g end end
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
GetMoney=function() return MONEY or 123456 end; NOW=0; GetTime=function() return NOW end
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
CLASS=sys.argv[1]
if CLASS=="WARLOCK":
    L.execute("""CLASS='WARLOCK'; ITEMS={[0]={{1,'Soul Shard',15,1,6265,1},{2,'Soul Shard',15,1,6265,1},{3,'Infernal Stone',15,1,5565,2},{4,'Linen Cloth',7,1,2589,10}},[1]={{1,'Soul Shard',15,1,6265,1}}}; SLOTS={[0]=16,[1]=20,[2]=0,[3]=0,[4]=0}
    C_Container.GetContainerNumFreeSlots=function(b) return 0, b==1 and 4 or 0 end""")
elif CLASS=="MAGE":
    L.execute("""CLASS='MAGE'; ITEMS={[0]={{1,'Rune of Teleportation',15,1,17031,1},{2,'Light Feather',15,1,17056,12},{3,'Arcane Powder',15,1,17020,2}}}; SLOTS={[0]=16,[1]=0,[2]=0,[3]=0,[4]=0}
    C_Container.GetContainerNumFreeSlots=function(b) return 0, 0 end""")
elif CLASS=="REAGENTBAG":
    L.execute("""CLASS='MAGE'; Enum={BagIndex={ReagentBag=5}}; ITEMS={[0]={{1,'Linen Cloth',7,1,2589,10}},[5]={{1,'Silk Cloth',7,1,4306,20},{2,'Peacebloom',7,1,2447,5}}}; SLOTS={[0]=16,[1]=0,[2]=0,[3]=0,[4]=0,[5]=10}
    C_Container.GetContainerNumFreeSlots=function(b) return 0, 0 end""")
elif CLASS=="SOULREAGENT":
    L.execute("""CLASS='WARLOCK'; Enum={BagIndex={ReagentBag=5}}; ITEMS={[0]={{1,'Linen Cloth',7,1,2589,10}},[5]={{1,'Soul Shard',15,1,6265,1}}}; SLOTS={[0]=16,[1]=0,[2]=0,[3]=0,[4]=0,[5]=20}
    C_Container.GetContainerNumFreeSlots=function(b) return 0, b==5 and 4 or 0 end""")
else:
    L.execute("""CLASS='WARRIOR'; GetInventoryItemID=function(u,s) if s==18 then return 2504 end end; ITEMS={[0]={{1,'Rough Arrow',6,1,2512,150},{2,'Linen Cloth',7,1,2589,10}}}; SLOTS={[0]=16,[1]=0,[2]=0,[3]=0,[4]=0}
    C_Container.GetContainerNumFreeSlots=function(b) return 0, 0 end""")
L.execute("""CLS={} for _,list in pairs(ITEMS) do for _,it in ipairs(list) do CLS[it[5]]=it[3] end end; CLS[2504]=2
local inst=C_Item.GetItemInfoInstant; C_Item.GetItemInfoInstant=function(id) if id==2504 then return id,nil,nil,nil,nil,2,2 end return id,nil,nil,nil,nil,CLS[id],0 end""")
L.execute(open('/home/claude/brand/AetherPack/AetherPack.lua').read())
L.execute('for _,f in ipairs(FR) do if rawget(f,"OnEvent") then EV=f end end; EV.OnEvent(EV,"ADDON_LOADED","AetherPack"); EV.OnEvent(EV,"PLAYER_LOGIN"); ToggleAllBags(); Fire()')
def sections():
    L.execute("""RES={} for _,f in ipairs(FR) do local t = rawget(f,"text"); t = type(t)=="table" and t.text or nil; if f.kind=="Button" and t and f.shown and f.parent==AetherPackFrame then RES[#RES+1]=t end end""")
    return [t.replace("|cff9d9d9d","").replace("|r","").replace("|cff4da6ff","") for t in L.eval('RES').values()]
print("==", CLASS)
for t in sections(): print("  ", t)
L.execute("""BARS={} local function hx(c) return c and string.format("#%02x%02x%02x",math.floor(c[1]*255+0.5),math.floor(c[2]*255+0.5),math.floor(c[3]*255+0.5)) or "?" end for _,b in ipairs(AetherPackFrame.bars) do if b.shown then BARS[#BARS+1]=b.label.text.." | "..(b.word.shown and (b.word.text.." "..hx(b.word.color)..(b.pulse.playing and " PULSING" or "").." + ") or "")..b.value.text.." "..hx(b.value.color) end end""")
for x in L.eval('BARS').values(): print("   bar:", x)
L.execute('for _,f in ipairs(FR) do end')
# Free slots layout: where the rows sit, and the class reagent line
print("rows at (x,y):", L.eval('(function() local t={} for _,b in ipairs(AetherPackFrame.bars) do if b.shown then t[#t+1]=tostring(b.pos[1])..","..tostring(b.pos[2]).." w"..tostring(b.w) end end return table.concat(t,"  ") end)()'), "| window", L.eval('AetherPackFrame.w'), "x", L.eval('AetherPackFrame.h'), "| deposit at", L.eval('AetherPackFrame.depositBox.pos[1]'), L.eval('AetherPackFrame.depositBox.pos[2]'))
print("reagent line:", L.eval('AetherPackFrame.reagentLine.shown'), L.eval('AetherPackFrame.reagentLine.text'))
print("deposit shown:", L.eval('AetherPackFrame.depositBox.shown'))
