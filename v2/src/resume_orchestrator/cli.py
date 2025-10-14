from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from .composer import ResumeComposer
from .data_store import DataStore
from .exporters import registry
from .loaders import TemplateLoader
from .settings import Settings


def _load_context(config_dir: Path | None = None):
    settings = Settings.from_project_root()
    if config_dir:
        settings.configs_dir = config_dir

    store = DataStore(settings.blocks_path())
    loader = TemplateLoader(settings.templates_dir())
    composer = ResumeComposer(store.bundle())
    return settings, store, loader, composer


def app():
    parser = argparse.ArgumentParser(prog="resume-cli", description="Resume Orchestrator CLI")
    parser.add_argument("--config-dir", type=Path, help="Override configs directory", dest="config_dir")

    subparsers = parser.add_subparsers(dest="command")

    tpl_list = subparsers.add_parser("templates", help="List or show templates")
    tpl_list_sub = tpl_list.add_subparsers(dest="templates_command")

    tpl_list_sub.add_parser("list", help="List available templates")
    tpl_show = tpl_list_sub.add_parser("show", help="Show template details")
    tpl_show.add_argument("template", help="Template key")

    build = subparsers.add_parser("build", help="Compose resume and export to file")
    build.add_argument("template", help="Template key")
    build.add_argument("--export", choices=registry.available_formats(), default="pdf", help="Export format")
    build.add_argument("--out", type=Path, default=Path("builds"), help="Output directory")
    build.add_argument("--filename", type=str, help="Optional output filename")

    preview = subparsers.add_parser("preview", help="Render resume to stdout")
    preview.add_argument("template", help="Template key")
    preview.add_argument("--export", choices=[fmt for fmt in registry.available_formats() if fmt != "pdf"], default="markdown")

    subparsers.add_parser("validate", help="Validate data blocks and templates")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    settings, store, loader, composer = _load_context(getattr(args, "config_dir", None))

    command = args.command
    if command == "templates":
        if args.templates_command == "list":
            _cmd_templates_list(loader)
        elif args.templates_command == "show":
            _cmd_templates_show(loader, args.template)
        else:
            tpl_list.print_help()
    elif command == "build":
        _cmd_build(args, loader, composer)
    elif command == "preview":
        _cmd_preview(args, loader, composer)
    elif command == "validate":
        _cmd_validate(store, loader)
    else:
        parser.print_help()


def _cmd_templates_list(loader: TemplateLoader):
    names = loader.list_templates()
    for name in names:
        print(name)


def _cmd_templates_show(loader: TemplateLoader, template: str):
    config = loader.load(template)
    data = config.dict()
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _cmd_build(args, loader: TemplateLoader, composer: ResumeComposer):
    config = loader.load(args.template)
    resume = composer.compose(config)

    exporter = registry.create(args.export)
    args.out.mkdir(parents=True, exist_ok=True)
    file_ext = args.export if args.export != "markdown" else "md"

    filename: str
    if args.filename:
        filename = args.filename
        if not filename.lower().endswith(f".{file_ext}"):
            filename = f"{filename}.{file_ext}"
    else:
        custom = None
        if config.output and isinstance(config.output, dict):
            custom_value = config.output.get("filename")
            if isinstance(custom_value, str) and custom_value.strip():
                custom = custom_value.strip()
        if custom:
            filename = custom
            if not filename.lower().endswith(f".{file_ext}"):
                filename = f"{filename}.{file_ext}"
        else:
            safe_name = config.template.replace("_", "-")
            filename = f"{safe_name}.{file_ext}"
    destination = args.out / filename

    output = exporter.export(resume, destination)
    print(f"✅ Created {args.export} at {output}")


def _cmd_preview(args, loader: TemplateLoader, composer: ResumeComposer):
    config = loader.load(args.template)
    resume = composer.compose(config)
    exporter = registry.create(args.export)
    content = exporter.export(resume, None)
    print(content)


def _cmd_validate(store: DataStore, loader: TemplateLoader):
    errors: list[str] = []
    try:
        store.bundle()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Blocks validation failed: {exc}")

    for config in loader.iter_configs():
        # ensure summary exists by instantiating composer later; here we just check fields
        if not config.skill_categories:
            errors.append(f"Template {config.template} has no skill categories")

    if errors:
        print("Validation issues detected:")
        for issue in errors:
            print(f"- {issue}")
    else:
        print("All blocks and templates look good.")


if __name__ == "__main__":
    app()
