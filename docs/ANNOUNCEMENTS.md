# Announcements from another work mode

After a completed Shadow of Israphel update, a work mode can publish a concise development note and attach real gameplay screenshots through this repository. The owner requested this workflow on 3 November 2026. Do not announce unfinished work as complete or override a later request to hold publication. This workflow does not send messages to Reddit, YouTube, email, or any other service.

Repository: https://github.com/Noahhubbs01/shadow-of-israphel-website

Production: https://shadowofisraphelproject.online/ — GitHub Pages, `main`, repository root.

## 1. Start from current production

Use an isolated branch/worktree from current `origin/main`. On the owner's computer, the established checkout is `/home/daddy/Games/Shadow-of-Israphel-Adventure/website/github-pages`. Other environments can clone the repository normally. Fetch first; do not edit another session's dirty checkout. Existing Git authentication is used; no credentials belong in content or scripts.

Install authoring dependencies in the isolated checkout:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 2. Write a local handoff

Put a JSON file outside the public repository, for example `/tmp/soi-update.json`:

```json
{
  "update_id": "build-0-8-6-town-fixes",
  "date": "2026-11-03",
  "title": "A short, specific title",
  "summary": "One sentence about the verified change.",
  "body": "A few conversational paragraphs in Markdown. Describe what changed, what was tested, and what still needs work. Do not publish this example text.",
  "evidence": ["Absolute path or reference to the completed update's handoff and test report"],
  "screenshots": [
    {
      "source": "/absolute/path/to/actual-gameplay-capture.png",
      "alt": "Describe what a visitor can see in this screenshot.",
      "caption": "Explain the scene and what changed in this build."
    },
    {
      "source": "/absolute/path/to/another-capture.webp",
      "alt": "Describe the second capture.",
      "caption": "A second factual caption, with the build/date if needed."
    }
  ]
}
```

Replace every example with actual update details. Use the real completion date and a stable, unique `update_id` tied to the build or task. Reusing the ID reports the existing entry instead of creating another announcement. For a text-only post, use `"screenshots": []`.

Review screenshots for private chat, server addresses, desktop overlays, or material that should not be public. Use actual in-game captures. If a screenshot is from an older build, say so in the caption. Evidence paths are kept only in an ignored local receipt; they are not inserted into public posts.

## 3. Import text and attach screenshots

```sh
.venv/bin/python scripts/announce.py --input /tmp/soi-update.json --ready
.venv/bin/python scripts/build.py
.venv/bin/python scripts/build.py --check
.venv/bin/python -m unittest discover -s tests
```

`--ready` means the verified entry is included in the next static build; it does **not** push or publish. Omit it to prepare a draft. To include that draft later, edit its Markdown and remove `draft: true`; re-importing the same ID deliberately leaves the existing draft untouched.

The importer validates all screenshots before creating the post, copies originals byte for byte into a post-specific `assets/updates/` folder, creates compressed WebP previews, and writes a caption/alt-text manifest in `content/screenshots/`. It supports multiple PNG, JPEG, or WebP captures of different aspect ratios. It does not modify the game originals or generate imagery.

Attached screenshots also appear as small previews in the homepage and blog listings. The importer records a `created_at` timestamp so multiple updates on one date appear in the right order.

The post filename is `DATE-UPDATE_ID.md`; its URL is `/blog/DATE-UPDATE_ID/`. Do not rename published entries. The local `.announcement-receipts/` directory is ignored by Git and contains evidence references and source hashes. Keep the input handoff outside the repository too.

## 4. Inspect and publish

Run `python3 scripts/preview.py --port 8766`, then inspect the new post at http://127.0.0.1:8766/blog/. Check the text, each caption, mobile scaling, full-size image viewer, and original-image links. The existing [blog guide](BLOG.md) covers optional video and manual editing.

Review `git diff` and `git status`. Stage the intended Markdown, screenshot manifest, copied images, generated pages, feed and sitemap. Do not stage receipts, unrelated game files, or another session's edits. Commit them together.

Fetch `origin/main` again before publishing. Integrate any intervening website updates, keeping both sets of source posts and assets, then regenerate shared HTML/feed/sitemap. Never force-push. With the completed update verified and no later hold instruction, use a normal fast-forward push of the checked commit to `main`:

```sh
git push origin HEAD:main
```

GitHub Pages publishes automatically. Wait for the new post to return 200 with the intended content, and verify its homepage/blog listing, attachment URLs, canonical URL, RSS and sitemap. Check that the live HTML matches the checked commit; a cached older homepage is not success. If deployment fails, keep the source/commit and inspect the Pages build status; do not alter DNS or unrelated services. Report the final public post URL to the owner.

## Discovery in other sessions

The `/community/` page records reviewed suggestions and contributor credits. Edit `templates/community.html` when adding or changing an entry, link to the relevant development post, and state whether the work is planned, under way, or implemented in the private build. Preserve existing credits. This is a manually maintained page; feedback is collected through the linked YouTube video.

This repository's `AGENTS.md` points here. A portable skill is in `agent-skills/soi-announcements/`; a copy is installed in the owner's local Codex skill directory. A new session can invoke `$soi-announcements`. An already-running work mode can read this guide directly without waiting for skill discovery. There is no background watcher or schedule; the work mode completing the update carries out this handoff.
