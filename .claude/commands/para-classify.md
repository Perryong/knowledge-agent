# /para-classify

Classify processed notes into PARA inside `05-knowledge/`.

## Triggers

- `/para-classify`
- "classify this with PARA"
- "organize this note"

## PARA Rules

- Project: active outcome with a deadline.
- Area: ongoing responsibility or standard.
- Resource: topic of interest or reference.
- Archive: inactive, completed, or superseded material.

## Process

1. Read the note and its raw source metadata.
2. Choose exactly one primary PARA type.
3. Add `para` and `raw_sources` frontmatter if missing.
4. Move or copy durable knowledge into the matching `05-knowledge/<para-type>/` folder.
5. Keep COG domain files in `01-daily/`, `02-personal/`, `03-professional/`, and `04-projects/` when they are workflow records rather than durable knowledge.
