# Hybrid Second Brain Operating Guide

COG remains the main framework. This hybrid layer adds the strongest capture and compilation patterns from `zhiwehu/second-brain` without weakening COG's existing agentic skills.

## Non-Negotiable Rule

Every external source must be preserved under `raw/` before an AI summary, analysis, PRD, story, booklet, or knowledge note is created.

This applies to URLs, articles, PDFs, screenshots, images, audio, video, meeting transcripts, job descriptions, trading charts, research papers, GitHub repositories, datasets, and uploaded files.

## Three-Layer Flow

1. `raw/` stores original or minimally transformed source material.
2. COG working folders store processed output:
   - `01-daily/` for briefs and reviews
   - `02-personal/`, `03-professional/`, and `04-projects/` for domain work
   - `05-knowledge/` for durable knowledge
3. `05-knowledge/schema/` stores extracted concepts and relationships for the lightweight knowledge graph.

## Raw Capture

Use this path convention:

```text
raw/<category>/YYYY-MM-DD-<slug>/
```

Each raw capture folder should contain the original source when possible plus `metadata.md`.

Minimum metadata:

```yaml
---
type: raw-source
category: articles
captured: YYYY-MM-DD HH:mm
source_url:
source_title:
source_author:
source_date:
status: captured
processed_to: []
tags: []
---
```

## PARA Inside COG

Keep COG's top-level folders. Add PARA only inside `05-knowledge/`:

- `05-knowledge/projects/` for active outcomes with deadlines.
- `05-knowledge/areas/` for ongoing responsibilities and standards.
- `05-knowledge/resources/` for reference topics and interests.
- `05-knowledge/archives/` for inactive or completed material.

PARA classification should be added to processed notes as frontmatter:

```yaml
para:
  type: project|area|resource|archive
  name: example
raw_sources:
  - raw/articles/YYYY-MM-DD-example/metadata.md
```

## Schema Compilation

Run schema compilation after a meaningful batch of notes has accumulated. Store concepts in `05-knowledge/schema/concepts/` and relationships in `05-knowledge/schema/relationships.md`.

Relationship format:

```markdown
- [[Concept A]] -- supports --> [[Concept B]]
- [[Concept A]] -- contradicts --> [[Concept C]]
- [[Tool A]] -- uses --> [[Method B]]
```

Core domains to extract:

- AI engineering concepts
- Career and job application entities
- Trading setups and market concepts
- Project ideas and product concepts
- People, teams, tools, companies, and repositories

## COG Skill Integration

Existing COG skills keep their behavior, with these additions:

- `/url-dump`, `/auto-research`, `/daily-brief`, `/meeting-transcript`, `/generate-prd`, and `/create-user-story` must create or reference raw captures before generating processed output.
- `/knowledge-consolidation` should read raw metadata links, preserve citations, classify durable notes into PARA, and update schema candidates.
- `/weekly-checkin` should review unprocessed raw captures and recommend `/raw-inbox-review` when needed.

## Commands

Hybrid command prompts live in `.claude/commands/`:

- `/raw-capture` preserves source material before processing.
- `/para-classify` classifies processed notes into COG's PARA folders.
- `/schema-compile` extracts concepts and relationships.
- `/raw-inbox-review` finds captured sources that still need processing.
