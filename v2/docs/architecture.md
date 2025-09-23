# Resume Orchestrator v2 – Architecture Notes

## Goals
- decouple resume content (blocks) from presentation (exporters)
- support data validation and linting workflows
- expose extension points for downstream automation (vacancy triage, chatbots)

## Components

### Data Store (`data_store.py`)
Central access layer for JSON blocks (`configs/blocks.json`). Handles I/O, caching, and validation errors. Future work: plug in remote sources (Notion, Google Sheets) via adapters.

### Loaders (`loaders.py`)
Utilities for reading YAML templates and binding them to strongly typed models. Responsible for version awareness and schema migrations.

### Filters (`filters.py`)
Reusable predicates (tag filters, year limits, visibility flags). Each filter is composable; templates define stacks of filters declaratively.

### Composer (`composer.py`)
Coordinates the pipeline: loads template, fetches matching blocks, normalises the order, and builds a `ComposedResume` object ready for export.

### Exporters (`exporters/`)
- `pdf.py`: wraps ReportLab to render layout (header, summary, skills, experience). Accepts theme overrides.
- `markdown.py`: renders the same structure in Markdown for quick edits.
- `base.py`: defines the protocol so new exporters (HTML, DOCX) can be registered easily.

### CLI (`cli.py`)
Built on top of Typer-style command groups (without external dependency) providing commands:
- `templates list`: inspect available templates and metadata
- `build`: generate output for a template with configurable exporters and output folder
- `preview`: dump Markdown to stdout for fast iteration
- `validate`: run schema checks on blocks/templates

## Data Flow

```
blocks.json ─┐
             │            ┌──────────┐
             ├─ loaders → │ template │
             │            └──────────┘
             │                  │
             │                  ▼
             │            filters.apply
             │                  │
             ▼                  ▼
        data_store → composer → exporters
```

## Future enhancements
- `tools/vacancy_digest.py`: NLP-driven extraction of keywords from vacancy descriptions to auto-suggest template overrides.
- Multi-page layouts with section weighting and whitespace heuristics.
- Telemetry/logging hooks for A/B-testing resume variants.

