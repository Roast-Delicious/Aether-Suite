# Guild & Communities crest glyph: A, the banner (user Nov 25 17:01,
# mock/guild_crest.py). White with alpha, tinted Aether gold in game.
# Run from tools/: python3 gen_guild_crest.py
import sys
sys.path.insert(0, '../mock'); sys.path.insert(0, '.')
from PIL import Image, ImageDraw
from gen_skins_art import write_rgba
import importlib.util
spec = importlib.util.spec_from_file_location("gc", "../mock/guild_crest.py")
src = open("../mock/guild_crest.py").read().split("shot = Image.open")[0]
ns = {}; exec(src, ns)
size, S = 128, 8
N = size * S
a = Image.new('L', (N, N), 0); ns['banner'](ImageDraw.Draw(a), N)
a = a.resize((size, size), Image.LANCZOS)
im = Image.new('RGBA', (size, size), (255, 255, 255, 0)); im.putalpha(a)
write_rgba('../AetherSkins/Media/gl_banner.tga', im)
print("ok gl_banner")
