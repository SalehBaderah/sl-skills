#!/usr/bin/env python3
"""Rebuild the emblem from the bundled guideline's original vector curves.

Development dependency: PyMuPDF. Runtime compositing only needs Pillow.
The supplied logo image is a visual reference; this is a faithful vector
extraction of the matching emblem, not a trace of that screenshot.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "references/ai-pioneers-guidelines-v2.pdf"
COLORS = {"white": "#FFFFFF", "purple": "#4A3B68", "dark-purple": "#2F2447", "navy": "#020624"}


def number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def make_path(drawing: dict) -> str:
    commands = []
    last = None
    for item in drawing["items"]:
        if item[0] not in {"c", "l"}:
            raise ValueError(f"Unexpected source primitive: {item[0]}")
        start = item[1]
        if last is None or abs(start.x-last.x) > 0.0001 or abs(start.y-last.y) > 0.0001:
            commands.append(f"M{number(start.x)} {number(start.y)}")
        if item[0] == "c":
            commands.append("C" + " ".join(number(v) for point in item[2:] for v in point))
        else:
            commands.append(f"L{number(item[2].x)} {number(item[2].y)}")
        last = item[-1]
    commands.append("Z")
    return " ".join(commands)


def main() -> None:
    with fitz.open(PDF) as doc:
        page = doc[5]  # One-based page 6, standalone emblem, excluding labels/rules.
        area = fitz.Rect(250, 450, 440, 600)
        shapes = [d for d in page.get_drawings()
                  if d["type"] == "f" and d["fill"] == (1.0, 1.0, 1.0)
                  and area.contains(d["rect"])]
    if len(shapes) != 7:
        raise ValueError("Expected exactly 7 original emblem paths; source may have changed")
    bounds = fitz.Rect(shapes[0]["rect"])
    for drawing in shapes[1:]:
        bounds |= drawing["rect"]
    paths = [make_path(d) for d in shapes]
    # Tiny padding avoids clipping antialiased edges at the viewBox boundary.
    viewbox = [bounds.x0-0.1, bounds.y0-0.1, bounds.width+0.2, bounds.height+0.2]
    width = 2048
    height = round(width * viewbox[3] / viewbox[2])
    out = ROOT / "assets/logos"
    out.mkdir(parents=True, exist_ok=True)
    for variant, color in COLORS.items():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="{" ".join(map(number, viewbox))}" '
               f'width="{width}" height="{height}" role="img" aria-label="AI Pioneers emblem">\n'
               '<title>AI Pioneers emblem</title>\n'
               f'<g fill="{color}">\n' +
               "\n".join(f'<path d="{path}"/>' for path in paths) +
               '\n</g>\n</svg>\n')
        (out / f"aip-emblem-{variant}.svg").write_text(svg, encoding="utf-8")
        with fitz.open(stream=svg.encode(), filetype="svg") as vector:
            with fitz.open(stream=vector.convert_to_pdf(), filetype="pdf") as rendered:
                pix = rendered[0].get_pixmap(matrix=fitz.Matrix(width/rendered[0].rect.width,
                                                               height/rendered[0].rect.height),
                                                alpha=True)
                pix.save(out / f"aip-emblem-{variant}.png")
    # Use the actual emblem for the skill's interface icon, with no added container.
    (ROOT / "assets/icon.svg").write_bytes((out / "aip-emblem-purple.svg").read_bytes())
    manifest = {
        "source": "references/ai-pioneers-guidelines-v2.pdf",
        "source_page_one_based": 6,
        "source_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "method": "Original PDF filled cubic/line paths; no raster tracing or generative reconstruction",
        "matches": "User-provided standalone white emblem on black, visually compared",
        "path_count": len(paths),
        "geometry_sha256": hashlib.sha256("\n".join(paths).encode()).hexdigest(),
        "viewBox": viewbox,
        "variants": {k: {"fill": v, "svg": f"aip-emblem-{k}.svg", "png": f"aip-emblem-{k}.png"}
                     for k, v in COLORS.items()},
        "notes": "White/purple variants are evidenced on guideline pages 6/11. Dark-purple/navy are user-authorized AIP-palette color variants; all preserve identical geometry. No wordmark synthesized."
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"Extracted {len(paths)} original paths; saved SVG and transparent PNG variants")


if __name__ == "__main__":
    main()
