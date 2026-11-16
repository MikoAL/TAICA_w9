/* 資料庫系統 考前講義: the only script.
   Builds the top bar, sidebar, compact TOC, pager, index cards and glossary
   from data/syllabus.json, data/pages.json and data/glossary.json (CLAUDE.md §11). */
(function () {
  'use strict';

  var INDEX_VISIBLE = 7;            // Hick's Law: ≤ 7 cards per chapter before 顯示更多
  var SITE_TITLE = '資料庫系統 考前講義';

  var script = document.currentScript || document.querySelector('script[src$="site.js"]');
  var ROOT = new URL('..', script.src);           // assets/site.js → site root
  var body = document.body;
  var pageId = body.dataset.pageId || null;
  var view = body.dataset.view || (pageId ? 'page' : 'other');

  function href(path) { return new URL(path, ROOT).href; }
  function pagePath(p) { return (p.type === 'problem' ? 'problems/' : 'concepts/') + p.id + '.html'; }
  function chapterLabel(id) { return 'Ch ' + id.replace(/^ch/, ''); }
  function badge(p) { return p.type === 'problem' ? '題' : '概'; }

  function h(tag, attrs) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'text') node.textContent = v;
        else if (k === 'class') node.className = v;
        else node.setAttribute(k, v === true ? '' : v);
      });
    }
    for (var i = 2; i < arguments.length; i++) {
      var c = arguments[i];
      if (c === null || c === undefined || c === false) continue;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return node;
  }

  function getJSON(path) {
    return fetch(href(path)).then(function (r) {
      if (!r.ok) throw new Error(path + ': ' + r.status);
      return r.json();
    });
  }

  /* ---------- Model ---------- */
  function buildModel(syllabus, pages) {
    var chapters = syllabus.chapters.map(function (ch) {
      var list = pages.filter(function (p) { return p.chapter === ch.id; });
      return {
        id: ch.id, title: ch.title, slides: ch.slides, pages: list,
        published: list.filter(function (p) { return p.status === 'published'; }).length
      };
    });
    var ordered = [];
    chapters.forEach(function (ch) { ordered = ordered.concat(ch.pages); });
    var publishedOrdered = ordered.filter(function (p) { return p.status === 'published'; });
    return {
      syllabus: syllabus,
      rangeLabel: syllabus.exam.replace(/考$/, '') + '範圍',
      chapters: chapters,
      total: ordered.length,
      published: publishedOrdered.length,
      publishedOrdered: publishedOrdered,
      current: ordered.filter(function (p) { return p.id === pageId; })[0] || null
    };
  }

  function steps() {
    return Array.prototype.slice.call(document.querySelectorAll('main section.step')).filter(function (s) {
      return s.querySelector('h2');
    });
  }

  // Display number matches the CSS counter: 題目 is 0, every other step counts from 1.
  function stepNumbers(list) {
    var n = 0;
    return list.map(function (s) { return s.id === 'problem' ? 0 : ++n; });
  }

  function progress(value, max, label) {
    return h('progress', { class: 'progress', value: String(value), max: String(max || 1), 'aria-label': label });
  }

  /* ---------- Top bar ---------- */
  function renderTopBar(model) {
    var bar = document.querySelector('header.top-bar');
    if (!bar) return;
    var label = model.rangeLabel + ' 已發布 ' + model.published + ' / ' + model.total;
    bar.appendChild(h('a', { class: 'site-title', href: href('index.html') }, SITE_TITLE));
    bar.appendChild(h('div', { class: 'top-actions' },
      h('a', { class: 'top-link', href: href('glossary.html'),
               'aria-current': view === 'glossary' ? 'page' : null }, '詞彙表'),
      h('span', { class: 'coverage' },
        h('span', null, h('span', { class: 'coverage-prefix' }, model.rangeLabel + ' 已發布 '),
          model.published + ' / ' + model.total),
        progress(model.published, model.total, label))
    ));
    var onScroll = function () { bar.classList.toggle('is-scrolled', window.scrollY > 0); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Navigation tree ---------- */
  function renderTree(model, stepList) {
    var nav = h('nav', { class: 'tree', 'aria-label': '目錄' });

    nav.appendChild(h('p', { class: 'tree-group' }, '開始'));
    nav.appendChild(h('ul', null,
      h('li', null, h('a', { class: 'tree-row', href: href('index.html'),
        'aria-current': view === 'index' ? 'page' : null }, '首頁')),
      h('li', null, h('a', { class: 'tree-row', href: href('glossary.html'),
        'aria-current': view === 'glossary' ? 'page' : null }, '詞彙表'))
    ));

    nav.appendChild(h('p', { class: 'tree-group' }, model.rangeLabel));
    var chList = h('ul', { class: 'tree-chapters' });
    model.chapters.forEach(function (ch) {
      var isCurrent = model.current && model.current.chapter === ch.id;
      var pagesUl = h('ul', { class: 'tree-pages' });
      ch.pages.forEach(function (p) {
        var li = h('li');
        if (p.status === 'published') {
          li.appendChild(h('a', {
            class: 'tree-row page-row', href: href(pagePath(p)),
            'aria-current': p.id === pageId ? 'page' : null
          }, h('span', { class: 'type-badge', 'aria-label': p.type === 'problem' ? '題解' : '概念' }, badge(p)),
             h('span', { class: 'page-title' }, p.title),
             h('span', { class: 'status-dot', 'aria-hidden': 'true' })));
        } else {
          li.appendChild(h('span', { class: 'tree-row page-row planned', 'aria-disabled': 'true' },
            h('span', { class: 'type-badge', 'aria-label': p.type === 'problem' ? '題解' : '概念' }, badge(p)),
            h('span', { class: 'page-title' }, p.title),
            h('span', { class: 'status-dot planned', 'aria-hidden': 'true' }),
            h('span', { class: 'visually-hidden' }, '規劃中')));
        }
        if (p.id === pageId && stepList.length) {
          var nums = stepNumbers(stepList);
          var ol = h('ol', { class: 'tree-steps' });
          stepList.forEach(function (s, i) {
            ol.appendChild(h('li', null, h('a', { class: 'tree-row step-row', href: '#' + s.id, 'data-step': s.id },
              h('span', { class: 'step-num' }, String(nums[i])),
              h('span', null, s.querySelector('h2').textContent.trim()))));
          });
          li.appendChild(ol);
        }
        pagesUl.appendChild(li);
      });
      chList.appendChild(h('li', null, h('details', { class: 'tree-chapter', open: isCurrent ? true : null },
        h('summary', { class: 'tree-row' },
          h('span', { class: 'ch-num' }, chapterLabel(ch.id)),
          h('span', { class: 'ch-title' }, ch.title),
          h('span', { class: 'ch-count', 'aria-label': '已發布 ' + ch.published + ' / ' + ch.pages.length },
            ch.published + '/' + ch.pages.length)),
        pagesUl)));
    });
    nav.appendChild(chList);
    return nav;
  }

  function renderNavigation(model) {
    var stepList = steps();
    var aside = document.querySelector('aside.sidebar');
    if (aside) aside.appendChild(renderTree(model, stepList));

    var shell = document.querySelector('.shell');
    var main = document.querySelector('main');
    if (!shell || !main) return;
    var summary = h('summary');
    var compact = h('details', { class: 'toc-compact' }, summary, renderTree(model, stepList));
    main.insertBefore(compact, main.firstChild);
    compact.addEventListener('click', function (e) {
      if (e.target.closest('a')) compact.open = false;
    });

    var base = '目錄';
    if (model.current) base += ' · ' + chapterLabel(model.current.chapter);
    function setSummary(index) {
      if (!stepList.length || index < 0) { summary.textContent = base; return; }
      var nums = stepNumbers(stepList);
      var last = nums[nums.length - 1];
      summary.textContent = base + ' · 第 ' + nums[index] + ' / ' + last + ' 步';
    }
    setSummary(stepList.length ? 0 : -1);
    if (stepList.length) watchSteps(stepList, setSummary);
  }

  /* Current step: the first step whose card crosses the band just under the top bar. */
  function watchSteps(stepList, onChange) {
    if (!('IntersectionObserver' in window)) return;
    var visible = new Set();
    var currentIndex = -1;
    function apply(index) {
      if (index === currentIndex) return;
      currentIndex = index;
      var id = stepList[index].id;
      document.querySelectorAll('.tree .step-row').forEach(function (a) {
        if (a.dataset.step === id) a.setAttribute('aria-current', 'location');
        else a.removeAttribute('aria-current');
      });
      onChange(index);
    }
    var topBar = document.querySelector('header.top-bar');
    var offset = (topBar ? topBar.offsetHeight : 64) + 48;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) visible.add(e.target); else visible.delete(e.target);
      });
      for (var i = 0; i < stepList.length; i++) {
        if (visible.has(stepList[i])) { apply(i); return; }
      }
    }, { rootMargin: '-' + offset + 'px 0px -55% 0px' });
    stepList.forEach(function (s) { io.observe(s); });
    apply(0);
  }

  /* ---------- Pager ---------- */
  function renderPager(model) {
    var pager = document.querySelector('nav.pager');
    if (!pager || !model.current) return;
    pager.setAttribute('aria-label', '上一頁與下一頁');
    var list = model.publishedOrdered;
    var i = list.indexOf(model.current);
    if (i < 0) return;
    var prev = list[i - 1], next = list[i + 1];
    if (prev) pager.appendChild(h('a', { class: 'pager-link prev', href: href(pagePath(prev)), rel: 'prev' },
      h('span', null, '← 上一頁'), h('span', { class: 'pager-title' }, prev.title)));
    if (next) pager.appendChild(h('a', { class: 'pager-link next', href: href(pagePath(next)), rel: 'next' },
      h('span', null, '下一頁 →'), h('span', { class: 'pager-title' }, next.title)));
  }

  /* ---------- Index ---------- */
  function renderIndex(model) {
    var root = document.getElementById('page-index');
    if (!root) return;
    model.chapters.forEach(function (ch) {
      var label = '已發布 ' + ch.published + ' / ' + ch.pages.length;
      var section = h('section', { class: 'index-chapter', 'aria-labelledby': 'idx-' + ch.id },
        h('div', { class: 'index-chapter-head' },
          h('h2', { id: 'idx-' + ch.id }, h('span', { class: 'ch-num' }, chapterLabel(ch.id)), ' ', ch.title),
          h('span', { class: 'index-coverage' }, label, progress(ch.published, ch.pages.length, label))),
        h('p', { class: 'index-meta' }, '投影片範圍：' + ch.slides));
      var ul = h('ul', { class: 'index-cards' });
      ch.pages.forEach(function (p, i) {
        var title = h('span', { class: 'index-card-title' },
          h('span', { class: 'type-badge', 'aria-label': p.type === 'problem' ? '題解' : '概念' }, badge(p)),
          h('span', null, p.title),
          p.status === 'published' ? null : h('span', { class: 'planned-label' }, '規劃中'));
        var summaryText = p.summary + (p.type === 'problem' && p.source ? '（' + p.source + '）' : '');
        var card = p.status === 'published'
          ? h('a', { class: 'index-card', href: href(pagePath(p)) }, title, h('span', { class: 'index-card-summary' }, summaryText))
          : h('div', { class: 'index-card planned', 'aria-disabled': 'true' }, title, h('span', { class: 'index-card-summary' }, summaryText));
        ul.appendChild(h('li', { hidden: i >= INDEX_VISIBLE ? true : null }, card));
      });
      section.appendChild(ul);
      var hiddenCount = ch.pages.length - INDEX_VISIBLE;
      if (hiddenCount > 0) {
        var more = h('button', { type: 'button', class: 'text-button', 'aria-expanded': 'false' }, '顯示更多（' + hiddenCount + '）');
        more.addEventListener('click', function () {
          ul.querySelectorAll('li[hidden]').forEach(function (li) { li.hidden = false; });
          more.remove();
        });
        section.appendChild(more);
      }
      root.appendChild(section);
    });
    var note = document.getElementById('range-note');
    if (note) {
      note.textContent = model.syllabus.exam + '範圍：' + model.syllabus.note + '。';
      if (model.syllabus.slides_url) {
        note.appendChild(document.createTextNode('投影片編號以每張投影片頁尾印的編號為準（例如 3.26），課本官方投影片目錄在 '));
        note.appendChild(h('a', { href: model.syllabus.slides_url, rel: 'noopener' }, 'db-book.com'));
        note.appendChild(document.createTextNode('。'));
      }
    }
  }

  /* ---------- Glossary ---------- */
  function renderGlossary(model, glossary) {
    var root = document.getElementById('glossary-list');
    if (!root) return;
    var byId = {};
    model.chapters.forEach(function (ch) { ch.pages.forEach(function (p) { byId[p.id] = p; }); });
    var dl = h('dl', { class: 'glossary' });
    glossary.slice().sort(function (a, b) {
      return a.term.toLowerCase().localeCompare(b.term.toLowerCase());
    }).forEach(function (t) {
      var p = byId[t.page];
      var termNode = p ? h('a', { href: href(pagePath(p)) + '#term-' + t.id }, t.term) : t.term;
      dl.appendChild(h('div', { class: 'glossary-entry', id: 'g-' + t.id },
        h('dt', null, termNode, ' ', h('span', { class: 'alt' }, '（' + t.alt + '）')),
        h('dd', null, h('span', { class: 'gl-label' }, '白話'), t.plain),
        h('dd', null, h('span', { class: 'gl-label' }, '定義'), t.definition),
        p ? h('dd', null, h('span', { class: 'gl-label' }, '出處'), h('a', { href: href(pagePath(p)) }, p.title)) : null));
    });
    root.appendChild(dl);
  }

  function showError(err) {
    var msg = '無法載入導覽資料（' + err.message + '）。請用 python3 -m http.server 預覽，不要直接開啟檔案。';
    var target = document.querySelector('aside.sidebar') || document.querySelector('main');
    if (target) target.appendChild(h('p', { class: 'load-error', role: 'alert' }, msg));
  }

  var loads = [getJSON('data/syllabus.json'), getJSON('data/pages.json')];
  if (view === 'glossary') loads.push(getJSON('data/glossary.json'));
  Promise.all(loads).then(function (data) {
    var model = buildModel(data[0], data[1]);
    renderTopBar(model);
    renderNavigation(model);
    renderPager(model);
    if (view === 'index') renderIndex(model);
    if (view === 'glossary') renderGlossary(model, data[2]);
  }).catch(showError);
})();
