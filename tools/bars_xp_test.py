from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a = src.index('local xpBar, xpMover'); b = src.index('local TrimXP   -- below')
L.execute(r'''
local M = {}; M.__index = function(t,k) return M[k] or function() end end
function New() return setmetatable({scripts={}, l=500, b=150, w=890, h=18, shown=true}, M) end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.GetLeft(s) return s.l end; function M.GetBottom(s) return s.b end
function M.GetWidth(s) return s.w end; function M.GetHeight(s) return s.h end
function M.SetSize(s,w,h) s.w=w; s.h=h end
function M.SetPoint(s,p,rel,rp,x,y) if type(x)=="number" then s.l=x; s.b=y end end
function M.GetEffectiveScale() return 1 end
function M.IsShown(s) return s.shown end
function M.SetShown(s,v) s.shown=v end
function M.Hide(s) s.shown=false end
function M.CreateFontString() return New() end
function M.CreateTexture() return New() end
function M.GetFrameLevel() return 1 end
CreateFrame=function(_,_,parent) local f=New(); LAST=f; FR=FR or {}; FR[#FR+1]=f; return f end
UIParent=New()
CX,CY=0,0; DOWN=true
GetCursorPosition=function() return CX,CY end
IsMouseButtonDown=function() return DOWN end
hooksecurefunc=function() end
Print=function(m) print(m) end
db={xp={}, hideArt=false, edgeAlpha=1}
''' + src[a:b] + r'''
xpBar = New(); xpBar.GetStatusBarTexture=function() end
SetXPUnlocked(); SETX = SetXPUnlocked
mover = FR[1]; done = FR[2]; grip = FR[3]
-- resize: drag corner right 100, down 6
CX,CY=1390,150; grip.scripts.OnMouseDown(grip)
CX,CY=1490,144; mover.scripts.OnUpdate()
DOWN=false; mover.scripts.OnUpdate()
print("after resize", xpBar.l, xpBar.b, xpBar.w, xpBar.h, "saved", db.xp.w, db.xp.h)
-- move: drag by (-50, +20)
DOWN=true; CX,CY=900,160; mover.scripts.OnMouseDown(mover,"LeftButton")
CX,CY=850,180; mover.scripts.OnUpdate(); mover.scripts.OnMouseUp()
print("after move", xpBar.l, xpBar.b, xpBar.w, xpBar.h, "saved", db.xp.left, db.xp.bottom)
''')
L.execute('done.scripts.OnClick(done)')
print("Done locks the XP bar:", L.eval('mover.shown')==False)
L.execute('SETX(true)'); a=L.eval('mover.shown'); L.execute('SETX(true)'); b=L.eval('mover.shown')
print("unlock is not a toggle:", a and b)
