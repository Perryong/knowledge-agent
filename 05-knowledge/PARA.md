# PARA in COG Knowledge

COG keeps its existing top-level folders. PARA is used inside `05-knowledge/` for durable knowledge organization.

- `projects/` contains active outcomes with deadlines.
- `areas/` contains ongoing responsibilities and standards.
- `resources/` contains reference material and topics of interest.
- `archives/` contains completed, inactive, or superseded material.

Processed notes should include frontmatter linking back to raw sources:

```yaml
para:
  type: project|area|resource|archive
  name: example
raw_sources:
  - raw/articles/YYYY-MM-DD-example/metadata.md
```
