/* Template A — 花磚 (tiles). Hash routes:
 *   #/               home
 *   #/<cat>          a category
 *   #/<cat>/<item>   a category with an item sheet open
 *   #/search         search
 */
(function () {
  'use strict';
  var D = window.P13, T = window.TILES;
  var STOPS = D.categories.map(function (c) { return Object.assign({}, c); });
  STOPS.push(Object.assign({}, D.cats, { isCats: true }));
  var byId = {};
  STOPS.forEach(function (s, i) { s.index = i; byId[s.id] = s; });
  var ITEMS = [];
  D.categories.forEach(function (c) { c.items.forEach(function (it) { ITEMS.push({ it: it, cat: byId[c.id] }); }); });
  var itemById = {};
  ITEMS.forEach(function (x) { itemById[x.it.id] = x; });

  var TAG = { decaf: '無咖啡因', season: '季節限定', pot: '熱飲一壺' };
  var QUOTE = [
    { t: '喝杯咖啡', go: 'coffee' },
    { t: '吃點東西', go: 'light' },
    { t: '不要急', go: 'dessert' },
    { t: '活著很好', go: 'cats' }
  ];

  var $ = function (s, el) { return (el || document).querySelector(s); };
  var view = $('#view'), chips = $('#chips'), sheetWrap = $('#sheetWrap'), sheet = $('#sheet');
  var searchWrap = $('#searchWrap'), searchInput = $('#searchInput');
  var current = null, sheetItem = null, pushedSheet = false, pushedSearch = false, lastFocus = null, laid = false;

  function esc(s) { return String(s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function src(s, small) { return '../assets/img/' + s + (small ? '-sm' : '') + '.webp'; }
  function tile(id) { return '--tile:' + T.url(id).replace(/"/g, '&quot;'); }
  function go(h) { if (location.hash !== h) location.hash = h; }

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
  function metaOf(stop) {
    if (stop.isCats) return stop.list.length + ' 隻，天天值班';
    var m = minPrice(stop);
    return stop.items.length + ' 道' + (m ? '，' + m + ' 元起' : '');
  }

  function pricesHTML(p) {
    if (typeof p === 'number') return '<span class="pr"><b>' + p + '</b></span>';
    if (typeof p === 'string') return '<span class="pr text">' + esc(p) + '</span>';
    return ['hot', 'ice'].filter(function (k) { return p[k] != null; }).map(function (k) {
      return '<span class="pr ' + k + '"><i>' + (k === 'hot' ? '熱' : '冰') + '</i><b>' + p[k] + '</b></span>';
    }).join('');
  }
  function tagsHTML(tags) {
    if (!tags || !tags.length) return '';
    return '<span class="tags">' + tags.map(function (t) { return '<span class="tag ' + t + '">' + TAG[t] + '</span>'; }).join('') + '</span>';
  }

  // ------------------------------------------------------------------ home
  function renderHome() {
    current = 'home';
    document.title = 'Platform 13｜菜單 Menu';
    chips.hidden = true;
    var h = '<section class="hero">' +
      '<h1 class="hero-title">Platform <span class="hero-13" style="' + tile('main') + '"><span><b>13</b></span></span></h1>' +
      '<p class="hero-sub">全店蔬食。今天想從哪裡開始？</p>' +
      '<div class="quote-tiles' + (laid ? '' : ' lay') + '">' + QUOTE.map(function (q, i) {
        var s = byId[q.go];
        return '<a class="qtile" href="#/' + q.go + '" style="' + tile(q.go) + ';--i:' + i + '"><span class="qcard"><b>' + q.t + '</b><small>' +
          esc(s.zh) + ' ' + esc(s.en) + '</small></span></a>';
      }).join('') + '</div>' +
      '<p class="quote-by">小貓咪的智慧要聽</p></section>';
    laid = true;
    h += '<button class="search-open" type="button" data-search><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>搜尋餐點或飲品</button>';
    h += '<div class="row-head"><h2>菜單分類</h2><p>左右滑動看全部</p></div>';
    h += '<div class="cat-row">' + STOPS.map(function (s) {
      var c = cover(s);
      return '<a class="cat-card" href="#/' + s.id + '"><span class="cat-frame" style="' + tile(s.id) + '">' +
        (c ? '<img src="' + src(c, true) + '" alt="" loading="lazy" decoding="async">' : '<span class="cat-blank"></span>') +
        '</span><span class="cat-name">' + esc(s.zh) + '</span><span class="cat-en">' + esc(s.en) + '</span><span class="cat-meta">' + metaOf(s) + '</span></a>';
    }).join('') + '</div>';
    h += '<section class="duty"><div class="duty-head"><h2>店貓值班中</h2><a href="#/cats">去看牠們</a></div><div class="duty-row">' +
      D.cats.list.map(function (c) {
        return '<a class="duty-cat" href="#/cats" style="--collar:' + c.color + '"><img src="' + src(c.img, true) + '" alt="店貓' + esc(c.name) + '" loading="lazy"><b>' + esc(c.name) + '</b><small>' + esc(c.collar) + '</small></a>';
      }).join('') + '</div></section>';
    h += '<details class="rules"><summary>內用須知<span>' + D.shop.rules.length + ' 條</span></summary><ol>' +
      D.shop.rules.map(function (r) { return '<li>' + esc(r) + '</li>'; }).join('') + '</ol></details>';
    swap(h, 0);
  }

  // ------------------------------------------------------------------ category
  function band(stop) {
    return '<header class="band" style="' + tile(stop.id) + '"><div class="cartouche"><h1>' + esc(stop.zh) + '</h1><p>' + esc(stop.en) + '</p></div></header>';
  }
  function renderStop(stop, dir) {
    current = stop.id;
    document.title = stop.zh + '｜Platform 13';
    renderChips(stop);
    var h = band(stop);
    if (stop.isCats) h += renderCats();
    else {
      if (stop.note) h += '<p class="ticket">' + esc(stop.note) + '</p>';
      h += '<div class="rows">' + stop.items.map(function (it, i) {
        var im = it.imgs && it.imgs[0];
        var pic = im
          ? '<span class="pic"><img src="' + src(im.src, true) + '" alt="" loading="lazy" decoding="async"></span>' + (im.kind === 'illust' ? '<span class="badge">插畫示意</span>' : '')
          : '<span class="pic ph"><span>照片準備中</span></span>';
        return '<button class="row' + (i % 2 ? ' flip' : '') + '" type="button" data-item="' + it.id + '">' +
          '<span class="frame" style="' + tile(stop.id) + '">' + pic + '</span>' +
          '<span class="txt"><span class="name">' + esc(it.zh) + '</span><span class="en">' + esc(it.en) + '</span>' +
          '<span class="prices">' + pricesHTML(it.price) + '</span>' + tagsHTML(it.tags) + '</span></button>';
      }).join('') + '</div>';
      if (stop.addons) h += addonsHTML(stop.addons, stop.id);
    }
    var nx = STOPS[(stop.index + 1) % STOPS.length];
    h += '<a class="next" href="#/' + nx.id + '" style="' + tile(nx.id) + '"><span><small>下一站</small><b>' + esc(nx.zh) + '</b></span></a>';
    h += '<p class="swipe-hint">在分類頁左右滑動，也可以換分類</p>';
    swap(h, dir || 0);
  }

  function addonsHTML(a, id) {
    var h = '<section class="addons" style="' + tile(id) + '"><div class="addons-in"><h3>' + esc(a.zh) + ' <small>' + esc(a.en) + '</small>' +
      (a.price ? '<span class="pr"><b>' + esc(a.price) + '</b></span>' : '') + '</h3>';
    var list = a.items || a.list;
    if (list) {
      h += '<ul>' + list.map(function (x) {
        return '<li>' + (x.img ? '<img src="' + src(x.img, true) + '" alt="" loading="lazy">' : '<span class="dot" style="' + tile(id) + '"></span>') +
          '<span><b>' + esc(x.zh) + '</b><small>' + esc(x.en) + '</small></span><em>' + esc(x.price) + '</em></li>';
      }).join('') + '</ul>';
    }
    if (a.lines) h += '<p class="meal">含' + a.lines.map(esc).join('、') + '</p><p class="meal-en">' + esc(a.linesEn) + '</p>';
    if (a.foot) h += '<p class="meal-foot">' + esc(a.foot) + '</p>';
    return h + '</div></section>';
  }

  function renderCats() {
    var h = '<div class="kitties">' + D.cats.list.map(function (c) {
      return '<article class="kitty" style="--collar:' + c.color + '"><div class="kitty-photo"><img src="' + src(c.img) + '" alt="店貓' + esc(c.name) + '" loading="lazy" decoding="async"></div>' +
        '<div class="kitty-body"><h2>' + esc(c.name) + '<span class="collar"><i></i>' + esc(c.collar) + '</span></h2><p class="bubble">' + esc(c.line) + '</p></div>' +
        (c.more ? '<div class="kitty-more"><img src="' + src(c.more, true) + '" alt="' + esc(c.name) + '的另一張照片" loading="lazy"><img src="' + src(D.cats.duo, true) + '" alt="KIKI 和咪嚕一起躺著" loading="lazy"></div>' : '') +
        '</article>';
    }).join('') + '</div>';
    h += '<div class="quote-tiles small">' + QUOTE.map(function (q) {
      return '<a class="qtile" href="#/' + q.go + '" style="' + tile(q.go) + '"><span class="qcard"><b>' + q.t + '</b></span></a>';
    }).join('') + '</div><p class="quote-by">小貓咪的智慧要聽</p>';
    return h;
  }

  function renderChips(stop) {
    if (chips.hidden || !chips.childElementCount) {
      chips.innerHTML = STOPS.map(function (s) {
        return '<a class="chip" href="#/' + s.id + '" data-stop="' + s.id + '"><span class="sw" style="' + tile(s.id) + '"></span>' + esc(s.zh) + '</a>';
      }).join('');
      chips.hidden = false;
    }
    Array.prototype.forEach.call(chips.children, function (a) {
      if (a.dataset.stop === stop.id) {
        a.setAttribute('aria-current', 'page');
        chips.scrollTo({ left: a.offsetLeft - (chips.clientWidth - a.offsetWidth) / 2, behavior: 'smooth' });
      } else a.removeAttribute('aria-current');
    });
  }

  function swap(html, dir) {
    view.innerHTML = html;
    view.classList.remove('enter', 'from-left');
    void view.offsetWidth;
    if (dir) view.classList.add('enter', dir < 0 ? 'from-left' : 'from-right');
    window.scrollTo(0, 0);
  }

  // ------------------------------------------------------------------ item sheet
  function showSheet(id) {
    var x = itemById[id];
    if (!x) return;
    var it = x.it, cat = x.cat;
    sheetItem = id;
    var imgs = it.imgs && it.imgs.length ? it.imgs : [null];
    var slides = imgs.map(function (im, i) {
      if (!im) return '<div class="slide"><div class="shot ph" style="' + tile(cat.id) + '"><span>照片準備中，之後會補上</span></div></div>';
      return '<div class="slide"><div class="shot ' + im.kind + '"><img src="' + src(im.src) + '" alt="' + esc(it.zh) + (im.cap ? '：' + esc(im.cap) : '') + '" decoding="async"' + (i ? ' loading="lazy"' : '') + '></div></div>';
    }).join('');
    var coasters;
    if (typeof it.price === 'number') coasters = '<span class="coaster" style="' + tile(cat.id) + '"><span><b>' + it.price + '</b><small>元</small></span></span>';
    else if (typeof it.price === 'string') coasters = '<span class="price-text">' + esc(it.price) + '</span>';
    else coasters = ['hot', 'ice'].filter(function (k) { return it.price[k] != null; }).map(function (k) {
      return '<span class="coaster ' + k + '" style="' + tile(cat.id) + '"><span><small>' + (k === 'hot' ? '熱' : '冰') + '</small><b>' + it.price[k] + '</b></span></span>';
    }).join('');
    var notes = [];
    if (it.extra) notes.push(['加點', it.extra]);
    if (it.flavour) notes.push(['加風味：焦糖、香草或榛果', '+20']);
    if (cat.note) notes.push([cat.note, '']);
    if (cat.id === 'waffle') notes.push(['加冰淇淋', '+25／球']);
    if (cat.id === 'coffee' && it.price && typeof it.price === 'object') notes.push(['加一份濃縮', '+30']);
    if (cat.id === 'main') notes.push(['升級套餐：薯條或生菜沙拉、甜點、紅茶或黑咖啡', '+140']);
    var kinds = imgs.map(function (im) { return im ? im.kind : 'none'; });
    var kindNote = kinds.indexOf('illust') >= 0 ? '圖為插畫示意，實際餐點以現場為準。' :
      (kinds.indexOf('none') >= 0 ? '這道還沒有照片，之後會補上。' : '照片為店內實拍，擺盤以現場為準。');
    var list = cat.items, idx = list.findIndex(function (z) { return z.id === id; });
    var pv = list[idx - 1], nx = list[idx + 1];
    sheet.style.cssText = tile(cat.id).replace(/&quot;/g, '"');
    sheet.innerHTML =
      '<button class="sheet-close" type="button" data-close aria-label="關閉"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
      '<div class="gallery" id="gallery">' + slides + '</div>' +
      (imgs.length > 1 ? '<div class="dots" id="dots">' + imgs.map(function (_, i) { return '<button type="button" aria-label="第 ' + (i + 1) + ' 張" data-dot="' + i + '"' + (i ? '' : ' aria-current="true"') + '></button>'; }).join('') + '</div>' : '') +
      '<p class="cap" id="cap">' + esc((imgs[0] && imgs[0].cap) || '') + '</p>' +
      '<div class="sheet-strip" aria-hidden="true"></div>' +
      '<div class="sheet-body"><h2 id="sheetTitle">' + esc(it.zh) + '</h2><p class="sheet-en">' + esc(it.en) + '</p>' +
      '<div class="coasters">' + coasters + '</div>' + (it.tags ? tagsHTML(it.tags) : '') +
      (notes.length ? '<ul class="notes">' + notes.map(function (n) { return '<li><span>' + esc(n[0]) + '</span><span>' + esc(n[1]) + '</span></li>'; }).join('') + '</ul>' : '') +
      '<p class="kind">' + kindNote + '</p><div class="sheet-nav">' +
      (pv ? '<a class="nav-btn" href="#/' + cat.id + '/' + pv.id + '" data-replace><span>上一道：' + esc(pv.zh) + '</span></a>' : '<span></span>') +
      (nx ? '<a class="nav-btn" href="#/' + cat.id + '/' + nx.id + '" data-replace><span>下一道：' + esc(nx.zh) + '</span></a>' : '<span></span>') +
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
      var i = Math.round(gal.scrollLeft / gal.clientWidth), im = imgs[i];
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
      return '<div class="rgroup"><h3><span class="sw" style="' + tile(cid) + '"></span>' + esc(cat.zh) + '</h3>' + groups[cid].map(function (x) {
        var im = x.it.imgs && x.it.imgs[0];
        return '<button class="result" type="button" data-go="#/' + cid + '/' + x.it.id + '"><span class="rt" style="' + tile(cid) + '">' +
          (im ? '<img src="' + src(im.src, true) + '" alt="" loading="lazy">' : '') + '</span>' +
          '<span><b>' + esc(x.it.zh) + '</b><small>' + esc(x.it.en) + '</small></span><span class="rp">' + pricesHTML(x.it.price) + '</span></button>';
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
    if (sheetWrap.hidden) document.body.classList.remove('locked');
  }
  function closeSearch() { if (pushedSearch) { pushedSearch = false; history.back(); } else location.replace('#/'); }
  searchInput.addEventListener('input', runSearch);
  searchInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { var b = $('#searchResults .result'); if (b) b.click(); } });

  // ------------------------------------------------------------------ routing
  function route() {
    var parts = decodeURIComponent(location.hash.replace(/^#\/?/, '')).split('/').filter(Boolean);
    if (parts[0] === 'search') { hideSheet(); if (!current) renderHome(); showSearch(); return; }
    hideSearch();
    var stop = parts[0] && byId[parts[0]];
    if (!stop) { hideSheet(); if (current !== 'home') renderHome(); return; }
    if (current !== stop.id) {
      var prev = byId[current];
      var dir = prev ? (stop.index > prev.index ? 1 : -1) : 0;
      if (prev && Math.abs(stop.index - prev.index) === STOPS.length - 1) dir = -dir;
      renderStop(stop, dir);
    }
    if (parts[1] && itemById[parts[1]]) showSheet(parts[1]); else hideSheet();
  }
  window.addEventListener('hashchange', route);

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-item],[data-close],[data-search],[data-go],[data-hint],[data-dot],[data-replace],#openSearch,#closeSearch');
    if (!t) return;
    if (t.dataset.item) { pushedSheet = true; go('#/' + current + '/' + t.dataset.item); return; }
    if (t.hasAttribute('data-close')) { closeSheet(); return; }
    if (t.id === 'openSearch' || t.hasAttribute('data-search')) { pushedSearch = true; go('#/search'); return; }
    if (t.id === 'closeSearch') { closeSearch(); return; }
    if (t.dataset.go) { pushedSheet = true; go(t.dataset.go); return; }
    if (t.dataset.hint) { searchInput.value = t.dataset.hint; runSearch(); searchInput.focus(); return; }
    if (t.dataset.dot) { var g = $('#gallery'); g.scrollTo({ left: g.clientWidth * +t.dataset.dot, behavior: 'smooth' }); return; }
    if (t.hasAttribute('data-replace')) { e.preventDefault(); location.replace(t.getAttribute('href')); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { if (!searchWrap.hidden) closeSearch(); else if (!sheetWrap.hidden) closeSheet(); }
    if (e.key === 'Tab' && !sheetWrap.hidden) {
      var f = sheet.querySelectorAll('button, a[href]');
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  });

  // swipe left/right on a category to change category
  var sx = 0, sy = 0, st = 0, track = false;
  view.addEventListener('touchstart', function (e) {
    if (!byId[current] || e.touches.length > 1 || e.target.closest('.cat-row, .chips, .gallery')) { track = false; return; }
    sx = e.touches[0].clientX; sy = e.touches[0].clientY; st = Date.now(); track = true;
  }, { passive: true });
  view.addEventListener('touchend', function (e) {
    if (!track) return;
    track = false;
    var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
    if (Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 1.7 && Date.now() - st < 800) {
      var s = byId[current];
      go('#/' + STOPS[(s.index + (dx < 0 ? 1 : -1) + STOPS.length) % STOPS.length].id);
    }
  }, { passive: true });

  // static decoration
  $('#brandTile').setAttribute('style', tile('main').replace(/&quot;/g, '"'));
  $('#barStrip').setAttribute('style', tile('tea').replace(/&quot;/g, '"'));
  $('#footStrip').setAttribute('style', tile('tea').replace(/&quot;/g, '"'));
  $('#footQuote').innerHTML = D.shop.quote.map(function (q) { return '<span>' + esc(q) + '</span>'; }).join('') + '<small>小貓咪的智慧要聽</small>';
  route();
})();
