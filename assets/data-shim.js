(() => {
  'use strict';

  const DATA_FILES = {
    'Source Detail 56': 'data/source-detail.json.gz.b64',
    'Creator Detail 88': 'data/creator-detail.json.gz.b64',
    'Added Magazines': 'data/added-magazines.json.gz.b64',
    'Coverage Gaps': 'data/coverage-gaps.json.gz.b64',
    'Taxonomy': 'data/taxonomy.json.gz.b64'
  };
  const nativeFetch = window.fetch.bind(window);
  let workbookBytesPromise = null;

  async function decodePayload(url) {
    const response = await nativeFetch(`${url}?v=${Date.now()}`);
    if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
    const text = (await response.text()).trim();
    const binary = atob(text);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    if (!('DecompressionStream' in window)) {
      throw new Error('Trình duyệt không hỗ trợ DecompressionStream (gzip).');
    }
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    return JSON.parse(await new Response(stream).text());
  }

  async function buildWorkbookBytes() {
    if (workbookBytesPromise) return workbookBytesPromise;
    workbookBytesPromise = (async () => {
      if (!window.XLSX) throw new Error('SheetJS chưa được tải.');
      const wb = XLSX.utils.book_new();
      for (const [sheetName, file] of Object.entries(DATA_FILES)) {
        const rows = await decodePayload(file);
        const ws = XLSX.utils.json_to_sheet(rows);
        XLSX.utils.book_append_sheet(wb, ws, sheetName);
      }
      return XLSX.write(wb, { bookType: 'xlsx', type: 'array', compression: true });
    })();
    return workbookBytesPromise;
  }

  window.fetch = async function(resource, options) {
    const url = typeof resource === 'string' ? resource : (resource && resource.url) || '';
    if (/data\/database\.xlsx(?:\?|$)/.test(url)) {
      try {
        const bytes = await buildWorkbookBytes();
        return new Response(bytes, {
          status: 200,
          headers: {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Cache-Control': 'no-store'
          }
        });
      } catch (err) {
        console.error('Không dựng được workbook từ snapshot:', err);
        return new Response('Workbook snapshot unavailable', { status: 500 });
      }
    }
    return nativeFetch(resource, options);
  };

  document.addEventListener('DOMContentLoaded', () => {
    const download = document.querySelector('a[href="data/database.xlsx"]');
    if (!download) return;
    download.addEventListener('click', async (event) => {
      event.preventDefault();
      const original = download.textContent;
      download.textContent = 'Đang tạo Excel…';
      try {
        const bytes = await buildWorkbookBytes();
        const blob = new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'vietnamese-media-data.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      } catch (err) {
        console.error(err);
        alert('Không thể tạo file Excel từ snapshot dữ liệu.');
      } finally {
        download.textContent = original;
      }
    });
  });
})();
