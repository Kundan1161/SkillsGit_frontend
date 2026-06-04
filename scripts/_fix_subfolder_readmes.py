"""One-shot rewrite of every docs/diagrams/*/README.md after the
.mmd -> .drawio conversion.

For each subfolder README:

1. Global replace ``.mmd`` -> ``.drawio`` (covers section headers, link
   refs, and prose mentions).
2. Replace any "How to view"-style block that walks through the
   ``Extras -> Edit Diagram`` / ``Insert -> Advanced -> Mermaid`` /
   ``Paste the contents of any .drawio file`` workflow with a short
   pointer to the master README.
3. Replace the prose phrase "render .drawio files inline" (which we
   inadvertently created via the .mmd -> .drawio swap and is FALSE for
   GitHub) with the truth — GitHub does not render .drawio inline.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS = ROOT / "docs/diagrams"

# New "How to view" block to use in every subfolder.
NEW_HOW_TO_VIEW = """## How to view

Every file in this folder is a `.drawio` file. Open it in the draw.io
desktop app or at [app.diagrams.net](https://app.diagrams.net), or
render it inline in VS Code with the
[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
extension. See [`docs/diagrams/README.md`](../README.md#how-to-view-these-diagrams)
for the full guide and the two flavours of `.drawio` in this repo
(native mxgraph vs Mermaid-embedded).
"""


def fix_one(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original

    # Step 1: global .mmd -> .drawio swap.
    text = text.replace(".mmd", ".drawio")

    # Step 2: cut out any old "How to view" / "How to open" block, plus
    # anything that mentions the Mermaid-paste workflow, and replace
    # with the new pointer block. Multiple subfolder READMEs use
    # slightly different headings (## How to view, ## How to open
    # these diagrams), so handle both.
    #
    # Strategy: find every "## How to view" or "## How to open" header
    # and replace through the next "## " (or end of file) with the new
    # block.
    pattern = re.compile(
        r"^##\s+How to (?:view|open)[^\n]*\n.*?(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    if pattern.search(text):
        text = pattern.sub(NEW_HOW_TO_VIEW + "\n", text)
    else:
        # No existing "How to view" block — leave as is. (Some folders
        # may not have one.)
        pass

    # Step 3: any leftover prose referring to .drawio rendering inline
    # in GitHub (which is wrong — `.mmd` rendered inline, `.drawio`
    # does not). After the global swap in step 1 these become
    # incorrect. We already nuked them via step 2 for the standard
    # blocks; this is a defensive sweep for inline prose mentions.
    text = re.sub(
        r"`?\.drawio`?\s+files\s+render\s+inline\s+in\s+GitHub[^\.]*\.",
        "`.drawio` files do not render inline in GitHub; open them in "
        "draw.io or VS Code (see master README).",
        text,
    )
    text = re.sub(
        r"Open\s+(?:any\s+)?`?\.drawio`?\s+file\s+in\s+the\s+GitHub\s+UI\.\s*"
        r"It\s+renders\s+inline\.?",
        "Open any `.drawio` file in draw.io (desktop or "
        "[app.diagrams.net](https://app.diagrams.net)) — or use the "
        "VS Code Draw.io Integration extension.",
        text,
    )

    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    skipped = 0
    for readme in sorted(DIAGRAMS.glob("*/README.md")):
        if fix_one(readme):
            changed += 1
            print(f"  fixed: {readme.relative_to(ROOT)}")
        else:
            skipped += 1
            print(f"  no change: {readme.relative_to(ROOT)}")
    print(f"\nFixed {changed} READMEs, skipped {skipped}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
