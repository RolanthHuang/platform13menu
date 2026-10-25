/* Template C — 時鐘下 (under the clocks, after Flinders Street Station). Hash routes:
 *   #/                    departure board (home)
 *   #/<cat>               full-screen photo feed of a category
 *   #/<cat>/<item>        the feed, scrolled to an item
 *   #/<cat>/<item>/info   the same with the item's detail sheet open
 *   #/search              search
 */
(function () {
  'use strict';
  var D = window.P13;
  var STOPS = D.categories.map(function (c) { return Object.assign({}, c); });
  STOPS.push(Object.assign({}, D.cats, { isCats: true }));
  var byId = {};
  STOPS.forEach(function (s, i) { s.index = i; s.no = (i < 9 ? '0' : '') + (i + 1); byId[s.id] = s; });
  var ITEMS = [];
  D.categories.forEach(function (c) { c.items.forEach(function (it) { ITEMS.push({ it: it, cat: byId[c.id] }); }); });
  var itemById = {};
  ITEMS.forEach(function (x) { itemById[x.it.id] = x; });
  var TAG = { decaf: '無咖啡因', season: '季節限定', pot: '熱飲一壺' };

  var $ = function (s, el) { return (el || document).querySelector(s); };
  var view = $('#view'), sheetWrap = $('#sheetWrap'), sheet = $('#sheet'), ambient = $('#ambient');
  var searchWrap = $('#searchWrap'), searchInput = $('#searchInput');
  var current = null, observer = null, pushedSheet = false, pushedSearch = false, lastFocus = null, flapped = false;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function esc(s) { return String(s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function src(s, small) { return '../assets/img/' + s + (small ? '-sm' : '') + '.webp'; }
  function go(h) { if (location.hash !== h) location.hash = h; }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  function cover(stop) {
    if (stop.cover) return stop.cover;
    for (var i = 0; i < (stop.items || []).length; i++) {
      var im = stop.items[i].imgs && stop.items[i].imgs[0];
      if (im && im.kind === 'photo') return im.src;
    }
    return null;
  }
  function minPrice(stop) {
    var m = Infinity;
    (stop.items || []).forEach(function (it) {
      var p = it.price;
      if (typeof p === 'number') m = Math.min(m, p);
      else if (p && typeof p === 'object') ['hot', 'ice'].forEach(function (k) { if (p[k] != null) m = Math.min(m, p[k]); });
    });
    return m === Infinity ? null : m;
  }
  function pricesHTML(p) {
    if (typeof p === 'number') return '<span class="p"><b>' + p + '</b></span>';
    if (typeof p === 'string') return '<span class="p text">' + esc(p) + '</span>';
    return ['hot', 'ice'].filter(function (k) { return p[k] != null; }).map(function (k) {
      return '<span class="p ' + k + '"><i>' + (k === 'hot' ? '熱' : '冰') + '</i><b>' + p[k] + '</b></span>';
    }).join('');
  }
  function tagsHTML(tags) {
    if (!tags || !tags.length) return '';
    return '<span class="tags">' + tags.map(function (t) { return '<span class="tag ' + t + '">' + TAG[t] + '</span>'; }).join('') + '</span>';
  }
  var SLEEPY = '<svg class="sleepy" viewBox="0 0 120 70" aria-hidden="true"><path d="M14 58c0-20 18-34 44-34 20 0 34 8 40 20 4 8 2 14-6 14H20c-4 0-6-0-6 0z"/>' +
    '<path d="M86 30l6-14 6 12M100 30l8-12 2 15"/><path d="M90 40c3 2 6 2 9 0M102 40c3 2 6 2 9 0"/><path d="M14 58c-6-2-10-8-6-14 3-4 9-3 10 1"/><path d="M104 12h8l-8 8h8M92 2h6l-6 6h6"/></svg>';

  function seeded(seed) { return function () { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }; }
  function todaysPicks(n) {
    var d = new Date(), rnd = seeded(d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate());
    var pool = ITEMS.filter(function (x) { return x.it.imgs && x.it.imgs[0] && x.it.imgs[0].kind === 'photo'; });
    for (var i = pool.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = pool[i]; pool[i] = pool[j]; pool[j] = t; }
    var out = [], seen = {};
    pool.forEach(function (x) { if (out.length < n && !seen[x.cat.id]) { seen[x.cat.id] = 1; out.push(x); } });
    return out;
  }

  // ------------------------------------------------------------------ split-flap cells
  function cellHTML(ch) {
    return '<span class="fc" data-ch="' + esc(ch) + '"><span class="h t"><span>' + esc(ch) + '</span></span><span class="h b"><span>' + esc(ch) + '</span></span></span>';
  }
  function flaps(text, cls, id) {
    return '<span class="flaps ' + (cls || '') + '"' + (id ? ' id="' + id + '"' : '') + '><span class="sr">' + esc(text) + '</span><span class="fcs" aria-hidden="true">' +
      Array.prototype.map.call(String(text), cellHTML).join('') + '</span></span>';
  }
  function setCell(cell, ch) {
    cell.setAttribute('data-ch', ch);
    cell.querySelector('.h.t > span').textContent = ch;
    cell.querySelector('.h.b > span').textContent = ch;
  }
  var FD = 72;   // ms for each half of a flip
  function flipTo(cell, ch) {
    var old = cell.getAttribute('data-ch');
    if (old === ch) return;
    if (reduce) { setCell(cell, ch); return; }
    Array.prototype.forEach.call(cell.querySelectorAll('.ft, .fb'), function (n) { n.remove(); });
    var top = cell.querySelector('.h.t:not(.ft) > span'), bot = cell.querySelector('.h.b:not(.fb) > span');
    var ft = document.createElement('span'), fb = document.createElement('span');
    ft.className = 'h t ft'; ft.innerHTML = '<span>' + esc(old) + '</span>';
    fb.className = 'h b fb'; fb.innerHTML = '<span>' + esc(ch) + '</span>';
    top.textContent = ch;
    cell.appendChild(ft); cell.appendChild(fb);
    cell.setAttribute('data-ch', ch);
    setTimeout(function () { bot.textContent = ch; ft.remove(); fb.remove(); }, FD * 2 + 20);
  }
  function runFlaps() {
    var DIG = '0123456789', CJK = '喵咪貓茶餅';
    Array.prototype.forEach.call(document.querySelectorAll('.brow'), function (row, r) {
      Array.prototype.forEach.call(row.querySelectorAll('.fc'), function (cell, c) {
        var final = cell.getAttribute('data-ch'), set = /\d/.test(final) ? DIG : CJK;
        var steps = Math.min(15, 3 + r + c * 2), seq = [];
        for (var k = 0; k < steps; k++) seq.push(set[Math.floor(Math.random() * set.length)]);
        setCell(cell, seq[0]);
        seq.slice(1).concat([final]).forEach(function (ch, k) {
          setTimeout(function () { flipTo(cell, ch); }, 300 + r * 70 + k * (FD * 2 + 34));
        });
      });
    });
  }

  // ------------------------------------------------------------------ clocks
  function pt(cx, cy, r, a) { return (cx + Math.sin(a) * r).toFixed(2) + ' ' + (cy - Math.cos(a) * r).toFixed(2); }
  function ringPath(cx, cy, R, r) {
    function c(rad) { return 'M' + (cx - rad) + ' ' + cy + 'a' + rad + ' ' + rad + ' 0 1 0 ' + 2 * rad + ' 0a' + rad + ' ' + rad + ' 0 1 0 ' + (-2 * rad) + ' 0Z'; }
    return c(R) + c(r);
  }
  var NUM = ['XII', 'I', 'II', 'III', 'IIII', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI'];
  var CHAPTER = (function () {
    var s = '<circle cx="60" cy="60" r="44.6" class="cr"/><circle cx="60" cy="60" r="39.2" class="cr thin"/><path class="mt" d="', i, a;
    for (i = 0; i < 60; i++) { if (i % 5 === 0) continue; a = i * Math.PI / 30; s += 'M' + pt(60, 60, 39.2, a) + 'L' + pt(60, 60, 44.6, a); }
    s += '"/><path class="ht" d="';
    for (i = 0; i < 12; i++) { a = i * Math.PI / 6; s += 'M' + pt(60, 60, 37.6, a) + 'L' + pt(60, 60, 45.6, a); }
    s += '"/><g class="nums">';
    NUM.forEach(function (n, k) { s += '<text x="60" y="32.6" transform="rotate(' + k * 30 + ' 60 60)">' + n + '</text>'; });
    return s + '</g><text class="mk" x="60" y="47.6">PLATFORM 13</text>';
  })();
  var HOUR = '<rect x="58.8" y="42.4" width="2.4" height="23.6" rx=".6"/><path fill-rule="evenodd" d="' + ringPath(60, 38.4, 4.5, 2.6) + '"/>' +
    '<path d="M58.3 34.6 L61.7 34.6 L60 27.8 Z"/><circle cx="60" cy="66.4" r="2.6"/>';
  var MINUTE = '<rect x="59.15" y="29.6" width="1.7" height="38.6" rx=".5"/><path fill-rule="evenodd" d="' + ringPath(60, 26.6, 3.2, 1.85) + '"/>' +
    '<path d="M58.75 24 L61.25 24 L60 16 Z"/><circle cx="60" cy="68.2" r="2.05"/>';
  function clockSVG(h, m, o) {
    o = o || {};
    var ha = ((h % 12) + m / 60) * 30, ma = m * 6;
    var id = function (k) { return o.id ? ' id="' + o.id + k + '"' : ''; };
    var s = '<svg class="clk' + (o.big ? ' big' : '') + '" viewBox="0 0 120 120" aria-hidden="true">' +
      '<circle cx="60" cy="60" r="58.4" fill="url(#brassA)"/><circle cx="60" cy="60" r="54" fill="url(#brassB)"/>' +
      '<circle cx="60" cy="60" r="51.1" fill="#3B2A15"/><circle cx="60" cy="60" r="50.3" fill="url(#dial)"/>' +
      '<circle cx="60" cy="60" r="49" class="age"/>' + CHAPTER +
      '<g class="hs" transform="translate(1.3 2.2)" filter="url(#handShadow)"><g' + id('Hs') + ' transform="rotate(' + ha.toFixed(2) + ' 60 60)">' + HOUR + '</g>' +
      '<g' + id('Ms') + ' transform="rotate(' + ma.toFixed(2) + ' 60 60)">' + MINUTE + '</g></g>' +
      '<g class="hd"><g' + id('H') + ' transform="rotate(' + ha.toFixed(2) + ' 60 60)">' + HOUR + '</g><g' + id('M') + ' transform="rotate(' + ma.toFixed(2) + ' 60 60)">' + MINUTE + '</g></g>';
    if (o.sec != null) {
      s += '<g' + id('S') + ' transform="rotate(' + Math.floor(o.sec) * 6 + ' 60 60)"><g class="sec"><path d="M59.6 75 L60.4 75 L60.18 14.5 L59.82 14.5 Z"/><circle cx="60" cy="71.5" r="2.7"/><circle cx="60" cy="60" r="2"/></g></g>';
    }
    s += '<circle cx="60" cy="60" r="3.3" fill="url(#cap)"/><circle cx="60" cy="60" r=".95" fill="#3B2A15"/>' +
      '<circle cx="60" cy="60" r="50.3" fill="url(#glass)"/>' +
      '<path d="M24.5 50 A37 37 0 0 1 52 23.5" class="glint"/><path d="M86 93 A37 37 0 0 0 95.5 80" class="glint dim"/></svg>';
    return s;
  }
  function towerSVG() {
    var d = new Date();
    return clockSVG(d.getHours(), d.getMinutes() + d.getSeconds() / 60, { id: 'tw', big: true, sec: d.getSeconds() + d.getMilliseconds() / 1000 });
  }
  function updateTower() {
    var h = document.getElementById('twH');
    if (!h) return;
    var d = new Date(), mm = d.getMinutes() + d.getSeconds() / 60;
    var ha = 'rotate(' + (((d.getHours() % 12) + mm / 60) * 30).toFixed(2) + ' 60 60)', ma = 'rotate(' + (mm * 6).toFixed(2) + ' 60 60)';
    ['twH', 'twHs'].forEach(function (k) { document.getElementById(k).setAttribute('transform', ha); });
    ['twM', 'twMs'].forEach(function (k) { document.getElementById(k).setAttribute('transform', ma); });
    if (reduce) document.getElementById('twS').setAttribute('transform', 'rotate(' + d.getSeconds() * 6 + ' 60 60)');
  }
  function departures() {
    var d = new Date(), base = Math.ceil((d.getHours() * 60 + d.getMinutes() + 1) / 5) * 5;
    return { key: base, list: STOPS.map(function (s, i) { var t = (base + i * 4) % 1440; return [Math.floor(t / 60), t % 60]; }) };
  }
  function hhmm(t) { return (t[0] < 10 ? '0' : '') + t[0] + ':' + (t[1] < 10 ? '0' : '') + t[1]; }
  var depKey = null;
  function renderClocks(force) {
    var row = $('#clocks');
    if (!row) return;
    var dep = departures();
    if (!force && dep.key === depKey) return;
    depKey = dep.key;
    row.innerHTML = STOPS.map(function (s, i) {
      return '<a class="uclock" href="#/' + s.id + '"><span class="plate"><b>' + esc(s.zh) + '</b></span>' + clockSVG(dep.list[i][0], dep.list[i][1]) +
        '<span class="tag">' + hhmm(dep.list[i]) + ' 發車</span></a>';
    }).join('');
  }

  // ------------------------------------------------------------------ facade drawings
  function ap(r, a) { return (100 + Math.cos(a) * r).toFixed(2) + ' ' + (100 - Math.sin(a) * r).toFixed(2); }
  var ARCH = (function () {
    var s = '<svg class="arch-svg" viewBox="0 0 200 100" preserveAspectRatio="none" aria-hidden="true">' +
      '<path d="M14 100 A86 86 0 0 1 186 100 Z" fill="url(#fan)"/>' +
      '<path d="M44 74 L76 28 L84 31 L52 79 Z M62 86 L98 25 L103 27 L68 89 Z" fill="#fff" opacity=".05"/>' +
      '<g class="bars">', a, i;
    for (a = 15; a < 180; a += 15) s += '<line x1="100" y1="100" x2="' + (100 + 86 * Math.cos(a * Math.PI / 180)).toFixed(2) + '" y2="' + (100 - 86 * Math.sin(a * Math.PI / 180)).toFixed(2) + '"/>';
    [31, 59].forEach(function (r) { s += '<path d="M' + (100 - r) + ' 100 A' + r + ' ' + r + ' 0 0 1 ' + (100 + r) + ' 100"/>'; });
    s += '</g><path d="M14 100 A86 86 0 0 1 186 100" class="recess"/>';
    var n = 19, cols = ['#EFDCB2', '#9C4834', '#F2E0B8', '#94432F'];
    for (i = 0; i < n; i++) {
      var a0 = Math.PI - i * Math.PI / n, a1 = Math.PI - (i + 1) * Math.PI / n, key = i === 9, ri = key ? 78 : 86;
      s += '<path d="M' + ap(100, a0) + ' A100 100 0 0 1 ' + ap(100, a1) + ' L' + ap(ri, a1) + ' A' + ri + ' ' + ri + ' 0 0 0 ' + ap(ri, a0) + ' Z" fill="' +
        (key ? '#F7E8C6' : cols[i % 4]) + '" class="vs' + (key ? ' key' : '') + '"/>';
    }
    return s + '<path d="M1.2 100 A98.8 98.8 0 0 1 198.8 100" class="lip"/></svg>';
  })();
  var DOME = (function () {
    var s = '<svg class="dome" viewBox="0 0 240 150" aria-hidden="true">' +
      '<line x1="120" y1="3" x2="120" y2="30" stroke="#4E3A22" stroke-width="1.6"/><circle cx="120" cy="4" r="2.6" fill="url(#cap)"/>' +
      '<path d="M107 46 C107 31 133 31 133 46 Z" fill="url(#verdigris)"/><path d="M107 46 C107 31 133 31 133 46 Z" fill="url(#domeShine)"/>' +
      '<rect x="109" y="46" width="22" height="16" fill="#E9CB8A"/><rect x="112.5" y="49" width="4.4" height="10" rx="2.2" fill="#24362F"/><rect x="123.1" y="49" width="4.4" height="10" rx="2.2" fill="#24362F"/>' +
      '<rect x="106" y="61" width="28" height="3.4" fill="#F4E4BE"/>' +
      '<path d="M57 130 C57 86 88 64 120 62 C152 64 183 86 183 130 Z" fill="url(#verdigris)"/>' +
      '<path d="M57 130 C57 86 88 64 120 62 C152 64 183 86 183 130 Z" fill="#fff" filter="url(#patina)" opacity=".42"/>' +
      '<g class="ribs">';
    for (var k = -3; k <= 3; k++) {
      var bx = 120 + k * 17.5;
      s += '<path d="M' + bx.toFixed(1) + ' 130 Q' + (120 + k * 15.5).toFixed(1) + ' 76 ' + (120 + k * 2.6).toFixed(1) + ' 63"/>';
    }
    s += '</g><path d="M57 130 C57 86 88 64 120 62 C152 64 183 86 183 130 Z" fill="url(#domeShine)"/>' +
      '<rect x="44" y="128" width="152" height="5" fill="#F4E4BE"/><rect x="44" y="133" width="152" height="1.4" fill="#5A3F22" opacity=".45"/>' +
      '<rect x="48" y="134" width="144" height="16" fill="url(#sandPat)"/><rect x="48" y="134" width="144" height="16" fill="#8A5A22" opacity=".12"/>';
    [66, 93, 120, 147, 174].forEach(function (x) { s += '<ellipse cx="' + x + '" cy="142" rx="4.6" ry="5.4" fill="#23352E" stroke="#F4E4BE" stroke-width="1.2"/>'; });
    return s + '</svg>';
  })();

  // ------------------------------------------------------------------ home
  function nowHM() { var d = new Date(); return (d.getHours() < 10 ? '0' : '') + d.getHours() + (d.getMinutes() < 10 ? '0' : '') + d.getMinutes(); }
  function boardClockHTML() {
    var hm = nowHM();
    return '<span class="flaps time" id="boardClock"><span class="sr">' + hm.slice(0, 2) + ':' + hm.slice(2) + '</span><span class="fcs" aria-hidden="true">' +
      cellHTML(hm[0]) + cellHTML(hm[1]) + '<i class="colon"></i>' + cellHTML(hm[2]) + cellHTML(hm[3]) + '</span></span>';
  }
  function renderHome() {
    leaveFeed();
    current = 'home';
    document.title = 'Platform 13｜菜單 Menu';
    depKey = null;
    var h = '<section class="facade"><div class="dome-wrap">' + DOME + '</div><div class="arch">' +
      '<div class="arch-head">' + ARCH + '<div class="tower" id="tower">' + towerSVG() + '</div></div>' +
      '<div class="arch-body"><div class="cornice" aria-hidden="true"></div>' +
      '<div class="plaque"><h1><span class="gilt">Platform</span> <span class="roundel">13</span></h1></div>' +
      '<p class="lede"><span>全店蔬食。</span><span>喝杯咖啡，</span><span>吃點東西，</span><span>不要急，</span><span>活著很好。</span></p>' +
      '<div class="plinth" aria-hidden="true"></div></div></div>' +
      '<div class="under"><div class="under-head"><h2 class="gilt">在時鐘下見</h2><p class="gilt">Meet me under the clocks</p></div>' +
      '<div class="clocks"><div class="track" id="clocks"></div></div></div></section>';
    h += '<section class="board" aria-labelledby="boardTitle"><i class="rail rt"></i><i class="rail rb"></i><i class="rail rl"></i><i class="rail rr"></i>' +
      '<i class="screw s1"></i><i class="screw s2"></i><i class="screw s3"></i><i class="screw s4"></i><div class="board-in">' +
      '<div class="board-top"><h2 id="boardTitle"><span class="gilt">發車看板</span><small class="gilt">Departures</small></h2>' +
      '<div class="now">' + boardClockHTML() + '<small>現在時刻</small></div></div>' +
      '<div class="cols" aria-hidden="true"><span>車次</span><span>開往</span><span>起價</span><span>品項</span></div><ol class="brows">' +
      STOPS.map(function (s) {
        var m = minPrice(s);
        return '<li><a class="brow" href="#/' + s.id + '">' + flaps(s.no, 'no') +
          '<span class="dest"><b>' + esc(s.zh) + '</b><small>' + esc(s.en) + '</small></span>' +
          (s.isCats ? flaps('喵', 'price') : flaps(String(m), 'price')) +
          '<span class="cnt">' + (s.isCats ? s.list.length + ' 隻' : s.items.length + ' 道') + '</span></a></li>';
      }).join('') + '</ol></div></section>';
    h += '<section class="picks"><div class="sec-head"><h2>今日推薦</h2><p>每天換一組</p></div><div class="pick-row">' +
      todaysPicks(6).map(function (x, i) {
        var im = x.it.imgs[0];
        return '<a class="pick" href="#/' + x.cat.id + '/' + x.it.id + '" style="--tilt:' + (i % 2 ? 1.6 : -1.8) + 'deg;--tape:' + (i % 3 - 1) * 4 + 'deg"><span class="pick-ph"><img src="' + src(im.src, true) + '" alt="" loading="lazy" decoding="async"></span>' +
          '<span class="pick-info"><small>' + esc(x.cat.zh) + '</small><b>' + esc(x.it.zh) + '</b><span class="pp">' + pricesHTML(x.it.price) + '</span></span></a>';
      }).join('') + '</div></section>';
    h += '<section class="duty"><div class="sec-head"><h2>本日站務員</h2><a href="#/cats">去看牠們</a></div><div class="duty-row">' +
      D.cats.list.map(function (c) {
        return '<a class="duty-cat" href="#/cats/' + c.id + '" style="--collar:' + c.color + '"><span class="duty-ph"><img src="' + src(c.img, true) + '" alt="店貓' + esc(c.name) + '" loading="lazy"></span><b class="nameplate">' + esc(c.name) + '</b><small>' + esc(c.collar) + '</small></a>';
      }).join('') + '</div></section>';
    h += '<details class="rules ticket"><summary><span class="t-no">No. 0013</span><span class="t-title">乘車須知<span class="t-sub">內用規則 ' + D.shop.rules.length + ' 條</span></span><i class="t-hole" aria-hidden="true"></i>' +
      '<svg class="stamp" viewBox="0 0 100 100" aria-hidden="true"><defs><path id="stampArc" d="M50 50 m-35 0 a35 35 0 1 1 70 0 a35 35 0 1 1 -70 0"/></defs>' +
      '<g filter="url(#distress)"><circle cx="50" cy="50" r="45" fill="none" stroke-width="3"/><circle cx="50" cy="50" r="27" fill="none" stroke-width="1.4"/>' +
      '<text class="arc"><textPath href="#stampArc" startOffset="0">PLATFORM 13 · 喝杯咖啡 · 不要急 ·</textPath></text>' +
      '<text class="mid" x="50" y="58" text-anchor="middle">13</text></g></svg></summary><ol>' +
      D.shop.rules.map(function (r) { return '<li>' + esc(r) + '</li>'; }).join('') + '</ol></details>';
    view.innerHTML = h;
    window.scrollTo(0, 0);
    renderClocks(true);
    if (!flapped && !reduce) runFlaps();
    flapped = true;
  }
  function tick() {
    var box = $('#boardClock');
    if (box) {
      var hm = nowHM(), cells = box.querySelectorAll('.fc');
      for (var i = 0; i < 4; i++) flipTo(cells[i], hm[i]);
      box.querySelector('.sr').textContent = hm.slice(0, 2) + ':' + hm.slice(2);
    }
    updateTower();
    renderClocks(false);
  }
  setInterval(tick, 10000);

  // ------------------------------------------------------------------ feed (a category)
  function slideHTML(it, i, total, cat) {
    var imgs = it.imgs || [];
    var kind = imgs[0] ? imgs[0].kind : 'none';
    var media;
    if (!imgs.length) media = '<div class="media none"><div class="m-ph">' + SLEEPY + '<span>照片準備中</span></div></div>';
    else media = '<div class="media ' + kind + '" data-media>' + imgs.map(function (im, j) {
      return '<img class="m-img' + (j ? '' : ' on') + '" src="' + src(im.src) + '" alt="' + esc(it.zh) + (im.cap ? '：' + esc(im.cap) : '') + '" loading="lazy" decoding="async" data-cap="' + esc(im.cap || '') + '">';
    }).join('') + '</div>';
    var segs = imgs.length > 1 ? '<div class="segs">' + imgs.map(function (_, j) { return '<i' + (j ? '' : ' class="on"') + '></i>'; }).join('') + '</div>' : '';
    return '<section class="slide" id="s-' + it.id + '" data-id="' + it.id + '" data-bg="' + (imgs[0] && kind === 'photo' ? src(imgs[0].src, true) : '') + '">' +
      media + segs + '<div class="shade"></div><div class="info">' +
      '<p class="idx">' + (i < 9 ? '0' : '') + (i + 1) + '<span>/ ' + (total < 10 ? '0' : '') + total + '</span></p>' +
      '<h2>' + esc(it.zh) + '</h2><p class="en">' + esc(it.en) + '</p>' +
      '<div class="pp">' + pricesHTML(it.price) + '</div>' + tagsHTML(it.tags) +
      '<p class="cap">' + esc((imgs[0] && imgs[0].cap) || '') + '</p>' +
      '<div class="acts"><button class="more" type="button" data-info="' + it.id + '">詳細與加點</button>' +
      (kind === 'illust' ? '<span class="badge">插畫示意</span>' : '') + (imgs.length > 1 ? '<span class="hint">點照片看下一張</span>' : '') + '</div></div></section>';
  }
  function catSlideHTML(c, i, total) {
    return '<section class="slide cat" id="s-' + c.id + '" data-id="' + c.id + '" data-bg="' + src(c.img, true) + '" style="--collar:' + c.color + '">' +
      '<div class="media photo"><img class="m-img on" src="' + src(c.img) + '" alt="店貓' + esc(c.name) + '" loading="lazy" decoding="async"></div>' +
      '<div class="shade"></div><div class="info"><p class="idx">' + (i < 9 ? '0' : '') + (i + 1) + '<span>/ 0' + total + '</span></p>' +
      '<h2 class="cat-name">' + esc(c.name) + '</h2><p class="collar"><i></i>' + esc(c.collar) + '</p><p class="says">「' + esc(c.line) + '」</p></div></section>';
  }
  function addonsHTML(a) {
    var h = '<div class="addons"><h3>' + esc(a.zh) + '<small>' + esc(a.en) + '</small>' + (a.price ? '<em>' + esc(a.price) + '</em>' : '') + '</h3>';
    var list = a.items || a.list;
    if (list) h += '<ul>' + list.map(function (x) { return '<li><span><b>' + esc(x.zh) + '</b><small>' + esc(x.en) + '</small></span><em>' + esc(x.price) + '</em></li>'; }).join('') + '</ul>';
    if (a.lines) h += '<p class="meal">含' + a.lines.map(esc).join('、') + '</p>';
    if (a.foot) h += '<p class="meal-foot">' + esc(a.foot) + '</p>';
    return h + '</div>';
  }
  function endSlideHTML(stop) {
    var nx = STOPS[(stop.index + 1) % STOPS.length], c = cover(nx);
    var h = '<section class="slide end" data-id="__end"><div class="end-in">';
    if (stop.isCats) h += '<p class="wisdom">' + D.shop.quote.map(esc).join('<br>') + '<small>小貓咪的智慧要聽</small></p>';
    else {
      if (stop.note) h += '<p class="note">' + esc(stop.note) + '</p>';
      if (stop.addons) h += addonsHTML(stop.addons);
    }
    h += '<a class="next-train" href="#/' + nx.id + '">' + (c ? '<img src="' + src(c, true) + '" alt="" loading="lazy">' : '') +
      '<span><small>下一班</small><b>' + esc(nx.zh) + '</b><em>' + esc(nx.en.toUpperCase()) + '</em></span></a>' +
      '<a class="to-board" href="#/">回到看板</a></div></section>';
    return h;
  }
  function listHTML(stop) {
    if (stop.isCats) return '';
    return '<div class="list" id="list">' + (stop.note ? '<p class="note">' + esc(stop.note) + '</p>' : '') + stop.items.map(function (it) {
      var im = it.imgs && it.imgs[0];
      return '<button class="lrow" type="button" data-jump="' + it.id + '"><span class="lt">' + (im ? '<img src="' + src(im.src, true) + '" alt="" loading="lazy">' : SLEEPY) + '</span>' +
        '<span class="ln"><b>' + esc(it.zh) + '</b><small>' + esc(it.en) + '</small>' + tagsHTML(it.tags) + '</span><span class="lp">' + pricesHTML(it.price) + '</span></button>';
    }).join('') + (stop.addons ? addonsHTML(stop.addons) : '') + '</div>';
  }

  function renderFeed(stop, focusId, dir) {
    current = stop.id;
    document.title = stop.zh + '｜Platform 13';
    document.body.classList.add('immersive');
    var list = stop.isCats ? stop.list : stop.items;
    var mode = stop.isCats ? 'feed' : (store('p13c-mode') || 'feed');
    view.innerHTML = '<div class="feed-wrap' + (mode === 'list' ? ' is-list' : '') + (dir ? ' enter' + (dir < 0 ? ' from-left' : '') : '') + '" id="feedWrap">' +
      '<div class="feed-top"><a class="back" href="#/" aria-label="回到看板"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5 8 12l7 7"/></svg>看板</a>' +
      '<div class="feed-title"><b>' + esc(stop.zh) + '</b><small>' + esc(stop.en.toUpperCase()) + '</small></div>' +
      (stop.isCats ? '<span></span>' : '<button class="mode" type="button" data-mode aria-pressed="' + (mode === 'list') + '">' + (mode === 'list' ? '大圖' : '清單') + '</button>') + '</div>' +
      '<div class="feed" id="feed" tabindex="-1">' + list.map(function (x, i) { return stop.isCats ? catSlideHTML(x, i, list.length) : slideHTML(x, i, list.length, stop); }).join('') + endSlideHTML(stop) + '</div>' +
      listHTML(stop) +
      '<div class="pager" aria-hidden="true"><button type="button" data-cat="-1" tabindex="-1">‹</button><button type="button" data-cat="1" tabindex="-1">›</button></div></div>';
    var feed = $('#feed');
    if (focusId && document.getElementById('s-' + focusId)) feed.scrollTop = document.getElementById('s-' + focusId).offsetTop;
    feed.focus({ preventScroll: true });
    if (observer) observer.disconnect();
    observer = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) { if (e.isIntersecting) setAmbient(e.target.getAttribute('data-bg')); });
    }, { root: feed, threshold: 0.6 });
    Array.prototype.forEach.call(feed.children, function (s) { observer.observe(s); });
    setAmbient((feed.children[0] && feed.children[0].getAttribute('data-bg')) || '');
  }
  function setAmbient(u) { ambient.style.backgroundImage = u ? 'url("' + u + '")' : 'none'; }
  function leaveFeed() {
    document.body.classList.remove('immersive');
    if (observer) { observer.disconnect(); observer = null; }
    setAmbient('');
  }
  function scrollToItem(id) {
    var s = document.getElementById('s-' + id), feed = $('#feed');
    if (s && feed) feed.scrollTop = s.offsetTop;
  }
  function changeCat(d) {
    var s = byId[current];
    if (!s) return;
    go('#/' + STOPS[(s.index + d + STOPS.length) % STOPS.length].id);
  }

  // ------------------------------------------------------------------ item sheet
  function showSheet(id) {
    var x = itemById[id];
    if (!x) return;
    var it = x.it, cat = x.cat, imgs = it.imgs || [];
    var notes = [];
    if (it.extra) notes.push(['加點', it.extra]);
    if (it.flavour) notes.push(['加風味：焦糖、香草或榛果', '+20']);
    if (cat.note) notes.push([cat.note, '']);
    if (cat.id === 'waffle') notes.push(['加冰淇淋', '+25／球']);
    if (cat.id === 'coffee' && it.price && typeof it.price === 'object') notes.push(['加一份濃縮', '+30']);
    if (cat.id === 'main') notes.push(['升級套餐：薯條或生菜沙拉、甜點、紅茶或黑咖啡', '+140']);
    var kinds = imgs.map(function (im) { return im.kind; });
    var kindNote = !imgs.length ? '這道還沒有照片，之後會補上。' : (kinds.indexOf('illust') >= 0 ? '圖為插畫示意，實際餐點以現場為準。' : '照片為店內實拍，擺盤以現場為準。');
    sheet.innerHTML = '<button class="sheet-close" type="button" data-close aria-label="關閉"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
      '<div class="grab" aria-hidden="true"></div><div class="sheet-body"><p class="sheet-cat">' + esc(cat.zh) + '</p><h2 id="sheetTitle">' + esc(it.zh) + '</h2><p class="sheet-en">' + esc(it.en) + '</p>' +
      '<div class="pp">' + pricesHTML(it.price) + '</div>' + tagsHTML(it.tags) +
      (imgs.length ? '<div class="thumbs">' + imgs.map(function (im) { return '<figure><img src="' + src(im.src, true) + '" alt="" loading="lazy">' + (im.cap ? '<figcaption>' + esc(im.cap) + '</figcaption>' : '') + '</figure>'; }).join('') + '</div>' : '') +
      (notes.length ? '<ul class="notes">' + notes.map(function (n) { return '<li><span>' + esc(n[0]) + '</span><span>' + esc(n[1]) + '</span></li>'; }).join('') + '</ul>' : '') +
      '<p class="kind">' + kindNote + '</p></div>';
    if (sheetWrap.hidden) { lastFocus = document.activeElement; sheetWrap.hidden = false; }
    sheet.scrollTop = 0;
    sheet.focus({ preventScroll: true });
  }
  function hideSheet() {
    if (sheetWrap.hidden) return;
    sheetWrap.hidden = true;
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }
  function closeSheet() {
    if (pushedSheet) { pushedSheet = false; history.back(); return; }
    var parts = location.hash.replace(/^#\/?/, '').split('/');
    location.replace('#/' + parts[0] + '/' + parts[1]);
  }

  // ------------------------------------------------------------------ search
  var HINTS = ['拿鐵', '鬆餅', '無咖啡因', '冰', '可頌', '沙拉', '氣泡', '千層麵'];
  var INDEX = ITEMS.map(function (x) {
    var p = x.it.price, extra = [];
    if (p && typeof p === 'object') { if (p.ice != null) extra.push('冰 冰飲 iced'); if (p.hot != null) extra.push('熱 熱飲 hot'); }
    (x.it.tags || []).forEach(function (t) { extra.push(TAG[t]); });
    return (x.it.zh + ' ' + x.it.en + ' ' + x.cat.zh + ' ' + x.cat.en + ' ' + extra.join(' ')).toLowerCase();
  });
  $('#searchHints').innerHTML = HINTS.map(function (h) { return '<button type="button" data-hint="' + h + '">' + h + '</button>'; }).join('');
  function runSearch() {
    var q = searchInput.value.trim().toLowerCase(), box = $('#searchResults');
    if (!q) { box.innerHTML = '<p class="empty">輸入餐點或飲品名稱，中英文都可以。</p>'; return; }
    var terms = q.split(/\s+/).filter(Boolean);
    var hits = ITEMS.filter(function (x, i) { return terms.every(function (t) { return INDEX[i].indexOf(t) >= 0; }); });
    if (!hits.length) { box.innerHTML = '<p class="empty">找不到「' + esc(searchInput.value.trim()) + '」。試試「拿鐵」「鬆餅」或「無咖啡因」。</p>'; return; }
    var groups = {};
    hits.forEach(function (x) { (groups[x.cat.id] = groups[x.cat.id] || []).push(x); });
    box.innerHTML = Object.keys(groups).map(function (cid) {
      var cat = byId[cid];
      return '<div class="rgroup"><h3><span>' + cat.no + '</span>' + esc(cat.zh) + '</h3>' + groups[cid].map(function (x) {
        var im = x.it.imgs && x.it.imgs[0];
        return '<button class="lrow" type="button" data-go="#/' + cid + '/' + x.it.id + '"><span class="lt">' + (im ? '<img src="' + src(im.src, true) + '" alt="" loading="lazy">' : SLEEPY) + '</span>' +
          '<span class="ln"><b>' + esc(x.it.zh) + '</b><small>' + esc(x.it.en) + '</small></span><span class="lp">' + pricesHTML(x.it.price) + '</span></button>';
      }).join('') + '</div>';
    }).join('');
  }
  function showSearch() {
    if (!searchWrap.hidden) return;
    searchWrap.hidden = false;
    document.body.classList.add('locked');
    runSearch();
    setTimeout(function () { searchInput.focus(); }, 30);
  }
  function hideSearch() {
    if (searchWrap.hidden) return;
    searchWrap.hidden = true;
    document.body.classList.remove('locked');
  }
  function closeSearch() { if (pushedSearch) { pushedSearch = false; history.back(); } else location.replace('#/'); }
  searchInput.addEventListener('input', runSearch);
  searchInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { var b = $('#searchResults .lrow'); if (b) b.click(); } });

  // ------------------------------------------------------------------ routing
  function route() {
    var parts = decodeURIComponent(location.hash.replace(/^#\/?/, '')).split('/').filter(Boolean);
    if (parts[0] === 'search') { hideSheet(); if (!current) renderHome(); showSearch(); return; }
    hideSearch();
    var stop = parts[0] && byId[parts[0]];
    if (!stop) { hideSheet(); if (current !== 'home') renderHome(); return; }
    if (current !== stop.id) {
      var prev = byId[current], dir = prev ? (stop.index > prev.index ? 1 : -1) : 0;
      if (prev && Math.abs(stop.index - prev.index) === STOPS.length - 1) dir = -dir;
      renderFeed(stop, parts[1], dir);
    } else if (parts[1] && !parts[2]) scrollToItem(parts[1]);
    if (parts[1] && parts[2] === 'info' && itemById[parts[1]]) showSheet(parts[1]); else hideSheet();
  }
  window.addEventListener('hashchange', route);

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-info],[data-close],[data-go],[data-hint],[data-mode],[data-jump],[data-cat],[data-media],#openSearch,#closeSearch');
    if (!t) return;
    if (t.dataset.info) { pushedSheet = true; go('#/' + current + '/' + t.dataset.info + '/info'); return; }
    if (t.hasAttribute('data-close')) { closeSheet(); return; }
    if (t.id === 'openSearch') { pushedSearch = true; go('#/search'); return; }
    if (t.id === 'closeSearch') { closeSearch(); return; }
    if (t.dataset.go) { go(t.dataset.go); return; }
    if (t.dataset.hint) { searchInput.value = t.dataset.hint; runSearch(); searchInput.focus(); return; }
    if (t.hasAttribute('data-mode')) {
      var wrap = $('#feedWrap'), list = !wrap.classList.contains('is-list');
      wrap.classList.toggle('is-list', list);
      t.textContent = list ? '大圖' : '清單';
      t.setAttribute('aria-pressed', list);
      store('p13c-mode', list ? 'list' : 'feed');
      return;
    }
    if (t.dataset.jump) {
      $('#feedWrap').classList.remove('is-list');
      var m = $('[data-mode]'); if (m) { m.textContent = '清單'; m.setAttribute('aria-pressed', 'false'); }
      store('p13c-mode', 'feed');
      scrollToItem(t.dataset.jump);
      return;
    }
    if (t.dataset.cat) { changeCat(+t.dataset.cat); return; }
    if (t.hasAttribute('data-media')) {
      var imgs = t.querySelectorAll('.m-img');
      if (imgs.length < 2) return;
      var cur = Array.prototype.findIndex.call(imgs, function (im) { return im.classList.contains('on'); });
      var r = t.getBoundingClientRect(), nxt = (e.clientX - r.left) < r.width * 0.35 ? cur - 1 : cur + 1;
      nxt = (nxt + imgs.length) % imgs.length;
      imgs[cur].classList.remove('on'); imgs[nxt].classList.add('on');
      var slide = t.closest('.slide');
      Array.prototype.forEach.call(slide.querySelectorAll('.segs i'), function (s, j) { s.classList.toggle('on', j === nxt); });
      slide.querySelector('.cap').textContent = imgs[nxt].getAttribute('data-cap');
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { if (!searchWrap.hidden) closeSearch(); else if (!sheetWrap.hidden) closeSheet(); else if (byId[current]) go('#/'); return; }
    if (!sheetWrap.hidden || !searchWrap.hidden || !byId[current]) return;
    if (e.key === 'ArrowRight') changeCat(1);
    if (e.key === 'ArrowLeft') changeCat(-1);
  });

  // horizontal swipe in the feed changes category
  var sx = 0, sy = 0, st = 0, track = false;
  view.addEventListener('touchstart', function (e) {
    if (!byId[current] || e.touches.length > 1) { track = false; return; }
    sx = e.touches[0].clientX; sy = e.touches[0].clientY; st = Date.now(); track = true;
  }, { passive: true });
  view.addEventListener('touchend', function (e) {
    if (!track) return;
    track = false;
    var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
    if (Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 1.7 && Date.now() - st < 800) changeCat(dx < 0 ? 1 : -1);
  }, { passive: true });

  $('#footQuote').innerHTML = D.shop.quote.map(function (q) { return '<span>' + esc(q) + '</span>'; }).join('') + '<small>小貓咪的智慧要聽</small>';
  route();
})();
