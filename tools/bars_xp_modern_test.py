# Modern client: the XP bar is an unnamed child of MainStatusTrackingBarContainer.
from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a = src.index('local xpBar, xpMover'); b = src.index('local TrimXP   -- below')
L.execute(r'''
local M = {}; M.__index = function(t,k) if M[k] then return M[k] end; if type(k)=="string" and (k:match("^Set") or k:match("^Get") or k:match("^Enable") or k:match("^Clear") or k:match("^Show")) then return function() end end end
function New(l,b,w,h) return setmetatable({scripts={}, l=l or 0, b=b or 0, w=w or 0, h=h or 0, shown=true}, M) end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.GetLeft(s) return s.l end; function M.GetBottom(s) return s.b end
function M.GetWidth(s) return s.w end; function M.GetHeight(s) return s.h end
function M.SetSize(s,w,h) s.w=w; s.h=h end
function M.SetHeight(s,h) s.h=h end
function M.SetPoint(s,p,rel,rp,x,y) if type(x)=="number" then s.pt={p,rel,x,y}; if rel==UIParent then s.l=x; s.b=y end end end
function M.GetEffectiveScale() return 1 end
function M.IsShown(s) return s.shown end
function M.SetShown(s,v) s.shown=v end
function M.Hide(s) s.shown=false end
function M.IsObjectType() return true end
function M.CreateFontString() return New() end
function M.CreateTexture() return New() end
function M.GetFrameLevel() return 1 end
CreateFrame=function(_,_,parent) local f=New(); f.parent=parent; FR=FR or {}; FR[#FR+1]=f; return f end
UIParent=New(0,0,1728,1080)
CX,CY=0,0; DOWN=true
GetCursorPosition=function() return CX,CY end
IsMouseButtonDown=function() return DOWN end
EnumerateFrames=function() return nil end
hooksecurefunc=function() end
KILLED={}; Kill=function(r) if r then KILLED[#KILLED+1]=r end end
Print=function(m) print("  chat: "..m) end
db={xp={}, hideArt=true, edgeAlpha=0}
-- Blizzard's layout: 571x17 container, bars inside at (1,5) sized 565x11
C = New(578, 150, 571, 17); C.BarFrameTexture = New(); C.bars = {}
for i=1,6 do local bar=New(1,5,565,11); bar.StatusBar=New(0,0,565,11); C.bars[i]=bar end
C.bars[4].isExpBar = true; C.bars[4].ExhaustionLevelFillBar = New(0,0,0,11)
C.bars[4].StatusBar.GetStatusBarTexture=function() return "XPFILL" end
MainStatusTrackingBarContainer = C
''' + src[a:b] + r'''
SetupXP()
print("found the container:", xpBar == C, "| frame art hidden:", KILLED[#KILLED] == C.BarFrameTexture, "| fill found:", XPFill())
SetXPUnlocked()
mover, done, grip = FR[1], FR[2], FR[3]
print("mover on UIParent:", mover.parent == UIParent, "| shown:", mover.shown)
CX,CY=1149,150; grip.scripts.OnMouseDown(grip)
CX,CY=1349,145; mover.scripts.OnUpdate()
DOWN=false; mover.scripts.OnUpdate()
local xp=C.bars[4]
print("after resize: container", C.w, C.h, "| XP bar", xp.w, xp.h, "| XP fill", xp.StatusBar.w, xp.StatusBar.h, "| rested", xp.ExhaustionLevelFillBar.h, "| saved", db.xp.w, db.xp.h)
DOWN=true; CX,CY=900,160; mover.scripts.OnMouseDown(mover,"LeftButton")
CX,CY=850,180; mover.scripts.OnUpdate(); mover.scripts.OnMouseUp()
print("after move: container at", C.l, C.b, "| saved", db.xp.left, db.xp.bottom)
SetXPUnlocked()
-- reload: Blizzard rebuilds at 571x17, ApplyXP puts the saved size back
for i=1,6 do C.bars[i].w, C.bars[i].h = 565, 11 end; C.w, C.h = 571, 17
ApplyXP()
print("after reload: container", C.l, C.b, C.w, C.h, "| XP bar", xp.w, xp.h)
''')
