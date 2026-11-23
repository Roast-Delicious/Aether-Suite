exec(open('frames_test.py').read().split("for name in [")[0])
from PIL import Image, ImageDraw, ImageFont
import math
L.execute('for _,n in ipairs({"AetherFramesPlayer","AetherFramesPet","AetherFramesTarget"}) do local f=_G[n]; f.shown=true; f.scripts.OnShow(f) end; EV.scripts.OnUpdate(EV,0.2)')
SC=3
def lua_list(t): return [t[i] for i in range(1, len(t)+1)] if t else []
def owner_frame(o, f):
    p=o.parent
    while p is not None:
        if p==f: return True
        p=p.parent
    return False
MEDIA='/home/claude/brand/AetherFrames/Media/'
SAME=L.eval('function(a,b) return rawequal(a,b) end')
from PIL import ImageChops
def render(fname, out, bg=(43,36,24)):
    f=L.eval(fname); W,H=f.w,f.h
    img=Image.new("RGBA",(int(W*SC)+20,int(H*SC)+20),bg+(255,))
    # scenery blobs to show transparency
    d0=ImageDraw.Draw(img)
    d0.ellipse([0,10,W*SC*0.6,H*SC*0.9],fill=(79,107,46,255)); d0.ellipse([W*SC*0.4,-40,W*SC*1.1,H*SC*0.6],fill=(110,90,58,255))
    over=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(over)
    layers={"BACKGROUND":0,"BORDER":1,"ARTWORK":2,"OVERLAY":3}
    L.execute('''function Collect(f) local out={} for _,o in ipairs(ALL) do if (o.kind=="Texture" or o.kind=="StatusBar" or o.kind=="FontString") and o.shown then local p=o.parent; local ok=false; while p do if p==f then ok=true break end p=p.parent end; if ok then o.relIsF=(o.pts[1] and o.pts[1][2]==f) or false; out[#out+1]=o end end end return out end''')
    global F; F=f
    items=lua_list(L.eval('Collect')(f))
    def pos(o):
        p=o.pts[1] if o.pts else None
        if p is None:
            if o.all: return 0,0,W,H
            return None
        pt,rel,rp,x,y=p[1],p[2],p[3],p[4],p[5]
        if rel is None and o.parent is not None and not SAME(o.parent,F) and o.kind != "Mask":
            q=o.parent.pts[1] if o.parent.pts else None
            if q and SAME(q[2],F) and q[1]=="CENTER":
                ax,ay=(q[4],-q[5]) if q[3]=="TOPLEFT" else (W+q[4],-q[5])
                w,h=o.w or 0,o.h or 0
                return ax-w/2, ay-h/2, w, h
        w,h=o.w or 0,o.h or 0
        if isinstance(rel,(int,float)): x,y,rp=rel,(rp or 0),pt
        if rel is None or isinstance(rp,(int,float)): rp=pt
        if not o.relIsF and not isinstance(rel,(int,float)) and rel is not None:
            # one level of nesting: a texture centered on a small frame that is itself placed on f
            q=rel.pts[1] if rel.pts else None
            if q and SAME(q[2],F) and q[1]=="CENTER" and pt=="CENTER":
                px,py=q[4],q[5]
                ax,ay=(px, -py) if q[3]=="TOPLEFT" else (W+px,-py)
                return ax-w/2, ay-h/2, w, h
            return None
        if rp=="TOPLEFT": ax,ay=x,-y
        elif rp=="TOPRIGHT": ax,ay=W+x,-y
        elif rp=="LEFT": ax,ay=x,H/2-y
        else: ax,ay=x,-y
        if pt=="TOPLEFT": l,t=ax,ay
        elif pt=="TOPRIGHT": l,t=ax-w,ay
        elif pt=="CENTER": l,t=ax-w/2,ay-h/2
        elif pt=="LEFT": l,t=ax,ay-h/2
        else: l,t=ax,ay
        return l,t,w,h
    def key(o):
        lv=layers.get(o.layer or "ARTWORK",2)
        if o.kind=="StatusBar": lv=2.5
        if o.kind=="FontString": lv=5
        return (lv, o.sub or 0)
    items.sort(key=key)
    for o in items:
        r=pos(o)
        if not r: continue
        l,t,w,h=r
        l+= 10/SC; t+=10/SC
        a=o.alpha if o.alpha is not None else 1
        # parent alpha (statusbar holders)
        if o.kind=="FontString":
            if o.text:
                col=(255,209,0) if (o.font is None) else (255,255,255)
                d.text((l*SC+2,t*SC+2),str(o.text),fill=(255,255,255,255))
            continue
        if o.tex and isinstance(o.tex,str) and "AetherFrames" in o.tex:
            im=Image.open(MEDIA+o.tex.split("\\")[-1]+".tga").convert("RGBA").resize((max(1,int(round(w*SC))),max(1,int(round(h*SC)))),Image.LANCZOS)
            tc=o.tc; 
            if tc and tc[1]==1 and tc[2]==0: im=im.transpose(Image.FLIP_LEFT_RIGHT)
            c=o.vc or (1,1,1,1)
            r,g,b_,al=im.split()
            al=al.point(lambda v: int(v*a))
            col=Image.new("RGBA",im.size,(int(c[1]*255),int(c[2]*255),int(c[3]*255),255)); col.putalpha(al)
            over.alpha_composite(col,(int(round(l*SC)),int(round(t*SC))))
            continue
        if o.kind=="StatusBar":
            mn=o.min or 0; frac=max(0,min(1,(o.value-mn)/(o.max-mn))) if (o.max is not None and o.max!=mn) else 1
            c=o.sbc or (1,1,1)
            W2,H2=max(1,int(round(w*SC))),max(1,int(round(h*SC)))
            fill=Image.new("L",(W2,H2),0); fd=ImageDraw.Draw(fill)
            if o.reverse: fd.rectangle([W2*(1-frac),0,W2,H2],fill=int(255*a))
            else: fd.rectangle([0,0,W2*frac,H2],fill=int(255*a))
            ft=o.fillTex
            if ft and ft.mask and ft.mask.tex:
                mk=Image.open(MEDIA+ft.mask.tex.split("\\")[-1]+".tga").convert("RGBA").resize((W2,H2),Image.LANCZOS).split()[3]
                fill=ImageChops.multiply(fill,mk)
            col=Image.new("RGBA",(W2,H2),tuple(int(v*255) for v in (c[1],c[2],c[3]))+(255,)); col.putalpha(fill)
            over.alpha_composite(col,(int(round(l*SC)),int(round(t*SC))))
            continue
        if o.kind=="StatusBarOld":
            mn=o.min or 0; frac=max(0,min(1,(o.value-mn)/(o.max-mn))) if (o.max is not None and o.max!=mn) else 1
            c=o.sbc or (1,1,1)
            if o.pts[1][1]=="TOPRIGHT":
                x0=(l+w*(1-frac))*SC; d.rectangle([x0,t*SC,(l+w)*SC,(t+h)*SC],fill=tuple(int(v*255) for v in (c[1],c[2],c[3]))+(int(255*a),))
            else:
                d.rectangle([l*SC,t*SC,(l+w*frac)*SC,(t+h)*SC],fill=tuple(int(v*255) for v in (c[1],c[2],c[3]))+(int(255*a),))
            continue
        if o.tex and "Mask" in str(o.tex):
            c=o.vc or (1,1,1,1)
            d.ellipse([l*SC,t*SC,(l+w)*SC,(t+h)*SC],fill=tuple(int(c[i]*255) for i in (1,2,3))+(int(255*a),))
            continue
        if o.portrait:
            d.ellipse([l*SC,t*SC,(l+w)*SC,(t+h)*SC],fill=(122,74,58,255)); continue
        if o.tex: 
            d.rectangle([l*SC,t*SC,(l+w)*SC,(t+h)*SC],fill=(90,200,90,int(255*a))); continue
        c=o.color
        if not c: continue
        fill=tuple(int(c[i]*255) for i in (1,2,3))+(int(255*a*(c[4] if c[4] else 1)),)
        rot=o.rot or 0
        if rot:
            cx,cy=(l+w/2)*SC,(t+h/2)*SC; hw,hh=w*SC/2,h*SC/2
            pts=[]
            for px,py in ((-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)):
                # WoW rotation is CCW with y up; in image y down -> rotate by -rot
                pts.append((cx+px*math.cos(-rot)-py*math.sin(-rot), cy+px*math.sin(-rot)+py*math.cos(-rot)))
            d.polygon(pts,fill=fill)
        else:
            d.rectangle([l*SC,t*SC,max(l*SC,(l+w)*SC-1),max(t*SC,(t+h)*SC-1)],fill=fill)
    img=Image.alpha_composite(img,over)
    img.save(out)
render("AetherFramesPlayer","/tmp/af_player.png")
render("AetherFramesPet","/tmp/af_pet.png")
render("AetherFramesTarget","/tmp/af_target.png")
print("ok")
