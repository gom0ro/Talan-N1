/* ══════════════════════════════════════════════════════════════
   Talant №1 — Аттестация: универсальный рендерер блоков
   ══════════════════════════════════════════════════════════════
   Бір компонент `type` (1–4) мәніне қарай әр түрлі макет салады.

     1 — Стандартты кесте
     2 — Жылдар бойынша екі деңгейлі аккордеон
     3 — Жаңаша ашылатын аккордеондар (ячейка ішінде)
     4 — Терең сатылар кестесі (3 деңгей)
     5 — Стандартты кесте, бірақ санат тақырыбы ашылып-жабылады

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

  function getNodeNumber(node, fallbackIndex, prefix, mode) {
    if (mode === 'none') {
      return '';
    }
    if (node && node.customNumber !== undefined && node.customNumber !== null && String(node.customNumber).trim() !== '') {
      return String(node.customNumber).trim();
    }
    if (mode === 'simple') {
      return String(fallbackIndex + 1);
    }
    if (prefix && mode !== 'simple') {
      return prefix + '.' + (fallbackIndex + 1);
    }
    return String(fallbackIndex + 1);
  }

  /* ─── кесте құрастырушылар ────────────────────────────── */

  /* Стандартты кесте: № | Құжаттар атауы | Файлды қарау */
  function standardTable(documents, numPrefix, mode) {
    // Егер тізімдегі элементтердің балалары (подпункттері 2.1, 2.2...) бар болса,
    // құрама нумерациялы (иерархиялық rowspan кестесін) саламыз:
    // Бағандар: № (Негізгі) | № (Қосалқы 2.1, 2.2) | Құжаттар атауы | Файлды қарау
    var hasSubItems = documents.some(function (d) { return d.children && d.children.length; });

    var table = el('table', 'att-table');
    var thead = el('thead');
    var headRow = el('tr');

    var headers = hasSubItems
      ? ['№', '№', 'Құжаттар атауы', 'Файлды қарау']
      : ['№', 'Құжаттар атауы', 'Файлды қарау'];

    headers.forEach(function (label, i) {
      var cls = '';
      if (hasSubItems) {
        if (i === 0) cls = 'att-col-main-num';
        else if (i === 1) cls = 'att-col-sub-num';
        else if (i === 3) cls = 'att-col-action';
      } else {
        if (i === 0) cls = 'att-col-num';
        else if (i === 2) cls = 'att-col-action';
      }
      headRow.appendChild(el('th', cls, label));
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = el('tbody');
    if (!documents.length) {
      var emptyRow = el('tr');
      var emptyCell = el('td', 'att-empty', 'Бұл санатта құжаттар жоқ');
      emptyCell.colSpan = hasSubItems ? 4 : 3;
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      table.appendChild(tbody);
      return wrapTable(table);
    }

    documents.forEach(function (node, index) {
      var mainNum = getNodeNumber(node, index, numPrefix, mode);
      var subs = node.children && node.children.length ? node.children : null;

      if (!subs) {
        // Жай ғана 1 құжат (подпункті жоқ)
        var tr = el('tr');
        var tdMain = el('td', hasSubItems ? 'att-col-main-num' : 'att-col-num', mainNum);
        tr.appendChild(tdMain);

        if (hasSubItems) {
          // Қосалқы баған бос немесе дефис
          tr.appendChild(el('td', 'att-col-sub-num', '—'));
        }

        var tdTitle = el('td', 'att-col-title');
        tdTitle.appendChild(document.createTextNode(node.title));
        if (node.subtitle) {
          var sub = el('small', 'att-block-subtitle');
          sub.textContent = node.subtitle;
          tdTitle.appendChild(sub);
        }
        tr.appendChild(tdTitle);

        var tdAction = el('td', 'att-col-action');
        tdAction.appendChild(createOpenButton(node));
        tr.appendChild(tdAction);

        tbody.appendChild(tr);
      } else {
        // Пункт 2 бөлінеді подпункттерге (2.1, 2.2, 2.3...)
        // Басты № ұяшығы барлық подпункттерге біріктіріледі (rowspan)
        subs.forEach(function (subNode, subIdx) {
          var trSub = el('tr');

          if (subIdx === 0) {
            var tdMerged = el('td', 'att-col-main-num', mainNum);
            tdMerged.rowSpan = subs.length;
            tdMerged.style.verticalAlign = 'middle';
            tdMerged.style.fontWeight = '700';
            tdMerged.style.background = '#f8fafc';
            trSub.appendChild(tdMerged);
          }

          var subNum = getNodeNumber(subNode, subIdx, mainNum, mode);
          var tdSubNum = el('td', 'att-col-sub-num', subNum);
          tdSubNum.style.fontWeight = '600';
          trSub.appendChild(tdSubNum);

          var tdSubTitle = el('td', 'att-col-title');
          tdSubTitle.appendChild(document.createTextNode(subNode.title));
          if (subNode.subtitle) {
            var s = el('small', 'att-block-subtitle');
            s.textContent = subNode.subtitle;
            tdSubTitle.appendChild(s);
          }
          trSub.appendChild(tdSubTitle);

          var tdSubAction = el('td', 'att-col-action');
          tdSubAction.appendChild(createOpenButton(subNode));
          trSub.appendChild(tdSubAction);

          tbody.appendChild(trSub);
        });
      }
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
    return standardTable(nodes, null, block ? block.numberingMode : null);
  }

  /* ─── 5-ТҮРІ: АШЫЛЫП-ЖАБЫЛАТЫН СТАНДАРТТЫ КЕСТЕ ─────────
     1-түрдің дәл өзі. Айырмашылығы тек санат тақырыбының
     ашылып-жабылуы (init ішінде көк аккордеонмен қапталады). */
  function renderType5(block, nodes) {
    return standardTable(nodes, null, block ? block.numberingMode : null);
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
          return standardTable(docs, null, block ? block.numberingMode : null);
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

    var mode = block ? block.numberingMode : 'auto';
    nodes.forEach(function (rowNode, index) {
      var tr = el('tr');
      tr.appendChild(el('td', 'att-col-num', getNodeNumber(rowNode, index, null, mode)));

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

    var mode4 = block ? block.numberingMode : 'auto';
    nodes.forEach(function (rowNode, index) {
      var tr = el('tr');
      tr.appendChild(el('td', 'att-col-num', getNodeNumber(rowNode, index, null, mode4)));

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

  /* ─── 6-ТҮРІ: БЛОК С ПОДПУНКТАМИ (1 Бөлім, ішінде 1.1, 1.2...) ── */

  function renderType6(block, nodes) {
    var wrap = el('div', 'att-stack');
    var mode = block ? block.numberingMode : 'auto';

    nodes.forEach(function (sectionNode, sIndex) {
      var secNum = getNodeNumber(sectionNode, sIndex, null, mode);
      var secTitle = sectionNode.title;
      // Егер тақырыптың алдында нөмірі жазылмаған болса, қосамыз
      var displayTitle = (secNum && !secTitle.startsWith(secNum)) ? (secNum + '. ' + secTitle) : secTitle;

      var children = sectionNode.children || [];

      if (!children.length) {
        // Егер подпункт болмаса — тікелей өзін 1 құжаттық кесте ретінде немесе қарапайым етіп шығарады
        wrap.appendChild(createAccordion({
          variant: 'grey',
          title: displayTitle,
          open: sectionNode.isOpen,
          render: function () {
            var rowPrefix = (mode === 'simple') ? null : secNum;
            return standardTable([sectionNode], rowPrefix, mode);
          }
        }));
      } else {
        // Ішкі балалары болса: егер олардың өз балалары бар болса немесе құжаттар болса
        var hasSubChildren = children.some(function (c) { return c.children && c.children.length; });

        wrap.appendChild(createAccordion({
          variant: 'grey',
          title: displayTitle,
          meta: children.length + ' тармақ',
          open: sectionNode.isOpen,
          render: function () {
            if (hasSubChildren) {
              // Екі деңгейлі подпункттер
              var subStack = el('div', 'att-stack');
              children.forEach(function (subNode, subIndex) {
                var subPrefix = (mode === 'simple') ? null : secNum;
                var subNum = getNodeNumber(subNode, subIndex, subPrefix, mode);
                var subTitle = subNode.title;
                var subDisplay = (subNum && !subTitle.startsWith(subNum)) ? (subNum + ' ' + subTitle) : subTitle;
                var subDocs = (subNode.children && subNode.children.length) ? subNode.children : [subNode];

                subStack.appendChild(createAccordion({
                  variant: 'grey',
                  title: subDisplay,
                  open: subNode.isOpen,
                  render: function () {
                    var docPrefix = (mode === 'simple') ? null : subNum;
                    return standardTable(subDocs, docPrefix, mode);
                  }
                }));
              });
              return subStack;
            } else {
              // Тікелей стандартты кесте: нөмірлері 1.1, 1.2... немесе 1, 2, 3 (егер simple болса)
              var tablePrefix = (mode === 'simple') ? null : secNum;
              return standardTable(children, tablePrefix, mode);
            }
          }
        }));
      }
    });

    if (!nodes.length) wrap.appendChild(emptyState());
    return wrap;
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
    4: renderType4,
    5: renderType5,
    6: renderType6
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

        if (block.type === 5) {
          /* 5 түр — 1 түрдің дәл өзі, бірақ ашылып-жабылады */
          var content5 = renderBlock(block);
          host.appendChild(createAccordion({
            variant: 'blue',
            title: block.categoryTitle,
            meta: flattenDocs(block.nodes || []).length + ' құжат',
            open: block.isOpen,
            render: function () {
              return content5;
            }
          }));
        } else if (block.type === 2 || block.type === 3 || block.type === 4 || block.type === 6) {
          /* 2–4 және 6 түрде санаттың өзі көк аккордеон болады */
          var content = renderBlock(block);
          host.appendChild(createAccordion({
            variant: 'blue',
            title: block.categoryTitle,
            open: block.isOpen,
            render: function () {
              return content;
            }
          }));
        } else {
          /* 1 түрде кесте тікелей, аккордеонсыз */
          var wrapper = el('div', 'att-block');
          var heading = el('div', 'att-cat-btn att-cat-btn--static');
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
