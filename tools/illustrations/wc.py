"""Watercolor-on-paper SVG engine for the Platform 13 menu illustrations.

Every illustration is built from three kinds of marks, the same way a
hand-painted menu illustration is made:
  * washes   - translucent pigment shapes with wobbly edges, darker
               dried rims, blooms and granulation (multiply-blended)
  * pencil   - thin graphite lines, slightly off-register from the paint
  * gouache  - opaque white/cream highlights added last
The SVG is rendered with headless Chromium (Playwright) at 2x and
downsampled, which gives clean anti-aliasing for the fine details.
"""
import math, random, os, io
from contextlib import contextmanager

TAU = math.pi * 2


# ---------------------------------------------------------------- geometry
def P(x, y):
    return (float(x), float(y))


def ell_pts(cx, cy, rx, ry, n=72, a0=0.0, a1=None, rot=0.0):
    """Points on an ellipse. a0/a1 in radians (0 = +x, pi/2 = +y/front)."""
    full = a1 is None
    if full:
        a1 = a0 + TAU
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    m = n if full else n - 1
    for i in range(n):
        a = a0 + (a1 - a0) * i / m
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def d_poly(pts, closed=True):
    s = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    return s + (' Z' if closed else '')


def d_smooth(pts, closed=True, t=0.5):
    """Catmull-Rom spline through pts as cubic Beziers."""
    n = len(pts)
    if n < 3:
        return d_poly(pts, closed)
    d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % n] if closed else pts[i + 1]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + (' Z' if closed else '')


def jitter(pts, amt, rng):
    return [(x + rng.uniform(-amt, amt), y + rng.uniform(-amt, amt)) for x, y in pts]


def xform(pts, dx=0, dy=0, sx=1, sy=1, rot=0, ox=0, oy=0):
    """scale+rotate about (ox,oy) then translate."""
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for x, y in pts:
        x0, y0 = (x - ox) * sx, (y - oy) * sy
        out.append((ox + x0 * c - y0 * s + dx, oy + x0 * s + y0 * c + dy))
    return out


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    """mix two #rrggbb colours."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(lerp(a[i], b[i], t)):02x}' for i in range(3))


def shp_d(geom, smooth=False):
    """shapely Polygon/MultiPolygon -> svg path d (with holes)."""
    from shapely.geometry import Polygon, MultiPolygon
    polys = [geom] if isinstance(geom, Polygon) else list(getattr(geom, 'geoms', []))
    out = []
    for p in polys:
        if p.is_empty or not isinstance(p, Polygon):
            continue
        rings = [list(p.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in p.interiors]
        for r in rings:
            if len(r) < 3:
                continue
            out.append(d_smooth(r) if smooth else d_poly(r))
    return ' '.join(out)


# ---------------------------------------------------------------- the canvas
class Art:
    def __init__(self, w=1200, h=900, seed=1, paper='#f5f0e7', fibers=True):
        self.w, self.h = w, h
        self.rng = random.Random(seed)
        self.seed = seed
        self.defs = []
        self.body = []
        self._n = 0
        self._filters = {}
        self.paper = paper
        self._paper(fibers)

    # -------------------------------------------------- ids / defs
    def uid(self, p='e'):
        self._n += 1
        return f'{p}{self._n}'

    def lin(self, stops, x1=0, y1=0, x2=0, y2=1, user=False):
        i = self.uid('lg')
        units = 'userSpaceOnUse' if user else 'objectBoundingBox'
        st = ''.join(self._stop(s) for s in stops)
        self.defs.append(f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="{units}">{st}</linearGradient>')
        return f'url(#{i})'

    def rad(self, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, user=False, gt=None):
        i = self.uid('rg')
        units = 'userSpaceOnUse' if user else 'objectBoundingBox'
        fxy = ''
        if fx is not None:
            fxy = f' fx="{fx}" fy="{fy}"'
        t = f' gradientTransform="{gt}"' if gt else ''
        st = ''.join(self._stop(s) for s in stops)
        self.defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}"{fxy} gradientUnits="{units}"{t}>{st}</radialGradient>')
        return f'url(#{i})'

    @staticmethod
    def _stop(s):
        if len(s) == 2:
            o, c = s
            a = 1
        else:
            o, c, a = s
        return f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>'

    # -------------------------------------------------- filters
    def wash_filter(self, disp=6.0, edge=3.5, rim=1.25, dark=0.62, bloom=0.35,
                    gran=0.22, freq=0.022, bfreq=0.03, gfreq=0.9, seed=None, blur=0.0):
        if seed is None:
            seed = self.rng.randint(1, 60)
        key = ('w', round(disp, 2), round(edge, 2), round(rim, 2), round(dark, 2), round(bloom, 2),
               round(gran, 2), freq, bfreq, gfreq, seed, blur)
        if key in self._filters:
            return self._filters[key]
        i = self.uid('wf')
        ba, bb = 2.2 * bloom, 1.0 - 0.75 * bloom
        ga, gb = 2.4 * gran, 1.0 - 0.9 * gran
        pre = f'<feGaussianBlur in="SourceGraphic" stdDeviation="{blur}" result="src"/>' if blur else ''
        src = 'src' if blur else 'SourceGraphic'
        f = f'''<filter id="{i}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">{pre}
<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="4" seed="{seed}" result="w"/>
<feDisplacementMap in="{src}" in2="w" scale="{disp}" xChannelSelector="R" yChannelSelector="G" result="s"/>
<feTurbulence type="fractalNoise" baseFrequency="{bfreq}" numOctaves="3" seed="{seed + 17}" result="bn"/>
<feColorMatrix in="bn" type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 {ba:.3f} 0 0 0 {bb:.3f}" result="ba"/>
<feTurbulence type="fractalNoise" baseFrequency="{gfreq}" numOctaves="2" seed="{seed + 31}" result="gn"/>
<feColorMatrix in="gn" type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 {ga:.3f} 0 0 {gb:.3f}" result="ga"/>
<feComposite in="s" in2="ba" operator="in" result="s2"/>
<feComposite in="s2" in2="ga" operator="in" result="s3"/>
<feGaussianBlur in="s" stdDeviation="{edge}" result="sb"/>
<feComposite in="s" in2="sb" operator="out" result="r0"/>
<feColorMatrix in="r0" type="matrix" values="{dark} 0 0 0 0 0 {dark} 0 0 0 0 0 {dark} 0 0 0 0 0 {rim} 0" result="rim"/>
<feMerge><feMergeNode in="s3"/><feMergeNode in="rim"/></feMerge>
</filter>'''
        self.defs.append(f)
        self._filters[key] = i
        return i

    def soft_filter(self, blur=6, disp=8, freq=0.02, seed=None):
        if seed is None:
            seed = self.rng.randint(1, 60)
        key = ('s', blur, disp, freq, seed)
        if key in self._filters:
            return self._filters[key]
        i = self.uid('sf')
        self.defs.append(f'''<filter id="{i}" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" seed="{seed}" result="w"/>
<feDisplacementMap in="SourceGraphic" in2="w" scale="{disp}" xChannelSelector="R" yChannelSelector="G" result="s"/>
<feGaussianBlur in="s" stdDeviation="{blur}"/></filter>''')
        self._filters[key] = i
        return i

    def pencil_filter(self, disp=2.2, seed=None, grain=1.0):
        if seed is None:
            seed = self.rng.randint(1, 60)
        key = ('p', disp, seed, grain)
        if key in self._filters:
            return self._filters[key]
        i = self.uid('pf')
        ga, gb = 2.0 * grain, 1.0 - 1.25 * grain
        self.defs.append(f'''<filter id="{i}" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{seed}" result="w"/>
<feDisplacementMap in="SourceGraphic" in2="w" scale="{disp}" xChannelSelector="R" yChannelSelector="G" result="s"/>
<feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="{seed + 7}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 {ga:.2f} 0 0 {gb:.2f}" result="ga"/>
<feComposite in="s" in2="ga" operator="in"/></filter>''')
        self._filters[key] = i
        return i

    def gouache_filter(self, disp=1.5, seed=None, blur=0.4):
        if seed is None:
            seed = self.rng.randint(1, 60)
        key = ('g', disp, seed, blur)
        if key in self._filters:
            return self._filters[key]
        i = self.uid('gf')
        self.defs.append(f'''<filter id="{i}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="{seed}" result="w"/>
<feDisplacementMap in="SourceGraphic" in2="w" scale="{disp}" xChannelSelector="R" yChannelSelector="G" result="s"/>
<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="1" seed="{seed + 3}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 1.2 0 0 0.35" result="ga"/>
<feComposite in="s" in2="ga" operator="in" result="s2"/>
<feGaussianBlur in="s2" stdDeviation="{blur}"/></filter>''')
        self._filters[key] = i
        return i

    # -------------------------------------------------- marks
    def add(self, s):
        self.body.append(s)

    def wash(self, d, fill, op=1.0, blend='multiply', **fk):
        f = self.wash_filter(**fk)
        self.add(f'<path d="{d}" fill="{fill}" opacity="{op:.3f}" filter="url(#{f})" style="mix-blend-mode:{blend}"/>')

    def soft(self, d, fill, op=1.0, blend='multiply', **fk):
        f = self.soft_filter(**fk)
        self.add(f'<path d="{d}" fill="{fill}" opacity="{op:.3f}" filter="url(#{f})" style="mix-blend-mode:{blend}"/>')

    def flat(self, d, fill, op=1.0, blend='normal', extra=''):
        self.add(f'<path d="{d}" fill="{fill}" opacity="{op:.3f}" style="mix-blend-mode:{blend}" {extra}/>')

    def stroke_wash(self, d, color, width, op=1.0, blend='multiply', cap='round', **fk):
        f = self.wash_filter(**fk)
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="{cap}" stroke-linejoin="round" opacity="{op:.3f}" filter="url(#{f})" style="mix-blend-mode:{blend}"/>')

    def pencil(self, d, w=1.3, color='#4b3d33', op=0.5, disp=2.2, grain=1.0, dash=None):
        f = self.pencil_filter(disp=disp, grain=grain)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{op:.3f}"{da} filter="url(#{f})" style="mix-blend-mode:multiply"/>')

    def gouache(self, d, fill='#fffdf8', op=0.9, disp=1.5, blur=0.4, stroke=None, sw=0):
        f = self.gouache_filter(disp=disp, blur=blur)
        if stroke:
            self.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" opacity="{op:.3f}" filter="url(#{f})"/>')
        else:
            self.add(f'<path d="{d}" fill="{fill}" opacity="{op:.3f}" filter="url(#{f})"/>')

    def dots(self, pts, r, color, op=0.8, blend='multiply', wash=True, **fk):
        """many small blobs in one path (fast)."""
        parts = []
        for p in pts:
            x, y = p[0], p[1]
            rr = p[2] if len(p) > 2 else r
            parts.append(f'M{x - rr:.1f},{y:.1f}a{rr:.1f},{rr:.1f} 0 1,0 {2 * rr:.1f},0a{rr:.1f},{rr:.1f} 0 1,0 {-2 * rr:.1f},0')
        d = ''.join(parts)
        if not parts:
            return
        if wash:
            fk.setdefault('disp', 1.2)
            fk.setdefault('edge', 0.8)
            self.wash(d, color, op, blend=blend, **fk)
        else:
            self.flat(d, color, op, blend=blend)

    def shadow(self, cx, cy, rx, ry, color='#7d7896', op=0.35, blur=14, rot=0):
        d = d_poly(ell_pts(cx, cy, rx, ry, 80, rot=rot))
        self.soft(d, color, op, blur=blur, disp=18, freq=0.012)

    @contextmanager
    def group(self, transform='', op=1.0, extra=''):
        self.add(f'<g transform="{transform}" opacity="{op}" {extra}>')
        yield
        self.add('</g>')

    # -------------------------------------------------- paper
    def _paper(self, fibers):
        r = random.Random(self.seed * 7 + 3)
        w, h = self.w, self.h
        self.defs.append(f'''<filter id="paperTex" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="0.11" numOctaves="4" seed="{r.randint(1, 99)}" result="n"/>
<feDiffuseLighting in="n" lighting-color="#ffffff" surfaceScale="0.32" diffuseConstant="1.135" result="l"><feDistantLight azimuth="225" elevation="62"/></feDiffuseLighting>
<feComposite in="l" in2="SourceGraphic" operator="arithmetic" k1="1" k2="0" k3="0" k4="0"/></filter>''')
        self.body.append(f'<rect width="{w}" height="{h}" fill="{self.paper}" filter="url(#paperTex)"/>')
        cloud = self.soft_filter(blur=40, disp=120, freq=0.004)
        self.body.append(f'<rect x="-100" y="-100" width="{w + 200}" height="{h + 200}" fill="#d9ccb6" opacity="0.10" filter="url(#{cloud})" style="mix-blend-mode:multiply"/>')
        if fibers:
            parts_d, parts_l = [], []
            for _ in range(46):
                x, y = r.uniform(0, w), r.uniform(0, h)
                a = r.uniform(0, TAU)
                L = r.uniform(18, 90)
                pts = []
                for k in range(6):
                    a += r.uniform(-0.5, 0.5)
                    x += math.cos(a) * L / 5
                    y += math.sin(a) * L / 5
                    pts.append((x, y))
                (parts_d if r.random() < 0.7 else parts_l).append(d_smooth(pts, closed=False))
            pf = self.pencil_filter(disp=1.0, grain=0.6)
            self.body.append(f'<path d="{" ".join(parts_d)}" fill="none" stroke="#a89880" stroke-width="0.7" opacity="0.22" filter="url(#{pf})" style="mix-blend-mode:multiply"/>')
            self.body.append(f'<path d="{" ".join(parts_l)}" fill="none" stroke="#fffaf0" stroke-width="1.1" opacity="0.5"/>')

    def occlude(self, d, op=1.0):
        """knock out what lies behind (the painter leaves this paper clean)."""
        self.add(f'<path d="{d}" fill="{self.paper}" opacity="{op}" filter="url(#paperTex)"/>')

    def clip(self, d):
        i = self.uid('cp')
        self.defs.append(f'<clipPath id="{i}"><path d="{d}"/></clipPath>')
        return i

    @contextmanager
    def clipped(self, d):
        i = self.clip(d)
        self.add(f'<g clip-path="url(#{i})">')
        yield
        self.add('</g>')

    def texture(self, d, color, freq=0.08, octaves=3, a=2.4, b=-1.0, op=1.0, blend='multiply', seed=None, stretch=None):
        """noise-driven pigment texture clipped to the shape (crumbs, pores, speckles)."""
        if seed is None:
            seed = self.rng.randint(1, 90)
        i = self.uid('tx')
        r_, g_, b_ = (int(color[k:k + 2], 16) / 255 for k in (1, 3, 5))
        bf = f'{freq}' if stretch is None else f'{freq * stretch[0]} {freq * stretch[1]}'
        self.defs.append(f'''<filter id="{i}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="{octaves}" seed="{seed}" result="n"/>
<feColorMatrix in="n" type="matrix" values="0 0 0 0 {r_:.3f} 0 0 0 0 {g_:.3f} 0 0 0 0 {b_:.3f} {a} 0 0 0 {b}"/></filter>''')
        cid = self.clip(d)
        self.add(f'<g clip-path="url(#{cid})"><path d="{d}" fill="#000" opacity="{op:.3f}" filter="url(#{i})" style="mix-blend-mode:{blend}"/></g>')

    def soft_in(self, clip_d, d, fill, op=1.0, blend='multiply', **fk):
        """soft (blurred) shading confined to a shape: crisp outside, soft inside."""
        f = self.soft_filter(**fk)
        cid = self.clip(clip_d)
        self.add(f'<g clip-path="url(#{cid})"><path d="{d}" fill="{fill}" opacity="{op:.3f}" filter="url(#{f})" style="mix-blend-mode:{blend}"/></g>')

    def vignette(self, op=0.10, color='#cbbda6'):
        g = self.rad([(0, color, 0), (0.62, color, 0), (1, color, 1)], cx=.5, cy=.48, r=.72)
        self.add(f'<rect width="{self.w}" height="{self.h}" fill="{g}" opacity="{op}" style="mix-blend-mode:multiply"/>')

    # -------------------------------------------------- output
    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}"><defs>{"".join(self.defs)}</defs>'
                f'<g style="isolation:isolate">{"".join(self.body)}</g></svg>')


# ---------------------------------------------------------------- rendering
class Renderer:
    def __init__(self, scale=2):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch()
        self.scale = scale
        self.page = None
        self._size = None

    def render(self, art, out_path, out_w=None, quality=86):
        from PIL import Image
        if self._size != (art.w, art.h):
            if self.page:
                self.page.close()
            self.page = self.browser.new_page(viewport={'width': art.w, 'height': art.h},
                                              device_scale_factor=self.scale)
            self._size = (art.w, art.h)
        html = ('<!doctype html><html><head><style>html,body{margin:0;padding:0;background:#fff}'
                'svg{display:block}</style></head><body>' + art.svg() + '</body></html>')
        self.page.set_content(html)
        self.page.wait_for_timeout(50)
        png = self.page.screenshot(clip={'x': 0, 'y': 0, 'width': art.w, 'height': art.h})
        im = Image.open(io.BytesIO(png)).convert('RGB')
        tw = out_w or art.w
        im = im.resize((tw, round(tw * art.h / art.w)), Image.LANCZOS)
        ext = os.path.splitext(out_path)[1].lower()
        if ext == '.webp':
            im.save(out_path, 'WEBP', quality=quality, method=6)
        elif ext in ('.jpg', '.jpeg'):
            im.save(out_path, quality=quality)
        else:
            im.save(out_path)
        return im

    def close(self):
        self.browser.close()
        self._pw.stop()
