"""Compositions for the drinks that have no photo yet."""
from food import *


def smooth_profile(ts, rs):
    """piecewise cubic (Catmull-Rom) radius profile through control points."""
    def f(t):
        if t <= ts[0]:
            return rs[0]
        if t >= ts[-1]:
            return rs[-1]
        for i in range(len(ts) - 1):
            if ts[i] <= t <= ts[i + 1]:
                u = (t - ts[i]) / (ts[i + 1] - ts[i])
                p0 = rs[max(i - 1, 0)]
                p1, p2 = rs[i], rs[i + 1]
                p3 = rs[min(i + 2, len(rs) - 1)]
                return 0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
        return rs[-1]
    return f


def stemless(cx, top_y, k=0.36, s=1.0):
    return Revolve(cx, top_y, 300 * s, k, smooth_profile([0, 0.2, 0.45, 0.65, 0.85, 1.0], [98 * s, 116 * s, 127 * s, 123 * s, 103 * s, 68 * s]))


def tumbler(cx, top_y, k=0.36, s=1.0):
    return Revolve(cx, top_y, 430 * s, k, lambda t: (112 - 20 * t) * s)


def mason(cx, top_y, k=0.36, s=1.0):
    def R(t):
        if t < 0.10:
            r = 92
        elif t < 0.22:
            u = (t - 0.10) / 0.12
            r = 92 + 20 * (3 * u * u - 2 * u ** 3)
        elif t < 0.94:
            r = 112 + 2 * (t - 0.22)
        else:
            r = 113 - 26 * ((t - 0.94) / 0.06) ** 2
        return r * s
    return Revolve(cx, top_y, 360 * s, k, R)


def mason_threads(art, rev):
    for t in (0.022, 0.050, 0.078):
        ex, ey, erx, ery = rev.ell(t)
        arc = ell_pts(ex, ey, erx + 3, ery + 1, 60, a0=0.05, a1=math.pi - 0.05)
        art.stroke_wash(d_smooth(arc, closed=False), '#9bb0b8', 2.2, 0.5, disp=0.8, edge=0.8, rim=0.8)
        arc2 = ell_pts(ex, ey - 3, erx + 3, ery + 1, 60, a0=0.4, a1=1.6)
        art.gouache(d_smooth(arc2, closed=False), stroke='#ffffff', sw=1.6, op=0.8)


# ------------------------------------------------------------------ cups
def cup_drink(art, surface, small=False, extras=None, steam=True, seed=4, art_kw=None):
    if small:
        cup = FlutedCup(art, cx=585, rim_y=405, R0=138, H=165, k=0.54, saucer_scale=1.75, seed=seed)
    else:
        cup = FlutedCup(art, cx=565, rim_y=318, R0=205, H=240, k=0.56, seed=seed)
    kw = art_kw or {}
    cup.draw(lambda c, l: latte_surface(c, l, **kw) if surface == 'latte' else surface(c, l), steam=steam)
    if extras:
        extras(cup)
    return cup


def espresso_surface(cup, liq):
    a = cup.a
    cx, cy, rx, ry = cup.liq_ell
    d = shp_d(liq)
    a.wash(d, a.rad([(0, '#d29a5c'), (0.55, '#b06a32'), (0.85, '#7a3f1a'), (1, '#4e2a14')], cx=.48, cy=.45, r=.55), 0.95,
           disp=2, edge=3, rim=1.2, dark=0.6, bloom=0.5, gran=0.35)
    a.texture(d, '#6b3517', freq=0.06, a=3.0, b=-1.55, op=0.55, stretch=(1, 2.2))
    a.texture(d, '#f0c890', freq=0.09, a=3.0, b=-1.7, op=0.45)
    gl = ell_pts(cx - rx * 0.38, cy - ry * 0.5, rx * 0.26, ry * 0.12, 30, rot=-0.18)
    a.gouache(d_smooth(gl), '#fff4e2', 0.35, disp=2, blur=3)


def black_surface(cup, liq):
    a = cup.a
    cx, cy, rx, ry = cup.liq_ell
    d = shp_d(liq)
    a.wash(d, a.rad([(0, '#3c2416'), (0.8, '#24150d'), (1, '#4a2a14')], cx=.5, cy=.5, r=.55), 0.95, disp=2, edge=3, rim=1.1, dark=0.6)
    ring = ellipse_poly(cx, cy, rx, ry).difference(ellipse_poly(cx, cy + 2, rx * 0.86, ry * 0.8)).intersection(liq)
    a.wash(shp_d(ring), '#9a5a2a', 0.65, disp=4, edge=2, rim=1.0, bloom=0.7)
    a.texture(shp_d(ring), '#d9a066', freq=0.08, a=3, b=-1.6, op=0.6)
    rng = random.Random(3)
    bb = [(cx + rr * rx * math.cos(t), cy + rr * ry * math.sin(t), rng.uniform(1, 3)) for t, rr in
          [(rng.uniform(0, TAU), rng.uniform(0.82, 0.97)) for _ in range(40)]]
    a.dots(bb, 2, '#e8c8a0', 0.55, blend='normal', wash=False)
    gl = ell_pts(cx - rx * 0.35, cy - ry * 0.45, rx * 0.34, ry * 0.12, 30, rot=-0.15)
    a.gouache(d_smooth(gl), '#f7efe6', 0.45, disp=2, blur=3)
    gl2 = ell_pts(cx + rx * 0.2, cy + ry * 0.25, rx * 0.12, ry * 0.05, 20, rot=-0.15)
    a.gouache(d_smooth(gl2), '#f7efe6', 0.3, disp=1, blur=2)


def spoon(art, x, y, L=150, ang=0.35, k=0.55, gold=True):
    c, s = math.cos(ang), math.sin(ang)

    def T(px, py):
        return (x + px * c - py * s, y + (px * s + py * c) * k)
    bowl = Polygon([T(L * 0.12 * math.cos(t) * 1.4 - L * 0.0, L * 0.085 * math.sin(t)) for t in [i / 30 * TAU for i in range(30)]]).buffer(0)
    handle = LineString([T(L * 0.15, 0), T(L * 0.55, L * 0.01), T(L, L * 0.02)]).buffer(L * 0.022, cap_style=1)
    g = unary_union([bowl, handle])
    col = ('#f3dc8c', '#c99b3c', '#7a5718') if gold else ('#f3f3f3', '#b9bcc4', '#6a6d78')
    cast_shadow(art, x + L * 0.4 * c, y + 10, L * 0.55, L * 0.08, op=0.25, blur=6, dx=10, dy=6)
    paint_form(art, g, col[0], col[1], col[2], shade=0.5, hi_op=0.9, outline=0.4, hi_scale=0.2, contact=0)
    art.gouache(d_poly([T(L * 0.3, -L * 0.005), T(L * 0.9, L * 0.008)], closed=False), stroke='#fff8e0', sw=1.6, op=0.8)


def cinnamon_stick(art, x, y, L=170, ang=-0.15, r=13):
    c, s = math.cos(ang), math.sin(ang)
    body = LineString([(x, y), (x + L * c, y + L * s)]).buffer(r, cap_style=2)
    paint_form(art, body, '#c98250', '#97532a', '#5b2c12', shade=0.5, hi_op=0.5, outline=0.4, contact=0.2)
    art.pencil(d_poly([(x + 6 * c, y + 6 * s - r * 0.2), (x + (L - 6) * c, y + (L - 6) * s - r * 0.2)], closed=False), 1.0, color='#4a220c', op=0.5)
    end = ell_pts(x + L * c, y + L * s, r * 0.45, r, 30, rot=ang)
    art.wash(d_poly(end), '#b9774a', 0.9, disp=1, edge=1.5, rim=1.2)
    spiral = [(x + L * c + r * 0.6 * (j / 20) * math.cos(j * 0.9) * 0.45, y + L * s + r * 0.6 * (j / 20) * math.sin(j * 0.9)) for j in range(21)]
    art.pencil(d_smooth(spiral, closed=False), 0.9, color='#5b2c12', op=0.5)


def star_anise(art, x, y, r=34, rot=0.2, k=0.7):
    pods = []
    for i in range(8):
        a = rot + TAU * i / 8
        pts = [(x, y)]
        for j in range(9):
            b = a - 0.25 + 0.5 * j / 8
            rr = r * (0.55 + 0.45 * math.sin(math.pi * j / 8))
            pts.append((x + rr * math.cos(b), y + rr * math.sin(b) * k))
        pods.append(Polygon(pts).buffer(1.2, join_style=1))
    g = unary_union(pods)
    paint_form(art, g, '#b06b3c', '#7c3e1d', '#401c0a', shade=0.45, hi_op=0.4, outline=0.45, contact=0.2)
    sd = [(x + r * 0.45 * math.cos(rot + TAU * i / 8 + 0.0), y + r * 0.45 * math.sin(rot + TAU * i / 8) * k, 3.2) for i in range(0, 8, 2)]
    art.dots(sd, 3, '#d9a26a', 0.85, blend='normal', wash=False)


def scene_espresso(art):
    cup_drink(art, espresso_surface, small=True, extras=lambda c: spoon(art, 700, 600, 170, ang=0.18, k=0.5), steam=True)


def scene_long_black(art):
    cup_drink(art, black_surface, extras=lambda c: spoon(art, 690, 660, 190, ang=0.12, k=0.5))


def scene_latte(art):
    cup_drink(art, 'latte', art_kw=dict(art='rosetta'))


def scene_cappuccino(art):
    cup_drink(art, 'latte', art_kw=dict(art='foam', dust=('#5a3a26', 420, 0.62), base_in='#a46a3e'))


def scene_flat_white(art):
    cup_drink(art, 'latte', small=True, art_kw=dict(art='tulip', base_in='#a86d40'))


def scene_chai(art):
    def ex(c):
        cinnamon_stick(art, 640, 640, 170, ang=-0.08, r=12)
        star_anise(art, 805, 600, 30, rot=0.3, k=0.55)
    cup_drink(art, 'latte', extras=ex, art_kw=dict(art='heart', base_out='#8a5530', base_in='#c9935c', foam='#fbf2e2',
                                                     dust=('#8a4a22', 260, 0.75)))


def scene_matcha(art):
    cup_drink(art, 'latte', art_kw=dict(art='rosetta', base_out='#56742a', base_in='#9db84c', foam='#f8f6e8'))


def scene_choco(art):
    cup_drink(art, 'latte', art_kw=dict(art='heart', base_out='#33190f', base_in='#6b3a22', foam='#f3e4d0',
                                        dust=('#2d150b', 320, 0.85)))


def scene_tea_latte(art):
    cup_drink(art, 'latte', art_kw=dict(art='tulip', base_out='#8d5d36', base_in='#c39466', foam='#fbf3e6'))


# ------------------------------------------------------------------ teapot sets
def teapot_set(art, tea='#c48a3c', extra=None, face=None, cup_face=None):
    bamboo_tray(art, 600, 662, 400, 150, 0.34)
    pot = StripedPot(art, 500, 552, a=158, b=128, k=0.34)
    pot.draw(face=face)
    rev, sil = striped_cup(art, 836, 612, r=64, h=76, k=0.36, tea=tea, steam=True)
    if cup_face:
        cup_face(rev)
    if extra:
        extra()
    return pot


def scene_earl_grey(art):
    def petals():
        rng = random.Random(5)
        for i in range(6):
            x, y = 330 + rng.uniform(-40, 40), 700 + rng.uniform(-14, 14)
            p = Polygon(blob_pts(x, y, 9, 4, rot=rng.uniform(0, 3), amp=0.3, freq=(2, 5), seed=i, n=20)).buffer(0)
            art.wash(shp_d(p), '#3d63c2', 0.85, disp=1, edge=1, rim=1.2)
    teapot_set(art, tea='#b0612b', extra=petals)


def scene_peppermint(art):
    teapot_set(art, tea='#c9b55a', extra=lambda: mint_sprig(art, 300, 712, 0.75, ang=-0.15, seed=7, k=0.6))


# ------------------------------------------------------------------ iced
def scene_orange_long_black(art):
    tile_coaster(art, 600, 752, 175, 0.40, rot=0.10)
    rev = tumbler(600, 262, 0.36, 1.0)
    paint_glass(art, rev, liquid=[(0.15, '#3b2416'), (0.40, '#5a3518'), (0.53, '#d9822e'), (0.90, '#f0a33a')], ice=5,
                straw=((652, 640), (705, 140), 11), droplets=34, caustic='#f0a33a',
                garnish=lambda info: citrus_wheel(art, 548, 548, 66, 'orange', rot=0.2, sx=0.92, inside=True, tinted='#e08a2a'))


def scene_cranberry_long_black(art):
    round_coaster(art, 600, 742, 190, 0.40)
    rev = stemless(600, 400, 0.36, 1.05)
    paint_glass(art, rev, liquid=[(0.14, '#3a2014'), (0.36, '#52261a'), (0.52, '#a52235'), (0.92, '#c12f42')], ice=4,
                straw=((640, 620), (690, 250), 11), droplets=24, caustic='#c12f42', wall=6, inner_bottom=0.9)
    berries(art, [(560, 410, 13), (585, 430, 12), (625, 418, 13)], 'cranberry')


def scene_brown_sugar(art):
    tile_coaster(art, 600, 752, 175, 0.40, rot=-0.08, pal=('#2f58a8', '#4f8f74', '#e08a6a', '#f3efe4'))
    rev = tumbler(600, 262, 0.36, 1.0)

    def stripes(info):
        liq = info['liquid']
        rng = random.Random(6)
        st = []
        for i in range(9):
            th = -1.3 + 2.6 * i / 8 + rng.uniform(-0.08, 0.08)
            t0 = rng.uniform(0.18, 0.4)
            pts = [rev.pt(t0 + (0.88 - t0) * j / 14, th + 0.18 * math.sin(j * 0.6 + i), inset=8) for j in range(15)]
            st.append(LineString(pts).buffer(rng.uniform(5, 11), cap_style=1))
        g = unary_union(st).intersection(liq)
        art.wash(shp_d(g), '#6b3416', 0.75, disp=4, edge=2.5, rim=1.4, dark=0.55, bloom=0.6)
        art.soft_in(shp_d(liq), shp_d(rev.solid(0.72, 0.9, inset=6)), '#5a2a10', 0.75, blur=10, disp=12)
    paint_glass(art, rev, liquid=[(0.15, '#f4ece0'), (0.6, '#eadbc5'), (0.75, '#c99566'), (0.9, '#7a4220')], ice=5,
                straw=((652, 640), (705, 140), 11), droplets=30, caustic='#c99566', garnish=stripes)


def sparkling(art, colors, fruits, seed=1, coaster_col='#c7a7a0'):
    round_coaster(art, 600, 748, 200, 0.40, pattern=coaster_col)
    rev = mason(600, 300, 0.36, 1.08)

    def g(info):
        fruits(info, rev)
    paint_glass(art, rev, liquid=colors, ice=5, wall=7, bubbles=110, straw=((650, 640), (708, 150), 11), droplets=20,
                caustic=colors[-1][1], garnish=g, seed=seed)
    mason_threads(art, rev)


def scene_lemon_lime(art):
    def f(info, rev):
        citrus_wheel(art, 540, 560, 62, 'lemon', rot=0.3, sx=0.9, inside=True, tinted='#f3c9b8')
        citrus_wheel(art, 650, 610, 56, 'lime', rot=-0.2, sx=0.85, inside=True, tinted='#f3c9b8')
    sparkling(art, [(0.13, '#f9e7d7'), (0.5, '#f4d2c4'), (0.92, '#efb9a8')], f)
    citrus_side(art, 690, 300, 52, 9, 'lime', ang=0.25)


def scene_raspberry(art):
    def f(info, rev):
        citrus_wheel(art, 545, 540, 62, 'lemon', rot=0.3, sx=0.88, inside=True, tinted='#e86a84')
        berries(art, [(640, 600, 20), (560, 660, 18), (620, 700, 19)], 'raspberry')
    sparkling(art, [(0.13, '#fbe0e4'), (0.45, '#f39aac'), (0.92, '#d23a5b')], f)
    berries(art, [(560, 300, 19), (595, 318, 18)], 'raspberry')
    mint_sprig(art, 620, 300, 0.7, ang=-1.9, seed=11)


def scene_peach(art):
    def f(info, rev):
        citrus_wheel(art, 548, 545, 60, 'lemon', rot=0.3, sx=0.88, inside=True, tinted='#f6b07a')
        for i, (x, y) in enumerate([(640, 610), (575, 660)]):
            p = Polygon(blob_pts(x, y, 44, 22, rot=0.5 + i, amp=0.05, freq=(3,), seed=i)).buffer(0)
            art.wash(shp_d(p), art.lin([(0, '#f9d29a'), (0.7, '#f39a5b'), (1, '#d8583a')], 0, 0, 1, 1), 0.85, disp=1.2, edge=1.5, rim=1.2)
    sparkling(art, [(0.13, '#fdf0e2'), (0.45, '#f9cfa4'), (0.92, '#f39a5b')], f, coaster_col='#d9a77a')
    mint_sprig(art, 610, 300, 0.7, ang=-1.7, seed=12)


# ------------------------------------------------------------------ affogato & cones
def ice_cream_scoop(art, cx, cy, r, color=('#fffaf0', '#f4e9d2', '#c9b79a'), seed=0, specks=True):
    rng = random.Random(seed)
    pts = []
    for i in range(80):
        t = TAU * i / 80
        rr = r * (1 + 0.04 * math.sin(t * 7 + seed) + (0.07 * math.sin(t * 13) if math.sin(t) > 0.2 else 0))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t) * 0.88))
    g = Polygon(pts).buffer(0)
    paint_form(art, g, color[0], color[1], color[2], shade=0.45, hi_op=0.8, outline=0.35, contact=0.25)
    # scooped ridges
    rid = []
    for j in range(3):
        y = cy - r * 0.2 + j * r * 0.28
        arc = [(cx + r * 0.85 * math.cos(t), y + r * 0.2 * math.sin(t)) for t in [math.pi * (0.1 + 0.8 * q / 12) for q in range(13)]]
        rid.append(d_smooth(arc, closed=False))
    art.pencil(' '.join(rid), 0.9, color='#a08f78', op=0.35)
    if specks:
        sp = [(cx + rng.uniform(-r, r) * 0.7, cy + rng.uniform(-r, r) * 0.6, rng.uniform(0.6, 1.3)) for _ in range(30)]
        art.dots(sp, 1, '#3a2a1f', 0.6, wash=False)
    return g


def scene_affogato(art):
    cx = 600
    # foot + stem + bowl
    foot = ellipse_poly(cx, 742, 120, 120 * 0.36)
    cast_shadow(art, cx, 744, 130, 46, op=0.28, blur=14, dx=34, dy=8)
    art.occlude(shp_d(affinity.translate(foot, 0, 8).union(foot)))
    art.wash(shp_d(foot), art.lin([(0, '#f3f6f6'), (1, '#c9d4d8')], 0, 0, 1, 0), 0.45, disp=1, edge=2, rim=1.2)
    art.pencil(shp_d(foot), 1.0, color='#5f7480', op=0.45)
    stem = LineString([(cx, 600), (cx, 740)]).buffer(15, cap_style=2)
    art.occlude(shp_d(stem))
    art.wash(shp_d(stem), art.lin([(0, '#f4f7f7'), (0.6, '#d6e0e3'), (1, '#9fb0b7')], 0, 0, 1, 0), 0.5, disp=1, edge=1.5, rim=1.2)
    art.gouache(d_poly([(cx - 6, 610), (cx - 6, 728)], closed=False), stroke='#ffffff', sw=3, op=0.8)
    bowl = Revolve(cx, 380, 230, 0.38, smooth_profile([0, 0.3, 0.6, 0.85, 1.0], [150, 146, 122, 70, 18]))
    def g(info):
        # espresso pooled at the bottom of the bowl
        pool = bowl.solid(0.55, 0.93, inset=6)
        art.wash(shp_d(pool), art.lin([(0, '#7a3f1c'), (1, '#3c1d0e')], 0, 0, 0, 1), 0.92, disp=2, edge=3, rim=1.2)
        art.add(f'<path d="{shp_d(pool)}" fill="#ffffff" opacity="0.10"/>')
    paint_glass(art, bowl, liquid=None, ice=0, garnish=g, base_shadow=False, wall=6, inner_bottom=0.95)
    # scoop sitting in the bowl
    ice_cream_scoop(art, cx - 10, 380, 120, seed=2)
    # espresso poured over
    pour = [(cx + 30, 300), (cx + 10, 350), (cx - 30, 372), (cx - 70, 410), (cx - 60, 455)]
    art.stroke_wash(d_smooth(pour, closed=False), '#4a2412', 16, 0.9, disp=2, edge=2, rim=1.3)
    pour2 = [(cx + 40, 310), (cx + 70, 360), (cx + 90, 420)]
    art.stroke_wash(d_smooth(pour2, closed=False), '#5a2c14', 10, 0.85, disp=2, edge=2, rim=1.3)
    top = Polygon(blob_pts(cx + 15, 300, 70, 28, rot=-0.2, amp=0.25, freq=(3, 5), seed=4)).buffer(0)
    art.wash(shp_d(top), art.lin([(0, '#8a4a22'), (1, '#4a2412')], 0, 0, 1, 1), 0.9, disp=2, edge=2, rim=1.4)
    art.gouache(d_smooth(ell_pts(cx - 10, 292, 22, 6, 20, rot=-0.2)), '#ffffff', 0.6, disp=1, blur=1.5)
    # rim of the bowl in front of the scoop
    ex, ey, erx, ery = bowl.ell(0)
    front = ell_pts(ex, ey, erx, ery, 80, a0=0.02, a1=math.pi - 0.02)
    art.gouache(d_smooth(front, closed=False), stroke='#ffffff', sw=2.6, op=0.85)
    art.pencil(d_smooth(front, closed=False), 1.0, color='#5f7480', op=0.45)
    # wafer biscuit
    w = Polygon([(820, 640), (930, 610), (952, 650), (842, 682)]).buffer(4, join_style=1)
    paint_form(art, w, '#f2d29a', '#d8a75e', '#8f5c22', shade=0.4, outline=0.4)
    hl = [d_poly([(825 + i * 22, 650 - i * 6), (845 + i * 22, 678 - i * 6)], closed=False) for i in range(5)]
    art.pencil(' '.join(hl), 0.8, color='#8f5c22', op=0.5)


def popcorn(art, cx, cy, w, h, n=40, seed=3, clip=None):
    rng = random.Random(seed)
    for i in range(n):
        x = cx + rng.uniform(-w / 2, w / 2)
        y = cy + rng.uniform(-h / 2, h / 2) + i * 0.3
        parts = [Point(x + rng.uniform(-9, 9), y + rng.uniform(-7, 7)).buffer(rng.uniform(8, 13)) for _ in range(4)]
        g = unary_union(parts)
        if clip is not None:
            g = g.intersection(clip)
            if g.is_empty:
                continue
        paint_form(art, g, '#fffbe6', '#f3e1a6', '#c39a48', shade=0.4, hi_op=0.6, outline=0.3, contact=0.15, hi_scale=0.3)
        art.dots([(x + rng.uniform(-4, 4), y + rng.uniform(-3, 3), 2.2)], 2, '#d9a64a', 0.6, disp=0.6, edge=0.5)


def waffle_cone(art, cx, top_y, r=80, L=270, tilt=0.06, top='coffee'):
    k = 0.42
    tip = (cx + L * math.sin(tilt), top_y + L * math.cos(tilt))
    rim = ell_pts(cx, top_y, r, r * k, 80)
    body = Polygon(ell_pts(cx, top_y, r, r * k, 80, a0=0, a1=math.pi) + [tip]).buffer(0)
    body = unary_union([body, ellipse_poly(cx, top_y, r, r * k)])
    d = shp_d(body)
    art.occlude(d)
    art.wash(d, art.lin([(0, '#f0c27a'), (0.55, '#d9963f'), (1, '#9c5a1e')], 0, 0, 1, 0), 0.92, disp=1.5, edge=2.5, rim=1.3, gran=0.4)
    # lattice
    ls = []
    for i in range(-12, 13):
        ls.append(d_poly([(cx - r * 1.2 + i * 22, top_y - 10), (cx - r * 1.2 + i * 22 + L * 0.55, top_y + L)], closed=False))
        ls.append(d_poly([(cx + r * 1.2 + i * 22, top_y - 10), (cx + r * 1.2 + i * 22 - L * 0.55, top_y + L)], closed=False))
    cid = art.clip(d)
    art.add(f'<g clip-path="url(#{cid})">')
    art.stroke_wash(' '.join(ls), '#9a5a22', 3.4, 0.55, disp=1, edge=1, rim=1.0)
    art.gouache(' '.join(ls[::3]), stroke='#ffe2a8', sw=1.0, op=0.35)
    art.add('</g>')
    art.soft_in(d, shp_d(Polygon([(cx + r * 0.2, top_y), (cx + r * 1.3, top_y), tip]).buffer(0)), '#6a3a14', 0.35, blur=12, disp=6)
    # chocolate-dipped rim with drips
    drip = []
    for i in range(41):
        a = math.pi * i / 40
        x = cx + r * math.cos(a)
        dd = 26 + 10 * math.sin(i * 1.7) + (16 if i % 9 == 4 else 0)
        drip.append((x, top_y + r * k * math.sin(a) + dd))
    band = Polygon(ell_pts(cx, top_y, r + 2, r * k + 1, 80, a0=math.pi, a1=TAU) + drip[::-1]).buffer(0).intersection(body.buffer(2))
    band = unary_union([band, ellipse_poly(cx, top_y, r + 2, r * k + 1)])
    art.wash(shp_d(band), art.lin([(0, '#6b3a22'), (1, '#2e170c')], 0, 0, 1, 1), 0.95, disp=1.2, edge=2, rim=1.3, dark=0.6)
    art.gouache(d_smooth(ell_pts(cx - r * 0.3, top_y + r * k * 0.6 + 14, r * 0.35, 4, 20, rot=0.1)), '#ffffff', 0.5, disp=1, blur=1.2)
    # the drink on top
    if top == 'coffee':
        foam = Polygon(ell_pts(cx, top_y - 6, r * 0.9, r * k * 0.9, 60)).buffer(0)
        art.wash(shp_d(foam), art.rad([(0, '#f6ecdc'), (1, '#d9bf9c')], cx=.45, cy=.4, r=.6), 0.95, blend='normal', disp=1.5, edge=2, rim=0.8)
        art.texture(shp_d(foam), '#5a3520', freq=0.12, a=3, b=-1.4, op=0.85)
    else:
        foam = Polygon(ell_pts(cx, top_y - 6, r * 0.9, r * k * 0.9, 60)).buffer(0)
        art.wash(shp_d(foam), art.rad([(0, '#b9805a'), (1, '#6b3a22')], cx=.45, cy=.4, r=.6), 0.95, disp=1.5, edge=2, rim=1.0)
        drizzle(art, zigzag(cx - r * 0.7, top_y - 8, cx + r * 0.7, top_y - 4, n=4, amp=10, seed=3), '#3a1a0c', 3.5, 0.95)
        art.texture(shp_d(foam), '#2e170c', freq=0.12, a=3, b=-1.5, op=0.7)
    art.pencil(d, 1.0, color='#5e3112', op=0.4)
    return body


def scene_cone(art, top='coffee'):
    round_coaster(art, 600, 742, 230, 0.40, ground='#eef0ee', pattern='#a9c0c8')
    spoon(art, 700, 735, 150, ang=-0.1, k=0.5)
    rev = Revolve(600, 520, 200, 0.40, lambda t: 112 - 14 * t)
    paint_glass(art, rev, liquid=None, ice=0, base_shadow=True, wall=6, inner_bottom=0.9,
                garnish=lambda info: popcorn(art, 600, 620, 200, 170, n=26, seed=4, clip=info['inner']))
    waffle_cone(art, 590, 300, r=82, L=300, tilt=0.05, top=top)
    popcorn(art, 600, 520, 220, 40, n=14, seed=9)


def scene_coffee_cone(art):
    scene_cone(art, 'coffee')


def scene_baileys_cone(art):
    scene_cone(art, 'choco')


DRINKS = {
    'espresso': scene_espresso, 'long-black': scene_long_black, 'cappuccino': scene_cappuccino,
    'flat-white': scene_flat_white, 'latte': scene_latte, 'chai-latte': scene_chai, 'matcha-latte': scene_matcha,
    'choco-latte': scene_choco, 'black-tea-latte': scene_tea_latte, 'earl-grey': scene_earl_grey,
    'peppermint-tea': scene_peppermint, 'orange-long-black': scene_orange_long_black,
    'cranberry-long-black': scene_cranberry_long_black, 'brown-sugar-latte': scene_brown_sugar,
    'lemon-lime-bitters': scene_lemon_lime, 'raspberry-sparkling': scene_raspberry, 'peach-sparkling': scene_peach,
    'affogato': scene_affogato, 'coffee-cone': scene_coffee_cone, 'baileys-cone': scene_baileys_cone,
}
