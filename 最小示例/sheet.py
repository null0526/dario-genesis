import sys, glob, os
from PIL import Image, ImageDraw
d = sys.argv[1]; out = sys.argv[2]; cols = int(sys.argv[3]); w = int(sys.argv[4])
fs = sorted(glob.glob(os.path.join(d, "*.*g")))
ims = []
for f in fs:
    im = Image.open(f).convert("RGB"); h = int(im.height * w / im.width); im = im.resize((w, h))
    ImageDraw.Draw(im).text((6, 6), os.path.basename(f), fill=(255, 0, 255))
    ims.append(im)
rows = (len(ims) + cols - 1) // cols
h = ims[0].height
S = Image.new("RGB", (cols * w, rows * h))
for i, im in enumerate(ims):
    S.paste(im, ((i % cols) * w, (i // cols) * h))
S.save(out, quality=88)
