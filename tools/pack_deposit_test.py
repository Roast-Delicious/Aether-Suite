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
L.execute("""
CLASS='HUNTER'; Enum={BagIndex={ReagentBag=5}}
-- bag 0 backpack 4 slots, bag 1 quiver 4 slots (type 1), bag 2 regular 4 slots, reagent bag 5 with 2 slots
ITEMS={[0]={{1,'Hearthstone',15,1,6948,1},{2,'Roasted Quail',0,1,4604,5}}, [1]={{1,'Jagged Arrow',6,1,3030,200}},
       [2]={{1,'Cutthroat Hat',4,2,8888,1}}, [5]={{1,'Silk Cloth',7,1,4306,20}}}
SLOTS={[0]=4,[1]=4,[2]=4,[3]=0,[4]=0,[5]=2}
TYPES={[1]=1}
local function used(b) return #(ITEMS[b] or {}) end
C_Container.GetContainerNumFreeSlots=function(b) return (SLOTS[b] or 0)-used(b), TYPES[b] or 0 end
C_Container.ContainerIDToInventoryID=function(b) return 30+b end
CLS={} for _,list in pairs(ITEMS) do for _,it in ipairs(list) do CLS[it[5]]=it[3] end end
CLS[2589]=7; CLS[2512]=6; CLS[5000]=0
FAMILY={[3030]=1,[2512]=1}
C_Item.GetItemFamily=function(id) return FAMILY[id] or 0 end
REAGENT={[2589]=true,[4306]=true}
local gi=C_Item.GetItemInfo
C_Item.GetItemInfo=function(x) if type(x)=='number' then return nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,0,nil,nil,nil,nil,nil,REAGENT[x] or false end return gi(x) end
bit={band=function(a,b) local r,k=0,1 while a>0 and b>0 do if a%2==1 and b%2==1 then r=r+k end a=math.floor(a/2) b=math.floor(b/2) k=k*2 end return r end}
CURSOR=nil; PUT={}
CursorHasItem=function() return CURSOR~=nil end
GetCursorInfo=function() if CURSOR then return 'item', CURSOR end end
PutItemInBackpack=function() PUT[#PUT+1]='backpack' end
PutItemInBag=function(s) PUT[#PUT+1]='bag'..s end
ERR={}; UIErrorsFrame={AddMessage=function(_,m) ERR[#ERR+1]=m end}
""")
L.execute("""
local CF = CreateFrame
CreateFrame = function(...)
  local f = CF(...)
  f.CreateAnimationGroup = function(self)
    local ag = { playing = false }
    function ag:SetLooping(v) self.looping = v end
    function ag:CreateAnimation(kind) local a = { kind = kind }
      function a:SetFromAlpha(v) ag.from = v end function a:SetToAlpha(v) ag.to = v end
      function a:SetDuration(v) ag.dur = v end function a:SetSmoothing(v) ag.smooth = v end
      return a end
    function ag:Play() self.playing = true end
    function ag:Stop() self.playing = false end
    function ag:IsPlaying() return self.playing end
    self.ag = ag
    return ag
  end
  f.GetFrameLevel = function() return 5 end
  return f
end
""")
L.execute(open('/home/claude/brand/AetherPack/AetherPack.lua').read())
L.execute('for _,f in ipairs(FR) do if rawget(f,"OnEvent") then EV=f end end; EV.OnEvent(EV,"ADDON_LOADED","AetherPack"); EV.OnEvent(EV,"PLAYER_LOGIN"); ToggleAllBags(); Fire()')
fails=[]
def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
E=L.eval
def drop(item):
    L.execute(f"PUT={{}}; ERR={{}}; CURSOR={item}; AetherPackDeposit.OnReceiveDrag(AetherPackDeposit)")
    return list(E("PUT").values()), list(E("ERR").values())
check("the deposit block is shown", E("AetherPackFrame.depositBox.shown") == True)
check("its art: well, glow, dark middle, rim, number glow, ink", E("AetherPackDeposit.tint[1] ~= nil and AetherPackDeposit.tint[2] ~= nil") == True)
check("count = free regular slots (backpack 2 + bag 3)", E("AetherPackDeposit.count.text") == 5)
put,_=drop(2589); check("cloth (crafting reagent) goes to the reagent bag", put == ["bag35"])
put,_=drop(3030); check("arrows go to the quiver", put == ["bag31"])
put,_=drop(5000); check("anything else: first regular bag with room (backpack)", put == ["backpack"])
L.execute("ITEMS[0]={{1,'a',0,1,1,1},{2,'b',0,1,2,1},{3,'c',0,1,3,1},{4,'d',0,1,4,1}}")
put,_=drop(5000); check("backpack full: next regular bag, not the quiver", put == ["bag32"])
L.execute("ITEMS[5]={{1,'x',7,1,4306,1},{2,'y',7,1,4306,1}}")
put,_=drop(2589); check("reagent bag full: cloth goes to a regular bag", put == ["bag32"])
L.execute("ITEMS[2]={{1,'a',0,1,1,1},{2,'b',0,1,2,1},{3,'c',0,1,3,1},{4,'d',0,1,4,1}}")
put,err=drop(5000); check("all full: nothing moved, a message instead", put == [] and len(err) == 1)
L.execute("PUT={}; CURSOR=nil; AetherPackDeposit.OnClick(AetherPackDeposit)")
check("click with nothing on the cursor does nothing", len(E("PUT")) == 0)
L.execute('for _,t in ipairs(AetherPackDeposit.tint) do t.SetVertexColor=function(self,r,g,b,a) self.vc={r,g,b} end end')
L.execute('EV.OnEvent(EV,"BAG_UPDATE_DELAYED"); Fire()')
check("count shows 0 when the regular bags are full", E("AetherPackDeposit.count.text") == 0)
check("frame turns red when full", E("AetherPackDeposit.tint[1].vc[1]") > 0.85 and E("AetherPackDeposit.tint[1].vc[2]") < 0.4)
# layout: label on the folded Free slots row, slot under it at the right, window tall enough
L.execute("ITEMS[2]={{1,'Cutthroat Hat',4,2,8888,1}}; EV.OnEvent(EV,'BAG_UPDATE_DELAYED'); Fire()")
check("amber again with room", abs(E("AetherPackDeposit.tint[1].vc[2]") - 0.69) < 1e-6)
check("bars run full width", E("AetherPackFrame.bars[1].pos[1]") == -10)
check("its own row, lined up with the item grid's first column", E("AetherPackFrame.depositBox.pos[1]") == 10)
L.execute("for _,b in ipairs(AetherPackFrame.bars) do local sp = b.SetPoint; b.SetPoint = function(self, a, r, rp, x, y) if a == 'TOPLEFT' then self.top = y end return sp(self, a, r, rp, x, y) end end; EV.OnEvent(EV,'BAG_UPDATE_DELAYED'); Fire()")
L.execute("BY = AetherPackFrame.depositBox.pos[2]; B1 = AetherPackFrame.bars[1].top")
check("the bars come after the deposit row", E("B1") <= E("BY") - 46)
check("window tall enough", E("AetherPackFrame.h") >= -E("B1") + 18)
# the pulse
L.execute("AetherPackDeposit.IsVisible = function() return true end; CURSOR = nil; EV.OnEvent(EV, 'CURSOR_CHANGED')")
check("pulse: set to 100% -> 10% and back, 2.7 s, eased", E("AetherPackDeposit.pulse.from") == 1 and abs(E("AetherPackDeposit.pulse.to") - 0.1) < 1e-6 and abs(E("AetherPackDeposit.pulse.dur") - 1.35) < 1e-6 and E("AetherPackDeposit.pulse.looping") == "BOUNCE")
check("no item held: the number stays still", not E("AetherPackDeposit.pulse.playing"))
L.execute("CURSOR = 2589; EV.OnEvent(EV, 'CURSOR_CHANGED')")
check("picking up an item starts the pulse", E("AetherPackDeposit.pulse.playing") == True)
L.execute("CURSOR = nil; EV.OnEvent(EV, 'CURSOR_UPDATE')")
check("putting it down stops it", not E("AetherPackDeposit.pulse.playing"))
L.execute('SlashCmdList.AETHERPACK("pulse always")')
check("/pack pulse always: pulses with nothing held", E("AetherPackDeposit.pulse.playing") == True)
L.execute('SlashCmdList.AETHERPACK("pulse off"); CURSOR = 2589; EV.OnEvent(EV, "CURSOR_CHANGED")')
check("/pack pulse off: never", not E("AetherPackDeposit.pulse.playing"))
L.execute('SlashCmdList.AETHERPACK("pulse item"); CURSOR = nil')
L.execute('SlashCmdList.AETHERPACK("deposit off")')
check("/pack deposit off hides it", not E("AetherPackFrame.depositBox.shown"))
check("bars still full width", E("AetherPackFrame.bars[1].pos[1]") == -10)
L.execute('SlashCmdList.AETHERPACK("deposit on")')
check("/pack deposit on brings it back", E("AetherPackFrame.depositBox.shown") == True)
print("FAILED:", fails) if fails else print("all passed")
sys.exit(1 if fails else 0)
