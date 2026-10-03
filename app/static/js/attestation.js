/* ══════════════════════════════════════════════════════════════
   Talant №1 — Аттестация: универсальный рендерер блоков
   ══════════════════════════════════════════════════════════════
   Бір компонент `type` (1–4) мәніне қарай әр түрлі макет салады.

     1 — Стандартты кесте
     2 — Жылдар бойынша екі деңгейлі аккордеон
     3 — Жаңаша ашылатын аккордеондар (ячейка ішінде)
     4 — Терең сатылар кестесі (3 деңгей)

   Дерек: JSON массиві — { type, categoryTitle, isOpen, yearTitle, nodes[] }
   ══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var GOOGLE_VIEWER = 'https://docs.google.com/viewer';
  var DIRECT_TYPES = ['pdf', 'image'];

  /* ─── көмекші функциялар ───────────────────────────────── */

  function el(tag, className, content) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    /* content — мәтін немесе дара узел */
    if (content !== undefined && content !== null) {
      if (typeof content === 'object' && content.nodeType) {
        node.appendChild(content);
      } else {
        node.textContent = content;
      }
    }
    return node;
  }

  function icon(name) {
    var i = document.createElement('i');
    i.className = 'bi bi-' + name;
    return i;
  }

  /* Файлды браузерде көрсетуге арналған URL. PDF пен сурет
     тікелей, қалғаны Google Docs Viewer арқылы. */
  function embedUrl(node) {
    if (!node.fileUrl) return '';
    var absolute;
    try {
      absolute = new URL(node.fileUrl, window.location.origin).href;
    } catch (e) {
      return node.fileUrl;
    }
    if (DIRECT_TYPES.indexOf(node.fileType) !== -1) return absolute;
    return GOOGLE_VIEWER + '?url=' + encodeURIComponent(absolute) + '&embedded=true';
  }

  /* ─── аккордеон компоненті ────────────────────────────── */

  function createAccordion(cfg) {
    var block = el('div', 'att-block att-block--' + cfg.variant);
    if (cfg.open) block.classList.add('is-open');

    var btn = el('button', 'att-cat-btn');
    btn.type = 'button';
    btn.setAttribute('aria-expanded', cfg.open ? 'true' : 'false');

    if (cfg.year) {
      var year = el('span', 'att-cat-year');
      year.appendChild(icon('calendar3'));
      year.appendChild(document.createTextNode(' ' + cfg.year));
      btn.appendChild(year);
    }

    btn.appendChild(el('span', 'att-cat-name', cfg.title));

    if (cfg.meta) btn.appendChild(el('span', 'att-cat-meta', cfg.meta));

    var arrow = icon('chevron-down');
    arrow.classList.add('att-cat-arrow');
    arrow.setAttribute('aria-hidden', 'true');
    btn.appendChild(arrow);

    var panel = el('div', 'att-panel');
    panel.setAttribute('role', 'region');
    var inner = el('div', 'att-panel-inner');
    inner.appendChild(cfg.render());
    panel.appendChild(inner);

    block.appendChild(btn);
    block.appendChild(panel);

    block._btn = btn;
    block._panel = panel;

    if (!cfg.open) panel.style.maxHeight = '0px';

    btn.addEventListener('click', function () {
      setOpen(block, !isOpen(block));
    });

    return block;
  }

  function isOpen(block) {
    return block._btn.getAttribute('aria-expanded') === 'true';
  }

  function setOpen(block, open) {
    var btn = block._btn;
    var panel = block._panel;

    if (open) closeSiblings(block);

    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    block.classList.toggle('is-open', open);

    if (open) {
      panel.style.maxHeight = panel.scrollHeight + 'px';
      panel.addEventListener('transitionend', function onEnd(event) {
        if (event.propertyName !== 'max-height') return;
        if (isOpen(block)) panel.style.maxHeight = 'none';
        panel.removeEventListener('transitionend', onEnd);
      });
    } else {
      panel.style.maxHeight = panel.scrollHeight + 'px';
      requestAnimationFrame(function () {
        panel.style.maxHeight = '0px';
      });
    }
  }

  /* Тек қатарлас аккордеондарды жабады — ұяңша ашылған
     аккордеондар жабылып қалмайды. */
  function closeSiblings(block) {
    var parent = block.parentNode;
    if (!parent) return;
    Array.prototype.forEach.call(parent.children, function (child) {
      if (child === block) return;
      if (!child.classList || !child.classList.contains('att-block')) return;
      if (isOpen(child)) setOpen(child, false);
    });
  }

  /* ─── «Ашу» батырмасы ─────────────────────────────────── */

  /* PDF, сурет және сыртқы сілтеме — тікелей жаңа қойындыда
     ашылады (<a class="btn-open" target="_blank">). Қалған кеңсе
     файлдары (Word/Excel/PPT) ішкі модальда Google Viewer арқылы. */
  function createOpenButton(node) {
    if (!node.hasFile) {
      return el('span', 'text-muted small', 'Файл жоқ');
    }

    var direct = DIRECT_TYPES.indexOf(node.fileType) !== -1 || node.fileType === 'link';

    if (direct) {
      var link = el('a', 'btn-open att-open-btn');
      link.href = node.fileUrl;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.title = node.title;
      link.appendChild(icon('box-arrow-up-right'));
      link.appendChild(document.createTextNode(' Ашу'));
      return link;
    }

    var btn = el('button', 'btn-open att-open-btn');
    btn.type = 'button';
    btn.appendChild(icon('eye'));
    btn.appendChild(document.createTextNode(' Ашу'));
    btn.setAttribute('data-att-view', '');
    btn.setAttribute('data-title', node.title);
    btn.setAttribute('data-url', embedUrl(node));
    btn.setAttribute('data-type', node.fileType);
    btn.setAttribute('data-raw', node.fileUrl);
    btn.title = node.title;
    return btn;
  }

  /* ─── кесте құрастырушылар ────────────────────────────── */

  /* Стандартты кесте: № | Құжаттар атауы | Файлды қарау */
  function standardTable(documents) {
    var table = el('table', 'att-table');
    var thead = el('thead');
    var headRow = el('tr');
    ['№', 'Құжаттар атауы', 'Файлды қарау'].forEach(function (label, i) {
      var th = el('th', i === 0 ? 'att-col-num' : (i === 2 ? 'att-col-action' : ''), label);
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = el('tbody');
    if (!documents.length) {
      var emptyRow = el('tr');
      var emptyCell = el('td', 'att-empty', 'Бұл санатта құжаттар жоқ');
      emptyCell.colSpan = 3;
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
    }

    documents.forEach(function (node, index) {
      var tr = el('tr');

      var num = el('td', 'att-col-num', String(index + 1));
      tr.appendChild(num);

      var title = el('td', 'att-col-title');
      title.appendChild(document.createTextNode(node.title));
      if (node.subtitle) {
        var sub = el('small', 'att-block-subtitle');
        sub.textContent = node.subtitle;
        title.appendChild(sub);
      }
      tr.appendChild(title);

      var action = el('td', 'att-col-action');
      action.appendChild(createOpenButton(node));
      tr.appendChild(action);

      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    return wrapTable(table);
  }

  /* Жаңаша ашылатын тізім (3-ші типтегі файлдар) */
  function fileList(nodes) {
    var list = el('ul', 'att-file-list');
    if (!nodes.length) {
      list.appendChild(el('li', 'att-empty', 'Құжаттар жоқ'));
      return list;
    }
    nodes.forEach(function (node) {
      var item = el('li', 'att-file-item');
      item.appendChild(el('span', 'att-file-label', node.title));
      item.appendChild(createOpenButton(node));
      list.appendChild(item);
    });
    return list;
  }

  function wrapTable(table) {
    var wrap = el('div', 'att-table-wrap');
    wrap.appendChild(table);
    return wrap;
  }

  /* ─── 1-ТҮРІ: СТАНДАРТТЫ КЕСТЕ ────────────────────────── */

  function renderType1(block, nodes) {
    return standardTable(nodes);
  }

  /* ─── 2-ТҮРІ: ЖЫЛДАР БОЙЫНША ЕКІ ДЕҢГЕЙЛІ АККОРДЕОН ── */

  function renderType2(block, nodes) {
    var wrap = el('div', 'att-stack');

    nodes.forEach(function (yearNode) {
      var docs = yearNode.children.length ? yearNode.children : [yearNode];

      wrap.appendChild(createAccordion({
        variant: 'grey',
        title: yearNode.title,
        open: yearNode.isOpen,
        render: function () {
          return standardTable(docs);
        }
      }));
    });

    if (!nodes.length) wrap.appendChild(emptyState());
    return wrap;
  }

  /* ─── 3-ТҮРІ: ЯЧЕЙКА ІШІНДЕГІ АККОРДЕОНДАР ────────────── */

  function renderType3(block, nodes) {
    var table = el('table', 'att-table');
    var thead = el('thead');
    var headRow = el('tr');
    ['№', 'Құжат атауы', 'Құжаттар'].forEach(function (label, i) {
      headRow.appendChild(el('th', i === 0 ? 'att-col-num' : (i === 1 ? 'att-col-title' : 'att-col-cell'), label));
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = el('tbody');
    if (!nodes.length) {
      var emptyRow = el('tr');
      var emptyCell = el('td', 'att-empty', 'Құжаттар жоқ');
      emptyCell.colSpan = 3;
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
    }

    nodes.forEach(function (rowNode, index) {
      var tr = el('tr');
      tr.appendChild(el('td', 'att-col-num', String(index + 1)));

      var title = el('td', 'att-col-title');
      title.appendChild(document.createTextNode(rowNode.title));
      if (rowNode.subtitle) {
        var sub = el('small', 'att-block-subtitle');
        sub.textContent = rowNode.subtitle;
        title.appendChild(sub);
      }
      tr.appendChild(title);

      var cell = el('td', 'att-col-cell');
      var groups = rowNode.children.length ? rowNode.children : [rowNode];
      var stack = el('div', 'att-stack');

      groups.forEach(function (groupNode) {
        stack.appendChild(createAccordion({
          variant: 'grey',
          title: groupNode.title,
          open: groupNode.isOpen,
          render: function () {
            return fileList(groupNode.children.length ? groupNode.children : [groupNode]);
          }
        }));
      });

      cell.appendChild(stack);
      tr.appendChild(cell);
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    return wrapTable(table);
  }

  /* ─── 4-ТҮРІ: ТЕРЕҢ САТЫЛАР КЕСТЕСІ ───────────────────── */

  function renderType4(block, nodes) {
    var table = el('table', 'att-table');
    var thead = el('thead');
    var headRow = el('tr');
    var headers = [
      { label: '№', cls: 'att-col-num' },
      { label: 'ТӘРБИЕ ЖҰМЫСЫ', cls: 'att-col-title' },
      { label: 'Оқу жылдары', cls: 'att-col-years' },
      { label: 'Дәлелдемелер (құжаттар)', cls: 'att-col-cell' }
    ];
    headers.forEach(function (head) {
      headRow.appendChild(el('th', head.cls, head.label));
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = el('tbody');
    if (!nodes.length) {
      var emptyRow = el('tr');
      var emptyCell = el('td', 'att-empty', 'Құжаттар жоқ');
      emptyCell.colSpan = 4;
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
    }

    nodes.forEach(function (rowNode, index) {
      var tr = el('tr');
      tr.appendChild(el('td', 'att-col-num', String(index + 1)));

      var title = el('td', 'att-col-title');
      title.appendChild(document.createTextNode(rowNode.title));
      tr.appendChild(title);

      tr.appendChild(el('td', 'att-col-years', rowNode.subtitle || '—'));

      var cell = el('td', 'att-col-cell');
      var stack = el('div', 'att-stack');
      var sections = rowNode.children.length ? rowNode.children : [rowNode];

      sections.forEach(function (section) {
        stack.appendChild(createAccordion({
          variant: 'grey',
          title: section.title,
          open: section.isOpen,
          render: function () {
            return renderEvidence(section.children);
          }
        }));
      });

      cell.appendChild(stack);
      tr.appendChild(cell);
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    return wrapTable(table);
  }

  /* 4-түрдің екінші деңгейі: жыл → құжат */
  function renderEvidence(yearNodes) {
    var stack = el('div', 'att-stack');

    (yearNodes.length ? yearNodes : []).forEach(function (yearNode) {
      stack.appendChild(createAccordion({
        variant: 'grey',
        title: yearNode.title,
        open: yearNode.isOpen,
        render: function () {
          return fileList(yearNode.children.length ? yearNode.children : [yearNode]);
        }
      }));
    });

    if (!yearNodes.length) stack.appendChild(el('div', 'att-empty', 'Дәлелдемелер жоқ'));
    return stack;
  }

  /* ─── бос күй ─────────────────────────────────────────── */

  function emptyState() {
    var box = el('div', 'empty-state');
    box.appendChild(icon('folder2-open'));
    box.appendChild(el('h4', null, 'Құжаттар жоқ'));
    box.appendChild(el('p', null, 'Құжаттар админкадан қосылады'));
    return box;
  }

  /* ─── диспетчер ───────────────────────────────────────── */

  var RENDERERS = {
    1: renderType1,
    2: renderType2,
    3: renderType3,
    4: renderType4
  };

  function renderBlock(block) {
    var renderer = RENDERERS[block.type] || renderType1;
    return renderer(block, block.nodes || []);
  }

  /* ─── құжатты модаль терезеде көрсету ─────────────────── */

  function initModal() {
    var modal = document.getElementById('attModal');
    if (!modal) return;

    var frame = document.getElementById('attModalFrame');
    var image = document.getElementById('attModalImage');
    var title = document.getElementById('attModalTitle');
    var download = document.getElementById('attModalDownload');
    var lastFocused = null;

    function open(trigger) {
      var url = trigger.getAttribute('data-url');
      if (!url) return;

      lastFocused = trigger;
      title.textContent = trigger.getAttribute('data-title') || 'Құжат';
      download.href = trigger.getAttribute('data-raw') || url;

      if (trigger.getAttribute('data-type') === 'image') {
        image.src = url;
        image.hidden = false;
        frame.hidden = true;
      } else {
        frame.src = url;
        frame.hidden = false;
        image.hidden = true;
      }

      modal.hidden = false;
      document.body.classList.add('att-modal-open');
      modal.querySelector('.att-modal-x').focus();
    }

    function close() {
      modal.hidden = true;
      document.body.classList.remove('att-modal-open');
      /* iframe-ті тастау — жүктелуді тоқтатып, серверді босатады */
      frame.removeAttribute('src');
      image.removeAttribute('src');
      if (lastFocused) lastFocused.focus();
    }

    document.addEventListener('click', function (event) {
      var trigger = event.target.closest ? event.target.closest('[data-att-view]') : null;
      if (trigger) open(trigger);
    });

    modal.querySelectorAll('[data-att-close]').forEach(function (element) {
      element.addEventListener('click', close);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !modal.hidden) close();
    });
  }

  /* ─── іске қосу ───────────────────────────────────────── */

  function init() {
    var roots = document.querySelectorAll('[data-att-root]');

    roots.forEach(function (root) {
      var payload;
      try {
        payload = JSON.parse(root.getAttribute('data-att-payload') || '[]');
      } catch (e) {
        return;
      }

      payload.forEach(function (block) {
        var host = el('div', 'att-block-host');
        host.id = 'att-block-' + block.id;

        if (block.type === 2 || block.type === 3 || block.type === 4) {
          /* 2–4 түрде санаттың өзі көк аккордеон болады */
          var content = renderBlock(block);
          host.appendChild(createAccordion({
            variant: 'blue',
            title: block.categoryTitle,
            year: block.yearTitle,
            open: block.isOpen,
            render: function () {
              return content;
            }
          }));
        } else {
          /* 1 түрде кесте тікелей, аккордеонсыз */
          var wrapper = el('div', 'att-block');
          var heading = el('div', 'att-cat-btn att-cat-btn--static');
          if (block.yearTitle) {
            var year = el('span', 'att-cat-year');
            year.appendChild(icon('calendar3'));
            year.appendChild(document.createTextNode(' ' + block.yearTitle));
            heading.appendChild(year);
          }
          heading.appendChild(el('span', 'att-cat-name', block.categoryTitle));
          var meta = el('span', 'att-cat-meta');
          var docs = flattenDocs(block.nodes || []);
          meta.textContent = docs.length + ' құжат';
          heading.appendChild(meta);
          wrapper.appendChild(heading);
          wrapper.appendChild(el('div', 'att-panel-inner', renderBlock(block)));
          host.appendChild(wrapper);
        }

        root.appendChild(host);
      });
    });

    /* Тереңдетілген аккордеондардың биіктігін қайта есептеу */
    window.addEventListener('resize', function () {
      document.querySelectorAll('.att-block.is-open').forEach(function (block) {
        if (block._panel) block._panel.style.maxHeight = 'none';
      });
    });

    initModal();
  }

  /* 1 түргіш беттегі құжат санын есептеу */
  function flattenDocs(nodes) {
    var result = [];
    (nodes || []).forEach(function (node) {
      if (node.children && node.children.length) {
        result = result.concat(flattenDocs(node.children));
      } else {
        result.push(node);
      }
    });
    return result;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
