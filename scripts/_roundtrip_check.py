"""Roundtrip byte-compare: decode mermaidData from .drawio, compare to
the original .mmd content retrieved from git history."""
from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DRAWIO = ROOT / "docs/diagrams/00-system-overview/system-context.drawio"
SAMPLE_MMD_GIT = "HEAD:docs/diagrams/00-system-overview/system-context.mmd"


def get_mermaid_data_from_drawio(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ET.fromstring(text)
    cell = tree.find("./diagram/mxGraphModel/root/mxCell[@id='2']")
    assert cell is not None
    style = cell.attrib["style"]
    for token in style.split(";"):
        if token.startswith("mermaidData="):
            return unquote(token[len("mermaidData="):])
    raise ValueError("mermaidData missing")


def main() -> int:
    decoded = get_mermaid_data_from_drawio(SAMPLE_DRAWIO)
    git_show = subprocess.run(
        ["git", "-C", str(ROOT), "show", SAMPLE_MMD_GIT],
        capture_output=True, check=True,
    )
    # git show returns the blob bytes — typically LF-only since git
    # stores blobs as LF.
    git_bytes = git_show.stdout
    git_text = git_bytes.decode("utf-8")

    # The decoded string is what was actually read from disk at script
    # time (Python `read_text` normalizes \r\n → \n on Windows by default
    # when newline=None, which is the default). So compare normalized.
    decoded_norm = decoded.replace("\r\n", "\n")
    git_norm = git_text.replace("\r\n", "\n")

    print(f"decoded length (normalised LF):     {len(decoded_norm)}")
    print(f"git blob length (normalised LF):    {len(git_norm)}")
    print(f"identical:                          {decoded_norm == git_norm}")
    if decoded_norm != git_norm:
        # Show the first difference index for diagnosis.
        for i, (a, b) in enumerate(zip(decoded_norm, git_norm)):
            if a != b:
                print(f"first diff at index {i}: "
                      f"decoded={a!r} ({ord(a)}), git={b!r} ({ord(b)})")
                print(f"context decoded: ...{decoded_norm[max(0,i-20):i+20]!r}")
                print(f"context git:     ...{git_norm[max(0,i-20):i+20]!r}")
                break
        if len(decoded_norm) != len(git_norm):
            print(f"length diff: decoded ends "
                  f"{decoded_norm[len(git_norm):][:40]!r}, git ends "
                  f"{git_norm[len(decoded_norm):][:40]!r}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
