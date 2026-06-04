"""Spot-check verification for the converted .drawio files.

For three sample files:
1. Parse as XML and assert well-formedness.
2. Walk the mxCell tree and find ``shape=mxgraph.mermaid;...;mermaidData=...``.
3. URL-decode the mermaidData payload and write it to a temp file.
4. (Caller diffs the temp file against the original .mmd if it still
   existed — since we deleted them, this script just prints the first
   200 chars of the decoded source so the user can eyeball it.)

Usage: python scripts/_verify_mermaid_drawio.py
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = [
    ROOT / "docs/diagrams/00-system-overview/system-context.drawio",
    ROOT / "docs/diagrams/05-capture-pipeline/capture-state-machine.drawio",
    ROOT / "docs/diagrams/03-data-model/er-marketplace.drawio",
]


def extract_mermaid_data(style: str) -> str:
    for token in style.split(";"):
        if token.startswith("mermaidData="):
            return token[len("mermaidData="):]
    raise ValueError("mermaidData not present in style")


def verify(path: Path) -> None:
    print(f"\n=== {path.relative_to(ROOT)} ===")
    text = path.read_text(encoding="utf-8")
    tree = ET.fromstring(text)
    assert tree.tag == "mxfile", f"root tag is {tree.tag!r}, expected 'mxfile'"
    diagram = tree.find("diagram")
    assert diagram is not None, "no <diagram>"
    name = diagram.attrib.get("name")
    diag_id = diagram.attrib.get("id")
    print(f"  XML well-formed: yes")
    print(f"  diagram name:    {name}")
    print(f"  diagram id:      {diag_id}")
    model = diagram.find("mxGraphModel")
    assert model is not None
    root_el = model.find("root")
    assert root_el is not None
    cells = root_el.findall("mxCell")
    print(f"  mxCell count:    {len(cells)}  (expect 3: id=0, id=1, id=2-mermaid)")
    mermaid_cell = next((c for c in cells if c.attrib.get("id") == "2"), None)
    assert mermaid_cell is not None, "no Mermaid cell (id=2)"
    style = mermaid_cell.attrib.get("style", "")
    assert "shape=mxgraph.mermaid" in style, "shape attribute missing"
    encoded = extract_mermaid_data(style)
    decoded = unquote(encoded)
    print(f"  mermaidData len: {len(encoded)} chars encoded, "
          f"{len(decoded)} chars decoded")
    first_lines = "\n  ".join(decoded.splitlines()[:5])
    # Re-encode to ASCII for the console — strip anything Windows cp1252
    # can't print so the preview never crashes the verifier.
    safe_preview = first_lines.encode("ascii", errors="replace").decode("ascii")
    print(f"  decoded preview:\n  {safe_preview}")


def main() -> int:
    for path in SAMPLES:
        if not path.is_file():
            print(f"MISSING: {path}", file=sys.stderr)
            return 1
        try:
            verify(path)
        except (AssertionError, ValueError, ET.ParseError) as exc:
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            return 2
    print("\nAll spot-checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
