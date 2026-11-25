# Gossip option text color (user, Nov 25): white now; Aether blue or gold.
from PIL import Image, ImageDraw
from talent_details import F
SRC = Image.open('/mnt/user-data/uploads/a02f4015-image.png').convert('RGB')
crop = SRC.crop((30, 160, 520, 300))
BG = SRC.getpixel((300, 290))
OPTS = [("A  White (now)", (235, 238, 245)), ("B  Aether blue  (my pick)", (77, 166, 255)), ("C  Aether gold", (255, 176, 0))]
W = crop.width; H = crop.height
sheet = Image.new('RGB', (W * 3 + 80, H + 70), (16, 18, 24)); d = ImageDraw.Draw(sheet)
for i, (t, c) in enumerate(OPTS):
    im = crop.copy(); dd = ImageDraw.Draw(im)
    dd.rectangle([34, 98, 300, 128], fill=BG)          # cover "I need a ride."
    dd.text((37, 114), "I need a ride.", font=F(18), fill=c, anchor='lm')
    x = 20 + i * (W + 20)
    d.text((x, 18), t, font=F(20, 'SemiBold'), fill=(255, 176, 0))
    sheet.paste(im, (x, 55))
sheet.save('out_gossip_opt.png'); print(sheet.size)
