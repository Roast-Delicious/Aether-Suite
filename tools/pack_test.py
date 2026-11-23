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
ToggleAllBags=function() ContainerFrameCombinedBags:Show() end; ContainerFrameCombinedBags=Obj(); OpenAllBags=function() end; CloseAllBags=function() end; ToggleBackpack=function() end; ToggleBag=function() end; OpenBackpack=function() end; CloseBackpack=function() end
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
L.execute(open('/home/claude/brand/AetherPack/AetherPack.lua').read())
L.execute('for _,f in ipairs(FR) do if rawget(f,"OnEvent") then EV=f end end; EV.OnEvent(EV,"ADDON_LOADED","AetherPack"); EV.OnEvent(EV,"PLAYER_LOGIN")')
def sections():
    L.execute('''RES={} for _,f in ipairs(FR) do local t = rawget(f,"text"); t = type(t)=="table" and t.text or nil; if f.kind=="Button" and t and f.shown and f.parent==AetherPackFrame then RES[#RES+1]=t end end''')
    return [t.replace("|cff9d9d9d","").replace("|r","").replace("|cff4da6ff","") for t in L.eval('RES').values()]
print("== press B (Blizzard opens 3 bags -> 3 calls)")
L.execute('ToggleAllBags(); ToggleBackpack(); ToggleBag(1); Fire()')
print("shown:", L.eval('AetherPackFrame.shown'))
for t in sections(): print("  ", t)
L.execute('''NAMES={} for b=0,2 do for s=1,(SLOTS[b]) do local btn=_G["AetherPackItem"..(b+1).."_"..s]; if btn and btn.shown and btn.icon then NAMES[#NAMES+1]=string.format("%s@%d,%d", btn.aetherLink:match("%[(.-)%]"), btn.pos[1], -btn.pos[2]) end end end''')
print("  item positions:", sorted(L.eval('NAMES').values(), key=lambda s:(int(s.split(",")[1]), int(s.split("@")[1].split(",")[0]))))
def bars():
    L.execute("""BARS={} for _,b in ipairs(AetherPackFrame.bars) do if b.shown then BARS[#BARS+1]=b.label.text.." | "..b.text.text..(b.fill.shown and (" | fill "..math.floor(b.fill.w)) or "") end end""")
    for x in L.eval('BARS').values(): print("   bar:", x)
bars()
print("money:", L.eval('AetherPackFrame.money.text'))
print("== B again closes")
L.execute('ToggleAllBags(); Fire()'); print("shown:", L.eval('AetherPackFrame.shown'))
print("== search 'arrow'")
L.execute('ToggleAllBags(); Fire(); AetherPackSearch:SetText("arrow"); AetherPackSearch.OnTextChanged(AetherPackSearch)')
print("  arrow alpha:", L.eval('AetherPackItem2_1.alpha'), "| quail alpha:", L.eval('AetherPackItem1_1.alpha'))
L.execute('AetherPackSearch:SetText(""); AetherPackSearch.OnTextChanged(AetherPackSearch)')
print("== fold Gear")
L.execute('''for _,f in ipairs(FR) do local t=rawget(f,"text"); if f.kind=="Button" and type(t)=="table" and t.text and t.text:find("^Gear") then f.OnClick(f) end end''')
print([t for t in sections() if t.startswith("Gear")], "| hat shown:", L.eval('AetherPackItem1_4.shown'))
print("== vendor: sell junk")
L.execute('EV.OnEvent(EV,"MERCHANT_SHOW"); Fire()'); print("sell button:", L.eval('AetherPackFrame.sell.shown'))
L.execute('AetherPackFrame.sell.OnClick(); Fire()'); print("sold:", list(L.eval('SOLD').values()), "| junk section now:", [t for t in sections() if t.startswith("Junk")])
print("== combat: layout waits")
L.execute('COMBAT=true; ITEMS[2][#ITEMS[2]+1]={3,"Linen Cloth",7,1,2589,5}; EV.OnEvent(EV,"BAG_UPDATE_DELAYED"); Fire()')
print("linen shown in combat:", L.eval('AetherPackItem3_3 and AetherPackItem3_3.shown and AetherPackItem3_3.icon ~= nil'))
L.execute('COMBAT=false; EV.OnEvent(EV,"PLAYER_REGEN_ENABLED")'); print("after combat:", L.eval('AetherPackItem3_3.icon ~= nil and AetherPackItem3_3.shown'))
print("== replace off: B does nothing to AetherPack")
L.execute('SlashCmdList.AETHERPACK("replace off"); AetherPackFrame:Hide(); ToggleAllBags(); Fire()'); print("shown:", L.eval('AetherPackFrame.shown'))
for x in L.eval('OUT').values(): print("  out:", x)


print("== combined Blizzard window (like the I key)")
L.execute('SlashCmdList.AETHERPACK("replace on"); AetherPackFrame:Hide(); ContainerFrameCombinedBags:Show(); Fire()')
print("pack:", L.eval('AetherPackFrame.shown'), "| blizzard combined:", L.eval('ContainerFrameCombinedBags.shown'))
L.execute('ContainerFrameCombinedBags:Show(); Fire()')
print("press again -> pack:", L.eval('AetherPackFrame.shown'), "| blizzard combined:", L.eval('ContainerFrameCombinedBags.shown'))
L.execute('ToggleAllBags(); Fire()')
print("B (opens combined + hook) -> pack:", L.eval('AetherPackFrame.shown'), "| blizzard combined:", L.eval('ContainerFrameCombinedBags.shown'))
L.execute('ToggleAllBags(); Fire()')
print("B again -> pack:", L.eval('AetherPackFrame.shown'))
L.execute('AetherPackFrame:Hide(); OpenAllBags(); ContainerFrameCombinedBags:Show(); Fire()')
print("vendor auto-open -> pack:", L.eval('AetherPackFrame.shown'))

print("== new item glow")
L.execute("""C_NewItems={IsNewItem=function(b,s) return b==0 and s==1 end}
for b=0,2 do for s=1,SLOTS[b] do local btn=_G["AetherPackItem"..(b+1).."_"..s]; if btn then btn.NewItemTexture=CreateFrame("Frame"); btn.NewItemTexture:Show() end end end
AetherPackFrame:Hide(); AetherPackFrame:Show()""")
L.execute("""G={} for b=0,2 do for s=1,SLOTS[b] do local btn=_G["AetherPackItem"..(b+1).."_"..s]; if btn and btn.shown and btn.icon and btn.NewItemTexture.shown then G[#G+1]=btn.aetherLink:match("%[(.-)%]") end end end""")
print("glowing:", list(L.eval('G').values()))
