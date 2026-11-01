---
name: psy-tours-blog-post
description: Guide the Psy-Tours owner through drafting, previewing, revising and preparing a new French blog post in this repository.
---

# New Psy-Tours blog post

Work in this repository on `preview` and follow its `AGENTS.md`. The owner can describe an idea in ordinary language; handle the files and commands yourself. Keep the original site styling, language and attribution. Do not invent clinical claims, credentials, prices, sources or author/photo credits.

## Resuming a writing conversation

When the owner resumes an unfinished article-writing conversation, automatically run `rtk proxy python3 scripts/blog_preview.py resume` before continuing. It reuses the active managed server or restarts the last draft, preferring the same local URL when its port is free. Give the owner the printed URL, especially if the port changed. If no draft was recorded, recover the slug from the conversation and use `start slug`; if multiple drafts make the intended one unclear, ask which one. Do not restart a finished or unrelated task.

## Writing wizard

1. Identify the topic, intended audience, main message and whether the owner supplies text or wants a proposed draft. Infer sensible defaults and ask only for missing decisions; group short questions. Suggest a French title, description and outline for review when useful. Avoid demanding technical input.
2. Create a unique ASCII slug and run `rtk npm run new -- post slug "Titre"`. Write the article in `content/posts/slug.md`. Keep `draft: true` during review. Preserve `additionalPost: true`, the local permalink and the original-theme layout. Set the real author, date, description and `categories` as objects with `slug` and `title`; use existing category slugs in `content/archives/`. Use approved local media and meaningful alt text, or agree on an image with the owner. Do not publish the favicon as a cover by accident. Credit any supplied image and guest author as appropriate.
3. Start the isolated preview with `rtk proxy python3 scripts/blog_preview.py start slug`. Give the owner the printed URL. This serves the selected draft while leaving it out of ordinary builds, collections, feed and sitemap. It refreshes after edits; inspect the article on desktop and mobile. Do not start or stop the separate server on port 8080. If an unrelated managed blog preview is running, explain and coordinate rather than silently stopping it.
4. Present the draft or a concise summary, accept natural-language revisions and update the same file. The preview refreshes automatically. Use `rtk proxy python3 scripts/blog_preview.py touch` if extended discussion or editing is active without browser interaction. The managed server stops after 30 minutes without browser activity or draft edits; `status` and `stop` are also available. Never kill a process merely because it uses a familiar port.
5. When the owner approves the content for inclusion in a build, set `draft: false`, verify author/date/categories/image and run `rtk npm run check`. Check the article and relevant blog/category lists at desktop and mobile sizes. Local build approval does not authorize a Git commit, push or publication: follow the owner's explicit instructions and `AGENTS.md` for each. Never push or deploy without explicit authorization.
6. Stop the managed preview with `rtk proxy python3 scripts/blog_preview.py stop` when this writing task ends, including after a requested commit or push, unless the owner explicitly asks to keep it running. The server also stops on long inactivity. Report the draft or article path, preview/review status, checks, and whether it was committed or published.

If asked to leave the post as a draft, keep `draft: true`; do not activate it merely to obtain a preview. When an approved post needs publication, distinguish the local build, GitHub preview and production, and do not move work to `main` without explicit authorization.
