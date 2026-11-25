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
