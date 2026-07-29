"""Render Mermaid diagrams when Mermaid CLI is installed."""

from __future__ import annotations

import shutil
import subprocess

from src.config import settings

if __name__ == "__main__":
    command = shutil.which("mmdc")
    sources = sorted((settings.root / "docs").glob("*.mmd"))
    if not command:
        print(
            "Mermaid CLI is unavailable. Valid .mmd files were retained. "
            "Render with: npx -p @mermaid-js/mermaid-cli mmdc -i INPUT.mmd -o OUTPUT.svg"
        )
    else:
        for source in sources:
            output = source.with_suffix(".svg")
            subprocess.run([command, "-i", str(source), "-o", str(output)], check=True)
            print(output)
