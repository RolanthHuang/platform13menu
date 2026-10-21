"""Build the small web fonts used by the menu.

The Chinese handwriting face (LXGW WenKai TC, SIL Open Font License) is
subset to only the characters that appear on the site, so the whole font is
a few hundred KB instead of tens of MB. Run this again after you add menu
items with new characters:

    npm install @fontsource/lxgw-wenkai-tc @fontsource/overpass   (once, anywhere)
    python3 tools/build_fonts.py /path/to/node_modules

Needs: pip install fonttools brotli
"""
import io, os, re, sys, glob
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.merge import Merger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'fonts')
SOURCES = ['index.html', 'assets/js/app.js', 'assets/js/menu-data.js']


def site_text():
    chars = set()
    for p in SOURCES:
        with open(os.path.join(ROOT, p), encoding='utf-8') as f:
            chars |= set(f.read())
    # ASCII, common punctuation and digits always
    chars |= set(chr(c) for c in range(0x20, 0x7f))
    chars |= set('，。、：；！？「」『』（）《》〈〉…—～・·○●◀▶←→')
    return ''.join(sorted(c for c in chars if ord(c) >= 0x20))


def build_wenkai(nm, weight, text):
    files = sorted(glob.glob(os.path.join(nm, '@fontsource/lxgw-wenkai-tc/files', f'lxgw-wenkai-tc-*-{weight}-normal.woff2')))
    need = set(ord(c) for c in text)
    picked = []
    for fpath in files:
        f = TTFont(fpath)
        cmap = f.getBestCmap() or {}
        if need & set(cmap):
            picked.append(fpath)
    print(f'wenkai {weight}: {len(picked)} of {len(files)} chunks contain site characters')
    tmp = []
    for i, fpath in enumerate(picked):
        f = TTFont(fpath)
        f.flavor = None
        cmap = set((f.getBestCmap() or {}).keys())
        opts = subset.Options()
        opts.layout_features = ['*']
        opts.notdef_outline = True
        opts.name_IDs = ['*']
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=sorted(need & cmap))
        sub.subset(f)
        path = os.path.join(OUT, f'_tmp_{weight}_{i}.ttf')
        f.save(path)
        tmp.append(path)
    merged = Merger().merge(tmp)
    merged.flavor = 'woff2'
    out = os.path.join(OUT, f'wenkai-{weight}.woff2')
    merged.save(out)
    for p in tmp:
        os.remove(p)
    print(' ->', out, os.path.getsize(out) // 1024, 'KB')


def copy_overpass(nm):
    import shutil
    for w in (600, 800):
        src = os.path.join(nm, '@fontsource/overpass/files', f'overpass-latin-{w}-normal.woff2')
        shutil.copy(src, os.path.join(OUT, f'overpass-{w}.woff2'))


if __name__ == '__main__':
    nm = sys.argv[1] if len(sys.argv) > 1 else 'node_modules'
    os.makedirs(OUT, exist_ok=True)
    text = site_text()
    print(len(text), 'distinct characters')
    for w in (400, 700):
        build_wenkai(nm, w, text)
    copy_overpass(nm)
