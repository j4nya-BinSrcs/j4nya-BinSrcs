#!/usr/bin/env python3
"""Remove the language legend + pie chart from the generated 3D-contrib SVG.

The github-profile-3d-contrib action renders a language breakdown (legend
swatches + pie chart) alongside the contribution calendar. This script strips
that language block so the profile only shows the isometric contribution
graph. The stripped regions are identified by unique group markers, so the
script is safe to re-run after each regeneration.

Usage: strip_lang_pie.py <file.svg>
"""

import re
import sys


def strip_languages(path: str) -> bool:
    with open(path, encoding="utf-8") as fh:
        svg = fh.read()

    legend_start = '<g transform="translate(273, 0)">'
    pie_start = '<g transform="translate(130, 130)">'

    start = svg.find(legend_start)
    if start == -1:
        return False

    pie = svg.find(pie_start, start)
    if pie == -1:
        return False

    # Walk from the pie group, tracking nested <g> depth, to its matching close.
    cursor = pie + len(pie_start)
    depth = 1
    for match in re.finditer(r"<g\b[^>]*>|</g>", svg[cursor:]):
        if match.group(0).startswith("</g>"):
            depth -= 1
            if depth == 0:
                end = cursor + match.end()
                break
        else:
            depth += 1
    else:
        return False

    stripped = svg[:start] + svg[end:]

    if svg.count("<g") - svg.count("</g>") != stripped.count("<g") - stripped.count("</g>"):
        raise SystemExit(f"aborting: group balance changed for {path}")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(stripped)

    return True


if __name__ == "__main__":
    changed = False
    for f in sys.argv[1:]:
        if strip_languages(f):
            changed = True
    if not changed:
        sys.exit(0)