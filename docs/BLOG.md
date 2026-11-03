# Adding a development update

The blog is plain Markdown turned into static HTML. It costs nothing extra to host and works without visitor JavaScript.

For another work mode handing off a completed update with **multiple screenshots**, use [the announcement importer and publishing workflow](ANNOUNCEMENTS.md). It creates the Markdown, copies original images, makes small previews, and adds captions/full-size viewing in one command.

1. Create a draft from the website directory:

   ```sh
   python3 scripts/new_post.py "A walk around Mistral"
   ```

2. Open the printed file in `content/posts/`. Replace the summary and write a few paragraphs. Keep claims specific to what you actually built or tested. Use the real date; there is no need to promise a schedule or release.

3. Remove `draft: true` when ready to include it in the **local review**. Rebuild:

   ```sh
   .venv/bin/python scripts/build.py
   .venv/bin/python scripts/build.py --check
   python3 scripts/preview.py
   ```

4. Open http://127.0.0.1:8765/blog/ and the new post. Check links, dates, image descriptions, and mobile layout. Commit the Markdown and generated pages together on an isolated branch. Routine announcements requested by the owner follow [the publishing workflow](ANNOUNCEMENTS.md); respect any later hold/review instruction. Pushing `main` deploys automatically.

If the `.venv` does not exist, follow the one-time setup in the [README](../README.md). Python 3.10+ is required for the build; the screenshot importer uses Pillow from the pinned requirements. Preview and basic draft creation use only the Python standard library.

## Post format

```markdown
---
title: A walk around Mistral
date: 2026-11-03
summary: A short description of what changed and what still needs work.
draft: true
---
Write a few ordinary paragraphs here.

## What still needs testing

- One useful detail.
- Another useful detail.

[A relevant link](https://example.com/)
```

The filename starts with the matching date, followed by a lowercase slug: `2026-11-03-a-walk-around-mistral.md`. Required metadata: `title`, `date`, `summary`. Keep metadata values on one line, without wrapping them in quotation marks. The rest is ordinary Markdown, including links, lists, headings, and emphasis. Do not paste scripts or tracking embeds into posts.

## Optional screenshot

Copy an actual gameplay capture into `assets/media/`, leaving the original game asset untouched. Add these metadata lines above the closing `---`:

```text
image: assets/media/07-mistral-market.webp
image_alt: Ms Miggles and Sir Marmalade on a cobbled street in Mistral.
image_caption: Mistral market in the November private build.
```

The build requires an existing local image, alt text, and caption. It uses the smaller preview automatically when the image already belongs to the gallery. For a new screenshot, export a compressed WebP preview and use that path; retain the full-size original if you link to it in the post. Choose a 16:9 image for the standard post figure. Markdown can include additional screenshots as `![Description](/assets/media/file.webp)`; add a caption underneath and keep sizes reasonable.

## Optional video

Add `video: true` to embed the current approved gameplay trailer with native controls, no autoplay, and the same YouTube fallback. To pin an entry to particular approved footage, or embed a new development video, add:

```text
video: true
video_src: assets/media/shadow-of-israphel-trailer.mp4
video_poster: assets/media/previews/01-mistral-overlook-1280.webp
video_caption: Gameplay from the private build · 1:48
video_url: https://youtu.be/99c3DlrMxWU
```

Use the real local MP4 path, authentic screenshot poster, caption, and HTTPS YouTube URL for that update. Both local files must already exist under `assets/`. The first trailer post pins its original footage this way, so changing the homepage trailer later cannot silently change the historical entry. The build does not upload or re-encode footage. Other videos can also be ordinary Markdown links; do not paste autoplay embeds. Change the homepage's selected trailer through `media.js` after footage approval.

## Retrospective notes

The initial five posts were written on 3 November 2026 from dated records. Their `date` is the date of the documented work in America/Chicago, and `written` is the writing date. They use `retrospective: true` so visitors see that distinction. Structured metadata and RSS use the writing date for publication, not the earlier milestone date. Screenshots made later are explicitly captioned as later captures.

For a new contemporaneous update, leave out `written` and `retrospective`; the post date is used. For a retrospective, set all three truthfully. Do not invent old dates to fill the archive.

## What is maintained automatically

Newest development dates appear first. For entries on the same day, `created_at` (an ISO timestamp with a timezone offset) puts the most recently authored update first. The importer records this automatically; existing dates and URLs stay unchanged. The homepage lists the latest three entries, including small versions of attached screenshots. The blog listings use the same previews, and selecting one opens the existing full-size viewer. Blog pages show five entries, with newer/older navigation when necessary. The archive groups posts by month. Every post has its own permanent URL and metadata; the RSS feed and sitemap include the published entries. Drafts are excluded. Never rename an already published post without planning a redirect; old generated URLs are retained deliberately.
