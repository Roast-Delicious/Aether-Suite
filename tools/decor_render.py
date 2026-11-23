# Renders AetherDecorate (the real Lua) for a test window, from its anchors and art.
import sys, math, numpy as np
from lupa.lua51 import LuaRuntime
from PIL import Image
ADDON=sys.argv[1] if len(sys.argv)>1 else "AetherHub"
FILE=sys.argv[2] if len(sys.argv)>2 else "AetherHub/AetherHub.lua"
W,H,TH=320,170,28
L=LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
TEX={}
M={}
M.__index=M
function M:SetTexture(f) self.file=f end
function M:SetVertexColor(r,g,b,a) self.c={r,g,b,a or 1} end
function M:SetColorTexture(r,g,b,a) self.file="WHITE"; self.c={r,g,b,a or 1} end
function M:SetSnapToPixelGrid() end
function M:SetTexelSnappingBias() end
function M:SetTexCoord(l,r,t,b) self.tc={l,r,t,b} end
function M:SetRotation(r) self.rot=r end
function M:SetSize(w,h) self.w=w; self.h=h end
function M:SetWidth(w) self.w=w end
function M:SetHeight(h) self.h=h end
function M:SetPoint(p,rel,rp,x,y) self.pts=self.pts or {}; self.pts[#self.pts+1]={p,rp or p,x or 0,y or 0} end
function M:SetShown() end
FRAME={}
''')
L.execute('FRAME={W=%d,H=%d}'%(W,H))
L.execute(r'''
function FRAME:CreateTexture(_,layer,_,sub) local t=setmetatable({layer=layer,sub=sub or 0},M); TEX[#TEX+1]=t; return t end
function FRAME:GetBackdrop() return {} end
function FRAME:GetBackdropColor() return 0.05,0.06,0.09,0.94 end
function FRAME:GetBackdropBorderColor() return 0.3,0.65,1,0.9 end
function FRAME:SetBackdrop() end
''')
src=open('/home/claude/brand/'+FILE).read()
a=src.index("local function AetherDecorate(frame, titleHeight)"); e=src.index("\nend\n",a)+5
L.execute(src[a:e]+"\nAetherDecorate(FRAME,%d)"%TH)
def anchor(pt,W,H):
    x={'LEFT':0,'RIGHT':W}; y={'TOP':0,'BOTTOM':H}
    ax=0 if 'LEFT' in pt else (W if 'RIGHT' in pt else W/2)
    ay=0 if 'TOP' in pt else (H if 'BOTTOM' in pt else H/2)
    return ax,ay
SC=4; M=40
img=np.zeros(((H+2*M)*SC,(W+2*M)*SC,4),np.float32)
bg=np.array(Image.open('/tmp/v4/f_057.png').convert('RGB').crop((1300,560,1300+W+2*M,560+H+2*M)).resize(((W+2*M)*SC,(H+2*M)*SC)),np.float32)
canvas=np.dstack([bg,np.full(bg.shape[:2],255,np.float32)])
order={"BACKGROUND":0,"BORDER":1,"ARTWORK":2,"OVERLAY":3}
texs=[L.eval('TEX')[i] for i in range(1,len(L.eval('TEX'))+1)]
texs.sort(key=lambda t:(order[t.layer],t.sub))
for t in texs:
    pts=[[t.pts[i][k] for k in (1,2,3,4)] for i in range(1,len(t.pts)+1)]
    if len(pts)==1:
        p,rp,x,y=pts[0]; ax,ay=anchor(rp,W,H); ax+=x; ay-=y
        w,h=t.w,t.h
        ox,oy=anchor(p,w,h); l,tp=ax-ox,ay-oy
    else:
        xs=[];ys=[]
        for p,rp,x,y in pts:
            ax,ay=anchor(rp,W,H); ax+=x; ay-=y
            # the edge this point fixes
            if 'LEFT' in p: xs.append(('l',ax))
            if 'RIGHT' in p: xs.append(('r',ax))
            if 'TOP' in p: ys.append(('t',ay))
            if 'BOTTOM' in p: ys.append(('b',ay))
        d=dict(xs); e=dict(ys)
        l=d.get('l', d.get('r',0)-(t.w or 0)); r_=d.get('r', l+(t.w or 0))
        tp=e.get('t', e.get('b',0)-(t.h or 0)); b_=e.get('b', tp+(t.h or 0))
        w,h=r_-l,b_-tp
    pw,ph=max(1,int(round(w*SC))),max(1,int(round(h*SC)))
    if t.file and 'WHITE' in t.file.upper():
        a=np.ones((ph,pw),np.float32)
    else:
        name=t.file.split('\\')[-1]
        im=Image.open('/home/claude/brand/%s/Media/%s.tga'%(ADDON,name)).convert('RGBA')
        if t.tc:
            l2,r2,t2,b2=t.tc[1],t.tc[2],t.tc[3],t.tc[4]
            if l2>r2: im=im.transpose(Image.FLIP_LEFT_RIGHT)
            if t2>b2: im=im.transpose(Image.FLIP_TOP_BOTTOM)
        if t.rot: im=im.rotate(math.degrees(t.rot),resample=Image.BICUBIC)   # positive = counter-clockwise
        a=np.array(im.resize((pw,ph),Image.LANCZOS)).astype(np.float32)[...,3]/255
    c=t.c; col=np.array([c[1]*255,c[2]*255,c[3]*255],np.float32); al=a*c[4]
    x0,y0=int(round((l+M)*SC)),int(round((tp+M)*SC))
    sl=canvas[max(0,y0):y0+ph, max(0,x0):x0+pw]
    aa=al[max(0,-y0):max(0,-y0)+sl.shape[0], max(0,-x0):max(0,-x0)+sl.shape[1]][...,None]
    sl[...,:3]=sl[...,:3]*(1-aa)+col*aa
out=Image.fromarray(canvas[...,:3].clip(0,255).astype(np.uint8)).resize((W+2*M,H+2*M),Image.LANCZOS)
out.save('/tmp/decor_%s.png'%ADDON); out.resize(((W+2*M)*2,(H+2*M)*2),Image.LANCZOS).save('/tmp/decor_%s_2x.png'%ADDON)
print("textures:",len(texs))
