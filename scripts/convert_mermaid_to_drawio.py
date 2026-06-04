"""Convert Mermaid-source `.drawio` files (the broken Mode-A wrappers) into
SVG-rendered, embedded-image `.drawio` files (Mode-B) that actually render
in draw.io / app.diagrams.net.

Background
----------
The previous version of this script produced a ``shape=mxgraph.mermaid``
cell with the Mermaid source URL-encoded into ``mermaidData``. draw.io 24+
does **not** render that shape format — it opens to an empty/broken cell.

This rewrite renders each Mermaid source to a PNG (via the local
``mmdc`` CLI from ``@mermaid-js/mermaid-cli``), then wraps the PNG as a
``shape=image`` cell with the PNG embedded as a base64 data URI. The
original Mermaid source is preserved inside the same ``.drawio`` file as a
hidden cell (positioned at large negative coordinates so it doesn't show
on the canvas) — that way the file remains the canonical authoring artifact
and this script can re-render it later without losing the source.

Critical encoding rule
----------------------
mxgraph parses style strings by splitting on ``;``. A raw data URI
(``data:image/png;base64,...``) contains a ``;`` which breaks the parser.
Workaround: replace ``;`` with ``%3B`` *and* place ``image=`` as the LAST
key in the style (no trailing semicolon). Browsers still decode the data
URI correctly (Chrome's URL parser tolerates ``%3B`` inside data URIs).
Verified empirically against viewer-static.min.js (the renderer used by
both the draw.io viewer and the desktop/web editor).

Files
-----
Three diagrams are skipped (they ship as hand-built native mxgraph cells
and the conversion would replace them with a rasterised version):

* ``docs/diagrams/00-system-overview/high-level-architecture.drawio``
* ``docs/diagrams/03-data-model/er-full.drawio``
* ``docs/diagrams/04-vault-and-obsidian/composition-merge.drawio``

The remaining 37 ``.drawio`` files under ``docs/diagrams/`` are
re-generated in place.

Requirements
------------
* Python 3.10+
* Node.js 20+
* ``@mermaid-js/mermaid-cli`` installed (e.g.
  ``npm install -g @mermaid-js/mermaid-cli``); the ``mmdc`` command must
  be on ``PATH``. Falls back to ``npx -y -p @mermaid-js/mermaid-cli mmdc``
  if ``mmdc`` isn't on PATH (slower per invocation).

Usage
-----
    python scripts/convert_mermaid_to_drawio.py [--dry-run] [--only NAME]

    --dry-run     Print plan without writing files
    --only NAME   Process a single file by filename (e.g. system-context.drawio)
    --keep-tmp    Keep tmp render dir for debugging

Re-run is safe: it overwrites existing Mode-B files. The 3 Mode-C native
diagrams listed above are never touched.
"""

from __future__ import annotations

import argparse
import base64
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote
from xml.sax.saxutils import escape as xml_escape

# ── Constants ───────────────────────────────────────────────────────────

# 3 hand-crafted native mxgraph .drawio files — never touched.
NATIVE_DRAWIO = {
    "high-level-architecture.drawio",
    "er-full.drawio",
    "composition-merge.drawio",
}

# Per-diagram-type render width hints (controls mmdc -w). Larger types get
# more width so labels stay readable; PNGs are scaled-down by draw.io's
# image rendering anyway.
WIDTH_BY_TYPE: dict[str, int] = {
    "erDiagram":         3000,
    "sequenceDiagram":   2200,
    "classDiagram":      2400,
    "stateDiagram-v2":   2200,
    "stateDiagram":      2200,
    "flowchart":         2400,
    "graph":             2400,
    "gantt":             2800,
    "pie":               1600,
    "journey":           2400,
    "mindmap":           2200,
    "gitGraph":          2400,
    "requirementDiagram":2400,
}
DEFAULT_WIDTH = 2400

# mmdc invocation timeout per file (Puppeteer can be slow on cold start).
MMDC_TIMEOUT_SECS = 180

# Off-canvas coordinates for the hidden source cell (the cell is positioned
# here so it doesn't appear next to the visible image even though style
# ``visible=0`` *should* hide it; belt + suspenders).
HIDDEN_X, HIDDEN_Y = -5000, -5000


# ── Helpers ─────────────────────────────────────────────────────────────


def diagram_title(stem: str) -> str:
    """``capture-state-machine`` -> ``Capture state machine``."""
    return stem.replace("-", " ").replace("_", " ").capitalize()


def detect_mermaid_type(source: str) -> str:
    """First non-comment, non-blank token of the Mermaid source.

    Used to pick a render width — flowcharts and ER diagrams need more.
    """
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        return line.split()[0]
    return ""


def render_width_for(mermaid_type: str) -> int:
    """Pick mmdc -w based on Mermaid diagram type."""
    if mermaid_type in WIDTH_BY_TYPE:
        return WIDTH_BY_TYPE[mermaid_type]
    base = mermaid_type.split("-")[0]
    if base in WIDTH_BY_TYPE:
        return WIDTH_BY_TYPE[base]
    return DEFAULT_WIDTH


def extract_mermaid_from_drawio(xml: str) -> str | None:
    """Decode the ``mermaidData=`` style attribute from a Mode-A .drawio.

    Returns the URL-decoded Mermaid source, or None if no mermaidData found
    (e.g. for a native Mode-C file).
    """
    # mermaidData is in a style attribute, terminated by ``;`` or quote
    m = re.search(r'mermaidData=([^;"]+)', xml)
    if not m:
        return None
    return unquote(m.group(1))


def extract_mermaid_from_hidden_cell(xml: str) -> str | None:
    """Decode Mermaid source from a Mode-B hidden cell (for re-runs).

    The hidden cell has style containing ``visible=0`` and its ``value``
    attribute is the XML-escaped Mermaid source. Looks for any text cell
    at the off-canvas coords we use.
    """
    # Look for the hidden source cell with our off-canvas geometry
    pattern = (
        r'<mxCell\s+[^>]*value="([^"]*)"\s+style="[^"]*visible=0[^"]*"\s+vertex="1"'
    )
    m = re.search(pattern, xml)
    if not m:
        return None
    # XML-unescape (just &amp; &lt; &gt; &quot; &apos;)
    val = m.group(1)
    val = (val.replace("&amp;", "&")
              .replace("&lt;", "<")
              .replace("&gt;", ">")
              .replace("&quot;", '"')
              .replace("&apos;", "'"))
    return val


def recover_mermaid_from_fixed_sources(drawio_path: Path, repo_root: Path) -> str | None:
    """Prefer hand-fixed sources at docs/diagrams/_sources/<basename>.mmd.

    These exist for the 12 diagrams whose originals contain Mermaid syntax
    no current parser accepts (sequenceDiagram <br/> in participant aliases,
    HTML entities in flowchart labels, etc.). The fixes preserve all
    architectural information from the originals — only the syntax is
    restructured to be mmdc-compatible.
    """
    src = repo_root / "docs" / "diagrams" / "_sources" / (drawio_path.stem + ".mmd")
    if src.is_file():
        try:
            return src.read_text(encoding="utf-8")
        except OSError:
            return None
    return None


def recover_mermaid_from_git(drawio_path: Path, repo_root: Path) -> str | None:
    """Recover the original clean Mermaid source from git commit a412721.

    The Mode-A round-trip mangled multi-byte unicode chars (em-dash → `�`).
    Commit a412721 holds the pristine .mmd files before that conversion.
    Returns None if the file wasn't in that commit (e.g. new diagrams).
    """
    rel = drawio_path.relative_to(repo_root).as_posix()
    mmd_path = rel.rsplit(".", 1)[0] + ".mmd"
    try:
        result = subprocess.run(
            ["git", "show", f"a412721:{mmd_path}"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def find_mmdc_command() -> list[str]:
    """Return the command tokens to run mmdc, preferring a PATH install."""
    if shutil.which("mmdc"):
        return ["mmdc"]
    # Fall back to npx (slower per invocation)
    if shutil.which("npx") or shutil.which("npx.cmd"):
        return ["npx", "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc"]
    raise RuntimeError(
        "Neither `mmdc` nor `npx` found on PATH. "
        "Install Node.js + run: `npm install -g @mermaid-js/mermaid-cli`."
    )


_MMDC_CMD: list[str] | None = None


def mmdc_cmd() -> list[str]:
    global _MMDC_CMD
    if _MMDC_CMD is None:
        _MMDC_CMD = find_mmdc_command()
    return _MMDC_CMD


def sanitize_for_mmdc(source: str, mermaid_type: str) -> str:
    """Strip Mermaid features that the bundled mmdc parser doesn't tolerate.

    Two known issues with the originals:

    1. Leading ``%%`` comment lines that contain unicode em-dashes or
       backticks confuse mmdc's lexer (it expects the diagram declaration
       on line 1). After the diagram type is declared, comments parse fine.
       Fix: strip the leading comment+blank block up to the first
       non-comment, non-blank line.

    2. ``<br/>`` inside ``sequenceDiagram`` message labels is rejected by
       mmdc's sequence parser (works in flowcharts; not in sequence
       diagrams). Fix: replace ``<br/>`` with newline escape (``\\n``)
       only for sequenceDiagram sources.

    The original (un-sanitized) source is what we store in the hidden cell
    of the .drawio — sanitization happens only for the mmdc render path.
    """
    # 1. Strip leading comment + blank block
    lines = source.splitlines()
    first_real = 0
    for i, raw in enumerate(lines):
        line = raw.strip()
        if line and not line.startswith("%%"):
            first_real = i
            break
    stripped = "\n".join(lines[first_real:])

    # 2. Sequence-diagram <br/> sanitization
    if mermaid_type.startswith("sequenceDiagram"):
        # Mermaid sequenceDiagram supports <br /> only inside notes (since
        # v10+), not inside message arrows. Safer to swap for an escape:
        # mmdc's sequence parser treats \n in double-quoted strings as
        # newline. For unquoted message text, fall back to a space.
        stripped = stripped.replace("<br/>", "\\n").replace("<br />", "\\n")
        stripped = stripped.replace("<br>", "\\n")
        # &nbsp; isn't recognized either
        stripped = stripped.replace("&nbsp;", " ")

    return stripped


_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def _http_get_png(url: str, timeout: int = 30) -> bytes:
    """GET a URL and return body bytes if Content-Type is PNG."""
    import urllib.request
    import urllib.error

    req = urllib.request.Request(
        url,
        headers={"User-Agent": _BROWSER_UA, "Accept": "image/png,*/*"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        msg = exc.read().decode("utf-8", errors="replace")[:200] if hasattr(exc, "read") else ""
        raise RuntimeError(f"HTTP {exc.code}: {msg}")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"network: {exc}")
    if not data.startswith(b"\x89PNG"):
        head = data[:120].decode("utf-8", errors="replace")
        raise RuntimeError(f"non-PNG response: {head!r}")
    return data


def _http_post_png(url: str, body: bytes, timeout: int = 30) -> bytes:
    import urllib.request
    import urllib.error

    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "User-Agent": _BROWSER_UA,
            "Content-Type": "text/plain",
            "Accept": "image/png,*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        msg = exc.read().decode("utf-8", errors="replace")[:200] if hasattr(exc, "read") else ""
        raise RuntimeError(f"HTTP {exc.code}: {msg}")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"network: {exc}")
    if not data.startswith(b"\x89PNG"):
        head = data[:120].decode("utf-8", errors="replace")
        raise RuntimeError(f"non-PNG response: {head!r}")
    return data


def render_png_via_kroki(mermaid_source: str) -> bytes:
    """Fallback A: kroki.io REST. Browser UA required (Cloudflare 1010)."""
    return _http_post_png(
        "https://kroki.io/mermaid/png", mermaid_source.encode("utf-8")
    )


def render_png_via_mermaid_ink(mermaid_source: str) -> bytes:
    """Fallback B: mermaid.ink GET API. Encodes source as base64-pako."""
    import zlib

    # mermaid.ink expects pako-deflated, base64-url-encoded source
    compressed = zlib.compress(mermaid_source.encode("utf-8"), 9)
    b64 = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return _http_get_png(f"https://mermaid.ink/img/pako:{b64}?type=png")


def render_png(mermaid_source: str, width: int, tmpdir: Path) -> bytes:
    """Render Mermaid source to PNG bytes via mmdc; fall back to kroki on failure."""
    in_file = tmpdir / "input.mmd"
    out_file = tmpdir / "output.png"
    mtype = detect_mermaid_type(mermaid_source)
    sanitized = sanitize_for_mmdc(mermaid_source, mtype)
    in_file.write_text(sanitized, encoding="utf-8")
    cmd = mmdc_cmd() + [
        "-i", str(in_file),
        "-o", str(out_file),
        "-w", str(width),
        "-b", "white",
    ]
    # shell=True on Windows so .cmd shims (npm-installed binaries) work
    use_shell = sys.platform == "win32"
    result = subprocess.run(
        cmd,
        capture_output=True,
        timeout=MMDC_TIMEOUT_SECS,
        shell=use_shell,
    )
    if result.returncode != 0 or not out_file.exists():
        # mmdc choked. Try kroki.io, then mermaid.ink — both use newer
        # Mermaid versions that may accept syntax mmdc rejected. Use the
        # ORIGINAL source (not the sanitized one).
        errors = []
        try:
            return render_png_via_kroki(mermaid_source)
        except RuntimeError as exc:
            errors.append(f"kroki: {exc}")
        try:
            return render_png_via_mermaid_ink(mermaid_source)
        except RuntimeError as exc:
            errors.append(f"mermaid.ink: {exc}")
        stderr = result.stderr.decode("utf-8", errors="replace")[:300]
        raise RuntimeError(
            f"mmdc exit={result.returncode}; all fallbacks failed: "
            f"{' | '.join(errors)}\nmmdc stderr: {stderr}"
        )
    return out_file.read_bytes()


def png_dimensions(png: bytes) -> tuple[int, int]:
    """Extract image dimensions from a PNG's IHDR chunk."""
    if not png.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG")
    w, h = struct.unpack(">II", png[16:24])
    return (int(w), int(h))


def build_drawio_xml(
    png: bytes,
    mermaid_source: str,
    diagram_name: str,
) -> str:
    """Build a valid Mode-B .drawio with PNG image cell + hidden Mermaid.

    Critical: data URI's ``;`` is replaced with ``%3B`` and ``image=`` is
    the LAST style key (with no trailing ``;``). This is the only encoding
    that draw.io's style parser accepts (verified empirically — see
    module docstring).
    """
    w, h = png_dimensions(png)
    # Add a 40-px margin around the image on the page
    page_w = w + 80
    page_h = h + 80

    png_b64 = base64.b64encode(png).decode("ascii")
    # ; → %3B inside the data URI. comma after mimetype is fine (not a style sep).
    data_uri = f"data:image/png%3Bbase64,{png_b64}"

    # XML-escape the diagram name
    safe_name = xml_escape(diagram_name, {'"': "&quot;"})
    # XML-escape the Mermaid source for use as a `value=""` attribute
    safe_mmd = xml_escape(mermaid_source, {'"': "&quot;", "'": "&apos;"})

    diagram_id = f"skg-png-{uuid.uuid4().hex[:12]}"

    # Image cell style: image= MUST be last and unterminated
    style_img = (
        "shape=image;html=1;imageAspect=1;"
        "verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;"
        f"image={data_uri}"
    )
    # XML-escape style for use in style="..." attribute
    style_img_esc = xml_escape(style_img, {'"': "&quot;"})

    # Hidden source cell — visible=0 + off-canvas coords (belt + suspenders)
    style_src = (
        "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;"
        "fontFamily=monospace;fontSize=10;visible=0;strokeColor=none;fillColor=none;"
    )
    style_src_esc = xml_escape(style_src, {'"': "&quot;"})

    return (
        f'<mxfile host="app.diagrams.net" agent="skillsgit-arch" '
        f'version="24.7.17" type="device">\n'
        f'  <diagram name="{safe_name}" id="{diagram_id}">\n'
        f'    <mxGraphModel dx="1422" dy="757" grid="1" gridSize="10" '
        f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
        f'page="1" pageScale="1" pageWidth="{page_w}" pageHeight="{page_h}" '
        f'math="0" shadow="0">\n'
        f'      <root>\n'
        f'        <mxCell id="0" />\n'
        f'        <mxCell id="1" parent="0" />\n'
        f'        <mxCell id="2" value="" style="{style_img_esc}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="40" y="40" width="{w}" height="{h}" as="geometry" />\n'
        f'        </mxCell>\n'
        f'        <mxCell id="3" value="{safe_mmd}" style="{style_src_esc}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{HIDDEN_X}" y="{HIDDEN_Y}" width="800" height="400" as="geometry" />\n'
        f'        </mxCell>\n'
        f'      </root>\n'
        f'    </mxGraphModel>\n'
        f'  </diagram>\n'
        f'</mxfile>\n'
    )


# ── Main loop ───────────────────────────────────────────────────────────


def iter_drawio_files(diagrams_dir: Path, only: str | None) -> Iterable[Path]:
    """Yield .drawio files to process (excluding native ones)."""
    for p in sorted(diagrams_dir.rglob("*.drawio")):
        if p.name in NATIVE_DRAWIO:
            continue
        if only and p.name != only:
            continue
        yield p


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=None,
        help="Repo root (defaults to one level above this script).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without writing.",
    )
    parser.add_argument(
        "--only",
        default=None,
        help="Process only the file with this name (e.g. system-context.drawio).",
    )
    parser.add_argument(
        "--keep-tmp",
        action="store_true",
        help="Keep tmp render dirs for debugging.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else script_dir.parent
    diagrams_dir = root / "docs" / "diagrams"
    if not diagrams_dir.is_dir():
        print(f"ERROR: {diagrams_dir} does not exist.", file=sys.stderr)
        return 1

    files = list(iter_drawio_files(diagrams_dir, args.only))
    if not files:
        print(f"No .drawio files matched under {diagrams_dir}.")
        return 0

    # Sanity-check mmdc up-front (unless dry-run)
    if not args.dry_run:
        try:
            _ = mmdc_cmd()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    converted: list[Path] = []
    errors: list[tuple[Path, str]] = []
    no_source: list[Path] = []
    total_size = 0
    max_size = 0
    max_size_path: Path | None = None

    t_start = time.time()
    for i, drawio in enumerate(files, 1):
        rel = drawio.relative_to(root)
        try:
            xml = drawio.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append((drawio, f"read failed: {exc}"))
            continue

        # Lookup order:
        # 1. Hand-fixed sources at docs/diagrams/_sources/<name>.mmd
        #    (mandatory for the 12 diagrams that mmdc can't parse from
        #    their git originals).
        # 2. Git-recovered original from commit a412721 (clean unicode).
        # 3. In-file extraction (Mode-A mermaidData or Mode-B hidden cell).
        mermaid = recover_mermaid_from_fixed_sources(drawio, root)
        if mermaid is None:
            mermaid = recover_mermaid_from_git(drawio, root)
        if mermaid is None:
            mermaid = extract_mermaid_from_drawio(xml)
        if mermaid is None:
            mermaid = extract_mermaid_from_hidden_cell(xml)
        if mermaid is None:
            no_source.append(drawio)
            print(f"  [{i:2}/{len(files)}] SKIP (no Mermaid source): {rel}")
            continue

        mtype = detect_mermaid_type(mermaid)
        width = render_width_for(mtype)
        diagram_name = diagram_title(drawio.stem)

        if args.dry_run:
            print(f"  [{i:2}/{len(files)}] DRY: {rel}  type={mtype}  w={width}  src={len(mermaid)}c")
            continue

        t0 = time.time()
        tmp = Path(tempfile.mkdtemp(prefix="skg-mmdc-"))
        try:
            try:
                png = render_png(mermaid, width=width, tmpdir=tmp)
            except subprocess.TimeoutExpired:
                errors.append((drawio, f"mmdc timeout after {MMDC_TIMEOUT_SECS}s"))
                print(f"  [{i:2}/{len(files)}] FAIL: {rel}  (mmdc timeout)")
                continue
            except RuntimeError as exc:
                errors.append((drawio, str(exc).splitlines()[0]))
                print(f"  [{i:2}/{len(files)}] FAIL: {rel}  ({str(exc).splitlines()[0][:120]})")
                continue

            png_w, png_h = png_dimensions(png)
            new_xml = build_drawio_xml(png, mermaid, diagram_name)
            try:
                drawio.write_text(new_xml, encoding="utf-8")
            except OSError as exc:
                errors.append((drawio, f"write failed: {exc}"))
                continue

            size = drawio.stat().st_size
            total_size += size
            if size > max_size:
                max_size = size
                max_size_path = drawio
            converted.append(drawio)
            dt = time.time() - t0
            print(
                f"  [{i:2}/{len(files)}] OK   {rel}  "
                f"type={mtype} {png_w}x{png_h} {size//1024}KB {dt:.1f}s"
            )
        finally:
            if not args.keep_tmp:
                shutil.rmtree(tmp, ignore_errors=True)

    dt_total = time.time() - t_start
    avg_size = total_size // len(converted) if converted else 0

    print()
    print("Summary")
    print("-------")
    print(f"  Files processed:  {len(files)}")
    print(f"  Converted (OK):   {len(converted)}")
    print(f"  Skipped (no src): {len(no_source)}")
    print(f"  Errors:           {len(errors)}")
    print(f"  Elapsed:          {dt_total:.1f}s "
          f"({dt_total/max(1,len(files)):.1f}s/file avg)")
    if converted:
        print(f"  Avg file size:    {avg_size//1024}KB")
        if max_size_path is not None:
            print(f"  Max file size:    {max_size//1024}KB "
                  f"({max_size_path.relative_to(root)})")
    if no_source:
        print("\nFiles with no Mermaid source (need manual attention):")
        for p in no_source:
            print(f"  - {p.relative_to(root)}")
    if errors:
        print("\nErrors:")
        for path, msg in errors:
            print(f"  - {path.relative_to(root)}: {msg}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
