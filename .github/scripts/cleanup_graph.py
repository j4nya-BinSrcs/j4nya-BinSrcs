#!/usr/bin/env python3
"""Clean up the generated 3D-contrib SVG for the profile.

The github-profile-3d-contrib action renders extra elements that are not
wanted on the profile:

  * a language legend + pie chart
  * star and fork counts in the footer

This script strips those blocks while keeping the contribution calendar and
the total contribution count. Every block is located by a unique group marker
and removed as a balanced <g>...</g> element, so it is safe to re-run after
each daily regeneration.

Usage: cleanup_graph.py <file.svg>...
"""

import re
import sys


def _balanced_end(svg: str, cursor: int) -> int:
    """Return the index just past the matching </g> for a <g> opening at cursor."""
    depth = 1
    for match in re.finditer(r"<g\b[^>]*>|</g>", svg[cursor:]):
        if match.group(0).startswith("</g>"):
            depth -= 1
            if depth == 0:
                return cursor + match.end()
        else:
            depth += 1
    raise ValueError("unbalanced <g>")


def _remove_through_text(svg: str, gmarker: str) -> str:
    """Remove a <g>...</g> block plus the immediately following <text>...</text>."""
    start = svg.find(gmarker)
    if start == -1:
        return svg
    close = svg.index("</g>", start)
    ti = svg.find("<text", close)
    if ti == -1:
        return svg
    te = svg.index("</text>", ti) + len("</text>")
    return svg[:start] + svg[te:]


def cleanup(path: str) -> bool:
    with open(path, encoding="utf-8") as fh:
        svg = fh.read()
    original = svg
    balance_before = svg.count("<g") - svg.count("</g>")

    # 1. language legend + pie chart
    legend_start = '<g transform="translate(273, 0)">'
    pie_start = '<g transform="translate(130, 130)">'
    start = svg.find(legend_start)
    if start != -1:
        pie = svg.find(pie_start, start)
        if pie != -1:
            cursor = pie + len(pie_start)
            end = _balanced_end(svg, cursor)
            svg = svg[:start] + svg[end:]

    # 2. star and fork counts in the footer
    svg = _remove_through_text(svg, '<g transform="translate(608, 802), scale(2)">')
    svg = _remove_through_text(svg, '<g transform="translate(736, 802), scale(2)">')

    if svg.count("<g") - svg.count("</g>") != balance_before:
        raise SystemExit(f"aborting: group balance changed for {path}")
    if svg == original:
        return False

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    return True


if __name__ == "__main__":
    for f in sys.argv[1:]:
        cleanup(f)