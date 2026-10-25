/* Tile patterns for template A, drawn after the shop's patterned coasters
 * and its blue-striped teapot. Each category has its own tile.
 * TILES.url(catId) -> CSS url() of a seamless 100x100 SVG tile. */
(function () {
  'use strict';
  var C = {
    cobalt: '#1D3F9E', leaf: '#2E8A62', mustard: '#EDB12F', rose: '#E58AA0',
    espresso: '#3B2519', cream: '#F7F2E6', latte: '#EBD9BF', ink: '#1C2033',
    orange: '#E8892B', mint: '#4CB38A', sky: '#2F63D3'
  };
  var corners = [[0, 0], [100, 0], [0, 100], [100, 100]];
  var edges = [[50, 0], [50, 100], [0, 50], [100, 50]];
  function f(n) { return Math.round(n * 10) / 10; }
  function circ(x, y, r, c) { return '<circle cx="' + f(x) + '" cy="' + f(y) + '" r="' + r + '" fill="' + c + '"/>'; }
  function ring(x, y, r, c, w) { return '<circle cx="' + f(x) + '" cy="' + f(y) + '" r="' + r + '" fill="none" stroke="' + c + '" stroke-width="' + w + '"/>'; }
  function ell(x, y, rx, ry, rot, c) {
    return '<ellipse cx="' + f(x) + '" cy="' + f(y) + '" rx="' + rx + '" ry="' + ry + '" transform="rotate(' + rot + ' ' + f(x) + ' ' + f(y) + ')" fill="' + c + '"/>';
  }
  function rad(a) { return a * Math.PI / 180; }

  var MOTIF = {
    leaf: function (c) {
      var s = '';
      [45, 135, 225, 315].forEach(function (a) { s += ell(50 + Math.cos(rad(a)) * 19, 50 + Math.sin(rad(a)) * 19, 17, 7, a, c.fg); });
      [0, 90, 180, 270].forEach(function (a) { s += ell(50 + Math.cos(rad(a)) * 13, 50 + Math.sin(rad(a)) * 13, 6, 2.6, a, c.ac); });
      s += circ(50, 50, 5, c.ac);
      corners.forEach(function (p) { s += circ(p[0], p[1], 10, c.fg) + circ(p[0], p[1], 4, c.ac); });
      edges.forEach(function (p) { s += circ(p[0], p[1], 3, c.fg); });
      return s;
    },
    star: function (c) {
      var p = [];
      for (var i = 0; i < 16; i++) {
        var a = Math.PI * 2 * i / 16 - Math.PI / 2, r = i % 2 ? 13 : 31;
        p.push(f(50 + Math.cos(a) * r) + ',' + f(50 + Math.sin(a) * r));
      }
      var s = '<polygon points="' + p.join(' ') + '" fill="' + c.fg + '"/>' + circ(50, 50, 8, c.ac) + circ(50, 50, 3, c.bg);
      corners.forEach(function (q) { s += circ(q[0], q[1], 12, c.fg) + circ(q[0], q[1], 5.5, c.bg); });
      edges.forEach(function (q) { s += circ(q[0], q[1], 3.5, c.ac); });
      return s;
    },
    sun: function (c) {
      var s = '';
      for (var i = 0; i < 12; i++) {
        var a = Math.PI * 2 * i / 12;
        var tip = [50 + Math.cos(a) * 37, 50 + Math.sin(a) * 37];
        var b1 = [50 + Math.cos(a - 0.14) * 25, 50 + Math.sin(a - 0.14) * 25];
        var b2 = [50 + Math.cos(a + 0.14) * 25, 50 + Math.sin(a + 0.14) * 25];
        s += '<polygon points="' + f(tip[0]) + ',' + f(tip[1]) + ' ' + f(b1[0]) + ',' + f(b1[1]) + ' ' + f(b2[0]) + ',' + f(b2[1]) + '" fill="' + c.fg + '"/>';
      }
      s += circ(50, 50, 21, c.fg) + circ(50, 50, 14, c.ac) + circ(50, 50, 7, c.fg);
      corners.forEach(function (q) { s += ring(q[0], q[1], 13, c.fg, 4) + circ(q[0], q[1], 5, c.ac); });
      return s;
    },
    lattice: function (c) {
      var s = '<path d="M50 5 L95 50 L50 95 L5 50 Z" fill="none" stroke="' + c.fg + '" stroke-width="6" stroke-linejoin="round"/>';
      s += '<path d="M50 24 L76 50 L50 76 L24 50 Z" fill="' + c.ac + '"/>' + circ(50, 50, 6, c.fg);
      corners.forEach(function (q) { s += circ(q[0], q[1], 8, c.fg); });
      return s;
    },
    flower: function (c) {
      var s = '';
      for (var i = 0; i < 8; i++) {
        var a = i * 45;
        s += ell(50 + Math.cos(rad(a)) * 16, 50 + Math.sin(rad(a)) * 16, 15, 6.5, a, c.fg);
      }
      s += circ(50, 50, 7, c.ac2 || c.ac) + circ(50, 50, 3, c.bg);
      corners.forEach(function (q) {
        [0, 90, 180, 270].forEach(function (a) { s += ell(q[0] + Math.cos(rad(a + 45)) * 9, q[1] + Math.sin(rad(a + 45)) * 9, 8, 4, a + 45, c.ac); });
      });
      edges.forEach(function (q) { s += circ(q[0], q[1], 3, c.fg); });
      return s;
    },
    chevron: function (c) {
      var s = '';
      [25, 75].forEach(function (y) {
        var pts = [];
        for (var i = 0; i <= 8; i++) pts.push(f(i * 12.5) + ',' + (i % 2 ? y + 8 : y - 8));
        s += '<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + c.fg + '" stroke-width="6" stroke-linejoin="round"/>';
      });
      [[25, 50], [75, 50], [0, 50], [100, 50], [50, 0], [50, 100]].forEach(function (q) { s += circ(q[0], q[1], 4, c.ac); });
      return s;
    },
    bean: function (c) {
      var s = '';
      [[27, 27, 35], [73, 73, 35], [73, 27, -35], [27, 73, -35]].forEach(function (b) {
        s += ell(b[0], b[1], 11, 16, b[2], c.fg);
        s += '<path d="M' + b[0] + ' ' + (b[1] - 13) + ' C' + (b[0] + 6) + ' ' + (b[1] - 4) + ' ' + (b[0] - 6) + ' ' + (b[1] + 4) + ' ' + b[0] + ' ' + (b[1] + 13) +
          '" transform="rotate(' + b[2] + ' ' + b[0] + ' ' + b[1] + ')" fill="none" stroke="' + c.bg + '" stroke-width="2.6" stroke-linecap="round"/>';
      });
      [[50, 50], [50, 0], [50, 100], [0, 50], [100, 50]].forEach(function (q) { s += circ(q[0], q[1], 3.2, c.ac); });
      return s;
    },
    stripes: function (c) {
      return [[6, 14], [30, 4], [56, 14], [80, 4]].map(function (r) {
        return '<rect x="' + r[0] + '" y="0" width="' + r[1] + '" height="100" fill="' + c.fg + '"/>';
      }).join('');
    },
    bubbles: function (c) {
      return ring(22, 28, 11, c.fg, 3) + circ(66, 18, 6, c.fg) + ring(72, 68, 15, c.fg, 3) + circ(28, 78, 5, c.fg) +
        circ(48, 50, 3, c.ac) + circ(88, 40, 3, c.ac) + circ(12, 56, 2.5, c.fg) + ring(52, 90, 4, c.fg, 2) +
        '<path d="M64 60 a10 10 0 0 1 9 -3" fill="none" stroke="' + c.fg + '" stroke-width="2.4" stroke-linecap="round"/>';
    },
    paw: function (c) {
      function paw(x, y, rot, col) {
        return '<g transform="translate(' + x + ' ' + y + ') rotate(' + rot + ')" fill="' + col + '">' +
          '<ellipse cx="0" cy="5" rx="9" ry="7.5"/><ellipse cx="-9.5" cy="-5" rx="3.6" ry="4.6"/><ellipse cx="-3.4" cy="-10.5" rx="3.6" ry="4.8"/>' +
          '<ellipse cx="3.6" cy="-10.5" rx="3.6" ry="4.8"/><ellipse cx="9.6" cy="-5" rx="3.6" ry="4.6"/></g>';
      }
      return paw(29, 33, -18, c.fg) + paw(72, 72, 16, c.ac) + circ(78, 22, 2.6, c.fg) + circ(20, 80, 2.6, c.ac) + circ(50, 50, 1.8, c.fg);
    }
  };

  var SPEC = {
    light:     { kind: 'leaf',    bg: C.leaf,     fg: C.cream,   ac: C.mustard },
    main:      { kind: 'star',    bg: C.cobalt,   fg: C.cream,   ac: C.mustard },
    tortilla:  { kind: 'sun',     bg: C.mustard,  fg: C.cobalt,  ac: C.cream },
    waffle:    { kind: 'lattice', bg: C.rose,     fg: C.cream,   ac: C.cobalt },
    dessert:   { kind: 'flower',  bg: C.cream,    fg: C.rose,    ac: C.leaf, ac2: C.mustard },
    cone:      { kind: 'chevron', bg: C.cream,    fg: C.espresso, ac: C.mustard },
    coffee:    { kind: 'bean',    bg: C.espresso, fg: C.latte,   ac: C.mustard },
    tea:       { kind: 'stripes', bg: C.cream,    fg: C.cobalt },
    sparkling: { kind: 'bubbles', bg: C.sky,      fg: C.cream,   ac: C.mustard },
    cats:      { kind: 'paw',     bg: C.ink,      fg: C.orange,  ac: C.mint }
  };

  function svg(spec) {
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">' +
      '<rect width="100" height="100" fill="' + spec.bg + '"/>' + MOTIF[spec.kind](spec) +
      '<path d="M0 .5H100M.5 0V100" stroke="#000" stroke-opacity=".12" stroke-width="1"/></svg>';
  }
  var cache = {};
  function url(id) {
    if (!cache[id]) cache[id] = 'url("data:image/svg+xml,' + encodeURIComponent(svg(SPEC[id] || SPEC.tea)) + '")';
    return cache[id];
  }
  window.TILES = { url: url, spec: SPEC, colors: C };
})();
