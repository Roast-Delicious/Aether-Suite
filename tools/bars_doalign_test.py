from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
src=open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a=src.index('-- ==========================================\n-- ALIGN'); b=src.index('-- The Aether XP bar: a pill-shaped bar')
trim_a=src.index('local function BoundsOf(list, uiScale)'); trim_b=src.index('local function Gap(a, b)')
L.execute(r'''
local M={}; M.__index=M
function F(name,parent,l,b,w,h) local f=setmetatable({name=name,parent=parent,l=l,b=b,w=w,h=h,vis=true},M); if name then _G[name]=f end; return f end
function M:GetName() return self.name end
function M:GetParent() return self.parent end
function M:IsForbidden() return false end
function M:IsVisible() return self.vis end
function M:IsShown() return self.vis end
function M:GetEffectiveScale() return 1 end
function M:GetLeft() return self.l end
function M:GetBottom() return self.b end
function M:GetRight() return self.l+self.w end
function M:GetTop() return self.b+self.h end
function M:GetWidth() return self.w end
function M:GetHeight() return self.h end
function M:ClearAllPoints() end
-- moving a bar frame moves its buttons
function M:SetPoint(p,rel,rp,x,y) self.pt={p,x,y}; if p=="BOTTOMRIGHT" then x=2420+x-self.w end; if self.kids then local dx,dy=x-self.l,y-self.b; for _,k in ipairs(self.kids) do k.l=k.l+dx; k.b=k.b+dy end end; self.l=x; self.b=y end
hooksecurefunc=function() end
UIParent=F("UIParent",nil,0,0,2420,1512)
function UIParent:GetWidth() return 2420 end
function UIParent:GetEffectiveScale() return 1 end
InCombatLockdown=function() return false end
IsSecret=function() return false end
NEAR=14; ALIGN=20
OUT={}; Print=function(s) OUT[#OUT+1]=s end
db={align={ MultiBarRight={2300,900} }, xp={}, alignCenter=true}
function bar(name,prefix,n,l,b,size,gap)
  local f=F(name,UIParent,l,b,n*(size+gap),size); f.kids={}
  local list={prefix=prefix}
  for i=1,n do local btn=F(nil,f,l+(i-1)*(size+gap),b,size,size); list[i]=btn; f.kids[i]=btn end
  return list
end
groups={ bar("MainMenuBar","ActionButton",12,500-330,20,54,2.5),
         bar("MultiBarBottomLeft","MultiBarBottomLeftButton",12,500-330,96,54,2.5),
         bar("MultiBarBottomRight","MultiBarBottomRightButton",12,1160-330,96,54,2.5),
         bar("MultiBarLeft","MultiBarLeftButton",10,500-330,170,46,2.5),
         bar("MultiBarRight","MultiBarRightButton",12,2300,500,46,2.5) }
-- vertical side bar: restack its buttons vertically
for i,btn in ipairs(groups[5]) do btn.l=2300; btn.b=500+(i-1)*50 end
MultiBarRight.w=46; MultiBarRight.h=600
BAGS={}; MICS={}
function BagButtonList() return BAGS end
function MicroButtonList() return MICS end
function OneRow() return false end
function MatchUtilitySizes() end
function LayoutTrims() end
xpBar=F("XPBar",UIParent,500,160,840,14)
function ApplyXP() xpBar.l=db.xp.left; xpBar.b=db.xp.bottom end
''')
L.execute(src[trim_a:trim_b] + src[a:b].replace("local function DoAlign","function DoAlign").replace("local function PlaceMover","function PlaceMover") )
L.execute('DoAlign()')
def frame(n):
    f=L.eval(n); return round(f.l), round(f.b)
print("chat:", [L.eval('OUT')[i] for i in range(1,len(L.eval('OUT'))+1)])
for n in ["MainMenuBar","MultiBarBottomLeft","MultiBarBottomRight","MultiBarLeft","MultiBarRight","XPBar"]: print(n, frame(n))
al=L.eval('db.align'); print("saved spots:", sorted(list(al.keys())))
g=L.eval('groups')
l=min(g[i][1].l for i in range(1,5)); r=max(g[i][len(g[i])].l+g[i][len(g[i])].w for i in range(1,5))
print("main block", round(l), round(r), "center", round((l+r)/2), "screen center 1210")
L.execute('OUT={}; DoAlign()'); print("second click:", L.eval('OUT[1]'))

# Blizzard's GetRightActionBarWidth: abs(x offset of point 1) + width
L.execute('PlaceMover(MultiBarRight, 2300, 500)')
pt=L.eval('MultiBarRight.pt'); w=L.eval('MultiBarRight.w')
print("side bar point:", pt[1], round(pt[2],1), "-> Blizzard right width", round(abs(pt[2])+w,1), "(left edge at", L.eval('MultiBarRight.l'),")")
L.execute('PlaceMover(MainMenuBar, 500, 20)'); print("main bar point:", L.eval('MainMenuBar.pt')[1])
