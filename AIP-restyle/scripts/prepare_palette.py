#!/usr/bin/env python3
"""Build portable palette assets from the canonical, source-verified JSON."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    assets = ROOT / "assets"
    palette = json.loads((assets / "palette.json").read_text())
    entries = palette["swatches"]
    css = ["/* AI Pioneers digital colors; see palette.json for source-label corrections. */", ":root {"]
    for entry in entries:
        css.append(f"  --aip-{entry['id'].replace('_', '-')}: {entry['hex']};")
    css.extend(["  --aip-logo-white: #FFFFFF;", "}"])
    (assets / "palette.css").write_text("\n".join(css)+"\n")
    gpl = ["GIMP Palette", "Name: AI Pioneers digital", "Columns: 8", "# Guideline page 11, resolved digital values"]
    for entry in entries:
        gpl.append(" ".join(str(n) for n in entry["rgb"]) + "\t" + entry["name"])
    (assets / "palette.gpl").write_text("\n".join(gpl)+"\n")
    with (assets / "palette.csv").open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["name", "hex", "r", "g", "b", "source_c", "source_m", "source_y", "source_k"])
        for entry in entries:
            writer.writerow([entry["name"], entry["hex"], *entry["rgb"], *entry["cmyk_source_label"]])

    width, height = 1200, 700
    image = Image.new("RGB", (width, height), "#F6F9FC")
    draw = ImageDraw.Draw(image)
    try:
        heading = ImageFont.truetype("DejaVuSans.ttf", 32)
        body = ImageFont.truetype("DejaVuSans.ttf", 17)
        small = ImageFont.truetype("DejaVuSans.ttf", 14)
    except OSError:
        heading = body = small = ImageFont.load_default()
    title = "AI Pioneers · Complete digital palette"
    draw.text((28, 20), title, font=heading, fill="#020624")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="1200" height="700" fill="#F6F9FC"/>',
           '<g font-family="DejaVu Sans, sans-serif">',
           f'<text x="28" y="48" font-size="32" fill="#020624">{html.escape(title)}</text>']
    for i, entry in enumerate(entries):
        x = 28 + (i % 4)*294
        y = 88 + (i // 4)*272
        fill = entry["hex"]
        ink = "#FFFFFF" if i <= 4 else "#020624"
        draw.rectangle((x, y, x+270, y+240), fill=fill, outline="#B7CDDD", width=1)
        lines = [entry["name"], fill, "RGB " + ", ".join(map(str, entry["rgb"])),
                 "Guide CMYK " + ", ".join(map(str, entry["cmyk_source_label"]))]
        svg.append(f'<g id="{entry["id"]}"><rect x="{x}" y="{y}" width="270" height="240" fill="{fill}" stroke="#B7CDDD"/>')
        for j, line in enumerate(lines):
            font = body if j < 2 else small
            draw.text((x+16, y+126+j*25), line, font=font, fill=ink)
            svg.append(f'<text x="{x+16}" y="{y+143+j*25}" font-size="{17 if j < 2 else 14}" fill="{ink}">{html.escape(line)}</text>')
        svg.append("</g>")
    note = "HEX/RGB are resolved digital values. CMYK labels are from the guide, not a new profile conversion."
    draw.text((28, 650), note, font=small, fill="#020624")
    svg.extend([f'<text x="28" y="668" font-size="14" fill="#020624">{html.escape(note)}</text>', "</g>", "</svg>"])
    image.save(assets / "palette.png")
    (assets / "palette.svg").write_text("\n".join(svg)+"\n", encoding="utf-8")
    print("Built all 8 colors as JSON-linked CSS, GPL, CSV, editable SVG, and PNG")


if __name__ == "__main__":
    main()
