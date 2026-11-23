import math, numpy as np
from lupa.lua51 import LuaRuntime
from PIL import Image
W,H=790,18; EARN,REST=0.58,0.75
L=LuaRuntime(unpack_returned_tuples=True)
src=open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a=src.index('local XP_MEDIA'); b=src.index('\nend\n',src.index('TrimXP = function()'))+5
L.execute(r'''
TEX={}
T={}; T.__index=T
function T:SetTexture(f) self.file=f end
function T:SetVertexColor(r,g,b,a) self.c={r,g,b,a or 1} end
function T:SetSnapToPixelGrid() end function T:SetTexelSnappingBias() end
function T:SetTexCoord(l,r,t,b) self.tc={l,r,t,b} end
function T:SetRotation(r) self.rot=r end
function T:SetSize(w,h) self.w=w; self.h=h end
function T:ClearAllPoints() self.pt=nil end
function T:SetPoint(p,rel,rp,x,y) self.pt={p,rp,x or 0,y or 0} end
function T:SetShown(v) self.shown=v and true or false end
function T:Hide() self.shown=false end
function T:Show() self.shown=true end
F={}; NOT={StatusBar=1,ExhaustionLevelFillBar=1,ExhaustionTick=1,OverlayFrame=1,UpdateStatusBarTextures=1,aetherSquare=1}; F.__index=function(t,k) if F[k] then return F[k] end if NOT[k] then return nil end return function() return 1 end end
function F:CreateTexture(_,layer,_,sub) local t=setmetatable({layer=layer,sub=sub or 0,shown=true},T); TEX[#TEX+1]=t; return t end
function F:GetWidth() return self.w end function F:GetHeight() return self.h end
function F:SetShown(v) self.shown=v end
CreateFrame=function() local f=setmetatable({w=@W@,h=@H@},F); OV=f; return f end
C_Timer={After=function(_,fn) fn() end}
hooksecurefunc=function() end
issecretvalue=function() return false end
UnitXP=function() return @E@ end
UnitXPMax=function() return 1000 end
GetXPExhaustion=function() return @R@ end
db={trim=true}
EXP=setmetatable({isExpBar=true},F)
xpBar={bars={EXP}}
'''.replace('@W@',str(W)).replace('@H@',str(H)).replace('@E@',str(int(EARN*1000))).replace('@R@',str(int((REST-EARN)*1000)))+src[a:b]+'\nTrimXP()\n')
SC=4; M=40
cw,ch=(W+2*M),(H+2*M)
import cv2
_src=np.array(Image.open('/tmp/v4/f_057.png').convert('RGB')); _m=np.zeros(_src.shape[:2],np.uint8); _m[1264:1290,916:1720]=255
_src=cv2.inpaint(_src,_m,6,cv2.INPAINT_TELEA)
bg=np.array(Image.fromarray(_src).crop((922-M,1268-M,922-M+cw,1268-M+ch)).resize((cw*SC,ch*SC)),np.float32)
order={"BACKGROUND":0,"BORDER":1,"ARTWORK":2,"OVERLAY":3}
texs=[L.eval('TEX')[i] for i in range(1,len(L.eval('TEX'))+1)]
texs=[t for t in texs if t.shown and t.pt]
texs.sort(key=lambda t:(order[t.layer],t.sub))
for t in texs:
    p,rp,x,y=[t.pt[k] for k in (1,2,3,4)]
    w,h=t.w,t.h
    if p=="TOPLEFT": l,tp=x,-y
    elif p=="CENTER": l,tp=x-w/2,-y-h/2
    elif p=="TOP": l,tp=x-w/2,-y
    pw,ph=max(1,int(round(w*SC))),max(1,int(round(h*SC)))
    if 'WHITE' in t.file.upper(): al=np.ones((ph,pw),np.float32)
    else:
        name=t.file.split('\\')[-1]
        im=Image.open('/home/claude/brand/AetherBars/Media/%s.tga'%name).convert('RGBA')
        if t.tc:
            l2,r2,t2,b2=[t.tc[k] for k in (1,2,3,4)]
            iw=im.width
            if l2<=r2: im=im.crop((int(round(l2*iw)),0,max(int(round(l2*iw))+1,int(round(r2*iw))),im.height))
            else: im=im.crop((int(round(r2*iw)),0,max(int(round(r2*iw))+1,int(round(l2*iw))),im.height)).transpose(Image.FLIP_LEFT_RIGHT)
        if t.rot: im=im.rotate(math.degrees(t.rot),resample=Image.BICUBIC)
        al=np.array(im.resize((pw,ph),Image.LANCZOS)).astype(np.float32)[...,3]/255
    c=t.c; col=np.array([c[1]*255,c[2]*255,c[3]*255],np.float32); al=al*c[4]
    x0,y0=int(round((l+M)*SC)),int(round((tp+M)*SC))
    sl=bg[max(0,y0):y0+ph, max(0,x0):x0+pw]
    aa=al[max(0,-y0):max(0,-y0)+sl.shape[0], max(0,-x0):max(0,-x0)+sl.shape[1]][...,None]
    sl[...]=sl*(1-aa)+col*aa
out=Image.fromarray(bg.clip(0,255).astype(np.uint8)).resize((cw,ch),Image.LANCZOS)
out.save('/tmp/xpbar_real.png')
z=out.crop((0,0,300,ch)).resize((900,ch*3),Image.LANCZOS); z2=out.crop((cw//2-150,0,cw//2+150,ch)).resize((900,ch*3),Image.LANCZOS)
zz=Image.new('RGB',(900,ch*6+6)); zz.paste(z,(0,0)); zz.paste(z2,(0,ch*3+6)); zz.save('/tmp/xpbar_real_zoom.png')
print("textures drawn:",len(texs))
