#!/usr/bin/env python3
"""Create a draft without publishing it: python3 scripts/new_post.py 'Post title'."""
import argparse
from datetime import date
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('title')
parser.add_argument('--date', default=date.today().isoformat())
args = parser.parse_args()
date.fromisoformat(args.date)
slug = re.sub(r'[^a-z0-9]+', '-', args.title.lower()).strip('-')
if not slug or '\n' in args.title:
    parser.error('Use a single-line title containing letters or numbers')
path = Path(__file__).resolve().parents[1] / 'content/posts' / f'{args.date}-{slug}.md'
with path.open('x') as file:
    file.write(f'---\ntitle: {args.title}\ndate: {args.date}\nsummary: Add a short, factual summary.\ndraft: true\n---\nWrite your update here.\n')
print(f'Created draft: {path}\nEdit it, then remove draft: true when ready for the local preview.')
