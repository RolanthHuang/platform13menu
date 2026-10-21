"""Turn a photo into the two web sizes the menu uses.

    python3 tools/add_photo.py ~/Downloads/IMG_1234.jpg latte

writes assets/img/photos/latte.webp (max 1200px) and latte-sm.webp (max 560px).
Then point the item at it in assets/js/menu-data.js:

    imgs: [{ src: 'photos/latte', kind: 'photo' }]

Needs: pip install pillow
"""
import os, sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'img', 'photos')

if len(sys.argv) != 3:
    sys.exit(__doc__)
src, name = sys.argv[1], sys.argv[2]
im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
for suffix, size, q in (('', 1200, 84), ('-sm', 560, 80)):
    c = im.copy()
    c.thumbnail((size, size), Image.LANCZOS)
    path = os.path.join(OUT, name + suffix + '.webp')
    c.save(path, 'WEBP', quality=q, method=6)
    print(path, c.size)
