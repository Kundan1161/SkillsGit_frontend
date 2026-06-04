"""Fix stale ``.mmd`` cross-references inside the URL-encoded
mermaidData payload of each Mermaid-embedded .drawio file.

Some original .mmd files had comments like
``%% see deployment-target.mmd`` or
``%% endpoint they hit per docs/diagrams/02-backend-api/api-surface.mmd``.
The .mmd → .drawio conversion preserved those comments (they live
inside the Mermaid source, which is URL-encoded into the mermaidData
attribute), but the references now point to non-existent files.

This script decodes mermaidData, swaps ``.mmd`` -> ``.drawio`` inside,
re-encodes, and writes the .drawio back. Only touches files where the
encoded payload actually contains an ``.mmd`` substring.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS = ROOT / "docs/diagrams"

# Match ``mermaidData=<value>;`` in a style string. Value can contain
# any char except semicolon (style attribute separator) and the
# trailing semicolon is not part of the capture.
MERMAID_DATA_RE = re.compile(r'mermaidData=([^;"]*)(;)')


def fix_one(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    match = MERMAID_DATA_RE.search(text)
    if not match:
        return False
    encoded = match.group(1)
    decoded = unquote(encoded)
    if ".mmd" not in decoded:
        return False
    fixed_decoded = decoded.replace(".mmd", ".drawio")
    new_encoded = quote(fixed_decoded, safe="")
    new_text = text[: match.start(1)] + new_encoded + text[match.end(1):]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    fixed = 0
    for path in sorted(DIAGRAMS.rglob("*.drawio")):
        if fix_one(path):
            fixed += 1
            print(f"  fixed: {path.relative_to(ROOT)}")
    print(f"\nFixed {fixed} .drawio files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
