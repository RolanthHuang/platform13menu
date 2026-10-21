"""Reusable painted parts: vessels of revolution, glasses, jars, coasters,
plates, boards, the striped teapot set, leaves, citrus, berries, ice."""
from ware import *


# =================================================================== geometry of revolution
class Revolve:
    """A vessel described by its radius profile R(t), t = 0 (rim) .. 1 (base)."""

    def __init__(self, cx, top_y, H, k, Rf):
        self.cx, self.top_y, self.H, self.k, self.Rf = cx, top_y, H, k, Rf

    def R(self, t):
        return self.Rf(min(max(t, 0.0), 1.0))

    def yc(self, t):
        return self.top_y + self.H * t

    def pt(self, t, th, inset=0.0):
        r = self.R(t) - inset
        return (self.cx + r * math.sin(th), self.yc(t) + self.k * r * math.cos(th))

    def ell(self, t, inset=0.0, scale=1.0):
        r = (self.R(t) - inset) * scale
        return (self.cx, self.yc(t), r, self.k * r)

    def solid(self, t0=0.0, t1=1.0, inset=0.0, n=40):
        secs = [self.ell(t0 + (t1 - t0) * i / n, inset) for i in range(n + 1)]
        return union_of_ellipses(secs)

    def line(self, th, t0=0.0, t1=1.0, n=24, inset=0.0):
        return [self.pt(t0 + (t1 - t0) * i / n, th, inset) for i in range(n + 1)]


def poly_d(geom):
    return shp_d(geom)


# =================================================================== small organic things
def leaf_poly(cx, cy, L, W, ang, teeth=0, tooth=0.07, k=1.0, curve=0.0, seed=0, tipw=1.0):
    """Leaf outline (local x along the blade). curve bends the midrib."""
    rng = random.Random(seed)
    pts_r, pts_l = [], []
    n = 40
    for i in range(n + 1):
        s = i / n
        w = W * (math.sin(math.pi * s) ** 0.85) * (1 - 0.25 * s) * (1 if s < 0.6 else tipw ** (s - 0.6))
        if teeth:
            w *= 1 + tooth * abs(math.sin(s * math.pi * teeth))
        y_mid = curve * L * (s - 0.5) ** 2 - curve * L * 0.25
        x = s * L
        pts_r.append((x, y_mid + w * 0.5))
        pts_l.append((x, y_mid - w * 0.5))
    pts = pts_r + pts_l[::-1]
    c, sn = math.cos(ang), math.sin(ang)
    out = [(cx + x * c - y * sn, cy + (x * sn + y * c) * k) for x, y in pts]
    mid = [(cx + x * c - (curve * L * (x / L - 0.5) ** 2 - curve * L * 0.25) * sn,
            cy + (x * sn + (curve * L * (x / L - 0.5) ** 2 - curve * L * 0.25) * c) * k) for x in [L * j / 20 for j in range(21)]]
    return out, mid


def paint_leaf(art, cx, cy, L, W, ang, light='#a9c95f', dark='#4d7f34', teeth=14, k=1.0, curve=0.08,
               veins=True, seed=0, op=0.95, occl=True, vein_color=None):
    pts, mid = leaf_poly(cx, cy, L, W, ang, teeth=teeth, k=k, curve=curve, seed=seed)
    d = d_smooth(pts[::1], closed=True, t=0.35) if not teeth else d_poly(pts)
    if occl:
        art.occlude(d)
    art.wash(d, art.lin([(0, light), (0.55, mix(light, dark, 0.4)), (1, dark)], 0, 0, 1, 1), op,
             disp=2.0, edge=2.2, rim=1.3, dark=0.6, bloom=0.5, gran=0.25)
    # shade one half of the blade
    half = Polygon(pts[: len(pts) // 2] + mid[::-1]).buffer(0)
    if not half.is_empty:
        art.wash(shp_d(half), dark, 0.22, disp=1.5, edge=1.5, rim=0.8)
    if veins:
        art.gouache(d_smooth(mid[1:-2], closed=False), stroke=vein_color or mix(light, '#ffffff', 0.45), sw=1.6, op=0.7)
        sv = []
        for j in range(3, 18, 3):
            x0, y0 = mid[j]
            # side veins toward both edges
            for sgn in (1, -1):
                ang2 = ang + sgn * 0.85
                L2 = W * 0.42 * (1 - abs(j - 9) / 14)
                x1 = x0 + math.cos(ang2) * L2
                y1 = y0 + math.sin(ang2) * L2 * k
                sv.append(f'M{x0:.1f},{y0:.1f} Q{(x0 + x1) / 2 + math.cos(ang) * 4:.1f},{(y0 + y1) / 2 + math.sin(ang) * 4 * k:.1f} {x1:.1f},{y1:.1f}')
        art.pencil(' '.join(sv), 0.9, color=dark, op=0.5, disp=1.0)
    art.pencil(d, 0.9, color=mix(dark, '#2b3a22', 0.4), op=0.35, disp=1.2)
    return Polygon(pts).buffer(0)


def mint_sprig(art, x, y, scale=1.0, ang=-1.2, seed=1, k=1.0, n=5):
    rng = random.Random(seed)
    # stem
    stem = [(x, y)]
    for i in range(1, 6):
        stem.append((x + math.cos(ang) * 22 * i * scale + rng.uniform(-2, 2), y + math.sin(ang) * 22 * i * scale))
    art.stroke_wash(d_smooth(stem, closed=False), '#6f8f3c', 3.2 * scale, 0.8, disp=1, edge=1, rim=0.6)
    polys = []
    for i in range(n):
        f = i / max(n - 1, 1)
        px, py = stem[min(1 + int(f * 4), 5)]
        side = 1 if i % 2 == 0 else -1
        La = (70 - 30 * f) * scale
        Wa = (44 - 18 * f) * scale
        a2 = ang + side * (0.9 - 0.4 * f) + rng.uniform(-0.15, 0.15)
        polys.append(paint_leaf(art, px, py, La, Wa, a2, light='#b5d36b', dark='#3f7a32', teeth=12, k=k,
                                curve=0.1 * side, seed=seed + i))
    return unary_union(polys)


def citrus_wheel(art, cx, cy, r, kind='orange', rot=0.0, sx=1.0, sy=1.0, op=0.95, seed=2, tinted=None, inside=False):
    pal = {
        'orange': ('#e9862a', '#f8f0dc', '#f4a33d', '#f9c46a'),
        'lemon': ('#efcb37', '#fbf6df', '#f4dc63', '#f9ea98'),
        'lime': ('#5f9233', '#eef3d8', '#b7cf5a', '#d6e48c'),
        'peach': ('#e98a4f', '#fbe2c4', '#f4ae6d', '#f8cc95'),
    }[kind]
    rind, pith, flesh, flesh_hi = pal
    rng = random.Random(seed)

    def T(px, py):
        x, y = px * sx, py * sy
        c, s = math.cos(rot), math.sin(rot)
        return (cx + x * c - y * s, cy + x * s + y * c)
    outer = [T(r * math.cos(t), r * math.sin(t)) for t in [i / 72 * TAU for i in range(72)]]
    if not inside:
        art.occlude(d_poly(outer))
    else:
        art.add(f'<path d="{d_poly(outer)}" fill="#ffffff" opacity="0.35"/>')
    art.wash(d_poly(outer), rind, op, disp=1.5, edge=2, rim=1.2, dark=0.7)
    pr = r * 0.88
    art.wash(d_poly([T(pr * math.cos(t), pr * math.sin(t)) for t in [i / 72 * TAU for i in range(72)]]), pith, 0.9,
             blend='normal', disp=1, edge=1, rim=0.3)
    nseg = 10
    segs = []
    for i in range(nseg):
        a0 = TAU * i / nseg + 0.06
        a1 = TAU * (i + 1) / nseg - 0.06
        pts = [T(r * 0.10 * math.cos((a0 + a1) / 2), r * 0.10 * math.sin((a0 + a1) / 2))]
        for j in range(9):
            a = a0 + (a1 - a0) * j / 8
            rr = r * 0.80 * (1 - 0.04 * math.sin(j / 8 * math.pi))
            pts.append(T(rr * math.cos(a), rr * math.sin(a)))
        segs.append(d_smooth(pts, closed=True, t=0.4))
    sd = ' '.join(segs)
    art.wash(sd, art.rad([(0, flesh_hi), (1, flesh)], cx=.5, cy=.5, r=.6), op, disp=1.2, edge=1.6, rim=1.1, dark=0.75, bloom=0.4, gran=0.3)
    # vesicles
    ves = []
    for _ in range(80):
        a = rng.uniform(0, TAU)
        rr = r * rng.uniform(0.15, 0.78)
        x, y = T(rr * math.cos(a), rr * math.sin(a))
        ves.append((x, y, rng.uniform(0.6, 1.4) * r / 40))
    art.dots(ves, 1, mix(flesh, '#ffffff', 0.5), 0.6, blend='normal', disp=0.5, edge=0.4)
    if tinted:
        art.wash(d_poly(outer), tinted, 0.30, disp=1, edge=1)
    if inside:
        art.add(f'<path d="{d_poly(outer)}" fill="#ffffff" opacity="0.12"/>')
    art.pencil(d_poly(outer), 0.9, color=mix(rind, '#3a2a1a', 0.5), op=0.4, disp=1)
    return Polygon(outer).buffer(0)


def citrus_side(art, cx, cy, r, th, kind='orange', ang=0.0, op=0.95):
    """Slice seen edge-on (half moon wedge on a rim)."""
    rind = {'orange': '#e9862a', 'lemon': '#efcb37', 'lime': '#5f9233'}[kind]
    flesh = {'orange': '#f6a843', 'lemon': '#f5dd6a', 'lime': '#bcd25e'}[kind]
    pts = []
    for i in range(41):
        t = math.pi * i / 40
        pts.append((r * math.cos(t), -r * math.sin(t)))
    pts += [(-r, 0), (r, 0)]
    c, s = math.cos(ang), math.sin(ang)
    P2 = [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]
    art.occlude(d_poly(P2))
    art.wash(d_poly(P2), flesh, op, disp=1.2, edge=1.5, rim=1.1)
    ring = []
    for i in range(41):
        t = math.pi * i / 40
        ring.append((cx + r * math.cos(t) * c + r * math.sin(t) * s, cy + r * math.cos(t) * s - r * math.sin(t) * c))
    art.stroke_wash(d_smooth(ring, closed=False), rind, th, op, disp=1, edge=1, rim=0.9)


def berries(art, pts, kind='cranberry', seed=3):
    rng = random.Random(seed)
    for (x, y, r) in pts:
        if kind == 'raspberry':
            dr = []
            for i in range(26):
                a = rng.uniform(0, TAU)
                rr = r * math.sqrt(rng.random()) * 0.85
                dr.append((x + rr * math.cos(a), y + rr * math.sin(a) * 0.9, r * rng.uniform(0.22, 0.3)))
            body = Point(x, y).buffer(r)
            art.occlude(shp_d(body))
            art.wash(shp_d(body), '#c4304a', 0.85, disp=1, edge=1.5, rim=1.2)
            art.dots(dr, 2, '#d8425c', 0.75, disp=0.6, edge=0.8)
            art.dots([(px - pr * 0.3, py - pr * 0.35, pr * 0.28) for px, py, pr in dr[::2]], 1, '#ffd9df', 0.6, blend='normal', wash=False)
        else:
            body = Point(x, y).buffer(r)
            art.occlude(shp_d(body))
            col = '#b0233a' if kind == 'cranberry' else '#7a1f2c'
            art.wash(shp_d(body), art.rad([(0, mix(col, '#ff8a8a', 0.35)), (1, col)], cx=.38, cy=.35, r=.7), 0.95,
                     disp=1 if kind == 'cranberry' else 2.5, edge=1.5, rim=1.3, dark=0.55)
            art.dots([(x - r * 0.35, y - r * 0.38, r * 0.2)], 1, '#fff2f0', 0.75, blend='normal', wash=False)


def ice_cube(art, x, y, s, rot, tint='#dfe9ee', clip=None, above=False, op=0.9):
    """A rounded cube seen at an angle: clear, with bright edges and a faint tint."""
    c, sn = math.cos(rot), math.sin(rot)
    def T(px, py):
        return (x + px * c - py * sn, y + px * sn + py * c)
    top = [T(-s * 0.5, -s * 0.55), T(s * 0.45, -s * 0.62), T(s * 0.62, -s * 0.18), T(-s * 0.32, -s * 0.10)]
    left = [T(-s * 0.5, -s * 0.55), T(-s * 0.32, -s * 0.10), T(-s * 0.30, s * 0.55), T(-s * 0.48, s * 0.12)]
    front = [T(-s * 0.32, -s * 0.10), T(s * 0.62, -s * 0.18), T(s * 0.58, s * 0.48), T(-s * 0.30, s * 0.55)]
    whole = Polygon(top + front[1:3] + left[2:]).convex_hull.buffer(s * 0.07, join_style=1)
    if clip is not None:
        whole = whole.intersection(clip)
        if whole.is_empty:
            return None
    d = shp_d(whole)
    if above:
        art.occlude(d, op=0.85)
        art.wash(d, '#e9f1f3', 0.5, disp=1.2, edge=1.5, rim=1.0)
    else:
        art.add(f'<path d="{d}" fill="#ffffff" opacity="0.42"/>')
        art.wash(d, tint, 0.22, disp=1.2, edge=1.5, rim=1.4, dark=0.6)
    for face, col, o in ((front, '#8aa3ae', 0.18), (left, '#a9bcc4', 0.12)):
        f = Polygon(face).buffer(0)
        if clip is not None:
            f = f.intersection(clip)
        if not f.is_empty:
            art.wash(shp_d(f), col, o, disp=1.2, edge=1.2, rim=1.2)
    art.gouache(d_poly([T(-s * 0.42, -s * 0.50), T(s * 0.40, -s * 0.58)], closed=False), stroke='#ffffff', sw=max(1.6, s * 0.06), op=0.95)
    art.gouache(d_poly([T(-s * 0.42, -s * 0.42), T(-s * 0.30, s * 0.38)], closed=False), stroke='#ffffff', sw=max(1.2, s * 0.04), op=0.75)
    art.gouache(d_poly([T(-s * 0.26, -s * 0.10), T(s * 0.55, -s * 0.16)], closed=False), stroke='#ffffff', sw=max(1.0, s * 0.03), op=0.55)
    art.pencil(d, 0.8, color='#5f7782', op=0.35, disp=1)
    return whole


# =================================================================== glass vessels
def paint_glass(art, rev, liquid=None, ice=0, ice_size=None, wall=6.0, liquid_top=0.14, inner_bottom=0.90,
                tint='#dfe7ea', seed=1, straw=None, droplets=0, garnish=None, caustic=None, base_shadow=True,
                surface=True, bubbles=0, rim_hi=True, foam=None):
    """liquid: (stops) list of (t, colour) from liquid_top downward (t in vessel coordinates)."""
    rng = random.Random(seed)
    cx = rev.cx
    sil = rev.solid(0, 1)
    bottom_y = rev.yc(1.0)
    rb = rev.R(1.0)
    if base_shadow:
        cast_shadow(art, cx, bottom_y + 2, rb * 1.25, rb * rev.k * 1.3, op=0.26, blur=14, dx=40, dy=8)
        if caustic:
            art.soft(d_poly(ell_pts(cx + rb * 0.9, bottom_y + 8, rb * 0.8, rb * rev.k * 0.7, 40)), caustic, 0.22, blur=10)
    art.occlude(shp_d(sil))
    art.wash(shp_d(sil), art.lin([(0, '#f4f7f7'), (0.6, tint), (1, mix(tint, '#8fa2ab', 0.4))], 0, 0, 1, 0), 0.32,
             disp=2, edge=2.5, rim=1.0, bloom=0.3)
    inner = rev.solid(0.0, inner_bottom, inset=wall)
    info = {'inner': inner, 'sil': sil}
    if liquid:
        liq = rev.solid(liquid_top, inner_bottom, inset=wall)
        y0, y1 = rev.yc(liquid_top) - rev.k * rev.R(liquid_top), rev.yc(inner_bottom) + rev.k * rev.R(inner_bottom)
        stops = [((rev.yc(t) - y0) / max(1, (y1 - y0)), c) for t, c in liquid]
        stops = [(min(max(o, 0), 1), c) for o, c in stops]
        g = art.lin(stops, 0, y0, 0, y1, user=True)
        art.wash(shp_d(liq), g, 0.92, disp=2.2, edge=3.5, rim=1.2, dark=0.7, bloom=0.45, gran=0.2)
        # light passes through the middle: lighter core, darker sides
        core = art.lin([(0, '#000000', 0), (0.18, '#ffffff', 0), (0.40, '#ffffff', 0.35), (0.55, '#ffffff', 0.10), (1, '#000000', 0)], 0, 0, 1, 0)
        art.add(f'<path d="{shp_d(liq)}" fill="{core}" opacity="0.8" style="mix-blend-mode:screen"/>')
        edge = art.lin([(0, '#3a2a2a', 0.5), (0.15, '#3a2a2a', 0), (0.85, '#3a2a2a', 0), (1, '#3a2a2a', 0.55)], 0, 0, 1, 0)
        art.wash(shp_d(liq), edge, 0.35, disp=2, edge=2, rim=0.5)
        info['liquid'] = liq
        if surface:
            ex, ey, erx, ery = rev.ell(liquid_top, inset=wall)
            surf = ellipse_poly(ex, ey, erx, ery)
            top_col = liquid[0][1]
            art.wash(shp_d(surf), mix(top_col, '#ffffff', 0.35), 0.75, blend='normal', disp=1.5, edge=2.5, rim=1.0, dark=0.7)
            art.pencil(d_smooth(ell_pts(ex, ey, erx, ery, 90), closed=True), 0.8, color=mix(top_col, '#2a1f1a', 0.5), op=0.35)
            info['surface'] = surf
        if foam:
            ex, ey, erx, ery = rev.ell(liquid_top - 0.05, inset=wall)
            fz = rev.solid(liquid_top - 0.06, liquid_top + 0.02, inset=wall)
            art.wash(shp_d(fz), foam, 0.95, blend='normal', disp=2, edge=2, rim=0.5)
    if bubbles and liquid:
        bb = []
        for _ in range(bubbles):
            t = rng.uniform(liquid_top + 0.03, inner_bottom - 0.03)
            th = rng.uniform(-1.3, 1.3)
            x, y = rev.pt(t, th, inset=wall + 4)
            bb.append((x, y - rng.uniform(0, 40), rng.uniform(1.0, 3.2)))
        art.dots(bb, 2, '#ffffff', 0.55, blend='normal', wash=False)
        art.add(f'<path d="{"".join(f"M{x - r:.1f},{y:.1f}a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0" for x, y, r in bb[::2])}" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.8"/>')
    if garnish:
        garnish(info)
    if ice:
        s = ice_size or rev.R(liquid_top) * 0.62
        ex, ey, erx, ery = rev.ell(liquid_top, inset=wall)
        spots = [(-0.42, -0.02, 0.4), (0.38, 0.05, -0.3), (-0.05, 0.42, 0.15), (0.15, -0.35, 0.6), (-0.55, 0.55, -0.1),
                 (0.55, 0.62, 0.35), (-0.2, 1.05, 0.2), (0.35, 1.25, -0.25)]
        for i in range(ice):
            u, v, r0 = spots[i % len(spots)]
            x = ex + u * erx * 0.9
            y = ey + v * s * 0.95 + rng.uniform(-6, 6)
            above = v < 0.12
            clip = inner if not above else inner.union(Polygon([(ex - erx, ey - s), (ex + erx, ey - s), (ex + erx, ey), (ex - erx, ey)]))
            ice_cube(art, x, y, s * rng.uniform(0.85, 1.05), r0 + rng.uniform(-0.2, 0.2), clip=clip, above=above,
                     tint=liquid[0][1] if liquid else tint)
    if straw:
        (x0, y0), (x1, y1), sw = straw
        L = LineString([(x0, y0), (x1, y1)])
        body = L.buffer(sw / 2, cap_style=2)
        art.wash(shp_d(body), '#eef3f4', 0.55, blend='normal', disp=1, edge=1, rim=0.6)
        for off in (sw / 2, -sw / 2):
            o = L.parallel_offset(abs(off), 'left' if off > 0 else 'right')
            if o.geom_type == 'LineString':
                art.pencil(d_poly(list(o.coords), closed=False), 1.0, color='#7d939c', op=0.55, disp=0.8)
        hl = L.parallel_offset(sw * 0.18, 'left')
        if hl.geom_type == 'LineString':
            art.gouache(d_poly(list(hl.coords), closed=False), stroke='#ffffff', sw=sw * 0.18, op=0.9)
    # glass walls: thick edges, highlights, rim
    for th, col, w, o in ((-1.48, '#8aa0a8', 6, 0.35), (1.48, '#6f858e', 8, 0.45)):
        art.stroke_wash(d_smooth(rev.line(th, 0.02, 0.98), closed=False), col, w, o, disp=1.5, edge=1.5, rim=1.0)
    for th, w, o in ((-1.05, 7, 0.75), (-0.82, 2.5, 0.65), (1.12, 3, 0.45)):
        ln = rev.line(th, 0.06, 0.86)
        art.gouache(d_smooth(ln, closed=False), stroke='#ffffff', sw=w, op=o, blur=1.2)
    ex, ey, erx, ery = rev.ell(0.0)
    art.wash(shp_d(ellipse_poly(ex, ey, erx, ery).difference(ellipse_poly(ex, ey + 0.5, erx - wall, ery - wall * rev.k))),
             '#c5d2d6', 0.5, disp=1, edge=1, rim=0.8)
    if rim_hi:
        art.gouache(d_smooth(ell_pts(ex, ey, erx - wall / 2, ery - wall * rev.k / 2, 80, a0=math.pi * 1.05, a1=math.pi * 1.7), closed=False),
                    stroke='#ffffff', sw=2.6, op=0.95)
        art.gouache(d_smooth(ell_pts(ex, ey, erx - wall / 2, ery - wall * rev.k / 2, 60, a0=0.2, a1=0.9), closed=False),
                    stroke='#ffffff', sw=2.0, op=0.8)
    # heavy base
    base = rev.solid(inner_bottom, 1.0)
    art.wash(shp_d(base), art.lin([(0, '#b7c6cb'), (1, '#e8eeef')], 0, 0, 0, 1), 0.45, disp=1.5, edge=2, rim=1.2)
    bx, by, brx, bry = rev.ell(0.985)
    art.gouache(d_smooth(ell_pts(bx, by, brx * 0.92, bry * 0.8, 50, a0=0.3, a1=2.6), closed=False), stroke='#ffffff', sw=2.2, op=0.75)
    ext = list(sil.exterior.coords)[:-1]
    art.pencil(d_smooth(ext[::2], closed=True), 1.0, color='#5f7480', op=0.45, dash='200 14 90 10')
    if droplets:
        dd = []
        for _ in range(droplets):
            t = rng.uniform(0.18, 0.92)
            th = rng.uniform(-1.25, 1.25)
            x, y = rev.pt(t, th)
            dd.append((x, y, rng.uniform(1.2, 3.0)))
        art.dots([(x, y + r * 0.4, r) for x, y, r in dd], 1, '#6f8794', 0.35, disp=0.5, edge=0.6)
        art.dots([(x - r * 0.3, y - r * 0.3, r * 0.45) for x, y, r in dd], 1, '#ffffff', 0.9, blend='normal', wash=False)
    return info


# =================================================================== coasters & plates
def tile_coaster(art, cx, cy, s, k, rot=0.18, thick=9, pal=('#2f58a8', '#4f8f74', '#d77d8e', '#f3efe4')):
    """Square ceramic tile coaster with a painted flower, like the shop's."""
    blue, green, pink, ground = pal
    c, sn = math.cos(rot), math.sin(rot)

    def T(x, y):  # top-down unit square [-1,1] -> screen
        X, Y = x * s, y * s
        return (cx + X * c - Y * sn, cy + (X * sn + Y * c) * k)
    sq = [T(-1, -1), T(1, -1), T(1, 1), T(-1, 1)]
    top = Polygon(sq)
    side = affinity.translate(top, 0, thick)
    cast_shadow(art, cx, cy + thick, s * 1.2, s * k * 1.25, op=0.25, blur=12, dx=26, dy=8)
    art.occlude(shp_d(unary_union([top, side])))
    art.wash(shp_d(unary_union([top, side]).difference(top)), '#a89f92', 0.6, disp=1.2, edge=1.2, rim=1.0)
    art.wash(shp_d(top), ground, 0.9, disp=1.2, edge=1.5, rim=0.8)
    # border band
    outer = Polygon([T(-0.92, -0.92), T(0.92, -0.92), T(0.92, 0.92), T(-0.92, 0.92)])
    inner = Polygon([T(-0.74, -0.74), T(0.74, -0.74), T(0.74, 0.74), T(-0.74, 0.74)])
    art.wash(shp_d(outer.difference(inner)), green, 0.55, disp=1.5, edge=1.2, rim=1.2, gran=0.3)
    # corner quarter flowers
    for qx, qy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        pts = []
        for i in range(25):
            a = math.atan2(-qy, -qx) - math.pi / 4 + math.pi / 2 * i / 24
            rr = 0.36 * (0.75 + 0.25 * math.cos(4 * (a - math.atan2(-qy, -qx))))
            pts.append(T(qx * 0.92 + rr * math.cos(a), qy * 0.92 + rr * math.sin(a)))
        pts.append(T(qx * 0.92, qy * 0.92))
        art.wash(d_poly(pts), pink, 0.6, disp=1.2, edge=1, rim=1.1)
    # central flower
    petals = []
    for i in range(8):
        a0 = TAU * i / 8
        pts = []
        for j in range(21):
            a = a0 - 0.32 + 0.64 * j / 20
            rr = 0.52 * math.sin(math.pi * j / 20) ** 0.6
            pts.append(T(rr * math.cos(a), rr * math.sin(a)))
        petals.append(d_smooth(pts, closed=True))
    art.wash(' '.join(petals), blue, 0.75, disp=1.2, edge=1.5, rim=1.3, gran=0.35)
    art.wash(d_poly([T(0.13 * math.cos(t), 0.13 * math.sin(t)) for t in [i / 24 * TAU for i in range(24)]]), '#e2b84a', 0.9, disp=1, edge=1)
    leaves = []
    for i in range(4):
        a = TAU * i / 4 + math.pi / 4
        pts = [T(0.35 * math.cos(a), 0.35 * math.sin(a)), T(0.62 * math.cos(a + 0.18), 0.62 * math.sin(a + 0.18)),
               T(0.72 * math.cos(a), 0.72 * math.sin(a)), T(0.62 * math.cos(a - 0.18), 0.62 * math.sin(a - 0.18))]
        leaves.append(d_smooth(pts))
    art.wash(' '.join(leaves), green, 0.7, disp=1, edge=1, rim=1.1)
    art.pencil(d_poly(sq), 1.0, op=0.4)
    art.gouache(d_poly([T(-1, -1), T(1, -1)], closed=False), stroke='#ffffff', sw=1.6, op=0.7)
    return top


def round_coaster(art, cx, cy, r, k, thick=6, ground='#f1eadb', pattern='#c7a7a0'):
    top = ellipse_poly(cx, cy, r, r * k)
    side = affinity.translate(top, 0, thick)
    cast_shadow(art, cx, cy + thick, r * 1.05, r * k * 1.1, op=0.22, blur=10, dx=20, dy=6)
    art.occlude(shp_d(unary_union([top, side])))
    art.wash(shp_d(unary_union([top, side]).difference(top)), '#b6a993', 0.55, disp=1, edge=1, rim=1.0)
    art.wash(shp_d(top), ground, 0.85, disp=1.2, edge=1.5, rim=0.8)
    # printed floral ring
    rng = random.Random(4)
    pts = []
    for i in range(28):
        a = TAU * i / 28
        rr = r * rng.uniform(0.72, 0.86)
        pts.append((cx + rr * math.cos(a), cy + rr * k * math.sin(a), r * rng.uniform(0.02, 0.05)))
    art.dots(pts, 2, pattern, 0.6, disp=1, edge=0.8)
    art.pencil(d_smooth(ell_pts(cx, cy, r * 0.9, r * k * 0.9, 80), closed=True), 0.8, color='#a08a78', op=0.35, dash='6 5')
    art.pencil(d_smooth(ell_pts(cx, cy, r, r * k, 80), closed=True), 1.0, op=0.35)
    return top


def stone_plate(art, cx, cy, rx, k, tone='dark', rim=0.17, thick=11, seed=5):
    """Charcoal speckled stoneware (tone='dark') or matte grey (tone='grey') plate. Returns the well ellipse."""
    rng = random.Random(seed)
    ry = rx * k
    if tone == 'dark':
        base, edge_c, hi, speck = '#3c3b3e', '#232326', '#9b9aa0', '#a3a09a'
    else:
        base, edge_c, hi, speck = '#77787c', '#4e4f53', '#d5d6d9', '#b9b8b3'
    top = ellipse_poly(cx, cy, rx, ry)
    side = affinity.translate(top, 0, thick)
    cast_shadow(art, cx, cy + thick, rx * 1.02, ry * 1.06, op=0.30, blur=18, dx=34, dy=10)
    body = unary_union([top, side])
    art.occlude(shp_d(body))
    art.wash(shp_d(body.difference(top)), edge_c, 0.85, disp=1.5, edge=1.5, rim=1.0, gran=0.35)
    art.wash(shp_d(top), art.rad([(0, mix(base, '#ffffff', 0.10)), (0.7, base), (1, mix(base, edge_c, 0.4))], cx=.45, cy=.42, r=.62), 0.94,
             disp=2, edge=3, rim=1.1, dark=0.75, bloom=0.12, gran=0.18, bfreq=0.012)
    # sheen on the far rim and on the near well wall
    wrx, wry = rx * (1 - rim), ry * (1 - rim)
    rimband = top.difference(ellipse_poly(cx, cy - 2, wrx, wry))
    art.wash(shp_d(rimband), mix(base, '#ffffff', 0.12), 0.35, disp=1.5, edge=2, rim=0.8)
    sheen = ell_pts(cx, cy, rx * 0.93, ry * 0.9, 50, a0=math.pi * 1.08, a1=math.pi * 1.62)
    art.soft(d_smooth(LineString(sheen).buffer(5, cap_style=1).exterior.coords[:]), hi, 0.45, blend='screen', blur=3, disp=3)
    sheen2 = ell_pts(cx, cy - 2, wrx * 1.0, wry * 1.0, 50, a0=0.25, a1=1.2)
    art.soft(d_smooth(LineString(sheen2).buffer(3, cap_style=1).exterior.coords[:]), hi, 0.3, blend='screen', blur=2.5, disp=2)
    sp = []
    for _ in range(160):
        a = rng.uniform(0, TAU)
        rr = math.sqrt(rng.random())
        sp.append((cx + rr * rx * 0.98 * math.cos(a), cy + rr * ry * 0.98 * math.sin(a), rng.uniform(0.5, 1.4)))
    art.dots(sp, 1, speck, 0.55, blend='screen', wash=False)
    art.pencil(d_smooth(ell_pts(cx, cy, rx, ry, 120), closed=True), 1.1, color='#1d1d20', op=0.5)
    return (cx, cy - 2, wrx, wry)


def fluted_plate(art, cx, cy, rx, k, thick=11, flutes=60):
    """Cream plate with radial flutes (the shop's dessert plates)."""
    ry = rx * k
    cast_shadow(art, cx, cy + thick, rx, ry * 1.04, op=0.28, blur=16, dx=30, dy=10)
    pts = []
    for i in range(240):
        th = TAU * i / 240
        m = 1 + 0.008 * math.cos(44 * th)
        pts.append((cx + rx * m * math.cos(th), cy + ry * m * math.sin(th)))
    top = Polygon(pts)
    side = affinity.translate(top, 0, thick)
    body = unary_union([top, side])
    art.occlude(shp_d(body))
    art.wash(shp_d(body.difference(top)), art.lin([(0, '#cfc2ac'), (0.5, '#bfb19b'), (1, '#c9bca8')], 0, 0, 1, 0), 0.6,
             disp=2, edge=2, rim=1.1, bloom=0.3, gran=0.2)
    art.wash(shp_d(top), art.lin([(0, '#e6e0d6'), (0.45, '#f4eee3'), (1, '#efe4d0')], 0, 0, 0, 1), 0.55,
             disp=3, edge=3.5, rim=1.0, dark=0.82, bloom=0.4, gran=0.15)
    irx, iry = rx * 0.6, ry * 0.6
    dark, light = [], []
    for i in range(flutes):
        th = TAU * i / flutes + 0.03
        x0, y0 = cx + irx * 1.1 * math.cos(th), cy - 3 + iry * 1.1 * math.sin(th)
        x1, y1 = cx + rx * 0.965 * math.cos(th), cy + ry * 0.965 * math.sin(th)
        mid = ((x0 + x1) / 2, (y0 + y1) / 2 + 1.5)
        (dark if i % 2 == 0 else light).append(d_smooth([(x0, y0), mid, (x1, y1)], closed=False))
    art.stroke_wash(' '.join(dark), '#cdbfa9', 2.4, 0.36, disp=1.8, edge=1.0, rim=0.8, bloom=0.4, gran=0.25)
    art.gouache(' '.join(light), stroke='#fffaf2', sw=1.6, op=0.45, blur=0.5)
    well = ellipse_poly(cx, cy - 3, irx, iry)
    art.wash(shp_d(well), art.lin([(0, '#ddd3c3'), (0.55, '#eee6d9'), (1, '#f4eee3')], 0, 0, 1, 0), 0.5,
             disp=2.5, edge=3, rim=1.0, dark=0.75)
    front = [(cx + rx * math.cos(th), cy + thick + ry * math.sin(th)) for th in [i / 60 * math.pi for i in range(61)]]
    art.pencil(d_smooth(front, closed=False), 1.2, op=0.42)
    art.pencil(d_smooth(ell_pts(cx, cy, rx, ry, 120), closed=True), 1.0, op=0.32, dash='170 26 70 14')
    hi = ell_pts(cx, cy, rx * 0.985, ry * 0.96, 50, a0=math.pi * 1.06, a1=math.pi * 1.55)
    art.gouache(d_smooth(hi, closed=False), stroke='#fffdf8', sw=3.0, op=0.85)
    return (cx, cy - 3, irx, iry)


def square_plate(art, cx, cy, s, k, rot=0.0, thick=10):
    """White square plate with a low raised rim (tortillas)."""
    c, sn = math.cos(rot), math.sin(rot)

    def T(x, y):
        X, Y = x * s, y * s
        return (cx + X * c - Y * sn, cy + (X * sn + Y * c) * k)
    def rr(m, rad=0.12):
        return Polygon([T(*p) for p in rounded_square(m, rad)])
    top = rr(1.0)
    side = affinity.translate(top, 0, thick)
    cast_shadow(art, cx, cy + thick, s * 1.15, s * k * 1.2, op=0.28, blur=18, dx=34, dy=10)
    body = unary_union([top, side])
    art.occlude(shp_d(body))
    art.wash(shp_d(body.difference(top)), '#b9b4ad', 0.6, disp=1.5, edge=1.5, rim=1.0)
    art.wash(shp_d(top), art.lin([(0, '#e7e5e2'), (0.5, '#f6f4f0'), (1, '#e4e0da')], 0, 0, 1, 1), 0.6, disp=2, edge=3, rim=1.0, dark=0.8)
    inner = rr(0.82, 0.1)
    art.wash(shp_d(top.difference(inner)), '#d9d5cf', 0.35, disp=1.5, edge=2, rim=0.9)
    art.pencil(shp_d(top), 1.0, op=0.38)
    art.pencil(shp_d(inner), 0.8, op=0.22)
    art.gouache(d_poly([T(-0.9, -0.97), T(0.9, -0.97)], closed=False), stroke='#ffffff', sw=2.5, op=0.8)
    return inner, T


def rounded_square(m, rad, n=8):
    pts = []
    corners = [(m - rad, -m + rad, -math.pi / 2), (m - rad, m - rad, 0), (-m + rad, m - rad, math.pi / 2), (-m + rad, -m + rad, math.pi)]
    for (x, y, a0) in corners:
        for i in range(n + 1):
            a = a0 + math.pi / 2 * i / n
            pts.append((x + rad * math.cos(a), y + rad * math.sin(a)))
    return pts


def wood_board(art, cx, cy, w, h, k, rot=0.0, thick=16, handle=True, seed=7, color='#c99a62'):
    rng = random.Random(seed)
    c, sn = math.cos(rot), math.sin(rot)

    def T(x, y):
        return (cx + x * c - y * sn, cy + (x * sn + y * c) * k)
    outline = [(x * w, y * h) for x, y in rounded_square(1.0, 0.10)]
    if handle:
        outline = [(x * w, y * h) for x, y in rounded_square(1.0, 0.10)]
    top = Polygon([T(x, y) for x, y in outline])
    if handle:
        hp = [T(w * 0.98, -h * 0.22), T(w * 1.32, -h * 0.20), T(w * 1.38, 0), T(w * 1.32, h * 0.20), T(w * 0.98, h * 0.22)]
        top = unary_union([top, Polygon(hp).buffer(6, join_style=1)])
        hole = Point(*T(w * 1.25, 0)).buffer(h * 0.07)
        hole = affinity.scale(hole, 1, k)
        top = top.difference(hole)
    side = affinity.translate(top, 0, thick)
    cast_shadow(art, cx, cy + thick, w * 1.15, h * k * 1.2, op=0.28, blur=18, dx=36, dy=10)
    body = unary_union([top, side])
    art.occlude(shp_d(body))
    art.wash(shp_d(body.difference(top)), mix(color, '#5a3b22', 0.45), 0.85, disp=1.5, edge=1.5, rim=1.0, gran=0.3)
    art.wash(shp_d(top), art.lin([(0, mix(color, '#f6e1c0', 0.35)), (0.6, color), (1, mix(color, '#8a5a32', 0.3))], 0, 0, 1, 1), 0.85,
             disp=2, edge=3, rim=1.1, dark=0.7, bloom=0.45, gran=0.35)
    grain = []
    for i in range(16):
        y0 = -h * 0.9 + 1.8 * h * i / 15 + rng.uniform(-6, 6)
        pts = []
        for j in range(13):
            x = -w * 0.95 + 1.9 * w * j / 12
            pts.append(T(x, y0 + 5 * math.sin(j * 0.7 + i) + rng.uniform(-2, 2)))
        grain.append(d_smooth(pts, closed=False))
    art.pencil(' '.join(grain), 0.9, color='#7a5232', op=0.35, disp=1.6)
    knots = [T(rng.uniform(-w * 0.6, w * 0.6), rng.uniform(-h * 0.5, h * 0.5)) for _ in range(2)]
    for (x, y) in knots:
        art.pencil(d_smooth(ell_pts(x, y, 12, 5, 24), closed=True), 0.9, color='#7a5232', op=0.35)
    art.pencil(shp_d(top), 1.1, color='#5e3e24', op=0.45)
    return top, T


def bamboo_tray(art, cx, cy, w, h, k, thick=12, color='#d8b57c'):
    def T(x, y):
        return (cx + x, cy + y * k)
    pts = [T(x * w, y * h) for x, y in rounded_square(1.0, 0.14)]
    top = Polygon(pts)
    side = affinity.translate(top, 0, thick)
    cast_shadow(art, cx, cy + thick, w * 1.1, h * k * 1.2, op=0.26, blur=16, dx=34, dy=8)
    body = unary_union([top, side])
    art.occlude(shp_d(body))
    art.wash(shp_d(body.difference(top)), mix(color, '#7a5530', 0.4), 0.8, disp=1.2, edge=1.2, rim=1.0)
    art.wash(shp_d(top), art.lin([(0, mix(color, '#fff3dc', 0.4)), (1, color)], 0, 0, 1, 1), 0.8, disp=1.5, edge=2.5, rim=1.0, gran=0.3)
    ls = []
    for i in range(1, 9):
        y = -h + 2 * h * i / 9
        ls.append(d_poly([T(-w * 0.96, y), T(w * 0.96, y)], closed=False))
    art.pencil(' '.join(ls), 0.8, color='#9c7444', op=0.3)
    art.pencil(shp_d(top), 1.0, color='#7a5530', op=0.4)
    return top, T


# =================================================================== the striped teapot set
class StripedPot:
    """White porcelain pot with indigo pinstripes, like the shop's chamomile pot."""

    def __init__(self, art, cx, cy, a=150, b=125, k=0.36, seed=4):
        self.art, self.cx, self.cy, self.a, self.b, self.k = art, cx, cy, a, b, k
        self.ce = math.sqrt(1 - k * k)
        self.rng = random.Random(seed)

    def P(self, lam, phi, s=1.0):
        X = self.a * s * math.cos(phi) * math.sin(lam)
        Y = self.b * s * math.sin(phi)
        Z = self.a * s * math.cos(phi) * math.cos(lam)
        return (self.cx + X, self.cy - Y * self.ce + Z * self.k)

    def visible(self, lam, phi):
        return math.sin(phi) * self.k / self.b + math.cos(phi) * math.cos(lam) * self.ce / self.a > 0

    def silhouette(self):
        secs = []
        for i in range(41):
            phi = -math.pi / 2 + math.pi * i / 40
            r = self.a * math.cos(phi)
            secs.append((self.cx, self.cy - self.b * math.sin(phi) * self.ce, max(r, 0.1), max(r * self.k, 0.1)))
        return union_of_ellipses(secs)

    def band(self, l0, l1, phi_lo=-1.5, phi_hi=1.25):
        left, right = [], []
        for i in range(31):
            phi = phi_lo + (phi_hi - phi_lo) * i / 30
            if self.visible(l0, phi):
                left.append(self.P(l0, phi))
            if self.visible(l1, phi):
                right.append(self.P(l1, phi))
        if len(left) < 2 or len(right) < 2:
            return None
        return Polygon(left + right[::-1]).buffer(0)

    def draw(self, spout=True, handle=True, face=None):
        art = self.art
        sil = self.silhouette()
        self.sil = sil
        # spout (behind body on the left)
        if spout:
            base = self.P(-1.30, -0.32)
            tip = (self.cx - self.a * 1.58, self.cy - self.b * 0.86)
            ctrl = (self.cx - self.a * 1.50, self.cy + self.b * 0.12)
            pts, rads = [], []
            for i in range(41):
                t = i / 40
                x = (1 - t) ** 2 * base[0] + 2 * (1 - t) * t * ctrl[0] + t * t * tip[0]
                y = (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * ctrl[1] + t * t * tip[1]
                pts.append((x, y))
                rads.append(lerp(self.a * 0.24, self.a * 0.075, t ** 0.8))
            body = unary_union([Point(x, y).buffer(r_) for (x, y), r_ in zip(pts, rads)]).buffer(0)
            sd = shp_d(body)
            art.occlude(sd)
            art.wash(sd, '#f2f2ef', 0.8, disp=2, edge=2.5, rim=1.0)
            # normals for offset lines
            def offs(f):
                out = []
                for i in range(1, 40):
                    (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
                    tx, ty = x1 - x0, y1 - y0
                    L = math.hypot(tx, ty) or 1
                    nx, ny = -ty / L, tx / L
                    out.append((pts[i][0] + nx * rads[i] * f, pts[i][1] + ny * rads[i] * f))
                return out
            art.soft_in(sd, shp_d(LineString(offs(-0.75)).buffer(self.a * 0.06)), '#8f93a8', 0.55, blur=5, disp=3)
            art.gouache(d_smooth(offs(0.45)[3:-4], closed=False), stroke='#ffffff', sw=3.5, op=0.8, blur=1.2)
            st = [d_smooth(offs(f)[2:-2], closed=False) for f in (-0.55, 0.0, 0.55)]
            cid = art.clip(sd)
            art.add(f'<g clip-path="url(#{cid})">')
            art.stroke_wash(' '.join(st), INDIGO, 3.2, 0.8, disp=1.0, edge=0.8, rim=1.0)
            art.add('</g>')
            tx_, ty_ = pts[-1][0] - pts[-3][0], pts[-1][1] - pts[-3][1]
            ang = math.atan2(ty_, tx_)
            tipe = ell_pts(tip[0], tip[1], rads[-1] * 1.05, rads[-1] * 0.45, 30, rot=ang + math.pi / 2)
            art.wash(d_poly(tipe), '#6f7488', 0.75, disp=1, edge=1)
            art.pencil(sd, 1.0, color='#3b4a6b', op=0.4)
        if handle:
            A = self.P(1.42, 0.55)
            B = self.P(1.42, -0.45)
            c1 = (A[0] + self.a * 0.75, A[1] - self.b * 0.25)
            c2 = (B[0] + self.a * 0.72, B[1] + self.b * 0.2)
            pts = []
            for i in range(41):
                t = i / 40
                x = (1 - t) ** 3 * A[0] + 3 * (1 - t) ** 2 * t * c1[0] + 3 * (1 - t) * t * t * c2[0] + t ** 3 * B[0]
                y = (1 - t) ** 3 * A[1] + 3 * (1 - t) ** 2 * t * c1[1] + 3 * (1 - t) * t * t * c2[1] + t ** 3 * B[1]
                pts.append((x, y))
            L = LineString(pts)
            hb = L.buffer(15, cap_style=1)
            art.occlude(shp_d(hb))
            art.wash(shp_d(hb), art.lin([(0, '#f4f3ef'), (1, '#c3c6d0')], 0, 0, 1, 1), 0.8, disp=2, edge=2.5, rim=1.0)
            mid = L.parallel_offset(0.0, 'left') if False else L
            for f_ in (-6, 6):
                o_ = L.parallel_offset(abs(f_), 'left' if f_ > 0 else 'right')
                if o_.geom_type == 'LineString':
                    art.stroke_wash(d_smooth(list(o_.coords)[2:-2], closed=False), INDIGO, 3.2, 0.8, disp=1.0, edge=0.8, rim=1.0)
            art.soft_in(shp_d(hb), shp_d(LineString([(x + 5, y + 6) for x, y in pts]).buffer(7)), '#8f93a8', 0.45, blur=4, disp=3)
            art.pencil(shp_d(hb), 1.0, color='#3b4a6b', op=0.4)
        cast_shadow(art, self.cx, self.cy + self.b * self.ce + 6, self.a * 1.05, self.a * self.k * 1.1, op=0.3, blur=16, dx=40, dy=6)
        art.occlude(shp_d(sil))
        # porcelain body shading
        art.wash(shp_d(sil), art.rad([(0, '#ffffff'), (0.55, '#eeeef0'), (1, '#b9bdcb')], cx=.36, cy=.32, r=.75), 0.75,
                 disp=2.5, edge=3.5, rim=1.0, dark=0.75, bloom=0.4, gran=0.2)
        # stripes: alternating thick and thin
        lam = -math.pi / 2 - 0.1
        stripes = []
        i = 0
        while lam < math.pi / 2 + 0.1:
            w = 0.075 if i % 3 == 0 else 0.032
            gap = 0.13 if i % 3 == 0 else 0.085
            stripes.append((lam, lam + w))
            lam += w + gap
            i += 1
        polys = []
        for l0, l1 in stripes:
            p = self.band(l0, l1)
            if p is not None and not p.is_empty:
                polys.append(p.intersection(sil))
        sd = ' '.join(shp_d(p) for p in polys if not p.is_empty)
        art.wash(sd, art.lin([(0, '#3657a4'), (0.6, INDIGO), (1, '#1f3466')], 0, 0, 1, 0), 0.85, disp=1.6, edge=1.6, rim=1.3, dark=0.6, gran=0.35)
        # form shadow over the stripes
        term = Polygon([self.P(0.55 - 0.2 * j / 20, -1.4 + 2.7 * j / 20) for j in range(21)] +
                       [(self.cx + self.a * 1.5, self.cy + self.b), (self.cx + self.a * 1.5, self.cy - self.b * 1.2)]).buffer(0).intersection(sil)
        if not term.is_empty:
            art.wash(shp_d(term), art.lin([(0, '#6d6f8a', 0), (0.4, '#6d6f8a', 0.45), (1, '#4a4c66', 0.6)], 0, 0, 1, 0), 0.5,
                     disp=4, edge=4, rim=1.0, bloom=0.5)
        # big window highlight
        hl = ell_pts(*self.P(-0.55, 0.42), 26, 15, 30, rot=-0.6)
        art.gouache(d_smooth(hl), '#ffffff', 0.9, disp=2, blur=2.5)
        hl2 = ell_pts(*self.P(-0.38, 0.25), 8, 5, 20, rot=-0.6)
        art.gouache(d_smooth(hl2), '#ffffff', 0.95, disp=1, blur=0.8)
        # lid
        lx, ly = self.P(0, math.pi / 2)
        lr = self.a * 0.52
        lid_e = ellipse_poly(lx, ly + 4, lr, lr * self.k)
        art.occlude(shp_d(lid_e))
        art.wash(shp_d(lid_e), art.lin([(0, '#ffffff'), (1, '#c6c9d6')], 0, 0, 1, 0), 0.8, disp=1.5, edge=2, rim=1.0)
        dome = unary_union([ellipse_poly(lx, ly + 4 - j * 3.2, lr * (1 - j * 0.075), lr * self.k * (1 - j * 0.075)) for j in range(9)])
        art.occlude(shp_d(dome))
        art.wash(shp_d(dome), art.rad([(0, '#ffffff'), (1, '#c7cad6')], cx=.35, cy=.3, r=.8), 0.8, disp=1.5, edge=2.2, rim=1.0)
        ls = []
        for j in range(-5, 6):
            th = j * 0.28
            p0 = (lx + lr * 0.95 * math.sin(th), ly + 4 + lr * self.k * 0.95 * math.cos(th))
            p1 = (lx + lr * 0.32 * math.sin(th), ly - 18 + lr * self.k * 0.32 * math.cos(th))
            ls.append(d_poly([p0, p1], closed=False))
        art.stroke_wash(' '.join(ls[::2]), INDIGO, 2.4, 0.7, disp=1, edge=0.8, rim=1.0)
        knob = Point(lx, ly - 30).buffer(15)
        knob = affinity.scale(knob, 1, 0.85)
        art.occlude(shp_d(knob))
        art.wash(shp_d(knob), art.rad([(0, '#4d6fbd'), (1, '#1d2f5c')], cx=.38, cy=.35, r=.7), 0.95, disp=1, edge=1.5, rim=1.2)
        art.gouache(d_smooth(ell_pts(lx - 5, ly - 35, 4, 2.5, 12)), '#ffffff', 0.9, disp=0.5, blur=0.5)
        art.pencil(shp_d(sil), 1.1, color='#3b4a6b', op=0.42, dash='260 14 80 10')
        art.pencil(shp_d(dome), 0.9, color='#3b4a6b', op=0.35)
        if face:
            face(self)
        return sil


def striped_cup(art, cx, top_y, r=62, h=74, k=0.36, tea='#c99545', tea_op=0.85, steam=False):
    rev = Revolve(cx, top_y, h, k, lambda t: r * (1 - 0.13 * t ** 1.4))
    sil = rev.solid(0, 1)
    cast_shadow(art, cx, top_y + h + 4, r * 1.0, r * k * 1.05, op=0.28, blur=12, dx=26, dy=6)
    art.occlude(shp_d(sil))
    art.wash(shp_d(sil), art.lin([(0, '#ffffff'), (0.55, '#eceef2'), (1, '#b8bccb')], 0, 0, 1, 0), 0.75, disp=2, edge=3, rim=1.0)
    st = []
    i = 0
    th = -math.pi / 2
    while th < math.pi / 2:
        w = 0.16 if i % 2 == 0 else 0.07
        pl = Polygon(rev.line(th, 0.06, 1.0) + rev.line(th + w, 0.06, 1.0)[::-1]).buffer(0)
        st.append(shp_d(pl.intersection(sil)))
        th += w + (0.26 if i % 2 == 0 else 0.17)
        i += 1
    art.wash(' '.join(st), INDIGO, 0.82, disp=1.2, edge=1.2, rim=1.3, gran=0.3)
    term = Polygon(rev.line(0.55, 0, 1) + [(cx + r * 1.4, top_y + h + 30), (cx + r * 1.4, top_y - 30)]).buffer(0).intersection(sil)
    art.wash(shp_d(term), '#5d6080', 0.32, disp=3, edge=3, rim=0.9)
    ex, ey, erx, ery = rev.ell(0)
    rim = ellipse_poly(ex, ey, erx, ery)
    art.occlude(shp_d(rim))
    inner = ellipse_poly(ex, ey + 1, erx - 5, ery - 2)
    art.wash(shp_d(rim), '#f3f3f1', 0.7, disp=1, edge=1, rim=0.8)
    tea_e = ellipse_poly(ex, ey + 6, erx - 6, ery - 3).intersection(inner)
    art.wash(shp_d(tea_e), art.rad([(0, mix(tea, '#ffffff', 0.25)), (1, tea)], cx=.45, cy=.4, r=.6), tea_op, disp=1.2, edge=2.5, rim=1.3, dark=0.65)
    art.gouache(d_smooth(ell_pts(ex - erx * 0.3, ey + 2, erx * 0.25, ery * 0.18, 20, rot=-0.15)), '#ffffff', 0.45, disp=1, blur=2)
    art.gouache(d_smooth(ell_pts(ex, ey, erx - 2.5, ery - 1, 60, a0=math.pi * 1.05, a1=math.pi * 1.9), closed=False), stroke='#ffffff', sw=2.2, op=0.9)
    art.pencil(shp_d(sil), 1.0, color='#3b4a6b', op=0.4)
    art.pencil(d_smooth(ell_pts(ex, ey, erx, ery, 60), closed=True), 0.9, color='#3b4a6b', op=0.4)
    if steam:
        for i in range(2):
            pts = [(ex - 10 + i * 22 + 10 * math.sin(j * 0.9 + i), ey - 20 - j * 16) for j in range(7)]
            art.soft(shp_d(LineString(pts).buffer(6 - i * 2, cap_style=1)), '#c9c3d2', 0.28, blur=4, disp=8)
    return rev, sil
