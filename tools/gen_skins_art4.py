# Bakes the flat profession and Collections tab glyphs (approved Nov 25
# 12:22, mock/profs_flat.py + mock/coll_flat.py): pr_*.tga, cl_*.tga,
# white with alpha, tinted Aether gold in game.
# Run from mock/: python3 ../tools/gen_skins_art4.py
import sys
sys.path.insert(0, '/home/claude/aether-repo/mock'); sys.path.insert(0, '/home/claude/aether-repo/tools')
from gen_skins_art3 import mono, OUT
from gen_skins_art import write_rgba
import profs_flat as PF, coll_flat as CF
W = (255, 255, 255)
for k, _ in PF.KINDS:
    write_rgba(OUT + '/pr_' + k + '.tga', mono(lambda d, n: PF.glyph(d, k, n / 2, n / 2, n * .40, W, BG=(0, 0, 0))))
for k, _ in CF.KINDS:
    write_rgba(OUT + '/cl_' + k + '.tga', mono(lambda d, n: CF.glyph(d, k, n / 2, n / 2, n * .40, W, BG=(0, 0, 0))))
print("ok")
# Group Finder browse tab: a magnifying glass (user Nov 25 14:12)
import math
def search(d, n):
    cx, cy, r = n * .43, n * .43, n * .24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=W, width=int(n * .09))
    a = math.radians(45); w = n * .065; L0, L1 = r * 1.05, r * 2.15
    pts = [(cx + math.cos(a) * L0 - math.sin(a) * w, cy + math.sin(a) * L0 + math.cos(a) * w),
           (cx + math.cos(a) * L1 - math.sin(a) * w, cy + math.sin(a) * L1 + math.cos(a) * w),
           (cx + math.cos(a) * L1 + math.sin(a) * w, cy + math.sin(a) * L1 - math.cos(a) * w),
           (cx + math.cos(a) * L0 + math.sin(a) * w, cy + math.sin(a) * L0 - math.cos(a) * w)]
    d.polygon(pts, fill=W)
write_rgba(OUT + '/gl_search.tga', mono(search))
print("search ok")
