# /raw-capture

Preserve source material before any AI processing.

## Triggers

- `/raw-capture`
- "save this raw source"
- "capture this before processing"
- "add this to raw"

## Process

1. Determine the source category: articles, pdfs, images, audio, video, documents, datasets, github, trading, jobs, research, meetings, or ideas.
2. Create `raw/<category>/YYYY-MM-DD-<slug>/`.
3. Save or reference the original source in that folder.
4. Create `metadata.md`.
5. Do not summarize until the raw capture exists.

## Metadata Template

```markdown
---
type: raw-source
category: <category>
captured: YYYY-MM-DD HH:mm
source_url:
source_title:
source_author:
source_date:
status: captured
processed_to: []
tags: []
---

# Raw Capture: <Source Title>

## Source

- URL:
- Local file:
- Captured from:

## Notes

Original user context or capture reason.
```
