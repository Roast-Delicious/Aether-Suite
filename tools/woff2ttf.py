# Convert .woff2 web fonts to .ttf (WoW loads TTF). Usage: woff2ttf.py out_dir file.woff2...
import sys, os
from fontTools.ttLib import TTFont
out = sys.argv[1]
for p in sys.argv[2:]:
    f = TTFont(p); f.flavor = None
    name = os.path.basename(p).replace('-latin', '').replace('-normal.woff2', '.ttf')
    f.save(os.path.join(out, name)); print(name)
