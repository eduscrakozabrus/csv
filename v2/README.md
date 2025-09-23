# Resume Orchestrator v2

## Overview

Version 2 of the resume builder evolves the existing PDF generator into a modular toolkit that can:
- model resume data as reusable blocks with validation
- apply layered filtering rules driven by YAML templates
- render to multiple formats (`pdf`, `markdown`) through pluggable exporters
- deliver a professional CLI for template discovery, previewing and batch generation
- prepare the ground for vacancy-aware recommendations and workflow automation

The implementation is organised as a Python package so it can be installed in editable mode and reused across projects.

```
v2/
├── README.md                 # High-level description and roadmap
├── pyproject.toml            # Package metadata and dependencies
├── configs/
│   ├── blocks.json           # Canonical data blocks (personal info, experience, skills)
│   └── templates/            # YAML templates that describe assembly rules
│       ├── blockchain_startup.yaml
│       ├── fintech_focused.yaml
│       └── senior_devops.yaml
├── docs/
│   └── architecture.md       # Design notes, extension points, backlog
├── src/
│   └── resume_orchestrator/  # Package with core modules, exporters, CLI
│       ├── __init__.py
│       ├── cli.py
│       ├── composer.py
│       ├── data_models.py
│       ├── data_store.py
│       ├── exporters/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── markdown.py
│       │   └── pdf.py
│       ├── filters.py
│       ├── loaders.py
│       └── settings.py
├── tools/
│   ├── vacancy_digest.py     # (stub) transforms vacancy text into filter hints
│   └── sync_blocks.py        # (stub) keeps configs in sync with legacy project
└── tests/
    └── test_filters.py       # Smoke tests for filtering logic
```

## Key ideas

1. **Config-first assembly** – resume layouts and selection heuristics live in `configs/templates/*.yaml`, enabling quick experiments without code changes.
2. **Typed data blocks** – JSON blocks loaded into Pydantic models (`data_models.py`) guarantee structure and surface validation errors early.
3. **Composable pipeline** – `composer.ResumeComposer` stitches together data, applies filters, and hands off to exporters.
4. **Multi-format output** – the exporter registry lets the CLI render to PDF, Markdown, JSON or any future format by dropping in new classes.
5. **Extensible tooling** – `tools/` is the place for automation (vacancy parsing, batch updates). Scripts share the same core package.

## Getting started

```bash
cd v2
python -m venv .venv
source .venv/bin/activate
pip install -e .
resume-cli templates list
resume-cli build blockchain_startup --export pdf --out builds/
resume-cli preview blockchain_startup --export markdown
```

The CLI automatically discovers templates, validates data against schemas, and writes output into the requested destination. PDF rendering uses ReportLab (already present in v1), Markdown output is helpful for manual edits or diff-friendly reviews.

## Roadmap highlights

- integrate with vacancy analysis reports and suggest best-fit templates
- add snapshot tests for exporters to catch layout changes
- introduce a thin web UI for previewing resumes in-browser
- expose automation hooks (e.g., GitHub Actions workflow) to refresh artefacts on data changes

