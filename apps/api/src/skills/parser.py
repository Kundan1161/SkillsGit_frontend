"""skills.md parser stub.

Phase 0 only exposes :func:`split_frontmatter`. Round-trip compilation from
the visual builder graph back to markdown lands in
``prompts/skill-creator/01-visual-builder.md`` (Phase 3).
"""

from __future__ import annotations

from typing import Any

import frontmatter


def split_frontmatter(content: bytes) -> tuple[dict[str, Any], str]:
    """Split a skills.md file into ``(frontmatter_dict, body_markdown)``.

    Raises ``ValueError`` on malformed frontmatter.
    """
    try:
        post = frontmatter.loads(content.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("skills.md must be UTF-8") from exc
    except Exception as exc:  # python-frontmatter raises generic YAMLError
        raise ValueError(f"Malformed YAML frontmatter: {exc}") from exc

    # python-frontmatter happily returns an empty dict when there is no
    # frontmatter at all; the validator treats that as missing metadata.
    return dict(post.metadata), post.content


__all__ = ["split_frontmatter"]
