# Bank and Auction House crest glyphs (user Nov 27 15:12: Bank A vault
# door, AH B scales; mock/bank_ah_crest.py). White with alpha, tinted
# Aether gold in game. Run from tools/: python3 gen_bank_ah_crest.py
import sys
sys.path.insert(0, '.')
from PIL import Image, ImageDraw
from gen_skins_art import write_rgba
src = open("../mock/bank_ah_crest.py").read().split("def glyph(")[0]
ns = {}; exec(src, ns)
for name, fn in (("gl_vault", ns["vault"]), ("gl_scales", ns["scales"])):
    size, S = 128, 8
    N = size * S
    a = Image.new('L', (N, N), 0); fn(ImageDraw.Draw(a), N)
    a = a.resize((size, size), Image.LANCZOS)
    im = Image.new('RGBA', (size, size), (255, 255, 255, 0)); im.putalpha(a)
    write_rgba('../AetherSkins/Media/%s.tga' % name, im)
    print("ok", name)
