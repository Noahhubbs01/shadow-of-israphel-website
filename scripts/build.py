#!/usr/bin/env python3
"""Build checked-in static pages. Hosting needs no Python or other runtime."""
import argparse
from collections import Counter
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

import markdown

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://shadowofisraphelproject.online'
PAGE_SIZE = 5


def template(name, **values):
    source = (ROOT / 'templates' / name).read_text()
    return re.sub(r'\{\{ (\w+) \}\}', lambda m: str(values[m[1]]), source)


def read_posts():
    posts = []
    update_ids = set()
    for path in sorted((ROOT / 'content/posts').glob('*.md')):
        source = path.read_text()
        if not source.startswith('---\n'):
            raise ValueError(f'{path.name}: expected metadata between --- lines')
        metadata, body = source[4:].split('\n---\n', 1)
        post = {}
        for line in metadata.splitlines():
            key, value = line.split(':', 1)
            if key in post:
                raise ValueError(f'{path.name}: duplicate metadata key {key}')
            post[key.strip()] = value.strip()
        if post.get('draft') == 'true':
            continue
        for key in ('date', 'title', 'summary'):
            if not post.get(key):
                raise ValueError(f'{path.name}: missing {key}')
        event = date.fromisoformat(post['date'])
        post['written'] = post.get('written', post['date'])
        written = date.fromisoformat(post['written'])
        created = datetime.fromisoformat(post.get('created_at', post['written'] + 'T00:00:00+00:00'))
        if created.tzinfo is None:
            raise ValueError(f'{path.name}: created_at needs a timezone offset')
        post['created_order'] = created.timestamp()
        if written < event:
            raise ValueError(f'{path.name}: written date cannot precede the development date')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*', path.stem):
            raise ValueError(f'{path.name}: use YYYY-MM-DD-lowercase-slug.md')
        if not path.stem.startswith(post['date'] + '-'):
            raise ValueError(f'{path.name}: filename date must match metadata')
        if post.get('image'):
            if not post.get('image_alt') or not post.get('image_caption'):
                raise ValueError(f'{path.name}: image needs image_alt and image_caption')
            image_path = (ROOT / post['image']).resolve()
            if not image_path.is_relative_to(ROOT / 'assets') or not image_path.is_file():
                raise ValueError(f'{path.name}: image must exist under assets/')
        for key in ('video_src', 'video_poster'):
            if post.get(key):
                remote = urlsplit(post[key])
                if key == 'video_src' and remote.scheme == 'https' and remote.netloc:
                    continue
                media_path = (ROOT / post[key]).resolve()
                if not media_path.is_relative_to(ROOT / 'assets') or not media_path.is_file():
                    raise ValueError(f'{path.name}: {key} must exist under assets/')
        if post.get('video_url') and urlsplit(post['video_url']).scheme != 'https':
            raise ValueError(f'{path.name}: video_url must use HTTPS')
        if post.get('youtube_id') and not re.fullmatch(r'[A-Za-z0-9_-]{11}', post['youtube_id']):
            raise ValueError(f'{path.name}: youtube_id must be an 11-character video ID')
        if post.get('update_id'):
            if post['update_id'] in update_ids:
                raise ValueError(f'{path.name}: duplicate update_id')
            update_ids.add(post['update_id'])
        post['screenshots_data'] = []
        if post.get('screenshots'):
            manifest = (ROOT / post['screenshots']).resolve()
            if not manifest.is_relative_to(ROOT / 'content/screenshots') or not manifest.is_file():
                raise ValueError(f'{path.name}: screenshots manifest must exist under content/screenshots/')
            attachments = json.loads(manifest.read_text())
            if not isinstance(attachments, list) or not attachments:
                raise ValueError(f'{path.name}: screenshots manifest must be a nonempty array')
            for shot in attachments:
                if not isinstance(shot, dict) or not all(isinstance(shot.get(k), str) and shot[k].strip() for k in ('src', 'preview', 'alt', 'caption')):
                    raise ValueError(f'{path.name}: each screenshot needs src, preview, alt and caption')
                if not all(isinstance(shot.get(k), int) and shot[k] > 0 for k in ('width', 'height')):
                    raise ValueError(f'{path.name}: screenshot dimensions must be positive integers')
                for key in ('src', 'preview'):
                    target = (ROOT / shot[key]).resolve()
                    if not target.is_relative_to(ROOT / 'assets') or not target.is_file():
                        raise ValueError(f'{path.name}: screenshot {key} must exist under assets/')
                post['screenshots_data'].append(shot)
        post.update(slug=path.stem, url=f'/blog/{path.stem}/', body=markdown.markdown(body, extensions=['sane_lists', 'fenced_code']), month=post['date'][:7], retrospective=post.get('retrospective') == 'true')
        posts.append(post)
    return sorted(posts, key=lambda p: (p['date'], p['created_order'], p['slug']), reverse=True)


def human_date(value):
    d = date.fromisoformat(value)
    return f'{d.day} {d:%B %Y}'


def post_date(post):
    label = f'<time datetime="{post["date"]}">{human_date(post["date"])}</time>'
    if post['retrospective']:
        label += ' <span>· retrospective note</span>'
    return f'<p class="journal-meta">{label}</p>'


def excerpt(post):
    screenshots = ''.join(f'''<a class="screenshot-link" href="/{escape(shot['src'])}" data-caption="{escape(shot['caption'])}" aria-label="View screenshot full size: {escape(shot['alt'])}">
        <img src="/{escape(shot['preview'])}" width="{shot['width']}" height="{shot['height']}" loading="lazy" decoding="async" alt="{escape(shot['alt'])}">
      </a>''' for shot in post['screenshots_data'])
    if screenshots:
        screenshots = f'<div class="update-screenshots">{screenshots}</div>'
    return f'''<article class="journal-entry">
      {post_date(post)}
      <h3><a href="{post['url']}">{escape(post['title'])}</a></h3>
      <p>{escape(post['summary'])}</p>
      {screenshots}<p class="update-read-more"><a href="{post['url']}">Read the update →</a></p>
    </article>'''


def video_html(media):
    trailer = media['trailer']
    youtube = escape(trailer.get('youtube', 'https://youtu.be/99c3DlrMxWU'))
    source = escape(trailer['src'] if trailer['src'].startswith('https://') else '/' + trailer['src'])
    title = escape(trailer.get('title', 'Shadow of Israphel gameplay trailer'))
    youtube_label = escape(trailer.get('youtube_label', 'Watch on YouTube ↗'))
    return f'''<div class="trailer-frame">
      <video controls playsinline preload="none" poster="/{escape(trailer['poster'])}" width="1920" height="1080" aria-label="{title}">
        <source src="{source}" type="video/mp4">
        <a href="{source}">Open the video</a>.
      </video>
      <button class="trailer-launch" type="button" aria-label="Play {title}" hidden><span aria-hidden="true">▶</span></button>
    </div>
    <p class="media-caption"><span>{escape(trailer['caption'])}</span><a href="{youtube}">{youtube_label}</a></p>
    <p class="video-error" role="status" hidden>Video playback couldn’t start. Try the player’s controls or <a href="{source}">open the MP4</a>.</p>'''


def youtube_html(video_id, title, caption):
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id):
        raise ValueError('Invalid YouTube video ID')
    return f'''<div class="youtube-frame">
      <iframe src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0" title="{escape(title)}" width="1920" height="1080" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>
    </div>
    <p class="media-caption"><span>{escape(caption)}</span><a href="https://youtu.be/{video_id}">Watch on YouTube ↗</a></p>'''


def gallery_html(media):
    figures = []
    for i, shot in enumerate(media['screenshots'], 1):
        figures.append(f'''<figure>
        <a class="screenshot-link" href="/{escape(shot['src'])}" data-caption="{escape(shot['caption'])}" aria-label="View {escape(shot['caption'])} full size">
          <img src="/{escape(shot['thumbnail'])}" srcset="/{escape(shot['thumbnail'])} 640w, /{escape(shot['preview'])} 1280w" sizes="(max-width: 560px) calc(100vw - 48px), (max-width: 760px) calc((100vw - 72px) / 2), 300px" width="{shot['width']}" height="{shot['height']}" alt="{escape(shot['alt'])}" loading="lazy" decoding="async">
        </a>
        <figcaption><span>{i:02d}</span> {escape(shot['caption'])}</figcaption>
      </figure>''')
    return '\n'.join(figures)


def outputs():
    posts = read_posts()
    if not posts:
        raise ValueError('At least one published post is required')
    media = json.loads((ROOT / 'media.js').read_text().split('window.SOI_MEDIA = ', 1)[1].strip().removesuffix(';'))
    rendered = {}
    pages = []

    def page(path, title, description, content, article=None):
        schema = ''
        if article:
            data = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': article['title'], 'description': article['summary'], 'datePublished': article['written'], 'dateModified': article['written'], 'mainEntityOfPage': ORIGIN + path, 'image': ORIGIN + '/assets/media/01-mistral-overlook.webp'}
            schema = '<script type="application/ld+json">' + json.dumps(data).replace('<', '\\u003c') + '</script>'
        rendered[path.lstrip('/') + 'index.html'] = template('base.html', title=escape(title), description=escape(description), canonical=ORIGIN + path, og_type='article' if article else 'website', home_current='aria-current="page"' if path == '/' else '', blog_current='aria-current="page"' if path.startswith('/blog/') else '', community_current='aria-current="page"' if path == '/community/' else '', content=content, structured_data=schema)
        pages.append(path)

    playthrough = media.get('playthrough')
    playthrough_html = ''
    if playthrough:
        playthrough_html = video_html({'trailer': playthrough}) if playthrough.get('src') else youtube_html(playthrough['id'], playthrough['title'], playthrough['caption'])
    homepage = template('home.html', trailer=video_html(media), playthrough=playthrough_html, gallery=gallery_html(media), screenshot_count=len(media['screenshots']), latest_posts='\n'.join(excerpt(p) for p in posts[:3]))
    page('/', 'Shadow of Israphel — A Minecraft fan adventure', 'An independent, unofficial Shadow of Israphel fan recreation. Watch real gameplay, explore screenshots, and follow this solo Minecraft passion project.', homepage)
    feedback_url = (playthrough or {}).get('youtube', 'https://www.youtube.com/@ShadowofIsraphelFanProject')
    page('/community/', 'Community suggestions — Shadow of Israphel', 'Community feedback, contributor credits, and the changes being made to the private Shadow of Israphel fan adventure.', template('community.html', feedback_url=escape(feedback_url)))

    months = Counter(p['month'] for p in posts)
    month_list = '<ul class="month-list">' + ''.join(f'<li><a href="/blog/archive/#{m}">{date.fromisoformat(m + "-01"):%B %Y}</a> <span>({n})</span></li>' for m, n in months.items()) + '</ul>'

    def blog_page(path, title, description, body, article=None, crumb=''):
        content = template('blog.html', blog_content=body, archive_months=month_list, breadcrumb=crumb)
        page(path, title + ' — Shadow of Israphel', description, content, article)

    count = (len(posts) + PAGE_SIZE - 1) // PAGE_SIZE
    for n in range(count):
        path = '/blog/' if n == 0 else f'/blog/page/{n + 1}/'
        intro = '<h1>Development blog</h1><p class="blog-intro">Notes from a solo Minecraft fan project. Work in progress, familiar places, and the small fixes along the way.</p>'
        if n == 0 and any(p['retrospective'] for p in posts):
            intro += '<p class="archive-note">The first entries are retrospective notes written on 3 November 2026 from dated project records. Their dates refer to the work described.</p>'
        body = intro + ''.join(excerpt(p) for p in posts[n * PAGE_SIZE:(n + 1) * PAGE_SIZE])
        if count > 1:
            body += '<nav class="pagination" aria-label="Blog pages">'
            if n:
                body += f'<a href="{"/blog/" if n == 1 else f"/blog/page/{n}/"}">← Newer posts</a>'
            body += f'<span>Page {n + 1} of {count}</span>'
            if n + 1 < count:
                body += f'<a href="/blog/page/{n + 2}/">Older posts →</a>'
            body += '</nav>'
        body += '<p class="archive-link"><a href="/blog/archive/">Browse all posts by month →</a></p>'
        blog_page(path, 'Development blog' + (f' · Page {n + 1}' if n else ''), 'Development notes from the independent Shadow of Israphel Minecraft fan recreation.', body)

    for i, post in enumerate(posts):
        body = f'<article class="full-post">{post_date(post)}<h1>{escape(post["title"])}</h1><p class="post-summary">{escape(post["summary"])}</p>'
        if post['retrospective']:
            body += f'<p class="archive-note">Looking back at work recorded on {human_date(post["date"])}. Written {human_date(post["written"])}.</p>'
        body += f'<div class="post-body">{post["body"]}</div>'
        if post.get('youtube_id'):
            body += '<div class="post-video">' + youtube_html(post['youtube_id'], post['title'], post.get('video_caption', 'Gameplay from the private development build')) + '</div>'
        if post.get('image'):
            shot = next((s for s in media['screenshots'] if s['src'] == post['image']), None)
            preview = shot['preview'] if shot else post['image']
            body += f'<figure class="post-image"><a href="/{escape(post["image"])}"><img src="/{escape(preview)}" width="1920" height="1080" loading="lazy" alt="{escape(post["image_alt"])}"></a><figcaption>{escape(post["image_caption"])}</figcaption></figure>'
        for shot in post['screenshots_data']:
            body += f'''<figure class="post-image">
              <a class="screenshot-link" href="/{escape(shot['src'])}" data-caption="{escape(shot['caption'])}" aria-label="View screenshot full size: {escape(shot['alt'])}">
                <img src="/{escape(shot['preview'])}" width="{shot['width']}" height="{shot['height']}" loading="lazy" decoding="async" alt="{escape(shot['alt'])}">
              </a><figcaption>{escape(shot['caption'])} <a href="/{escape(shot['src'])}">Full-size image</a></figcaption>
            </figure>'''
        if post.get('video') == 'true':
            selection = dict(media['trailer'])
            for key, field in [('video_src', 'src'), ('video_poster', 'poster'), ('video_caption', 'caption'), ('video_url', 'youtube'), ('video_title', 'title'), ('video_youtube_label', 'youtube_label')]:
                if post.get(key):
                    selection[field] = post[key]
            body += '<div class="post-video">' + video_html({'trailer': selection}) + '</div>'
        body += '</article><nav class="post-navigation" aria-label="More development posts">'
        if i + 1 < len(posts):
            older = posts[i + 1]
            body += f'<a href="{older["url"]}">← Older: {escape(older["title"])}</a>'
        if i:
            newer = posts[i - 1]
            body += f'<a href="{newer["url"]}">Newer: {escape(newer["title"])} →</a>'
        body += '</nav>'
        blog_page(post['url'], post['title'], post['summary'], body, post, ' / Post')

    body = '<h1>Development archive</h1><p class="blog-intro">All the notes so far, newest first.</p>'
    for month in months:
        body += f'<section class="archive-month" id="{month}"><h2>{date.fromisoformat(month + "-01"):%B %Y}</h2><ul>'
        for p in posts:
            if p['month'] == month:
                body += f'<li><time datetime="{p["date"]}">{date.fromisoformat(p["date"]).day:02d}</time><a href="{p["url"]}">{escape(p["title"])}</a></li>'
        body += '</ul></section>'
    blog_page('/blog/archive/', 'Development archive', 'Browse the Shadow of Israphel development blog by month.', body, crumb=' / Archive')

    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for path in pages:
        ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = ORIGIN + path
    rendered['sitemap.xml'] = ET.tostring(sitemap, encoding='unicode', xml_declaration=True) + '\n'
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    for tag, text in [('title', 'Shadow of Israphel development blog'), ('link', ORIGIN + '/blog/'), ('description', 'Notes from an independent Minecraft fan recreation.'), ('language', 'en-us')]:
        ET.SubElement(channel, tag).text = text
    for p in posts:
        item = ET.SubElement(channel, 'item')
        for tag, value in [('title', p['title']), ('link', ORIGIN + p['url']), ('guid', ORIGIN + p['url']), ('description', p['summary']), ('pubDate', format_datetime(datetime.combine(date.fromisoformat(p['written']), datetime.min.time(), tzinfo=timezone.utc)))]:
            ET.SubElement(item, tag).text = value
    rendered['feed.xml'] = ET.tostring(rss, encoding='unicode', xml_declaration=True) + '\n'
    rendered['.generated-pages.json'] = json.dumps(sorted(rendered), indent=2) + '\n'
    return rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check output without changing files')
    args = parser.parse_args()
    changed = []
    for name, source in outputs().items():
        path = ROOT / name
        if not path.exists() or path.read_text() != source:
            changed.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source)
    if args.check and changed:
        print('Generated files need rebuilding: ' + ', '.join(changed), file=sys.stderr)
        return 1
    print(f'{"Checked" if args.check else "Built"} static site; {len(changed)} file(s) {"out of date" if args.check else "updated"}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
