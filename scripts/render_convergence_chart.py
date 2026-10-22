#!/usr/bin/env python3
"""Render a reference-style convergence chart from TSV evidence.

The chart is intentionally dependency-free so it works on clean Windows and
remote Linux hosts without matplotlib. It emits SVG using the visual contract in
``references/convergence.md``.
"""

from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path


BLUE = "#3f7be0"
GRID = "#e8edf4"
AXIS = "#d5dde8"
TEXT = "#233044"
MUTED = "#7c8aa0"


def parse_filter(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("filters must use key=value")
    key, expected = value.split("=", 1)
    if not key:
        raise argparse.ArgumentTypeError("filter key cannot be empty")
    return key, expected


def read_rows(path: Path, filters: list[tuple[str, str]], safe_only: bool) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    selected: list[dict[str, str]] = []
    for row in rows:
        if any(row.get(key, "") != expected for key, expected in filters):
            continue
        if safe_only:
            if row.get("status") != "PASS":
                continue
            if row.get("lost", "0") not in {"", "0"}:
                continue
            if row.get("unknown_pushes", "0") not in {"", "0"}:
                continue
        selected.append(row)
    return selected


def numeric(row: dict[str, str], column: str) -> float:
    value = row.get(column, "")
    if value == "":
        raise ValueError(f"missing numeric column {column!r} in row {row}")
    return float(value)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_text(
    x: float,
    y: float,
    body: object,
    *,
    size: int = 14,
    color: str = TEXT,
    anchor: str = "middle",
    weight: int = 400,
    rotate: float | None = None,
) -> str:
    transform = f' transform="rotate({rotate:.1f} {x:.1f} {y:.1f})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Microsoft YaHei, sans-serif" '
        f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{transform}>'
        f"{esc(body)}</text>"
    )


def point_scale(values: list[float], span: float, pad_ratio: float, zero_min: bool) -> tuple[float, float]:
    lo = 0.0 if zero_min else min(values)
    hi = max(values)
    if hi == lo:
        hi = lo + 1.0
    pad = (hi - lo) * pad_ratio
    return lo, hi + pad


def coord(value: float, lo: float, hi: float, start: float, length: float, invert: bool = False) -> float:
    if hi == lo:
        ratio = 0.0
    else:
        ratio = (value - lo) / (hi - lo)
    if invert:
        ratio = 1.0 - ratio
    return start + ratio * length


def render_chart(
    rows: list[dict[str, str]],
    output: Path,
    *,
    x_column: str,
    y_column: str,
    label_column: str,
    title: str,
    subtitle: str,
    x_title: str,
    y_title: str,
    footer: str,
    unit: str,
    remap_x: bool,
    zero_min: bool,
    labels: list[str],
) -> None:
    if not rows:
        raise ValueError("no rows selected for chart")

    xs = list(range(len(rows))) if remap_x else [numeric(row, x_column) for row in rows]
    ys = [numeric(row, y_column) for row in rows]
    point_labels = labels if labels else [row.get(label_column, "") for row in rows]
    if len(point_labels) < len(rows):
        point_labels.extend([""] * (len(rows) - len(point_labels)))

    width, height = 1040, 579
    left, top = 108, 92
    plot_width, plot_height = 795, 380
    bottom = top + plot_height
    right = left + plot_width

    x_lo, x_hi = min(xs), max(xs)
    if x_lo == x_hi:
        x_hi = x_lo + 1.0
    y_lo, y_hi = point_scale(ys, plot_height, 0.12, zero_min)

    points = [
        (
            coord(x, x_lo, x_hi, left, plot_width),
            coord(y, y_lo, y_hi, top, plot_height, invert=True),
        )
        for x, y in zip(xs, ys)
    ]
    poly_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text(left + 16, top - 24, title, size=18, color=TEXT, anchor="start", weight=700),
        svg_text(left + 16, top - 3, subtitle, size=14, color="#50627a", anchor="start"),
    ]

    for index in range(7):
        y = top + index * plot_height / 6
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{GRID}" stroke-dasharray="3 4"/>')
        value = y_hi - index * (y_hi - y_lo) / 6
        tick = f"{value:.0f}" if abs(value) >= 10 else f"{value:.2f}".rstrip("0").rstrip(".")
        parts.append(svg_text(left - 18, y + 4, tick, size=13, color=MUTED, anchor="end"))

    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="{AXIS}" stroke-width="1.2"/>')
    parts.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{AXIS}" stroke-width="1.2"/>')

    for x in xs:
        px = coord(x, x_lo, x_hi, left, plot_width)
        tick = f"{x:.0f}" if float(x).is_integer() else f"{x:g}"
        parts.append(svg_text(px, bottom + 24, tick, size=13, color=MUTED))

    parts.append(
        f'<polyline points="{poly_points}" fill="none" stroke="{BLUE}" stroke-width="3.8" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )

    for idx, ((px, py), y_value, label) in enumerate(zip(points, ys, point_labels)):
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10.5" fill="#ffffff" stroke="{BLUE}" stroke-width="3"/>')
        value = f"{y_value:.2f}".rstrip("0").rstrip(".")
        parts.append(svg_text(px, py + 31, f"{value}{unit}", size=13, color="#111827", weight=700))
        if label:
            rotation = -47 if idx == 0 else -42
            label_x = px + 8
            label_y = py - 18
            parts.append(svg_text(label_x, label_y, label, size=13, color="#6b7a90", anchor="start", rotate=rotation))

    parts.append(svg_text((left + right) / 2, height - 48, x_title, size=20, color=TEXT, weight=500))
    parts.append(svg_text(38, (top + bottom) / 2, y_title, size=20, color=TEXT, rotate=-90, weight=500))
    parts.append(svg_text(right, height - 27, footer, size=12, color="#9aa7b8", anchor="end"))
    parts.append("</svg>")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--filter", dest="filters", type=parse_filter, action="append", default=[])
    parser.add_argument("--safe-only", action="store_true", help="Keep only PASS rows with lost=0 and unknown_pushes=0.")
    parser.add_argument("--x-column", default="iter")
    parser.add_argument("--y-column", required=True)
    parser.add_argument("--label-column", default="notes")
    parser.add_argument("--labels", default="", help="Optional semicolon-separated point labels.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", required=True)
    parser.add_argument("--x-title", default="迭代次数 (Iter)")
    parser.add_argument("--y-title", required=True)
    parser.add_argument("--footer", default="Linux gate · compare passed")
    parser.add_argument("--unit", default="")
    parser.add_argument("--remap-x", action="store_true", help="Render selected rows as 0..N-1.")
    parser.add_argument("--zero-min", action="store_true", help="Force Y axis to start at zero.")
    args = parser.parse_args()

    labels = [item.strip() for item in args.labels.split(";") if item.strip()]
    rows = read_rows(args.input, args.filters, args.safe_only)
    rows.sort(key=lambda row: numeric(row, args.x_column))
    render_chart(
        rows,
        args.output,
        x_column=args.x_column,
        y_column=args.y_column,
        label_column=args.label_column,
        title=args.title,
        subtitle=args.subtitle,
        x_title=args.x_title,
        y_title=args.y_title,
        footer=args.footer,
        unit=args.unit,
        remap_x=args.remap_x,
        zero_min=args.zero_min,
        labels=labels,
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
