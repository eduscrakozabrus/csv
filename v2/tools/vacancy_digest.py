#!/usr/bin/env python3
"""Stub for vacancy text analysis feeding resume templates."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

KEYWORDS = {
    "blockchain": {"tags": ["blockchain", "distributed-systems"], "template": "blockchain_startup"},
    "fintech": {"tags": ["fintech", "pci"], "template": "fintech_focused"},
    "sre": {"tags": ["monitoring", "reliability"], "template": "senior_devops_standard"},
}


def analyse(text: str):
    words = re.findall(r"[a-zA-Z0-9_-]+", text.lower())
    counts = Counter(words)
    suggestions = []
    for keyword, payload in KEYWORDS.items():
        if counts[keyword] > 0:
            suggestions.append(payload)
    return {
        "total_words": len(words),
        "top_terms": counts.most_common(10),
        "suggestions": suggestions,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyse vacancy text and suggest resume presets")
    parser.add_argument("file", type=Path, help="Vacancy text file")
    args = parser.parse_args()

    text = args.file.read_text(encoding="utf-8")
    result = analyse(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
