(() => {
  const $=id=>document.getElementById(id);
  let items=[],health=[];
  const clean=v=>(v??'').toString().trim();
  const esc=s=>clean(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const fmtDate=s=>{if(!s)return '—'; const d=new Date(s); return isNaN(d)?esc(s):new Intl.DateTimeFormat('vi-VN',{dateStyle:'medium',timeStyle:'short'}).format(d)};
  async function load(){
    try{
      const [a,b]=await Promise.all([
        fetch(`data/live/latest.json?v=${Date.now()}`).then(r=>{if(!r.ok)throw new Error('latest.json chưa có');return r.json()}),
        fetch(`data/live/health.json?v=${Date.now()}`).then(r=>{if(!r.ok)throw new Error('health.json chưa có');return r.json()})
      ]);
      items=a.items||[]; health=b.sources||[];
      const links=health.filter(x=>x.link_only || !x.ok);
      $('generated').textContent=fmtDate(a.generated_at);
      $('statusText').textContent=`${items.length} mục từ ${health.length} nguồn có link`;
      $('kSources').textContent=health.length;
      $('kOk').textContent=health.filter(x=>x.ok).length;
      $('kLinks').textContent=health.filter(x=>x.link_only).length;
      $('kItems').textContent=items.length;
      $('kErrors').textContent=health.filter(x=>!x.ok&&!x.link_only).length;
      fillFilters(); renderFeed(); renderHealth(); renderLinkOnly();
    }catch(e){
      $('generated').textContent='Chưa có lần thu thập thành công';
      $('statusText').textContent='Collector sẽ tạo dữ liệu sau khi GitHub Actions chạy.';
      $('feed').innerHTML=`<div class="empty-state">Chưa có live data. Kiểm tra GitHub Actions.</div>`;
      $('health').innerHTML=`<div class="errorbox">${esc(e.message)}</div>`;
      $('linkOnly').innerHTML='<div class="empty-state">Chưa có danh sách link.</div>';
    }
  }
  function fillFilters(){
    const src=[...new Set(items.map(x=>clean(x.source_name)).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'vi'));
    const kinds=[...new Set(health.map(x=>clean(x.kind)).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'vi'));
    $('source').innerHTML='<option value="">Tất cả nguồn</option>'+src.map(x=>`<option>${esc(x)}</option>`).join('');
    $('kind').innerHTML='<option value="">Tất cả loại</option>'+kinds.map(x=>`<option>${esc(x)}</option>`).join('');
  }
  function filtered(){
    const q=clean($('q').value).toLowerCase(),s=$('source').value,k=$('kind').value;
    return items.filter(x=>(!s||x.source_name===s)&&(!k||x.source_kind===k)&&(!q||Object.values(x).some(v=>clean(v).toLowerCase().includes(q))));
  }
  function renderFeed(){
    const rows=filtered();
    $('feed').innerHTML=rows.length?rows.slice(0,300).map(x=>`<article class="feed-item"><div class="meta"><strong>${esc(x.source_name)}</strong><span>•</span><span>${esc(x.country)}</span><span>•</span><span>${esc(x.source_kind)}</span><span>•</span><span>${fmtDate(x.published_at)}</span></div><h3><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.title||'(không tiêu đề)')}</a></h3>${x.author?`<div class="meta">Tác giả: ${esc(x.author)}</div>`:''}${x.summary?`<p>${esc(x.summary)}</p>`:''}</article>`).join(''):'<div class="empty-state">Không có mục phù hợp bộ lọc.</div>';
  }
  function renderHealth(){
    $('health').innerHTML=health.length?health.map(x=>`<div class="health-row"><div><div class="health-name"><a href="${esc(x.homepage)}" target="_blank" rel="noopener">${esc(x.source_name)}</a></div><div class="meta">${esc(x.country)} · ${esc(x.kind)} · ${x.items_fetched||0} items · ${fmtDate(x.latest_item_at)}</div>${x.method_effective?`<div class="meta">Kết nối: ${esc(x.method_effective)}</div>`:''}${x.error?`<div class="meta" style="color:#b42318">${esc(x.error)}</div>`:''}</div><div><span class="pill ${esc(x.status)}">${esc(x.status)}</span></div></div>`).join(''):'<div class="empty-state">Chưa có health data.</div>';
  }
  function renderLinkOnly(){
    const q=clean($('linkQ').value).toLowerCase();
    const rows=health.filter(x=>x.link_only || !x.ok).filter(x=>!q||[x.source_name,x.country,x.kind,x.homepage,x.error].some(v=>clean(v).toLowerCase().includes(q)));
    $('linkOnly').innerHTML=rows.length?rows.map(x=>`<div class="link-row"><div><div class="health-name">${esc(x.source_name)}</div><div class="meta">${esc(x.country)} · ${esc(x.kind)}${x.link_only?' · link-only':' · chưa lấy được bài'}</div>${x.error?`<div class="meta" style="color:#b42318">${esc(x.error)}</div>`:''}</div><a class="link-open" href="${esc(x.homepage)}" target="_blank" rel="noopener">Mở nguồn ↗</a></div>`).join(''):'<div class="empty-state">Không có nguồn link-only phù hợp.</div>';
  }
  ['q','source','kind'].forEach(id=>$(id).addEventListener(id==='q'?'input':'change',renderFeed));
  $('linkQ').addEventListener('input',renderLinkOnly);
  load();
})();
