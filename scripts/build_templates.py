#!/usr/bin/env python3
"""Build base DOCX templates programmatically."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from template_builder.builder import TemplateBuilder


def main() -> None:
    settings = get_settings()
    builder = TemplateBuilder()
    paths = builder.build_all_base_templates(settings.templates_dir)
    print("Generated templates:")
    for name, path in paths.items():
        print(f"  {name} -> {path}")


if __name__ == "__main__":
    main()
