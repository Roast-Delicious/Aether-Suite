from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New(kind) local f = setmetatable({kind=kind, shown=true, alpha=1, tex={}}, M); return f end
function M.CreateTexture(s) local t = New("Texture"); s.tex[#s.tex+1]=t; return t end
function M.SetColorTexture(s,r,g,b,a) s.color={r,g,b,a} end
function M.SetPoint(s,a,rel,b,x,y) s.pt={a,b,x,y} end
function M.SetSize(s,w,h) s.w=w; s.h=h end
function M.Show(s) s.shown=true end
function M.Hide(s) s.shown=false end
function M.SetShown(s,v) s.shown=v end
function M.IsVisible(s) return s.shown end
function M.SetAlpha(s,a) s.alpha=a end
function M.SetScale(s,v) s.scale=v end
function M.SetRotation() end
wipe=function(t) for k in pairs(t) do t[k]=nil end end
GetPhysicalScreenSize=function() return 2560,1440 end
function M.GetAlpha(s) return s.alpha end
function M.GetEffectiveScale(s) return 1 end
function M.GetLeft(s) return s.l end
function M.GetRight(s) return s.l+36 end
function M.GetTop(s) return s.b+36 end
function M.GetBottom(s) return s.b end
function M.IsMouseOver(s) return false end
CreateFrame = function() return New("Frame") end
UIParent = New("Frame")
InCombatLockdown = function() return COMBAT end; UnitAffectingCombat = function() return COMBAT end
function M.SetPoint(s,a,rel,b,x,y) if type(rel)=='table' then s.pt={a,b,x,y} else s.pt={a,a,rel,b} end end
issecretvalue = function() return false end
''')
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a = src.index('-- AETHER TRIM'); a = src.rfind('-- ====', 0, a)
b = src.index('local function RefreshLook()')
L.execute('db = {trim=true, alpha=0.35, combat=true, mouseover=true}\ngroups = {}\nlocal xpBar\nlocal function IsSecret() return false end\nlocal TrimXP\nBAGB, MICB = {}, {}\nfunction BagButtonList() return BAGB end\nfunction PanelAlpha() return AetherMeterDB and AetherMeterDB.opacityOutCombat or 0.2 end\nfunction MicroButtonList() return MICB end\n' + src[a:b] + '''
local main, other = {prefix="ActionButton"}, {prefix="MultiBarBottomLeftButton"}
for i=1,12 do local x=New("CheckButton"); x.l=100+(i-1)*38; x.b=20; main[i]=x end
for i=1,12 do local x=New("CheckButton"); x.l=100+(i-1)*38; x.b=62; other[i]=x end
other[12].shown=false
groups[1]=main; groups[2]=other
for i=1,5 do local x=New('Button'); x.l=600+(i-1)*38; x.b=20; BAGB[i]=x end
for i=1,10 do local x=New('Button'); x.l=800+(i-1)*30; x.b=20; MICB[i]=x end
LayoutTrims(); UpdateFade()
T = trims
FADE = UpdateFade; LAYOUT = LayoutTrims; 
''')
def show():
    n=0
    for k in range(1,9):
        p=L.eval('T[%d]'%k)
        if p is None: break
        if not p.shown: continue
        n+=1
        corners={c:p.corners[c][1].shown for c in ('TOPLEFT','TOPRIGHT','BOTTOMLEFT','BOTTOMRIGHT')}
        print(" panel",k,"px",p.pt[3],p.pt[4],"size",p.w,p.h,"scale",round(p.scale,4),"gem",p.gem[1].shown,"alpha",p.alpha,"corners",corners)
    return n
print("layout A: main+bar2 stacked, bags+micro beside")
show()
L.execute("COMBAT=false; db.alpha=0.35; FADE()"); print("faded alpha (mixed block stays 1):"); show()
L.execute("for i=1,5 do BAGB[i].l=2000+i*38 end; for i=1,10 do MICB[i].l=2300+i*30 end; LAYOUT(); FADE()")
print("bags far away:"); show()
L.execute("for i=1,12 do groups[2][i].l=100+(i-1)*38+480; groups[2][i].b=20 end; groups[2][12].shown=true; LAYOUT()")
print("bar2 side by side 4px gap after bar1 (L-shape avoided? same row -> merge)"); show()
L.execute("for i=1,6 do groups[2][i].shown=false end; for i=7,12 do groups[2][i].b=62; groups[2][i].l=560+(i-7)*38 end; LAYOUT()")
print("bar2 shorter, up and to the right (L-shape -> separate)"); show()
L.execute('db.trim=false; LAYOUT()'); print("trim off ->", show(), "panels")
