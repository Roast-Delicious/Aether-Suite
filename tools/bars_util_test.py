from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a = src.index('local function MicroSocket(b)')
b = src.index('-- XP bar: clean thin look')
L.execute(r'''
local M = {}; M.__index = M
setmetatable(M, {__index=function() return function() end end})
function F(sl,sb,w,h) return setmetatable({sl=sl,sb=sb,w=w,h=h,scale=1,shown=true,tex={}},M) end
function M:GetEffectiveScale() return self.scale end
function M:GetScale() return self.scale end
function M:SetScale(s) self.scale=s end
function M:GetWidth() return self.w end
function M:GetHeight() return self.h end
function M:GetLeft() return self.sl/self.scale end
function M:GetRight() return (self.sl+self.w*self.scale)/self.scale end
function M:GetTop() return (self.sb+self.h*self.scale)/self.scale end
function M:GetBottom() return self.sb/self.scale end
function M:IsShown() return self.shown end
function M:GetParent() return PARENT end
function M:GetPoint() return "CENTER", nil, "CENTER", 0, 0 end
function M:GetNumPoints() return 1 end
function M:SetPoint(p1, ref, p2, x, y)
  if type(ref)~="table" then return end
  if ref==UIParent then
    if p1=="BOTTOMLEFT" then self.sl = x*self.scale else self.sl = x*self.scale - self.w*self.scale end
    self.sb = y*self.scale; return
  end
  if p1=="BOTTOMLEFT" then self.sl = ref.sl + ref.w*ref.scale + x*self.scale
  else self.sl = ref.sl + x*self.scale - self.w*self.scale end
  self.sb = ref.sb
end
function M:CreateTexture() local t=setmetatable({},M); return t end
PARENT = setmetatable({scale=1}, M)
UIParent = F(0,0,1700,900)
db = {size="bar2", trim=true, edgeAlpha=0.85}
groups = {}
local m = {}; for i=1,12 do m[i]=F(18+(i-1)*56.5, 12, 54, 54) end
groups[1]=m
BAGS={} ; for i=1,6 do BAGS[i]=F(705+(i-1)*70, 8, 46, 46) end
MICS={} ; for i=1,10 do MICS[i]=F(1140+(i-1)*45, 12, 38, 44) end
function BagButtonList() return BAGS end
function MicroButtonList() return MICS end
function IsSecret() return false end
function InCombatLockdown() return false end
function wipe(t) for k in pairs(t) do t[k]=nil end end
function EdgeColor() end
''' + src[a:b] + '''
MatchUtilitySizes(); MatchUtilitySizes()
MUS = MatchUtilitySizes
''')
def row(name):
    lst=L.eval(name); out=[]
    for i in range(1,len(lst)+1):
        f=lst[i]; out.append((round(f.sl,1), round(f.sb,1), round(f.h*f.scale,1)))
    return out
print("micro right end before 1583;","main gap 2.5, size 54")
print("bags :", row('BAGS'))
print("micro:", row('MICS'))
L.execute('db.size="off"; MUS()')
print("off  :", round(L.eval('BAGS[1].scale'),3), round(L.eval('MICS[1].scale'),3))

L.execute('db.size="bar2"; db.strip={x=1540, y=0, fromRight=true, uiScale=1}; MUS(); MUS()')
print("pinned:", row('BAGS')[0], row('MICS')[-1], "right end", round(L.eval('MICS[10].sl + MICS[10].w*MICS[10].scale'),1))
L.execute('KeyRingButton=F(640,8,30,46); function KeyRingButton:IsShown() return true end')
