import os, re
exec(open('frames_test.py').read().split("for name in [")[0])
# every texture file referenced exists
L.execute('USED={}; for _,o in ipairs(ALL) do if o.tex and type(o.tex)=="string" and o.tex:find("AetherFrames") then USED[o.tex]=true end end')
L.execute('MASKS={}; for _,o in ipairs(ALL) do if o.kind=="Mask" and o.tex and tostring(o.tex):find("AetherFrames") then MASKS[#MASKS+1]=o.tex end end')
used=[k for k in L.eval('USED').keys()]
masks=[L.eval('MASKS')[i] for i in range(1,len(L.eval('MASKS'))+1)]
media='/home/claude/brand/AetherFrames/Media/'
missing=[u for u in used+masks if not os.path.exists(media+u.split('\\')[-1]+'.tga')]
print("art files used:", len(set(used+masks)), "| missing:", missing)
# fill rects vs the generator's
out=os.popen('python3 gen_frame_art.py /tmp/artcheck').read()
man=eval(out.split("fill rects (key, bar, P0, P1): ")[1].split("\n")[0])
for unit,key in (("Player","player"),("Target","player"),("Pet","pet4")):
    f=L.eval('AetherFrames'+unit)
    for i in (1,2):
        sb=f.bars[i].sb; p=sb.pts[1]
        x = -p[4] if p[1]=="TOPRIGHT" else p[4]
        exp=[m for m in man if m[0]==key and m[1]==i][0]
        print(unit, "bar", i, "fill from", round(x,3), "to", round(x+sb.w,3), "| art", exp[2], exp[3], "| match", abs(x-exp[2])<0.01 and abs(x+sb.w-exp[3])<0.01)
# own buffs off by default; totem strip attaches under the crest
L.execute('hooksecurefunc=function() end; TotemFrame=New("Frame", PlayerFrame, "TotemFrame"); function TotemFrame:GetParent() return self.parent end; C_Timer={After=function(t,fn) fn() end}')
L.execute('EV.scripts.OnEvent(EV,"PLAYER_ENTERING_WORLD")')
tf=L.eval('TotemFrame')
print("own buff row default:", L.eval('AetherFramesDB.myBuffs'), "| totem strip parent is your frame:", L.eval('TotemFrame.parent==AetherFramesPlayer'),
      "| anchor:", tf.pts[1][1], round(tf.pts[1][4],1), round(tf.pts[1][5],1), "| ignored by Blizzard layout:", L.eval('TotemFrame.ignoreFramePositionManager'))
