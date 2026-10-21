"""Tableware of the shop, painted: fluted cream cup & saucer, blue-striped
teapot set, stoneware plates, glasses and jars."""
import math
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from shapely.ops import unary_union
from wc import *

# pigments (watercolour names, approximate hex)
SEPIA = '#5a4636'
UMBER = '#7b4d2e'
SIENNA = '#b8693a'
OCHRE = '#d4a24e'
PAYNE = '#4b5361'
VIOLET_GRAY = '#7f7a98'
INDIGO = '#2c4a86'
COBALT = '#3b67b5'
CREAM = '#efe4cf'
WARM_GRAY = '#b9ab97'


def ellipse_poly(cx, cy, rx, ry, n=96, rot=0.0):
    return Polygon(ell_pts(cx, cy, rx, ry, n, rot=rot))


def union_of_ellipses(sections, n=96):
    """sections: list of (cx, cy, rx, ry) -> silhouette polygon."""
    return unary_union([ellipse_poly(*s, n=n) for s in sections]).buffer(0)


def cast_shadow(art, cx, cy, rx, ry, op=0.32, blur=16, color=VIOLET_GRAY, dx=26, dy=14):
    art.shadow(cx + dx, cy + dy, rx, ry, color=color, op=op, blur=blur)


# =================================================================== cup
class FlutedCup:
    """The shop's cream fluted cup on its scalloped saucer (seen in the photos)."""

    def __init__(self, art, cx=560, rim_y=400, R0=200, H=210, k=0.30, small=False, saucer=True,
                 handle=True, flute_from=0.30, seed=3, saucer_scale=1.52):
        self.a = art
        self.cx, self.rim_y, self.R0, self.H, self.k = cx, rim_y, R0, H, k
        self.small = small
        self.saucer_on = saucer
        self.handle_on = handle
        self.flute_from = flute_from
        self.saucer_scale = saucer_scale
        self.rng = random.Random(seed)

    # profile
    def R(self, t):
        t = min(max(t, 0.0), 1.0)
        return self.R0 * (0.47 + 0.53 * math.cos(t * math.pi / 2) ** 0.82)

    def yc(self, t):
        return self.rim_y + self.H * t

    def pt(self, t, th):
        """surface point at height t, angle th (0 = front centre, +pi/2 = right)."""
        r = self.R(t)
        return (self.cx + r * math.sin(th), self.yc(t) + self.k * r * math.cos(th))

    def silhouette(self):
        secs = [(self.cx, self.yc(t), self.R(t), self.k * self.R(t)) for t in [i / 40 for i in range(41)]]
        rf = self.R(1.0)
        secs.append((self.cx, self.yc(1.0) + 10, rf * 0.97, self.k * rf * 0.97))
        return union_of_ellipses(secs)

    # ------------------------------------------------------------ saucer
    def draw_saucer(self):
        a = self.a
        k = self.k
        cx = self.cx + 14
        cy = self.yc(1.0) + 10 + 8 * (k / 0.3)
        rx = self.R0 * self.saucer_scale
        ry = rx * k
        self.saucer_geom = (cx, cy, rx, ry)
        th_px = 12 + 4 * (0.5 - min(k, 0.5))
        cast_shadow(a, cx, cy + th_px, rx * 1.0, ry * 1.04, op=0.28, blur=16, dx=30, dy=12 + 10 * k)
        pts = []
        n = 240
        for i in range(n):
            th = TAU * i / n
            m = 1 + 0.008 * math.cos(44 * th)
            pts.append((cx + rx * m * math.cos(th), cy + ry * m * math.sin(th)))
        top = Polygon(pts)
        side = affinity.translate(top, 0, th_px)
        body = unary_union([top, side])
        a.occlude(shp_d(body))
        # thickness band (front)
        a.wash(shp_d(body.difference(top)), a.lin([(0, '#cfc2ac'), (0.5, '#bfb19b'), (1, '#c9bca8')], 0, 0, 1, 0), 0.6,
               disp=2, edge=2, rim=1.1, bloom=0.3, gran=0.2)
        # top surface: nearly white, cool shade toward the back, warm toward the front
        a.wash(shp_d(top), a.lin([(0, '#e6e0d6'), (0.45, '#f4eee3'), (1, '#efe4d0')], 0, 0, 0, 1), 0.55,
               disp=3, edge=3.5, rim=1.0, dark=0.82, bloom=0.4, gran=0.15)
        a.wash(shp_d(top), a.lin([(0, '#ffffff', 0), (0.62, '#cfc4b3', 0), (1, '#b9ad9c', 0.6)], 0, 0, 1, 0.3), 0.45,
               disp=3, edge=3, rim=0.8, bloom=0.4)
        # radial flutes on the rim band
        inner_rx, inner_ry = rx * 0.55, ry * 0.55
        wcx, wcy = cx - 6, cy - 4 * (k / 0.3)
        dark, light = [], []
        nf = 60
        for i in range(nf):
            th = TAU * i / nf + 0.03
            x0, y0 = wcx + inner_rx * 1.12 * math.cos(th), wcy + inner_ry * 1.12 * math.sin(th)
            x1, y1 = cx + rx * 0.965 * math.cos(th), cy + ry * 0.965 * math.sin(th)
            mid = ((x0 + x1) / 2, (y0 + y1) / 2 + 1.5)
            seg = d_smooth([(x0, y0), mid, (x1, y1)], closed=False)
            (dark if i % 2 == 0 else light).append(seg)
        a.stroke_wash(' '.join(dark), '#cdbfa9', 2.4, 0.36, disp=1.8, edge=1.0, rim=0.8, bloom=0.4, gran=0.25)
        a.gouache(' '.join(light), stroke='#fffaf2', sw=1.6, op=0.45, blur=0.5)
        # inner well (concave: left slope in shade)
        well = ellipse_poly(wcx, wcy, inner_rx, inner_ry)
        a.wash(shp_d(well), a.lin([(0, '#d9cfbf'), (0.55, '#ece4d6'), (1, '#f3ede2')], 0, 0, 1, 0), 0.55,
               disp=2.5, edge=3, rim=1.0, dark=0.75)
        a.pencil(d_smooth(ell_pts(wcx, wcy, inner_rx, inner_ry, 90, a0=0.25, a1=math.pi - 0.2), closed=False), 0.9, op=0.28)
        # rim edges
        front = [(cx + rx * math.cos(th), cy + th_px + ry * math.sin(th)) for th in [i / 60 * math.pi for i in range(61)]]
        a.pencil(d_smooth(front, closed=False), 1.2, op=0.42)
        a.pencil(d_smooth(ell_pts(cx, cy, rx, ry, 120), closed=True), 1.0, op=0.32, dash='170 26 70 14')
        hi = ell_pts(cx, cy, rx * 0.985, ry * 0.96, 50, a0=math.pi * 1.06, a1=math.pi * 1.55)
        a.gouache(d_smooth(hi, closed=False), stroke='#fffdf8', sw=3.0, op=0.85)
        # the cup's own shadow falling on the saucer (light from upper left)
        rf = self.R(1.0)
        a.soft(d_poly(ell_pts(cx + rf * 0.55, wcy + 4, rf * 1.45, rf * 1.45 * k * 1.1, 60)), VIOLET_GRAY, 0.34, blur=12, disp=10)

    # ------------------------------------------------------------ cup body
    def draw_body(self):
        a = self.a
        sil = self.silhouette()
        self.sil = sil
        d = shp_d(sil)
        a.occlude(d)
        # glaze: warm cream, barely there on the lit side
        a.wash(d, a.lin([(0, '#f6efe2'), (0.5, '#f0e5d1'), (1, '#e8dcc6')], 0, 0, 1, 0), 0.7,
               disp=2.5, edge=3.5, rim=1.0, dark=0.8, bloom=0.45, gran=0.15)
        # form shadow: soft band from the middle to the right, with core shadow and reflected light
        a.wash(d, a.lin([(0, '#ffffff', 0), (0.48, '#d6c9b4', 0), (0.70, '#bfb09a', 0.55), (0.86, '#a39788', 0.8),
                         (1, '#b9ae9f', 0.55)], 0, 0, 1, 0), 0.62, disp=3.5, edge=4, rim=0.9, bloom=0.5, gran=0.25)
        # cooler shade low under the belly
        a.wash(d, a.lin([(0, '#ffffff', 0), (0.5, '#c4bdb4', 0), (1, '#9b97a3', 0.7)], 0, 0, 0, 1), 0.42,
               disp=3.5, edge=3, rim=0.7, bloom=0.5, gran=0.2)
        # painted shadow shape with a soft-hard terminator (violet grey + warm reflected light)
        term = [self.pt(t, 0.42 - 0.12 * t) for t in [j / 30 for j in range(31)]]
        far = [(self.cx + self.R0 * 1.4, self.yc(1.0) + 80), (self.cx + self.R0 * 1.4, self.rim_y - 80)]
        region = Polygon(term + far).buffer(0).intersection(sil)
        if not region.is_empty:
            a.wash(shp_d(region), a.lin([(0, '#a39bae', 0), (0.30, '#a39bae', 0.45), (0.72, '#9c9186', 0.85), (1, '#c8b9a2', 0.5)], 0, 0, 1, 0), 0.40,
                   disp=5, edge=5, rim=1.4, dark=0.62, bloom=0.6, gran=0.35)
        self.draw_flutes()
        pts = []
        for _ in range(45):
            t = self.rng.uniform(0.06, 0.97)
            th = self.rng.uniform(-1.35, 1.35)
            x, y = self.pt(t, th)
            pts.append((x, y, self.rng.uniform(0.6, 1.3)))
        a.dots(pts, 1, '#7a5d46', 0.45)
        ext = list(sil.exterior.coords)[:-1]
        a.pencil(d_smooth(ext[::2], closed=True), 1.2, op=0.40, dash='240 16 90 12 150 22')

    def draw_flutes(self):
        a = self.a
        n = 26
        t0, t1 = self.flute_from, 0.99
        shade, deep, hi = [], [], []
        for i in range(n):
            th = -math.pi + TAU * (i + 0.5) / n
            if abs(th) > math.pi / 2 * 0.97:
                continue
            ts = [t0 + (t1 - t0) * j / 24 for j in range(25)]
            line = [self.pt(t, th) for t in ts]
            light = -math.sin(th)
            dd = d_smooth(line, closed=False)
            if light < 0.55:
                shade.append((dd, light))
        for dd, light in shade:
            op = 0.05 + 0.15 * (1 - light) / 2
            a.stroke_wash(dd, '#a6977f', 5.5, op, disp=2.6, edge=2.0, rim=1.0, bloom=0.5, gran=0.3)
        for i in range(n):
            th = -math.pi + TAU * i / n
            if abs(th) > math.pi / 2 * 0.93:
                continue
            light = -math.sin(th)
            ts = [t0 + 0.05 + (t1 - t0 - 0.10) * j / 20 for j in range(21)]
            dd = d_smooth([self.pt(t, th) for t in ts], closed=False)
            if light > 0.0:
                hi.append(dd)
        a.gouache(' '.join(hi), stroke='#fffdf7', sw=1.5, op=0.55, blur=0.8)
        # fine pencil grooves, only some of them
        sel = []
        for i in range(n):
            th = -math.pi + TAU * (i + 0.5) / n
            if abs(th) > math.pi / 2 * 0.95 or self.rng.random() < 0.45:
                continue
            ts = [t0 + 0.08 + (t1 - t0 - 0.2) * j / 14 for j in range(15)]
            sel.append(d_smooth([self.pt(t, th) for t in ts], closed=False))
        a.pencil(' '.join(sel), 0.8, op=0.22)

    # ------------------------------------------------------------ handle
    def draw_handle(self):
        a = self.a
        A = self.pt(0.10, math.pi / 2 * 0.97)
        B = self.pt(0.58, math.pi / 2 * 0.97)
        A = (A[0] - 8, A[1] + 2)
        B = (B[0] - 12, B[1])
        c1 = (A[0] + 118, A[1] - 22)
        c2 = (B[0] + 112, B[1] + 20)
        pts = []
        for i in range(41):
            t = i / 40
            x = (1 - t) ** 3 * A[0] + 3 * (1 - t) ** 2 * t * c1[0] + 3 * (1 - t) * t * t * c2[0] + t ** 3 * B[0]
            y = (1 - t) ** 3 * A[1] + 3 * (1 - t) ** 2 * t * c1[1] + 3 * (1 - t) * t * t * c2[1] + t ** 3 * B[1]
            pts.append((x, y))
        L = LineString(pts)
        band = L.buffer(13, cap_style=1)
        a.occlude(shp_d(band))
        a.wash(shp_d(band), a.lin([(0, '#f1e8d7'), (1, '#d9ccb6')], 0, 0, 1, 1), 0.75, disp=2.5, edge=3, rim=1.0, dark=0.78)
        sh = LineString([(x + 4, y + 6) for x, y in pts[8:]]).buffer(6.5, cap_style=1).intersection(band)
        a.wash(shp_d(sh), '#a99b88', 0.5, disp=2.5, edge=2, rim=0.8)
        hi = [(x - 4, y - 6) for x, y in pts[3:24]]
        a.gouache(d_smooth(hi, closed=False), stroke='#fffdf7', sw=3.4, op=0.85)
        for off in (13, -13):
            o = L.parallel_offset(off, 'left' if off > 0 else 'right', join_style=1)
            if o.geom_type == 'LineString':
                a.pencil(d_smooth(list(o.coords)[::2], closed=False), 1.1, op=0.4)

    # ------------------------------------------------------------ opening + drink
    def opening(self):
        r = self.R(0.0)
        return (self.cx, self.rim_y, r, self.k * r)

    def liquid(self, depth=0.07):
        r = self.R(depth) * 0.985
        return (self.cx, self.yc(depth), r, self.k * r)

    def draw_opening(self, liquid_depth=0.07):
        a = self.a
        cx, cy, rx, ry = self.opening()
        rim = ellipse_poly(cx, cy, rx, ry)
        lip_w = 7 if not self.small else 5
        inner = ellipse_poly(cx, cy + 1, rx - lip_w, ry - lip_w * self.k)
        a.occlude(shp_d(rim))
        a.wash(shp_d(inner), a.lin([(0, '#d3c6b1'), (0.45, '#ebe2d2'), (1, '#f6f0e4')], 0, 0, 1, 0), 0.75,
               disp=2, edge=2.5, rim=0.9, dark=0.8)
        lq = self.liquid(liquid_depth)
        liq = ellipse_poly(*lq).intersection(inner)
        self.liq_poly = liq
        self.liq_ell = lq
        lip = rim.difference(inner)
        a.wash(shp_d(lip), a.lin([(0, '#f2eadc'), (1, '#ded2bf')], 0, 0, 1, 0), 0.6, disp=1.2, edge=1.2, rim=0.6)
        top_arc = ell_pts(cx, cy - 0.5, rx - lip_w / 2, ry - lip_w * self.k / 2, 80, a0=math.pi * 1.04, a1=math.pi * 1.9)
        a.gouache(d_smooth(top_arc, closed=False), stroke='#fffdf8', sw=2.8, op=0.95)
        front_arc = ell_pts(cx, cy + 0.5, rx - lip_w / 2, ry - lip_w * self.k / 2, 80, a0=0.15, a1=math.pi - 0.6)
        a.gouache(d_smooth(front_arc, closed=False), stroke='#fffaf0', sw=2.2, op=0.75)
        a.pencil(d_smooth(ell_pts(cx, cy, rx, ry, 120), closed=True), 1.15, op=0.45, dash='300 16 120 10')
        a.pencil(d_smooth(ell_pts(cx, cy + 1, rx - lip_w, ry - lip_w * self.k, 100, a0=math.pi * 1.05, a1=TAU * 0.98), closed=False), 0.8, op=0.28)
        return liq

    def steam(self, n=2, op=0.30):
        a = self.a
        cx, cy, rx, ry = self.opening()
        for i in range(n):
            x0 = cx + (i - (n - 1) / 2) * rx * 0.32 + self.rng.uniform(-10, 10)
            pts = []
            for j in range(9):
                y = cy - 30 - j * 22
                x = x0 + 16 * math.sin(j * 0.9 + i * 1.7) + j * 2
                pts.append((x, y))
            a.soft(LineString(pts).buffer(9 - 2 * i, cap_style=1).simplify(0.5).exterior and shp_d(LineString(pts).buffer(9 - 2 * i, cap_style=1)), '#c9c3d2', op * (1 - 0.2 * i), blur=5, disp=10)

    def draw(self, drink_fn=None, liquid_depth=0.07, steam=False):
        if self.saucer_on:
            self.draw_saucer()
        if self.handle_on:
            self.draw_handle()
        self.draw_body()
        liq = self.draw_opening(liquid_depth)
        if drink_fn:
            drink_fn(self, liq)
        if steam:
            self.steam()
        return liq


# =================================================================== drinks in cups
def rosetta_geom(rng, n_layers=9):
    """Top-down rosetta in the unit circle (y toward the viewer): white layers with thin crema gaps."""
    right = [(0.0, -0.60), (0.22, -0.70), (0.50, -0.66), (0.70, -0.50), (0.77, -0.30), (0.72, -0.08),
             (0.60, 0.14), (0.44, 0.36), (0.27, 0.56), (0.12, 0.73), (0.0, 0.86)]
    left = [(-x, y) for x, y in right[1:-1][::-1]]
    outline = right + left
    sil = Polygon([(x, y) for x, y in _catmull(outline, 10)]).buffer(0)
    layers = []
    ys = [lerp(-0.98, 0.42, i / n_layers) for i in range(n_layers + 1)]
    for i in range(n_layers):
        f = i / (n_layers - 1)
        sag0 = lerp(0.50, 0.28, i / n_layers)
        sag1 = lerp(0.50, 0.28, (i + 1) / n_layers)
        prof = lambda u: (1 - abs(u) ** 1.3) - 0.32 * u ** 4
        g = 0.028 + 0.006 * f
        top = [(u, ys[i] + sag0 * prof(u) + g / 2) for u in [-1.2 + 2.4 * j / 60 for j in range(61)]]
        bot = [(u, ys[i + 1] + sag1 * prof(u) - g / 2) for u in [1.2 - 2.4 * j / 60 for j in range(61)]]
        if i == 0:
            top = [(u, -1.2) for u in [-1.2, 1.2]]
        if i == n_layers - 1:
            bot = [(u, 1.2) for u in [1.2, -1.2]]
        band = Polygon(top + bot).buffer(0)
        piece = sil.intersection(band)
        piece = piece.buffer(0.03, join_style=1).buffer(-0.055, join_style=1).buffer(0.025, join_style=1)
        if not piece.is_empty:
            layers.append(piece)
    foam = unary_union(layers)
    # pulled line through the middle
    stem = LineString([(0.0, -0.64), (0.004, 0.0), (0.0, 0.88)]).buffer(0.018, cap_style=1)
    foam = foam.difference(stem)
    tail = LineString([(0.0, 0.84), (0.0, 0.93)]).buffer(0.012, cap_style=1)
    foam = unary_union([foam, tail])
    return foam


def _catmull(pts, seg=8):
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        for s in range(seg):
            t = s / seg
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


def latte_surface(cup, liq, base_out='#6a3a1d', base_in='#b07445', art='rosetta', foam='#fbf5ea',
                  rot=-0.07, dust=None, seed=5, scale=1.0, tone='coffee'):
    """Crema + foam art on the liquid surface of a cup."""
    a = cup.a
    rng = random.Random(seed)
    cx, cy, rx, ry = cup.liq_ell
    d = shp_d(liq)
    a.wash(d, a.rad([(0, base_in), (0.62, mix(base_in, base_out, 0.45)), (1, base_out)], cx=.5, cy=.5, r=.55), 0.95,
           disp=2, edge=3.5, rim=1.0, dark=0.6, bloom=0.4, gran=0.3)
    # crema mottling
    mot = []
    for _ in range(90):
        u, v = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if u * u + v * v > 0.95:
            continue
        mot.append((cx + u * rx * 0.97, cy + v * ry * 0.97, rng.uniform(2, 7)))
    a.dots(mot, 3, mix(base_in, '#e2b07a', 0.3), 0.18, wash=True, disp=3, edge=1.5)
    ring = ellipse_poly(cx, cy, rx, ry).difference(ellipse_poly(cx, cy, rx * 0.9, ry * 0.86)).intersection(liq)
    a.wash(shp_d(ring), base_out, 0.35, disp=3, edge=3, rim=1.2, bloom=0.5)
    gl = ell_pts(cx - rx * 0.42, cy - ry * 0.55, rx * 0.30, ry * 0.10, 30, rot=-0.18)
    a.gouache(d_smooth(gl), '#fff8ec', 0.28, disp=3, blur=4)

    def M(u, v):
        c, s = math.cos(rot), math.sin(rot)
        uu, vv = u * c - v * s, u * s + v * c
        return (cx + uu * rx * 0.94 * scale, cy + vv * ry * 0.94 * scale)

    shapes = []
    if art == 'rosetta':
        foam_geom = rosetta_geom(rng)
        def to_d(g):
            out = []
            for p in (g.geoms if hasattr(g, 'geoms') else [g]):
                if p.is_empty:
                    continue
                out.append(d_smooth([M(x, y) for x, y in list(p.exterior.coords)[:-1]], closed=True))
            return ' '.join(out)
        foam_d = to_d(foam_geom)
        a.soft(foam_d, '#d2a477', 0.5, blur=2.6, disp=2.5)
        a.gouache(foam_d, foam, 0.97, disp=1.2, blur=0.55)
        # faint milky veil between the layers
        a.gouache(to_d(foam_geom.convex_hull.buffer(-0.04)), '#f3e3cc', 0.18, disp=2, blur=3)
    elif art == 'heart':
        hp = []
        for j in range(60):
            t = TAU * j / 60
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            hp.append(M(x / 26, y / 26 + 0.05))
        hd = d_smooth(hp)
        ring = [M(0.62 * math.cos(t), 0.62 * math.sin(t)) for t in [i / 48 * TAU for i in range(48)]]
        a.gouache(d_smooth(ring), foam, 0.35, disp=4, blur=3)
        a.gouache(hd, foam, 0.94, disp=1.8, blur=0.8)
        stem = [M(0.0, lerp(-0.38, 0.48, j / 12)) for j in range(13)]
        a.stroke_wash(d_smooth(stem, closed=False), mix(base_out, base_in, 0.6), 2.2, 0.5, disp=1, edge=0.8, rim=0.4)
    elif art == 'tulip':
        for i, (v, w) in enumerate([(0.45, 0.52), (0.12, 0.42), (-0.18, 0.32)]):
            pts = []
            for j in range(40):
                t = TAU * j / 40
                x = w * math.sin(t)
                y = v - 0.22 * w * math.cos(t) - (0.12 * w if math.cos(t) < 0 else 0) * (1 - abs(math.sin(t)))
                pts.append(M(x, y))
            a.gouache(d_smooth(pts), foam, 0.93, disp=1.8, blur=0.8)
        stem = [M(0.0, lerp(-0.3, 0.75, j / 12)) for j in range(13)]
        a.stroke_wash(d_smooth(stem, closed=False), mix(base_out, base_in, 0.5), 2.6, 0.6, disp=1, edge=0.8, rim=0.4)
    elif art == 'foam':
        cap = [M(0.88 * math.cos(t), 0.88 * math.sin(t)) for t in [i / 60 * TAU for i in range(60)]]
        a.gouache(d_smooth(cap), foam, 0.92, disp=3, blur=2.2)
        # small bubbles
        bub = []
        for _ in range(70):
            u, v = rng.uniform(-0.85, 0.85), rng.uniform(-0.85, 0.85)
            if u * u + v * v < 0.7:
                x, y = M(u, v)
                bub.append((x, y, rng.uniform(1.2, 3.2)))
        a.dots(bub, 2, '#d8c3a5', 0.35, disp=0.8, edge=0.6)
    if dust:
        col, amt, rr = dust
        pts = []
        for _ in range(amt):
            ang, rad_ = rng.uniform(0, TAU), rr * math.sqrt(rng.random())
            x, y = M(rad_ * math.cos(ang), rad_ * math.sin(ang))
            pts.append((x, y, rng.uniform(0.5, 1.6)))
        a.dots(pts, 1, col, 0.55, disp=0.8, edge=0.5)
    # bubbles at the rim of the drink
    rimb = []
    for _ in range(40):
        t = rng.uniform(0, TAU)
        rr = rng.uniform(0.9, 0.99)
        rimb.append((cx + rr * rx * math.cos(t), cy + rr * ry * math.sin(t), rng.uniform(1, 2.6)))
    a.dots(rimb, 2, '#f3e6d0', 0.6, blend='normal', disp=0.6, edge=0.5)
