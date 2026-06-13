# /schema-compile

Compile a lightweight knowledge graph from COG notes.

## Triggers

- `/schema-compile`
- "compile my second brain schema"
- "build the knowledge graph"
- "extract concepts and relationships"

## Process

1. Scan new or changed notes in `01-daily/`, `02-personal/`, `03-professional/`, `04-projects/`, and `05-knowledge/`.
2. Read linked raw metadata from `raw/` when available.
3. Extract concepts, entities, people, tools, companies, repositories, trading setups, job entities, product ideas, and AI engineering methods.
4. Create or update concept files in `05-knowledge/schema/concepts/`.
5. Add graph edges to `05-knowledge/schema/relationships.md`.
6. Write a compilation report to `05-knowledge/schema/logs/YYYY-MM-DD-schema-compile.md`.

## Relationship Types

- `supports`
- `contradicts`
- `influences`
- `uses`
- `part_of`
- `derived_from`
- `related_to`
