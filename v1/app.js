/* Platform 13 menu app — hash routes:
 *   #/                 overview (the line of stops)
 *   #/<stop>           a category (stop), e.g. #/coffee
 *   #/<stop>/<item>    the same with an item sheet open
 *   #/search           search overlay
 */
(function () {
  'use strict';
  var D = window.P13;
  var CATS = D.categories;
  var STOPS = CATS.map(function (c, i) { return Object.assign({}, c, { no: pad(i + 1) }); });
  STOPS.push(Object.assign({}, D.cats, { no: pad(CATS.length + 1), isCats: true }));
  var stopById = {};
  STOPS.forEach(function (s, i) { s.index = i; stopById[s.id] = s; });
  var ITEMS = [];
  CATS.forEach(function (c) { c.items.forEach(function (it) { ITEMS.push({ it: it, cat: stopById[c.id] }); }); });
  var itemById = {};
  ITEMS.forEach(function (x) { itemById[x.it.id] = x; });

  var TAG = { decaf: '無咖啡因', season: '季節限定', pot: '熱飲一壺' };
  var ICON = {
    plate: '<svg viewBox="0 0 48 48" aria-hidden="true"><ellipse cx="25" cy="31" rx="15" ry="7"/><ellipse cx="25" cy="30.5" rx="8.5" ry="3.6"/><path d="M5 12v7c0 2 1.2 3 3 3s3-1 3-3v-7M8 22v16M43 12c-3 1.5-4.5 5.5-4.5 10h4.5v16"/></svg>',
    cup: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M9 22h24v4a12 12 0 0 1-24 0z"/><path d="M33 24h3a4 4 0 0 1 0 8h-4"/><path d="M5 40h33"/><path d="M17 9c-2 2 2 4 0 7M24 7c-2 2 2 4 0 8"/></svg>',
    glass: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M13 14h22l-3 28H16z"/><path d="M15 23h18"/><path d="M28 14 33 4"/><circle cx="21" cy="30" r="1.4"/><circle cx="26" cy="35" r="1.2"/></svg>',
    cone: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M14 20h20L24 44z"/><path d="M14 20a10 9 0 0 1 20 0"/><path d="M18 26l8 8M22 22l9 9M17 30l5 5"/></svg>'
  };
  var ICON_OF = { light: 'plate', main: 'plate', tortilla: 'plate', waffle: 'plate', dessert: 'plate', cone: 'cone', coffee: 'cup', tea: 'cup', sparkling: 'glass' };

  var $ = function (s, el) { return (el || document).querySelector(s); };
  var view = $('#view');
  var stopsNav = $('#stops');
  var sheetWrap = $('#sheetWrap');
  var sheet = $('#sheet');
  var searchWrap = $('#searchWrap');
  var searchInput = $('#searchInput');
  var current = null;          // id of the rendered view ('home' or a stop id)
  var sheetItem = null;        // open item id
  var pushedSheet = false;     // the sheet was opened by a click in this session
  var pushedSearch = false;
  var lastFocus = null;

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function src(s, small) { return '../assets/img/' + s + (small ? '-sm' : '') + '.webp'; }
  function go(hash) { if (location.hash !== hash) location.hash = hash; }

  // ------------------------------------------------------------------ pieces
  function priceHTML(p, cls) {
    cls = cls || 'price';
    if (typeof p === 'number') return '<span class="' + cls + '">' + p + '</span>';
    if (typeof p === 'string') return '<span class="' + cls + ' text">' + esc(p) + '</span>';
    return ['hot', 'ice'].filter(function (k) { return p[k] != null; }).map(function (k) {
      return '<span class="' + cls + '"><small>' + (k === 'hot' ? '熱' : '冰') + '</small>' + p[k] + '</span>';
    }).join('');
  }
  function tagsHTML(tags) {
    if (!tags || !tags.length) return '';
    return '<span class="tags">' + tags.map(function (t) { return '<span class="tag ' + t + '">' + TAG[t] + '</span>'; }).join('') + '</span>';
  }
  function placeholder(catId, label) {
    var text = label === '' ? '' : (label || '照片準備中');
    return '<div class="placeholder">' + ICON[ICON_OF[catId] || 'plate'] + (text ? '<span>' + text + '</span>' : '') + '</div>';
  }
  function thumbHTML(x) {
    var im = x.it.imgs && x.it.imgs[0];
    if (!im) return '<div class="thumb">' + placeholder(x.cat.id) + '</div>';
    return '<div class="thumb"><img src="' + src(im.src, true) + '" alt="" loading="lazy" decoding="async">' +
      (im.kind === 'illust' ? '<span class="badge">插畫示意</span>' : '') + '</div>';
  }
  function sign(o) {
    var prev = o.prev, next = o.next;
    function end(p, cls) {
      if (!p) return '<span></span>';
      var inner = '<b>' + esc(p.zh) + '</b><small>' + esc(p.en) + '</small>';
      return p.href ? '<a class="' + cls + '" href="' + p.href + '" aria-label="' + (cls === 'prev' ? '上一站：' : '下一站：') + esc(p.zh) + '">' + inner + '</a>'
                    : '<span class="' + cls + '">' + inner + '</span>';
    }
    var long = o.latin ? ' latin' : (o.name.length > 3 ? ' long' : '');
    return '<div class="sign">' +
      '<div class="sign-no" aria-hidden="true"><small>' + esc(o.top || 'P13') + '</small><b>' + esc(o.no) + '</b></div>' +
      '<h1 class="sign-name' + long + '">' + esc(o.name) + '</h1>' +
      '<p class="sign-en">' + esc(o.en) + '</p>' +
      '<div class="sign-band"></div>' +
      '<div class="sign-next">' + end(prev, 'prev') + end(next, 'next') + '</div></div>';
  }
  function neighbour(stop, d) {
    var s = STOPS[(stop.index + d + STOPS.length) % STOPS.length];
    return { zh: s.zh, en: s.en, href: '#/' + s.id };
  }
  function count(stop) {
    if (stop.isCats) return stop.list.length + ' 隻';
    return stop.items.length + ' 品項';
  }
  function cover(stop) {
    if (stop.cover) return '<img src="' + src(stop.cover, true) + '" alt="" loading="lazy" decoding="async">';
    return '<div class="stripes"><span>' + esc(stop.zh) + '</span></div>';
  }

  // ------------------------------------------------------------------ views
  function renderHome() {
    current = 'home';
    document.title = 'Platform 13｜菜單 Menu';
    stopsNav.hidden = true;
    document.documentElement.style.setProperty('--stops', '0px');
    var h = '';
    h += '<section class="hero">' +
      sign({ top: 'P', no: '13', name: 'Platform 13', en: '菜單 Menu', latin: true,
             prev: { zh: '喝杯咖啡', en: 'Coffee', href: '#/coffee' }, next: { zh: '吃點東西', en: 'Light Meal', href: '#/light' } }) +
      '<button class="search-open" type="button" data-search>' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>' +
      '搜尋餐點或飲品</button></section>';
    h += '<div class="section-head"><h2>選一站下車</h2><p>左右滑動看全部</p></div>';
    h += '<div class="line" id="line"><div class="line-track" aria-hidden="true"></div>' + STOPS.map(function (s) {
      return '<a class="station" href="#/' + s.id + '"><div class="station-card"><div class="station-img">' + cover(s) + '</div>' +
        '<div class="station-body"><span class="station-no">13-' + s.no + '</span><span class="station-name">' + esc(s.zh) + '</span>' +
        '<span class="station-meta">' + esc(s.en) + ' <span>· ' + count(s) + '</span></span></div></div></a>';
    }).join('') + '</div>';
    h += '<section class="pick"><img src="' + src('photos/cat-kiki', true) + '" alt="店貓 KIKI 躺在地板上" loading="lazy">' +
      '<div><h3>選不出來嗎？</h3><p>讓店貓 KIKI 幫你點一道。</p><button class="btn" type="button" data-random><span class="paw" aria-hidden="true">🐾</span>隨機推薦</button></div></section>';
    h += '<section class="notice" aria-labelledby="rulesTitle"><h2 id="rulesTitle">月台須知</h2><ol>' +
      D.shop.rules.map(function (r) { return '<li>' + esc(r) + '</li>'; }).join('') + '</ol></section>';
    swap(h, 0);
    layoutLine();
  }

  function renderStop(stop, dir) {
    current = stop.id;
    document.title = stop.zh + '｜Platform 13';
    renderStopsNav(stop);
    var h = sign({ no: '13-' + stop.no, top: 'STOP', name: stop.zh, en: stop.en, prev: neighbour(stop, -1), next: neighbour(stop, 1) });
    if (stop.isCats) {
      h += renderCats(stop);
    } else {
      if (stop.note) h += '<div class="cat-note"><span class="ticket">' + esc(stop.note) + '</span></div>';
      h += '<div class="grid">' + stop.items.map(function (it) {
        var x = itemById[it.id];
        return '<button class="item" type="button" data-item="' + it.id + '">' + thumbHTML(x) +
          '<span class="item-body"><span class="item-zh">' + esc(it.zh) + '</span><span class="item-en">' + esc(it.en) + '</span>' +
          '<span class="item-foot">' + priceHTML(it.price) + tagsHTML(it.tags) + '</span></span></button>';
      }).join('') + '</div>';
      if (stop.addons) h += addonsHTML(stop.addons);
    }
    var nx = STOPS[(stop.index + 1) % STOPS.length];
    h += '<p class="swipe-hint">左右滑動可以換站</p>';
    h += '<div class="next-stop"><a class="btn ghost" href="#/' + nx.id + '">下一站：' + esc(nx.zh) + '</a></div>';
    swap(h, dir || 0);
  }

  function addonsHTML(a) {
    var h = '<section class="addons"><h3><span>' + esc(a.zh) + ' <small>' + esc(a.en) + '</small></span>' + (a.price ? priceHTML(a.price) : '') + '</h3>';
    if (a.items) {
      h += '<ul>' + a.items.map(function (x) {
        return '<li' + (x.img ? '' : ' class="noimg"') + '>' + (x.img ? '<img src="' + src(x.img, true) + '" alt="" loading="lazy">' : '') +
          '<span><b>' + esc(x.zh) + '</b><small>' + esc(x.en) + '</small></span>' + priceHTML(x.price) + '</li>';
      }).join('') + '</ul>';
    }
    if (a.list) {
      h += '<ul>' + a.list.map(function (x) {
        return '<li class="noimg"><span><b>' + esc(x.zh) + '</b><small>' + esc(x.en) + '</small></span>' + priceHTML(x.price) + '</li>';
      }).join('') + '</ul>';
    }
    if (a.lines) h += '<p class="meal">含' + a.lines.map(esc).join('、') + '</p><p class="meal-en">' + esc(a.linesEn) + '</p>';
    if (a.foot) h += '<p class="foot">' + esc(a.foot) + '</p>';
    return h + '</section>';
  }

  function renderCats(stop) {
    var h = '<div class="cats">' + stop.list.map(function (c) {
      return '<article class="cat-card"><div class="ph"><img src="' + src(c.img) + '" alt="店貓' + esc(c.name) + '" loading="lazy" decoding="async"></div>' +
        '<div class="cat-body"><div class="cat-name">' + esc(c.name) + '<span class="collar"><i style="background:' + c.color + '"></i>' + esc(c.collar) + '</span></div>' +
        '<p class="bubble">' + esc(c.line) + '</p></div>' +
        (c.more ? '<div class="cat-more"><img src="' + src(c.more, true) + '" alt="' + esc(c.name) + '的另一張照片" loading="lazy"><img src="' + src(stop.duo, true) + '" alt="KIKI 和咪嚕一起躺著" loading="lazy"></div>' : '') +
        '</article>';
    }).join('') + '</div>';
    h += '<section class="wisdom"><p>' + D.shop.quote.map(esc).join('<br>') + '</p><small>' + esc(D.shop.quoteBy) + '</small></section>';
    return h;
  }

  function renderStopsNav(stop) {
    if (stopsNav.hidden || !stopsNav.childElementCount) {
      stopsNav.innerHTML = STOPS.map(function (s) {
        return '<a class="stop" href="#/' + s.id + '" data-stop="' + s.id + '"><span class="no">' + s.no + '</span>' + esc(s.zh) + '</a>';
      }).join('');
      stopsNav.hidden = false;
    }
    Array.prototype.forEach.call(stopsNav.children, function (a) {
      if (a.dataset.stop === stop.id) {
        a.setAttribute('aria-current', 'page');
        var l = a.offsetLeft - (stopsNav.clientWidth - a.offsetWidth) / 2;
        stopsNav.scrollTo({ left: l, behavior: 'smooth' });
      } else a.removeAttribute('aria-current');
    });
    document.documentElement.style.setProperty('--stops', stopsNav.offsetHeight + 'px');
  }

  function swap(html, dir) {
    view.innerHTML = html;
    view.classList.remove('view-enter', 'from-left');
    void view.offsetWidth;
    if (dir) view.classList.add('view-enter', dir < 0 ? 'from-left' : 'from-right');
    window.scrollTo(0, 0);
  }

  function layoutLine() {
    var line = $('#line');
    if (!line) return;
    var cards = line.querySelectorAll('.station');
    var track = line.querySelector('.line-track');
    if (!cards.length) return;
    var first = cards[0], last = cards[cards.length - 1];
    track.style.left = (first.offsetLeft + 30) + 'px';
    track.style.width = (last.offsetLeft - first.offsetLeft) + 'px';
  }
  window.addEventListener('resize', layoutLine);

  // ------------------------------------------------------------------ item sheet
  function showSheet(id) {
    var x = itemById[id];
    if (!x) return;
    var it = x.it, cat = x.cat;
    sheetItem = id;
    var imgs = it.imgs && it.imgs.length ? it.imgs : [null];
    var slides = imgs.map(function (im, i) {
      if (!im) return '<div class="slide"><div class="frame">' + placeholder(cat.id, '照片準備中，先看文字吧') + '</div></div>';
      return '<div class="slide"><div class="frame ' + im.kind + '"><img src="' + src(im.src) + '" alt="' + esc(it.zh) + (im.cap ? '：' + esc(im.cap) : '') + '" decoding="async"' + (i ? ' loading="lazy"' : '') + '></div></div>';
    }).join('');
    var notes = [];
    if (it.extra) notes.push(['加點', it.extra]);
    if (it.flavour) notes.push(['加風味：焦糖、香草或榛果', '+20']);
    if (cat.note) notes.push([cat.note, '']);
    if (cat.id === 'waffle') notes.push(['加冰淇淋', '+25／球']);
    if (cat.id === 'coffee' && it.price && typeof it.price === 'object') notes.push(['加一份濃縮', '+30']);
    if (cat.id === 'main') notes.push(['升級套餐：薯條或生菜沙拉、甜點、紅茶或黑咖啡', '+140']);
    var prices = '';
    if (typeof it.price === 'number') prices = '<span class="pp"><b>' + it.price + '</b><small>元</small></span>';
    else if (typeof it.price === 'string') prices = '<span class="pp text"><b>' + esc(it.price) + '</b></span>';
    else prices = ['hot', 'ice'].filter(function (k) { return it.price[k] != null; }).map(function (k) {
      return '<span class="pp ' + k + '"><small>' + (k === 'hot' ? '熱' : '冰') + '</small><b>' + it.price[k] + '</b></span>';
    }).join('');
    var kinds = imgs.map(function (im) { return im ? im.kind : 'none'; });
    var kindNote = kinds.indexOf('illust') >= 0 ? '圖為插畫示意，實際餐點以現場為準。' :
      (kinds.indexOf('none') >= 0 ? '這道還沒有照片，之後會補上。' : '照片為店內實拍，擺盤以現場為準。');
    var list = cat.items, idx = list.findIndex(function (z) { return z.id === id; });
    var pv = list[idx - 1], nx = list[idx + 1];
    sheet.innerHTML =
      '<button class="sheet-close" type="button" data-close aria-label="關閉"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
      '<div class="grab" aria-hidden="true"></div>' +
      '<div class="gallery" id="gallery">' + slides + '</div>' +
      (imgs.length > 1 ? '<div class="dots" id="dots">' + imgs.map(function (_, i) { return '<button type="button" aria-label="第 ' + (i + 1) + ' 張" data-dot="' + i + '"' + (i ? '' : ' aria-current="true"') + '></button>'; }).join('') + '</div>' : '') +
      '<p class="cap" id="cap">' + esc((imgs[0] && imgs[0].cap) || '') + '</p>' +
      '<div class="sheet-body"><h2 id="sheetTitle">' + esc(it.zh) + '</h2><p class="sheet-en">' + esc(it.en) + '</p>' +
      '<div class="sheet-price">' + prices + '</div>' +
      (it.tags ? '<div class="sheet-tags">' + tagsHTML(it.tags) + '</div>' : '') +
      (notes.length ? '<ul class="sheet-notes">' + notes.map(function (n) { return '<li><span>' + esc(n[0]) + '</span><span>' + esc(n[1]) + '</span></li>'; }).join('') + '</ul>' : '') +
      '<p class="sheet-kind">' + kindNote + '</p>' +
      '<div class="sheet-nav">' +
      (pv ? '<a class="btn ghost" href="#/' + cat.id + '/' + pv.id + '" data-replace><span>◀ ' + esc(pv.zh) + '</span></a>' : '<span></span>') +
      (nx ? '<a class="btn ghost" href="#/' + cat.id + '/' + nx.id + '" data-replace><span>' + esc(nx.zh) + ' ▶</span></a>' : '<span></span>') +
      '</div></div>';
    if (sheetWrap.hidden) {
      lastFocus = document.activeElement;
      sheetWrap.hidden = false;
      document.body.classList.add('locked');
    }
    sheet.scrollTop = 0;
    sheet.focus({ preventScroll: true });
    var gal = $('#gallery');
    gal.addEventListener('scroll', function () {
      var i = Math.round(gal.scrollLeft / gal.clientWidth);
      var im = imgs[i];
      $('#cap').textContent = (im && im.cap) || '';
      var dots = $('#dots');
      if (dots) Array.prototype.forEach.call(dots.children, function (b, j) { b.setAttribute('aria-current', j === i ? 'true' : 'false'); });
    }, { passive: true });
  }
  function hideSheet() {
    if (sheetWrap.hidden) return;
    sheetWrap.hidden = true;
    sheetItem = null;
    document.body.classList.remove('locked');
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }
  function closeSheet() {
    var x = itemById[sheetItem];
    if (pushedSheet) { pushedSheet = false; history.back(); }
    else if (x) location.replace('#/' + x.cat.id);
    else hideSheet();
  }

  // ------------------------------------------------------------------ search
  var HINTS = ['拿鐵', '鬆餅', '無咖啡因', '冰飲', '可頌', '沙拉', '氣泡', '季節限定'];
  var INDEX = ITEMS.map(function (x) {
    var p = x.it.price, extra = [];
    if (p && typeof p === 'object') { if (p.ice != null) extra.push('冰 冰飲 iced'); if (p.hot != null) extra.push('熱 熱飲 hot'); }
    (x.it.tags || []).forEach(function (t) { extra.push(TAG[t]); });
    return (x.it.zh + ' ' + x.it.en + ' ' + x.cat.zh + ' ' + x.cat.en + ' ' + extra.join(' ')).toLowerCase();
  });
  $('#searchHints').innerHTML = HINTS.map(function (h) { return '<button type="button" data-hint="' + h + '">' + h + '</button>'; }).join('');

  function runSearch() {
    var q = searchInput.value.trim().toLowerCase();
    var box = $('#searchResults');
    if (!q) { box.innerHTML = '<p class="empty">輸入餐點或飲品名稱，中英文都可以。</p>'; return; }
    var terms = q.replace(/飲$/, '').split(/\s+/).filter(Boolean);
    var hits = ITEMS.filter(function (x, i) { return terms.every(function (t) { return INDEX[i].indexOf(t) >= 0; }); });
    if (!hits.length) {
      box.innerHTML = '<p class="empty">找不到「' + esc(searchInput.value.trim()) + '」。試試「拿鐵」「鬆餅」或「無咖啡因」。</p>';
      return;
    }
    var groups = {};
    hits.forEach(function (x) { (groups[x.cat.id] = groups[x.cat.id] || []).push(x); });
    box.innerHTML = Object.keys(groups).map(function (cid) {
      var cat = stopById[cid];
      return '<div class="result-group"><h3>13-' + cat.no + ' ' + esc(cat.zh) + '</h3>' + groups[cid].map(function (x) {
        var im = x.it.imgs && x.it.imgs[0];
        return '<button class="result" type="button" data-go="#/' + cid + '/' + x.it.id + '"><span class="rt">' +
          (im ? '<img src="' + src(im.src, true) + '" alt="" loading="lazy">' : placeholder(cid, '')) + '</span>' +
          '<span><b>' + mark(x.it.zh, terms) + '</b><small>' + esc(x.it.en) + '</small></span><span class="rp">' + priceHTML(x.it.price, 'p') + '</span></button>';
      }).join('') + '</div>';
    }).join('');
  }
  function mark(s, terms) {
    var out = esc(s);
    terms.forEach(function (t) {
      if (!t) return;
      var i = s.toLowerCase().indexOf(t);
      if (i >= 0) out = esc(s.slice(0, i)) + '<mark>' + esc(s.slice(i, i + t.length)) + '</mark>' + esc(s.slice(i + t.length));
    });
    return out;
  }
  function showSearch() {
    if (!searchWrap.hidden) return;
    lastFocus = document.activeElement;
    searchWrap.hidden = false;
    document.body.classList.add('locked');
    runSearch();
    setTimeout(function () { searchInput.focus(); }, 30);
  }
  function hideSearch() {
    if (searchWrap.hidden) return;
    searchWrap.hidden = true;
    if (sheetWrap.hidden) document.body.classList.remove('locked');
  }
  function closeSearch() {
    if (pushedSearch) { pushedSearch = false; history.back(); } else location.replace('#/');
  }
  searchInput.addEventListener('input', runSearch);
  searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { var b = $('#searchResults .result'); if (b) b.click(); }
  });

  // ------------------------------------------------------------------ routing
  function route() {
    var h = decodeURIComponent(location.hash.replace(/^#\/?/, ''));
    var parts = h.split('/').filter(Boolean);
    if (parts[0] === 'search') {
      hideSheet();
      if (!current) renderHome();
      showSearch();
      return;
    }
    hideSearch();
    var stop = parts[0] && stopById[parts[0]];
    if (!stop) {
      hideSheet();
      if (current !== 'home') renderHome();
      return;
    }
    if (current !== stop.id) {
      var prev = stopById[current];
      var dir = prev ? (stop.index > prev.index ? 1 : -1) : 0;
      if (prev && Math.abs(stop.index - prev.index) === STOPS.length - 1) dir = -dir;
      renderStop(stop, dir);
    }
    if (parts[1] && itemById[parts[1]]) showSheet(parts[1]);
    else hideSheet();
  }
  window.addEventListener('hashchange', route);

  // ------------------------------------------------------------------ events
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-item],[data-close],[data-search],[data-random],[data-go],[data-hint],[data-dot],[data-replace],#openSearch,#closeSearch');
    if (!t) return;
    if (t.dataset.item) { pushedSheet = true; go('#/' + current + '/' + t.dataset.item); return; }
    if (t.hasAttribute('data-close')) { closeSheet(); return; }
    if (t.id === 'openSearch' || t.hasAttribute('data-search')) { pushedSearch = true; go('#/search'); return; }
    if (t.id === 'closeSearch') { closeSearch(); return; }
    if (t.hasAttribute('data-random')) {
      var pool = ITEMS.filter(function (x) { return x.it.imgs && x.it.imgs.length; });
      var x = pool[Math.floor(Math.random() * pool.length)];
      pushedSheet = true;
      go('#/' + x.cat.id + '/' + x.it.id);
      return;
    }
    if (t.dataset.go) { pushedSheet = true; go(t.dataset.go); return; }
    if (t.dataset.hint) { searchInput.value = t.dataset.hint; runSearch(); searchInput.focus(); return; }
    if (t.dataset.dot) { var g = $('#gallery'); g.scrollTo({ left: g.clientWidth * +t.dataset.dot, behavior: 'smooth' }); return; }
    if (t.hasAttribute('data-replace')) { e.preventDefault(); location.replace(t.getAttribute('href')); return; }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (!searchWrap.hidden) closeSearch();
      else if (!sheetWrap.hidden) closeSheet();
    }
    if (e.key === 'Tab' && !sheetWrap.hidden) {   // keep focus inside the sheet
      var f = sheet.querySelectorAll('button, a[href]');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  // swipe left/right on a stop to change stops
  var sx = 0, sy = 0, st = 0, track = false;
  view.addEventListener('touchstart', function (e) {
    if (!stopById[current] || e.touches.length > 1 || e.target.closest('.gallery, .line, .stops')) { track = false; return; }
    sx = e.touches[0].clientX; sy = e.touches[0].clientY; st = Date.now(); track = true;
  }, { passive: true });
  view.addEventListener('touchend', function (e) {
    if (!track) return;
    track = false;
    var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
    if (Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 1.7 && Date.now() - st < 800) {
      var s = stopById[current];
      var nx = STOPS[(s.index + (dx < 0 ? 1 : -1) + STOPS.length) % STOPS.length];
      go('#/' + nx.id);
    }
  }, { passive: true });

  $('#footQuote').innerHTML = D.shop.quote.map(esc).join('　') + '<small>— ' + esc(D.shop.quoteBy) + '</small>';
  route();
})();
