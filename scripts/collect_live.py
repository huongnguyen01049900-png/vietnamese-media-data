#!/usr/bin/env python3
import json, os, re, sys, hashlib, time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
import feedparser
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'config', 'sources.json')
LIVE_DIR = os.path.join(ROOT, 'data', 'live')
HIST_DIR = os.path.join(ROOT, 'data', 'history')
UA = 'VietnameseMediaDataPortal/1.0 (+https://github.com/huongnguyen01049900-png/vietnamese-media-data)'
TIMEOUT = 20

session = requests.Session()
session.headers.update({'User-Agent': UA, 'Accept-Language': 'vi,en;q=0.8'})


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


def clean_html(text):
    if not text: return ''
    soup = BeautifulSoup(str(text), 'html.parser')
    s = ' '.join(soup.get_text(' ', strip=True).split())
    return s[:700]


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
        if v: return str(v)
    return ''


def dedupe(items):
    seen = set(); out=[]
    for x in items:
        key = x.get('url') or x.get('guid') or (x.get('source_id','') + '|' + x.get('title',''))
        if not key or key in seen: continue
        seen.add(key); out.append(x)
    return out


def discover_feed(home):
    r = session.get(home, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    candidates=[]
    for link in soup.find_all('link'):
        typ=(link.get('type') or '').lower()
        rel=' '.join(link.get('rel') or []).lower()
        href=link.get('href')
        if href and 'alternate' in rel and ('rss' in typ or 'atom' in typ or 'xml' in typ):
            candidates.append(urljoin(r.url,href))
    candidates += [urljoin(r.url,'feed/'), urljoin(r.url,'rss'), urljoin(r.url,'rss.xml'), urljoin(r.url,'feed')]
    # keep order unique
    uniq=[]
    for c in candidates:
        if c not in uniq: uniq.append(c)
    for c in uniq[:8]:
        try:
            fr=session.get(c, timeout=TIMEOUT)
            if fr.ok and ('xml' in fr.headers.get('content-type','').lower() or '<rss' in fr.text[:500].lower() or '<feed' in fr.text[:500].lower()):
                parsed=feedparser.parse(fr.content)
                if parsed.entries: return c
        except Exception:
            pass
    return ''


def resolve_youtube_feed(url):
    r=session.get(url, timeout=TIMEOUT, allow_redirects=True)
    r.raise_for_status()
    html=r.text
    patterns=[r'"channelId":"(UC[^"]+)"', r'"externalId":"(UC[^"]+)"', r'<meta itemprop="channelId" content="([^"]+)"']
    channel_id=''
    for p in patterns:
        m=re.search(p,html)
        if m: channel_id=m.group(1); break
    if not channel_id:
        m=re.search(r'youtube\.com/channel/(UC[\w-]+)',r.url)
        if m: channel_id=m.group(1)
    if not channel_id: raise RuntimeError('Không phân giải được YouTube channelId')
    return f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}', channel_id


def collect_feed(src, feed_url):
    r=session.get(feed_url,timeout=TIMEOUT)
    r.raise_for_status()
    f=feedparser.parse(r.content)
    if getattr(f,'bozo',0) and not f.entries:
        raise RuntimeError(f'Feed parse error: {getattr(f,"bozo_exception","")}')
    max_items=int(src.get('max_items',20))
    items=[]
    for e in f.entries[:max_items]:
        link=e.get('link','')
        author=e.get('author','')
        summary=e.get('summary') or e.get('description') or ''
        item={
            'source_id':src['id'],'source_name':src['name'],'country':src.get('country',''),
            'source_kind':src.get('kind',''),'title':clean_html(e.get('title','')),
            'url':link,'published_at':parse_dt(e),'author':clean_html(author),
            'summary':clean_html(summary),'collected_at':now_iso(),'method':'feed'
        }
        if e.get('yt_videoid'):
            item['platform']='youtube'; item['video_id']=e.get('yt_videoid')
            item['thumbnail']=f'https://i.ytimg.com/vi/{e.get("yt_videoid")}/hqdefault.jpg'
        items.append(item)
    return items


def age_days(ts):
    if not ts: return None
    try:
        dt=datetime.fromisoformat(ts.replace('Z','+00:00'))
        return (datetime.now(timezone.utc)-dt).total_seconds()/86400
    except Exception:
        return None


def health_status(latest, ok):
    if not ok: return 'error'
    d=age_days(latest)
    if d is None: return 'unknown'
    if d <= 3: return 'active'
    if d <= 30: return 'low_activity'
    if d <= 180: return 'stale'
    return 'inactive'


def main():
    os.makedirs(LIVE_DIR,exist_ok=True); os.makedirs(HIST_DIR,exist_ok=True)
    with open(CONFIG,encoding='utf-8') as fh: sources=json.load(fh)
    all_items=[]; health=[]
    for i,src in enumerate(sources,1):
        started=time.time(); method=src.get('method','auto'); feed_url=src.get('feed',''); channel_id=''
        err=''; items=[]
        try:
            if method=='youtube':
                feed_url,channel_id=resolve_youtube_feed(src['url'])
            elif method=='auto':
                feed_url=discover_feed(src['url'])
                if not feed_url: raise RuntimeError('Không phát hiện RSS/Atom feed')
            elif method=='rss':
                if not feed_url: raise RuntimeError('Thiếu feed URL')
            else:
                raise RuntimeError(f'Phương thức chưa hỗ trợ: {method}')
            items=collect_feed(src,feed_url)
            if not items: raise RuntimeError('Feed không có item')
            all_items.extend(items)
        except Exception as e:
            err=f'{type(e).__name__}: {e}'[:400]
        latest=max([x.get('published_at','') for x in items if x.get('published_at')],default='')
        health.append({
            'source_id':src['id'],'source_name':src['name'],'country':src.get('country',''),
            'kind':src.get('kind',''),'homepage':src.get('url',''),'method_requested':method,
            'feed_url':feed_url,'youtube_channel_id':channel_id,'ok':not bool(err),
            'status':health_status(latest,not bool(err)),'items_fetched':len(items),
            'latest_item_at':latest,'checked_at':now_iso(),'elapsed_ms':round((time.time()-started)*1000),
            'error':err
        })
        print(f'[{i:02}/{len(sources)}] {src["name"]}: {"OK" if not err else "ERR"} {len(items)} items {err}')
    all_items=dedupe(all_items)
    all_items.sort(key=lambda x:x.get('published_at',''),reverse=True)
    generated=now_iso()
    payload={'generated_at':generated,'source_count':len(sources),'item_count':len(all_items),'items':all_items}
    hp={'generated_at':generated,'source_count':len(sources),'sources':health}
    with open(os.path.join(LIVE_DIR,'latest.json'),'w',encoding='utf-8') as f: json.dump(payload,f,ensure_ascii=False,indent=2)
    with open(os.path.join(LIVE_DIR,'health.json'),'w',encoding='utf-8') as f: json.dump(hp,f,ensure_ascii=False,indent=2)
    day=datetime.now(timezone.utc).strftime('%Y-%m-%d')
    with open(os.path.join(HIST_DIR,f'{day}.json'),'w',encoding='utf-8') as f: json.dump(payload,f,ensure_ascii=False,indent=2)
    ok=sum(1 for x in health if x['ok'])
    print(f'Completed: {ok}/{len(health)} sources OK, {len(all_items)} unique items')
    # Never fail whole pipeline just because some sources fail. Fail only if none worked.
    return 0 if ok else 2

if __name__=='__main__':
    sys.exit(main())
