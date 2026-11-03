---
name: soi-announcements
description: Add a factual Shadow of Israphel development announcement after a completed project update, with optional gameplay screenshot attachments. Use for the project's website update handoff, not unrelated announcements or game implementation.
---

# Shadow of Israphel update announcements

Use the established website repository, `https://github.com/Noahhubbs01/shadow-of-israphel-website`. On the owner's computer its primary checkout is `/home/daddy/Games/Shadow-of-Israphel-Adventure/website/github-pages`; elsewhere use a normal clone. Production is `https://shadowofisraphelproject.online/`, with GitHub Pages publishing `main` from the repository root.

Read `AGENTS.md` and `docs/ANNOUNCEMENTS.md` in the current website checkout before writing. They contain the handoff schema, screenshot importer, build checks, and publication procedure. The owner requested routine announcements after project updates, including attached screenshots, on 3 November 2026. Respect any later instruction to hold publication or prepare only a draft; do not infer authorization for unrelated design changes, social messages, or account/service mutations.

Use the completed update's actual handoff, test results, and captures. Write a concise personal note about what changed, what was checked, and what still needs work. Distinguish a private build from a public release, test success from owner acceptance, and historical evidence from adaptations. Do not invent progress, dates, release promises, endorsement, or claims about absence of AI assistance.

Use an isolated website branch/worktree from current `origin/main`. Prepare a local JSON handoff outside the public repository with a stable `update_id`, real date, title, summary, Markdown body, evidence references, and optional screenshots. Each screenshot needs an absolute source path, alt text, and caption. Copy only actual project captures; do not change originals or use generic/generated gameplay imagery. Check captures for private overlays before publication.

Run `scripts/announce.py --input <handoff.json> --ready` using the website's Python environment for a verified update; omit `--ready` for a draft. It copies originals and creates small previews without modifying source captures. It does not push. An existing update ID is left untouched, so retrying cannot silently replace an announcement. Evidence paths stay in ignored local receipts.

Build, run the authoring tests, and inspect the generated post and attached images on desktop/mobile. Commit intended source/assets/generated files together. Fetch again and integrate intervening announcements before a normal push to `main`; never force-push or overwrite another work mode's changes. Preserve hosting, analytics, existing URLs and approved footage. Verify the public post and its attachments after Pages updates, then report its public URL.

No background scheduler is installed by this skill. A work mode finishing an update performs the handoff. An already-running session can read `docs/ANNOUNCEMENTS.md` directly even if its skill catalog has not refreshed.
