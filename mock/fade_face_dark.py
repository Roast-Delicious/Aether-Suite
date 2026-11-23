# Fade options for frames without aggro in combat: the real frame art (rendered
# from AetherFrames.lua by frames_render.py) at several fade levels, with and
# without the bars fading too, over a patch of the user's own game (video
# frame), at actual size (1.29 px per unit) plus a zoom. The face is the real
# 3D portrait from the video (faces don't fade).
import sys, numpy as np
src = open('/home/claude/tools/frames_render.py').read()
src = src.split('render("AetherFramesPlayer"')[0]
src = src.replace('img=Image.new("RGBA",(int(W*SC)+20,int(H*SC)+20),bg+(255,))', 'img=Image.new("RGBA",(int(W*SC)+20,int(H*SC)+20),(0,0,0,0))')
src = src.replace("d0.ellipse([0,10,W*SC*0.6,H*SC*0.9],fill=(79,107,46,255)); d0.ellipse([W*SC*0.4,-40,W*SC*1.1,H*SC*0.6],fill=(110,90,58,255))", "pass")
exec(src)
from PIL import Image, ImageDraw, ImageFont
K = 1.29
video = Image.open('/home/claude/vid2/c_%04d.png' % (66 * 4 + 1)).convert('RGB')   # Jay solid at 66 s
bgsrc = Image.open('/home/claude/vid2/grass.png').convert('RGB')   # clean grass from the same video frame
F = L.eval('AetherFramesPlayer')
# the 3D portrait's layers (glow frame, model) aren't drawable here: the real face is pasted in instead
L.execute('for _, o in ipairs(ALL) do local p = o.parent; while p do if p == AetherFramesPlayer.portraitBack or p == AetherFramesPlayer.model then o.shown = false break end p = p.parent end end; AetherFramesPlayer.portraitBack.shown = false')
def set_alpha(a, bars):
    L.execute('''(function(a, bars)
      local f = AetherFramesPlayer
      for _, t in ipairs(f.soft) do t.alpha = (t.baseAlpha or 1) * a end
      for _, o in ipairs(ALL) do
        if o.kind == "StatusBar" then
          local p = o.parent; local mine = false
          while p do if p == f then mine = true break end p = p.parent end
          if mine then o.alpha = bars and math.max(a, 0.45) or 1 end
        end
      end end)(%r, %s)''' % (a, 'true' if bars else 'false'))
def frame_img(a, bars, face_a=1.0):
    set_alpha(a, bars)
    render("AetherFramesPlayer", "/tmp/fo.png")
    im = Image.open("/tmp/fo.png").convert("RGBA")
    s = K / SC
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    pad = round(10 * s)
    # real face from the video: crest center there ~ (74.5, 90.2), face radius 32 units
    fr = 32 * K; cxv, cyv = 74.5, 90.2
    face = video.crop((round(cxv - fr), round(cyv - fr), round(cxv + fr), round(cyv + fr))).convert("RGBA")
    m = Image.new("L", face.size, 0); ImageDraw.Draw(m).ellipse([1, 1, face.width - 2, face.height - 2], fill=255)
    # a solid dark disc behind the face (never fades), then the faded face over it
    if face_a < 1:
        dark = Image.new("RGBA", face.size, (11, 13, 18, 255))
        face = Image.blend(dark, face.convert("RGBA"), face_a)
    face.putalpha(m)
    cx, cy = F.cx * K + pad, F.cy * K + pad
    im.alpha_composite(face, (round(cx - fr), round(cy - fr)))
    bg = bgsrc.crop((0, 0, im.width, im.height)).convert("RGBA")
    return Image.alpha_composite(bg, im).convert("RGB")
import os
opts = [("Solid (has aggro)", 1, False, 1.0), ("Face at 30% over a dark disc (no yellow)", 0.3, True, 0.3)]
font = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 18)
tiles = [(n, frame_img(a, b, fa)) for n, a, b, fa in opts]
w, h = tiles[0][1].size
Z = 2
sheet = Image.new("RGB", (20 + w + 30 + w * Z, len(tiles) * (h * Z + 34) + 10), (20, 22, 28)); d = ImageDraw.Draw(sheet)
y = 6
for n, t in tiles:
    d.text((10, y), n, font=font, fill=(255, 209, 0))
    sheet.paste(t, (10, y + 28)); sheet.paste(t.resize((w * Z, h * Z), Image.LANCZOS), (10 + w + 30, y + 28))
    y += h * Z + 34
sheet.save(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/work/fade_options.png"); print(sheet.size)
