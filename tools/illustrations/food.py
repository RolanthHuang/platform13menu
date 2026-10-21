"""Painted food: greens, fruit, breads, waffles, sauces, cheese, toppings."""
from parts import *

LIGHT = (-0.62, -0.78)  # light from the upper left


def blob_pts(cx, cy, rx, ry, rot=0.0, amp=0.08, freq=(3, 7), seed=0, n=72, phase=None):
    rng = random.Random(seed)
    ph = [rng.uniform(0, TAU) for _ in freq] if phase is None else phase
    am = [amp * rng.uniform(0.6, 1.2) / (i + 1) for i in range(len(freq))]
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        t = TAU * i / n
        m = 1 + sum(a * math.sin(f * t + p) for a, f, p in zip(am, freq, ph))
        x, y = rx * m * math.cos(t), ry * m * math.sin(t)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def paint_form(art, geom, light, mid, dark, op=0.92, shade=0.5, shift=None, hi=True, hi_op=0.75,
               outline=0.35, line_col=None, disp=2.0, gran=0.3, bloom=0.45, occl=True, hi_scale=0.28, rim=1.2,
               contact=0.3, tex=None, soft=True):
    """Give any 2D shape watercolour volume: lit gradient, soft form shadow, contact shadow, highlight."""
    if geom is None or geom.is_empty:
        return
    d = shp_d(geom)
    if occl:
        art.occlude(d)
    art.wash(d, art.rad([(0, light), (0.55, mid), (1, mix(mid, dark, 0.35))], cx=.36, cy=.32, r=.8), op,
             disp=disp, edge=2.5, rim=rim, dark=0.65, bloom=bloom, gran=gran)
    minx, miny, maxx, maxy = geom.bounds
    sz = max(maxx - minx, maxy - miny)
    sh = shift if shift is not None else sz * 0.18
    cres = geom.difference(affinity.translate(geom, LIGHT[0] * sh, LIGHT[1] * sh))
    if not cres.is_empty and shade > 0:
        if soft:
            art.soft_in(d, shp_d(cres.buffer(sz * 0.02)), dark, shade, blur=max(2, sz * 0.045), disp=4)
        else:
            art.wash(shp_d(cres), dark, shade, disp=disp * 1.2, edge=3, rim=1.0, bloom=0.5, gran=gran)
    if contact > 0:
        low = geom.difference(affinity.translate(geom, 0, -sz * 0.07))
        if not low.is_empty:
            art.soft_in(d, shp_d(low.buffer(sz * 0.01)), mix(dark, '#1e1410', 0.4), contact, blur=max(1.5, sz * 0.02), disp=2)
    if tex:
        col, fq, a_, b_, o_ = tex
        art.texture(d, col, freq=fq, a=a_, b=b_, op=o_)
    if hi:
        c = geom.centroid
        hx, hy = c.x + LIGHT[0] * sz * 0.2, c.y + LIGHT[1] * sz * 0.18
        hp = ell_pts(hx, hy, sz * hi_scale * 0.5, sz * hi_scale * 0.22, 24, rot=-0.5)
        hg = Polygon(hp).buffer(0).intersection(geom.buffer(-sz * 0.04))
        if not hg.is_empty:
            art.gouache(shp_d(hg), '#fffaf0', hi_op, disp=1.5, blur=max(1.5, sz * 0.02))
    if outline:
        art.pencil(d, 1.0, color=line_col or mix(dark, '#2a1d14', 0.5), op=outline, disp=1.6)


# =================================================================== greens
def lettuce(art, cx, cy, L, W, ang, kind='green', k=0.7, seed=0, fold=True):
    rng = random.Random(seed)
    pal = {
        'green': ('#dfeaa2', '#97c25a', '#4f8a35'),
        'pale': ('#eef1c4', '#c3db7f', '#79a84a'),
        'romaine': ('#e6edb2', '#8fbe56', '#4c8434'),
        'radicchio': ('#f2dfe6', '#9c2c55', '#5e1430'),
        'dark': ('#b9d27a', '#5f9a3e', '#2f5f27'),
    }[kind]
    lt, md, dk = pal
    pts = []
    n = 96
    c, s = math.cos(ang), math.sin(ang)
    ph1, ph2, ph3 = rng.uniform(0, TAU), rng.uniform(0, TAU), rng.uniform(0, TAU)
    for i in range(n):
        t = TAU * i / n
        frill = 0.07 * math.sin(t * 15 + ph1) + 0.035 * math.sin(t * 31 + ph2) + 0.10 * math.sin(t * 3 + ph3)
        if kind == 'romaine':
            frill *= 0.6
        x = L * 0.5 * (1 + frill) * math.cos(t)
        y = W * 0.5 * (1 + frill) * math.sin(t) * (1 - 0.25 * math.cos(t))
        pts.append((cx + x * c - y * s, cy + (x * s + y * c) * k))
    poly = Polygon(pts).buffer(0)
    d = shp_d(poly)
    art.occlude(d)
    art.wash(d, art.rad([(0, lt), (0.55, md), (1, dk)], cx=.42, cy=.45, r=.7), 0.93, disp=2.5, edge=2.2, rim=1.4,
             dark=0.6, bloom=0.55, gran=0.25)
    if fold:
        # a fold of shadow across the blade
        fx = rng.uniform(-0.2, 0.25)
        band = [(cx + (fx * L + 0.0) * c - (y) * s, cy + ((fx * L) * s + y * c) * k) for y in (-W, W)]
        bpoly = LineString(band).buffer(W * 0.18, cap_style=2).intersection(poly)
        if not bpoly.is_empty:
            art.wash(shp_d(bpoly), dk, 0.30, disp=4, edge=4, rim=0.8, bloom=0.6)
    # frilled edge shading
    edge = poly.difference(poly.buffer(-max(4, W * 0.07)))
    if not edge.is_empty:
        art.wash(shp_d(edge), dk, 0.25, disp=2, edge=1.5, rim=1.0)
    # midrib and veins
    rib = [(cx + x * c, cy + (x * s) * k) for x in [-L * 0.46 + L * 0.92 * j / 12 for j in range(13)]]
    vein_col = '#fbf6e6' if kind != 'radicchio' else '#f7e9ee'
    art.gouache(d_smooth(rib, closed=False), stroke=vein_col, sw=max(2.0, W * 0.07 if kind == 'romaine' else W * 0.04), op=0.75, blur=0.8)
    vs = []
    for j in range(1, 11):
        x0 = -L * 0.42 + L * 0.84 * j / 11
        for sg in (1, -1):
            x1 = x0 + L * 0.10
            y1 = sg * W * 0.40
            p0 = (cx + x0 * c, cy + (x0 * s) * k)
            p1 = (cx + x1 * c - y1 * s, cy + (x1 * s + y1 * c) * k)
            vs.append(f'M{p0[0]:.1f},{p0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f}')
    if kind == 'radicchio':
        art.gouache(' '.join(vs), stroke=vein_col, sw=1.6, op=0.6, blur=0.6)
    else:
        art.pencil(' '.join(vs), 0.8, color=mix(dk, '#1f3a14', 0.3), op=0.35)
    art.pencil(d, 0.9, color=mix(dk, '#1b2a12', 0.4), op=0.35, disp=1.4)
    return poly


def cherry_tomato_half(art, cx, cy, r, ang=0.0, k=0.75, seed=0, cut=True):
    rng = random.Random(seed)
    outer = Polygon(ell_pts(cx, cy, r, r * k, 48, rot=ang)).buffer(0)
    art.occlude(shp_d(outer))
    if not cut:
        paint_form(art, outer, '#f26a4f', '#d8322b', '#8f1714', hi_op=0.9, outline=0.3, occl=False)
        return outer
    art.wash(shp_d(outer), '#d42f2a', 0.95, disp=1, edge=1.8, rim=1.3, dark=0.6)
    inner = Polygon(ell_pts(cx, cy, r * 0.78, r * k * 0.78, 48, rot=ang)).buffer(0)
    art.wash(shp_d(inner), '#f0624c', 0.85, disp=1, edge=1.5, rim=0.9)
    # chambers with gel and seeds
    for j in range(3):
        a = ang + TAU * j / 3 + 0.5
        ch = Polygon(ell_pts(cx + math.cos(a) * r * 0.36, cy + math.sin(a) * r * 0.36 * k, r * 0.30, r * 0.22 * k, 24, rot=a)).buffer(0)
        art.wash(shp_d(ch), '#f7a58a', 0.75, disp=0.8, edge=1, rim=0.8)
        sd = [(cx + math.cos(a) * r * rng.uniform(0.25, 0.5), cy + math.sin(a) * r * rng.uniform(0.25, 0.5) * k, r * 0.05) for _ in range(3)]
        art.dots(sd, 1, '#f6e3a3', 0.9, blend='normal', wash=False)
    art.gouache(d_smooth(ell_pts(cx, cy, r * 0.10, r * 0.08 * k, 12)), '#ffd2c4', 0.7, disp=0.6, blur=0.6)
    art.gouache(d_smooth(ell_pts(cx - r * 0.42, cy - r * 0.45 * k, r * 0.18, r * 0.07, 12, rot=-0.6)), '#ffffff', 0.7, disp=0.6, blur=1)
    art.pencil(shp_d(outer), 0.8, color='#6e1410', op=0.35)
    return outer


def dried_cranberry(art, x, y, r, seed=0):
    p = Polygon(blob_pts(x, y, r, r * 0.8, rot=seed, amp=0.18, freq=(3, 5, 9), seed=seed, n=36)).buffer(0)
    paint_form(art, p, '#c04050', '#86203a', '#4b0f1f', shade=0.5, hi_op=0.7, outline=0.25, hi_scale=0.4)


def almond(art, x, y, L, ang, seed=0):
    pts = []
    for i in range(40):
        t = TAU * i / 40
        rr = 1 - 0.35 * (1 + math.cos(t)) / 2 * 0
        px = L * 0.5 * math.cos(t)
        py = L * 0.30 * math.sin(t) * (0.55 + 0.45 * (1 - math.cos(t)) / 2)
        c, s = math.cos(ang), math.sin(ang)
        pts.append((x + px * c - py * s, y + px * s + py * c))
    p = Polygon(pts).buffer(0)
    paint_form(art, p, '#d79a5e', '#a5622f', '#5c3016', shade=0.45, hi_op=0.55, outline=0.3)
    rng = random.Random(seed)
    ln = []
    for j in range(5):
        o = -0.3 + 0.15 * j
        c, s = math.cos(ang), math.sin(ang)
        a0 = (x + (-L * 0.35) * c - (o * L * 0.4) * s, y + (-L * 0.35) * s + (o * L * 0.4) * c)
        a1 = (x + (L * 0.30) * c - (o * L * 0.3) * s, y + (L * 0.30) * s + (o * L * 0.3) * c)
        ln.append(d_poly([a0, a1], closed=False))
    art.pencil(' '.join(ln), 0.7, color='#5c3016', op=0.35)


def granola(art, x, y, r, seed=0):
    rng = random.Random(seed)
    pieces = []
    for i in range(7):
        a = rng.uniform(0, TAU)
        rr = r * rng.uniform(0, 0.7)
        pieces.append(Polygon(blob_pts(x + rr * math.cos(a), y + rr * math.sin(a) * 0.8, r * rng.uniform(0.25, 0.45),
                                       r * rng.uniform(0.2, 0.35), rot=rng.uniform(0, 3), amp=0.25, freq=(3, 6), seed=seed + i, n=24)).buffer(0))
    g = unary_union(pieces)
    paint_form(art, g, '#ecc77e', '#c99144', '#7c4f1f', shade=0.5, hi_op=0.5, outline=0.3, gran=0.5)
    oats = [(x + rng.uniform(-r, r) * 0.6, y + rng.uniform(-r, r) * 0.5, r * 0.12) for _ in range(5)]
    art.dots(oats, 1, '#f8e7bf', 0.8, blend='normal', wash=False)


def drizzle(art, pts, color='#3a1d14', width=4.0, op=0.9, hi=True):
    d = d_smooth(pts, closed=False)
    art.stroke_wash(d, color, width, op, disp=1.2, edge=1.0, rim=1.2, dark=0.6)
    if hi:
        art.gouache(d_smooth([(x - 1, y - width * 0.25) for x, y in pts], closed=False), stroke='#ffffff', sw=max(0.8, width * 0.22), op=0.55)


def zigzag(x0, y0, x1, y1, n=6, amp=20.0, seed=0, jitter_=4):
    rng = random.Random(seed)
    pts = []
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    for i in range(n * 4 + 1):
        t = i / (n * 4)
        w = amp * math.sin(t * n * math.pi)
        pts.append((x0 + dx * t + nx * w + rng.uniform(-jitter_, jitter_), y0 + dy * t + ny * w + rng.uniform(-jitter_, jitter_)))
    return pts


def salad_mound(art, cx, cy, w, h, k=0.62, seed=1, kinds=('green', 'pale', 'radicchio', 'green', 'dark'), n=18,
                toppings=True, caesar=False, tomatoes=4):
    rng = random.Random(seed)
    leaves = []
    for i in range(n):
        f = i / n
        # back leaves first (higher on screen), front ones later
        yy = cy - h * 0.45 + h * 0.9 * f + rng.uniform(-h * 0.08, h * 0.08)
        span = w * (0.55 + 0.45 * math.sin(math.pi * min(0.999, 0.15 + f * 0.85)))
        xx = cx + rng.uniform(-span * 0.5, span * 0.5)
        kind = 'romaine' if caesar else kinds[rng.randrange(len(kinds))]
        L = rng.uniform(0.42, 0.62) * w * (0.75 if caesar else 0.6)
        W = L * rng.uniform(0.45, 0.7) * (0.75 if caesar else 1)
        leaves.append(lettuce(art, xx, yy, L, W, rng.uniform(-0.9, 0.9) + (math.pi / 2 if caesar and rng.random() < 0.3 else 0),
                              kind=kind, k=k, seed=seed * 31 + i))
        if caesar and i % 2 == 1:
            # creamy dressing on the leaf
            cpts = []
            for _ in range(4):
                bx, by = xx + rng.uniform(-L * 0.35, L * 0.35), yy + rng.uniform(-W * 0.2, W * 0.2) * k
                cpts.append(Polygon(blob_pts(bx, by, L * 0.16, L * 0.08, rot=rng.uniform(0, 3), amp=0.3, freq=(3, 5), seed=seed + i * 7, n=24)).buffer(0))
            cg = unary_union(cpts).intersection(leaves[-1])
            if not cg.is_empty:
                art.wash(shp_d(cg), '#f3ecd4', 0.85, blend='normal', disp=2, edge=1.5, rim=0.6)
                pep = [(rng.uniform(cg.bounds[0], cg.bounds[2]), rng.uniform(cg.bounds[1], cg.bounds[3]), rng.uniform(0.6, 1.3)) for _ in range(14)]
                pep = [p for p in pep if cg.contains(Point(p[0], p[1]))]
                art.dots(pep, 1, '#3b3530', 0.7, wash=False)
    mound = unary_union(leaves)
    if toppings:
        for j in range(tomatoes):
            tx, ty = cx + rng.uniform(-w * 0.32, w * 0.32), cy + rng.uniform(-h * 0.25, h * 0.32)
            cherry_tomato_half(art, tx, ty, w * 0.055, ang=rng.uniform(0, 3), k=0.72, seed=j)
        if not caesar:
            for j in range(5):
                dried_cranberry(art, cx + rng.uniform(-w * 0.3, w * 0.3), cy + rng.uniform(-h * 0.3, h * 0.3), w * 0.022, seed=j)
            for j in range(3):
                almond(art, cx + rng.uniform(-w * 0.28, w * 0.28), cy + rng.uniform(-h * 0.3, h * 0.25), w * 0.06, rng.uniform(0, 3), seed=j)
            for j in range(4):
                granola(art, cx + rng.uniform(-w * 0.3, w * 0.3), cy + rng.uniform(-h * 0.35, h * 0.2), w * 0.04, seed=j)
            for j in range(2):
                x0 = cx - w * 0.3 + rng.uniform(-20, 20)
                drizzle(art, zigzag(x0, cy - h * 0.1 + j * h * 0.25, x0 + w * 0.55, cy + j * h * 0.2, n=4, amp=h * 0.12, seed=j), '#4a2219', 2.4, 0.7)
    return mound


# =================================================================== fried & baked
def fries(art, cx, cy, n=12, L=150, wdt=17, k=0.6, seed=3, spread=1.0, color=('#f6d48a', '#e2a443', '#a8601f')):
    rng = random.Random(seed)
    geoms = []
    for i in range(n):
        a = rng.uniform(-0.9, 0.9) + (0 if i % 2 else math.pi / 2 * 0.3)
        x = cx + rng.uniform(-L * 0.45, L * 0.45) * spread
        y = cy + rng.uniform(-L * 0.25, L * 0.25) * k * spread
        ll = L * rng.uniform(0.55, 1.0)
        c, s = math.cos(a), math.sin(a)
        p0 = (x - c * ll / 2, y - s * ll / 2 * k)
        p1 = (x + c * ll / 2, y + s * ll / 2 * k)
        g = LineString([p0, p1]).buffer(wdt * rng.uniform(0.8, 1.1) / 2, cap_style=2, join_style=2)
        g = g.buffer(3, join_style=1).buffer(-3, join_style=1)
        paint_form(art, g, color[0], color[1], color[2], shade=0.45, hi_op=0.6, outline=0.3, hi_scale=0.35, gran=0.35)
        # browned ends
        for pe in (p0, p1):
            art.wash(shp_d(Point(pe).buffer(wdt * 0.55).intersection(g)), color[2], 0.35, disp=1.5, edge=1.5)
        geoms.append(g)
    herb = [(cx + rng.uniform(-L * 0.5, L * 0.5), cy + rng.uniform(-L * 0.3, L * 0.3) * k, rng.uniform(1, 2.2)) for _ in range(30)]
    art.dots(herb, 1, '#5f7a2e', 0.6, wash=False)
    pep = [(cx + rng.uniform(-L * 0.5, L * 0.5), cy + rng.uniform(-L * 0.3, L * 0.3) * k, rng.uniform(0.6, 1.2)) for _ in range(30)]
    art.dots(pep, 1, '#3a2c22', 0.6, wash=False)
    return unary_union(geoms)


def crinkle_chips(art, cx, cy, n=5, r=46, k=0.55, seed=4):
    rng = random.Random(seed)
    for i in range(n):
        x = cx + rng.uniform(-r * 1.4, r * 1.4)
        y = cy + rng.uniform(-r * 0.6, r * 0.6)
        rot = rng.uniform(-0.6, 0.6)
        p = Polygon(blob_pts(x, y, r * rng.uniform(0.8, 1.1), r * k * rng.uniform(0.8, 1.2), rot=rot, amp=0.06, freq=(4, 9), seed=seed + i)).buffer(0)
        paint_form(art, p, '#fbeec2', '#ecd08a', '#b9873c', shade=0.35, hi_op=0.5, outline=0.35, gran=0.3)
        ridges = []
        for j in range(-4, 5):
            c, s = math.cos(rot + 0.3), math.sin(rot + 0.3)
            o = j * r * 0.2
            pts = [(x + (t * r) * c - o * s, y + ((t * r) * s + o * c) * k) for t in [-1.2 + 2.4 * q / 10 for q in range(11)]]
            ln = LineString(pts).intersection(p)
            if not ln.is_empty and ln.geom_type == 'LineString':
                ridges.append(d_smooth(list(ln.coords), closed=False))
        art.stroke_wash(' '.join(ridges), '#c89a4c', 2.4, 0.45, disp=1.6, edge=1, rim=1.0)
        art.gouache(' '.join(ridges), stroke='#fffbea', sw=0.9, op=0.5)


def bread_slice(art, poly, crust=('#d79a52', '#a7602a'), crumb=('#fbeccb', '#eed3a0'), seed=0, toast=0.3, pores=60, crust_w=10):
    """A cut bread face with crust rim and airy crumb."""
    rng = random.Random(seed)
    art.occlude(shp_d(poly))
    art.wash(shp_d(poly), art.lin([(0, crust[0]), (1, crust[1])], 0, 0, 1, 1), 0.9, disp=1.8, edge=2, rim=1.2, gran=0.35)
    inner = poly.buffer(-crust_w, join_style=1)
    if inner.is_empty:
        return
    art.wash(shp_d(inner), art.rad([(0, crumb[0]), (1, crumb[1])], cx=.4, cy=.4, r=.75), 0.95, blend='normal', disp=1.5, edge=2, rim=0.8, gran=0.3)
    if toast:
        art.wash(shp_d(inner), art.rad([(0, '#e3ad62', 0), (0.7, '#d89a50', toast), (1, '#b8742f', toast * 1.4)], cx=.45, cy=.45, r=.7), 0.8,
                 disp=3, edge=3, rim=0.8, bloom=0.6)
    minx, miny, maxx, maxy = inner.bounds
    pp = []
    for _ in range(pores):
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        if inner.contains(Point(x, y)):
            pp.append((x, y, rng.uniform(0.8, 2.6)))
    art.dots(pp, 1.5, '#c99a5a', 0.5, disp=0.8, edge=0.8)
    art.pencil(shp_d(poly), 1.0, color='#6a3d1c', op=0.4)


def croissant(art, cx, cy, size=1.0, ang=0.0, k=0.62, seed=2, glaze=True):
    """Seven rolled lobes along a crescent."""
    rng = random.Random(seed)
    R = 150 * size
    lobes = []
    n = 7
    for i in range(n):
        f = i / (n - 1)
        th = math.pi * (1.10 + 0.80 * f)            # along an upward arc
        rr = R * (0.92 + 0.08 * math.sin(math.pi * f))
        x, y = rr * math.cos(th), rr * math.sin(th) * 0.55 + R * 0.38
        wbig = (0.28 + 0.34 * math.sin(math.pi * f) ** 1.2) * R
        lobes.append((x, y, wbig, th))
    c, s = math.cos(ang), math.sin(ang)

    def T(x, y):
        return (cx + x * c - y * s, cy + (x * s + y * c) * k + 0)
    # body silhouette (for shadow) then lobes painted from the tips inward, centre lobe last
    order = sorted(range(n), key=lambda i: -abs(i - (n - 1) / 2))
    polys = []
    for i in order:
        x, y, wb, th = lobes[i]
        tang = th + math.pi / 2
        pts = []
        for j in range(40):
            t = TAU * j / 40
            px = wb * 0.36 * math.cos(t)
            py = wb * 0.62 * math.sin(t) * (1.0 if math.sin(t) > 0 else 0.85)
            qx = x + px * math.cos(tang) - py * math.sin(tang)
            qy = y + px * math.sin(tang) + py * math.cos(tang)
            pts.append(T(qx, qy))
        polys.append((i, Polygon(pts).buffer(0)))
    allp = unary_union([p for _, p in polys])
    mb = allp.bounds
    cast_shadow(art, (mb[0] + mb[2]) / 2, mb[3] - 10, (mb[2] - mb[0]) * 0.5, (mb[3] - mb[1]) * 0.25, op=0.28, blur=14, dx=24, dy=6)
    for i, p in polys:
        f = abs(i - (n - 1) / 2) / ((n - 1) / 2)
        light = mix('#f6cf86', '#f2c070', f)
        paint_form(art, p, light, '#d99540', '#8e4c18', shade=0.55, hi_op=0.65, outline=0.38, gran=0.4, hi_scale=0.32)
        # flaky layer lines along each lobe
        x, y, wb, th = lobes[i]
        tang = th + math.pi / 2
        ls = []
        for q in range(4):
            off = -0.5 + q * 0.33
            pts = []
            for j in range(12):
                t = -1 + 2 * j / 11
                px = wb * 0.30 * off + 0.02 * wb * math.sin(t * 3)
                py = wb * 0.55 * t
                qx = x + px * math.cos(tang) - py * math.sin(tang)
                qy = y + px * math.sin(tang) + py * math.cos(tang)
                pts.append(T(qx, qy))
            ls.append(d_smooth(pts, closed=False))
        art.pencil(' '.join(ls), 0.8, color='#8a4a18', op=0.32, disp=1.2)
    if glaze:
        g = []
        for _ in range(25):
            x, y = rng.uniform(mb[0], mb[2]), rng.uniform(mb[1], mb[1] + (mb[3] - mb[1]) * 0.6)
            if allp.contains(Point(x, y)):
                g.append((x, y, rng.uniform(1.2, 3.2)))
        art.dots(g, 2, '#fff6dc', 0.6, blend='normal', wash=False)
    return allp


# =================================================================== waffle & toppings
def waffle_wedge(art, pts4, depth=26, cells=(5, 4), seed=0, tone=1.0):
    """pts4: top face corners (screen) A,B,C,D; side drops by depth. Grid pockets on top."""
    A, B, C, D = pts4
    top = Polygon([A, B, C, D]).buffer(0)
    sides = []
    for P0, P1 in ((C, D), (B, C)):
        q = Polygon([P0, P1, (P1[0], P1[1] + depth), (P0[0], P0[1] + depth)]).buffer(0)
        sides.append(q)
    body = unary_union([top] + sides).buffer(2, join_style=1).buffer(-2, join_style=1)
    art.occlude(shp_d(body))
    sd = shp_d(unary_union(sides).difference(top))
    art.wash(sd, art.lin([(0, '#c6833d'), (1, '#8a4b1d')], 0, 0, 0, 1), 0.9, disp=1.5, edge=2, rim=1.2, gran=0.4)
    art.wash(shp_d(top), art.rad([(0, '#efc47a'), (0.6, '#dc9d4c'), (1, '#b56e2a')], cx=.4, cy=.35, r=.8), 0.92, disp=1.5, edge=2.5, rim=1.2, gran=0.45)
    # pockets
    nu, nv = cells

    def M(u, v):
        x = (1 - u) * (1 - v) * A[0] + u * (1 - v) * B[0] + u * v * C[0] + (1 - u) * v * D[0]
        y = (1 - u) * (1 - v) * A[1] + u * (1 - v) * B[1] + u * v * C[1] + (1 - u) * v * D[1]
        return (x, y)
    pockets, rims = [], []
    m = 0.16
    for i in range(nu):
        for j in range(nv):
            u0, u1 = (i + m) / nu, (i + 1 - m) / nu
            v0, v1 = (j + m) / nv, (j + 1 - m) / nv
            p = Polygon([M(u0, v0), M(u1, v0), M(u1, v1), M(u0, v1)]).buffer(0)
            pockets.append(p)
            # inner shadow on the upper-left walls of each pocket
            rims.append(Polygon([M(u0, v0), M(u1, v0), M(u1 - 0.05 / nu * 3, v0 + 0.25 / nv), M(u0 + 0.25 / nu, v0 + 0.25 / nv), M(u0 + 0.25 / nu, v1 - 0.05 / nv), M(u0, v1)]).buffer(0))
    pk = unary_union(pockets).intersection(top)
    art.wash(shp_d(pk), '#c27a31', 0.55, disp=1, edge=1.5, rim=1.3, gran=0.4)
    rk = unary_union(rims).intersection(top)
    art.wash(shp_d(rk), '#7b3f14', 0.45, disp=0.8, edge=1, rim=1.0)
    # ridge highlights
    hl = []
    for i in range(nu + 1):
        hl.append(d_poly([M(i / nu, 0.02), M(i / nu, 0.98)], closed=False))
    for j in range(nv + 1):
        hl.append(d_poly([M(0.02, j / nv), M(0.98, j / nv)], closed=False))
    art.gouache(' '.join(hl), stroke='#ffe7b5', sw=1.6, op=0.55, blur=0.6)
    art.pencil(shp_d(body), 1.0, color='#5e3112', op=0.42)
    return body


def whipped_cream(art, cx, cy, r, k=0.75, seed=0, peak=True):
    rng = random.Random(seed)
    tiers = []
    for i in range(4):
        rr = r * (1 - i * 0.22)
        yy = cy - i * r * 0.32
        tiers.append(Polygon(blob_pts(cx + rng.uniform(-3, 3), yy, rr, rr * k * 0.55, amp=0.08, freq=(5, 8), seed=seed + i, n=48)).buffer(0))
    if peak:
        tiers.append(Polygon([(cx - r * 0.2, cy - r * 0.95), (cx + r * 0.05, cy - r * 1.35), (cx + r * 0.22, cy - r * 0.95)]).buffer(r * 0.1, join_style=1))
    g = unary_union(tiers)
    art.occlude(shp_d(g))
    art.wash(shp_d(g), '#fbf7ee', 0.9, blend='normal', disp=2, edge=2, rim=0.6)
    for t in tiers:
        sh = t.difference(affinity.translate(t, -r * 0.14, -r * 0.1))
        art.wash(shp_d(sh), '#b8b6c8', 0.35, disp=2, edge=2, rim=0.8, bloom=0.5)
    art.pencil(shp_d(g), 0.9, color='#8d8aa0', op=0.35)
    return g


def banana_slice(art, x, y, r, k=0.8, ang=0.0, seed=0, fresh=True):
    p = Polygon(blob_pts(x, y, r, r * k, rot=ang, amp=0.04, freq=(3, 5), seed=seed, n=40)).buffer(0)
    art.occlude(shp_d(p))
    art.wash(shp_d(p), art.rad([(0, '#fff6d8'), (0.75, '#f6e8b6'), (1, '#e8cf86')], cx=.45, cy=.42, r=.6), 0.95, disp=1, edge=2, rim=1.1)
    rng = random.Random(seed)
    seeds = []
    for j in range(7):
        a = TAU * j / 7 + rng.uniform(-0.2, 0.2)
        seeds.append((x + math.cos(a) * r * 0.32, y + math.sin(a) * r * 0.32 * k, r * 0.05))
    art.dots(seeds, 1, '#8a6a3a', 0.6, disp=0.5, edge=0.5)
    art.wash(shp_d(Point(x, y).buffer(r * 0.22)), '#e7d39a', 0.45, disp=1, edge=1)
    art.pencil(shp_d(p), 0.8, color='#9a7a3c', op=0.4)
    return p


def kiwi_wedge(art, x, y, r, ang=0.0, seed=0):
    pts = [(x, y)]
    for j in range(13):
        a = ang - 0.55 + 1.1 * j / 12
        pts.append((x + r * math.cos(a), y + r * math.sin(a) * 0.8))
    p = Polygon(pts).buffer(1)
    art.occlude(shp_d(p))
    art.wash(shp_d(p), art.rad([(0, '#f2f4c8'), (0.35, '#b9d24c'), (0.9, '#8db53a'), (1, '#6c5a2a')], cx=0, cy=.5, r=1.0), 0.95, disp=1, edge=1.5, rim=1.2)
    rng = random.Random(seed)
    sd = []
    for j in range(9):
        a = ang - 0.45 + 0.9 * j / 8
        sd.append((x + r * 0.42 * math.cos(a), y + r * 0.42 * math.sin(a) * 0.8, r * 0.05))
    art.dots(sd, 1, '#2a2416', 0.8, wash=False)
    art.pencil(shp_d(p), 0.8, color='#4a5a1a', op=0.4)


def strawberry_cut(art, x, y, r, ang=0.0, seed=0):
    pts = []
    for j in range(40):
        t = TAU * j / 40
        px = r * 0.8 * math.sin(t)
        py = -r * math.cos(t) * (1.05 if math.cos(t) > 0 else 0.8)
        px *= (1 - 0.25 * (1 + math.cos(t)) / 2)
        c, s = math.cos(ang), math.sin(ang)
        pts.append((x + px * c - py * s, y + px * s + py * c))
    p = Polygon(pts).buffer(0)
    art.occlude(shp_d(p))
    art.wash(shp_d(p), art.rad([(0, '#ffd0c8'), (0.45, '#f06a6a'), (1, '#c81f2e')], cx=.5, cy=.55, r=.6), 0.95, disp=1, edge=2, rim=1.3)
    art.pencil(shp_d(p), 0.8, color='#7a1018', op=0.4)


def powdered_sugar(art, geom, n=220, seed=0, op=0.7):
    rng = random.Random(seed)
    minx, miny, maxx, maxy = geom.bounds
    pts = []
    for _ in range(n * 3):
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        if geom.contains(Point(x, y)):
            pts.append((x, y, rng.uniform(0.5, 1.6)))
        if len(pts) >= n:
            break
    art.dots(pts, 1, '#ffffff', op, blend='normal', wash=False)


# =================================================================== savoury bits
def mushroom_slice(art, x, y, s, ang=0.0, seed=0, cooked=True):
    """Vertical slice through a button mushroom: cap dome + stem."""
    pts = []
    for j in range(25):
        t = math.pi * j / 24
        pts.append((s * 0.62 * math.cos(math.pi - t), -s * 0.42 * math.sin(t) - s * 0.05))
    pts += [(s * 0.62, -s * 0.02), (s * 0.20, s * 0.02), (s * 0.20, s * 0.48), (-s * 0.20, s * 0.48), (-s * 0.20, s * 0.02), (-s * 0.62, -s * 0.02)]
    c, sn = math.cos(ang), math.sin(ang)
    P2 = [(x + px * c - py * sn, y + px * sn + py * c) for px, py in pts]
    g = Polygon(P2).buffer(s * 0.05, join_style=1)
    art.occlude(shp_d(g))
    inner = '#e7d2ac' if cooked else '#f6eedc'
    art.wash(shp_d(g), art.rad([(0, inner), (1, '#b88a55' if cooked else '#d9c4a0')], cx=.5, cy=.4, r=.7), 0.95, disp=1.2, edge=1.8, rim=1.0)
    rimp = g.difference(g.buffer(-s * 0.07))
    art.wash(shp_d(rimp), '#7a4f2c' if cooked else '#a98b62', 0.75, disp=1, edge=1, rim=1.1)
    if cooked:
        art.wash(shp_d(g), '#8a5a2e', 0.25, disp=3, edge=3, bloom=0.7)
    art.pencil(shp_d(g), 0.8, color='#4e321d', op=0.4)
    return g


def sauteed_mushrooms(art, cx, cy, w, h, n=16, seed=3, herbs=True):
    rng = random.Random(seed)
    gs = []
    for i in range(n):
        x = cx + rng.uniform(-w * 0.45, w * 0.45)
        y = cy + rng.uniform(-h * 0.4, h * 0.4) + i * 0.6
        gs.append(mushroom_slice(art, x, y, rng.uniform(0.11, 0.16) * w, ang=rng.uniform(-1.2, 1.2), seed=i))
    if herbs:
        hp = [(cx + rng.uniform(-w * 0.5, w * 0.5), cy + rng.uniform(-h * 0.5, h * 0.5), rng.uniform(1.4, 3.0)) for _ in range(40)]
        art.dots(hp, 2, '#4f7a2a', 0.75, disp=1, edge=0.8)
    return unary_union(gs)


def veggie_bacon(art, x0, y0, L, wdt, ang=0.0, waves=3, seed=0):
    """Wavy strip, reddish-brown with lighter marbling bands."""
    rng = random.Random(seed)
    c, s = math.cos(ang), math.sin(ang)
    mid = []
    for j in range(31):
        t = j / 30
        px = t * L
        py = math.sin(t * math.pi * waves + seed) * wdt * 0.35
        mid.append((x0 + px * c - py * s, y0 + px * s + py * c))
    L_ = LineString(mid)
    g = L_.buffer(wdt / 2, cap_style=2, join_style=1)
    art.occlude(shp_d(g))
    art.wash(shp_d(g), art.lin([(0, '#c5533a'), (1, '#8e2f22')], 0, 0, 0, 1), 0.95, disp=1.8, edge=2, rim=1.3, gran=0.35)
    for off, col, w2, o in ((wdt * 0.18, '#f0b49a', wdt * 0.12, 0.55), (-wdt * 0.22, '#e7a184', wdt * 0.09, 0.45)):
        o2 = L_.parallel_offset(abs(off), 'left' if off > 0 else 'right')
        if o2.geom_type == 'LineString':
            art.stroke_wash(d_smooth(list(o2.coords)[::2], closed=False), col, w2, o, disp=2, edge=1, rim=0.8)
    art.gouache(d_smooth([(px, py - wdt * 0.3) for px, py in mid[2:-2:2]], closed=False), stroke='#fff0e6', sw=1.4, op=0.5)
    art.pencil(shp_d(g), 0.9, color='#5a1c12', op=0.4)
    return g


def melted_cheese(art, geom, seed=0, color=('#fbe7a4', '#f2c65a', '#c98a2c'), browned=0.35):
    rng = random.Random(seed)
    art.occlude(shp_d(geom))
    art.wash(shp_d(geom), art.rad([(0, color[0]), (0.6, color[1]), (1, color[2])], cx=.45, cy=.4, r=.75), 0.92, disp=2, edge=2, rim=1.1, bloom=0.5)
    if browned:
        minx, miny, maxx, maxy = geom.bounds
        spots = []
        for _ in range(18):
            x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
            if geom.contains(Point(x, y)):
                spots.append(Polygon(blob_pts(x, y, rng.uniform(5, 14), rng.uniform(3, 8), rot=rng.uniform(0, 3), amp=0.3, freq=(3, 5), seed=rng.randint(0, 99), n=20)).buffer(0))
        sp = unary_union(spots).intersection(geom)
        if not sp.is_empty:
            art.wash(shp_d(sp), '#c6802e', browned, disp=1.5, edge=1.5, rim=1.0)
    gl = []
    minx, miny, maxx, maxy = geom.bounds
    for _ in range(10):
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        if geom.contains(Point(x, y)):
            gl.append(d_smooth(ell_pts(x, y, rng.uniform(4, 9), rng.uniform(1.5, 3), 12, rot=-0.4)))
    if gl:
        art.gouache(' '.join(gl), '#fffbe8', 0.75, disp=0.8, blur=0.8)
    art.pencil(shp_d(geom), 0.9, color='#9a6a1c', op=0.35)


def herb_flecks(art, cx, cy, w, h, n=50, seed=0, color='#4f7a2a'):
    rng = random.Random(seed)
    pts = [(cx + rng.uniform(-w / 2, w / 2), cy + rng.uniform(-h / 2, h / 2), rng.uniform(0.8, 2.2)) for _ in range(n)]
    art.dots(pts, 1, color, 0.7, disp=0.6, edge=0.5)
