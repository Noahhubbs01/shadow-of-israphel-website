# Website updates and announcements

This repository is the public Shadow of Israphel fan-project website. Production is GitHub Pages from `main` at the repository root, at https://shadowofisraphelproject.online/.

The owner approved the reviewed redesign on 3 November 2026 and requested an avenue for other work modes to add announcements after updates, including attached screenshots. Use [docs/ANNOUNCEMENTS.md](docs/ANNOUNCEMENTS.md) for that workflow. Routine factual announcements after completed project updates are in scope; a later instruction to hold publication, make a draft, or seek review takes precedence. This is not authorization for unrelated redesigns, account changes, social posts, or game edits.

- Work in a separate branch/worktree from current `origin/main`. Preserve other sessions' work and never force-push. If another announcement lands first, integrate its Markdown/assets and rebuild shared generated pages.
- Announce only verified work from the completed update. Distinguish playable, tested, pending owner review, planned, and historically verified claims. Never invent release dates or milestones. The project is independent, unofficial, solo, and noncommercial.
- `scripts/announce.py` imports a JSON handoff and multiple screenshots. Use a stable `update_id`; existing announcements are not overwritten. Source screenshots and game/research files are read-only. Internal evidence references stay in ignored local receipts.
- Edit `content/posts/`, `content/screenshots/`, or templates, then build. Do not hand-edit generated HTML. Check the generated post and media before publication.
- Keep CNAME, .nojekyll, robots, Umami settings, existing URLs, approved trailer, and original screenshots. Commit source, attachments, and generated output together.
- Pushing a validated commit to `main` deploys automatically. Verify the resulting public post, homepage listing, RSS and sitemap. An HTTP success on an older page alone is not proof that the new commit deployed.
