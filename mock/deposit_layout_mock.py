# The final deposit slot in the user's real AetherPack window, rearranged: the Free
# slots line runs full width; under it, the space bars (left) and the deposit block
# (right: label, chevrons, slot) are centered vertically on each other.
import sys, os
SRC, OUT = sys.argv[1], sys.argv[2]
code = open('/home/claude/mock-work/deposit_v3.py').read()
code = code[:code.index("fl = ImageFont.truetype(FIRA % 'Regular', 18)")]
sys.argv = [sys.argv[0], SRC, os.path.dirname(OUT)]
exec(code)          # defines render(), the slot art, base (rebuilt below), OX, OY, etc.

O37 = mix(GOLD, ORANGE, 0.37)
G = dict(col=O37, n_stack=3, ch_size=16, chev_sizes=[17, 13.5, 10], step=6.5, glow_r=6.6, glow_k=1.6, dark_mid=0.6,
         interior='glowstreaks', num=('glow',), num_size=11.5, erase_line=False)

def window_with(G, tag):
    global base
    base = base0
    _, box = render(**{**G, 'ytop': 1100})[:2]
    block_h = box[3] - (1100 - 9)
    TOP_END = 1112; PAD_T, PAD_B = 4, 4
    mid_h = PAD_T + int(block_h) + PAD_B
    top = src.crop((WX0, 225, WX1, TOP_END))
    filler = src.crop((WX0, 1114, WX1, 1115)).resize((WX1 - WX0, max(mid_h, 80)))
    bottom = src.crop((WX0, 1206, WX1, 1245))
    nb = Image.new('RGB', (WX1 - WX0, top.height + filler.height + bottom.height))
    nb.paste(top, (0, 0)); nb.paste(filler, (0, top.height)); nb.paste(bottom, (0, top.height + filler.height))
    block_top = TOP_END + PAD_T
    bars = src.crop((1168, 1126, 1700, 1204))
    bars_y = int(block_top + max(block_h, 76) / 2 - bars.height / 2)
    nb.paste(bars, (1168 - OX, bars_y - OY))
    base = nb
    img, box = render(**{**G, 'ytop': block_top + 9 + max(0, (76 - block_h) / 2)})[:2]
    return img, OY + base.height - 22
base0 = base
HOOK = {**G, 'arrow': 'hook', 'slot_right': 1740}
GH = {**HOOK, 'hand_font': '/home/claude/mock-work/hfonts/gochi-hand-400.ttf', 'hand_size': 12.5, 'hand_lines': 14}
results = [("Before: slogan in the arrow's yellow",) + window_with(GH, 'a'),
           ("Slogan matches the slot",) + window_with({**GH, 'hand_col': O37}, 'b'),
           ("Slogan and arrow both match the slot",) + window_with({**GH, 'hand_col': O37, 'arrow_col': O37}, 'c')]
fnt = ImageFont.truetype(FIRA % 'Regular', 18)
pad = 16
cells = []
for label, img, ybot in results:
    act = img.crop((1162 - OX, 1090 - OY, 1782 - OX, ybot - OY))
    right = act.crop((440, 0, act.width - 6, act.height))
    zoom = right.resize((right.width * 3, right.height * 3), Image.LANCZOS)
    cells.append((label, zoom, act))
cw = max(c[1].width for c in cells); ch = max(c[1].height for c in cells)
aw = cells[0][2].width; ah = cells[0][2].height
cols = 3; rows = (len(cells) + cols - 1) // cols
cellW = max(cw, aw // 1) + pad
cellH = 30 + ch + 8 + ah + pad
cv = Image.new('RGB', (pad + cols * cellW, 34 + rows * cellH), (18, 20, 26)); cdd = ImageDraw.Draw(cv)
cdd.text((pad, 8), "Gochi Hand. 3x on top; the bottom of your window at actual size below.", fill=(140, 150, 170), font=ImageFont.truetype(FIRA % 'Regular', 15))
for i, (label, zoom, act) in enumerate(cells):
    x = pad + (i % cols) * cellW; y = 34 + (i // cols) * cellH
    cdd.text((x, y), label, fill=(255, 209, 0), font=fnt)
    cv.paste(zoom, (x, y + 30))
    cv.paste(act.crop((max(0, act.width - cellW + pad), 0, act.width, act.height)), (x, y + 30 + ch + 8))
cv.save(OUT); print(cv.size)
