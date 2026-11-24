# Lays out the AetherLedger travel window with real Fira text metrics and
# draws it at in-game size (1.15 px per unit), to check that text fits.
import lupa.lua51 as l, sys
from PIL import Image, ImageDraw, ImageFont
FD='/home/claude/brand/AetherHub/Media/Fonts/FiraSans-'
FONTS={'AetherFontNormal':('SemiBold',15.1),'AetherFontHighlightSmall':('Regular',11.7)}  # calibrated to the user's screenshot
K=1.15; SS=4
def pil(name): w,sz=FONTS[name]; return ImageFont.truetype(FD+w+'.ttf',int(sz*K*SS))
def width(name,text):
    import re; text=re.sub(r'\|c........|\|r','',text or '')
    return pil(name).getlength(text)/(K*SS)
def wrap(name,text,w):
    words=(text or '').split(' '); lines=[]; cur=''
    for wd in words:
        t=(cur+' '+wd).strip()
        if cur and width(name,t)>w: lines.append(cur); cur=wd
        else: cur=t
    lines.append(cur); return lines
L=l.LuaRuntime(unpack_returned_tuples=True)
G=L.globals(); G.PyWidth=width; G.PyWrap=lambda n,t,w: len(wrap(n,t,w))
L.execute(r'''
FS={}
local function Obj(kind,font) local o={shown=true,font=font,kind=kind,color={1,1,1},pts={}}
  return setmetatable(o,{__index=function(t,k)
   if k=="SetText" then return function(s,x) s.text=x end end
   if k=="SetWidth" then return function(s,w) s.w=w end end
   if k=="GetWidth" then return function(s) return s.w or 0 end end
   if k=="SetHeight" then return function(s,h) s.h=h end end
   if k=="SetSize" then return function(s,w,h) s.w=w; s.h=h end end
   if k=="SetPoint" then return function(s,...) s.pts[#s.pts+1]={...} end end
   if k=="ClearAllPoints" then return function(s) s.pts={} end end
   if k=="Show" then return function(s) s.shown=true end end
   if k=="Hide" then return function(s) s.shown=false end end
   if k=="SetShown" then return function(s,v) s.shown=v and true or false end end
   if k=="IsShown" then return function(s) return s.shown end end
   if k=="SetTextColor" then return function(s,r,g,b) s.color={r,g,b} end end
   if k=="SetWordWrap" then return function(s,v) s.wrap=v end end
   if k=="GetUnboundedStringWidth" then return function(s) return PyWidth(s.font,s.text) end end
   if k=="GetStringWidth" then return function(s) local w=PyWidth(s.font,s.text); return s.w and math.min(w,s.w) or w end end
   if k=="GetStringHeight" then return function(s) local n=(s.wrap==false or not s.w) and 1 or PyWrap(s.font,s.text,s.w); local h=s.font=="AetherFontNormal" and 15.1 or 11.7; return n*h+(n-1)*2 end end
   if k=="CreateFontString" then return function(_,_,_,font) local f=Obj("fs",font); FS[#FS+1]=f; return f end end
   if k=="CreateTexture" then return function() local f=Obj("tex"); FS[#FS+1]=f; return f end end
   if k=="SetScript" then return function(s,n,f) s[n]=f end end
   if type(k)=="string" and k:match("^%u") then return function() end end
  end}) end
CreateFrame=function(kind,name) local o=Obj(kind); if name then _G[name]=o end; return o end
UIParent=Obj(); C_Timer={After=function() end}; GetTime=function() return 0 end
C_Map={GetMapInfo=function(m) return {name=MAPS[m]} end}
MAPS={[1445]="Dustwallow Marsh",[1443]="Desolace"}
AetherDecorate=function() end; AetherClose=function() return Obj() end
''')
src=open('/home/claude/brand/AetherLedger/AetherLedger_Travel.lua').read()
src+='\nfunction TEST_Render(t, extra) trip = t; if not win then BuildWindow() end; Render(extra) end\n'
L.execute(src)
def run(dest,zone,steps,at,extra,out):
    pass
    t=L.eval('{}'); 
    L.execute('TRIP={dest={name=%r,map=%d},steps={},at=%d}'%(dest,zone,at))
    for s in steps: L.execute('table.insert(TRIP.steps,{text=%r})'%s)
    L.execute('TEST_Render(TRIP, %s)'%(repr(extra) if extra else 'nil'))
    W=L.eval('AetherLedgerTravel.w'); H=L.eval('AetherLedgerTravel.h')
    title=L.eval('AetherLedgerTravel.title.text')
    tw=width('AetherFontNormal',title)
    print(out, 'window', W, 'x', H, '| title:', title, '| title fits:', tw <= W-36)
    # draw
    sc=K*SS; im=Image.new('RGBA',(int((W+20)*sc),int((H+20)*sc)),(40,44,36,255)); d=ImageDraw.Draw(im)
    o=10*sc
    d.rounded_rectangle([o,o,o+W*sc,o+H*sc],radius=8*sc,fill=(13,15,23),outline=(77,166,255),width=int(sc))
    d.rectangle([o+4*sc,o+4*sc,o+(W-4)*sc,o+26*sc],fill=(19,40,74)); d.line([o+4*sc,o+26*sc,o+(W-4)*sc,o+26*sc],fill=(255,176,0),width=int(sc))
    shown=title
    while width('AetherFontNormal',shown+'...')>W-36 and len(shown)>3 and tw>W-36: shown=shown[:-1]
    if shown!=title: shown=shown.rstrip()+'...'
    d.text((o+10*sc,o+8*sc),shown,font=pil('AetherFontNormal'),fill=(255,176,0))
    d.rectangle([o+(W-24)*sc,o+6*sc,o+(W-6)*sc,o+24*sc],outline=(77,166,255),width=int(sc))
    ok=True
    for f in L.eval('FS').values():
        if not f.shown or not f.pts or f.kind!='fs' or f is L.eval('AetherLedgerTravel.title'): continue
        if f.font=='AetherFontNormal': continue
        p=f.pts[1]; x=p[4] if len(p)>=4 else 0; y=-(p[5] if len(p)>=5 else 0)
        col=tuple(int(c*255) for c in f.color.values())
        lines=wrap(f.font,f.text,f.w) if f.w and f.wrap is not False else [f.text]
        for i,line in enumerate(lines):
            lw=width(f.font,line)
            if x+lw>W-6: ok=False; print('  OVERFLOW:',line)
            d.text((o+x*sc,o+(y+i*13.7)*sc),line or '',font=pil(f.font),fill=col)
        if y+len(lines)*13.7>H: ok=False; print('  BELOW BOTTOM:',f.text)
    im=im.resize((im.width//SS,im.height//SS),Image.LANCZOS); im.save(out)
    return ok
ok=run("Suspicious Hoofprint",1445,["Go to Thalon, the flight master in Desolace (22, 74)","Fly to Dustwallow Marsh (Shardi)","Walk to Suspicious Hoofprint in Dustwallow Marsh (30, 48)"],1,"697 yards northwest","/tmp/travel1.png")
ok&=run("Suspicious Hoofprint",1445,["Go to Thalon, the flight master in Desolace (22, 74)","Fly to Dustwallow Marsh (Shardi)","Walk to Suspicious Hoofprint in Dustwallow Marsh (30, 48)"],3,"697 yards northwest","/tmp/travel2.png")
ok&=run("The Very Long Named Quest Giver of Somewhere Quite Far Away",1443,["Take the zeppelin from the tower outside Orgrimmar to Tirisfal Glades and then walk all the way to the end of the road (61, 59)","Walk"],1,None,"/tmp/travel3.png")
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
