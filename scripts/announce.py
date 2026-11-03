#!/usr/bin/env python3
"""Import a completed update and screenshots into this website; never pushes Git."""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def line(value, field):
    if not isinstance(value, str) or not value.strip() or '\n' in value or '\r' in value:
        raise ValueError(f'{field} must be a nonempty single line')
    return value.strip()


def import_update(payload, root=ROOT, ready=False):
    update_id = line(payload.get('update_id'), 'update_id')
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,99}', update_id):
        raise ValueError('update_id must use lowercase letters, digits, dots, underscores or hyphens')
    posts = root / 'content/posts'
    for path in posts.glob('*.md'):
        metadata = path.read_text().split('\n---\n', 1)[0]
        if f'\nupdate_id: {update_id}\n' in metadata + '\n':
            return {'status': 'already_exists', 'post': str(path), 'message': 'Existing announcement preserved; no new text or images imported.'}
    title = line(payload.get('title'), 'title')
    summary = line(payload.get('summary'), 'summary')
    day = line(payload.get('date'), 'date')
    date.fromisoformat(day)
    body = payload.get('body')
    if not isinstance(body, str) or not body.strip():
        raise ValueError('body must contain the factual update in Markdown')
    if re.search(r'<\s*(script|iframe|style)\b', body, re.I):
        raise ValueError('Use Markdown text and approved media fields, not executable embeds')
    evidence = payload.get('evidence')
    if not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
        raise ValueError('evidence must list the records used to verify this update; these stay local')
    slug = f'{day}-{update_id}'
    post_path = posts / f'{slug}.md'
    image_dir = root / 'assets/updates' / slug
    manifest_path = root / 'content/screenshots' / f'{slug}.json'
    if post_path.exists() or image_dir.exists() or manifest_path.exists():
        raise ValueError(f'{slug} already has files; review them instead of overwriting')
    shots = payload.get('screenshots', [])
    if not isinstance(shots, list):
        raise ValueError('screenshots must be an array')
    # Validate and prepare every attachment before writing any website files.
    with tempfile.TemporaryDirectory(prefix='soi-announcement-') as temp:
        prepared = Path(temp)
        screenshots, receipts = [], []
        for number, shot in enumerate(shots, 1):
            if not isinstance(shot, dict):
                raise ValueError('Each screenshot must have source, alt and caption fields')
            source = Path(line(shot.get('source'), 'screenshot source')).expanduser()
            alt = line(shot.get('alt'), 'screenshot alt')
            caption = line(shot.get('caption'), 'screenshot caption')
            if not source.is_absolute() or not source.is_file():
                raise ValueError(f'Screenshot must be an existing absolute file path: {source}')
            with Image.open(source) as image:
                if image.format not in ('PNG', 'JPEG', 'WEBP') or getattr(image, 'n_frames', 1) != 1:
                    raise ValueError('Use a still PNG, JPEG, or WebP gameplay capture')
                extension = {'PNG': '.png', 'JPEG': '.jpg', 'WEBP': '.webp'}[image.format]
                image.load()
                preview = ImageOps.exif_transpose(image).convert('RGB')
                width, height = preview.size
                preview.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                preview.save(prepared / f'{number:02d}-preview.webp', 'WEBP', quality=82, method=6)
            original_name = f'{number:02d}-original{extension}'
            shutil.copyfile(source, prepared / original_name)
            original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            if hashlib.sha256((prepared / original_name).read_bytes()).hexdigest() != original_hash:
                raise ValueError('Screenshot changed during import; retry after capture finishes')
            base = f'assets/updates/{slug}'
            screenshots.append({'src': f'{base}/{original_name}', 'preview': f'{base}/{number:02d}-preview.webp', 'width': width, 'height': height, 'alt': alt, 'caption': caption})
            receipts.append({'source': str(source), 'sha256': original_hash})
        metadata = f'---\ntitle: {title}\ndate: {day}\nsummary: {summary}\nupdate_id: {update_id}\n'
        metadata += f'created_at: {datetime.now(timezone.utc).isoformat(timespec="seconds")}\n'
        if not ready:
            metadata += 'draft: true\n'
        if screenshots:
            metadata += f'screenshots: content/screenshots/{slug}.json\n'
        content = metadata + '---\n' + body.strip() + '\n'
        # Publish the source entry last. A failed import never becomes a half-written post.
        if screenshots:
            image_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(prepared, image_dir)
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with manifest_path.open('x') as stream:
                json.dump(screenshots, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
        posts.mkdir(parents=True, exist_ok=True)
        with post_path.open('x') as stream:
            stream.write(content)
    receipt_dir = root / '.announcement-receipts'
    receipt_dir.mkdir(exist_ok=True)
    (receipt_dir / f'{slug}.json').write_text(json.dumps({'update_id': update_id, 'evidence': evidence, 'screenshots': receipts}, indent=2) + '\n')
    return {'status': 'created', 'post': str(post_path), 'screenshots': len(screenshots), 'draft': not ready, 'url': f'/blog/{slug}/'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Local JSON handoff; keep it outside the public repository')
    parser.add_argument('--ready', action='store_true', help='Include verified content in the next build instead of creating a draft')
    args = parser.parse_args()
    try:
        result = import_update(json.loads(args.input.read_text()), ready=args.ready)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'Announcement not imported: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
