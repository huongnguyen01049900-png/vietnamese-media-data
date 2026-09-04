#!/usr/bin/env python3
import base64
import gzip
import json
import os
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'config', 'sources.json')
LIVE_DIR = os.path.join(ROOT, 'data', 'live')
HIST_DIR = os.path.join(ROOT, 'data', 'history')
DATA_DIR = os.path.join(ROOT, 'data')
UA = 'VietnameseMediaDataPortal/1.2 (+https://github.com/huongnguyen01049900-png/vietnamese-media-data)'
TIMEOUT = 20
MAX_WORKERS = 8
HEADERS = {'User-Agent': UA, 'Accept-Language': 'vi,en;q=0.8'}

SNAPSHOTS = {
    'source-detail': os.path.join(DATA_DIR, 'source-detail.json.gz.b64'),
    'creator-detail': os.path.join(DATA_DIR, 'creator-detail.json.gz.b64'),
    'added-magazines': os.path.join(DATA_DIR, 'added-magazines.json.gz.b64'),
}


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def http_get(url, **kwargs):
    headers = dict(HEADERS)
    headers.update(kwargs.pop('headers', {}) or {})
    return requests.get(url, headers=headers, timeout=kwargs.pop('timeout', TIMEOUT), **kwargs)


def clean_html(text):
    if not text:
        return ''
    soup = BeautifulSoup(str(text), 'html.parser')
    return ' '.join(soup.get_text(' ', strip=True).split())[:700]


def parse_dt(entry):
    for key in ('published_parsed', 'updated_parsed', 'created_parsed'):
        st = entry.get(key)
        if st:
            try:
                return datetime(*st[:6], tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
            except Exception:
                pass
    for key in ('published', 'updated', 'created'):
        value = entry.get(key)
        if value:
            return str(value)
    return ''


def normalize_date(value):
    if not value:
        return ''
    value = str(value).strip()
    if not value:
        return ''
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    except Exception:
        return value


def valid_url(value):
    return isinstance(value, str) and value.strip().lower().startswith(('http://', 'https://'))


def canonical_url(value):
    if not valid_url(value):
        return ''
    try:
        p = urlparse(value.strip())
        host = p.netloc.lower().replace('www.', '')
        path = p.path.rstrip('/')
        query = ('?' + p.query) if p.query else ''
        return f'{p.scheme.lower()}://{host}{path}{query}'
    except Exception:
        return value.strip().rstrip('/').lower()


def slugify(value):
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode().lower()
    value = re.sub(r'[^a-z0-9]+', '-', value).strip('-')
    return value[:54] or 'source'


def dedupe(items):
    seen = set(); out = []
    for item in items:
        key = item.get('url') or item.get('guid') or (item.get('source_id', '') + '|' + item.get('title', ''))
        if not key or key in seen:
            continue
        seen.add(key); out.append(item)
    return out


def load_snapshot(path):
    if not os.path.exists(path):
        return []
    try:
        text = open(path, encoding='utf-8').read().strip()
        raw = gzip.decompress(base64.b64decode(text)).decode('utf-8')
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception as exc:
        print(f'[registry] Không đọc được snapshot {os.path.basename(path)}: {exc}')
        return []


def choose_method(url, status='', platform=''):
    low_url = (url or '').lower()
    low_status = (status or '').lower()
    low_platform = (platform or '').lower()
    if 'historical' in low_status:
        return 'link', ''
    if 'youtube.com' in low_url:
        if '/results?' in low_url or 'search_query=' in low_url:
            return 'link', ''
        return 'youtube', ''
    if any(host in low_url for host in ('facebook.com', 'tiktok.com', 'instagram.com', 'twitter.com', 'x.com/')):
        return 'link', ''
    if 'blogspot.' in low_url:
        root = url.split('?', 1)[0].rstrip('/')
        return 'rss', root + '/feeds/posts/default?alt=rss'
    if 'wordpress.com' in low_url:
        root = url.split('?', 1)[0].rstrip('/')
        return 'rss', root + '/feed/'
    if 'facebook' in low_platform or 'tiktok' in low_platform:
        return 'link', ''
    return 'auto', ''


def build_registry():
    with open(CONFIG, encoding='utf-8') as fh:
        base_sources = json.load(fh)
    sources = list(base_sources)
    seen_urls = {canonical_url(x.get('url', '')) for x in sources if valid_url(x.get('url', ''))}
    used_ids = {x.get('id') for x in sources}

    def add(name, country, kind, url, status, origin, platform='', notes=''):
        if not valid_url(url):
            return
        url = url.strip()
        key = canonical_url(url)
        if key in seen_urls:
            return
        method, feed = choose_method(url, status, platform)
        sid_base = f'{origin[:3]}-{slugify(name)}'
        sid = sid_base; n = 2
        while sid in used_ids:
            sid = f'{sid_base}-{n}'; n += 1
        entry = {
            'id': sid, 'name': str(name), 'country': str(country or ''), 'kind': kind,
            'method': method, 'url': url, 'max_items': 0 if method == 'link' else (15 if method == 'youtube' else 20),
            'status_hint': str(status or ''), 'origin': origin,
        }
        if feed:
            entry['feed'] = feed
        if notes:
            entry['notes'] = str(notes)
        sources.append(entry); used_ids.add(sid); seen_urls.add(key)

    for row in load_snapshot(SNAPSHOTS['source-detail']):
        add(
            row.get('Tên nguồn', ''), row.get('Quốc gia/Thị trường', ''), 'media-source',
            row.get('Website chính', ''), row.get('Trạng thái 2026', ''), 'source-detail',
            notes=row.get('Loại hình gốc', '')
        )

    for row in load_snapshot(SNAPSHOTS['creator-detail']):
        platform = str(row.get('Nền tảng chính', '') or '')
        low = platform.lower()
        if 'youtube' in low:
            kind = 'youtube-creator'
        elif 'tiktok' in low:
            kind = 'tiktok-creator'
        elif 'facebook' in low:
            kind = 'facebook-creator'
        elif 'blog' in low or 'website' in low:
            kind = 'blog'
        else:
            kind = 'creator'
        add(
            row.get('Creator/Kênh', ''), row.get('Quốc gia/Thị trường', ''), kind,
            row.get('Link chính', ''), row.get('Trạng thái 2026', ''), 'creator-detail',
            platform=platform, notes=platform
        )

    for row in load_snapshot(SNAPSHOTS['added-magazines']):
        url = row.get('Website/Archive', '')
        if not valid_url(url):
            url = row.get('Nguồn chính', '')
        add(
            row.get('Tên tạp chí/ấn phẩm', ''), row.get('Quốc gia', ''), 'magazine',
            url, row.get('Trạng thái 2026', ''), 'added-magazines', notes=row.get('Loại', '')
        )

    print(f'[registry] Base {len(base_sources)} + mở rộng = {len(sources)} nguồn có link')
    return sources


def discover_feed(home):
    r = http_get(home)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    candidates = []
    for link in soup.find_all('link'):
        typ = (link.get('type') or '').lower()
        rel = ' '.join(link.get('rel') or []).lower()
        href = link.get('href')
        if href and 'alternate' in rel and ('rss' in typ or 'atom' in typ or 'xml' in typ):
            candidates.append(urljoin(r.url, href))
    candidates += [urljoin(r.url, 'feed/'), urljoin(r.url, 'rss'), urljoin(r.url, 'rss.xml'), urljoin(r.url, 'feed')]
    unique = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    for candidate in unique[:6]:
        try:
            fr = http_get(candidate)
            head = fr.text[:800].lower() if fr.text else ''
            if fr.ok and ('xml' in fr.headers.get('content-type', '').lower() or '<rss' in head or '<feed' in head):
                parsed = feedparser.parse(fr.content)
                if parsed.entries:
                    return candidate
        except Exception:
            pass
    return ''


def resolve_youtube_feed(url):
    r = http_get(url, allow_redirects=True)
    r.raise_for_status()
    html = r.text
    channel_id = ''
    for pattern in (r'"channelId":"(UC[^"]+)"', r'"externalId":"(UC[^"]+)"', r'<meta itemprop="channelId" content="([^"]+)"'):
        match = re.search(pattern, html)
        if match:
            channel_id = match.group(1); break
    if not channel_id:
        match = re.search(r'youtube\.com/channel/(UC[\w-]+)', r.url)
        if match:
            channel_id = match.group(1)
    if not channel_id:
        raise RuntimeError('Không phân giải được YouTube channelId')
    return f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}', channel_id


def collect_feed(src, feed_url):
    r = http_get(feed_url)
    r.raise_for_status()
    parsed = feedparser.parse(r.content)
    if getattr(parsed, 'bozo', 0) and not parsed.entries:
        raise RuntimeError(f'Feed parse error: {getattr(parsed, "bozo_exception", "")}')
    items = []
    for entry in parsed.entries[:int(src.get('max_items', 20))]:
        item = {
            'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country', ''),
            'source_kind': src.get('kind', ''), 'title': clean_html(entry.get('title', '')),
            'url': entry.get('link', ''), 'published_at': parse_dt(entry), 'author': clean_html(entry.get('author', '')),
            'summary': clean_html(entry.get('summary') or entry.get('description') or ''),
            'collected_at': now_iso(), 'method': 'feed'
        }
        if entry.get('yt_videoid'):
            item['platform'] = 'youtube'; item['video_id'] = entry.get('yt_videoid')
            item['thumbnail'] = f'https://i.ytimg.com/vi/{entry.get("yt_videoid")}/hqdefault.jpg'
        items.append(item)
    return items


def flatten_jsonld(obj):
    out = []
    if isinstance(obj, list):
        for value in obj:
            out.extend(flatten_jsonld(value))
    elif isinstance(obj, dict):
        if '@graph' in obj:
            out.extend(flatten_jsonld(obj.get('@graph')))
        typ = obj.get('@type')
        types = typ if isinstance(typ, list) else [typ]
        if any(t in ('NewsArticle', 'Article', 'ReportageNewsArticle', 'BlogPosting', 'VideoObject') for t in types if t):
            out.append(obj)
        for key, value in obj.items():
            if key != '@graph' and isinstance(value, (dict, list)):
                out.extend(flatten_jsonld(value))
    return out


def author_name(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get('name', '')
    if isinstance(value, list):
        return ', '.join(x for x in (author_name(v) for v in value) if x)
    return ''


def same_site(base, target):
    try:
        b = urlparse(base).netloc.lower().replace('www.', '')
        t = urlparse(target).netloc.lower().replace('www.', '')
        return bool(t) and (t == b or t.endswith('.' + b) or b.endswith('.' + t))
    except Exception:
        return False


def probable_article_url(url):
    try:
        path = urlparse(url).path.strip('/')
        if not path:
            return False
        low = path.lower()
        bad = ('tag/', 'tags/', 'category/', 'categories/', 'author/', 'authors/', 'topic/', 'topics/', 'search', 'login', 'register', 'about', 'contact', 'privacy', 'terms', 'rss', 'feed')
        if any(token in low for token in bad):
            return False
        if re.search(r'/20\d{2}/\d{1,2}/', '/' + path + '/') or re.search(r'20\d{2}[-_/]\d{1,2}[-_/]\d{1,2}', path):
            return True
        parts = [x for x in path.split('/') if x]
        return (len(parts) >= 2 and len(parts[-1]) >= 18) or len(parts) >= 3
    except Exception:
        return False


def collect_html(src, home):
    r = http_get(home)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    max_items = int(src.get('max_items', 20))
    items = []

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
            items.append({
                'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country', ''),
                'source_kind': src.get('kind', ''), 'title': title, 'url': url,
                'published_at': normalize_date(obj.get('datePublished') or obj.get('uploadDate') or obj.get('dateModified')),
                'author': clean_html(author_name(obj.get('author'))), 'summary': clean_html(obj.get('description') or ''),
                'collected_at': now_iso(), 'method': 'html-jsonld'
            })

    items = dedupe(items)
    if len(items) >= max_items:
        return items[:max_items]

    seen_urls = {x.get('url') for x in items}
    for anchor in soup.find_all('a', href=True):
        href = anchor.get('href', '').strip()
        if not href or href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
            continue
        url = urljoin(r.url, href)
        if url in seen_urls or not same_site(r.url, url) or not probable_article_url(url):
            continue
        title = clean_html(anchor.get('aria-label') or anchor.get('title') or anchor.get_text(' ', strip=True))
        if len(title) < 18 or len(title) > 260:
            continue
        parent = anchor.find_parent(['article', 'li', 'div'])
        published = ''; summary = ''
        if parent:
            time_tag = parent.find('time')
            if time_tag:
                published = normalize_date(time_tag.get('datetime') or time_tag.get_text(' ', strip=True))
            paragraph = parent.find('p')
            if paragraph:
                summary = clean_html(paragraph.get_text(' ', strip=True))
        items.append({
            'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country', ''),
            'source_kind': src.get('kind', ''), 'title': title, 'url': url,
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
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 86400
    except Exception:
        return None


def health_status(latest, ok):
    if not ok:
        return 'error'
    days = age_days(latest)
    if days is None:
        return 'unknown'
    if days <= 3:
        return 'active'
    if days <= 30:
        return 'low_activity'
    if days <= 180:
        return 'stale'
    return 'inactive'


def process_source(src):
    started = time.time(); method = src.get('method', 'auto'); feed_url = src.get('feed', ''); channel_id = ''
    error = ''; items = []; effective_method = method; link_only = method == 'link'
    if link_only:
        return [], {
            'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country', ''),
            'kind': src.get('kind', ''), 'homepage': src.get('url', ''), 'method_requested': method,
            'method_effective': 'link-only', 'feed_url': '', 'youtube_channel_id': '', 'ok': False,
            'link_only': True, 'status': 'link_only', 'items_fetched': 0, 'latest_item_at': '',
            'checked_at': now_iso(), 'elapsed_ms': 0, 'error': '', 'origin': src.get('origin', 'config'),
            'status_hint': src.get('status_hint', ''), 'notes': src.get('notes', '')
        }
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
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'[:400]
    latest = max([x.get('published_at', '') for x in items if x.get('published_at')], default='')
    health = {
        'source_id': src['id'], 'source_name': src['name'], 'country': src.get('country', ''),
        'kind': src.get('kind', ''), 'homepage': src.get('url', ''), 'method_requested': method,
        'method_effective': effective_method, 'feed_url': feed_url, 'youtube_channel_id': channel_id,
        'ok': not bool(error), 'link_only': False, 'status': health_status(latest, not bool(error)),
        'items_fetched': len(items), 'latest_item_at': latest, 'checked_at': now_iso(),
        'elapsed_ms': round((time.time() - started) * 1000), 'error': error,
        'origin': src.get('origin', 'config'), 'status_hint': src.get('status_hint', ''), 'notes': src.get('notes', '')
    }
    return items, health


def main():
    os.makedirs(LIVE_DIR, exist_ok=True); os.makedirs(HIST_DIR, exist_ok=True)
    sources = build_registry()
    all_items = []; health = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_source, src): src for src in sources}
        done = 0
        for future in as_completed(futures):
            src = futures[future]; done += 1
            try:
                items, row = future.result()
            except Exception as exc:
                items = []
                row = {
                    'source_id': src.get('id', ''), 'source_name': src.get('name', ''), 'country': src.get('country', ''),
                    'kind': src.get('kind', ''), 'homepage': src.get('url', ''), 'method_requested': src.get('method', ''),
                    'method_effective': 'internal-error', 'feed_url': '', 'youtube_channel_id': '', 'ok': False,
                    'link_only': False, 'status': 'error', 'items_fetched': 0, 'latest_item_at': '',
                    'checked_at': now_iso(), 'elapsed_ms': 0, 'error': f'{type(exc).__name__}: {exc}'[:400],
                    'origin': src.get('origin', 'config'), 'status_hint': src.get('status_hint', ''), 'notes': src.get('notes', '')
                }
            all_items.extend(items); health.append(row)
            label = 'LINK' if row.get('link_only') else ('OK' if row.get('ok') else 'ERR')
            print(f'[{done:03}/{len(sources)}] {src.get("name")}: {label} {len(items)} items via {row.get("method_effective")} {row.get("error", "")}')

    all_items = dedupe(all_items)
    all_items.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    health.sort(key=lambda x: (x.get('link_only', False), not x.get('ok', False), x.get('source_name', '').lower()))
    generated = now_iso()
    payload = {'generated_at': generated, 'source_count': len(sources), 'item_count': len(all_items), 'items': all_items}
    hp = {'generated_at': generated, 'source_count': len(sources), 'sources': health}

    with open(os.path.join(LIVE_DIR, 'latest.json'), 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(LIVE_DIR, 'health.json'), 'w', encoding='utf-8') as fh:
        json.dump(hp, fh, ensure_ascii=False, indent=2)
    day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    with open(os.path.join(HIST_DIR, f'{day}.json'), 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    ok = sum(1 for row in health if row.get('ok'))
    link_only = sum(1 for row in health if row.get('link_only'))
    errors = len(health) - ok - link_only
    print(f'Completed: {ok} fetchable OK, {link_only} link-only, {errors} fetch errors, {len(all_items)} unique items')
    return 0 if (ok or link_only) else 2


if __name__ == '__main__':
    sys.exit(main())
