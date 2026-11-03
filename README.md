# Shadow of Israphel website

Public website for an independent Minecraft fan adventure.

Live site: https://shadowofisraphelproject.online/

Static HTML, CSS, and JavaScript, hosted on GitHub Pages from the main branch at the repository root. Generated pages are committed, so hosting needs no build service, database, or server runtime. `CNAME`, `.nojekyll`, the approved MP4, and original screenshot URLs are retained.

## Local preview

Run `python3 scripts/preview.py` from this directory, then open **http://127.0.0.1:8765/**. Ctrl+C stops the preview. This loopback-only server supports video seeking and adds a noindex header to local responses. It never publishes. Use HTTP preview rather than opening HTML directly: site links are relative to the domain root.

## Editing

Install the small authoring dependency once:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then edit:

- `content/posts/*.md` for development posts. See [the blog guide](docs/BLOG.md) or [the work-mode announcement workflow](docs/ANNOUNCEMENTS.md) for text with multiple screenshot attachments.
- `templates/home.html` for homepage writing.
- `templates/base.html` for shared navigation, metadata, and footer.
- `templates/blog.html` for the blog sidebar and shared layout.
- `style.css` and `app.js` for presentation and progressive enhancements.
- `media.js` for the approved trailer and gallery selection.

Rebuild with `.venv/bin/python scripts/build.py`. Verify committed pages match their sources with `.venv/bin/python scripts/build.py --check`. The build updates the homepage, blog, archive, pagination when needed, RSS, and sitemap. It does not deploy. Do not edit generated HTML directly: the next build would overwrite it.

Run the authoring regression tests with `.venv/bin/python -m unittest discover -s tests`. They check draft exclusion, pagination, required metadata, retrospective dates, and stable video selection.

## Hosting and review

The custom domain remains `shadowofisraphelproject.online`; GitHub Pages serves the `main` branch from `/`. A push to `main` publishes automatically. The owner approved this redesign for publication on 3 November 2026 and requested routine update announcements with screenshot attachments. See [the announcement workflow](docs/ANNOUNCEMENTS.md). Unrelated redesigns still need review; a later instruction to hold publication takes precedence. Review the complete diff and generated output before any push to `main`.

Umami uses the existing website ID, domain allowlist, hash exclusion, and Do Not Track setting in `templates/base.html`. Local previews are excluded from analytics collection. Canonical URLs always use the live HTTPS domain. Never put a preview noindex directive into the production HTML or robots.txt.

Old anchors `#home`, `#main`, `#trailer`, `#screenshots`, `#updates`, and `#about` remain valid. Keep published blog filenames and URLs stable. Build output deliberately does not delete old URLs; handle any future removals or redirects explicitly.

Third-party characters, artwork, textures, and trademarks belong to their respective owners. This project is not affiliated with The Yogscast, Mojang Studios, or Microsoft.
