(() => {
  'use strict';

  const DEFAULT_FILE = 'data/database.xlsx';
  const DATASETS = {
    sources: {
      label: 'Nguồn truyền thông', sheet: 'Source Detail 56',
      titleKey: 'Tên nguồn', countryKey: 'Quốc gia/Thị trường', statusKey: 'Trạng thái 2026', typeKey: 'Loại hình gốc',
      columns: ['Tên nguồn','Quốc gia/Thị trường','Loại hình gốc','Năm/ngày thành lập hoặc số đầu','Tổng biên tập/Người phụ trách','Tần suất/lịch cập nhật hiện nay','Độ dài video/audio/podcast','Trạng thái 2026','Mức bằng chứng','Ngày kiểm tra']
    },
    creators: {
      label: 'Creator / blog', sheet: 'Creator Detail 88',
      titleKey: 'Creator/Kênh', countryKey: 'Quốc gia/Thị trường', statusKey: 'Trạng thái 2026', typeKey: 'Nền tảng chính',
      columns: ['Creator/Kênh','Nền tảng chính','Quốc gia/Thị trường','Năm tạo kênh/khởi đầu đã xác minh','Chủ kênh/Người phụ trách','Cụm nội dung','Tần suất đăng/cập nhật','Độ dài video/tập','Subscriber/Follower/View đã xác minh','Trạng thái 2026','Cấp xác minh','Ngày rà']
    },
    magazines: {
      label: 'Tạp chí', sheet: 'Added Magazines',
      titleKey: 'Tên tạp chí/ấn phẩm', countryKey: 'Quốc gia', statusKey: 'Trạng thái 2026', typeKey: 'Loại',
      columns: ['Tên tạp chí/ấn phẩm','Quốc gia','Loại','Trạng thái 2026','Năm/số đầu','Người sáng lập/Chủ trương','Chủ biên/Tổng biên tập','Hình thức phát hành','Tần suất','Website/Archive','Ngày kiểm tra']
    },
    gaps: {
      label: 'Coverage gaps', sheet: 'Coverage Gaps',
      titleKey: 'Quốc gia', countryKey: 'Quốc gia', statusKey: '', typeKey: 'Khu vực',
      columns: ['Khu vực','Quốc gia','Kết quả hiện tại','Hướng rà tiếp']
    },
    taxonomy: {
      label: 'Taxonomy', sheet: 'Taxonomy',
      titleKey: 'Loại nguồn', countryKey: '', statusKey: '', typeKey: 'Mã',
      columns: ['Mã','Loại nguồn','Mô tả']
    }
  };

  let bookData = {};
  let currentDataset = 'sources';
  let filteredRows = [];
  let sortState = { key: '', dir: 1 };
  let charts = {};

  const $ = id => document.getElementById(id);
  const els = {
    status: $('loadStatus'), source: $('dataSourceText'), file: $('fileInput'), tabs: $('datasetTabs'),
    search: $('searchInput'), country: $('countryFilter'), statusFilter: $('statusFilter'), type: $('typeFilter'),
    reset: $('resetFilters'), export: $('exportCsv'), table: $('dataTable'), count: $('visibleCount'),
    drawer: $('detailDrawer'), drawerTitle: $('drawerTitle'), drawerBody: $('drawerBody'), close: $('closeDrawer'), backdrop: $('drawerBackdrop')
  };

  function clean(v) { return v === null || v === undefined ? '' : String(v).trim(); }
  function isURL(v) { return /^https?:\/\//i.test(clean(v)); }
  function safe(v) { return clean(v).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
  function normalizeStatus(v) {
    const s = clean(v).toLowerCase();
    if (s.includes('active') || s.includes('đang hoạt động')) return 'active';
    if (s.includes('stale')) return 'stale';
    if (s.includes('historical')) return 'historical';
    if (s.includes('uncertain') || s.includes('cần xác minh') || s.includes('tìm thấy công khai')) return 'uncertain';
    if (s.includes('không hoạt động') || s.includes('inactive')) return 'inactive';
    if (s === 'a' || s === 'b' || s === 'c') return s;
    return '';
  }
  function badge(v) {
    const text = clean(v); if (!text) return '';
    return `<span class="badge ${normalizeStatus(text)}">${safe(text)}</span>`;
  }
  function dateCandidate(v) {
    const s = clean(v);
    if (!s) return '';
    if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0,10);
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(s)) return s;
    return s;
  }

  function sheetRows(wb, sheetName) {
    const ws = wb.Sheets[sheetName];
    if (!ws) return [];
    return XLSX.utils.sheet_to_json(ws, { defval: '', raw: false });
  }

  async function loadWorkbookFromArrayBuffer(buf, sourceLabel) {
    try {
      els.status.textContent = 'Đang đọc workbook…';
      const wb = XLSX.read(buf, { type: 'array', cellDates: true });
      bookData = {};
      Object.entries(DATASETS).forEach(([key, cfg]) => bookData[key] = sheetRows(wb, cfg.sheet));
      els.source.textContent = sourceLabel;
      els.status.textContent = `Đã tải ${Object.values(bookData).reduce((n, rows) => n + rows.length, 0)} dòng từ các sheet hiển thị`;
      buildTabs();
      updateKPIs();
      updateCharts();
      selectDataset(currentDataset);
    } catch (err) {
      console.error(err);
      els.status.textContent = 'Không đọc được workbook. Kiểm tra tên sheet hoặc định dạng file.';
    }
  }

  async function loadDefault() {
    try {
      const r = await fetch(`${DEFAULT_FILE}?v=${Date.now()}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      await loadWorkbookFromArrayBuffer(await r.arrayBuffer(), DEFAULT_FILE);
    } catch (err) {
      console.error(err);
      els.status.textContent = 'Không tải được data/database.xlsx. Bạn vẫn có thể chọn “Mở Excel khác”.';
    }
  }

  function buildTabs() {
    els.tabs.innerHTML = '';
    Object.entries(DATASETS).forEach(([key, cfg]) => {
      const b = document.createElement('button');
      b.className = `dataset-tab ${key === currentDataset ? 'active' : ''}`;
      b.type = 'button'; b.textContent = `${cfg.label} (${(bookData[key] || []).length})`;
      b.addEventListener('click', () => selectDataset(key));
      els.tabs.appendChild(b);
    });
  }

  function selectDataset(key) {
    currentDataset = key; sortState = { key: '', dir: 1 };
    [...els.tabs.children].forEach((n, i) => n.classList.toggle('active', Object.keys(DATASETS)[i] === key));
    els.search.value = ''; els.country.value = ''; els.statusFilter.value = ''; els.type.value = '';
    populateFilters(); applyFilters();
  }

  function unique(rows, key) {
    if (!key) return [];
    return [...new Set(rows.map(r => clean(r[key])).filter(Boolean))].sort((a,b) => a.localeCompare(b,'vi'));
  }
  function fillSelect(select, values, allLabel='Tất cả') {
    select.innerHTML = `<option value="">${allLabel}</option>` + values.map(v => `<option value="${safe(v)}">${safe(v)}</option>`).join('');
  }
  function populateFilters() {
    const cfg = DATASETS[currentDataset], rows = bookData[currentDataset] || [];
    fillSelect(els.country, unique(rows, cfg.countryKey));
    fillSelect(els.statusFilter, unique(rows, cfg.statusKey));
    fillSelect(els.type, unique(rows, cfg.typeKey));
    els.country.disabled = !cfg.countryKey;
    els.statusFilter.disabled = !cfg.statusKey;
    els.type.disabled = !cfg.typeKey;
  }

  function applyFilters() {
    const cfg = DATASETS[currentDataset], q = clean(els.search.value).toLowerCase();
    const c = els.country.value, s = els.statusFilter.value, t = els.type.value;
    filteredRows = (bookData[currentDataset] || []).filter(row => {
      if (c && clean(row[cfg.countryKey]) !== c) return false;
      if (s && clean(row[cfg.statusKey]) !== s) return false;
      if (t && clean(row[cfg.typeKey]) !== t) return false;
      if (q && !Object.values(row).some(v => clean(v).toLowerCase().includes(q))) return false;
      return true;
    });
    if (sortState.key) filteredRows.sort((a,b) => clean(a[sortState.key]).localeCompare(clean(b[sortState.key]),'vi',{numeric:true}) * sortState.dir);
    renderTable();
  }

  function formatCell(key, v) {
    const value = clean(v);
    if (!value) return '<span style="color:#a0acb8">—</span>';
    if (/trạng thái|mức bằng chứng|cấp xác minh/i.test(key)) return badge(value);
    if (/ngày kiểm tra|ngày rà/i.test(key)) return safe(dateCandidate(value));
    if (isURL(value)) return `<a href="${safe(value)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Mở nguồn ↗</a>`;
    return safe(value);
  }

  function renderTable() {
    const cfg = DATASETS[currentDataset];
    els.count.textContent = filteredRows.length.toLocaleString('vi-VN');
    const head = els.table.querySelector('thead'), body = els.table.querySelector('tbody');
    head.innerHTML = `<tr>${cfg.columns.map(k => `<th data-key="${safe(k)}">${safe(k)}${sortState.key === k ? (sortState.dir === 1 ? ' ↑' : ' ↓') : ''}</th>`).join('')}</tr>`;
    if (!filteredRows.length) {
      body.innerHTML = `<tr><td class="empty" colspan="${cfg.columns.length}">Không có bản ghi phù hợp bộ lọc.</td></tr>`;
    } else {
      body.innerHTML = filteredRows.map((row, idx) => `<tr data-idx="${idx}">${cfg.columns.map(k => `<td>${formatCell(k,row[k])}</td>`).join('')}</tr>`).join('');
    }
    head.querySelectorAll('th').forEach(th => th.addEventListener('click', () => {
      const key = th.dataset.key;
      sortState = sortState.key === key ? {key, dir: sortState.dir * -1} : {key, dir: 1}; applyFilters();
    }));
    body.querySelectorAll('tr[data-idx]').forEach(tr => tr.addEventListener('click', () => openDetail(filteredRows[Number(tr.dataset.idx)])));
  }

  function openDetail(row) {
    const cfg = DATASETS[currentDataset];
    els.drawerTitle.textContent = clean(row[cfg.titleKey]) || cfg.label;
    els.drawerBody.innerHTML = Object.entries(row).map(([k,v]) => {
      const val = clean(v);
      let html = val ? (isURL(val) ? `<a href="${safe(val)}" target="_blank" rel="noopener">${safe(val)} ↗</a>` : formatCell(k,val)) : '<span style="color:#a0acb8">—</span>';
      return `<div class="detail-row"><div class="detail-key">${safe(k)}</div><div class="detail-value">${html}</div></div>`;
    }).join('');
    els.drawer.classList.add('open'); els.drawer.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden';
  }
  function closeDetail() { els.drawer.classList.remove('open'); els.drawer.setAttribute('aria-hidden','true'); document.body.style.overflow=''; }

  function countBy(values) {
    const map = new Map();
    values.filter(Boolean).forEach(v => map.set(v, (map.get(v)||0)+1));
    return [...map.entries()].sort((a,b) => b[1]-a[1]);
  }

  function updateKPIs() {
    const src = bookData.sources || [], cr = bookData.creators || [], mag = bookData.magazines || [];
    $('kpiSources').textContent = src.length.toLocaleString('vi-VN');
    $('kpiCreators').textContent = cr.length.toLocaleString('vi-VN');
    $('kpiMagazines').textContent = mag.length.toLocaleString('vi-VN');
    $('kpiTotal').textContent = (src.length+cr.length+mag.length).toLocaleString('vi-VN');
    const countries = new Set([
      ...src.map(r=>clean(r['Quốc gia/Thị trường'])),
      ...cr.map(r=>clean(r['Quốc gia/Thị trường'])),
      ...mag.map(r=>clean(r['Quốc gia']))
    ].filter(Boolean));
    $('kpiCountries').textContent = countries.size.toLocaleString('vi-VN');
    const checked = [...src.map(r=>dateCandidate(r['Ngày kiểm tra'])), ...cr.map(r=>dateCandidate(r['Ngày rà'])), ...mag.map(r=>dateCandidate(r['Ngày kiểm tra']))].filter(Boolean).sort();
    $('kpiChecked').textContent = checked.at(-1) || '—';
  }

  function destroyCharts() { Object.values(charts).forEach(c => c?.destroy()); charts = {}; }
  function updateCharts() {
    if (typeof Chart === 'undefined') return;
    destroyCharts();
    const src = bookData.sources || [], cr = bookData.creators || [], mag = bookData.magazines || [];
    const countryCounts = countBy([
      ...src.map(r=>clean(r['Quốc gia/Thị trường'])),
      ...cr.map(r=>clean(r['Quốc gia/Thị trường'])),
      ...mag.map(r=>clean(r['Quốc gia']))
    ]).slice(0,14);
    const statusCounts = countBy([
      ...src.map(r=>clean(r['Trạng thái 2026'])),
      ...cr.map(r=>clean(r['Trạng thái 2026'])),
      ...mag.map(r=>clean(r['Trạng thái 2026']))
    ]);
    const common = { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true, ticks:{precision:0}}, x:{ticks:{autoSkip:false,maxRotation:55,minRotation:0}}} };
    charts.country = new Chart($('countryChart'), {type:'bar', data:{labels:countryCounts.map(x=>x[0]), datasets:[{data:countryCounts.map(x=>x[1]), backgroundColor:'#2f6fb6', borderRadius:4}]}, options:common});
    charts.status = new Chart($('statusChart'), {type:'doughnut', data:{labels:statusCounts.map(x=>x[0]), datasets:[{data:statusCounts.map(x=>x[1]), backgroundColor:['#16825d','#a65d00','#6f42c1','#b02a37','#2f6fb6','#718096']}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:12,font:{size:10}}}}}});
    charts.dataset = new Chart($('datasetChart'), {type:'bar', data:{labels:['Nguồn','Creator','Tạp chí'],datasets:[{data:[src.length,cr.length,mag.length],backgroundColor:['#163b64','#1463ff','#6f42c1'],borderRadius:5}]}, options:common});
  }

  function csvEscape(v) { const s = clean(v).replace(/"/g,'""'); return `"${s}"`; }
  function exportCSV() {
    if (!filteredRows.length) return;
    const keys = Object.keys(filteredRows[0]);
    const csv = '\ufeff' + [keys.map(csvEscape).join(','), ...filteredRows.map(r => keys.map(k=>csvEscape(r[k])).join(','))].join('\n');
    const blob = new Blob([csv], {type:'text/csv;charset=utf-8'}); const a=document.createElement('a');
    a.href=URL.createObjectURL(blob); a.download=`${currentDataset}-filtered.csv`; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),1000);
  }

  [els.search, els.country, els.statusFilter, els.type].forEach(el => el.addEventListener(el.tagName === 'INPUT' ? 'input' : 'change', applyFilters));
  els.reset.addEventListener('click', () => { els.search.value=''; els.country.value=''; els.statusFilter.value=''; els.type.value=''; applyFilters(); });
  els.export.addEventListener('click', exportCSV);
  els.close.addEventListener('click', closeDetail); els.backdrop.addEventListener('click', closeDetail);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });
  els.file.addEventListener('change', async e => {
    const file = e.target.files?.[0]; if (!file) return;
    await loadWorkbookFromArrayBuffer(await file.arrayBuffer(), `Tệp cục bộ: ${file.name} (chỉ xem thử, không upload lên GitHub)`);
  });

  loadDefault();
})();
