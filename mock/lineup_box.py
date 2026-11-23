# The "Line up your frames?" box: real AetherDecorate trim (via decor_render.py),
# plus text and buttons drawn to the Lua's sizes. Actual size (1.15 px/unit) + zoom.
import sys
from PIL import Image, ImageDraw, ImageFont
src = open('/home/claude/tools/decor_render.py').read()
src = src.replace("W,H,TH=320,170,28", "W,H,TH=384,104,0")
sys.argv = ["x", "AetherFrames", "AetherFrames/AetherFrames.lua"]
exec(src)                                   # writes /tmp/decor_AetherFrames.png at 1 px/unit, margin M
SC = 4
img = Image.open('/tmp/decor_AetherFrames.png').resize(((W + 2 * M) * SC, (H + 2 * M) * SC), Image.LANCZOS)
d = ImageDraw.Draw(img)
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
try: ImageFont.truetype(FR, 10)
except Exception: FR = "/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf"
big = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 13 * SC)
small = ImageFont.truetype(FR, 10 * SC)
btn = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 12 * SC)
def U(x, y): return ((x + M) * SC, (y + M) * SC)
d.text(U(W / 2, 14), "Line up your frames?", font=big, fill=(255, 255, 255), anchor="mt")
d.multiline_text(U(W / 2, 34), "Levels the rows and lines up the inner ends. Keep As Is\nleaves them exactly where you put them.",
                 font=small, fill=(191, 191, 191), anchor="ma", align="center", spacing=2 * SC)
defs = [("Line Up", 96), ("Line Up and Center", 140), ("Keep As Is", 96)]
total = sum(w for _, w in defs) + 8 * (len(defs) - 1)
x = W / 2 - total / 2
for label, w in defs:
    x0, y0 = U(x, H - 12 - 22); x1, y1 = U(x + w, H - 12)
    d.rectangle([x0, y0, x1, y1], fill=(18, 43, 82), outline=(77, 166, 255), width=SC)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), label, font=btn, fill=(255, 255, 255), anchor="mm")
    x += w + 8
K = 1.15
actual = img.resize((round((W + 2 * M) * K), round((H + 2 * M) * K)), Image.LANCZOS)
zoom = img.resize(((W + 2 * M) * 3, (H + 2 * M) * 3), Image.LANCZOS)
sheet = Image.new("RGB", (zoom.width + 20, actual.height + zoom.height + 90), (20, 22, 28))
dd = ImageDraw.Draw(sheet); lab = ImageFont.truetype("/home/claude/brand/AetherFrames/Media/FiraSans-Bold.ttf", 22)
dd.text((10, 8), "Actual size", font=lab, fill=(255, 209, 0)); sheet.paste(actual, (10, 40))
dd.text((10, actual.height + 50), "Zoom", font=lab, fill=(255, 209, 0)); sheet.paste(zoom, (10, actual.height + 80))
sheet.save(sys.argv_out if False else "/home/claude/work/lineup_box.png"); print(sheet.size)
