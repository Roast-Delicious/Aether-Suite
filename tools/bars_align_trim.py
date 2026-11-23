exec(open('bars_trim_test.py').read().split("def show():")[0])
L.execute('''
groups = {}
local function bar(prefix, n, l, r, b, t)
  local list={prefix=prefix}; local w=(r-l+2.5)/n
  for i=1,n do local x=New("CheckButton"); x.l=l+(i-1)*w; x.b=b; x.GetRight=function(s) return s.l+w-2.5 end; x.GetTop=function() return t end; list[i]=x end
  return list
end
groups[1]=bar("ActionButton",12,18,695,12,68)
groups[2]=bar("MultiBarBottomLeftButton",12,18,695,80,136)
groups[3]=bar("MultiBarRightButton",10,18,500,148,198)
groups[4]=bar("MultiBarBottomRightButton",12,707,1387,80,136)
local bg=bar("x",6,707,1040,12,66); for i=1,6 do BAGB[i]=bg[i] end; for i=7,#BAGB do BAGB[i]=nil end
local mc=bar("y",10,1060,1590.5,12,66); for i=1,10 do MICB[i]=mc[i] end
GetPhysicalScreenSize=function() return 1920,1080 end
AetherMeterDB={opacityOutCombat=0.2}; db.alpha=1; db.trim=true; LAYOUT(); FADE()
''')
for k in range(1,9):
    p=L.eval('T[%d]'%k)
    if p is None: break
    if not p.shown: continue
    s=p.scale; x,y=p.pt[3]*s,p.pt[4]*s
    print("panel",k,"UI x %.0f-%.0f y %.0f-%.0f"%(x,x+p.w*s,y,y+p.h*s),"gem",p.gem[1].shown,
          "members",len(p.members),"hidden corners",[c for c in ('TOPLEFT','TOPRIGHT','BOTTOMLEFT','BOTTOMRIGHT') if not p.corners[c][1].shown])
