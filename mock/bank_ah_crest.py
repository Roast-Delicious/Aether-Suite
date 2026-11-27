# Bank and Auction House crests (user Nov 27 15:08: "we don't have window
# icons for the bank and auction house"). Flat gold glyphs on the navy disc,
# like gl_banner. White = gold, 0 = cut-out.
import math, sys
from PIL import Image, ImageDraw, ImageFont
W, K = 255, 0
GOLD = (255, 176, 0)

def vault(d, n):                     # Bank A: vault door with a wheel
    c = n / 2
    d.rounded_rectangle([n*.12, n*.12, n*.88, n*.88], radius=n*.08, fill=W)
    d.ellipse([c - n*.29, c - n*.29, c + n*.29, c + n*.29], fill=K)
    d.ellipse([c - n*.22, c - n*.22, c + n*.22, c + n*.22], fill=W)
    d.ellipse([c - n*.07, c - n*.07, c + n*.07, c + n*.07], fill=K)
    for a in range(0, 360, 60):
        r = math.radians(a)
        x1, y1 = c + math.cos(r) * n*.09, c + math.sin(r) * n*.09
        x2, y2 = c + math.cos(r) * n*.19, c + math.sin(r) * n*.19
        d.line([x1, y1, x2, y2], fill=K, width=int(n*.035))
    for y in (n*.25, n*.75):                         # hinges
        d.rectangle([n*.08, y - n*.04, n*.14, y + n*.04], fill=W)

def coins(d, n):                     # Bank B: stacked coins
    def coin(x, y, w):
        h = w * .32
        for i in range(4):
            yy = y - i * h * .55
            d.ellipse([x - w/2, yy - h/2, x + w/2, yy + h/2], fill=W)
            d.arc([x - w/2, yy - h/2, x + w/2, yy + h/2], 0, 180, fill=K, width=max(2, int(n*.018)))
        top = y - 3 * h * .55
        d.ellipse([x - w*.32, top - h*.3, x + w*.32, top + h*.3], outline=K, width=max(2, int(n*.018)))
    coin(n*.34, n*.86, n*.52)
    coin(n*.66, n*.70, n*.52)

def strongbox(d, n):                 # Bank C: strongbox with a lock
    d.rounded_rectangle([n*.12, n*.30, n*.88, n*.84], radius=n*.05, fill=W)
    d.rectangle([n*.12, n*.44, n*.88, n*.48], fill=K)          # lid line
    d.rounded_rectangle([n*.22, n*.16, n*.78, n*.32], radius=n*.06, outline=W, width=int(n*.05))  # handle
    d.rounded_rectangle([n*.41, n*.40, n*.59, n*.62], radius=n*.03, fill=K)
    d.ellipse([n*.47, n*.46, n*.53, n*.52], fill=W)
    d.rectangle([n*.485, n*.50, n*.515, n*.57], fill=W)

def gavel(d, n):                     # AH A: auctioneer's gavel and block
    c = n / 2
    head = [(-.30, -.10), (.08, -.10), (.08, .10), (-.30, .10)]
    ang = math.radians(-40)
    def rot(px, py, cx, cy):
        return (cx + (px*math.cos(ang) - py*math.sin(ang)) * n, cy + (px*math.sin(ang) + py*math.cos(ang)) * n)
    cx, cy = n*.46, n*.40
    d.polygon([rot(x, y, cx, cy) for x, y in head], fill=W)
    hx = [(-.11, -.13), (-.03, -.13), (-.03, .13), (-.11, .13)]          # head bands
    d.polygon([rot(x, y, cx, cy) for x, y in [(-.24, -.10), (-.21, -.10), (-.21, .10), (-.24, .10)]], fill=K)
    d.polygon([rot(x, y, cx, cy) for x, y in [(.0, -.10), (.03, -.10), (.03, .10), (.0, .10)]], fill=K)
    d.polygon([rot(x, y, cx, cy) for x, y in [(-.14, .0), (-.06, .0), (-.06, .50), (-.14, .50)]], fill=W)   # handle
    d.rounded_rectangle([n*.18, n*.78, n*.82, n*.88], radius=n*.03, fill=W)    # block
    d.rectangle([n*.26, n*.72, n*.74, n*.79], fill=W)

def scales(d, n):                    # AH B: balance scales
    c = n / 2
    d.rectangle([c - n*.025, n*.18, c + n*.025, n*.80], fill=W)
    d.rounded_rectangle([n*.30, n*.78, n*.70, n*.86], radius=n*.03, fill=W)
    d.rectangle([n*.14, n*.24, n*.86, n*.28], fill=W)
    d.ellipse([c - n*.05, n*.13, c + n*.05, n*.23], fill=W)
    for x in (n*.22, n*.78):
        d.line([x, n*.28, x - n*.12, n*.56], fill=W, width=int(n*.02))
        d.line([x, n*.28, x + n*.12, n*.56], fill=W, width=int(n*.02))
        d.chord([x - n*.15, n*.46, x + n*.15, n*.66], 0, 180, fill=W)

def tag(d, n):                       # AH C: price tag with a coin
    pts = [(n*.14, n*.42), (n*.42, n*.14), (n*.86, n*.14), (n*.86, n*.58), (n*.58, n*.86)]
    d.polygon(pts, fill=W)
    d.ellipse([n*.66, n*.24, n*.76, n*.34], fill=K)                    # hole
    c = (n*.53, n*.55); r = n*.15
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=K)
    r2 = n*.11
    d.ellipse([c[0] - r2, c[1] - r2, c[0] + r2, c[1] + r2], fill=W)
    d.ellipse([c[0] - n*.05, c[1] - n*.05, c[0] + n*.05, c[1] + n*.05], fill=K)

def glyph(fn, size, S=8):
    N = size * S
    im = Image.new('L', (N, N), 0); fn(ImageDraw.Draw(im), N)
    a = im.resize((size, size), Image.LANCZOS)
    g = Image.new('RGBA', (size, size), GOLD + (0,)); g.putalpha(a)
    return g

rows = [("Bank", [("A  Vault door", vault), ("B  Coin stacks", coins), ("C  Strongbox", strongbox)]),
        ("Auction House", [("A  Gavel", gavel), ("B  Scales", scales), ("C  Price tag", tag)])]
try:
    f = ImageFont.truetype('/home/claude/aether/AetherHub/Media/Fonts/FiraSans-SemiBold.ttf', 26)
    fs = ImageFont.truetype('/home/claude/aether/AetherHub/Media/Fonts/FiraSans-SemiBold.ttf', 20)
except Exception:
    f = fs = ImageFont.load_default()
cell, pad = 300, 24
out = Image.new('RGBA', (pad + 3 * (cell + pad) + 40, 2 * 300 + 20), (14, 18, 28, 255))
d = ImageDraw.Draw(out)
for ri, (title, opts) in enumerate(rows):
    y0 = 20 + ri * 300
    d.text((pad, y0), title, font=f, fill=(230, 236, 245))
    for ci, (label, fn) in enumerate(opts):
        x = pad + ci * (cell + pad)
        y = y0 + 40
        # in-game size: crest disc ~88 px with a 56 px glyph, beside a big one
        disc = Image.new('RGBA', (100, 100), (0, 0, 0, 0)); dd = ImageDraw.Draw(disc)
        dd.ellipse([2, 2, 97, 97], fill=(19, 40, 74, 255), outline=(77, 166, 255, 255), width=3)
        disc.alpha_composite(glyph(fn, 58), (21, 21))
        out.alpha_composite(disc, (x, y))
        d.rounded_rectangle([x + 112, y, x + 112 + 188, y + 188], 12, fill=(19, 40, 74, 255), outline=(77, 166, 255, 255), width=2)
        out.alpha_composite(glyph(fn, 168), (x + 122, y + 10))
        d.text((x, y + 200), label, font=fs, fill=GOLD)
out.convert('RGB').save(sys.argv[1]); print("ok", out.size)
