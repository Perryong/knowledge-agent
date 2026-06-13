# /raw-inbox-review

Review raw captures that have not been processed.

## Triggers

- `/raw-inbox-review`
- "review raw inbox"
- "process unprocessed raw files"

## Process

1. Scan `raw/**/metadata.md`.
2. Find captures where `status` is `captured` or `processed_to` is empty.
3. Group by category and age.
4. Recommend the next command:
   - `/url-dump` for articles and web pages.
   - `/knowledge-consolidation` for durable insight synthesis.
   - `/para-classify` for processed notes missing PARA metadata.
   - `/schema-compile` after a batch has been processed.
5. Produce a short review report in `00-inbox/raw-inbox-review-YYYY-MM-DD.md` when requested.
