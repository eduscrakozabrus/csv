#!/usr/bin/env python3
"""Synchronise v1 JSON blocks with the new v2 bundle."""

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def merge_blocks(legacy_dir: Path, output: Path):
    personal = load_json(legacy_dir / "personal_info.json")
    summaries = load_json(legacy_dir / "professional_summaries.json")
    experience = load_json(legacy_dir / "experience_blocks.json")
    skills = load_json(legacy_dir / "technical_skills.json")

    bundle = {
        "personal_info": personal["personal_info"],
        "summaries": {k: v["content"] if isinstance(v, dict) and "content" in v else v for k, v in summaries["professional_summaries"].items()},
        "skills": {k: {"category": v["category"], "levels": v["skills"]} for k, v in skills["technical_skills"].items()},
        "experience": experience["experience_blocks"],
    }

    output.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description="Sync legacy v1 blocks into v2 bundle")
    parser.add_argument("legacy", type=Path, help="Path to v1 resume_blocks directory")
    parser.add_argument("--out", type=Path, default=Path("../configs/blocks.json"), help="Destination bundle path")
    args = parser.parse_args()

    path = merge_blocks(args.legacy, args.out)
    print(f"Merged blocks into {path}")


if __name__ == "__main__":
    main()
