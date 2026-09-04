#!/usr/bin/env python3
import json, os, re, sys, time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
import feedparser
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'config', 'sources.json')
LIVE_DIR = os.path.join(ROOT, 'data', 'live')
HIST_DIR = os.path.join(ROOT, 'data', 'history')
UA = 'VietnameseMediaDataPortal/1.1 (+https://github.com/huongnguyen01049900-png/vietnamese-media-data)'
TIMEOUT = 20

session = requests.Session()
session.headers.update({'User-Agent': UA, 'Accept-Language': 'vi,en;q=0.8'})


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


def clean_html(text):
    if not text:
        return ''
    soup = BeautifulSoup(str(text), 'html.parser')
    return ' '.join(soup.get_text(' ', strip=True).split())[:700]


def parse_dt(entry):
    for key in ('published_parsed','updated_parsed','created_parsed'):
        st = entry.get(key)
        if st:
            try:
                return datetime(*st[:6], tzinfo=timezone.utc).isoformat().replace('+00:00','Z')
            except Exception:
                pass
    for key in ('published','updated','created'):
        v = entry.get(key)
        if v:
            return str(v)
    return ''


def normalize_date(value):
    if not value:
        return ''
    value = str(value).strip()
    if not value:
        return ''
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    except Exception:
        return value


def dedupe(items):
    seen = set(); out = []
    for x in items:
        key = x.get('url') or x.get('guid') or (x.get('source_id','') + '|' + x.get('title',''))
        if not key or key in seen:
            continue
        seen.add(key); out.append(x)
    return out


def discover_feed(home):
    r = session.get(home, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    candidates = []
    for link in soup.find_all('link'):
        typ = (link.get('type') or '').lower()
        rel = ' '.join(link.get('rel') or []).lower()
        href = link.get('href')
        if href and 'alternate' in rel and ('rss' in typ or 'atom' in typ or 'xml' in typ):
            candidates.append(urljoin(r.url, href))
    candidates += [urljoin(r.url,'feed/'), urljoin(r.url,'rss'), urljoin(r.url,'rss.xml'), urljoin(r.url,'feed')]
    uniq = []
    for c in candidates:
        if c not in uniq:
            uniq.append(c)
    for c in uniq[:8]:
        try:
            fr = session.get(c, timeout=TIMEOUT)
            head = fr.text[:800].lower() if fr.text else ''
            if fr.ok and ('xml' in fr.headers.get('content-type','').lower() or '<rss' in head or '<feed' in head):
                parsed = feedparser.parse(fr.content)
                if parsed.entries:
                    return c
        except Exception:
            pass
    return ''


def resolve_youtube_feed(url):
    r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
    r.raise_for_status()
    html = r.text
    patterns = [r'"channelId":"(UC[^"]+)"', r'"externalId":"(UC[^"]+)"', r'<meta itemprop="channelId" content="([^"]+)"']
    channel_id = ''
    for p in patterns:
        m = re.search(p, html)
        if m:
            channel_id = m.group(1); break
    if not channel_id:
        m = re.search(r'youtube\.com/channel/(UC[\w-]+)', r.url)
        if m:
            channel_id = m.group(1)
    if not channel_id:
        raise RuntimeError('Không phân giải được YouTube channelId')
    return f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}', channel_id


def collect_feed(src, feed_url):
    r = session.get(feed_url, timeout=TIMEOUT)
    r.raise_for_status()
    f = feedparser.parse(r.content)
    if getattr(f,'bozo',0) and not f.entries:
        raise RuntimeError(f'Feed parse error: {getattr(f,"bozo_exception","")}')
    max_items = int(src.get('max_items',20))
    items = []
    for e in f.entries[:max_items]:
        item = {
            'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country',''),
            'source_kind': src.get('kind',''), 'title': clean_html(e.get('title','')),
            'url': e.get('link',''), 'published_at': parse_dt(e), 'author': clean_html(e.get('author','')),
            'summary': clean_html(e.get('summary') or e.get('description') or ''),
            'collected_at': now_iso(), 'method': 'feed'
        }
        if e.get('yt_videoid'):
            item['platform'] = 'youtube'; item['video_id'] = e.get('yt_videoid')
            item['thumbnail'] = f'https://i.ytimg.com/vi/{e.get("yt_videoid")}/hqdefault.jpg'
        items.append(item)
    return items


def flatten_jsonld(obj):
    out = []
    if isinstance(obj, list):
        for x in obj:
            out.extend(flatten_jsonld(x))
    elif isinstance(obj, dict):
        if '@graph' in obj:
            out.extend(flatten_jsonld(obj.get('@graph')))
        typ = obj.get('@type')
        types = typ if isinstance(typ, list) else [typ]
        if any(t in ('NewsArticle','Article','ReportageNewsArticle','BlogPosting','VideoObject') for t in types if t):
            out.append(obj)
        for k, v in obj.items():
            if k not in ('@graph',) and isinstance(v, (dict,list)):
                out.extend(flatten_jsonld(v))
    return out


def author_name(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get('name','')
    if isinstance(value, list):
        vals = [author_name(x) for x in value]
        return ', '.join([x for x in vals if x])
    return ''


def same_site(base, target):
    try:
        b = urlparse(base).netloc.lower().replace('www.','')
        t = urlparse(target).netloc.lower().replace('www.','')
        return bool(t) and (t == b or t.endswith('.' + b) or b.endswith('.' + t))
    except Exception:
        return False


def probable_article_url(url):
    try:
        p = urlparse(url)
        path = p.path.strip('/')
        if not path:
            return False
        low = path.lower()
        bad = ('tag/','tags/','category/','categories/','author/','authors/','topic/','topics/','search','login','register','about','contact','privacy','terms','rss','feed')
        if any(x in low for x in bad):
            return False
        # Date/path depth/article-like slug heuristics.
        if re.search(r'/20\d{2}/\d{1,2}/', '/' + path + '/'):
            return True
        if re.search(r'20\d{2}[-_/]\d{1,2}[-_/]\d{1,2}', path):
            return True
        parts = [x for x in path.split('/') if x]
        if len(parts) >= 2 and len(parts[-1]) >= 18:
            return True
        if len(parts) >= 3:
            return True
        return False
    except Exception:
        return False


def collect_html(src, home):
    r = session.get(home, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    max_items = int(src.get('max_items',20))
    items = []

    # 1) Prefer structured metadata supplied by the publisher.
    for script in soup.find_all('script', attrs={'type': re.compile('ld\\+json', re.I)}):
        raw = script.string or script.get_text() or ''
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        for obj in flatten_jsonld(data):
            title = clean_html(obj.get('headline') or obj.get('name') or '')
            url = obj.get('url') or obj.get('mainEntityOfPage') or ''
            if isinstance(url, dict):
                url = url.get('@id') or url.get('url') or ''
            if not url:
                continue
            url = urljoin(r.url, str(url))
            if not same_site(r.url, url) or not title:
                continue
            summary = clean_html(obj.get('description') or '')
            items.append({
                'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country',''),
                'source_kind': src.get('kind',''), 'title': title, 'url': url,
                'published_at': normalize_date(obj.get('datePublished') or obj.get('uploadDate') or obj.get('dateModified')),
                'author': clean_html(author_name(obj.get('author'))), 'summary': summary,
                'collected_at': now_iso(), 'method': 'html-jsonld'
            })

    items = dedupe(items)
    if len(items) >= max_items:
        return items[:max_items]

    # 2) Fallback to article-like anchors already present in server-rendered HTML.
    seen_urls = {x.get('url') for x in items}
    for a in soup.find_all('a', href=True):
        href = a.get('href','').strip()
        if not href or href.startswith(('#','mailto:','javascript:','tel:')):
            continue
        url = urljoin(r.url, href)
        if url in seen_urls or not same_site(r.url, url) or not probable_article_url(url):
            continue
        title = clean_html(a.get('aria-label') or a.get('title') or a.get_text(' ', strip=True))
        if len(title) < 18 or len(title) > 260:
            continue
        parent = a.find_parent(['article','li','div'])
        published = ''
        summary = ''
        if parent:
            time_tag = parent.find('time')
            if time_tag:
                published = normalize_date(time_tag.get('datetime') or time_tag.get_text(' ', strip=True))
            p = parent.find('p')
            if p:
                summary = clean_html(p.get_text(' ', strip=True))
        items.append({
            'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country',''),
            'source_kind': src.get('kind',''), 'title': title, 'url': url,
            'published_at': published, 'author': '', 'summary': summary,
            'collected_at': now_iso(), 'method': 'html-anchor'
        })
        seen_urls.add(url)
        if len(items) >= max_items:
            break
    return dedupe(items)[:max_items]


def age_days(ts):
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace('Z','+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc)-dt.astimezone(timezone.utc)).total_seconds()/86400
    except Exception:
        return None


def health_status(latest, ok):
    if not ok:
        return 'error'
    d = age_days(latest)
    if d is None:
        return 'unknown'
    if d <= 3:
        return 'active'
    if d <= 30:
        return 'low_activity'
    if d <= 180:
        return 'stale'
    return 'inactive'


def main():
    os.makedirs(LIVE_DIR, exist_ok=True); os.makedirs(HIST_DIR, exist_ok=True)
    with open(CONFIG, encoding='utf-8') as fh:
        sources = json.load(fh)
    all_items = []; health = []
    for i, src in enumerate(sources, 1):
        started = time.time(); method = src.get('method','auto'); feed_url = src.get('feed',''); channel_id = ''
        err = ''; items = []; effective_method = method
        try:
            if method == 'youtube':
                feed_url, channel_id = resolve_youtube_feed(src['url'])
                items = collect_feed(src, feed_url); effective_method = 'youtube-feed'
            elif method == 'auto':
                feed_url = discover_feed(src['url'])
                if feed_url:
                    items = collect_feed(src, feed_url); effective_method = 'feed'
                else:
                    items = collect_html(src, src['url']); effective_method = 'html'
            elif method == 'rss':
                if not feed_url:
                    raise RuntimeError('Thiếu feed URL')
                items = collect_feed(src, feed_url); effective_method = 'feed'
            elif method == 'html':
                items = collect_html(src, src['url']); effective_method = 'html'
            else:
                raise RuntimeError(f'Phương thức chưa hỗ trợ: {method}')
            if not items:
                raise RuntimeError('Không lấy được item công khai')
            all_items.extend(items)
        except Exception as e:
            err = f'{type(e).__name__}: {e}'[:400]
        latest = max([x.get('published_at','') for x in items if x.get('published_at')], default='')
        health.append({
            'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country',''),
            'kind': src.get('kind',''), 'homepage': src.get('url',''), 'method_requested': method,
            'method_effective': effective_method, 'feed_url': feed_url, 'youtube_channel_id': channel_id,
            'ok': not bool(err), 'status': health_status(latest, not bool(err)), 'items_fetched': len(items),
            'latest_item_at': latest, 'checked_at': now_iso(), 'elapsed_ms': round((time.time()-started)*1000),
            'error': err
        })
        print(f'[{i:02}/{len(sources)}] {src["name"]}: {"OK" if not err else "ERR"} {len(items)} items via {effective_method} {err}')
    all_items = dedupe(all_items)
    all_items.sort(key=lambda x: x.get('published_at',''), reverse=True)
    generated = now_iso()
    payload = {'generated_at': generated, 'source_count': len(sources), 'item_count': len(all_items), 'items': all_items}
    hp = {'generated_at': generated, 'source_count': len(sources), 'sources': health}
    with open(os.path.join(LIVE_DIR,'latest.json'),'w',encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    with open(os.path.join(LIVE_DIR,'health.json'),'w',encoding='utf-8') as f:
        json.dump(hp, f, ensure_ascii=False, indent=2)
    day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    with open(os.path.join(HIST_DIR,f'{day}.json'),'w',encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    ok = sum(1 for x in health if x['ok'])
    print(f'Completed: {ok}/{len(health)} sources OK, {len(all_items)} unique items')
    return 0 if ok else 2

if __name__ == '__main__':
    sys.exit(main())
