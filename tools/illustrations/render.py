"""Render the illustration scenes.

usage: python3 render.py OUT_DIR [scene ...]
Writes OUT_DIR/<scene>.png (1200x900) and a contact sheet OUT_DIR/_sheet.jpg.
"""
import sys, os, time, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wc import Art, Renderer

SCENES = {}
for mod in ('scenes_drinks', 'scenes_food', 'scenes_creative'):
    try:
        m = importlib.import_module(mod)
    except ModuleNotFoundError:
        continue
    for attr in ('DRINKS', 'FOOD', 'CREATIVE'):
        SCENES.update(getattr(m, attr, {}))


def main():
    out = sys.argv[1]
    names = sys.argv[2:] or list(SCENES)
    os.makedirs(out, exist_ok=True)
    r = Renderer()
    done = []
    for i, n in enumerate(names):
        t = time.time()
        art = Art(seed=101 + sum(map(ord, n)) % 97)
        SCENES[n](art)
        art.vignette()
        r.render(art, os.path.join(out, n + '.png'))
        done.append(n)
        print(f'{n:24s} {time.time() - t:5.1f}s', flush=True)
    r.close()
    from PIL import Image, ImageDraw, ImageFont
    tw, th = 400, 300
    cols = 4 if len(done) > 3 else len(done)
    rows = (len(done) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * (th + 22)), 'white')
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
    except Exception:
        f = None
    for j, n in enumerate(done):
        im = Image.open(os.path.join(out, n + '.png')).resize((tw, th), Image.LANCZOS)
        x, y = (j % cols) * tw, (j // cols) * (th + 22)
        sheet.paste(im, (x, y + 22))
        d.text((x + 6, y + 3), n, fill='black', font=f)
    sheet.save(os.path.join(out, '_sheet.jpg'), quality=88)


if __name__ == '__main__':
    main()
