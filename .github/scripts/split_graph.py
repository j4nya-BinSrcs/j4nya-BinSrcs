#!/usr/bin/env python3
"""Split the cleaned 3D-contrib SVG into two standalone SVGs.

The single generated SVG contains the isometric contribution calendar (a grid
of per-cell <g transform="translate(x y)"> groups) and, at top-right, a radar
"stats web" chart. This script splits them into two separate SVGs for a
side-by-side profile layout:

  contrib-graph.svg  -> the contribution calendar only
  contrib-stats.svg  -> the radar stats web only

It also strips the total "contributions" count text and the (now empty)
languages container group. All group nesting is kept balanced.

Usage: split_graph.py <cleaned_input.svg>
"""

import re
import sys


def _balanced_end(svg: str, cursor: int) -> int:
    depth = 1
    for match in re.finditer(r"<g\b[^>]*>|</g>", svg[cursor:]):
        if match.group(0).startswith("</g>"):
            depth -= 1
            if depth == 0:
                return cursor + match.end()
        else:
            depth += 1
    raise ValueError("unbalanced <g>")


def _wrap(svg: str, view_box: str, title: str) -> str:
    m = re.search(r"<svg[^>]*>", svg)
    tag = m.group(0)
    new_tag = tag.replace('viewBox="0 0 1280 850"', f'viewBox="{view_box}"')
    new_tag = new_tag[:-1] + f">\n<title>{title}</title>"
    return svg[: m.start()] + new_tag + svg[m.end():]


def _remove_footer_count(svg: str) -> str:
    s = svg
    m = re.search(r'<text[^>]*?x="384"[^>]*>287</text>', s)
    if m:
        s = s[:m.start()] + s[m.end():]
    m = re.search(r'<text[^>]*?x="394"[^>]*>contributions</text>', s)
    if m:
        s = s[:m.start()] + s[m.end():]
    return s


def _remove_group(svg: str, marker: str) -> str:
    start = svg.find(marker)
    if start == -1:
        return svg
    cursor = start + len(marker)
    end = _balanced_end(svg, cursor)
    return svg[:start] + svg[end:]


def _remove_calendar_cells(svg: str) -> str:
    """Remove every per-cell calendar group: <g transform="translate(X Y)">..."""
    out = []
    cursor = 0
    pattern = re.compile(r'<g transform="translate\((-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)\)">')
    while True:
        m = pattern.search(svg, cursor)
        if not m:
            out.append(svg[cursor:])
            break
        out.append(svg[cursor:m.start()])
        end = _balanced_end(svg, m.start() + len(m.group(0)))
        cursor = end
    return "".join(out)


def split_graph(path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        svg = fh.read()

    radar_group = '<g transform="translate(980, 284.5)">'

    # --- contribution graph (remove radar + footer count) ---
    graph = _remove_group(svg, radar_group)
    graph = _remove_footer_count(graph)
    graph = _remove_group(graph, '<g transform="translate(40, 520)">')
    graph = _wrap(graph, "0 110 1280 740", "GitHub contribution calendar")
    out_graph = path.rsplit("/", 1)[0] + "/contrib-graph.svg"
    with open(out_graph, "w", encoding="utf-8") as fh:
        fh.write(graph)

    # --- stats web (keep only radar) ---
    stats = _remove_calendar_cells(svg)
    stats = _remove_footer_count(stats)
    stats = _remove_group(stats, '<g transform="translate(40, 520)">')
    stats = _wrap(stats, "750 50 460 460", "GitHub activity stats")
    out_stats = path.rsplit("/", 1)[0] + "/contrib-stats.svg"
    with open(out_stats, "w", encoding="utf-8") as fh:
        fh.write(stats)

    for name, out, src in (("graph", out_graph, graph), ("stats", out_stats, stats)):
        if src.count("<g") - src.count("</g>") != svg.count("<g") - svg.count("</g>"):
            raise SystemExit(f"group balance changed for {name}")


if __name__ == "__main__":
    split_graph(sys.argv[1])