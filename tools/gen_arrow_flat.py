# Talent arrows, Nov 25 15:18 (user: same thickness everywhere, no 3D, no
# double heads): one FLAT white arrowhead, tinted in game (gold / blue /
# gray). Same shape and orientation as arrow_head_gray (its alpha), no
# shading. Run from tools/.
import struct, numpy as np
from PIL import Image
def write_tga(path, alpha):
    h, w = alpha.shape
    a = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8); rgba[..., 0:3] = 255; rgba[..., 3] = a
    rows = rgba[::-1]; bgra = rows[..., [2, 1, 0, 3]]
    hdr = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    with open(path, 'wb') as fh: fh.write(hdr); fh.write(bgra.tobytes())
M = '/home/claude/brand/AetherSkins/Media/'
a = np.array(Image.open(M + 'arrow_head_gray.tga').convert('RGBA'))[..., 3] / 255.0
write_tga(M + 'arrow_head_flat.tga', a)
print('arrow_head_flat.tga', a.shape)
