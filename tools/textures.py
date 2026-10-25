"""Seamless material textures for template C (Flinders-style station).

    python3 tools/textures.py

writes assets/img/tex/{sandstone,wood-h,wood-v,paint,card}.webp
All tiles are generated at 2x and shown at half size, and tile seamlessly
(noise is made periodic with an FFT filter; strokes are drawn wrapped).
Needs: pip install numpy pillow
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'img', 'tex')
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(13)


def pnoise(h, w, sy, sx=None):
    """periodic gaussian-filtered noise, unit std. sy/sx = blur sigma in px."""
    sx = sy if sx is None else sx
    f = np.fft.fft2(RNG.standard_normal((h, w)))
    ky = np.fft.fftfreq(h)[:, None]
    kx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (math.pi ** 2) * ((ky * sy) ** 2 + (kx * sx) ** 2))
    out = np.real(np.fft.ifft2(f * g))
    return out / (out.std() + 1e-9)


def save(arr, name, q=82):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    im.save(os.path.join(OUT, name), 'WEBP', quality=q, method=6)
    print(name, im.size, os.path.getsize(os.path.join(OUT, name)) // 1024, 'KB')
    return im


def wrapped_lines(w, h, lines, width, blur):
    """draw polylines on a 3x3 canvas and fold back, so strokes wrap seamlessly."""
    cv = Image.new('L', (w * 3, h * 3), 0)
    d = ImageDraw.Draw(cv)
    for pts, val in lines:
        for ox in (0, w, 2 * w):
            for oy in (0, h, 2 * h):
                d.line([(x + ox, y + oy) for x, y in pts], fill=val, width=width)
    if blur:
        cv = cv.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(cv, np.float32)
    return a[h:2 * h, w:2 * w] / 255.0


# ------------------------------------------------------------------ sandstone (ashlar)
def sandstone():
    W, H = 640, 480              # 2x; shown at 320x240
    ch = 80                      # course height
    bw = 160                     # block width
    base = np.array([219, 176, 100], np.float32)
    red = np.array([198, 138, 80], np.float32)
    big = pnoise(H, W, 60)
    mid = pnoise(H, W, 14)
    fine = pnoise(H, W, 1.2)
    sed = pnoise(H, W, 1.5, 40)                     # horizontal sediment
    streak = pnoise(H, W, 70, 6)                    # vertical weathering
    lum = 1 + .035 * big + .03 * mid + .028 * fine + .02 * sed - .03 * np.clip(streak, 0, None)
    hue = np.clip(.5 + .22 * pnoise(H, W, 45), 0, 1)[..., None]
    col = base * (1 - .25 * hue) + red * .25 * hue
    img = col * lum[..., None]
    # per block tone
    yy, xx = np.mgrid[0:H, 0:W]
    row = yy // ch
    off = (row % 2) * (bw // 2)
    blk = ((xx + off) % W) // bw
    tone = np.ones((H, W), np.float32)
    rs = np.random.default_rng(5)
    table = 1 + rs.uniform(-.045, .045, size=(H // ch, W // bw))
    tone = table[row, blk]
    img *= tone[..., None]
    # joints with slight wobble
    wob = pnoise(H, W, 10) * .35
    yj = (yy + wob) % ch
    xj = (xx + off + wob) % bw
    mortar = np.array([236, 214, 164], np.float32)
    jw = 2.6
    hj = (yj < jw) | (yj > ch - .5)
    vj = (xj < jw) | (xj > bw - .5)
    m = (hj | vj)
    img[m] = img[m] * .35 + mortar * .65
    # shadow just below/right of a joint, highlight just above/left of the next
    sh = ((yj >= jw) & (yj < jw + 2.2)) | ((xj >= jw) & (xj < jw + 1.8))
    hl = ((yj > ch - 3) & (yj <= ch - .5)) | ((xj > bw - 2.5) & (xj <= bw - .5))
    img[sh & ~m] *= .86
    img[hl & ~m] = np.minimum(255, img[hl & ~m] * 1.05)
    # speckles
    sp = RNG.random((H, W))
    img[sp < .0035] *= .78
    img[(sp > .9965)] = np.minimum(255, img[sp > .9965] * 1.1)
    img = np.asarray(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.35)), np.float32)
    save(img, 'sandstone.webp')


# ------------------------------------------------------------------ wood
def wood():
    W, H = 1024, 128             # 2x; shown at 512x64
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    warp = pnoise(H, W, 26, 160) * 9 + pnoise(H, W, 6, 50) * 2.2
    y2 = yy + warp
    period = 9.5 + 2.5 * pnoise(H, W, 40, 200)
    rings = .5 + .5 * np.sin(2 * math.pi * y2 / period)
    rings = rings ** 1.8
    fib = pnoise(H, W, .7, 30)
    light = np.array([130, 80, 46], np.float32)
    dark = np.array([70, 40, 22], np.float32)
    t = np.clip(.35 + .45 * rings + .08 * fib + .1 * pnoise(H, W, 18, 220), 0, 1)[..., None]
    img = light * (1 - t) + dark * t
    # pores: short dark dashes
    lines = []
    rs = random.Random(3)
    for _ in range(420):
        x, y = rs.uniform(0, W), rs.uniform(0, H)
        L = rs.uniform(4, 14)
        lines.append(([(x, y), (x + L, y + rs.uniform(-.4, .4))], rs.randint(90, 200)))
    pores = wrapped_lines(W, H, lines, 1, .4)
    img *= (1 - .32 * pores)[..., None]
    img *= (1 + .03 * pnoise(H, W, 2))[..., None]
    save(img, 'wood-h.webp')
    im = Image.open(os.path.join(OUT, 'wood-h.webp')).rotate(90, expand=True)
    im.save(os.path.join(OUT, 'wood-v.webp'), 'WEBP', quality=82, method=6)
    print('wood-v.webp', im.size)


# ------------------------------------------------------------------ painted board
def paint():
    W = H = 512                  # 2x; shown at 256
    base = np.array([29, 52, 41], np.float32)
    lum = 1 + .07 * pnoise(H, W, 50) + .035 * pnoise(H, W, 1.2, 28) + .025 * pnoise(H, W, 1)
    img = base * lum[..., None]
    rs = random.Random(9)
    lines = []
    for _ in range(26):
        x, y = rs.uniform(0, W), rs.uniform(0, H)
        a = rs.uniform(-.25, .25) + (math.pi if rs.random() < .5 else 0)
        L = rs.uniform(20, 120)
        pts = [(x, y)]
        for k in range(6):
            a += rs.uniform(-.08, .08)
            x += math.cos(a) * L / 6
            y += math.sin(a) * L / 6
            pts.append((x, y))
        lines.append((pts, rs.randint(60, 160)))
    scr = wrapped_lines(W, H, lines, 1, .5)
    img = img + scr[..., None] * np.array([34, 38, 30], np.float32)
    save(img, 'paint.webp')


# ------------------------------------------------------------------ ticket card
def card():
    W = H = 512                  # 2x; shown at 256
    base = np.array([246, 233, 200], np.float32)
    lum = 1 + .011 * pnoise(H, W, 40) + .012 * pnoise(H, W, 3) + .012 * pnoise(H, W, .8)
    img = base * lum[..., None]
    rs = random.Random(21)
    dark, lightl = [], []
    for i in range(90):
        x, y = rs.uniform(0, W), rs.uniform(0, H)
        a = rs.uniform(0, 2 * math.pi)
        L = rs.uniform(10, 60)
        pts = [(x, y)]
        for k in range(5):
            a += rs.uniform(-.6, .6)
            x += math.cos(a) * L / 5
            y += math.sin(a) * L / 5
            pts.append((x, y))
        (dark if i % 3 else lightl).append((pts, rs.randint(80, 200)))
    fd = wrapped_lines(W, H, dark, 1, .45)
    fl = wrapped_lines(W, H, lightl, 2, .6)
    img = img * (1 - .07 * fd)[..., None] + fl[..., None] * 10
    save(img, 'card.webp')


if __name__ == '__main__':
    sandstone()
    wood()
    paint()
    card()
