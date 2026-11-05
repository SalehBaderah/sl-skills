#!/usr/bin/env python3
"""Validate package links, palette, interface metadata, and logo integrity."""

from __future__ import annotations

import hashlib
import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
NS = {"s": "http://www.w3.org/2000/svg"}
EXPECTED = ["#020624", "#0F1543", "#2F2447", "#4A3B68", "#58709C", "#B7CDDD", "#D4DAFA", "#F6F9FC"]


def validate(root=ROOT):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    check(skill.startswith("---\nname: restyle-ai-pioneers\ndescription: "), "Missing skill front matter")
    check("logo: auto" in skill and "required" in skill and "none" in skill, "Missing logo modes")
    check(len(skill.split()) < 3500, "Core skill too long; move detail to references")
    for markdown in root.rglob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", markdown.read_text(encoding="utf-8")):
            if "://" not in target and not target.startswith("#"):
                check((markdown.parent / target.split("#")[0]).is_file(),
                      f"Broken link in {markdown.relative_to(root)}: {target}")
    palette = json.loads((root / "assets/palette.json").read_text())
    check(list(palette["colors"].values()) == EXPECTED, "Digital palette differs from reference")
    swatches = palette["swatches"]
    check(len(swatches) == 8 and [s["id"] for s in swatches] == list(palette["colors"]), "Missing palette entries")
    css = (root / "assets/palette.css").read_text()
    with (root / "assets/palette.csv").open(newline="") as file:
        csv_rows = list(csv.DictReader(file))
    gpl_rows = [line.split() for line in (root / "assets/palette.gpl").read_text().splitlines()
                if re.match(r"^\d+\s+\d+\s+\d+\s", line)]
    vector_palette = ET.parse(root / "assets/palette.svg").getroot()
    check(len(csv_rows) == len(gpl_rows) == 8, "CSV/GPL must contain all eight colors")
    with Image.open(root / "assets/palette.png") as preview:
        for i, swatch in enumerate(swatches):
            expected = tuple(bytes.fromhex(swatch["hex"][1:]))
            check(swatch["hex"] == EXPECTED[i] and tuple(swatch["rgb"]) == expected,
                  f"Palette HEX/RGB mismatch: {swatch['id']}")
            token = f"--aip-{swatch['id'].replace('_', '-')}: {swatch['hex']};"
            check(token in css, f"CSS missing {swatch['id']}")
            if i < len(csv_rows):
                row = csv_rows[i]
                check(row["hex"] == swatch["hex"] and [int(row[k]) for k in ("r", "g", "b")] == swatch["rgb"],
                      f"CSV color mismatch: {swatch['id']}")
                check([int(row[k]) for k in ("source_c", "source_m", "source_y", "source_k")] == swatch["cmyk_source_label"],
                      f"CSV guide CMYK mismatch: {swatch['id']}")
            if i < len(gpl_rows):
                check(tuple(map(int, gpl_rows[i][:3])) == expected, f"GPL mismatch: {swatch['id']}")
            rect = vector_palette.find(f".//s:g[@id='{swatch['id']}']/s:rect", NS)
            check(rect is not None and rect.get("fill") == swatch["hex"], f"SVG swatch mismatch: {swatch['id']}")
            check(preview.convert("RGB").getpixel((36+(i%4)*294, 96+(i//4)*272)) == expected,
                  f"PNG swatch mismatch: {swatch['id']}")
    logo_dir = root / "assets/logos"
    manifest = json.loads((logo_dir / "manifest.json").read_text())
    check(set(manifest["variants"]) == {"white", "purple", "dark-purple", "navy"}, "Missing logo color variants")
    check(hashlib.sha256((root / manifest["source"]).read_bytes()).hexdigest() == manifest["source_sha256"],
          "Original guideline hash changed")
    check(manifest["source_page_one_based"] == 6 and manifest["path_count"] == 7, "Unexpected emblem source")
    alpha = None
    viewbox = None
    for variant, record in manifest["variants"].items():
        svg = ET.parse(logo_dir / record["svg"]).getroot()
        paths = [p.attrib["d"] for p in svg.findall(".//s:path", NS)]
        check(len(paths) == 7, f"{variant}: expected seven original paths")
        check(hashlib.sha256("\n".join(paths).encode()).hexdigest() == manifest["geometry_sha256"],
              f"{variant}: emblem geometry was modified")
        fills = [g.get("fill") for g in svg.findall(".//s:g", NS)]
        check(fills == [record["fill"]], f"{variant}: incorrect SVG fill")
        check(not svg.findall(".//s:image", NS) and not svg.findall(".//s:text", NS),
              f"{variant}: SVG must be native paths without raster/text")
        if viewbox is None:
            viewbox = svg.get("viewBox")
        check(viewbox == svg.get("viewBox"), "Variant viewBoxes differ")
        with Image.open(logo_dir / record["png"]) as png:
            check(png.mode == "RGBA" and png.width == 2048, f"{variant}: unexpected PNG format/size")
            a = png.getchannel("A")
            check(a.getextrema() == (0, 255), f"{variant}: PNG must have real transparency and opaque fill")
            if alpha is None:
                alpha = a.tobytes()
            check(alpha == a.tobytes(), "PNG variants have different alpha/geometry")
            expected_rgb = tuple(bytes.fromhex(record["fill"].lstrip("#")))
            opaque = a.point(lambda value: 255 if value == 255 else 0)
            difference = ImageChops.difference(png.convert("RGB"), Image.new("RGB", png.size, expected_rgb))
            check(all(ImageChops.multiply(channel, opaque).getbbox() is None for channel in difference.split()),
                  f"{variant}: PNG interior color differs from SVG")
    interface = (root / "agents/openai.yaml").read_text()
    check("$restyle-ai-pioneers" in interface and "exact bundled team emblem" in interface,
          "Interface prompt missing new behavior")
    for script in (root / "scripts").glob("*.py"):
        try:
            compile(script.read_text(), str(script), "exec")
        except SyntaxError as error:
            errors.append(str(error))
    check((root / "assets/icon.svg").read_bytes() == (logo_dir / "aip-emblem-purple.svg").read_bytes(),
          "Skill interface icon differs from exact emblem")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        raise SystemExit("Validation failed:\n" + "\n".join(problems))
    print("PASS: skill metadata, local links, palette, source provenance, vector geometry, PNG alpha/colors, and scripts")
