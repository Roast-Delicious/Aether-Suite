# Chevron accents, class medallion and class glyphs (white with soft edges,
# tinted in game). Same geometry as the approved mockups.
import os, math, sys
import numpy as np
from PIL import Image, ImageDraw
sys.argv=[sys.argv[0]]
from gen_frame_art import write_tga, pot
HI=16   # px per unit while drawing (then reduced)

def to_tga(path, img_L, out_px):
    small=img_L.resize((out_px,out_px),Image.LANCZOS)
    write_tga(path, np.asarray(small,dtype=np.float32)/255.0)

def chevron(path, r, direction, th, fn, grow=0.0, box_grow=None):
    """r = the accent's reach unit; u points `direction`. th/fn = line widths (units).
    The gold and its dark backing share one box (box_grow) so they line up."""
    half=1.35*r+(grow if box_grow is None else box_grow)+1
    size=2*half; N=int(round(size*HI))
    im=Image.new("L",(N,N),0); d=ImageDraw.Draw(im)
    du,dv={"up":((0,-1),(1,0)),"down":((0,1),(1,0)),"right":((1,0),(0,1)),"left":((-1,0),(0,1))}[direction]
    def P(u,v): return ((half+(u*du[0]+v*dv[0])*r)*HI,(half+(u*du[1]+v*dv[1])*r)*HI)
    for pts,w in (([(-0.2,-0.85),(0.55,0),(-0.2,0.85)],th),([(0.35,-0.75),(1.1,0),(0.35,0.75)],fn)):
        d.line([P(*p) for p in pts],fill=255,width=max(1,int(round((w+grow)*HI))),joint="curve")
        for p in (pts[0],pts[-1]):      # round the line ends
            q=P(*p); rr=(w+grow)/2*HI; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],fill=255)
    to_tga(path, im, pot(int(math.ceil(size*2))))
    return size

def ring(path, D, width):
    N=int(D*HI); im=Image.new("L",(N,N),0); d=ImageDraw.Draw(im)
    d.ellipse([0,0,N-1,N-1],outline=255,width=int(round(width*HI)))
    to_tga(path, im, pot(D*3))

exec(open('/tmp/glyphs.py').read().split("def medallion")[0].split("GOLDC=(255,209,0,255); DARKC=(10,11,14,255)")[1])  # glyph()
def class_glyph(path, kind, D=20):
    N=int(D*HI); im=Image.new("L",(N,N),0); d=ImageDraw.Draw(im)
    glyph(d, N/2, N/2, N*0.33, kind, 255)
    to_tga(path, im, pot(D*3))

if __name__ == "__main__":
    fr='/home/claude/brand/AetherFrames/Media/'
    K=1.15
    sizes={}
    for S,g in ((80,9),(58,6)):
        r=g/2*math.sqrt(2)
        for dirn in ("up","down","left","right"):
            sizes[S]=chevron(fr+'chev%d_%s_gold.tga'%(S,dirn), r, dirn, 1.6/K, 0.75/K, box_grow=1.9/K)
            chevron(fr+'chev%d_%s_dark.tga'%(S,dirn), r, dirn, 1.6/K, 0.75/K, grow=1.9/K, box_grow=1.9/K)
    ring(fr+'medal_ring.tga', 20, 0.75/K)
    for k in ("hunter","mage","warrior","rogue","priest","paladin","druid","shaman","warlock"):
        class_glyph(fr+'class_%s.tga'%k, k)
    # window accent (one size, pointing up) for every addon with an Aether window
    wins=["AetherHub","AetherMeter","AetherCoords","AetherItemID","AetherLedger","AetherPack","AetherBars"]
    for a in wins:
        os.makedirs('/home/claude/brand/%s/Media'%a, exist_ok=True)
        wsize=chevron('/home/claude/brand/%s/Media/win_chev_gold.tga'%a, 5.0, "up", 2.0, 1.0, box_grow=1.6)
        chevron('/home/claude/brand/%s/Media/win_chev_dark.tga'%a, 5.0, "up", 2.0, 1.0, grow=1.6, box_grow=1.6)
    print("crest chevron box sizes (units):", {k:round(v,2) for k,v in sizes.items()}, "| window chevron box:", round(wsize,2))
